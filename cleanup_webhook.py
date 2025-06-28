#!/usr/bin/env python3
"""
Webhook Cleanup Script for KICKAI
Cleans up any existing webhooks that might be causing 409 conflicts
"""

import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_bot_token_from_db():
    """Get bot token from Supabase database."""
    try:
        from src.tools.supabase_tools import get_supabase_client
        supabase = get_supabase_client()
        
        response = supabase.table('team_bots').select('bot_token').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').eq('is_active', True).execute()
        
        if response and hasattr(response, 'data') and response.data:
            return response.data[0]['bot_token']
        else:
            logger.error("No active bot found in database")
            return None
            
    except Exception as e:
        logger.error(f"Error getting bot token: {e}")
        return None

def cleanup_webhook(bot_token):
    """Clean up webhook and check status."""
    try:
        # Delete webhook
        delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        delete_response = requests.post(delete_url, timeout=10)
        
        if delete_response.status_code == 200:
            logger.info("✅ Webhook deleted successfully")
        else:
            logger.warning(f"Failed to delete webhook: {delete_response.status_code}")
        
        # Get webhook info
        info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        info_response = requests.get(info_url, timeout=10)
        
        if info_response.status_code == 200:
            webhook_info = info_response.json()
            if webhook_info.get('ok'):
                result = webhook_info['result']
                if result.get('url'):
                    logger.warning(f"⚠️ Webhook still active: {result['url']}")
                    logger.warning(f"   Pending updates: {result.get('pending_update_count', 0)}")
                else:
                    logger.info("✅ Webhook is properly deleted")
                    logger.info(f"   Pending updates: {result.get('pending_update_count', 0)}")
            else:
                logger.error(f"Failed to get webhook info: {webhook_info}")
        else:
            logger.error(f"Failed to get webhook info: {info_response.status_code}")
            
    except Exception as e:
        logger.error(f"Error during webhook cleanup: {e}")

def test_bot_connection(bot_token):
    """Test bot connection."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        bot_info = response.json()
        
        if bot_info.get('ok'):
            bot = bot_info['result']
            logger.info(f"✅ Bot connection successful!")
            logger.info(f"   Name: {bot.get('first_name')}")
            logger.info(f"   Username: @{bot.get('username')}")
            logger.info(f"   ID: {bot.get('id')}")
            return True
        else:
            logger.error(f"❌ Bot connection failed: {bot_info}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing bot connection: {e}")
        return False

def main():
    """Main function."""
    print("🧹 KICKAI Webhook Cleanup")
    print("=" * 30)
    
    # Get bot token
    bot_token = get_bot_token_from_db()
    if not bot_token:
        print("❌ Could not get bot token from database")
        return
    
    print(f"📱 Bot token: {bot_token[:10]}...")
    
    # Test connection
    print("\n🔍 Testing bot connection...")
    if not test_bot_connection(bot_token):
        print("❌ Bot connection failed")
        return
    
    # Cleanup webhook
    print("\n🧹 Cleaning up webhook...")
    cleanup_webhook(bot_token)
    
    print("\n✅ Webhook cleanup completed!")

if __name__ == "__main__":
    main() 