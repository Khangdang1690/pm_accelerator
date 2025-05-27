# Advanced Weather App Backend

A comprehensive weather application backend built with FastAPI, featuring CRUD operations, API integrations, and data export capabilities.

## Features

- **Weather Data**: Real-time weather information using Open-Meteo API
- **AI Assistant**: Google Gemini-powered conversational weather assistant
- **CRUD Operations**: Full Create, Read, Update, Delete operations for weather requests
- **API Integrations**: 
  - **YouTube Videos**: Using Agno's YouTube tools for location-related content
  - **Google Maps**: Using Agno's Google Maps tools for comprehensive location data
  - **News Articles**: Location-related news (demo implementation)
  - **Timezone Information**: Accurate timezone data for locations
- **Data Export**: Multiple formats (JSON, XML, CSV, PDF, Markdown)
- **Database**: SQLite with comprehensive weather request management

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Required for Google Gemini AI
GOOGLE_API_KEY=your_google_api_key_here

# Required for Agno YouTube tools integration
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional for enhanced Google Maps integration
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Optional for news integration
NEWS_API_KEY=your_news_api_key_here
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (see above)

3. Run the server:
```bash
python agent.py
```

## API Endpoints

### Core Endpoints
- `POST /chat` - Conversational weather queries
- `GET /test` - Health check

### CRUD Operations
- `POST /weather-requests` - Create new weather request
- `GET /weather-requests` - List all weather requests
- `GET /weather-requests/{id}` - Get specific weather request
- `PUT /weather-requests/{id}` - Update weather request
- `DELETE /weather-requests/{id}` - Delete weather request

### API Integrations
- `GET /youtube-videos/{location}` - Get YouTube videos using Agno tools
- `GET /google-maps/{location}` - Get Google Maps data using Agno tools
- `GET /location-enrichment/{location}` - Get comprehensive location data

### Data Export
- `GET /export/weather-requests?format={json|xml|csv|pdf|markdown}` - Export data

### Statistics
- `GET /statistics` - Get database statistics

## Agno YouTube Integration

This application uses [Agno's YouTube tools](https://docs.agno.com/examples/concepts/tools/others/youtube#youtube-tools) for better YouTube API integration:

### Benefits of Agno YouTube Tools:
- **Simplified Integration**: No need to manually handle YouTube API complexities
- **Built-in Error Handling**: Robust error handling and fallback mechanisms
- **Structured Responses**: Consistent data format for video information
- **Agent-based Approach**: Leverages AI for better search query optimization

### Setup:
1. Get a YouTube API key from Google Cloud Console
2. Set the `YOUTUBE_API_KEY` environment variable
3. The application will automatically use Agno's YouTube tools when available
4. Falls back to mock data if the API key is not configured

### Usage Example:
```python
from agno.agent import Agent
from agno.tools.youtube import YouTubeTools

agent = Agent(
    tools=[YouTubeTools()],
    show_tool_calls=True,
    markdown=True,
)
agent.print_response("Search for recent videos about New York travel weather guide")
```

## Agno Google Maps Integration

This application also uses [Agno's Google Maps tools](https://docs.agno.com/examples/concepts/tools/others/google_maps#google-maps-tools) for comprehensive location data:

### Benefits of Agno Google Maps Tools:
- **Comprehensive Location Analysis**: Address validation, geocoding, and nearby places
- **Business Search**: Find highly rated businesses and points of interest
- **Directions and Distance**: Calculate travel times and routes
- **Multi-mode Transit**: Compare driving, walking, and transit options
- **Elevation and Timezone**: Get detailed location metadata

### Setup:
1. Get a Google Maps API key from Google Cloud Console
2. Set the `GOOGLE_MAPS_API_KEY` environment variable
3. The application will automatically use Agno's Google Maps tools when available
4. Falls back to mock data if the API key is not configured

### Usage Example:
```python
from agno.agent import Agent
from agno.tools.google_maps import GoogleMapTools

agent = Agent(
    name="Maps API Agent",
    tools=[GoogleMapTools()],
    description="Location and business information specialist for mapping and location-based queries.",
    markdown=True,
    show_tool_calls=True,
)

# Business search example
agent.print_response("Find me highly rated restaurants in New York with their contact details")

# Location analysis example
agent.print_response("""Analyze this location: 'Times Square, New York'
Please provide:
1. Exact coordinates
2. Nearby landmarks
3. Local timezone""")
```

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Agno**: AI agent framework with built-in tool integrations
- **Google Gemini**: Advanced AI model for natural language processing
- **SQLite**: Lightweight database for data persistence
- **Open-Meteo**: Free weather API for accurate weather data

## Development

The application is structured with modular components:
- `agent.py` - Main FastAPI application and endpoints
- `database.py` - Database operations and models
- `api_integrations.py` - External API integrations (YouTube, Maps, etc.)
- `data_export.py` - Data export functionality
- `open_meteo_tool.py` - Weather data fetching tool

## Error Handling

The application includes comprehensive error handling:
- Graceful fallbacks when API keys are not configured
- Detailed error messages for debugging
- Automatic retry mechanisms for external API calls
- Validation for all input data 

# API Integrations Setup

This module provides integration with YouTube and Google Maps APIs through both direct API calls and Agno tools.

## Quick Fix for YouTube Feature

The YouTube feature was returning fake URLs because it was using fallback data. Here's how to fix it:

### Option 1: Use SerpAPI for YouTube Search (Recommended)

1. **Get a SerpAPI key:**
   - Go to [SerpAPI](https://serpapi.com/)
   - Sign up for a free account (100 searches/month free)
   - Get your API key from the dashboard

2. **Set the environment variable:**
   ```bash
   # Windows (PowerShell)
   $env:SERPAPI_API_KEY="your_serpapi_key_here"
   
   # Windows (Command Prompt)
   set SERPAPI_API_KEY=your_serpapi_key_here
   
   # Linux/Mac
   export SERPAPI_API_KEY=your_serpapi_key_here
   ```

3. **Install SerpAPI dependency:**
   ```bash
   pip install google-search-results
   ```

### Option 2: Use Direct YouTube Data API v3

1. **Get a YouTube Data API v3 key:**
   - Go to [Google Cloud Console](https://console.developers.google.com/)
   - Create a new project or select existing one
   - Enable "YouTube Data API v3"
   - Create credentials (API Key)

2. **Set the environment variable:**
   ```bash
   # Windows (PowerShell)
   $env:YOUTUBE_API_KEY="your_actual_api_key_here"
   
   # Windows (Command Prompt)
   set YOUTUBE_API_KEY=your_actual_api_key_here
   
   # Linux/Mac
   export YOUTUBE_API_KEY=your_actual_api_key_here
   ```

## API Keys Required

### SerpAPI (Recommended for YouTube)
- **Purpose:** Search YouTube videos using SerpAPI
- **Get it from:** [SerpAPI](https://serpapi.com/) (100 free searches/month)
- **Environment variable:** `SERPAPI_API_KEY`

### YouTube Data API v3 (Alternative)
- **Purpose:** Direct YouTube video search
- **Get it from:** [Google Cloud Console](https://console.developers.google.com/)
- **Environment variable:** `YOUTUBE_API_KEY`

### Google Maps API
- **Purpose:** Location data, directions, places
- **Get it from:** [Google Cloud Console](https://console.cloud.google.com/)
- **Environment variable:** `GOOGLE_MAPS_API_KEY`
- **Required APIs to enable:**
  - Places API
  - Directions API
  - Geocoding API
  - Maps JavaScript API

## Testing

Run the test script to check your setup:

```bash
cd backend
python test_youtube.py
```

This will show you:
- ✓ Which API keys are configured
- ✓ Whether Agno tools are available
- ✓ Sample API calls with real results

## Current Implementation

The system now:
1. **First tries Agno SerpAPI tools** (if SERPAPI_API_KEY is configured)
2. **Falls back to direct YouTube Data API calls** (if YOUTUBE_API_KEY is configured)
3. **Returns error message** (if no valid API keys are configured)

No more fake URLs like `https://youtube.com/watch?v=example_Tokyo`!

## Troubleshooting

### "YouTube API unavailable" error
- Check that `YOUTUBE_API_KEY` environment variable is set
- Verify your API key is valid and has YouTube Data API v3 enabled
- Check API quotas in Google Cloud Console

### "Agno YouTube tools not available" warning
- Install Agno: `pip install agno`
- This is just a warning - direct API calls will still work

### Rate limits
- YouTube API has daily quotas
- Consider implementing caching for production use 