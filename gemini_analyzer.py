import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import asyncio
import aiohttp
import json
from datetime import datetime

load_dotenv()

class GeminiSentimentAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.is_available = bool(self.api_key)
        
        if self.is_available:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"❌ Gemini AI initialization failed: {e}")
                self.is_available = False
        else:
            print("⚠️ Gemini API key not found. Using fallback analysis.")
    
    async def analyze_sentiment_detailed(self, text):
        """Get detailed sentiment analysis using Gemini AI"""
        if not self.is_available:
            return self._fallback_analysis(text)
        
        try:
            prompt = f"""
            Analyze the following social media post for sentiment and provide a detailed analysis:
            
            Post: "{text}"
            
            Please provide analysis in this JSON format:
            {{
                "sentiment": "positive/neutral/negative",
                "confidence": 0.0-1.0,
                "emotional_tone": ["adjective1", "adjective2"],
                "key_topics": ["topic1", "topic2"],
                "summary": "brief summary of sentiment",
                "reasoning": "explanation of why this sentiment was determined",
                "intensity": "low/medium/high"
            }}
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.model.generate_content(prompt)
            )
            
            # Extract JSON from response
            response_text = response.text
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].strip()
            else:
                json_str = response_text.strip()
            
            analysis = json.loads(json_str)
            return analysis
            
        except Exception as e:
            print(f"❌ Gemini analysis failed: {e}")
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text):
        """Fallback analysis when Gemini is unavailable"""
        from textblob import TextBlob
        
        # Use TextBlob for fallback
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Determine sentiment
        if polarity > 0.1:
            sentiment = "positive"
            confidence = min((polarity + 1) / 2, 0.85)
        elif polarity < -0.1:
            sentiment = "negative"
            confidence = min((abs(polarity) + 1) / 2, 0.85)
        else:
            sentiment = "neutral"
            confidence = 0.7
        
        # Simple topic extraction
        words = text.lower().split()
        key_topics = [word for word in words if len(word) > 4 and word.isalpha()][:3]
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "emotional_tone": self._get_emotional_tone(text, sentiment),
            "key_topics": key_topics,
            "summary": f"Text appears {sentiment} based on linguistic analysis",
            "reasoning": f"Determined through polarity analysis (polarity: {polarity:.2f})",
            "intensity": "high" if abs(polarity) > 0.5 else "medium" if abs(polarity) > 0.2 else "low"
        }
    
    def _get_emotional_tone(self, text, sentiment):
        """Extract emotional tone from text"""
        emotional_words = {
            "positive": ["excited", "happy", "optimistic", "enthusiastic", "pleased"],
            "negative": ["frustrated", "angry", "disappointed", "concerned", "annoyed"],
            "neutral": ["curious", "interested", "observant", "contemplative", "analytical"]
        }
        
        text_lower = text.lower()
        tone_words = []
        
        for word in emotional_words.get(sentiment, []):
            if word in text_lower:
                tone_words.append(word)
        
        # Add some default tones if none found
        if not tone_words:
            tone_words = emotional_words.get(sentiment, [])[:2]
        
        return tone_words
    
    async def analyze_batch_posts(self, posts, max_analyze=10):
        """Analyze a batch of posts (limit to avoid rate limits)"""
        if not self.is_available:
            return {}
        
        analyzed_posts = {}
        tasks = []
        
        # Limit the number of posts to analyze with Gemini
        posts_to_analyze = posts[:max_analyze]
        
        for i, post in enumerate(posts_to_analyze):
            if isinstance(post, dict) and 'text' in post:
                task = self.analyze_sentiment_detailed(post['text'])
                tasks.append((i, task))
        
        # Process analyses concurrently
        for i, task in tasks:
            try:
                analysis = await task
                analyzed_posts[i] = analysis
            except Exception as e:
                print(f"Error analyzing post {i}: {e}")
                analyzed_posts[i] = self._fallback_analysis(posts[i]['text'])
        
        return analyzed_posts

# Test the Gemini analyzer
async def test_gemini_analyzer():
    analyzer = GeminiSentimentAnalyzer()
    
    test_posts = [
        {"text": "I absolutely love this new feature! It's revolutionary and works perfectly!"},
        {"text": "This update is terrible. Everything is broken and slow."},
        {"text": "The weather is nice today. Working on some code updates."}
    ]
    
    print("Testing Gemini AI Sentiment Analyzer:")
    for i, post in enumerate(test_posts):
        analysis = await analyzer.analyze_sentiment_detailed(post['text'])
        print(f"\n{i+1}. {post['text']}")
        print(f"   Sentiment: {analysis['sentiment']} (Confidence: {analysis['confidence']})")
        print(f"   Topics: {analysis['key_topics']}")

if __name__ == "__main__":
    asyncio.run(test_gemini_analyzer())