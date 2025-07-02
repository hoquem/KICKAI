#!/usr/bin/env python3
"""
Direct Chat ID Getter
This script helps you get chat IDs by sending a message to the bot.
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_bot_info(bot_token):
    """Get bot information."""
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting bot info: {e}")
        return None

def get_updates(bot_token):
    """Get updates from the bot."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return None

def main():
    # Get bot token
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return
    
    # Get bot info
    bot_info = get_bot_info(bot_token)
    if not bot_info or not bot_info.get('ok'):
        print("❌ Failed to get bot info")
        return
    
    bot = bot_info['result']
    print(f"🤖 Bot: @{bot['username']} ({bot['first_name']})")
    print(f"🆔 Bot ID: {bot['id']}")
    print()
    
    print("📋 Instructions:")
    print("1. Add the bot to your group")
    print("2. Make the bot an ADMIN in the group")
    print("3. Send a message in the group")
    print("4. Press Enter to check for updates")
    print()
    
    input("Press Enter after adding bot to group and sending a message...")
    
    # Get updates
    updates = get_updates(bot_token)
    if not updates or not updates.get('ok'):
        print("❌ Failed to get updates")
        return
    
    results = updates.get('result', [])
    if not results:
        print("❌ No updates found. Please check:")
        print("   - Bot is added to the group")
        print("   - Bot is an admin in the group")
        print("   - You sent a message in the group")
        print("   - Bot has permission to read messages")
        return
    
    print("✅ Found updates:")
    print("=" * 50)
    
    chats_found = set()
    
    for i, update in enumerate(results):
        if 'message' in update:
            message = update['message']
            chat = message.get('chat', {})
            from_user = message.get('from', {})
            
            chat_id = str(chat.get('id'))
            chat_type = chat.get('type')
            chat_title = chat.get('title', 'Private Chat')
            
            print(f"📨 Update #{i+1}:")
            print(f"   🆔 Chat ID: {chat_id}")
            print(f"   📝 Chat Type: {chat_type}")
            print(f"   📋 Chat Title: {chat_title}")
            print(f"   👤 From: {from_user.get('first_name', 'Unknown')}")
            print(f"   💬 Message: {message.get('text', 'No text')}")
            print()
            
            chats_found.add(chat_id)
    
    if chats_found:
        print("🎯 CHAT IDS FOUND:")
        print("=" * 50)
        for chat_id in chats_found:
            print(f"🆔 Chat ID: {chat_id}")
            print(f"💡 Railway command:")
            print(f"   railway variables --set \"TELEGRAM_MAIN_CHAT_ID={chat_id}\"")
            print()
        
        print("💡 If you have multiple groups, you'll need to:")
        print("1. Create a second group for leadership")
        print("2. Add the bot to that group")
        print("3. Send a message in that group")
        print("4. Run this script again")
    else:
        print("❌ No chat IDs found")

if __name__ == "__main__":
    main()
