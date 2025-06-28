#!/usr/bin/env python3
"""
Bot Status Checker for KICKAI
Checks current bot status and identifies any conflicts
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

def check_bot_status(bot_token):
    """Check comprehensive bot status."""
    try:
        # Test bot connection
        me_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        me_response = requests.get(me_url, timeout=10)
        
        if me_response.status_code == 200:
            bot_info = me_response.json()
            if bot_info.get('ok'):
                bot = bot_info['result']
                logger.info(f"✅ Bot connection successful!")
                logger.info(f"   Name: {bot.get('first_name')}")
                logger.info(f"   Username: @{bot.get('username')}")
                logger.info(f"   ID: {bot.get('id')}")
            else:
                logger.error(f"❌ Bot connection failed: {bot_info}")
                return False
        else:
            logger.error(f"❌ Bot connection failed: {me_response.status_code}")
            return False
        
        # Check webhook status
        webhook_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        webhook_response = requests.get(webhook_url, timeout=10)
        
        if webhook_response.status_code == 200:
            webhook_info = webhook_response.json()
            if webhook_info.get('ok'):
                result = webhook_info['result']
                if result.get('url'):
                    logger.warning(f"⚠️ Webhook is active: {result['url']}")
                    logger.warning(f"   Pending updates: {result.get('pending_update_count', 0)}")
                    logger.warning(f"   Last error: {result.get('last_error_message', 'None')}")
                    return False
                else:
                    logger.info("✅ Webhook is properly deleted")
                    logger.info(f"   Pending updates: {result.get('pending_update_count', 0)}")
            else:
                logger.error(f"Failed to get webhook info: {webhook_info}")
                return False
        else:
            logger.error(f"Failed to get webhook info: {webhook_response.status_code}")
            return False
        
        # Test getUpdates
        updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        updates_response = requests.get(updates_url, params={'limit': 1, 'timeout': 1}, timeout=5)
        
        if updates_response.status_code == 200:
            updates_info = updates_response.json()
            if updates_info.get('ok'):
                logger.info("✅ getUpdates API working")
                return True
            else:
                logger.error(f"getUpdates failed: {updates_info}")
                return False
        elif updates_response.status_code == 409:
            logger.error("❌ 409 Conflict: Another bot instance is running")
            return False
        else:
            logger.error(f"getUpdates failed: {updates_response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        return False

def force_cleanup_webhook(bot_token):
    """Force cleanup webhook with multiple attempts."""
    logger.info("🧹 Force cleaning up webhook...")
    
    for attempt in range(3):
        try:
            # Delete webhook
            delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
            delete_response = requests.post(delete_url, timeout=10)
            
            if delete_response.status_code == 200:
                logger.info(f"✅ Webhook deletion attempt {attempt + 1} successful")
            else:
                logger.warning(f"Webhook deletion attempt {attempt + 1} failed: {delete_response.status_code}")
            
            # Wait between attempts
            if attempt < 2:
                import time
                time.sleep(5)
                
        except Exception as e:
            logger.warning(f"Webhook deletion attempt {attempt + 1} error: {e}")
            if attempt < 2:
                import time
                time.sleep(5)
    
    # Final check
    return check_bot_status(bot_token)

def main():
    """Main function."""
    print("🔍 KICKAI Bot Status Checker")
    print("=" * 30)
    
    # Get bot token
    bot_token = get_bot_token_from_db()
    if not bot_token:
        print("❌ Could not get bot token from database")
        return
    
    print(f"📱 Bot token: {bot_token[:10]}...")
    
    # Check current status
    print("\n🔍 Checking current bot status...")
    if check_bot_status(bot_token):
        print("\n✅ Bot is ready to run!")
    else:
        print("\n❌ Bot has issues. Attempting cleanup...")
        if force_cleanup_webhook(bot_token):
            print("\n✅ Bot cleanup successful! Ready to run.")
        else:
            print("\n❌ Bot cleanup failed. Manual intervention may be needed.")

if __name__ == "__main__":
    main() 