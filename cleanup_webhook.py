#!/usr/bin/env python3
"""
Webhook Cleanup Script
Cleans up Telegram webhook configuration.
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

def delete_webhook():
    """Delete the current webhook configuration."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment")
            return False
        
        # Delete webhook
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                logger.info("✅ Webhook deleted successfully")
                return True
            else:
                logger.error(f"❌ Failed to delete webhook: {data.get('description', 'Unknown error')}")
                return False
        else:
            logger.error(f"❌ Webhook deletion request failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Webhook deletion failed: {e}")
        return False

def get_webhook_info():
    """Get current webhook information."""
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
                    logger.info(f"📡 Current webhook URL: {webhook_info['url']}")
                    logger.info(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
                    logger.info(f"🕐 Last error: {webhook_info.get('last_error_date', 'None')}")
                    logger.info(f"❌ Last error message: {webhook_info.get('last_error_message', 'None')}")
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
        logger.error(f"❌ Webhook info retrieval failed: {e}")
        return False

def set_webhook(webhook_url: str):
    """Set a new webhook URL."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment")
            return False
        
        # Set webhook
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        data = {'url': webhook_url}
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                logger.info(f"✅ Webhook set successfully to: {webhook_url}")
                return True
            else:
                logger.error(f"❌ Failed to set webhook: {data.get('description', 'Unknown error')}")
                return False
        else:
            logger.error(f"❌ Webhook setting request failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Webhook setting failed: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Telegram webhook')
    parser.add_argument('action', choices=['delete', 'info', 'set'],
                       help='Action to perform')
    parser.add_argument('--url', help='Webhook URL (required for set action)')
    
    args = parser.parse_args()
    
    logger.info("🔧 Starting Webhook Management")
    logger.info(f"📅 Timestamp: {datetime.now()}")
    
    if args.action == 'delete':
        logger.info("\n🗑️ Deleting webhook...")
        success = delete_webhook()
        if success:
            logger.info("✅ Webhook cleanup completed")
        else:
            logger.error("❌ Webhook cleanup failed")
    
    elif args.action == 'info':
        logger.info("\n📡 Getting webhook info...")
        success = get_webhook_info()
        if not success:
            logger.error("❌ Failed to get webhook info")
    
    elif args.action == 'set':
        if not args.url:
            logger.error("❌ --url is required for set action")
            return
        
        logger.info(f"\n📡 Setting webhook to: {args.url}")
        success = set_webhook(args.url)
        if success:
            logger.info("✅ Webhook set successfully")
        else:
            logger.error("❌ Failed to set webhook")

if __name__ == "__main__":
    main() 