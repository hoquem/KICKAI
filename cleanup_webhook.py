#!/usr/bin/env python3
"""
Clean up webhook configuration to resolve 409 conflicts
"""

import requests
import logging
from src.tools.supabase_tools import get_supabase_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_webhook():
    """Clean up webhook configuration."""
    print("🧹 Cleaning up webhook configuration...")
    
    try:
        # Get bot token from database
        supabase = get_supabase_client()
        response = supabase.table('team_bots').select('bot_token').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').eq('is_active', True).execute()
        
        if not response.data:
            print("❌ No active bot found in database")
            return False
        
        bot_token = response.data[0]['bot_token']
        print(f"📱 Using bot token: {bot_token[:10]}...")
        
        # Delete webhook
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook deleted successfully")
                print(f"   Result: {result}")
            else:
                print(f"⚠️ Webhook deletion returned error: {result}")
        else:
            print(f"⚠️ Webhook deletion failed with status: {response.status_code}")
        
        # Get webhook info to confirm
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result['result']
                print(f"📋 Webhook info:")
                print(f"   URL: {webhook_info.get('url', 'None')}")
                print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
                print(f"   Pending update count: {webhook_info.get('pending_update_count', 0)}")
                print(f"   Last error date: {webhook_info.get('last_error_date', 'None')}")
                print(f"   Last error message: {webhook_info.get('last_error_message', 'None')}")
                
                if not webhook_info.get('url'):
                    print("✅ No webhook URL set - ready for polling mode")
                    return True
                else:
                    print("⚠️ Webhook URL still set - may need manual cleanup")
                    return False
            else:
                print(f"❌ Failed to get webhook info: {result}")
                return False
        else:
            print(f"❌ Failed to get webhook info: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        logger.error(f"Cleanup error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    cleanup_webhook() 