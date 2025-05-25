import React from 'react';
import { 
  WiDaySunny, 
  WiCloudy, 
  WiRain, 
  WiSnow, 
  WiThunderstorm,
  WiFog,
  WiDayCloudyHigh,
  WiNightClear,
  WiNightCloudy,
  WiHumidity,
  WiStrongWind,
  WiRaindrop
} from 'react-icons/wi';
import './WeatherCard.css';

const WeatherCard = ({ weather }) => {
  // Helper function to clean markdown formatting
  const cleanMarkdown = (text) => {
    if (!text) return text;
    return text.replace(/\*\*/g, '').replace(/\*/g, '').trim();
  };

  // Parse weather data from the AI response if it's a string, otherwise use the object
  const parseWeatherData = (data) => {
    if (!data) {
      return {
        location: 'Unknown',
        temperature: 'N/A',
        condition: 'N/A',
        humidity: 'N/A',
        windSpeed: 'N/A',
        description: 'No data available'
      };
    }
    
    if (typeof data === 'object' && data !== null) {
      return data; // Already parsed
    }
    
    const lines = data.split('\n');
    const weatherInfo = {
      location: 'Unknown',
      temperature: 'N/A',
      condition: 'N/A',
      humidity: 'N/A',
      windSpeed: 'N/A',
      description: data
    };
    
    // Extract location from the first line: "Current weather in [location] (Daytime):"
    const firstLine = lines[0];
    if (firstLine && firstLine.includes('Current weather in')) {
      const locationMatch = firstLine.match(/Current weather in (.+?) \(/);
      if (locationMatch) {
        weatherInfo.location = locationMatch[1].trim();
      }
    }
    
    // Extract current weather information
    lines.forEach(line => {
      // Clean the line of markdown formatting first
      const cleanLine = cleanMarkdown(line);
      
      // Temperature: 18.5°C (Feels like: 14.9°C)
      if (cleanLine.includes('Temperature:')) {
        const tempMatch = cleanLine.match(/Temperature:\s*([^(]+)/);
        if (tempMatch) weatherInfo.temperature = tempMatch[1].trim();
        
        const feelsLikeMatch = cleanLine.match(/Feels like:\s*([^)]+)/);
        if (feelsLikeMatch) weatherInfo.feelsLike = feelsLikeMatch[1].trim();
      }
      
      // Humidity: 46%
      if (cleanLine.includes('Humidity:')) {
        const humidityMatch = cleanLine.match(/Humidity:\s*(\d+%)/);
        if (humidityMatch) weatherInfo.humidity = humidityMatch[1];
      }
      
      // Condition: Overcast (WMO Code: 3)
      if (cleanLine.includes('Condition:')) {
        const conditionMatch = cleanLine.match(/Condition:\s*([^(]+)/);
        if (conditionMatch) weatherInfo.condition = cleanMarkdown(conditionMatch[1]).trim();
      }
      
      // Wind Speed: 18.8 km/h
      if (cleanLine.includes('Wind Speed:')) {
        const windMatch = cleanLine.match(/Wind Speed:\s*(.+)/);
        if (windMatch) weatherInfo.windSpeed = windMatch[1].trim();
      }
      
      // Precipitation (last hour): 0.0mm
      if (cleanLine.includes('Precipitation')) {
        const precipMatch = cleanLine.match(/Precipitation[^:]*:\s*(.+)/);
        if (precipMatch) weatherInfo.precipitation = precipMatch[1].trim();
      }
    });
    
    return weatherInfo;
  };

  const getWeatherIcon = (condition, isDay = true) => {
    const conditionLower = condition?.toLowerCase() || '';
    
    if (conditionLower.includes('clear') || conditionLower.includes('sunny')) {
      return isDay ? <WiDaySunny /> : <WiNightClear />;
    } else if (conditionLower.includes('cloud') || conditionLower.includes('overcast')) {
      return isDay ? <WiDayCloudyHigh /> : <WiNightCloudy />;
    } else if (conditionLower.includes('rain') || conditionLower.includes('drizzle')) {
      return <WiRain />;
    } else if (conditionLower.includes('snow')) {
      return <WiSnow />;
    } else if (conditionLower.includes('thunder')) {
      return <WiThunderstorm />;
    } else if (conditionLower.includes('fog')) {
      return <WiFog />;
    } else {
      return <WiCloudy />;
    }
  };

  const weatherData = parseWeatherData(weather);
  const isDay = new Date().getHours() >= 6 && new Date().getHours() < 18;

  return (
    <div className="weather-card">
      <div className="weather-header">
        <div className="location-info">
          <h2>{weatherData.location}</h2>
          <p className="time-info">{isDay ? 'Daytime' : 'Nighttime'}</p>
        </div>
        <div className="weather-icon-main">
          {getWeatherIcon(weatherData.condition, isDay)}
        </div>
      </div>

      <div className="weather-main">
        <div className="temperature-section">
          <div className="main-temp">
            {weatherData.temperature}
          </div>
          {weatherData.feelsLike && (
            <div className="feels-like">
              Feels like {weatherData.feelsLike}
            </div>
          )}
          <div className="condition">
            {weatherData.condition}
          </div>
        </div>
      </div>

      <div className="weather-details">
        <div className="detail-item">
          <WiHumidity className="detail-icon" />
          <div className="detail-content">
            <span className="detail-label">Humidity</span>
            <span className="detail-value">{weatherData.humidity}</span>
          </div>
        </div>

        <div className="detail-item">
          <WiStrongWind className="detail-icon" />
          <div className="detail-content">
            <span className="detail-label">Wind Speed</span>
            <span className="detail-value">{weatherData.windSpeed}</span>
          </div>
        </div>

        {weatherData.precipitation && (
          <div className="detail-item">
            <WiRaindrop className="detail-icon" />
            <div className="detail-content">
              <span className="detail-label">Precipitation</span>
              <span className="detail-value">{weatherData.precipitation}</span>
            </div>
          </div>
        )}
      </div>

      {/* Show full description if available */}
      {weatherData.description && weatherData.description !== weatherData.condition && (
        <div className="weather-description">
          <h4>Detailed Forecast:</h4>
          <p>{cleanMarkdown(weatherData.description)}</p>
        </div>
      )}
    </div>
  );
};

export default WeatherCard; 