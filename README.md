# 🤖 AI-Powered Social Sentiment Analyzer

A real-time multilingual sentiment analysis platform that uses advanced AI to analyze social media posts across different languages and geographic locations.

## ✨ Features

- **🌐 Multilingual Analysis**: Supports 12+ languages with automatic detection
- **🗺️ Geographic Mapping**: Visualize sentiment patterns across countries and regions
- **🧠 Gemini AI Integration**: Advanced AI-powered sentiment analysis
- **📊 Real-time Dashboard**: Interactive visualizations with Streamlit
- **⚡ High Performance**: Async data fetching and processing
- **🔒 Enterprise Security**: Secure API key management

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd sentiment-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon')"