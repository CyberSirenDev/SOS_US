import os
import aiohttp
import asyncio
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import tweepy
import re
import time

load_dotenv()

class TwitterClient:
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
        self.consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Real-time streaming attributes (SIMPLIFIED)
        self.recent_posts = []
        self.max_recent_posts = 200
        self.stream_callbacks = []
        self.is_streaming = False
        self.last_stream_check = None
        
        print("🔄 Initializing Twitter Client...")
        
        # Test API connectivity
        self.api_available = self._test_api_connectivity()
        
        # Enhanced sample data
        self.sample_posts = [
            "Just implemented the new AI feature and it's revolutionary! The accuracy is incredible. #AI #Innovation",
            "Frustrated with the latest update. The UI became so confusing and performance dropped significantly. #Disappointed",
            "Weather today is perfect for coding. Working on some new features for our sentiment analysis tool. #Programming",
            "The machine learning model training is going well. Validation accuracy reached 95%! #MachineLearning #Success",
            "Server downtime again! This is affecting our production environment. Need immediate fix. #TechIssues",
        ]

    def _test_api_connectivity(self):
        """Test if Twitter API credentials work"""
        if not self.bearer_token:
            print("⚠️ No Twitter Bearer Token found")
            return False
        
        try:
            # Simple test with tweepy
            client = tweepy.Client(bearer_token=self.bearer_token)
            # Try a simple search to test connectivity
            response = client.search_recent_tweets(query="test", max_results=1)
            print("✅ Twitter API connectivity confirmed")
            return True
        except Exception as e:
            print(f"❌ Twitter API test failed: {e}")
            return False

    async def fetch_real_posts(self, query, limit=50):
        """Fetch real posts from Twitter with proper error handling"""
        print(f"🔍 Fetching posts for: '{query}' (limit: {limit})")
        
        if not self.api_available:
            print("⚠️ API not available, using simulated data")
            return await self.fetch_simulated_posts(query, limit)
        
        try:
            return await self._fetch_v2_posts_safe(query, limit)
        except Exception as e:
            print(f"❌ Twitter API error: {e}")
            return await self.fetch_simulated_posts(query, limit)

    async def _fetch_v2_posts_safe(self, query, limit):
        """Safe Twitter API v2 implementation"""
        try:
            client = tweepy.Client(bearer_token=self.bearer_token)
            
            clean_query = self._clean_query(query) + " -is:retweet lang:en"
            
            response = client.search_recent_tweets(
                query=clean_query,
                max_results=min(limit, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                user_fields=['username', 'verified'],
                expansions=['author_id']
            )
            
            if not response.data:
                raise Exception("No tweets found")
            
            posts = []
            users = {}
            if response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            for tweet in response.data:
                user = users.get(tweet.author_id)
                posts.append({
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                    'likes': tweet.public_metrics.get('like_count', 0),
                    'retweets': tweet.public_metrics.get('retweet_count', 0),
                    'user': user.username if user else 'unknown',
                    'verified': user.verified if user else False,
                    'id': str(tweet.id),
                    'source': 'twitter_v2'
                })
            
            return posts
            
        except Exception as e:
            raise Exception(f"Twitter API v2 error: {e}")

    def _clean_query(self, query):
        """Clean query for Twitter API"""
        return re.sub(r'[^\w\s#@]', '', query).strip()

    # SIMPLIFIED REAL-TIME STREAMING (Using polling instead of actual streaming)
    def start_real_time_stream(self, query, callback_function):
        """Start simulated real-time streaming using polling"""
        try:
            self.stream_query = query
            self.stream_callbacks.append(callback_function)
            self.is_streaming = True
            self.last_stream_check = datetime.now()
            
            print(f"✅ Real-time polling started for: '{query}'")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start streaming: {e}")
            return False

    async def check_stream_updates(self):
        """Check for new posts (polling-based real-time)"""
        if not self.is_streaming:
            return []
        
        try:
            # Fetch new posts every 30 seconds
            if self.last_stream_check and (datetime.now() - self.last_stream_check).total_seconds() < 300:
                return []
            
            new_posts = await self.fetch_real_posts(self.stream_query, 10)
            self.last_stream_check = datetime.now()
            
            # Process new posts through callbacks
            for post in new_posts:
                post['real_time'] = True
                for callback in self.stream_callbacks:
                    try:
                        callback(post)
                    except Exception as e:
                        print(f"❌ Callback error: {e}")
            
            return new_posts
            
        except Exception as e:
            print(f"❌ Stream update error: {e}")
            return []

    def stop_stream(self):
        """Stop the real-time stream"""
        self.is_streaming = False
        self.stream_callbacks.clear()
        print("✅ Real-time stream stopped")

    def add_stream_callback(self, callback_function):
        """Add a callback function for new posts"""
        self.stream_callbacks.append(callback_function)

    # SIMULATED DATA METHODS (Enhanced Fallback)
    async def fetch_simulated_posts(self, query, limit=50):
        """Generate realistic simulated posts"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        posts = []
        base_time = datetime.utcnow()
        
        # Topic-specific sentiment distributions
        topic_sentiments = {
            "technology": {"positive": 0.6, "neutral": 0.3, "negative": 0.1},
            "ai": {"positive": 0.7, "neutral": 0.2, "negative": 0.1},
            "crypto": {"positive": 0.5, "neutral": 0.3, "negative": 0.2},
            "politics": {"positive": 0.3, "neutral": 0.4, "negative": 0.3},
        }
        
        # Determine topic
        current_topic = "technology"
        for topic in topic_sentiments.keys():
            if topic in query.lower():
                current_topic = topic
                break
        
        sentiment_dist = topic_sentiments.get(current_topic, {"positive": 0.5, "neutral": 0.3, "negative": 0.2})
        
        for i in range(limit):
            # Determine sentiment
            rand_val = random.random()
            if rand_val < sentiment_dist["positive"]:
                sentiment = "positive"
                text = f"Amazing developments in {query}! The future looks bright. #{current_topic.title()}"
            elif rand_val < sentiment_dist["positive"] + sentiment_dist["neutral"]:
                sentiment = "neutral"
                text = f"Interesting analysis of {query} trends. Monitoring developments. #{current_topic.title()}"
            else:
                sentiment = "negative"
                text = f"Concerns about {query} implementation. Need improvements. #{current_topic.title()}"
            
            # Random timestamp
            time_offset = timedelta(minutes=random.randint(0, 1440))  # Last 24 hours
            post_time = base_time - time_offset
            
            posts.append({
                'text': text,
                'created_at': post_time.isoformat(),
                'likes': random.randint(0, 100),
                'retweets': random.randint(0, 50),
                'user': f"user_{random.randint(1000, 9999)}",
                'verified': random.random() < 0.2,
                'source': 'simulated',
                'real_time': False
            })
        
        print(f"📊 Generated {len(posts)} simulated posts for '{query}'")
        return posts

# Test function
async def test_twitter_client():
    client = TwitterClient()
    posts = await client.fetch_real_posts("AI technology", 3)
    print(f"✅ Test completed: {len(posts)} posts fetched")

if __name__ == "__main__":
    asyncio.run(test_twitter_client())