#!/usr/bin/env python3
"""
Test Dual Chat Architecture for KICKAI
Tests the setup of leadership and main team groups
"""

import os
import requests
from src.telegram_command_handler import TelegramCommandHandler

def test_bot_connection():
    """Test bot connection and get updates."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ Bot connected: @{bot_info['username']} ({bot_info['first_name']})")
            return True
        else:
            print(f"❌ Bot connection failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to bot: {e}")
        return False

def test_chat_groups():
    """Test and list chat groups the bot is in."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            print("\n📱 Chat Groups Bot is in:")
            print("-" * 40)
            
            groups = {}
            for update in data['result']:
                if 'message' in update and 'chat' in update['message']:
                    chat = update['message']['chat']
                    chat_id = chat['id']
                    chat_title = chat.get('title', 'Unknown')
                    chat_type = chat.get('type', 'unknown')
                    
                    if chat_type in ['group', 'supergroup']:
                        groups[chat_id] = {
                            'title': chat_title,
                            'type': chat_type,
                            'last_message': update['message'].get('text', 'No text')
                        }
            
            if groups:
                for chat_id, info in groups.items():
                    print(f"📋 {info['title']}")
                    print(f"   ID: {chat_id}")
                    print(f"   Type: {info['type']}")
                    print(f"   Last message: {info['last_message'][:50]}...")
                    print()
            else:
                print("❌ No group chats found")
                print("💡 Make sure the bot is added to groups and messages are sent")
            
            return len(groups) > 0
        else:
            print("❌ No updates found")
            return False
            
    except Exception as e:
        print(f"❌ Error getting chat groups: {e}")
        return False

def test_command_handler():
    """Test the command handler initialization."""
    try:
        handler = TelegramCommandHandler()
        print("✅ Command handler initialized successfully")
        
        print(f"\n📋 Available commands: {len(handler.commands)}")
        for cmd, info in handler.commands.items():
            print(f"  {cmd:<15} - {info['description']}")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing command handler: {e}")
        return False

def test_database_connection():
    """Test database connection and schema."""
    try:
        handler = TelegramCommandHandler()
        
        # Test team_bots table
        response = handler.supabase.table('team_bots').select('*').execute()
        print(f"✅ Database connected - Found {len(response.data)} team bot mappings")
        
        if response.data:
            for bot in response.data:
                print(f"  Team: {bot.get('team_id', 'Unknown')}")
                print(f"  Main Chat: {bot.get('chat_id', 'Not set')}")
                print(f"  Leadership Chat: {bot.get('leadership_chat_id', 'Not set')}")
                print()
        
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main test function."""
    print("🏆 KICKAI Dual Chat Architecture Test")
    print("=" * 50)
    
    # Test bot connection
    print("1. Testing bot connection...")
    bot_ok = test_bot_connection()
    
    # Test chat groups
    print("\n2. Testing chat groups...")
    groups_ok = test_chat_groups()
    
    # Test command handler
    print("\n3. Testing command handler...")
    handler_ok = test_command_handler()
    
    # Test database connection
    print("\n4. Testing database connection...")
    db_ok = test_database_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Bot Connection: {'✅ PASS' if bot_ok else '❌ FAIL'}")
    print(f"  Chat Groups: {'✅ PASS' if groups_ok else '❌ FAIL'}")
    print(f"  Command Handler: {'✅ PASS' if handler_ok else '❌ FAIL'}")
    print(f"  Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    
    if all([bot_ok, groups_ok, handler_ok, db_ok]):
        print("\n🎉 All tests passed! Dual chat architecture is ready.")
        print("\n📋 Next Steps:")
        print("1. Create the leadership Telegram group")
        print("2. Add @bphatters_bot to the leadership group")
        print("3. Make the bot an admin in the leadership group")
        print("4. Send a message in the leadership group")
        print("5. Run the SQL commands in Supabase")
        print("6. Update the team_bots table with leadership chat ID")
        print("7. Test commands in both groups")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        if not bot_ok:
            print("  - Check TELEGRAM_BOT_TOKEN environment variable")
        if not groups_ok:
            print("  - Make sure bot is added to groups")
            print("  - Send messages in groups to register them")
        if not handler_ok:
            print("  - Check Python dependencies")
        if not db_ok:
            print("  - Check Supabase connection")
            print("  - Verify database schema")

if __name__ == "__main__":
    main() 