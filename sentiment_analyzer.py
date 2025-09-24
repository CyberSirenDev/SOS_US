import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import asyncio
import re

class SentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        print("✅ Basic Sentiment Analyzer initialized")

    def classify_sentiment(self, text):
        """Classify sentiment using VADER"""
        try:
            if not text or not isinstance(text, str) or len(text.strip()) == 0:
                return 'neutral', 0.0
            
            # VADER analysis
            vader_scores = self.vader_analyzer.polarity_scores(text)
            compound_score = vader_scores['compound']
            
            # Enhanced classification with TextBlob fallback
            try:
                blob = TextBlob(text)
                blob_polarity = blob.sentiment.polarity
                # Combine VADER and TextBlob scores
                combined_score = (compound_score + blob_polarity) / 2
            except:
                combined_score = compound_score
            
            # Determine sentiment
            if combined_score > 0.05:
                sentiment = 'positive'
            elif combined_score < -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return sentiment, combined_score
            
        except Exception as e:
            print(f"❌ Error in sentiment classification: {e}")
            return 'neutral', 0.0

    def analyze_posts(self, posts):
        """Basic sentiment analysis for posts"""
        if not posts:
            return {
                'total_posts': 0,
                'sentiment_counts': {'positive': 0, 'neutral': 0, 'negative': 0},
                'sentiment_percentages': {'positive': 0, 'neutral': 0, 'negative': 0},
                'overall_sentiment': 'neutral',
                'average_score': 0.0
            }, pd.DataFrame(), pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(posts)
        
        # Analyze sentiment for each post
        sentiment_results = []
        scores = []
        
        for text in df['text']:
            sentiment, score = self.classify_sentiment(text)
            sentiment_results.append(sentiment)
            scores.append(score)
        
        df['sentiment'] = sentiment_results
        df['score'] = scores
        
        # Add timestamp if not present
        if 'created_at' not in df.columns:
            df['created_at'] = [datetime.now() - timedelta(hours=i) for i in range(len(df))]
        
        # Convert created_at to datetime if it's string
        if df['created_at'].dtype == 'object':
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            # Fill NaT with current time
            df['created_at'] = df['created_at'].fillna(datetime.now())
        
        # Calculate summary statistics
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        total_posts = len(df)
        
        sentiment_percentages = {
            'positive': (sentiment_counts.get('positive', 0) / total_posts) * 100,
            'neutral': (sentiment_counts.get('neutral', 0) / total_posts) * 100,
            'negative': (sentiment_counts.get('negative', 0) / total_posts) * 100
        }
        
        # Determine overall sentiment
        if sentiment_percentages['positive'] > sentiment_percentages['negative']:
            overall_sentiment = 'positive'
        elif sentiment_percentages['negative'] > sentiment_percentages['positive']:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        average_score = np.mean(scores) if scores else 0.0
        
        # Generate trends by hour
        df['hour'] = df['created_at'].dt.hour
        trends = df.groupby(['hour', 'sentiment']).size().unstack(fill_value=0)
        
        # Ensure all sentiment columns exist
        for sentiment in ['positive', 'neutral', 'negative']:
            if sentiment not in trends.columns:
                trends[sentiment] = 0
        
        summary = {
            'total_posts': total_posts,
            'sentiment_counts': sentiment_counts,
            'sentiment_percentages': sentiment_percentages,
            'overall_sentiment': overall_sentiment,
            'average_score': average_score
        }
        
        return summary, trends, df

class EnhancedSentimentAnalyzer(SentimentAnalyzer):
    def __init__(self, gemini_analyzer=None):
        super().__init__()
        self.gemini_analyzer = gemini_analyzer
        print("✅ Enhanced Sentiment Analyzer initialized")

    async def analyze_posts_enhanced(self, posts_df):
        """Enhanced analysis with Gemini AI integration"""
        # Get basic analysis
        basic_summary, trends, detailed_df = self.analyze_posts(posts_df.to_dict('records'))
        
        # Gemini AI analysis for selected posts
        gemini_analyses = {}
        if self.gemini_analyzer and self.gemini_analyzer.is_available:
            try:
                # Analyze top 5 posts with highest absolute sentiment scores
                if not detailed_df.empty:
                    top_posts = detailed_df.nlargest(5, 'score') if len(detailed_df) >= 5 else detailed_df
                    gemini_analyses = await self.gemini_analyzer.analyze_batch_posts(
                        top_posts.to_dict('records'), 
                        max_analyze=min(5, len(top_posts))
                    )
            except Exception as e:
                print(f"❌ Gemini analysis failed: {e}")
        
        return basic_summary, trends, detailed_df, gemini_analyses

    def detect_emotions(self, text):
        """Basic emotion detection"""
        emotions = {
            'joy': ['happy', 'excited', 'great', 'amazing', 'wonderful', 'love', 'excellent'],
            'anger': ['angry', 'frustrated', 'mad', 'annoyed', 'outraged', 'hate'],
            'sadness': ['sad', 'disappointed', 'unhappy', 'depressed', 'terrible', 'awful'],
            'fear': ['scared', 'worried', 'anxious', 'nervous', 'concerned', 'afraid'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'unexpected']
        }
        
        detected_emotions = []
        text_lower = text.lower()
        
        for emotion, keywords in emotions.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions if detected_emotions else ['neutral']

# Test the sentiment analyzer
def test_sentiment_analyzer():
    analyzer = SentimentAnalyzer()
    
    test_posts = [
        {"text": "I love this product! It's absolutely amazing!"},
        {"text": "This is terrible. Worst experience ever."},
        {"text": "The weather is nice today. Nothing special."},
        {"text": "Incredible performance and outstanding results!"},
        {"text": "Very disappointed with the service quality."}
    ]
    
    print("Testing Sentiment Analyzer:")
    summary, trends, df = analyzer.analyze_posts(test_posts)
    
    print(f"\nSummary:")
    print(f"Total posts: {summary['total_posts']}")
    print(f"Sentiment distribution: {summary['sentiment_percentages']}")
    print(f"Overall sentiment: {summary['overall_sentiment']}")
    
    print(f"\nSample analysis:")
    for i, row in df.iterrows():
        print(f"{i+1}. {row['text'][:50]}... -> {row['sentiment']} (score: {row['score']:.2f})")

if __name__ == "__main__":
    test_sentiment_analyzer()