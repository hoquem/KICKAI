#!/usr/bin/env python3
"""
Preview Deployment Script
Shows what the deployment will look like without actually deploying.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'firebase_admin',
        'google.generativeai',
        'openai',
        'crewai',
        'python-telegram-bot',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    
    logger.info("✅ All required packages are installed")
    return True

def check_environment_variables():
    """Check if all required environment variables are set."""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_AUTH_URI',
        'FIREBASE_TOKEN_URI',
        'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
        'FIREBASE_CLIENT_X509_CERT_URL',
        'GOOGLE_API_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def check_firebase_connection():
    """Test Firebase connection."""
    try:
        from src.tools.firebase_tools import get_firebase_client
        client = get_firebase_client()
        # Test a simple query
        client.collection('teams').limit(1).get()
        logger.info("✅ Firebase connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Firebase connection failed: {e}")
        return False

def check_telegram_bot():
    """Test Telegram bot configuration."""
    try:
        import requests
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found")
            return False
        
        # Test bot API
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                logger.info(f"✅ Telegram bot configured: @{bot_info.get('username', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Telegram bot API error: {data.get('description', 'Unknown error')}")
                return False
        else:
            logger.error(f"❌ Telegram bot API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Telegram bot check failed: {e}")
        return False

def show_deployment_info():
    """Show deployment information."""
    print("\n🚀 KICKAI Deployment Preview")
    print("=" * 50)
    
    # Environment info
    environment = os.getenv('RAILWAY_ENVIRONMENT', 'development')
    print(f"🌍 Environment: {environment}")
    print(f"📅 Timestamp: {datetime.now()}")
    
    # Configuration info
    print("\n⚙️ Configuration:")
    print(f"   Database: Firebase Firestore")
    print(f"   AI Provider: Google Gemini (Production) / Ollama (Development)")
    print(f"   Bot Platform: Telegram")
    print(f"   Deployment: Railway")
    
    # Environment variables
    print("\n🔧 Environment Variables:")
    print("   ├── TELEGRAM_BOT_TOKEN=***")
    print("   ├── FIREBASE_PROJECT_ID=***")
    print("   ├── FIREBASE_PRIVATE_KEY_ID=***")
    print("   ├── FIREBASE_PRIVATE_KEY=***")
    print("   ├── FIREBASE_CLIENT_EMAIL=***")
    print("   ├── FIREBASE_CLIENT_ID=***")
    print("   ├── FIREBASE_AUTH_URI=***")
    print("   ├── FIREBASE_TOKEN_URI=***")
    print("   ├── FIREBASE_AUTH_PROVIDER_X509_CERT_URL=***")
    print("   ├── FIREBASE_CLIENT_X509_CERT_URL=***")
    print("   ├── GOOGLE_API_KEY=***")
    print("   └── OPENAI_API_KEY=***")
    
    print("\n💡 Note: TELEGRAM_BOT_TOKEN is fetched from Firebase database per team")
    
    # Deployment steps
    print("\n📋 Deployment Steps:")
    print("1. ✅ Check dependencies")
    print("2. ✅ Verify environment variables")
    print("3. ✅ Test Firebase connection")
    print("4. ✅ Test Telegram bot")
    print("5. 🚀 Deploy to Railway")
    print("6. 🔧 Configure webhook")
    print("7. 🧪 Test bot functionality")
    
    # Railway commands
    print("\n🚂 Railway Commands:")
    print("   railway login")
    print("   railway link")
    print("   railway variables set TELEGRAM_BOT_TOKEN=\"your_token\"")
    print("   railway variables set FIREBASE_PROJECT_ID=\"your_project_id\"")
    print("   railway variables set FIREBASE_PRIVATE_KEY_ID=\"your_key_id\"")
    print("   railway variables set FIREBASE_PRIVATE_KEY=\"your_private_key\"")
    print("   railway variables set FIREBASE_CLIENT_EMAIL=\"your_client_email\"")
    print("   railway variables set FIREBASE_CLIENT_ID=\"your_client_id\"")
    print("   railway variables set FIREBASE_AUTH_URI=\"https://accounts.google.com/o/oauth2/auth\"")
    print("   railway variables set FIREBASE_TOKEN_URI=\"https://oauth2.googleapis.com/token\"")
    print("   railway variables set FIREBASE_AUTH_PROVIDER_X509_CERT_URL=\"https://www.googleapis.com/oauth2/v1/certs\"")
    print("   railway variables set FIREBASE_CLIENT_X509_CERT_URL=\"your_cert_url\"")
    print("   railway variables set GOOGLE_API_KEY=\"your_google_api_key\"")
    print("   railway variables set OPENAI_API_KEY=\"your_openai_api_key\"")
    print("   railway deploy")
    
    # Post-deployment
    print("\n🎯 Post-Deployment:")
    print("1. Set webhook URL in Telegram")
    print("2. Test bot commands")
    print("3. Monitor logs")
    print("4. Configure team settings")

def main():
    """Main function."""
    logger.info("🔍 Starting deployment preview...")
    
    # Check dependencies
    logger.info("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()
    
    # Check environment variables
    logger.info("\n🔧 Checking environment variables...")
    env_ok = check_environment_variables()
    
    # Check Firebase connection
    logger.info("\n🔥 Checking Firebase connection...")
    firebase_ok = check_firebase_connection()
    
    # Check Telegram bot
    logger.info("\n🤖 Checking Telegram bot...")
    bot_ok = check_telegram_bot()
    
    # Show deployment info
    show_deployment_info()
    
    # Summary
    logger.info("\n📊 Preview Summary:")
    logger.info(f"Dependencies: {'✅ OK' if deps_ok else '❌ FAILED'}")
    logger.info(f"Environment: {'✅ OK' if env_ok else '❌ FAILED'}")
    logger.info(f"Firebase: {'✅ OK' if firebase_ok else '❌ FAILED'}")
    logger.info(f"Telegram Bot: {'✅ OK' if bot_ok else '❌ FAILED'}")
    
    if all([deps_ok, env_ok, firebase_ok, bot_ok]):
        logger.info("\n🎉 All checks passed! Ready for deployment.")
        return True
    else:
        logger.error("\n⚠️ Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 