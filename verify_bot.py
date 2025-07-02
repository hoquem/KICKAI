#!/usr/bin/env python3
"""
Verify Telegram Bot Tokens
This script helps you verify which bot token corresponds to which bot.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_bot_info(bot_token):
    """Get bot information from Telegram API."""
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    print("🔍 Telegram Bot Token Verification")
    print("=" * 50)
    
    # Check all possible bot tokens
    tokens_to_check = {
        "TELEGRAM_BOT_TOKEN": os.getenv('TELEGRAM_BOT_TOKEN'),
        "TELEGRAM_LEADERSHIP_BOT_TOKEN": os.getenv('TELEGRAM_LEADERSHIP_BOT_TOKEN'),
        "TELEGRAM_BOT_TOKEN_TESTING": os.getenv('TELEGRAM_BOT_TOKEN_TESTING')
    }
    
    print("📋 Checking all bot tokens in environment:")
    print()
    
    valid_botss = []
    
    for token_name, token in tokens_to_check.items():
        if not token:
            print(f"❌ {token_name}: Not set")
            continue
            
        print(f"🔍 {token_name}:")
        print(f"   Token: {token[:20]}...")
        
        # Get bot info from Telegram
        bot_info = get_bot_info(token)
        
        if bot_info.get('ok'):
            bot = bot_info['result']
            print(f"   ✅ Bot Name: {bot.get('first_name')}")
            print(f"   ✅ Username: @{bot.get('username')}")
            print(f"   ✅ Bot ID: {bot.get('id')}")
            print(f"   ✅ Can Join Groups: {bot.get('can_join_groups', 'Unknown')}")
            print(f"   ✅ Can Read All Group Messages: {bot.get('can_read_all_group_messages', 'Unknown')}")
            
            valid_botss.append({
                'name': token_name,
                'token': token,
                'bot_info': bot
            })
        else:
            print(f"   ❌ Error: {bot_info.get('error', 'Unknown error')}")
        
        print()
    
    # Summary
    print("📊 SUMMARY:")
    print("=" * 50)
    
    if len(valid_botss) == 0:
        print("❌ No valid bot tokens found!")
        return
    
    print(f"✅ Found {len(valid_botss)} valid bot(s):")
    print()
    
    for i, bot in enumerate(valid_botss, 1):
        bot_info = bot['bot_info']
        print(f"{i}. {bot['name']}:")
        print(f"   🤖 @{bot_info['username']} ({bot_info['first_name']})")
        print(f"   🆔 Bot ID: {bot_info['id']}")
        print(f"   🔑 Token: {bot['token'][:20]}...")
        print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("=" * 50)
    
    if len(valid_botss) == 1:
        print("✅ You have 1 bot - this is perfect for the single bot design!")
        print(f"   Use: {valid_botss[0]['name']}")
        
    elif len(valid_botss) == 2:
        print("⚠️  You have 2 bots - you need to choose one for the single bot design:")
        print()
        print("Option 1: Use the main bot token")
        print("   - Keep TELEGRAM_BOT_TOKEN")
        print("   - Remove TELEGRAM_LEADERSHIP_BOT_TOKEN")
        print()
        print("Option 2: Use the leadership bot token")
        print("   - Replace TELEGRAM_BOT_TOKEN with TELEGRAM_LEADERSHIP_BOT_TOKEN")
        print("   - Remove TELEGRAM_LEADERSHIP_BOT_TOKEN")
        print()
        print("💡 I recommend Option 1 (keep the main bot token)")
        
    else:
        print("❓ You have multiple bots - please choose one for the single bot design")
    
    print()
    print("🚀 NEXT STEPS:")
    print("1. Choose which bot to use")
    print("2. Add that bot to your Telegram groups")
    print("3. Run: python get_chat_ids.py")
    print("4. Set the chat IDs in Railway")

if __name__ == "__main__":
    main()
