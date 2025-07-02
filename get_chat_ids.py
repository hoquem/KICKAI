#!/usr/bin/env python3
"""
Get Telegram Chat IDs for KICKAI Setup
This script helps you get the chat IDs for both main and leadership groups.
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
    
    print("📋 KICKAI Chat ID Setup Instructions:")
    print("=" * 50)
    print("You need to set up TWO Telegram groups:")
    print()
    print("1. 📢 MAIN GROUP - All players and members")
    print("   - Add the bot to this group")
    print("   - Send a message: 'Hello bot'")
    print()
    print("2. 👑 LEADERSHIP GROUP - Admins only")
    print("   - Add the bot to this group")
    print("   - Send a message: 'Admin setup'")
    print()
    
    input("Press Enter after adding the bot to BOTH groups and sending messages...")
    
    # Get updates
    updates = get_updates(bot_token)
    if not updates or not updates.get('ok'):
        print("❌ Failed to get updates")
        return
    
    results = updates.get('result', [])
    if not results:
        print("❌ No updates found. Make sure you:")
        print("   - Added the bot to both groups")
        print("   - Sent messages in both groups")
        print("   - The bot has permission to read messages")
        return
    
    print("✅ Found updates:")
    print("=" * 50)
    
    # Collect all unique chats
    chats = {}
    for i, update in enumerate(results):
        if 'message' in update:
            message = update['message']
            chat = message.get('chat', {})
            from_user = message.get('from', {})
            
            chat_id = str(chat.get('id'))
            if chat_id not in chats:
                chats[chat_id] = {
                    'chat': chat,
                    'messages': [],
                    'users': set()
                }
            
            chats[chat_id]['messages'].append(message.get('text', 'No text'))
            chats[chat_id]['users'].add(from_user.get('first_name', 'Unknown'))
    
    # Display chat information
    print(f"📊 Found {len(chats)} unique chats:")
    print()
    
    for chat_id, chat_data in chats.items():
        chat = chat_data['chat']
        messages = chat_data['messages']
        users = list(chat_data['users'])
        
        print(f"🆔 Chat ID: {chat_id}")
        print(f"📝 Chat Type: {chat.get('type')}")
        print(f"📋 Chat Title: {chat.get('title', 'Private Chat')}")
        print(f"👥 Users: {', '.join(users[:3])}{'...' if len(users) > 3 else ''}")
        print(f"💬 Messages: {len(messages)}")
        print()
    
    # Provide setup instructions
    print("🎯 SETUP INSTRUCTIONS:")
    print("=" * 50)
    
    if len(chats) >= 2:
        chat_list = list(chats.keys())
        main_chat_id = chat_list[0]
        leadership_chat_id = chat_list[1]
        
        print("✅ Perfect! You have 2+ groups. Here's how to set them up:")
        print()
        print("📢 MAIN GROUP (All players):")
        print(f"   Chat ID: {main_chat_id}")
        print()
        print("👑 LEADERSHIP GROUP (Admins only):")
        print(f"   Chat ID: {leadership_chat_id}")
        print()
        print("🚀 Railway Commands:")
        print(f"   railway variables --set \"TELEGRAM_MAIN_CHAT_ID={main_chat_id}\"")
        print(f"   railway variables --set \"TELEGRAM_LEADERSHIP_CHAT_ID={leadership_chat_id}\"")
        print()
        print("📝 Config File Update:")
        print("   Update config/bot_config.json with these chat IDs")
        
    elif len(chats) == 1:
        chat_id = list(chats.keys())[0]
        print("⚠️  You only have 1 group. You need 2 groups:")
        print()
        print("1. Create a SECOND group for leadership")
        print("2. Add the bot to the new group")
        print("3. Send a message in the new group")
        print("4. Run this script again")
        print()
        print(f"Current group Chat ID: {chat_id}")
        
    else:
        print("❌ No groups found. Please:")
        print("1. Create your main group")
        print("2. Add the bot to the group")
        print("3. Send a message in the group")
        print("4. Run this script again")
    
    print()
    print("💡 Tips:")
    print("- Make sure the bot is an admin in both groups")
    print("- The bot needs to read messages to detect chat IDs")
    print("- You can rename groups later without affecting the setup")

if __name__ == "__main__":
    main()
