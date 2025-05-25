import React, { useState } from 'react';
import LocationInput from './components/LocationInput';
import WeatherCard from './components/WeatherCard';
import ForecastCard from './components/ForecastCard';
import WeatherManager from './components/WeatherManager';
import { FaCloud, FaDatabase, FaHome } from 'react-icons/fa';
import './App.css';

function App() {
  const [weatherData, setWeatherData] = useState(null);
  const [forecastData, setForecastData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('weather'); // 'weather' or 'manager'

  const handleWeatherData = (data, forecast) => {
    setWeatherData(data);
    setForecastData(forecast);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
  };

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="app-nav">
        <div className="nav-brand">
          <FaCloud className="nav-icon" />
          <span>Advanced Weather App</span>
        </div>
        <div className="nav-links">
          <button 
            className={`nav-btn ${currentView === 'weather' ? 'active' : ''}`}
            onClick={() => setCurrentView('weather')}
          >
            <FaHome /> Weather
          </button>
          <button 
            className={`nav-btn ${currentView === 'manager' ? 'active' : ''}`}
            onClick={() => setCurrentView('manager')}
          >
            <FaDatabase /> Data Manager
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="app-content">
        {currentView === 'weather' ? (
          <>
            {/* Original Weather App */}
            <div className="app-header">
              <h1>🌤️ Weather Forecast App</h1>
              <p>Get accurate weather information for any location worldwide</p>
            </div>

            <LocationInput 
              onWeatherData={handleWeatherData}
              onLoading={handleLoading}
              onError={handleError}
            />

            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}

            {loading && (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Fetching weather data...</p>
              </div>
            )}

            {weatherData && !loading && (
              <WeatherCard weather={weatherData} />
            )}

            {forecastData.length > 0 && !loading && (
              <ForecastCard forecast={forecastData} />
            )}
          </>
        ) : (
          <>
            {/* Weather Data Manager */}
            <WeatherManager />
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Advanced Weather App with CRUD Operations, API Integrations & Data Export
        </p>
        <p>
          Features: Real-time weather data, Location validation, YouTube videos, 
          Google Maps integration, Multi-format data export (JSON, CSV, XML, PDF, Markdown)
        </p>
      </footer>
    </div>
  );
}

export default App;
