# test_fixes.py
import asyncio
import os
from dotenv import load_dotenv
from twitter_client import TwitterClient
from gemini_analyzer import GeminiSentimentAnalyzer

load_dotenv()

async def test_fixes():
    print("🧪 Testing fixes...")
    
    # Test Gemini
    print("1. Testing Gemini API...")
    gemini = GeminiSentimentAnalyzer()
    if gemini.is_available:
        test_text = "I love this product! It's amazing!"
        result = await gemini.analyze_sentiment_detailed(test_text)
        print(f"✅ Gemini working: {result.get('sentiment', 'Unknown')}")
    else:
        print("❌ Gemini not available")
    
    # Test Twitter
    print("2. Testing Twitter API...")
    twitter = TwitterClient()
    posts = await twitter.fetch_real_posts("technology", 5)
    print(f"✅ Twitter fetched {len(posts)} posts")
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_fixes())