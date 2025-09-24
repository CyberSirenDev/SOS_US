#!/usr/bin/env python3
"""
Real-Time Social Sentiment Analyzer
AI dashboard classifying live posts (positive/neutral/negative) and visualizing public opinion trends
"""

from flask import Flask, render_template, request, jsonify, Response
from textblob import TextBlob
import json
from datetime import datetime
import sqlite3
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentiment_analyzer_secret_key'

# Initialize database
def init_db():
    conn = sqlite3.connect('sentiment_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT NOT NULL,
                  sentiment TEXT NOT NULL,
                  polarity REAL NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return sentiment, polarity

def store_post(text, sentiment, polarity):
    """Store post and sentiment data in database"""
    conn = sqlite3.connect('sentiment_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO posts (text, sentiment, polarity) VALUES (?, ?, ?)",
              (text, sentiment, polarity))
    conn.commit()
    conn.close()

def get_recent_posts(limit=50):
    """Get recent posts from database"""
    conn = sqlite3.connect('sentiment_data.db')
    c = conn.cursor()
    c.execute("""SELECT text, sentiment, polarity, timestamp 
                 FROM posts 
                 ORDER BY timestamp DESC 
                 LIMIT ?""", (limit,))
    posts = c.fetchall()
    conn.close()
    return posts

def get_sentiment_stats():
    """Get sentiment statistics"""
    conn = sqlite3.connect('sentiment_data.db')
    c = conn.cursor()
    c.execute("""SELECT sentiment, COUNT(*) as count 
                 FROM posts 
                 WHERE datetime(timestamp) >= datetime('now', '-1 hour')
                 GROUP BY sentiment""")
    stats = c.fetchall()
    conn.close()
    
    result = {'positive': 0, 'neutral': 0, 'negative': 0}
    for sentiment, count in stats:
        result[sentiment] = count
    
    return result

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_post():
    """Analyze sentiment of a social media post"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'error': 'Text is required'}), 400
    
    sentiment, polarity = analyze_sentiment(text)
    
    # Store in database
    store_post(text, sentiment, polarity)
    
    return jsonify({
        'text': text,
        'sentiment': sentiment,
        'polarity': polarity,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    """Get current sentiment statistics"""
    return jsonify(get_sentiment_stats())

@app.route('/api/recent')
def get_recent():
    """Get recent posts"""
    posts = get_recent_posts()
    return jsonify([{
        'text': post[0],
        'sentiment': post[1],
        'polarity': post[2],
        'timestamp': post[3]
    } for post in posts])

@app.route('/api/events')
def events():
    """Server-Sent Events endpoint for real-time updates"""
    def event_stream():
        while True:
            stats = get_sentiment_stats()
            yield f"data: {json.dumps({'stats': stats})}\n\n"
            time.sleep(5)  # Update every 5 seconds
    
    return Response(event_stream(), mimetype="text/plain")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)