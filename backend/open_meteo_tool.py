import requests
import json

# WMO Weather interpretation codes (https://open-meteo.com/en/docs)
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light intensity",
    53: "Drizzle: Moderate intensity",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light intensity",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight intensity",
    63: "Rain: Moderate intensity",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light intensity",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight intensity",
    73: "Snow fall: Moderate intensity",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight intensity",
    81: "Rain showers: Moderate intensity",
    82: "Rain showers: Violent intensity",
    85: "Snow showers: Slight intensity",
    86: "Snow showers: Heavy intensity",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def _get_coordinates(location: str) -> tuple[float, float] | None:
    """Helper function to get latitude and longitude for a location."""
    # Check if location is already coordinates (lat, lon format)
    if ',' in location:
        try:
            parts = location.strip().split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                # Validate coordinate ranges
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
        except ValueError:
            pass  # Not valid coordinates, continue with geocoding
    
    # If not coordinates, use geocoding API
    try:
        response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&format=json"
        )
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
    except requests.exceptions.RequestException as e:
        print(f"Error geocoding {location}: {e}")
    return None

def _translate_wmo_code(code: int) -> str:
    """Translates WMO weather code to a human-readable description."""
    return WMO_CODES.get(code, "Unknown weather code")

def get_weather_forecast(location: str, units: str = "metric", forecast_days: int = 1) -> str:
    """
    Fetches the current weather and a brief forecast for a specified location using the Open-Meteo API.

    Args:
        location (str): The city and optionally country (e.g., "Berlin, Germany") or coordinates (e.g., "40.7128, -74.0060").
        units (str): Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit). Default 'metric'.
        forecast_days (int): Number of days for the forecast (1-7). Default 1.
    
    Returns:
        str: A string describing the weather conditions or an error message.
    """
    coordinates = _get_coordinates(location)
    if not coordinates:
        return f"Could not find coordinates for {location}."

    latitude, longitude = coordinates
    
    # Determine display location name
    if ',' in location and len(location.split(',')) == 2:
        try:
            # Check if it's coordinates
            float(location.split(',')[0].strip())
            float(location.split(',')[1].strip())
            display_location = f"coordinates {latitude:.4f}, {longitude:.4f}"
        except ValueError:
            display_location = location
    else:
        display_location = location
    
    temperature_unit = "fahrenheit" if units == "imperial" else "celsius"
    wind_speed_unit = "mph" if units == "imperial" else "kmh"
    
    # Clamp forecast_days between 1 and 7 for simplicity with API
    forecast_days = max(1, min(forecast_days, 7))

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", "weather_code", "wind_speed_10m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max"],
        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "precipitation_unit": "inch" if units == "imperial" else "mm",
        "forecast_days": forecast_days,
        "timezone": "auto" 
    }

    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        response.raise_for_status()
        data = response.json()

        current = data.get("current")
        daily = data.get("daily")

        if not current:
            return f"Could not retrieve current weather data for {display_location}."

        current_temp = current.get('temperature_2m')
        apparent_temp = current.get('apparent_temperature')
        humidity = current.get('relative_humidity_2m')
        current_precipitation = current.get('precipitation')
        current_weather_code = current.get('weather_code')
        current_wind_speed = current.get('wind_speed_10m')
        is_day_text = "Daytime" if current.get('is_day', 0) == 1 else "Nighttime"
        
        current_weather_desc = _translate_wmo_code(current_weather_code)
        
        temp_symbol = "°F" if units == "imperial" else "°C"
        wind_symbol = "mph" if units == "imperial" else "km/h"
        precip_symbol = "in" if units == "imperial" else "mm"

        result = (
            f"Current weather in {display_location} ({is_day_text}):\n"
            f"- Temperature: {current_temp}{temp_symbol} (Feels like: {apparent_temp}{temp_symbol})\n"
            f"- Humidity: {humidity}%\n"
            f"- Condition: {current_weather_desc} (WMO Code: {current_weather_code})\n"
            f"- Wind Speed: {current_wind_speed} {wind_symbol}\n"
            f"- Precipitation (last hour): {current_precipitation}{precip_symbol}\n"
        )
        
        if daily and forecast_days > 0:
            result += "\nBrief Forecast:\n"
            for i in range(min(forecast_days, len(daily.get("time", [])))):
                date = daily["time"][i]
                max_temp = daily["temperature_2m_max"][i]
                min_temp = daily["temperature_2m_min"][i]
                daily_weather_code = daily["weather_code"][i]
                daily_weather_desc = _translate_wmo_code(daily_weather_code)
                precip_sum = daily["precipitation_sum"][i]
                precip_prob = daily["precipitation_probability_max"][i]
                
                result += (
                    f"  {date}: {daily_weather_desc}. High: {max_temp}{temp_symbol}, Low: {min_temp}{temp_symbol}. "
                    f"Precip: {precip_sum}{precip_symbol} (Prob: {precip_prob}%)\n"
                )
        return result.strip()

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data for {display_location}: {e}"
    except (KeyError, IndexError) as e:
        return f"Error parsing weather data for {display_location}: Missing expected data. {e}"

if __name__ == '__main__':
    # Example Usage:
    
    # Test 1: Simple case (default units metric, 1 day forecast)
    weather_berlin = get_weather_forecast(location="Berlin")
    print("--- Berlin Weather (Metric, 1 Day) ---")
    print(weather_berlin)
    print("\n")

    # Test 2: Imperial units, 3 days forecast
    weather_ny_imperial = get_weather_forecast(location="New York", units="imperial", forecast_days=3)
    print("--- New York Weather (Imperial, 3 Days) ---")
    print(weather_ny_imperial)
    print("\n")

    # Test 3: Location not found
    weather_nonexistent = get_weather_forecast(location="NonExistentCityXYZ")
    print("--- NonExistentCityXYZ Weather ---")
    print(weather_nonexistent)
    print("\n")
    
    # Test 4: Tokyo
    weather_tokyo = get_weather_forecast(location="Tokyo", units="imperial")
    print("--- Tokyo Weather (Imperial, 1 Day) ---")
    print(weather_tokyo) 