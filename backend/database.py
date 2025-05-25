import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import os

class WeatherDatabase:
    def __init__(self, db_path: str = "weather_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Weather requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT NOT NULL,
                    normalized_location TEXT,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    weather_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    coordinates TEXT,
                    additional_data TEXT
                )
            ''')
            
            # Location cache table for validation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS location_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_term TEXT UNIQUE,
                    normalized_name TEXT,
                    coordinates TEXT,
                    country TEXT,
                    is_valid BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def validate_date_range(self, start_date: str, end_date: str) -> Tuple[bool, str, date, date]:
        """Validate date range input"""
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start_dt > end_dt:
                return False, "Start date cannot be after end date", None, None
            
            if start_dt > date.today():
                return False, "Start date cannot be in the future", None, None
            
            # Limit to 30 days range for API efficiency
            if (end_dt - start_dt).days > 30:
                return False, "Date range cannot exceed 30 days", None, None
            
            return True, "Valid date range", start_dt, end_dt
            
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD", None, None
    
    def validate_location(self, location: str) -> Tuple[bool, str, Optional[Dict]]:
        """Validate location and get coordinates"""
        # Check cache first
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT normalized_name, coordinates, country, is_valid FROM location_cache WHERE search_term = ?",
                (location.lower(),)
            )
            cached = cursor.fetchone()
            
            if cached:
                if cached[3]:  # is_valid
                    return True, "Location found in cache", {
                        'name': cached[0],
                        'coordinates': cached[1],
                        'country': cached[2]
                    }
                else:
                    return False, "Location not found", None
        
        # Validate with geocoding API
        from open_meteo_tool import _get_coordinates
        import requests
        
        try:
            # Try to get coordinates
            coords = _get_coordinates(location)
            if coords:
                # Get detailed location info
                response = requests.get(
                    f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&format=json"
                )
                data = response.json()
                
                if data.get("results"):
                    result = data["results"][0]
                    location_info = {
                        'name': result.get('name', location),
                        'coordinates': f"{result['latitude']},{result['longitude']}",
                        'country': result.get('country', '')
                    }
                    
                    # Cache the result
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT OR REPLACE INTO location_cache 
                            (search_term, normalized_name, coordinates, country, is_valid)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            location.lower(),
                            location_info['name'],
                            location_info['coordinates'],
                            location_info['country'],
                            True
                        ))
                        conn.commit()
                    
                    return True, "Location validated", location_info
            
            # Cache negative result
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO location_cache 
                    (search_term, normalized_name, coordinates, country, is_valid)
                    VALUES (?, ?, ?, ?, ?)
                ''', (location.lower(), location, "", "", False))
                conn.commit()
            
            return False, "Location not found or invalid", None
            
        except Exception as e:
            return False, f"Error validating location: {str(e)}", None
    
    def create_weather_request(self, location: str, start_date: str, end_date: str, 
                             user_id: str = None) -> Tuple[bool, str, Optional[int]]:
        """Create a new weather request record"""
        # Validate date range
        date_valid, date_msg, start_dt, end_dt = self.validate_date_range(start_date, end_date)
        if not date_valid:
            return False, date_msg, None
        
        # Validate location
        loc_valid, loc_msg, loc_info = self.validate_location(location)
        if not loc_valid:
            return False, loc_msg, None
        
        try:
            # Fetch weather data for the date range
            from open_meteo_tool import get_weather_forecast
            
            # For historical data, we'll use the coordinates
            coords = loc_info['coordinates'].split(',')
            lat, lon = float(coords[0]), float(coords[1])
            
            # Get weather data (this is a simplified version - in reality you'd need historical weather API)
            weather_data = get_weather_forecast(location, forecast_days=min(7, (end_dt - start_dt).days + 1))
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO weather_requests 
                    (location, normalized_location, start_date, end_date, weather_data, user_id, coordinates)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    location,
                    loc_info['name'],
                    start_date,
                    end_date,
                    weather_data,
                    user_id,
                    loc_info['coordinates']
                ))
                
                request_id = cursor.lastrowid
                conn.commit()
                
                return True, f"Weather request created successfully for {loc_info['name']}", request_id
                
        except Exception as e:
            return False, f"Error creating weather request: {str(e)}", None
    
    def read_weather_requests(self, limit: int = 50, offset: int = 0, 
                            location_filter: str = None) -> List[Dict]:
        """Read weather requests from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, location, normalized_location, start_date, end_date, 
                       weather_data, created_at, updated_at, user_id, coordinates
                FROM weather_requests
            '''
            params = []
            
            if location_filter:
                query += " WHERE location LIKE ? OR normalized_location LIKE ?"
                params.extend([f"%{location_filter}%", f"%{location_filter}%"])
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            columns = ['id', 'location', 'normalized_location', 'start_date', 'end_date',
                      'weather_data', 'created_at', 'updated_at', 'user_id', 'coordinates']
            
            return [dict(zip(columns, row)) for row in rows]
    
    def read_weather_request_by_id(self, request_id: int) -> Optional[Dict]:
        """Read a specific weather request by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, location, normalized_location, start_date, end_date, 
                       weather_data, created_at, updated_at, user_id, coordinates
                FROM weather_requests WHERE id = ?
            ''', (request_id,))
            
            row = cursor.fetchone()
            if row:
                columns = ['id', 'location', 'normalized_location', 'start_date', 'end_date',
                          'weather_data', 'created_at', 'updated_at', 'user_id', 'coordinates']
                return dict(zip(columns, row))
            return None
    
    def update_weather_request(self, request_id: int, location: str = None, 
                             start_date: str = None, end_date: str = None) -> Tuple[bool, str]:
        """Update an existing weather request"""
        # Check if record exists
        existing = self.read_weather_request_by_id(request_id)
        if not existing:
            return False, "Weather request not found"
        
        updates = []
        params = []
        
        # Validate and update location if provided
        if location:
            loc_valid, loc_msg, loc_info = self.validate_location(location)
            if not loc_valid:
                return False, loc_msg
            
            updates.extend(["location = ?", "normalized_location = ?", "coordinates = ?"])
            params.extend([location, loc_info['name'], loc_info['coordinates']])
        
        # Validate and update dates if provided
        current_start = start_date or existing['start_date']
        current_end = end_date or existing['end_date']
        
        date_valid, date_msg, start_dt, end_dt = self.validate_date_range(current_start, current_end)
        if not date_valid:
            return False, date_msg
        
        if start_date:
            updates.append("start_date = ?")
            params.append(start_date)
        
        if end_date:
            updates.append("end_date = ?")
            params.append(end_date)
        
        if not updates:
            return False, "No valid updates provided"
        
        # Add updated timestamp
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(request_id)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = f"UPDATE weather_requests SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True, "Weather request updated successfully"
                else:
                    return False, "No changes made"
                    
        except Exception as e:
            return False, f"Error updating weather request: {str(e)}"
    
    def delete_weather_request(self, request_id: int) -> Tuple[bool, str]:
        """Delete a weather request"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM weather_requests WHERE id = ?", (request_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True, "Weather request deleted successfully"
                else:
                    return False, "Weather request not found"
                    
        except Exception as e:
            return False, f"Error deleting weather request: {str(e)}"
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total requests
            cursor.execute("SELECT COUNT(*) FROM weather_requests")
            total_requests = cursor.fetchone()[0]
            
            # Unique locations
            cursor.execute("SELECT COUNT(DISTINCT normalized_location) FROM weather_requests")
            unique_locations = cursor.fetchone()[0]
            
            # Most requested locations
            cursor.execute('''
                SELECT normalized_location, COUNT(*) as count 
                FROM weather_requests 
                GROUP BY normalized_location 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            top_locations = cursor.fetchall()
            
            return {
                'total_requests': total_requests,
                'unique_locations': unique_locations,
                'top_locations': [{'location': loc, 'count': count} for loc, count in top_locations]
            } 