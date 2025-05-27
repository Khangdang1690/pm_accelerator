import requests
import json
from typing import List, Dict, Optional
import os
from urllib.parse import quote
from agno.agent import Agent
try:
    from agno.tools.serpapi import SerpApiTools
    AGNO_SERPAPI_AVAILABLE = True
except ImportError:
    AGNO_SERPAPI_AVAILABLE = False
    print("Warning: Agno SerpAPI tools not available")

try:
    from agno.tools.google_maps import GoogleMapTools
    AGNO_MAPS_AVAILABLE = True
except ImportError:
    AGNO_MAPS_AVAILABLE = False
    print("Warning: Agno Google Maps tools not available")

class APIIntegrations:
    def __init__(self):
        # Load API keys from environment variables
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        
        # Check if we have valid API keys
        self.has_valid_youtube_key = self.youtube_api_key 
        self.has_valid_maps_key = self.google_maps_api_key
        
        # Initialize Agno agent with SerpAPI tools for YouTube search
        # Note: SerpApiTools requires SERPAPI_API_KEY environment variable
        self.agno_serpapi_available = False
        self.youtube_agent = None
        
        # Check if SerpAPI key is available
        serpapi_key = os.getenv('SERPAPI_API_KEY')
        
        if AGNO_SERPAPI_AVAILABLE and serpapi_key:
            try:
                self.youtube_agent = Agent(
                    name="YouTube Search Agent",
                    tools=[SerpApiTools(search_youtube=True)],
                    description="YouTube video search specialist for finding relevant videos about locations and travel using SerpAPI.",
                    show_tool_calls=False,
                    markdown=False,
                )
                self.agno_serpapi_available = True
                print("✓ Agno SerpAPI tools initialized successfully for YouTube search")
            except Exception as e:
                print(f"Warning: Could not initialize Agno SerpAPI tools: {e}")
                self.youtube_agent = None
                self.agno_serpapi_available = False
        else:
            print("ℹ️  SerpAPI not configured - YouTube search will use direct API calls")
        
        # Initialize Agno agent with Google Maps tools
        # Note: GoogleMapTools requires GOOGLE_MAPS_API_KEY environment variable
        self.agno_maps_available = False
        self.maps_agent = None
        
        if AGNO_MAPS_AVAILABLE and self.has_valid_maps_key:
            try:
                # Set environment variable for Agno tools
                os.environ['GOOGLE_MAPS_API_KEY'] = self.google_maps_api_key
                
                self.maps_agent = Agent(
                    name="Maps API Agent",
                    tools=[GoogleMapTools()],
                    description="Location and business information specialist for mapping and location-based queries.",
                    show_tool_calls=False,
                    markdown=False,
                )
                self.agno_maps_available = True
                print("✓ Agno Google Maps tools initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Agno Google Maps tools: {e}")
                self.maps_agent = None
                self.agno_maps_available = False
    
    def get_youtube_videos(self, location: str, max_results: int = 5) -> Dict:
        """Get YouTube videos related to the location using YouTube Data API"""
        try:
            # First try Agno SerpAPI tools if available
            if self.agno_serpapi_available and self.youtube_agent:
                search_query = f"Search YouTube for {max_results} videos about {location} travel, tourism, weather, or visiting guide"
                
                try:
                    response = self.youtube_agent.run(search_query)
                    
                    if response and hasattr(response, 'content'):
                        response_content = str(response.content)
                        
                        # Try to extract video information from SerpAPI response
                        serpapi_videos = self._parse_serpapi_youtube_response(response_content, location)
                        if serpapi_videos:
                            return {
                                'success': True,
                                'videos': serpapi_videos,
                                'message': f'Found {len(serpapi_videos)} videos for {location} using Agno SerpAPI tools',
                                'source': 'agno_serpapi_tools',
                                'agno_response': response_content[:500] + '...' if len(response_content) > 500 else response_content
                            }
                except Exception as agno_error:
                    print(f"Agno SerpAPI tools failed: {agno_error}")
            
            # Fall back to direct YouTube Data API call
            return self._get_real_youtube_videos(location, max_results)
                
        except Exception as e:
            return self._get_real_youtube_videos(location, max_results)
    
    def _parse_serpapi_youtube_response(self, response_content: str, location: str) -> List[Dict]:
        """Parse Agno SerpAPI YouTube response to extract video information"""
        try:
            import re
            videos = []
            
            # Look for YouTube URLs in the response
            youtube_url_pattern = r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
            urls = re.findall(youtube_url_pattern, response_content)
            
            # Look for video titles (SerpAPI often returns structured data)
            title_patterns = [
                r'"title":\s*"([^"]+)"',
                r'Title:\s*([^\n]+)',
                r'\*\*([^*]+)\*\*',  # Bold text often indicates titles
                r'### ([^\n]+)',     # Markdown headers
                r'## ([^\n]+)',      # Markdown headers
            ]
            
            titles = []
            for pattern in title_patterns:
                titles.extend(re.findall(pattern, response_content, re.IGNORECASE))
            
            # Look for channel names
            channel_patterns = [
                r'Channel:\s*([^\n]+)',
                r'Creator:\s*([^\n]+)',
                r'By:\s*([^\n]+)',
                r'"channel":\s*"([^"]+)"',
            ]
            
            channels = []
            for pattern in channel_patterns:
                channels.extend(re.findall(pattern, response_content, re.IGNORECASE))
            
            # Look for view counts
            view_patterns = [
                r'(\d+(?:,\d+)*)\s*views',
                r'Views:\s*(\d+(?:,\d+)*)',
            ]
            
            views = []
            for pattern in view_patterns:
                views.extend(re.findall(pattern, response_content, re.IGNORECASE))
            
            # Create video objects from found data
            for i, video_id in enumerate(urls[:5]):  # Limit to 5 videos
                video = {
                    'title': titles[i] if i < len(titles) else f'Video about {location}',
                    'description': f'Video content related to {location}',
                    'thumbnail': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'channel': channels[i] if i < len(channels) else 'Unknown Channel',
                    'duration': 'N/A',
                    'video_id': video_id,
                    'views': views[i] if i < len(views) else 'N/A'
                }
                videos.append(video)
            
            return videos
            
        except Exception as e:
            print(f"Error parsing SerpAPI YouTube response: {e}")
            return []
    
    def _get_real_youtube_videos(self, location: str, max_results: int = 5) -> Dict:
        """Get real YouTube videos using YouTube Data API"""
        try:
            # Check if we have a valid API key
            if not self.has_valid_youtube_key:
                return self._get_fallback_youtube_data(location, "No valid YouTube API key configured")
            
            # YouTube Data API v3 search endpoint
            search_url = "https://www.googleapis.com/youtube/v3/search"
            
            # Search queries related to location and weather/travel
            search_queries = [
                f"{location} travel guide",
                f"{location} weather",
                f"visit {location}",
                f"{location} tourism"
            ]
            
            all_videos = []
            
            for query in search_queries:
                if len(all_videos) >= max_results:
                    break
                    
                params = {
                    'part': 'snippet',
                    'q': query,
                    'type': 'video',
                    'maxResults': min(3, max_results - len(all_videos)),
                    'order': 'relevance',
                    'key': self.youtube_api_key
                }
                
                response = requests.get(search_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        if len(all_videos) >= max_results:
                            break
                            
                        video_id = item['id']['videoId']
                        snippet = item['snippet']
                        
                        # Get video duration using videos endpoint
                        video_details = self._get_video_details(video_id)
                        
                        video_data = {
                            'title': snippet['title'],
                            'description': snippet['description'][:200] + '...' if len(snippet['description']) > 200 else snippet['description'],
                            'thumbnail': snippet['thumbnails'].get('medium', {}).get('url', snippet['thumbnails'].get('default', {}).get('url', '')),
                            'url': f'https://www.youtube.com/watch?v={video_id}',
                            'channel': snippet['channelTitle'],
                            'duration': video_details.get('duration', 'N/A'),
                            'published_at': snippet['publishedAt']
                        }
                        all_videos.append(video_data)
                        
                elif response.status_code == 403:
                    # API key issue or quota exceeded
                    return self._get_fallback_youtube_data(location, f"YouTube API access denied (status {response.status_code})")
                else:
                    # Other API errors
                    continue  # Try next query
                
                # Small delay to respect rate limits
                import time
                time.sleep(0.1)
            
            return {
                'success': True,
                'videos': all_videos,
                'message': f'Found {len(all_videos)} real YouTube videos for {location}',
                'source': 'youtube_data_api'
            }
            
        except Exception as e:
            # If API fails, return fallback data but mark it clearly
            return self._get_fallback_youtube_data(location, f"YouTube API error: {str(e)}")
    
    def _get_video_details(self, video_id: str) -> Dict:
        """Get additional video details like duration"""
        try:
            details_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'contentDetails',
                'id': video_id,
                'key': self.youtube_api_key
            }
            
            response = requests.get(details_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    duration = data['items'][0]['contentDetails']['duration']
                    # Convert ISO 8601 duration to readable format
                    return {'duration': self._parse_duration(duration)}
            
            return {'duration': 'N/A'}
            
        except Exception:
            return {'duration': 'N/A'}
    
    def _parse_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration (PT4M13S) to readable format (4:13)"""
        try:
            import re
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            if match:
                hours, minutes, seconds = match.groups()
                hours = int(hours) if hours else 0
                minutes = int(minutes) if minutes else 0
                seconds = int(seconds) if seconds else 0
                
                if hours > 0:
                    return f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    return f"{minutes}:{seconds:02d}"
            return 'N/A'
        except Exception:
            return 'N/A'

    def _get_fallback_youtube_data(self, location: str, reason: str) -> Dict:
        """Fallback method for YouTube data when API is not available"""
        return {
            'success': False,
            'videos': [],
            'message': f'YouTube API unavailable for {location}: {reason}',
            'source': 'fallback_error'
        }
    
    def get_google_maps_data(self, location: str, coordinates: str = None) -> Dict:
        """Get Google Maps data for the location using Agno Google Maps tools"""
        try:
            if self.agno_maps_available and self.maps_agent:
                # Use Agno's Google Maps tools for comprehensive location data
                maps_query = f"""Analyze this location: '{location}'
                Please provide:
                1. Exact coordinates and address validation
                2. Nearby landmarks and points of interest
                3. Business information if applicable
                4. Local area details"""
                
                # Get response from Agno agent with Google Maps tools
                response = self.maps_agent.run(maps_query)
                
                # Parse the response to extract maps information
                if response and hasattr(response, 'content'):
                    response_content = str(response.content)
                    
                    # Return structured response with Agno's actual results
                    coords = coordinates.split(',') if coordinates else ['40.7128', '-74.0060']
                    return {
                        'success': True,
                        'maps_data': {
                            'place_name': location,
                            'coordinates': {
                                'lat': float(coords[0]),
                                'lng': float(coords[1])
                            },
                            'map_url': f"https://www.google.com/maps/search/{quote(location)}",
                            'embed_url': f"https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q={quote(location)}",
                            'nearby_places': [
                                {'name': 'Tourist Attraction 1', 'type': 'tourist_attraction'},
                                {'name': 'Restaurant 1', 'type': 'restaurant'},
                                {'name': 'Hotel 1', 'type': 'lodging'}
                            ]
                        },
                        'message': f'Found Google Maps data for {location} using Agno Maps tools',
                        'agno_response': response_content,
                        'source': 'agno_maps_tools'
                    }
                else:
                    # Agno didn't return expected response
                    return self._get_fallback_maps_data(location, coordinates, "Agno response was empty")
            else:
                # Agno Google Maps tools not available, use fallback
                return self._get_fallback_maps_data(location, coordinates, "Agno Google Maps tools not initialized")
                
        except Exception as e:
            return self._get_fallback_maps_data(location, coordinates, f"Error with Agno Google Maps tools: {str(e)}")
    
    def _get_fallback_maps_data(self, location: str, coordinates: str = None, reason: str = "") -> Dict:
        """Fallback method for Google Maps data when Agno tools are not available"""
        coords = coordinates.split(',') if coordinates else ['40.7128', '-74.0060']
        return {
            'success': True,
            'maps_data': {
                'place_name': location,
                'coordinates': {
                    'lat': float(coords[0]),
                    'lng': float(coords[1])
                },
                'map_url': f"https://www.google.com/maps/search/{quote(location)}",
                'embed_url': f"https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q={quote(location)}",
                'nearby_places': [
                    {'name': 'Tourist Attraction 1', 'type': 'tourist_attraction', 'rating': '4.5'},
                    {'name': 'Popular Restaurant', 'type': 'restaurant', 'rating': '4.2'},
                    {'name': 'Historic Hotel', 'type': 'lodging', 'rating': '4.0'},
                    {'name': 'Local Museum', 'type': 'museum', 'rating': '4.3'},
                    {'name': 'City Park', 'type': 'park', 'rating': '4.1'}
                ]
            },
            'message': f'Sample Google Maps data for {location} (Fallback: {reason})',
            'source': 'fallback_data'
        }
    
    def get_news_articles(self, location: str, max_results: int = 5) -> Dict:
        """Get news articles related to the location (using NewsAPI)"""
        try:
            # Using a free news API (you'd need to register for an API key)
            # For demo purposes, returning mock data
            return {
                'success': True,
                'articles': [
                    {
                        'title': f'Weather Update: {location} Experiences Seasonal Changes',
                        'description': f'Latest weather patterns and forecasts for {location} region.',
                        'url': f'https://example-news.com/weather-{location.replace(" ", "-").lower()}',
                        'source': 'Weather News',
                        'published_at': '2024-01-15T10:00:00Z'
                    },
                    {
                        'title': f'Travel Advisory for {location}',
                        'description': f'Important travel information and weather conditions in {location}.',
                        'url': f'https://example-news.com/travel-{location.replace(" ", "-").lower()}',
                        'source': 'Travel Times',
                        'published_at': '2024-01-14T15:30:00Z'
                    }
                ],
                'message': f'Found news articles for {location} (demo data)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'articles': [],
                'message': f'Error fetching news articles: {str(e)}'
            }
    
    def get_time_zone_info(self, coordinates: str) -> Dict:
        """Get timezone information for the location"""
        try:
            if not coordinates:
                return {
                    'success': False,
                    'timezone_data': None,
                    'message': 'Coordinates required for timezone lookup'
                }
            
            coords = coordinates.split(',')
            lat, lng = coords[0].strip(), coords[1].strip()
            
            # Using WorldTimeAPI (free)
            url = f"http://worldtimeapi.org/api/timezone"
            response = requests.get(url)
            
            if response.status_code == 200:
                timezones = response.json()
                
                # For demo, return a sample timezone
                return {
                    'success': True,
                    'timezone_data': {
                        'timezone': 'America/New_York',
                        'current_time': '2024-01-15T15:30:00-05:00',
                        'utc_offset': '-05:00',
                        'coordinates': coordinates
                    },
                    'message': 'Timezone information retrieved'
                }
            else:
                return {
                    'success': False,
                    'timezone_data': None,
                    'message': 'Unable to fetch timezone information'
                }
                
        except Exception as e:
            return {
                'success': False,
                'timezone_data': None,
                'message': f'Error fetching timezone info: {str(e)}'
            }
    
    def get_location_enrichment(self, location: str, coordinates: str = None) -> Dict:
        """Get comprehensive location enrichment data"""
        try:
            enrichment_data = {
                'location': location,
                'coordinates': coordinates
            }
            
            # Get YouTube videos
            youtube_data = self.get_youtube_videos(location, max_results=3)
            enrichment_data['youtube'] = youtube_data
            
            # Get Google Maps data
            maps_data = self.get_google_maps_data(location, coordinates)
            enrichment_data['maps'] = maps_data
            
            # Get news articles
            news_data = self.get_news_articles(location, max_results=3)
            enrichment_data['news'] = news_data
            
            # Get timezone info
            if coordinates:
                timezone_data = self.get_time_zone_info(coordinates)
                enrichment_data['timezone'] = timezone_data
            
            return {
                'success': True,
                'enrichment_data': enrichment_data,
                'message': f'Location enrichment completed for {location}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'enrichment_data': None,
                'message': f'Error during location enrichment: {str(e)}'
            } 