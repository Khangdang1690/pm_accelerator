# Weather App Backend

A backend service for retrieving weather information using Agno and MCP tools.

## Features

- Get current weather for any location (city, zip code, landmark, etc.)
- Get 5-day weather forecast
- Get weather by GPS coordinates (for current location functionality)

## Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

Create a `.env` file in the project root with the following content:

```
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
```

## Running the API Server

Start the server with:

```bash
python weather_app.py
```

The API will be available at http://localhost:8001

## API Endpoints

### Get Current Weather

```
POST /api/current-weather
```

Request body:
```json
{
  "location": "New York City"
}
```

### Get Weather Forecast

```
POST /api/forecast
```

Request body:
```json
{
  "location": "Paris, France",
  "days": 5
}
```

### Get Weather by Coordinates

```
POST /api/weather-by-coordinates
```

Request body:
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

## Testing the API

You can test the API using curl, Postman, or any API testing tool:

```bash
# Example curl command to get current weather
curl -X POST "http://localhost:8001/api/current-weather" \
     -H "Content-Type: application/json" \
     -d '{"location": "London"}'
```

## Customization

To modify or extend the API:

1. Edit the custom routes in `weather_app.py`
2. Add additional models in the Pydantic models section
3. Update the Agno agent configuration as needed 