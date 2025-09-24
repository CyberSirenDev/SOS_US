#!/bin/bash

# SOS_US Real-Time Social Sentiment Analyzer
# Installation and launch script

echo "🚨 SOS_US - Real-Time Social Sentiment Analyzer"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ to continue."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip to continue."
    exit 1
fi

echo "✅ pip3 found"

# Install requirements
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please check your internet connection and try again."
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Download nltk data for TextBlob
echo "📚 Downloading TextBlob corpora..."
python3 -c "import nltk; nltk.download('punkt'); nltk.download('brown')"

echo ""
echo "🚀 Starting SOS_US Real-Time Social Sentiment Analyzer..."
echo "📱 Open your browser to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python3 app.py