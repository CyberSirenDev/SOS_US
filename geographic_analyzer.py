import pandas as pd
import re
import asyncio
from collections import defaultdict
import random

class GeographicSentimentAnalyzer:
    def __init__(self):
        self.country_keywords = {
            'usa': ['usa', 'united states', 'us', 'america', 'new york', 'california', 'texas', 'florida'],
            'uk': ['uk', 'united kingdom', 'britain', 'london', 'england', 'scotland', 'wales'],
            'canada': ['canada', 'toronto', 'vancouver', 'montreal', 'ottawa'],
            'australia': ['australia', 'sydney', 'melbourne', 'brisbane', 'perth'],
            'germany': ['germany', 'berlin', 'munich', 'frankfurt', 'hamburg'],
            'france': ['france', 'paris', 'lyon', 'marseille', 'toulouse'],
            'spain': ['spain', 'madrid', 'barcelona', 'valencia', 'seville'],
            'italy': ['italy', 'rome', 'milan', 'naples', 'turin'],
            'japan': ['japan', 'tokyo', 'osaka', 'kyoto', 'yokohama'],
            'china': ['china', 'beijing', 'shanghai', 'hong kong', 'shenzhen'],
            'india': ['india', 'mumbai', 'delhi', 'bangalore', 'chennai'],
            'brazil': ['brazil', 'sao paulo', 'rio de janeiro', 'brasilia', 'salvador'],
            'mexico': ['mexico', 'mexico city', 'guadalajara', 'monterrey', 'puebla'],
            'russia': ['russia', 'moscow', 'saint petersburg', 'novosibirsk', 'yekaterinburg']
        }
        
        self.country_coordinates = {
            'usa': {'lat': 37.0902, 'lon': -95.7129, 'region': 'North America'},
            'uk': {'lat': 55.3781, 'lon': -3.4360, 'region': 'Europe'},
            'canada': {'lat': 56.1304, 'lon': -106.3468, 'region': 'North America'},
            'australia': {'lat': -25.2744, 'lon': 133.7751, 'region': 'Oceania'},
            'germany': {'lat': 51.1657, 'lon': 10.4515, 'region': 'Europe'},
            'france': {'lat': 46.6034, 'lon': 1.8883, 'region': 'Europe'},
            'spain': {'lat': 40.4637, 'lon': -3.7492, 'region': 'Europe'},
            'italy': {'lat': 41.8719, 'lon': 12.5674, 'region': 'Europe'},
            'japan': {'lat': 36.2048, 'lon': 138.2529, 'region': 'Asia'},
            'china': {'lat': 35.8617, 'lon': 104.1954, 'region': 'Asia'},
            'india': {'lat': 20.5937, 'lon': 78.9629, 'region': 'Asia'},
            'brazil': {'lat': -14.2350, 'lon': -51.9253, 'region': 'South America'},
            'mexico': {'lat': 23.6345, 'lon': -102.5528, 'region': 'North America'},
            'russia': {'lat': 61.5240, 'lon': 105.3188, 'region': 'Europe/Asia'}
        }
        
        print("✅ Geographic Sentiment Analyzer initialized")

    def extract_location(self, text):
        """Extract location mentions from text"""
        text_lower = text.lower()
        detected_countries = []
        
        for country, keywords in self.country_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_countries.append(country)
        
        # Also look for city-country patterns
        city_patterns = {
            'new york': 'usa', 'los angeles': 'usa', 'chicago': 'usa',
            'london': 'uk', 'manchester': 'uk', 'birmingham': 'uk',
            'toronto': 'canada', 'vancouver': 'canada', 'montreal': 'canada',
            'sydney': 'australia', 'melbourne': 'australia', 'brisbane': 'australia',
            'berlin': 'germany', 'munich': 'germany', 'hamburg': 'germany',
            'paris': 'france', 'lyon': 'france', 'marseille': 'france',
            'madrid': 'spain', 'barcelona': 'spain', 'valencia': 'spain',
            'rome': 'italy', 'milan': 'italy', 'naples': 'italy',
            'tokyo': 'japan', 'osaka': 'japan', 'kyoto': 'japan',
            'beijing': 'china', 'shanghai': 'china', 'hong kong': 'china',
            'mumbai': 'india', 'delhi': 'india', 'bangalore': 'india',
            'sao paulo': 'brazil', 'rio de janeiro': 'brazil', 'brasilia': 'brazil',
            'mexico city': 'mexico', 'guadalajara': 'mexico', 'monterrey': 'mexico',
            'moscow': 'russia', 'saint petersburg': 'russia', 'novosibirsk': 'russia'
        }
        
        for city, country in city_patterns.items():
            if city in text_lower:
                detected_countries.append(country)
        
        # Remove duplicates
        detected_countries = list(set(detected_countries))
        
        return detected_countries[0] if detected_countries else None

    async def analyze_posts_geographic(self, posts, sentiment_df):
        """Analyze geographic distribution of sentiments"""
        if not posts or sentiment_df.empty:
            return {
                'total_posts': 0,
                'total_located_posts': 0,
                'country_sentiments': {},
                'regional_sentiments': {},
                'coverage_percentage': 0
            }
        
        country_sentiments = defaultdict(lambda: {
            'total_posts': 0,
            'positive': 0,
            'neutral': 0,
            'negative': 0,
            'sentiment_distribution': {},
            'average_score': 0.0,
            'coordinates': None
        })
        
        located_posts = 0
        
        for i, post in enumerate(posts):
            if i >= len(sentiment_df):
                continue
                
            text = post.get('text', '')
            country = self.extract_location(text)
            
            if country:
                located_posts += 1
                sentiment = sentiment_df.iloc[i]['sentiment'] if i < len(sentiment_df) else 'neutral'
                score = sentiment_df.iloc[i]['score'] if i < len(sentiment_df) else 0.0
                
                country_sentiments[country]['total_posts'] += 1
                country_sentiments[country][sentiment] += 1
                
                # Update average score
                current_avg = country_sentiments[country]['average_score']
                current_count = country_sentiments[country]['total_posts']
                country_sentiments[country]['average_score'] = (
                    (current_avg * (current_count - 1) + score) / current_count
                )
                
                # Set coordinates
                if country in self.country_coordinates:
                    country_sentiments[country]['coordinates'] = self.country_coordinates[country]
        
        # Calculate sentiment distributions for each country
        for country, data in country_sentiments.items():
            total = data['total_posts']
            if total > 0:
                data['sentiment_distribution'] = {
                    'positive': (data['positive'] / total) * 100,
                    'neutral': (data['neutral'] / total) * 100,
                    'negative': (data['negative'] / total) * 100
                }
        
        # Aggregate by region
        regional_sentiments = defaultdict(lambda: {
            'total_posts': 0,
            'positive': 0,
            'neutral': 0,
            'negative': 0,
            'sentiment_distribution': {},
            'countries': []
        })
        
        for country, data in country_sentiments.items():
            if country in self.country_coordinates:
                region = self.country_coordinates[country]['region']
                regional_sentiments[region]['total_posts'] += data['total_posts']
                regional_sentiments[region]['positive'] += data['positive']
                regional_sentiments[region]['neutral'] += data['neutral']
                regional_sentiments[region]['negative'] += data['negative']
                regional_sentiments[region]['countries'].append(country)
        
        # Calculate regional distributions
        for region, data in regional_sentiments.items():
            total = data['total_posts']
            if total > 0:
                data['sentiment_distribution'] = {
                    'positive': (data['positive'] / total) * 100,
                    'neutral': (data['neutral'] / total) * 100,
                    'negative': (data['negative'] / total) * 100
                }
        
        coverage_percentage = (located_posts / len(posts)) * 100
        
        return {
            'total_posts': len(posts),
            'total_located_posts': located_posts,
            'country_sentiments': dict(country_sentiments),
            'regional_sentiments': dict(regional_sentiments),
            'coverage_percentage': coverage_percentage
        }

    def get_world_sentiment_map_data(self, geographic_analysis):
        """Prepare data for world map visualization"""
        map_data = []
        
        for country, data in geographic_analysis.get('country_sentiments', {}).items():
            if data['coordinates']:
                map_data.append({
                    'country': country.title(),
                    'lat': data['coordinates']['lat'],
                    'lon': data['coordinates']['lon'],
                    'total_posts': data['total_posts'],
                    'sentiment': self._get_dominant_sentiment(data['sentiment_distribution']),
                    'positive_percent': data['sentiment_distribution'].get('positive', 0),
                    'negative_percent': data['sentiment_distribution'].get('negative', 0),
                    'region': data['coordinates']['region']
                })
        
        return map_data

    def _get_dominant_sentiment(self, distribution):
        """Get the dominant sentiment from distribution"""
        if not distribution:
            return 'neutral'
        
        return max(distribution.items(), key=lambda x: x[1])[0]

    def generate_geographic_insights(self, geographic_analysis):
        """Generate insights from geographic analysis"""
        insights = []
        
        if not geographic_analysis or geographic_analysis['total_located_posts'] == 0:
            return ["No geographic data available for insights."]
        
        country_sentiments = geographic_analysis['country_sentiments']
        regional_sentiments = geographic_analysis['regional_sentiments']
        
        # Find most positive country
        if country_sentiments:
            most_positive = max(
                country_sentiments.items(),
                key=lambda x: x[1]['sentiment_distribution'].get('positive', 0)
            )
            insights.append(f"🇺🇸 Most positive sentiment in {most_positive[0].title()} "
                          f"({most_positive[1]['sentiment_distribution']['positive']:.1f}% positive)")
        
        # Find most negative country
        if country_sentiments:
            most_negative = max(
                country_sentiments.items(),
                key=lambda x: x[1]['sentiment_distribution'].get('negative', 0)
            )
            insights.append(f"🇺🇸 Most negative sentiment in {most_negative[0].title()} "
                          f"({most_negative[1]['sentiment_distribution']['negative']:.1f}% negative)")
        
        # Regional insights
        if regional_sentiments:
            most_active_region = max(
                regional_sentiments.items(),
                key=lambda x: x[1]['total_posts']
            )
            insights.append(f"🌍 Most active region: {most_active_region[0]} "
                          f"({most_active_region[1]['total_posts']} posts)")
        
        # Coverage insight
        coverage = geographic_analysis['coverage_percentage']
        insights.append(f"📊 Geographic coverage: {coverage:.1f}% of posts located")
        
        return insights

# Test the geographic analyzer
async def test_geographic_analyzer():
    analyzer = GeographicSentimentAnalyzer()
    
    test_posts = [
        {"text": "Love the weather in New York today! #usa"},
        {"text": "Problems with service in London. Very disappointed. #uk"},
        {"text": "Great conference in Tokyo! Amazing experience. #japan"},
        {"text": "Berlin is wonderful this time of year. #germany"},
        {"text": "Having issues with the product in Sydney. #australia"}
    ]
    
    # Create a simple sentiment dataframe
    sentiment_data = []
    for post in test_posts:
        sentiment_data.append({
            'sentiment': random.choice(['positive', 'negative', 'neutral']),
            'score': random.uniform(-1, 1)
        })
    
    sentiment_df = pd.DataFrame(sentiment_data)
    
    print("Testing Geographic Sentiment Analyzer:")
    analysis = await analyzer.analyze_posts_geographic(test_posts, sentiment_df)
    
    print(f"\nGeographic Analysis:")
    print(f"Total posts: {analysis['total_posts']}")
    print(f"Located posts: {analysis['total_located_posts']}")
    print(f"Coverage: {analysis['coverage_percentage']:.1f}%")
    
    print(f"\nCountry sentiments:")
    for country, data in analysis['country_sentiments'].items():
        print(f"{country.title()}: {data['sentiment_distribution']}")

if __name__ == "__main__":
    asyncio.run(test_geographic_analyzer())