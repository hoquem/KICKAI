#!/usr/bin/env python3
"""
Find Telegram Chat IDs Script

This script helps you find the chat IDs for your Telegram groups
so you can configure them in your .env file for the bot.
"""

import os
import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv('.env')

async def find_chat_ids():
    """Find and display all available chat IDs."""
    
    # Get credentials from .env
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    session_string = os.getenv('ADMIN_SESSION_STRING')
    
    if not all([api_id, api_hash, session_string]):
        logger.error("❌ Missing required environment variables in .env")
        logger.error("Required: TELEGRAM_API_ID, TELEGRAM_API_HASH, ADMIN_SESSION_STRING")
        logger.info("\n💡 To generate a session string, run: python generate_session_string.py")
        return
    
    logger.info("🔍 Connecting to Telegram...")
    
    try:
        # Create client
        client = TelegramClient(
            StringSession(session_string),
            int(api_id),
            api_hash
        )
        
        # Start client
        await client.start()
        logger.info("✅ Connected to Telegram successfully!")
        
        logger.info("\n📋 Available Chats:")
        logger.info("=" * 80)
        
        chats_found = []
        
        # Iterate through all dialogs (chats)
        async for dialog in client.iter_dialogs():
            chat_type = "Group" if dialog.is_group else "Channel" if dialog.is_channel else "Private"
            chat_id = dialog.id
            
            # Format the output
            logger.info(f"📱 {chat_type}: {dialog.name}")
            logger.info(f"   ID: {chat_id}")
            logger.info(f"   Username: @{dialog.entity.username if hasattr(dialog.entity, 'username') and dialog.entity.username else 'None'}")
            logger.info("-" * 40)
            
            chats_found.append({
                'name': dialog.name,
                'id': chat_id,
                'type': chat_type,
                'username': dialog.entity.username if hasattr(dialog.entity, 'username') and dialog.entity.username else None
            })
        
        logger.info(f"\n📊 Summary: Found {len(chats_found)} chats")
        
        # Show recommended configuration
        logger.info("\n🎯 Recommended .env Configuration:")
        logger.info("=" * 50)
        
        # Find groups (negative IDs)
        groups = [chat for chat in chats_found if chat['id'] < 0]
        
        if len(groups) >= 2:
            logger.info(f"TELEGRAM_MAIN_CHAT_ID={groups[0]['id']}  # {groups[0]['name']}")
            logger.info(f"TELEGRAM_LEADERSHIP_CHAT_ID={groups[1]['id']}  # {groups[1]['name']}")
        elif len(groups) == 1:
            logger.info(f"TELEGRAM_MAIN_CHAT_ID={groups[0]['id']}  # {groups[0]['name']}")
            logger.info("TELEGRAM_LEADERSHIP_CHAT_ID=your_leadership_chat_id  # Add your leadership group")
        else:
            logger.error("❌ No groups found. You need to:")
            logger.error("   1. Create Telegram groups")
            logger.error("   2. Add your bot to the groups")
            logger.error("   3. Run this script again")
        
        # Disconnect
        await client.disconnect()
        logger.info("\n✅ Disconnected from Telegram")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error("\n🔧 Troubleshooting:")
        logger.error("   1. Check your TELEGRAM_API_ID and TELEGRAM_API_HASH")
        logger.error("   2. Verify your ADMIN_SESSION_STRING is valid")
        logger.error("   3. Make sure your .env file is properly configured")

if __name__ == "__main__":
    logger.info("🧪 KICKAI Chat ID Finder")
    logger.info("=" * 30)
    asyncio.run(find_chat_ids()) 