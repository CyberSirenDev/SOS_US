# setup.py
import nltk
import os

def setup_environment():
    print("🔧 Setting up environment...")
    
    # Download NLTK data
    try:
        nltk.download('vader_lexicon')
        print("✅ NLTK data downloaded")
    except:
        print("⚠️ NLTK download failed, but continuing...")
    
    # Check environment variables
    required_vars = ['TWITTER_BEARER_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {missing_vars}")
        print("💡 Create a .env file with these variables")
    else:
        print("✅ Environment variables check passed")
    
    print("🎉 Setup completed!")

if __name__ == "__main__":
    setup_environment()