#!/usr/bin/env python3
"""
Generate Telegram Session String

This script helps you generate a session string for the E2E testing framework.
"""

from telethon import TelegramClient
from telethon.sessions import StringSession


def generate_session():
    """Generate a Telegram session string."""
    print("🔑 Telegram Session String Generator")
    print("=" * 40)
    print()
    
    # Get API credentials
    print("📋 Enter your Telegram API credentials:")
    print("(Get these from https://my.telegram.org)")
    print()
    
    api_id = input("Enter your API ID: ").strip()
    api_hash = input("Enter your API Hash: ").strip()
    
    if not api_id.isdigit() or not api_hash:
        print("❌ Invalid API ID or Hash")
        return
    
    try:
        # Create client
        print("\n🔗 Creating Telegram client...")
        client = TelegramClient(StringSession(), int(api_id), api_hash)
        
        # Start client (this will prompt for phone number and code)
        print("📱 Starting client...")
        print("You will be prompted for your phone number and verification code.")
        client.start()
        
        # Get session string
        session_string = client.session.save()
        
        print("\n✅ Session string generated successfully!")
        print("=" * 50)
        print(f"Session string: {session_string}")
        print("=" * 50)
        
        # Stop client
        client.disconnect()
        
        print("\n📝 Next steps:")
        print("1. Copy this session string")
        print("2. Add it to your .env file as TELEGRAM_SESSION_STRING")
        print("3. Run: python setup_telegram_credentials.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    generate_session() 