#!/usr/bin/env python3
"""
Test script for the FIXED YouTube API integration
Now uses SerpAPI for proper YouTube video search
"""

import os
from api_integrations import APIIntegrations

def test_youtube_fix():
    print("🔧 Testing FIXED YouTube API Integration")
    print("=" * 60)
    
    # Test the new implementation
    print("1. Testing current implementation:")
    api = APIIntegrations()
    
    # Check what's available
    serpapi_key = os.getenv('SERPAPI_API_KEY')
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    
    print(f"   SerpAPI key configured: {'✓' if serpapi_key else '✗'}")
    print(f"   YouTube API key configured: {'✓' if youtube_key else '✗'}")
    print(f"   Agno SerpAPI available: {'✓' if api.agno_serpapi_available else '✗'}")
    print()
    
    # Test with Tokyo
    test_location = "Tokyo"
    print(f"2. Testing with location: {test_location}")
    print("-" * 40)
    
    try:
        result = api.get_youtube_videos(test_location, max_results=3)
        
        print(f"   Success: {result['success']}")
        print(f"   Source: {result['source']}")
        print(f"   Message: {result['message']}")
        print(f"   Videos returned: {len(result['videos'])}")
        print()
        
        if result['videos']:
            print("   Sample videos found:")
            for i, video in enumerate(result['videos'][:2], 1):
                print(f"   {i}. {video['title']}")
                print(f"      Channel: {video['channel']}")
                print(f"      URL: {video['url']}")
                print(f"      Duration: {video['duration']}")
                print()
        else:
            print("   No videos returned")
            
    except Exception as e:
        print(f"   Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

def show_setup_instructions():
    print("\n" + "=" * 60)
    print("🚀 SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📋 OPTION 1: SerpAPI (Recommended - 100 free searches/month)")
    print("   1. Go to https://serpapi.com/")
    print("   2. Sign up for free account")
    print("   3. Get your API key")
    print("   4. Set environment variable:")
    print("      Windows: $env:SERPAPI_API_KEY='your_key_here'")
    print("      Linux/Mac: export SERPAPI_API_KEY='your_key_here'")
    print("   5. Install dependency: pip install google-search-results")
    
    print("\n📋 OPTION 2: YouTube Data API v3 (Alternative)")
    print("   1. Go to https://console.developers.google.com/")
    print("   2. Create project and enable YouTube Data API v3")
    print("   3. Create API key")
    print("   4. Set environment variable:")
    print("      Windows: $env:YOUTUBE_API_KEY='your_key_here'")
    print("      Linux/Mac: export YOUTUBE_API_KEY='your_key_here'")
    
    print("\n🎯 WHAT'S FIXED:")
    print("   ❌ Before: Fake URLs like 'youtube.com/watch?v=example_Tokyo'")
    print("   ✅ After: Real YouTube videos OR proper error messages")
    print("   ✅ Uses correct Agno SerpAPI tools for YouTube search")
    print("   ✅ Falls back to direct YouTube API if needed")

if __name__ == "__main__":
    test_youtube_fix()
    show_setup_instructions() 