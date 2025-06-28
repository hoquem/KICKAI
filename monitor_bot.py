#!/usr/bin/env python3
"""
Monitor Telegram bot status during testing
"""

import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_bot_info():
    """Get bot information from database and API."""
    try:
        from src.tools.supabase_tools import get_supabase_client
        
        # Get bot token from database
        supabase = get_supabase_client()
        response = supabase.table('team_bots').select('bot_token').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').eq('is_active', True).execute()
        
        if response.data:
            bot_token = response.data[0]['bot_token']
            
            # Test bot API
            api_response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
            if api_response.status_code == 200:
                bot_info = api_response.json()['result']
                return {
                    'token': bot_token[:10] + '...',
                    'name': bot_info['first_name'],
                    'username': bot_info['username'],
                    'id': bot_info['id'],
                    'status': 'active'
                }
        
        return None
        
    except Exception as e:
        return {'error': str(e)}

def check_process():
    """Check if bot process is running."""
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'python run_telegram_bot.py' in result.stdout:
            return True
        return False
    except:
        return False

def main():
    """Monitor bot status."""
    print("🤖 KICKAI Telegram Bot Monitor")
    print("=" * 40)
    
    while True:
        # Check bot info
        bot_info = get_bot_info()
        process_running = check_process()
        
        print(f"\n⏰ {time.strftime('%H:%M:%S')}")
        print("-" * 20)
        
        if bot_info and 'error' not in bot_info:
            print(f"✅ Bot: {bot_info['name']} (@{bot_info['username']})")
            print(f"   ID: {bot_info['id']}")
            print(f"   Token: {bot_info['token']}")
            print(f"   Status: {bot_info['status']}")
        elif bot_info and 'error' in bot_info:
            print(f"❌ Bot Error: {bot_info.get('error', 'Unknown error')}")
        else:
            print(f"❌ Bot: Not found or not accessible")
        
        if process_running:
            print(f"✅ Process: Running")
        else:
            print(f"❌ Process: Not running")
        
        print(f"🌍 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
        
        # Wait 10 seconds before next check
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped") 