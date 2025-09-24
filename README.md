# 🚨 SOS_US - Real-Time Social Sentiment Analyzer

**Real-time AI dashboard classifying live posts (positive/neutral/negative) and visualizing public opinion trends**

## 🌟 Features

- **Real-time Sentiment Analysis**: Analyze social media posts instantly using AI
- **Live Statistics Dashboard**: View real-time sentiment distribution
- **Interactive Web Interface**: Modern, responsive dashboard
- **Trend Visualization**: Track public opinion trends over time
- **RESTful API**: Easy integration with other systems
- **Real-time Updates**: Server-Sent Events for live data updates

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip3 package manager
- Modern web browser

### Installation & Running

1. **Clone the repository** (if not already done)
2. **Run the application**:
   ```bash
   ./run.sh
   ```
   Or manually:
   ```bash
   pip3 install -r requirements.txt
   python3 -c "import nltk; nltk.download('punkt'); nltk.download('brown')"
   python3 app.py
   ```

3. **Open your browser** to `http://localhost:5000`

## 🖥️ Usage

### Web Interface

1. Open the dashboard at `http://localhost:5000`
2. Enter social media post text in the textarea
3. Click "Analyze Sentiment" to get instant classification
4. View real-time statistics and recent posts
5. Monitor public opinion trends as they update

### API Endpoints

#### Analyze Post Sentiment
```http
POST /api/analyze
Content-Type: application/json

{
  "text": "I love this amazing product!"
}
```

Response:
```json
{
  "text": "I love this amazing product!",
  "sentiment": "positive",
  "polarity": 0.625,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### Get Current Statistics
```http
GET /api/stats
```

Response:
```json
{
  "positive": 10,
  "neutral": 5,
  "negative": 3
}
```

#### Get Recent Posts
```http
GET /api/recent
```

Response:
```json
[
  {
    "text": "I love this amazing product!",
    "sentiment": "positive",
    "polarity": 0.625,
    "timestamp": "2024-01-01 12:00:00"
  }
]
```

#### Real-time Updates
```http
GET /api/events
```
Server-Sent Events stream for real-time statistics updates.

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python3 test_app.py
```

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **AI/ML**: TextBlob for sentiment analysis
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Database**: SQLite
- **Real-time**: Server-Sent Events (SSE)

## 📊 Sentiment Classification

The AI model classifies posts into three categories:

- **Positive**: Polarity > 0.1 (😊 Green)
- **Neutral**: -0.1 ≤ Polarity ≤ 0.1 (😐 Yellow)
- **Negative**: Polarity < -0.1 (😞 Red)

## 🔧 Configuration

The application runs on `localhost:5000` by default. To modify:

1. Edit the `host` and `port` parameters in `app.py`
2. Update any frontend API calls if using a different URL

## 📁 Project Structure

```
SOS_US/
├── app.py                  # Main Flask application
├── templates/
│   └── index.html         # Web dashboard interface
├── requirements.txt       # Python dependencies
├── run.sh                # Quick start script
├── test_app.py           # Test suite
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## 📋 API Response Codes

- `200 OK`: Successful operation
- `400 Bad Request`: Invalid input (e.g., empty text)
- `500 Internal Server Error`: Server processing error

## 🎯 Use Cases

- **Social Media Monitoring**: Track brand sentiment
- **Customer Feedback**: Analyze product reviews
- **Public Opinion**: Monitor political or social trends
- **Content Moderation**: Identify negative content
- **Market Research**: Understand consumer sentiment

## 📈 Future Enhancements

- Integration with Twitter/X API
- Advanced ML models (BERT, GPT)
- Historical trend analysis
- Export functionality
- User authentication
- Multiple language support
- Sentiment intensity scoring
- Topic classification

---

Made with ❤️ for real-time social sentiment analysis
