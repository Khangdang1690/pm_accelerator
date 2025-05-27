from agno.agent import Agent
from agno.app.fastapi.app import FastAPIApp
from agno.app.fastapi.serve import serve_fastapi_app
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from open_meteo_tool import get_weather_forecast
from database import WeatherDatabase
from api_integrations import APIIntegrations
from data_export import DataExporter
import os
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
import base64

# Pydantic models for requests
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class WeatherRequest(BaseModel):
    location: str = Field(..., description="Location name, coordinates, or address")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    user_id: Optional[str] = None

class WeatherUpdateRequest(BaseModel):
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# Initialize components
db = WeatherDatabase()
api_integrations = APIIntegrations()
data_exporter = DataExporter()

basic_agent = Agent(
    name="Weather Assistant",
    model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY")),
    tools=[
        DuckDuckGoTools(), 
        get_weather_forecast
    ],
    show_tool_calls=True,
    add_history_to_messages=True,
    num_history_responses=3,
    add_datetime_to_instructions=True,
    markdown=True,
    instructions="""You are a helpful weather assistant. When users ask for weather information:
    1. Always use the get_weather_forecast tool to get accurate weather data
    2. For forecasts, always request 5 days of forecast data by setting forecast_days=5
    3. Present the information in a clear, organized format
    4. Include current weather conditions and the 5-day forecast when requested
    5. Be friendly and helpful in your responses"""
)

# Create the main FastAPI app
app = FastAPI(
    title="Advanced Weather App API",
    description="A comprehensive weather application with CRUD operations, API integrations, and data export",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the agent router
agent_router = FastAPIApp(agent=basic_agent).get_async_router()

@app.post("/chat")
async def chat_handler(request: ChatRequest):
    """Original chat endpoint for conversational weather queries"""
    try:
        user_message = request.message
        user_id = request.user_id

        agent_response = await basic_agent.arun(user_message, user_id=user_id)
        
        if hasattr(agent_response, 'content') and agent_response.content is not None:
            response_content = agent_response.content
        else:
            response_content = str(agent_response)
        
        if not isinstance(response_content, str):
            response_content = str(response_content)
            
        return {"response": response_content, "status": "success"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/test")
async def test_endpoint():
    """Health check endpoint"""
    return {"message": "Advanced Weather App API is running!", "version": "2.0.0"}

# ============ CRUD ENDPOINTS ============

@app.post("/weather-requests")
async def create_weather_request(request: WeatherRequest):
    """CREATE: Store a new weather request with date range validation"""
    try:
        success, message, request_id = db.create_weather_request(
            location=request.location,
            start_date=request.start_date,
            end_date=request.end_date,
            user_id=request.user_id
        )
        
        if success:
            # Get enrichment data
            weather_record = db.read_weather_request_by_id(request_id)
            enrichment = api_integrations.get_location_enrichment(
                request.location, 
                weather_record.get('coordinates')
            )
            
            return {
                "success": True,
                "message": message,
                "request_id": request_id,
                "weather_data": weather_record,
                "enrichment": enrichment.get('enrichment_data') if enrichment['success'] else None
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/weather-requests")
async def read_weather_requests(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    location_filter: Optional[str] = Query(None)
):
    """READ: Get all weather requests with optional filtering"""
    try:
        requests = db.read_weather_requests(
            limit=limit,
            offset=offset,
            location_filter=location_filter
        )
        
        return {
            "success": True,
            "requests": requests,
            "count": len(requests),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading requests: {str(e)}")

@app.get("/weather-requests/{request_id}")
async def read_weather_request(request_id: int):
    """READ: Get a specific weather request by ID"""
    try:
        request_data = db.read_weather_request_by_id(request_id)
        
        if not request_data:
            raise HTTPException(status_code=404, detail="Weather request not found")
        
        # Get enrichment data
        enrichment = api_integrations.get_location_enrichment(
            request_data['location'],
            request_data.get('coordinates')
        )
        
        return {
            "success": True,
            "request": request_data,
            "enrichment": enrichment.get('enrichment_data') if enrichment['success'] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading request: {str(e)}")

@app.put("/weather-requests/{request_id}")
async def update_weather_request(request_id: int, update_data: WeatherUpdateRequest):
    """UPDATE: Modify an existing weather request"""
    try:
        success, message = db.update_weather_request(
            request_id=request_id,
            location=update_data.location,
            start_date=update_data.start_date,
            end_date=update_data.end_date
        )
        
        if success:
            updated_request = db.read_weather_request_by_id(request_id)
            return {
                "success": True,
                "message": message,
                "updated_request": updated_request
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating request: {str(e)}")

@app.delete("/weather-requests/{request_id}")
async def delete_weather_request(request_id: int):
    """DELETE: Remove a weather request"""
    try:
        success, message = db.delete_weather_request(request_id)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=404, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting request: {str(e)}")

# ============ API INTEGRATION ENDPOINTS ============

@app.get("/location-enrichment/{location}")
async def get_location_enrichment(location: str):
    """Get comprehensive location data including YouTube videos, maps, and news"""
    try:
        enrichment = api_integrations.get_location_enrichment(location)
        return enrichment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting enrichment data: {str(e)}")

@app.get("/youtube-videos/{location}")
async def get_youtube_videos(location: str, max_results: int = Query(5, ge=1, le=10)):
    """Get YouTube videos related to the location"""
    try:
        videos = api_integrations.get_youtube_videos(location, max_results)
        return videos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching YouTube videos: {str(e)}")

@app.get("/google-maps/{location}")
async def get_google_maps_data(location: str):
    """Get Google Maps data for the location"""
    try:
        maps_data = api_integrations.get_google_maps_data(location)
        return maps_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Google Maps data: {str(e)}")

# ============ DATA EXPORT ENDPOINTS ============

@app.get("/export/weather-requests")
async def export_weather_requests(
    format: str = Query(..., pattern="^(json|xml|csv|markdown|md|pdf)$"),
    limit: int = Query(100, ge=1, le=1000),
    location_filter: Optional[str] = Query(None)
):
    """Export weather requests data in various formats"""
    try:
        # Get data to export
        data = db.read_weather_requests(
            limit=limit,
            offset=0,
            location_filter=location_filter
        )
        
        # Export data
        export_result = data_exporter.export_data(data, format)
        
        if not export_result['success']:
            raise HTTPException(status_code=400, detail=export_result['error'])
        
        # Return appropriate response based on format
        if export_result.get('is_binary', False):
            # For PDF files
            return Response(
                content=export_result['content'],
                media_type=export_result['content_type'],
                headers={
                    "Content-Disposition": f"attachment; filename={export_result['filename']}"
                }
            )
        else:
            # For text-based formats
            return Response(
                content=export_result['content'],
                media_type=export_result['content_type'],
                headers={
                    "Content-Disposition": f"attachment; filename={export_result['filename']}"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# ============ STATISTICS ENDPOINT ============

@app.get("/statistics")
async def get_statistics():
    """Get database and usage statistics"""
    try:
        stats = db.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

# Include the agent router for backward compatibility
app.include_router(agent_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent:app", host="0.0.0.0", port=8001, reload=True)