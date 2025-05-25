import React from 'react';
import { 
  WiDaySunny, 
  WiCloudy, 
  WiRain, 
  WiSnow, 
  WiThunderstorm,
  WiFog,
  WiDayCloudyHigh,
  WiRaindrop
} from 'react-icons/wi';
import './ForecastCard.css';

const ForecastCard = ({ forecast }) => {
  const getWeatherIcon = (condition) => {
    const conditionLower = condition?.toLowerCase() || '';
    
    if (conditionLower.includes('clear') || conditionLower.includes('sunny')) {
      return <WiDaySunny />;
    } else if (conditionLower.includes('cloud') || conditionLower.includes('overcast')) {
      return <WiDayCloudyHigh />;
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

  // If forecast is a string (AI response), try to parse it
  const parseForecastFromString = (data) => {
    const lines = data.split('\n');
    const forecastDays = [];
    let inForecastSection = false;
    
    lines.forEach(line => {
      if (line.includes('Brief Forecast:') || line.includes('Forecast:')) {
        inForecastSection = true;
        return;
      }
      
      if (inForecastSection && line.trim() && line.includes(':')) {
        // Parse forecast line format: "2024-01-15: Clear sky. High: 25°C, Low: 15°C. Precip: 0mm (Prob: 0%)"
        const dateMatch = line.match(/(\d{4}-\d{2}-\d{2}):/);
        const conditionMatch = line.match(/:\s*([^.]+)\./);
        const highMatch = line.match(/High:\s*([^,]+)/);
        const lowMatch = line.match(/Low:\s*([^.]+)/);
        const precipMatch = line.match(/Precip:\s*([^(]+)/);
        const probMatch = line.match(/Prob:\s*([^)]+)/);
        
        if (dateMatch && conditionMatch) {
          const date = new Date(dateMatch[1]);
          const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
          const monthDay = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          
          forecastDays.push({
            date: dateMatch[1],
            day: forecastDays.length === 0 ? 'Today' : dayName,
            monthDay,
            condition: conditionMatch[1].trim(),
            temperature: `${highMatch ? highMatch[1].trim() : 'N/A'}/${lowMatch ? lowMatch[1].trim() : 'N/A'}`,
            precipitation: precipMatch ? precipMatch[1].trim() : '0mm',
            precipProbability: probMatch ? probMatch[1].trim() : '0%',
            icon: getWeatherIcon(conditionMatch[1].trim())
          });
        }
      }
    });
    
    return forecastDays;
  };

  // Determine if forecast is an array or string
  let forecastDays = [];
  if (Array.isArray(forecast)) {
    forecastDays = forecast;
  } else if (typeof forecast === 'string') {
    forecastDays = parseForecastFromString(forecast);
  }

  if (forecastDays.length === 0) {
    return null;
  }

  return (
    <div className="forecast-card">
      <h3 className="forecast-title">5-Day Forecast</h3>
      <div className="forecast-container">
        {forecastDays.map((day, index) => (
          <div key={index} className="forecast-day">
            <div className="forecast-date">
              <span className="day-name">{day.day}</span>
              {day.monthDay && <span className="month-day">{day.monthDay}</span>}
            </div>
            
            <div className="forecast-icon">
              {day.icon || getWeatherIcon(day.condition)}
            </div>
            
            <div className="forecast-condition">
              {day.condition}
            </div>
            
            <div className="forecast-temps">
              {day.temperature}
            </div>
            
            {(day.precipProbability || day.precipitation) && (
              <div className="forecast-precipitation">
                <WiRaindrop className="precip-icon" />
                <span className="precip-text">
                  {day.precipProbability || day.precipitation || '0%'}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ForecastCard; 