#!/usr/bin/env python3
"""
Test script for Telegram integration features.
Tests all Telegram messaging capabilities for KICKAI.
"""

import os
import time
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_telegram_environment():
    """Test if Telegram environment variables are set."""
    print("🔍 Testing Telegram Environment...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Missing Telegram environment variables")
        print("   Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file")
        return False
    
    print("✅ Telegram environment variables are set")
    print(f"   Bot Token: {bot_token[:10]}...")
    print(f"   Chat ID: {chat_id}")
    return True


def test_basic_message():
    """Test sending a basic Telegram message."""
    print("\n📝 Testing Basic Message...")
    
    try:
        from src.tools.telegram_tools import SendTelegramMessageTool
        
        tool = SendTelegramMessageTool()
        message = "🧪 Test message from KICKAI Telegram integration"
        
        result = tool._run(message)
        print(f"✅ Basic message sent: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending basic message: {e}")
        return False


def test_telegram_poll():
    """Test sending a Telegram poll."""
    print("\n📊 Testing Telegram Poll...")
    
    try:
        from src.tools.telegram_tools import SendTelegramPollTool
        
        tool = SendTelegramPollTool()
        question = "What's your preferred match time for Sunday?"
        options = ["10:00 AM", "2:00 PM", "4:00 PM", "6:00 PM"]
        
        result = tool._run(question, options)
        print(f"✅ Poll sent: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending poll: {e}")
        return False


def test_availability_poll():
    """Test sending an availability poll."""
    print("\n⚽ Testing Availability Poll...")
    
    try:
        from src.tools.telegram_tools import SendAvailabilityPollTool
        
        tool = SendAvailabilityPollTool()
        fixture_details = "vs Thunder FC"
        match_date = "Sunday, July 7th"
        match_time = "2:00 PM"
        location = "Central Park"
        
        result = tool._run(fixture_details, match_date, match_time, location)
        print(f"✅ Availability poll sent: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending availability poll: {e}")
        return False


def test_squad_announcement():
    """Test sending a squad announcement."""
    print("\n🏆 Testing Squad Announcement...")
    
    try:
        from src.tools.telegram_tools import SendSquadAnnouncementTool
        
        tool = SendSquadAnnouncementTool()
        fixture_details = "vs Thunder FC"
        match_date = "Sunday, July 7th"
        match_time = "2:00 PM"
        starters = [
            "John Smith (GK)",
            "Mike Johnson (RB)",
            "David Wilson (CB)",
            "Tom Brown (CB)",
            "James Garcia (LB)",
            "Chris Davis (CM)",
            "Rob Martinez (CM)",
            "Luke Thomas (RW)",
            "Alex Wilson (LW)",
            "Sam Taylor (ST)",
            "Ben Jackson (ST)"
        ]
        substitutes = [
            "Dan Anderson",
            "Ryan White",
            "Matt Harris"
        ]
        
        result = tool._run(fixture_details, match_date, match_time, starters, substitutes)
        print(f"✅ Squad announcement sent: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending squad announcement: {e}")
        return False


def test_payment_reminder():
    """Test sending a payment reminder."""
    print("\n💰 Testing Payment Reminder...")
    
    try:
        from src.tools.telegram_tools import SendPaymentReminderTool
        
        tool = SendPaymentReminderTool()
        unpaid_players = ["John Smith", "Mike Johnson", "David Wilson"]
        amount = 15.00
        fixture_details = "vs Thunder FC"
        
        result = tool._run(unpaid_players, amount, fixture_details)
        print(f"✅ Payment reminder sent: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending payment reminder: {e}")
        return False


def test_rich_formatting():
    """Test rich formatting with HTML."""
    print("\n🎨 Testing Rich Formatting...")
    
    try:
        from src.tools.telegram_tools import SendTelegramMessageTool, get_team_name
        
        tool = SendTelegramMessageTool()
        team_name = get_team_name()
        message = f"""
🎯 <b>{team_name} Team Update</b>

📅 <b>Next Match:</b> Sunday vs Thunder FC
🕐 <b>Time:</b> 2:00 PM
📍 <b>Location:</b> Central Park

📋 <b>Current Squad:</b>
• John Smith (Captain)
• Mike Johnson (Vice Captain)
• David Wilson
• Tom Brown

💰 <b>Match Fee:</b> £15 per player

<i>Please confirm your availability by voting in the poll above!</i>
        """.strip()
        
        result = tool._run(message)
        print(f"✅ Rich formatting test sent: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending rich formatting: {e}")
        return False


def test_team_introduction():
    """Test sending a team introduction message."""
    print("\n🤖 Testing Team Introduction...")
    
    try:
        from src.tools.telegram_tools import SendTelegramMessageTool, get_team_name
        
        tool = SendTelegramMessageTool()
        team_name = get_team_name()
        message = f"""
🤖 <b>Welcome to {team_name} Team Manager!</b>

This AI-powered bot will help manage our Sunday League team:

✅ <b>Features:</b>
• Check availability for matches
• Announce squads and lineups
• Send payment reminders
• Manage team communications
• Track player statistics

📱 <b>How to use:</b>
• Vote in availability polls
• Respond to squad announcements
• Check payment status
• Ask questions about fixtures

🎯 <b>Let's get started!</b>
The bot will send regular updates and polls to keep everyone informed.
        """.strip()
        
        result = tool._run(message)
        print(f"✅ Team introduction sent: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending team introduction: {e}")
        return False


def test_bot_connection():
    """Test if the bot can connect to Telegram API."""
    print("\n🔗 Testing Bot Connection...")
    
    try:
        import requests
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ Bot connected successfully!")
            print(f"   Name: {bot_info['first_name']}")
            print(f"   Username: @{bot_info['username']}")
            print(f"   ID: {bot_info['id']}")
            return True
        else:
            print(f"❌ Bot API error: {data.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to bot: {e}")
        return False


def test_chat_access():
    """Test if the bot can access the chat."""
    print("\n💬 Testing Chat Access...")
    
    try:
        import requests
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        
        response = requests.get(url, params={'chat_id': chat_id})
        response.raise_for_status()
        
        data = response.json()
        if data.get('ok'):
            chat_info = data['result']
            print(f"✅ Chat access successful!")
            print(f"   Title: {chat_info.get('title', 'Private Chat')}")
            print(f"   Type: {chat_info['type']}")
            print(f"   ID: {chat_info['id']}")
            return True
        else:
            print(f"❌ Chat access error: {data.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing chat: {e}")
        return False


def main():
    """Run all Telegram tests."""
    print("🚀 KICKAI Telegram Integration Test")
    print("=" * 50)
    
    # Test environment
    if not test_telegram_environment():
        print("\n❌ Environment setup failed. Please check your .env file.")
        return
    
    # Test connection
    if not test_bot_connection():
        print("\n❌ Bot connection failed. Please check your bot token.")
        return
    
    if not test_chat_access():
        print("\n❌ Chat access failed. Please check your chat ID.")
        return
    
    # Test features
    tests = [
        test_basic_message,
        test_rich_formatting,
        test_telegram_poll,
        test_availability_poll,
        test_squad_announcement,
        test_payment_reminder,
        test_team_introduction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(2)  # Wait between tests to avoid rate limiting
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Telegram tests passed! Your integration is working perfectly.")
        print("\n📱 Next steps:")
        print("1. Invite your team members to the Telegram group")
        print("2. Start using the bot for team management")
        print("3. Customize messages and features as needed")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify your bot token is correct")
        print("2. Ensure the bot is added to your group")
        print("3. Check that the bot has permission to send messages")
        print("4. Verify your chat ID is correct")


if __name__ == "__main__":
    main() 