#!/usr/bin/env python3
"""
Test script for YouTube API integration
Run this to test if the YouTube feature is working properly
"""

import os
import sys
from api_integrations import APIIntegrations

def test_youtube_integration():
    """Test the YouTube API integration"""
    print("Testing YouTube API Integration...")
    print("=" * 50)
    
    # Initialize API integrations
    api = APIIntegrations()
    
    # Check API key status
    print(f"YouTube API Key configured: {api.has_valid_youtube_key}")
    print(f"Agno YouTube tools available: {api.agno_youtube_available}")
    print()
    
    # Test with a sample location
    test_location = "Tokyo"
    print(f"Testing with location: {test_location}")
    print("-" * 30)
    
    try:
        result = api.get_youtube_videos(test_location, max_results=3)
        
        print(f"Success: {result['success']}")
        print(f"Source: {result['source']}")
        print(f"Message: {result['message']}")
        print(f"Number of videos: {len(result['videos'])}")
        print()
        
        if result['videos']:
            print("Sample videos found:")
            for i, video in enumerate(result['videos'][:2], 1):
                print(f"{i}. {video['title']}")
                print(f"   Channel: {video['channel']}")
                print(f"   URL: {video['url']}")
                print(f"   Duration: {video['duration']}")
                print()
        else:
            print("No videos returned")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

def check_environment():
    """Check environment setup"""
    print("Environment Check:")
    print("=" * 50)
    
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    if youtube_key:
        print(f"✓ YOUTUBE_API_KEY is set (length: {len(youtube_key)})")
    else:
        print("✗ YOUTUBE_API_KEY is not set")
        print("  Set it with: export YOUTUBE_API_KEY=your_api_key")
    
    maps_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if maps_key:
        print(f"✓ GOOGLE_MAPS_API_KEY is set (length: {len(maps_key)})")
    else:
        print("✗ GOOGLE_MAPS_API_KEY is not set")
        print("  Set it with: export GOOGLE_MAPS_API_KEY=your_api_key")
    
    print()

if __name__ == "__main__":
    check_environment()
    test_youtube_integration()
    
    print("\nTo get real YouTube videos:")
    print("1. Get a YouTube Data API v3 key from: https://console.developers.google.com/")
    print("2. Set the environment variable: export YOUTUBE_API_KEY=your_actual_key")
    print("3. Run this test again") 