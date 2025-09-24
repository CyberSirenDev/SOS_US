"""
Real-Time Social Sentiment Analyzer
Main Flask application for sentiment analysis dashboard
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from textblob import TextBlob
import sqlite3
import json
import random
import threading
import time
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'sentiment_data.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            polarity REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def analyze_sentiment(text):
    """Analyze sentiment of given text using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return sentiment, polarity

def save_post(text, sentiment, polarity):
    """Save analyzed post to database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO posts (text, sentiment, polarity) VALUES (?, ?, ?)',
        (text, sentiment, polarity)
    )
    conn.commit()
    conn.close()

def get_recent_posts(limit=50):
    """Get recent posts from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM posts ORDER BY timestamp DESC LIMIT ?',
        (limit,)
    )
    posts = cursor.fetchall()
    conn.close()
    return posts

def get_sentiment_stats():
    """Get sentiment distribution statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sentiment, COUNT(*) as count 
        FROM posts 
        GROUP BY sentiment
    ''')
    stats = dict(cursor.fetchall())
    conn.close()
    return stats

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """API endpoint to analyze sentiment of submitted text"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    sentiment, polarity = analyze_sentiment(text)
    save_post(text, sentiment, polarity)
    
    return jsonify({
        'text': text,
        'sentiment': sentiment,
        'polarity': polarity,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/posts')
def get_posts():
    """API endpoint to get recent posts"""
    posts = get_recent_posts()
    return jsonify([{
        'id': post[0],
        'text': post[1],
        'sentiment': post[2],
        'polarity': post[3],
        'timestamp': post[4]
    } for post in posts])

@app.route('/api/stats')
def get_stats():
    """API endpoint to get sentiment statistics"""
    stats = get_sentiment_stats()
    return jsonify(stats)

@app.route('/api/trends')
def get_trends():
    """API endpoint to get sentiment trends over time"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(timestamp) as date, sentiment, COUNT(*) as count
        FROM posts 
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY date, sentiment
        ORDER BY date
    ''')
    trends = cursor.fetchall()
    conn.close()
    
    # Format data for chart
    result = {}
    for date, sentiment, count in trends:
        if date not in result:
            result[date] = {'positive': 0, 'negative': 0, 'neutral': 0}
        result[date][sentiment] = count
    
    return jsonify(result)

# Sample data generator for demonstration
sample_posts = [
    "I love this new product! It's amazing!",
    "This is the worst service I've ever experienced.",
    "The weather is okay today, nothing special.",
    "Absolutely fantastic experience, highly recommend!",
    "Not impressed, could be better.",
    "Great job on the presentation today!",
    "I'm feeling quite disappointed with the results.",
    "The food was delicious and the service was excellent!",
    "Traffic was terrible this morning.",
    "Having a wonderful day with family and friends!",
    "The movie was just average, not great but not bad either.",
    "Extremely satisfied with the customer support!",
    "This is completely unacceptable and frustrating.",
    "Beautiful sunset today, very peaceful.",
    "Outstanding performance by the team!"
]

def simulate_live_posts():
    """Simulate live posts for demonstration"""
    while True:
        time.sleep(random.randint(5, 15))  # Random interval between 5-15 seconds
        text = random.choice(sample_posts)
        sentiment, polarity = analyze_sentiment(text)
        save_post(text, sentiment, polarity)

if __name__ == '__main__':
    init_db()
    
    # Start simulation thread
    simulation_thread = threading.Thread(target=simulate_live_posts, daemon=True)
    simulation_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)