#!/usr/bin/env python3
"""
Get Telegram Group Chat ID using Bot API
This script helps you get the chat ID of a Telegram group.
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

def get_updates(bot_token, offset=None):
    """Get updates from the bot."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {}
    if offset:
        params['offset'] = offset
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return None

def main():
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
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
    print("1. Add the bot to your Telegram group")
    print("2. Send ANY message in the group (e.g., 'Hello bot')")
    print("3. Wait a few seconds, then press Enter")
    print()
    
    input("Press Enter after sending a message in the group...")
    
    # Get updates
    updates = get_updates(bot_token)
    if not updates or not updates.get('ok'):
        print("❌ Failed to get updates")
        return
    
    results = updates.get('result', [])
    if not results:
        print("❌ No updates found. Make sure you:")
        print("   - Added the bot to the group")
        print("   - Sent a message in the group")
        print("   - The bot has permission to read messages")
        return
    
    print("✅ Found updates:")
    print("=" * 50)
    
    for i, update in enumerate(results):
        if 'message' in update:
            message = update['message']
            chat = message.get('chat', {})
            from_user = message.get('from', {})
            
            print(f"📨 Update #{i+1}:")
            print(f"   🆔 Chat ID: {chat.get('id')}")
            print(f"   📝 Chat Type: {chat.get('type')}")
            print(f"   📋 Chat Title: {chat.get('title', 'Private Chat')}")
            print(f"   👤 From User: {from_user.get('first_name', 'Unknown')} (@{from_user.get('username', 'no_username')})")
            print(f"   💬 Message: {message.get('text', 'No text')}")
            print()
    
    # Find group chats
    group_chats = []
    for update in results:
        if 'message' in update:
            chat = update['message'].get('chat', {})
            if chat.get('type') in ['group', 'supergroup']:
                group_chats.append(chat)
    
    if group_chats:
        print("🎯 GROUP CHATS FOUND:")
        print("=" * 50)
        for chat in group_chats:
            print(f"🆔 Chat ID: {chat.get('id')}")
            print(f"📝 Chat Type: {chat.get('type')}")
            print(f"📋 Chat Title: {chat.get('title')}")
            print(f"💡 Railway Command:")
            print(f"   railway variables --set \"TELEGRAM_CHAT_ID={chat.get('id')}\"")
            print()
    else:
        print("❌ No group chats found. Make sure you sent a message in a group, not a private chat.")
    
    print("💡 Alternative: Use @userinfobot")
    print("   1. Add @userinfobot to your group")
    print("   2. Send any message")
    print("   3. The bot will show you the chat ID")

if __name__ == "__main__":
    main()
