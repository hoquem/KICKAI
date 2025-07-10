#!/usr/bin/env python3
"""
Find Telegram Chat IDs Script

This script helps you find the chat IDs for your Telegram groups
so you can configure them in your .env file for the bot.
"""

import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv('.env')

async def find_chat_ids():
    """Find and display all available chat IDs."""
    
    # Get credentials from .env
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    session_string = os.getenv('ADMIN_SESSION_STRING')
    
    if not all([api_id, api_hash, session_string]):
        print("❌ Missing required environment variables in .env")
        print("Required: TELEGRAM_API_ID, TELEGRAM_API_HASH, ADMIN_SESSION_STRING")
        print("\n💡 To generate a session string, run: python generate_session_string.py")
        return
    
    print("🔍 Connecting to Telegram...")
    
    try:
        # Create client
        client = TelegramClient(
            StringSession(session_string),
            int(api_id),
            api_hash
        )
        
        # Start client
        await client.start()
        print("✅ Connected to Telegram successfully!")
        
        print("\n📋 Available Chats:")
        print("=" * 80)
        
        chats_found = []
        
        # Iterate through all dialogs (chats)
        async for dialog in client.iter_dialogs():
            chat_type = "Group" if dialog.is_group else "Channel" if dialog.is_channel else "Private"
            chat_id = dialog.id
            
            # Format the output
            print(f"📱 {chat_type}: {dialog.name}")
            print(f"   ID: {chat_id}")
            print(f"   Username: @{dialog.entity.username if hasattr(dialog.entity, 'username') and dialog.entity.username else 'None'}")
            print("-" * 40)
            
            chats_found.append({
                'name': dialog.name,
                'id': chat_id,
                'type': chat_type,
                'username': dialog.entity.username if hasattr(dialog.entity, 'username') and dialog.entity.username else None
            })
        
        print(f"\n📊 Summary: Found {len(chats_found)} chats")
        
        # Show recommended configuration
        print("\n🎯 Recommended .env Configuration:")
        print("=" * 50)
        
        # Find groups (negative IDs)
        groups = [chat for chat in chats_found if chat['id'] < 0]
        
        if len(groups) >= 2:
            print(f"TELEGRAM_MAIN_CHAT_ID={groups[0]['id']}  # {groups[0]['name']}")
            print(f"TELEGRAM_LEADERSHIP_CHAT_ID={groups[1]['id']}  # {groups[1]['name']}")
        elif len(groups) == 1:
            print(f"TELEGRAM_MAIN_CHAT_ID={groups[0]['id']}  # {groups[0]['name']}")
            print("TELEGRAM_LEADERSHIP_CHAT_ID=your_leadership_chat_id  # Add your leadership group")
        else:
            print("❌ No groups found. You need to:")
            print("   1. Create Telegram groups")
            print("   2. Add your bot to the groups")
            print("   3. Run this script again")
        
        # Disconnect
        await client.disconnect()
        print("\n✅ Disconnected from Telegram")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your TELEGRAM_API_ID and TELEGRAM_API_HASH")
        print("   2. Verify your ADMIN_SESSION_STRING is valid")
        print("   3. Make sure your .env file is properly configured")

if __name__ == "__main__":
    print("🧪 KICKAI Chat ID Finder")
    print("=" * 30)
    asyncio.run(find_chat_ids()) 