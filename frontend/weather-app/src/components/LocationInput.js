import React, { useState } from 'react';
import axios from 'axios';
import { FaSearch, FaLocationArrow } from 'react-icons/fa';
import './LocationInput.css';

const LocationInput = ({ onWeatherData, onLoading, onError }) => {
  const [inputValue, setInputValue] = useState('');



  const parseForecastData = (responseText) => {
    // Parse the actual forecast data from the API response
    const forecast = [];
    const lines = responseText.split('\n');
    let inForecastSection = false;
    
    // Helper function to clean markdown formatting
    const cleanMarkdown = (text) => {
      if (!text) return text;
      return text.replace(/\*\*/g, '').replace(/\*/g, '').trim();
    };
    
    lines.forEach(line => {
      if (line.includes('Brief Forecast:') || line.includes('Forecast:')) {
        inForecastSection = true;
        return;
      }
      
      if (inForecastSection && line.trim() && line.includes(':')) {
        // Clean the line of markdown formatting first
        const cleanLine = cleanMarkdown(line);
        
        // Parse forecast line format: "2024-01-15: Clear sky. High: 25°C, Low: 15°C. Precip: 0mm (Prob: 0%)"
        const dateMatch = cleanLine.match(/(\d{4}-\d{2}-\d{2}):/);
        const conditionMatch = cleanLine.match(/:\s*([^.]+)\./);
        const highMatch = cleanLine.match(/High:\s*([^,]+)/);
        const lowMatch = cleanLine.match(/Low:\s*([^.]+)/);
        const precipMatch = cleanLine.match(/Precip:\s*([^(]+)/);
        const probMatch = cleanLine.match(/Prob:\s*([^)]+)/);
        
        if (dateMatch && conditionMatch) {
          const date = new Date(dateMatch[1]);
          const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
          const monthDay = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          
          forecast.push({
            date: dateMatch[1],
            day: forecast.length === 0 ? 'Today' : dayName,
            monthDay,
            condition: cleanMarkdown(conditionMatch[1]).trim(),
            temperature: `${highMatch ? cleanMarkdown(highMatch[1]).trim() : 'N/A'}/${lowMatch ? cleanMarkdown(lowMatch[1]).trim() : 'N/A'}`,
            precipitation: precipMatch ? cleanMarkdown(precipMatch[1]).trim() : '0mm',
            precipProbability: probMatch ? cleanMarkdown(probMatch[1]).trim() : '0%'
          });
        }
      }
    });
    
    return forecast;
  };

  const fetchWeather = async (locationQuery, isCurrentLocation = false) => {
    onLoading(true);
    onError('');
    
    try {
      let message;
      if (isCurrentLocation) {
        message = `Get current weather and 5-day forecast for coordinates: ${locationQuery}`;
      } else {
        message = `Get current weather and 5-day forecast for ${locationQuery}`;
      }

      const response = await axios.post('http://localhost:8001/chat', {
        message: message,
        user_id: 'weather_app_user'
      });

      if (response.data.status === 'success') {
        // Pass the raw response to WeatherCard for proper parsing
        const weatherData = response.data.response;
        const forecastData = parseForecastData(response.data.response);
        
        onWeatherData(weatherData, forecastData);
        onError('');
      } else {
        onError('Failed to fetch weather data');
      }
    } catch (err) {
      onError('Error connecting to weather service. Make sure the backend is running on port 8001.');
      console.error('Weather fetch error:', err);
    } finally {
      onLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      fetchWeather(inputValue.trim());
    }
  };

  const handleCurrentLocation = () => {
    if (navigator.geolocation) {
      onLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          fetchWeather(`${latitude}, ${longitude}`, true);
        },
        (error) => {
          onError('Unable to get your location. Please enter a location manually.');
          onLoading(false);
        }
      );
    } else {
      onError('Geolocation is not supported by this browser.');
    }
  };

  return (
    <div className="location-input-container">
      <div className="location-input-card">
        <h2>Enter Location</h2>
        <p className="input-description">
          Enter any location: city name, zip code, coordinates, or landmark
        </p>
        
        <form onSubmit={handleSubmit} className="location-form">
          <div className="input-group">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="e.g., New York, 10001, 40.7128,-74.0060, Times Square"
              className="location-input"
            />
            <button 
              type="submit" 
              className="search-button"
              disabled={!inputValue.trim()}
            >
              <FaSearch />
            </button>
          </div>
        </form>

        <div className="divider">
          <span>OR</span>
        </div>

        <button 
          onClick={handleCurrentLocation}
          className="current-location-button"
        >
          <FaLocationArrow />
          Use Current Location
        </button>

        <div className="location-examples">
          <h4>Example formats:</h4>
          <ul>
            <li><strong>City:</strong> London, Paris, Tokyo</li>
            <li><strong>City, Country:</strong> Berlin, Germany</li>
            <li><strong>Zip Code:</strong> 10001, SW1A 1AA</li>
            <li><strong>Coordinates:</strong> 40.7128, -74.0060</li>
            <li><strong>Landmarks:</strong> Eiffel Tower, Central Park</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LocationInput; 