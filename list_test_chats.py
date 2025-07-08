#!/usr/bin/env python3
"""
List accessible chat IDs for testing
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

# Load test environment
load_dotenv('.env.test')

async def list_accessible_chats():
    """List all chats accessible to the test session."""
    
    # Get credentials from .env.test
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    session_string = os.getenv('TELEGRAM_SESSION_STRING')
    
    if not all([api_id, api_hash, session_string]):
        print("❌ Missing required environment variables")
        return
    
    print(f"🔑 Using API ID: {api_id}")
    print(f"🔑 Using API Hash: {api_hash[:10]}...")
    print(f"🔑 Using Session String: {session_string[:50]}...")
    
    # Create client
    client = TelegramClient(
        StringSession(session_string),
        int(api_id),
        api_hash
    )
    
    try:
        await client.start()
        print("✅ Connected to Telegram")
        
        # Get all dialogs (chats)
        dialogs = await client.get_dialogs()
        
        print(f"\n📋 Found {len(dialogs)} accessible chats:")
        print("=" * 80)
        
        for i, dialog in enumerate(dialogs[:20], 1):  # Show first 20
            chat = dialog.entity
            chat_type = "Group" if hasattr(chat, 'megagroup') and chat.megagroup else "Channel" if hasattr(chat, 'broadcast') else "Private"
            title = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
            
            print(f"{i:2d}. {chat_type:8} | ID: {chat.id:15} | Title: {title}")
            
            # Show more details for groups/channels
            if hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast'):
                print(f"     Username: @{getattr(chat, 'username', 'None')}")
                print(f"     Access Hash: {getattr(chat, 'access_hash', 'None')}")
        
        if len(dialogs) > 20:
            print(f"\n... and {len(dialogs) - 20} more chats")
        
        # Check specific chat IDs from .env.test
        print(f"\n🔍 Checking specific chat IDs from .env.test:")
        main_chat_id = os.getenv('TELEGRAM_MAIN_CHAT_ID')
        leadership_chat_id = os.getenv('TELEGRAM_LEADERSHIP_CHAT_ID')
        
        print(f"Main Chat ID: {main_chat_id}")
        print(f"Leadership Chat ID: {leadership_chat_id}")
        
        # Try to get these specific chats
        for chat_id in [main_chat_id, leadership_chat_id]:
            if chat_id:
                try:
                    chat = await client.get_entity(int(chat_id))
                    print(f"✅ Found chat {chat_id}: {getattr(chat, 'title', 'Unknown')}")
                except Exception as e:
                    print(f"❌ Cannot access chat {chat_id}: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.disconnect()
        print("\n✅ Disconnected from Telegram")

if __name__ == "__main__":
    asyncio.run(list_accessible_chats()) 