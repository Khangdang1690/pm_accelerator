import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  FaPlus, 
  FaEdit, 
  FaTrash, 
  FaDownload, 
  FaYoutube, 
  FaMapMarkerAlt,
  FaCalendarAlt,
  FaSearch,
  FaEye
} from 'react-icons/fa';
import './WeatherManager.css';

const WeatherManager = () => {
  const [weatherRequests, setWeatherRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingRequest, setEditingRequest] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [enrichmentData, setEnrichmentData] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({
    location: '',
    start_date: '',
    end_date: '',
    user_id: 'weather_app_user'
  });
  
  // Filter states
  const [filters, setFilters] = useState({
    location_filter: '',
    limit: 20,
    offset: 0
  });

  useEffect(() => {
    fetchWeatherRequests();
  }, [filters.location_filter, filters.limit, filters.offset]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchWeatherRequests = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.location_filter) params.append('location_filter', filters.location_filter);
      params.append('limit', filters.limit);
      params.append('offset', filters.offset);

      const response = await axios.get(`http://localhost:8001/weather-requests?${params}`);
      setWeatherRequests(response.data.requests);
      setError('');
    } catch (err) {
      setError('Failed to fetch weather requests');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post('http://localhost:8001/weather-requests', formData);
      
      if (response.data.success) {
        setShowCreateForm(false);
        setFormData({ location: '', start_date: '', end_date: '', user_id: 'weather_app_user' });
        fetchWeatherRequests();
        setError('');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create weather request');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const updateData = {
        location: formData.location || undefined,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined
      };
      
      const response = await axios.put(
        `http://localhost:8001/weather-requests/${editingRequest.id}`,
        updateData
      );
      
      if (response.data.success) {
        setEditingRequest(null);
        setFormData({ location: '', start_date: '', end_date: '', user_id: 'weather_app_user' });
        fetchWeatherRequests();
        setError('');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update weather request');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRequest = async (requestId) => {
    if (!window.confirm('Are you sure you want to delete this weather request?')) {
      return;
    }
    
    setLoading(true);
    try {
      await axios.delete(`http://localhost:8001/weather-requests/${requestId}`);
      fetchWeatherRequests();
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete weather request');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (request) => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8001/weather-requests/${request.id}`);
      setSelectedRequest(response.data.request);
      setEnrichmentData(response.data.enrichment);
      setError('');
    } catch (err) {
      setError('Failed to fetch request details');
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async (format) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('format', format);
      params.append('limit', 100);
      if (filters.location_filter) params.append('location_filter', filters.location_filter);

      const response = await axios.get(
        `http://localhost:8001/export/weather-requests?${params}`,
        { responseType: format === 'pdf' ? 'blob' : 'text' }
      );

      // Create download link
      const blob = new Blob([response.data], {
        type: response.headers['content-type']
      });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition'];
      const filename = contentDisposition 
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `weather_data.${format}`;
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setError('');
    } catch (err) {
      setError(`Failed to export data as ${format.toUpperCase()}`);
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (request) => {
    setEditingRequest(request);
    setFormData({
      location: request.location,
      start_date: request.start_date,
      end_date: request.end_date,
      user_id: request.user_id || 'weather_app_user'
    });
    setShowCreateForm(true);
  };

  const cancelEdit = () => {
    setEditingRequest(null);
    setShowCreateForm(false);
    setFormData({ location: '', start_date: '', end_date: '', user_id: 'weather_app_user' });
  };

  return (
    <div className="weather-manager">
      <div className="manager-header">
        <h2>Weather Request Manager</h2>
        <p>Manage your weather data requests with full CRUD operations</p>
      </div>

      {/* Action Buttons */}
      <div className="action-bar">
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(true)}
          disabled={loading}
        >
          <FaPlus /> New Request
        </button>
        
        <div className="export-buttons">
          <span>Export as:</span>
          {['json', 'csv', 'xml', 'pdf', 'markdown'].map(format => (
            <button
              key={format}
              className="btn btn-export"
              onClick={() => handleExportData(format)}
              disabled={loading}
            >
              <FaDownload /> {format.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="filters">
        <div className="filter-group">
          <label>Filter by location:</label>
          <input
            type="text"
            value={filters.location_filter}
            onChange={(e) => setFilters({...filters, location_filter: e.target.value})}
            placeholder="Enter location to filter..."
          />
        </div>
        <button className="btn btn-secondary" onClick={fetchWeatherRequests}>
          <FaSearch /> Search
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {/* Create/Edit Form */}
      {showCreateForm && (
        <div className="form-modal">
          <div className="form-container">
            <h3>{editingRequest ? 'Edit Weather Request' : 'Create New Weather Request'}</h3>
            
            <form onSubmit={editingRequest ? handleUpdateRequest : handleCreateRequest}>
              <div className="form-group">
                <label>Location *</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  placeholder="City, coordinates, zip code, landmark..."
                  required={!editingRequest}
                />
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Start Date *</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                    required={!editingRequest}
                  />
                </div>
                
                <div className="form-group">
                  <label>End Date *</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                    required={!editingRequest}
                  />
                </div>
              </div>
              
              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {editingRequest ? 'Update' : 'Create'} Request
                </button>
                <button type="button" className="btn btn-secondary" onClick={cancelEdit}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Weather Requests List */}
      <div className="requests-list">
        {loading && <div className="loading">Loading...</div>}
        
        {weatherRequests.length === 0 && !loading && (
          <div className="no-data">
            <p>No weather requests found. Create your first request!</p>
          </div>
        )}
        
        {weatherRequests.map(request => (
          <div key={request.id} className="request-card">
            <div className="request-header">
              <h4>{request.normalized_location || request.location}</h4>
              <div className="request-actions">
                <button 
                  className="btn-icon"
                  onClick={() => handleViewDetails(request)}
                  title="View Details"
                >
                  <FaEye />
                </button>
                <button 
                  className="btn-icon"
                  onClick={() => startEdit(request)}
                  title="Edit"
                >
                  <FaEdit />
                </button>
                <button 
                  className="btn-icon btn-danger"
                  onClick={() => handleDeleteRequest(request.id)}
                  title="Delete"
                >
                  <FaTrash />
                </button>
              </div>
            </div>
            
            <div className="request-details">
              <div className="detail-item">
                <FaCalendarAlt />
                <span>{request.start_date} to {request.end_date}</span>
              </div>
              <div className="detail-item">
                <FaMapMarkerAlt />
                <span>{request.coordinates}</span>
              </div>
              <div className="detail-item">
                <span className="created-at">Created: {new Date(request.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Request Details Modal */}
      {selectedRequest && (
        <div className="details-modal">
          <div className="details-container">
            <div className="details-header">
              <h3>Weather Request Details</h3>
              <button 
                className="close-btn"
                onClick={() => {setSelectedRequest(null); setEnrichmentData(null);}}
              >
                ×
              </button>
            </div>
            
            <div className="details-content">
              <div className="weather-data">
                <h4>Weather Information</h4>
                <pre>{selectedRequest.weather_data}</pre>
              </div>
              
              {enrichmentData && (
                <div className="enrichment-data">
                  <h4>Additional Information</h4>
                  
                  {enrichmentData.youtube?.videos && (
                    <div className="youtube-section">
                      <h5><FaYoutube /> Related Videos</h5>
                      {enrichmentData.youtube.videos.map((video, index) => (
                        <div key={index} className="video-item">
                          <a href={video.url} target="_blank" rel="noopener noreferrer">
                            {video.title}
                          </a>
                          <p>{video.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {enrichmentData.maps?.maps_data && (
                    <div className="maps-section">
                      <h5><FaMapMarkerAlt /> Location Information</h5>
                      <p><strong>Address:</strong> {enrichmentData.maps.maps_data.formatted_address || enrichmentData.maps.maps_data.place_name}</p>
                      <a 
                        href={enrichmentData.maps.maps_data.map_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="maps-link"
                      >
                        View on Google Maps
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WeatherManager; 