#!/usr/bin/env python3
"""
Bot Status Check Script
Checks the status of the Telegram bot and related services.
"""

import os
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

def get_firebase_client():
    """Get Firebase client with proper error handling."""
    try:
        return get_firebase_client()
    except Exception as e:
        logger.error(f"Failed to get Firebase client: {e}")
        raise

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
                logger.info(f"📝 Bot name: {bot_info.get('first_name', 'Unknown')}")
                logger.info(f"🆔 Bot ID: {bot_info.get('id', 'Unknown')}")
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

def check_webhook_status():
    """Check webhook configuration."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment")
            return False
        
        # Get webhook info
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                webhook_info = data.get('result', {})
                
                if webhook_info.get('url'):
                    logger.info(f"📡 Webhook URL: {webhook_info['url']}")
                    logger.info(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
                    
                    if webhook_info.get('last_error_date'):
                        logger.warning(f"⚠️ Last error: {webhook_info.get('last_error_message', 'Unknown error')}")
                    else:
                        logger.info("✅ Webhook is working properly")
                    
                    return True
                else:
                    logger.info("📡 No webhook is currently set")
                    return True
            else:
                logger.error(f"❌ Failed to get webhook info: {data.get('description', 'Unknown error')}")
                return False
        else:
            logger.error(f"❌ Webhook info request failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Webhook status check failed: {e}")
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

def check_environment():
    """Check environment variables."""
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

def main():
    """Main status check function."""
    logger.info("🔍 Starting Bot Status Check")
    logger.info(f"📅 Check timestamp: {datetime.now()}")
    
    # Check environment
    logger.info("\n📋 Checking environment variables...")
    env_ok = check_environment()
    
    # Check bot status
    logger.info("\n🤖 Checking bot status...")
    bot_ok = check_bot_status()
    
    # Check webhook status
    logger.info("\n📡 Checking webhook status...")
    webhook_ok = check_webhook_status()
    
    # Check Firebase connection
    logger.info("\n🔥 Checking Firebase connection...")
    firebase_ok = check_firebase_connection()
    
    # Summary
    logger.info("\n📊 Status Summary:")
    logger.info(f"Environment: {'✅ OK' if env_ok else '❌ FAILED'}")
    logger.info(f"Bot Status: {'✅ OK' if bot_ok else '❌ FAILED'}")
    logger.info(f"Webhook: {'✅ OK' if webhook_ok else '❌ FAILED'}")
    logger.info(f"Firebase: {'✅ OK' if firebase_ok else '❌ FAILED'}")
    
    # Overall status
    if env_ok and bot_ok and firebase_ok:
        logger.info("\n🎉 Bot is ready and operational!")
        return True
    else:
        logger.error("\n⚠️ Bot has issues that need to be resolved")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 