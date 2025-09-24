# SOS_US - Real-Time Social Sentiment Analyzer

🚨 **AI dashboard classifying live posts (positive/neutral/negative) and visualizing public opinion trends**

![SOS US Dashboard](https://github.com/user-attachments/assets/677ffff6-cde9-42f5-9dfe-3490559da5a8)

## 🌟 Features

- **Real-Time Sentiment Analysis**: Instantly analyze text sentiment using advanced AI models
- **Interactive Dashboard**: Beautiful, responsive web interface with live updates
- **Visual Analytics**: Custom charts showing sentiment distribution and trends
- **Live Post Feed**: Real-time stream of analyzed posts with sentiment scores
- **Polarity Scoring**: Precise sentiment measurement from -1.0 to +1.0
- **Auto-Simulation**: Background generation of sample posts for demonstration

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CyberSirenDev/SOS_US.git
   cd SOS_US
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data** (required for TextBlob):
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('brown')"
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📱 How to Use

1. **Analyze Text**: Enter any text in the input field and click "Analyze Sentiment"
2. **View Results**: See immediate sentiment classification (Positive/Negative/Neutral) with polarity scores
3. **Monitor Dashboard**: Watch real-time updates of sentiment distribution and live post feed
4. **Track Trends**: Observe how sentiment patterns change over time

## 🛠 Technical Stack

- **Backend**: Flask (Python web framework)
- **AI/ML**: TextBlob with NLTK for natural language processing
- **Database**: SQLite for lightweight data storage
- **Frontend**: Pure JavaScript, HTML5, CSS3
- **Visualization**: Custom HTML5 Canvas charts
- **Styling**: Modern responsive design with CSS gradients

## 📊 API Endpoints

- `POST /api/analyze` - Analyze sentiment of submitted text
- `GET /api/posts` - Retrieve recent posts with sentiment data
- `GET /api/stats` - Get sentiment distribution statistics
- `GET /api/trends` - Get sentiment trends over time

## 🎨 Sentiment Classification

The system uses TextBlob's sentiment analysis to classify text:

- **Positive** (polarity > 0.1): 😊 Green background
- **Negative** (polarity < -0.1): 😞 Orange background  
- **Neutral** (-0.1 ≤ polarity ≤ 0.1): 😐 Blue background

## 🔧 Configuration

The application includes:
- SQLite database auto-initialization
- Background simulation of social media posts
- Real-time updates every 10 seconds
- Responsive design for mobile and desktop

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/CyberSirenDev/SOS_US/issues).

## 👨‍💻 Developer

Created by **CyberSirenDev** - Real-time social sentiment analysis made simple and beautiful.

---

*Start analyzing social sentiment today with SOS US! 🚀*
