#!/usr/bin/env python3
"""
Test script for the SOS_US Real-Time Social Sentiment Analyzer
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_sentiment_analysis():
    """Test sentiment analysis with various inputs"""
    print("🧪 Testing sentiment analysis...")
    
    test_cases = [
        ("I love this amazing product!", "positive"),
        ("This is terrible and awful", "negative"), 
        ("The weather is okay", "neutral"),
        ("Amazing! Best thing ever! Love it!", "positive"),
        ("Hate this so much, worst ever", "negative"),
        ("It's just okay, nothing special", "neutral")
    ]
    
    for text, expected_sentiment in test_cases:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            headers={"Content-Type": "application/json"},
            json={"text": text}
        )
        
        if response.status_code == 200:
            result = response.json()
            actual_sentiment = result["sentiment"]
            polarity = result["polarity"]
            
            status = "✅ PASS" if actual_sentiment == expected_sentiment else "❌ FAIL"
            print(f"{status} '{text}' -> {actual_sentiment} (polarity: {polarity:.2f}, expected: {expected_sentiment})")
        else:
            print(f"❌ API ERROR for '{text}': {response.status_code}")

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🌐 Testing API endpoints...")
    
    # Test stats endpoint
    response = requests.get(f"{BASE_URL}/api/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Stats API: {stats}")
    else:
        print(f"❌ Stats API error: {response.status_code}")
    
    # Test recent posts endpoint
    response = requests.get(f"{BASE_URL}/api/recent")
    if response.status_code == 200:
        posts = response.json()
        print(f"✅ Recent posts API: {len(posts)} posts retrieved")
    else:
        print(f"❌ Recent posts API error: {response.status_code}")

def test_web_interface():
    """Test that web interface loads"""
    print("\n🖥️ Testing web interface...")
    
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        if "SOS_US" in response.text and "Social Sentiment Analyzer" in response.text:
            print("✅ Web interface loads successfully")
        else:
            print("❌ Web interface content missing")
    else:
        print(f"❌ Web interface error: {response.status_code}")

if __name__ == "__main__":
    print("🚨 SOS_US Real-Time Social Sentiment Analyzer - Test Suite")
    print("=" * 60)
    
    try:
        test_sentiment_analysis()
        test_api_endpoints()
        test_web_interface()
        print("\n🎉 All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running at http://localhost:5000")
    except Exception as e:
        print(f"❌ Test error: {e}")