#!/usr/bin/env python3
"""
Bot Monitoring Script
Monitors the status of the Telegram bot and related services.
"""

import os
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from src.tools.firebase_tools import get_firebase_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_bot_status():
    """Check if the bot is running and responding."""
    try:
        # Get bot token from environment
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment")
            return False
        
        # Test bot API
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                logger.info(f"✅ Bot is running: @{bot_info.get('username', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Bot API error: {data.get('description', 'Unknown error')}")
                return False
        else:
            logger.error(f"❌ Bot API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Bot status check failed: {e}")
        return False

def check_firebase_connection():
    """Check Firebase connection."""
    try:
        client = get_firebase_client()
        # Test a simple query
        client.collection('teams').limit(1).get()
        logger.info("✅ Firebase connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Firebase connection failed: {e}")
        return False

def check_health_endpoint():
    """Check if the health endpoint is responding."""
    try:
        # Try to connect to health endpoint
        port = os.getenv('PORT', 8080)
        url = f"http://localhost:{port}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ Health endpoint responding")
            return True
        else:
            logger.error(f"❌ Health endpoint error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Health endpoint not available (bot may not be running)")
        return False
    except Exception as e:
        logger.error(f"❌ Health endpoint check failed: {e}")
        return False

def get_system_info():
    """Get system information."""
    try:
        # Get environment info
        environment = os.getenv('RAILWAY_ENVIRONMENT', 'development')
        python_version = os.sys.version
        working_dir = os.getcwd()
        
        # Get configuration info
        from config import config
        ai_provider = config.ai_provider
        
        return {
            'environment': environment,
            'python_version': python_version,
            'working_directory': working_dir,
            'ai_provider': ai_provider,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main monitoring function."""
    logger.info("🔍 Starting KICKAI Bot Monitoring")
    logger.info(f"📅 Check timestamp: {datetime.now()}")
    
    # Get system info
    system_info = get_system_info()
    logger.info(f"🌍 Environment: {system_info.get('environment', 'Unknown')}")
    logger.info(f"🤖 AI Provider: {system_info.get('ai_provider', 'Unknown')}")
    
    # Check bot status
    logger.info("\n🤖 Checking bot status...")
    bot_status = check_bot_status()
    
    # Check Firebase connection
    logger.info("\n🔥 Checking Firebase connection...")
    firebase_status = check_firebase_connection()
    
    # Check health endpoint
    logger.info("\n🏥 Checking health endpoint...")
    health_status = check_health_endpoint()
    
    # Summary
    logger.info("\n📊 Monitoring Summary:")
    logger.info(f"Bot Status: {'✅ OK' if bot_status else '❌ FAILED'}")
    logger.info(f"Firebase: {'✅ OK' if firebase_status else '❌ FAILED'}")
    logger.info(f"Health Endpoint: {'✅ OK' if health_status else '❌ FAILED'}")
    
    # Overall status
    if bot_status and firebase_status:
        logger.info("\n🎉 All critical services are running!")
        return True
    else:
        logger.error("\n⚠️ Some services are not running properly")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 