import streamlit as st
import asyncio
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import threading
from queue import Queue

from twitter_client import TwitterClient
from sentiment_analyzer import EnhancedSentimentAnalyzer
from multilingual_analyzer import MultilingualSentimentAnalyzer
from geographic_analyzer import GeographicSentimentAnalyzer
from gemini_analyzer import GeminiSentimentAnalyzer

# Configure page
st.set_page_config(
    page_title="AI-Powered Real-Time Social Sentiment Analyzer",
    page_icon="🤖",
    layout="wide"
)

# Initialize clients
@st.cache_resource
def get_clients():
    try:
        gemini_analyzer = GeminiSentimentAnalyzer()
        enhanced_analyzer = EnhancedSentimentAnalyzer(gemini_analyzer)
        multilingual_analyzer = MultilingualSentimentAnalyzer()
        geo_analyzer = GeographicSentimentAnalyzer()
        twitter_client = TwitterClient()
        
        # Initialize streaming client
        streaming_client = twitter_client if twitter_client.bearer_token else None
        
        return (
            twitter_client, 
            enhanced_analyzer,
            multilingual_analyzer,
            geo_analyzer,
            gemini_analyzer,
            streaming_client  # This now refers to twitter_client instance
)
    except Exception as e:
        st.error(f"Error initializing clients: {e}")
        # Fallback to basic components
        from sentiment_analyzer import SentimentAnalyzer
        return TwitterClient(), SentimentAnalyzer(), None, None, None, None

try:
    twitter_client, analyzer, multilingual_analyzer, geo_analyzer, gemini_analyzer, streaming_client = get_clients()
    gemini_available = gemini_analyzer.is_available if gemini_analyzer else False
    multilingual_available = multilingual_analyzer is not None
    streaming_available = streaming_client is not None and twitter_client.bearer_token is not None
except Exception as e:
    st.error(f"Error initializing analyzers: {e}")
    gemini_available = False
    multilingual_available = False
    streaming_available = False
    # Fallback to basic analyzer
    from sentiment_analyzer import SentimentAnalyzer
    twitter_client = TwitterClient()
    analyzer = SentimentAnalyzer()
    multilingual_analyzer, geo_analyzer, gemini_analyzer = None, None, None
    streaming_client = twitter_client if twitter_client.bearer_token else None

# Real-time data queue
if 'tweet_queue' not in st.session_state:
    st.session_state.tweet_queue = Queue()
if 'real_time_posts' not in st.session_state:
    st.session_state.real_time_posts = []
if 'streaming_active' not in st.session_state:
    st.session_state.streaming_active = False
if 'stream_start_time' not in st.session_state:
    st.session_state.stream_start_time = None

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1DA1F2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .ai-header {
        font-size: 2rem;
        color: #4285F4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .gemini-analysis {
        background-color: #e8f0fe;
        border-left: 4px solid #4285F4;
        padding: 1rem;
        margin: 1rem 0;
    }
    .positive { color: #00cc96; }
    .negative { color: #ef553b; }
    .neutral { color: #636efa; }
    .language-badge {
        background-color: #ff6b6b;
        color: black;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .confidence-high { color: #00cc96; }
    .confidence-medium { color: #ffa500; }
    .confidence-low { color: #ef553b; }
    .real-time-indicator {
        background-color: #ff4444;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        animation: pulse 1.5s infinite;
        text-align: center;
        font-weight: bold;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .live-tweet {
        border-left: 4px solid #1DA1F2;
        padding: 0.5rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🤖 AI-Powered Real-Time Social Sentiment Analyzer</div>', unsafe_allow_html=True)

# Sidebar for controls
st.sidebar.title("🎛️ Analysis Controls")

# Analysis mode selection
analysis_mode = st.sidebar.radio(
    "Analysis Mode:",
    ["Real-Time Streaming", "Historical Analysis"]
)

# Advanced features toggle
st.sidebar.title("Advanced AI Features")
enable_gemini = st.sidebar.checkbox("Enable Gemini AI Analysis", value=gemini_available)
enable_multilingual = st.sidebar.checkbox("Enable Multilingual Analysis", value=multilingual_available)
enable_geographic = st.sidebar.checkbox("Enable Geographic Analysis", value=multilingual_available)

# Status indicators
if not gemini_available:
    st.sidebar.warning("⚠️ Gemini AI unavailable - add GEMINI_API_KEY to .env")
if not multilingual_available:
    st.sidebar.warning("⚠️ Multilingual features unavailable")
if not streaming_available and analysis_mode == "Real-Time Streaming":
    st.sidebar.warning("⚠️ Real-time streaming unavailable - check Twitter API credentials")

# REAL-TIME STREAMING MODE
if analysis_mode == "Real-Time Streaming":
    st.sidebar.title("🔴 Real-Time Controls")
    query = st.sidebar.text_input("Enter topic to monitor:", "AI technology")
    max_tweets = st.sidebar.slider("Max tweets to keep:", 100, 2000, 500)
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🎯 Start Streaming", type="primary", use_container_width=True):
            if twitter_client and streaming_available:
                st.session_state.streaming_active = True
                st.session_state.stream_start_time = datetime.now()
                st.session_state.real_time_posts = []
                
                # Add callback for new tweets
                def on_new_tweet(tweet_data):
                    st.session_state.tweet_queue.put(tweet_data)
                
                # Start streaming using TwitterClient's method
                twitter_client.add_stream_callback(on_new_tweet)
                success = twitter_client.start_real_time_stream(query, on_new_tweet)
                
                if success:
                    st.success("🎯 Real-time streaming started!")
                else:
                    st.error("❌ Failed to start streaming")
            else:
                st.error("❌ Streaming not available. Check Twitter API credentials.")
    
    with col2:
        if st.button("⏹️ Stop Streaming", use_container_width=True):
            st.session_state.streaming_active = False
            st.session_state.stream_start_time = None
            st.info("Streaming stopped")
    
    # Real-time stats
    if st.session_state.streaming_active:
        st.sidebar.markdown(f"""
        <div class="real-time-indicator">
        🔴 LIVE STREAMING
        </div>
        """, unsafe_allow_html=True)
        
        duration = datetime.now() - st.session_state.stream_start_time
        st.sidebar.write(f"⏱️ Duration: {duration.total_seconds():.0f}s")
        st.sidebar.write(f"📊 Tweets collected: {len(st.session_state.real_time_posts)}")

# HISTORICAL ANALYSIS MODE
else:
    st.sidebar.title("📊 Historical Controls")
    query = st.sidebar.text_input("Enter topic to analyze:", "AI technology")
    post_limit = st.sidebar.slider("Number of posts to analyze:", 10, 200, 50)
    refresh_rate = st.sidebar.selectbox("Refresh rate (seconds):", [30, 60, 120, 300], index=1)
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)

# Process real-time tweets
if st.session_state.streaming_active:
    # Process new tweets from queue
    new_tweets = []
    while not st.session_state.tweet_queue.empty():
        try:
            tweet_data = st.session_state.tweet_queue.get_nowait()
            new_tweets.append(tweet_data)
        except:
            break
    
    if new_tweets:
        # Convert to post format
        for tweet in new_tweets:
            post = {
                'text': tweet.get('text', ''),
                'created_at': tweet.get('created_at', datetime.now().isoformat()),
                'id': tweet.get('id', ''),
                'likes': tweet.get('public_metrics', {}).get('like_count', 0),
                'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
                'user': 'twitter_user',
                'verified': False,
                'source': 'realtime_stream',
                'real_time': True
            }
            st.session_state.real_time_posts.append(post)
        
        # Keep only recent tweets
        if len(st.session_state.real_time_posts) > max_tweets:
            st.session_state.real_time_posts = st.session_state.real_time_posts[-max_tweets:]

# Add this function in app.py
async def check_real_time_updates():
    """Check for real-time updates"""
    if (st.session_state.streaming_active and 
        streaming_client and 
        hasattr(streaming_client, 'check_stream_updates')):
        
        try:
            new_posts = await streaming_client.check_stream_updates()
            for post in new_posts:
                st.session_state.tweet_queue.put(post)
        except Exception as e:
            st.error(f"Stream update error: {e}")

# Analysis function for real-time data
async def analyze_real_time_data():
    """Analyze real-time streaming data"""
    if not st.session_state.real_time_posts:
        return None
    
    posts = st.session_state.real_time_posts[-100:]  # Analyze last 100 tweets
    
    with st.spinner("🔄 Analyzing real-time sentiment..."):
        # Convert to DataFrame
        df = pd.DataFrame(posts)
        
        # Enhanced sentiment analysis
        if hasattr(analyzer, 'analyze_posts_enhanced'):
            basic_summary, trends, detailed_df, gemini_analyses = await analyzer.analyze_posts_enhanced(df)
        else:
            basic_summary, trends, detailed_df = analyzer.analyze_posts(posts)
            gemini_analyses = {}
        
        return {
            'basic': basic_summary,
            'trends': trends,
            'detailed_df': detailed_df,
            'gemini_analyses': gemini_analyses,
            'raw_posts': posts
        }

# Main analysis function for historical data
async def perform_ai_analysis(query, limit, enable_gemini, enable_multilingual, enable_geographic):
    """Fetch posts and perform AI-powered analysis"""
    with st.spinner("🔄 Fetching and analyzing posts with AI..."):
        # Fetch posts
        posts = await twitter_client.fetch_real_posts(query, limit)
        
        if not posts:
            st.error("❌ No posts found or API error. Using simulated data.")
            posts = await twitter_client.fetch_simulated_posts(query, limit)
        
        # Convert to DataFrame
        df = pd.DataFrame(posts)
        
        # Enhanced sentiment analysis
        if hasattr(analyzer, 'analyze_posts_enhanced'):
            basic_summary, trends, detailed_df, gemini_analyses = await analyzer.analyze_posts_enhanced(df)
        else:
            # Fallback to basic analysis
            basic_summary, trends, detailed_df = analyzer.analyze_posts(posts)
            gemini_analyses = {}
        
        # Multilingual analysis
        multilingual_summary = None
        multilingual_df = None
        if enable_multilingual and multilingual_analyzer:
            try:
                multilingual_summary, multilingual_df = multilingual_analyzer.analyze_posts_multilingual(posts)
            except Exception as e:
                st.warning(f"Multilingual analysis failed: {e}")
        
        # Geographic analysis
        geographic_analysis = None
        if enable_geographic and geo_analyzer and detailed_df is not None:
            try:
                geographic_analysis = await geo_analyzer.analyze_posts_geographic(posts, detailed_df)
            except Exception as e:
                st.warning(f"Geographic analysis failed: {e}")
        
        return {
            'basic': basic_summary,
            'trends': trends,
            'detailed_df': detailed_df,
            'gemini_analyses': gemini_analyses,
            'multilingual': multilingual_summary,
            'multilingual_df': multilingual_df,
            'geographic': geographic_analysis,
            'raw_posts': posts
        }

# MAIN DISPLAY LOGIC

# REAL-TIME STREAMING DISPLAY
if analysis_mode == "Real-Time Streaming" and st.session_state.streaming_active:
    # Real-time dashboard
    st.subheader("📊 Real-Time Sentiment Dashboard")
    
    # Auto-refresh real-time analysis
    if st.session_state.real_time_posts:
        if 'last_realtime_analysis' not in st.session_state:
            st.session_state.last_realtime_analysis = datetime.now()
        
        # Analyze every 10 seconds or when new tweets arrive
        time_since_analysis = (datetime.now() - st.session_state.last_realtime_analysis).total_seconds()
        if time_since_analysis >= 10 or new_tweets:
            analysis_data = asyncio.run(analyze_real_time_data())
            st.session_state.last_realtime_analysis = datetime.now()
            if analysis_data:
                st.session_state.realtime_analysis_data = analysis_data
    
    # Display real-time analysis
    if 'realtime_analysis_data' in st.session_state and st.session_state.realtime_analysis_data:
        analysis_data = st.session_state.realtime_analysis_data
        basic_summary = analysis_data['basic']
        
        # Real-time metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Tweets", len(st.session_state.real_time_posts))
        
        with col2:
            st.metric("Positive", f"{basic_summary['sentiment_percentages']['positive']:.1f}%")
        
        with col3:
            st.metric("Neutral", f"{basic_summary['sentiment_percentages']['neutral']:.1f}%")
        
        with col4:
            st.metric("Negative", f"{basic_summary['sentiment_percentages']['negative']:.1f}%")
        
        with col5:
            sentiment_value = basic_summary['overall_sentiment']
            if isinstance(sentiment_value, dict):
                sentiment_value = sentiment_value.get('sentiment', 'neutral')
            sentiment_icon = "😊" if sentiment_value == "positive" else "😐" if sentiment_value == "neutral" else "😞"
            st.metric("Overall", f"{sentiment_icon} {sentiment_value.title()}")
        
        # Real-time chart
        st.subheader("📈 Real-Time Sentiment Trend")
        
        if len(st.session_state.real_time_posts) > 10:
            # Create time-series data
            time_data = []
            for i, post in enumerate(st.session_state.real_time_posts[-50:]):
                sentiment, _ = analyzer.classify_sentiment(post['text'])
                time_data.append({
                    'time': i,
                    'sentiment': sentiment,
                    'text': post['text'][:50] + '...'
                })
            
            time_df = pd.DataFrame(time_data)
            sentiment_counts = time_df.groupby('time')['sentiment'].value_counts().unstack(fill_value=0)
            
            fig = go.Figure()
            for sentiment in ['positive', 'neutral', 'negative']:
                if sentiment in sentiment_counts.columns:
                    fig.add_trace(go.Scatter(
                        x=sentiment_counts.index,
                        y=sentiment_counts[sentiment],
                        name=sentiment.title(),
                        mode='lines+markers',
                        line=dict(width=3)
                    ))
            
            fig.update_layout(
                title="Sentiment Trend (Last 50 Tweets)",
                xaxis_title="Time Sequence",
                yaxis_title="Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Live tweet feed
        st.subheader("🐦 Live Tweet Feed")
        
        for post in st.session_state.real_time_posts[-10:][::-1]:  # Show latest first
            sentiment, score = analyzer.classify_sentiment(post['text'])
            sentiment_color = {
                'positive': 'positive',
                'neutral': 'neutral', 
                'negative': 'negative'
            }[sentiment]
            
            st.markdown(f"""
            <div class="live-tweet">
                <div>
                    <span class="{sentiment_color}"><strong>{sentiment.title()}</strong></span>
                    <small>Score: {score:.2f} | Likes: {post.get('likes', 0)} | RTs: {post.get('retweets', 0)}</small>
                </div>
                {post['text']}<br>
                <small>Posted: {post.get('created_at', 'Just now')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("🎯 Waiting for real-time tweets... Stream is active!")

# HISTORICAL ANALYSIS DISPLAY
elif analysis_mode == "Historical Analysis":
    # Initialize session state for historical analysis
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = None

    # Manual refresh button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Analyze Now", type="primary", use_container_width=True):
            st.session_state.last_refresh = datetime.now()

    # Auto-refresh logic
    if auto_refresh and st.session_state.last_refresh:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh >= refresh_rate:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

    # Perform analysis if refresh was triggered
    if st.session_state.last_refresh:
        analysis_data = asyncio.run(
            perform_ai_analysis(query, post_limit, enable_gemini, enable_multilingual, enable_geographic)
        )
        st.session_state.analysis_data = analysis_data
    else:
        analysis_data = None

    # Display results if we have data
    if st.session_state.analysis_data:
        analysis_data = st.session_state.analysis_data
        basic_summary = analysis_data['basic']
        trends = analysis_data['trends']
        detailed_df = analysis_data['detailed_df']
        multilingual_summary = analysis_data['multilingual']
        geographic_analysis = analysis_data['geographic']
        
        # Basic sentiment metrics
        st.subheader("📈 Basic Sentiment Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Posts Analyzed", basic_summary['total_posts'])
        
        with col2:
            st.metric(
                "Positive", 
                f"{basic_summary['sentiment_percentages']['positive']:.1f}%"
            )
        
        with col3:
            st.metric(
                "Neutral", 
                f"{basic_summary['sentiment_percentages']['neutral']:.1f}%"
            )
        
        with col4:
            overall_sentiment = basic_summary['overall_sentiment']
            if isinstance(overall_sentiment, dict):
                sentiment_value = overall_sentiment.get('sentiment', 'neutral')
            else:
                sentiment_value = overall_sentiment
            sentiment_icon = "😊" if sentiment_value == "positive" else "😐" if sentiment_value == "neutral" else "😞"
            st.metric(
                "Overall Sentiment", 
                f"{sentiment_icon} {sentiment_value.title()}"
            )
        
        # Gemini AI Analysis Section
        if enable_gemini and analysis_data['gemini_analyses']:
            st.markdown('<div class="ai-header">🧠 Gemini AI Detailed Analysis</div>', unsafe_allow_html=True)
            
            gemini_analyses = analysis_data['gemini_analyses']
            st.info(f"Gemini AI analyzed {len(gemini_analyses)} posts in detail")
            
            for idx, analysis in gemini_analyses.items():
                if idx < len(analysis_data['raw_posts']):
                    post = analysis_data['raw_posts'][idx]
                    with st.expander(f"🧠 AI Analysis: {post['text'][:50]}..."):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Sentiment", analysis['sentiment'].title())
                            st.metric("Confidence", f"{analysis['confidence']*100:.1f}%")
                            st.metric("Intensity", analysis['intensity'].title())
                        
                        with col2:
                            st.write("**Emotional Tone:**")
                            st.write(", ".join(analysis['emotional_tone']))
                            
                            st.write("**Key Topics:**")
                            st.write(", ".join(analysis['key_topics']))
                        
                        st.write("**Summary:**")
                        st.info(analysis['summary'])
                        
                        st.write("**Reasoning:**")
                        st.write(analysis['reasoning'])

        # Multilingual analysis section
        if enable_multilingual and multilingual_summary:
            st.subheader("🌐 Multilingual Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Language distribution pie chart
                if multilingual_summary['language_breakdown']:
                    lang_data = []
                    for lang, data in multilingual_summary['language_breakdown'].items():
                        lang_data.append({
                            'Language': data['language_name'],
                            'Posts': data['count'],
                            'Percentage': (data['count'] / multilingual_summary['total_posts']) * 100
                        })
                    
                    lang_df = pd.DataFrame(lang_data)
                    fig_lang = px.pie(
                        lang_df, 
                        values='Posts', 
                        names='Language',
                        title=f"Posts by Language ({multilingual_summary['languages_detected']} languages detected)"
                    )
                    st.plotly_chart(fig_lang, use_container_width=True)
            
            with col2:
                # Sentiment by language
                if multilingual_summary['language_breakdown']:
                    sentiment_by_lang = []
                    for lang, data in multilingual_summary['language_breakdown'].items():
                        for sentiment, percentage in data['percentages'].items():
                            sentiment_by_lang.append({
                                'Language': data['language_name'],
                                'Sentiment': sentiment,
                                'Percentage': percentage
                            })
                    
                    sentiment_df = pd.DataFrame(sentiment_by_lang)
                    if not sentiment_df.empty:
                        fig_sentiment_lang = px.bar(
                            sentiment_df,
                            x='Language',
                            y='Percentage',
                            color='Sentiment',
                            title="Sentiment Distribution by Language",
                            color_discrete_map={
                                'positive': '#00cc96',
                                'neutral': '#636efa', 
                                'negative': '#ef553b'
                            }
                        )
                        st.plotly_chart(fig_sentiment_lang, use_container_width=True)
        
        # Geographic analysis section
        if enable_geographic and geographic_analysis and geographic_analysis.get('total_located_posts', 0) > 0:
            st.subheader("🗺️ Geographic Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # World map visualization
                map_data = geo_analyzer.get_world_sentiment_map_data(geographic_analysis)
                if map_data:
                    map_df = pd.DataFrame(map_data)
                    fig_map = px.scatter_geo(
                        map_df,
                        lat='lat',
                        lon='lon',
                        color='sentiment',
                        size='total_posts',
                        hover_name='country',
                        hover_data={
                            'positive_percent': ':.1f',
                            'negative_percent': ':.1f',
                            'total_posts': True
                        },
                        title="Sentiment Analysis by Country",
                        color_discrete_map={
                            'positive': '#00cc96',
                            'neutral': '#636efa', 
                            'negative': '#ef553b'
                        }
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
            
            with col2:
                # Regional sentiment analysis
                if geographic_analysis.get('regional_sentiments'):
                    regional_data = []
                    for region, data in geographic_analysis['regional_sentiments'].items():
                        for sentiment, percentage in data['sentiment_distribution'].items():
                            regional_data.append({
                                'Region': region,
                                'Sentiment': sentiment,
                                'Percentage': percentage,
                                'Total Posts': data['total_posts']
                            })
                    
                    regional_df = pd.DataFrame(regional_data)
                    if not regional_df.empty:
                        fig_regional = px.bar(
                            regional_df,
                            x='Region',
                            y='Percentage',
                            color='Sentiment',
                            title="Sentiment Distribution by Region",
                            color_discrete_map={
                                'positive': '#00cc96',
                                'neutral': '#636efa', 
                                'negative': '#ef553b'
                            }
                        )
                        st.plotly_chart(fig_regional, use_container_width=True)
            
            # Country-level details
            with st.expander("Country-level Sentiment Details"):
                if geographic_analysis.get('country_sentiments'):
                    country_data = []
                    for country, data in geographic_analysis['country_sentiments'].items():
                        country_data.append({
                            'Country': country,
                            'Total Posts': data['total_posts'],
                            'Positive %': data['sentiment_distribution'].get('positive', 0),
                            'Neutral %': data['sentiment_distribution'].get('neutral', 0),
                            'Negative %': data['sentiment_distribution'].get('negative', 0),
                            'Avg Score': data['average_score']
                        })
                    
                    country_df = pd.DataFrame(country_data)
                    st.dataframe(country_df.sort_values('Total Posts', ascending=False))
        
        # Basic visualizations
        st.subheader("📊 Basic Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            sentiment_data = pd.DataFrame({
                'Sentiment': list(basic_summary['sentiment_percentages'].keys()),
                'Percentage': list(basic_summary['sentiment_percentages'].values())
            })
            
            fig_pie = px.pie(
                sentiment_data, 
                values='Percentage', 
                names='Sentiment',
                color='Sentiment',
                color_discrete_map={
                    'positive': '#00cc96',
                    'neutral': '#636efa', 
                    'negative': '#ef553b'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Trend chart
            if trends is not None and not trends.empty and len(trends) > 1:
                # Reset index and prepare data for plotting
                trends_reset = trends.reset_index()
                if 'hour' in trends_reset.columns:
                    fig_trend = px.line(
                        trends_reset, 
                        x='hour', 
                        y=['positive', 'neutral', 'negative'],
                        labels={'value': 'Number of Posts', 'hour': 'Time'},
                        color_discrete_map={
                            'positive': '#00cc96',
                            'neutral': '#636efa',
                            'negative': '#ef553b'
                        }
                    )
                    fig_trend.update_layout(showlegend=True)
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("Not enough data for trend analysis")
            else:
                st.info("Not enough data for trend analysis")
        
        # Sample posts with language badges
        st.subheader("📝 Sample Posts")
        
        # Filter options
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            sentiment_filter = st.selectbox("Filter by sentiment:", ["All", "Positive", "Neutral", "Negative"])
        with col2:
            language_filter = st.selectbox("Filter by language:", ["All", "English", "Spanish", "French", "German", "Other"])
        
        # Display posts
        display_df = analysis_data['multilingual_df'] if enable_multilingual and analysis_data['multilingual_df'] is not None else detailed_df
        
        if not display_df.empty:
            filtered_df = display_df
            
            # Apply sentiment filter
            if sentiment_filter != "All":
                filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter.lower()]
            
            # Apply language filter if multilingual data available
            if enable_multilingual and 'language' in filtered_df.columns and language_filter != "All":
                lang_map = {
                    "English": "en", "Spanish": "es", "French": "fr", 
                    "German": "de", "Other": lambda x: x not in ['en', 'es', 'fr', 'de']
                }
                if language_filter == "Other":
                    filtered_df = filtered_df[filtered_df['language'].apply(lang_map[language_filter])]
                else:
                    filtered_df = filtered_df[filtered_df['language'] == lang_map[language_filter]]
            
            for _, post in filtered_df.head(10).iterrows():
                sentiment_color = {
                    'positive': 'positive',
                    'neutral': 'neutral', 
                    'negative': 'negative'
                }[post['sentiment']]
                
                # Language display
                if enable_multilingual and 'language' in post:
                    lang_name = multilingual_analyzer.language_patterns.get(
                        post.get('language', 'en'), {}
                    ).get('name', post.get('language', 'en')) if multilingual_analyzer else 'Unknown'
                    lang_badge = f'<span class="language-badge">{lang_name}</span>'
                else:
                    lang_badge = '<span class="language-badge">English</span>'
                
                st.markdown(f"""
                <div class="metric-card">
                    <div>
                        <span class="{sentiment_color}"><strong>{post['sentiment'].title()}</strong> (Score: {post.get('score', 0):.2f})</span>
                        {lang_badge}
                    </div>
                    {post['text']}<br>
                    <small>Posted: {post.get('created_at', 'Unknown')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No posts to display")
        
        # Last refresh time
        st.sidebar.markdown(f"**Last refresh:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")

    else:
        # Initial state for historical analysis
        st.info("👆 Click 'Analyze Now' to start sentiment analysis!")
        
        if not multilingual_available:
            st.warning("⚠️ Multilingual features are currently unavailable. Using basic sentiment analysis.")
        
        # Feature overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🌐 Multilingual")
            st.markdown("""
            - Detect 12+ languages
            - Translation-based analysis
            - Language distribution charts
            """)
        
        with col2:
            st.subheader("🗺️ Geographic")
            st.markdown("""
            - Location extraction from text
            - Country-level sentiment mapping
            - Regional analysis
            - Interactive world map
            """)
        
        with col3:
            st.subheader("📊 Advanced Analytics")
            st.markdown("""
            - Real-time sentiment trends
            - Multi-modal analysis
            - Export capabilities
            - Custom filtering
            """)

# WELCOME SCREEN (when no mode is active)
else:
    st.info("👆 Select an analysis mode and configure settings to get started!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Real-Time Features")
        st.markdown("""
        - **Live Twitter streaming**
        - **Real-time sentiment analysis**
        - **Live tweet feed**
        - **Dynamic sentiment trends**
        - **Instant metric updates**
        - **No data limits during streaming**
        """)
    
    with col2:
        st.subheader("📊 Historical Analysis")
        st.markdown("""
        - **Deep sentiment analysis**
        - **Multilingual support**
        - **Geographic mapping**
        - **Gemini AI integration**
        - **Advanced visualizations**
        - **Comprehensive reporting**
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with Streamlit • Real-Time Twitter Streaming • Advanced NLP • Multilingual Support • Geographic Analysis</p>
</div>
""", unsafe_allow_html=True)