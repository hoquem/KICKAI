#!/usr/bin/env python3
"""
Sanity Check Script
Performs basic sanity checks on the KICKAI system.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.tools.firebase_tools import get_firebase_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if all required environment variables are set."""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
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
        client = get_firebase_client()
        # Test a simple query
        client.collection('teams').limit(1).get()
        logger.info("✅ Firebase connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Firebase connection failed: {e}")
        return False

def check_ai_provider():
    """Check AI provider configuration."""
    try:
        from config import config
        ai_provider = config.ai_provider
        logger.info(f"✅ AI Provider configured: {ai_provider}")
        return True
    except Exception as e:
        logger.error(f"❌ AI Provider configuration failed: {e}")
        return False

def check_telegram_bot():
    """Check Telegram bot configuration."""
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

def check_python_dependencies():
    """Check if all required Python packages are installed."""
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
        logger.error(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        return False
    
    logger.info("✅ All required Python packages are installed")
    return True

def main():
    """Main sanity check function."""
    logger.info("🔍 Starting KICKAI Sanity Check")
    logger.info(f"📅 Check timestamp: {datetime.now()}")
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Firebase Connection", check_firebase_connection),
        ("AI Provider", check_ai_provider),
        ("Telegram Bot", check_telegram_bot),
        ("Python Dependencies", check_python_dependencies)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        logger.info(f"\n🔍 Checking {check_name}...")
        if check_func():
            passed_checks += 1
    
    # Summary
    logger.info(f"\n📊 Sanity Check Summary:")
    logger.info(f"Passed: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        logger.info("🎉 All checks passed! System is ready.")
        return True
    else:
        logger.error("⚠️ Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 