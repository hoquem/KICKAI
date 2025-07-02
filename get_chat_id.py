#!/usr/bin/env python3
"""
Simple script to get Telegram chat ID from bot token.
Run this script and then send a message to your bot to get the chat ID.
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_bot_updates(bot_token):
    """Get recent updates from the bot."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
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
    
    print(f"🤖 Bot token: {bot_token[:10]}...")
    print("📱 Instructions:")
    print("1. Add the bot to your Telegram group")
    print("2. Send a message in the group (any message)")
    print("3. Wait a few seconds and press Enter to check for updates")
    print()
    
    input("Press Enter after sending a message in the group...")
    
    # Get updates
    updates = get_bot_updates(bot_token)
    if not updates or not updates.get('ok'):
        print("❌ Failed to get updates")
        return
    
    results = updates.get('result', [])
    if not results:
        print("❌ No updates found. Make sure you sent a message in the group.")
        return
    
    print("✅ Found updates:")
    for update in results:
        if 'message' in update:
            message = update['message']
            chat = message.get('chat', {})
            chat_id = chat.get('id')
            chat_type = chat.get('type')
            chat_title = chat.get('title', 'Private Chat')
            
            print(f"📋 Chat ID: {chat_id}")
            print(f"📋 Chat Type: {chat_type}")
            print(f"📋 Chat Title: {chat_title}")
            print(f"📋 Message: {message.get('text', 'No text')}")
            print("---")
    
    print("💡 Use the Chat ID above in your Railway environment variables:")
    print("railway variables --set \"TELEGRAM_CHAT_ID=<CHAT_ID_HERE>\"")

if __name__ == "__main__":
    main()
