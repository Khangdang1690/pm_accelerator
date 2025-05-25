from agno.agent import Agent
from agno.app.fastapi.app import FastAPIApp
from agno.app.fastapi.serve import serve_fastapi_app
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from open_meteo_tool import get_weather_forecast
import os
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Optional

# Pydantic model for the chat request
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None # Optional: if you want to pass user_id later

basic_agent = Agent(
    name="Basic Agent",
    model=Gemini(id="gemini-2.0-flash",api_key=os.getenv("GOOGLE_GEMINI_API_KEY")),
    tools=[
        DuckDuckGoTools(), 
        get_weather_forecast
    ],
    show_tool_calls=True,
    add_history_to_messages=True,
    num_history_responses=3,
    add_datetime_to_instructions=True,
    markdown=True,
)

app = FastAPIApp(
    agent=basic_agent,
).get_async_router()

# New chat endpoint
@app.post("/chat")
async def chat_handler(request: ChatRequest):
    try:
        user_message = request.message
        user_id = request.user_id

        agent_response = await basic_agent.arun(user_message, user_id=user_id)
        
        if hasattr(agent_response, 'content') and agent_response.content is not None:
            response_content = agent_response.content
        else:
            response_content = str(agent_response)
        
        # Ensure the extracted content is a string
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
    return {"message": "Test endpoint is working!"}

if __name__ == "__main__":
    serve_fastapi_app("agent:app", port=8001, reload=True)