#!/usr/bin/env python3
"""
Leadership Group Setup Script
Sets up dual-channel Telegram configuration for team leadership.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.tools.firebase_tools import get_firebase_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_firebase_client():
    """Get Firebase client for database operations."""
    try:
        return get_firebase_client()
    except ImportError:
        print("⚠️  Firebase client not available. Install with: pip install firebase-admin")
        return None
    except Exception as e:
        print(f"❌ Error creating Firebase client: {e}")
        return None

def setup_leadership_group(team_name: str, leadership_chat_id: str):
    """Set up leadership group configuration."""
    print(f"🏆 Setting up leadership group for team: {team_name}")
    print(f"📱 Leadership chat ID: {leadership_chat_id}")
    print()
    
    # Step 1: Create leadership group in Telegram
    print("📋 Step 1: Create Leadership Group in Telegram")
    print("=" * 50)
    print("1. Open Telegram")
    print("2. Create a new group called 'BP Hatters FC - Leadership'")
    print("3. Add only team leaders (captain, vice-captain, secretary, treasurer)")
    print("4. Add the bot to this group")
    print("5. Make the bot an admin in this group")
    print("6. Get the group chat ID (use @userinfobot or similar)")
    print()
    
    # Step 2: Update database schema
    print("🗄️ Step 2: Update Database Schema")
    print("=" * 50)
    print("The team_bots table needs a 'leadership_chat_id' column.")
    print("This script will attempt to update the schema automatically.")
    print()
    
    # Step 3: Update bot mapping
    print("🤖 Step 3: Update Bot Mapping")
    print("=" * 50)
    print("The bot will be configured to handle two different chat types:")
    print("• Main group chat: All team members")
    print("• Leadership chat: Team leaders only")
    print()
    
    # Step 4: Test configuration
    print("🧪 Step 4: Test Configuration")
    print("=" * 50)
    print("After setup, test the following:")
    print("• Bot responds in main group")
    print("• Bot responds in leadership group")
    print("• Admin commands work in leadership group")
    print("• Regular commands work in main group")
    print()
    
    # Database update instructions
    print("📋 Database Schema Update")
    print("=" * 50)
    print("If automatic update fails, run these commands manually:")
    print()
    
    # SQL commands for manual execution
    print("📋 SQL Commands to run in Firebase:")
    print("1. Navigate to your Firebase project")
    print("2. Go to Firestore Database")
    print("3. The schema will be automatically updated when you add the leadership_chat_id field")
    print()
    
    print("💡 The leadership_chat_id field will be added automatically when you update the bot mapping")
    print()
    
    # Try to update via Firebase if available
    firebase = get_firebase_client()
    if firebase:
        try:
            # Find team by name
            teams_ref = firebase.collection('teams')
            team_query = teams_ref.where('name', '==', team_name)
            team_response = team_query.get()
            
            if team_response:
                team_doc = team_response[0]
                team_id = team_doc.id
                
                # Update bot mapping with leadership chat ID
                bots_ref = firebase.collection('team_bots')
                bot_query = bots_ref.where('team_id', '==', team_id)
                bot_response = bot_query.get()
                
                if bot_response:
                    bot_doc = bot_response[0]
                    bot_ref = firebase.collection('team_bots').document(bot_doc.id)
                    bot_ref.update({
                        'leadership_chat_id': leadership_chat_id,
                        'updated_at': datetime.now()
                    })
                    
                    print("✅ Successfully updated team_bots table via Firebase")
                    print(f"   Team: {team_name}")
                    print(f"   Leadership Chat ID: {leadership_chat_id}")
                else:
                    print("⚠️  No bot mapping found for this team")
            else:
                print("⚠️  Team not found in database")
                
        except Exception as e:
            print(f"⚠️  Error updating via Firebase: {e}")
    
    # Final instructions
    print("🎯 Final Setup Instructions")
    print("=" * 50)
    print("1. ✅ Create leadership group in Telegram")
    print("2. ✅ Add bot to leadership group")
    print("3. ✅ Make bot admin in leadership group")
    print("4. ✅ Update database with leadership chat ID")
    print("5. 🔄 Restart the bot application")
    print("6. 🧪 Test both group chats")
    print()
    
    print("📝 Command to update bot mapping:")
    print(f"python kickai_cli.py setup-dual --name '{team_name}' --leadership-chat-id '{leadership_chat_id}'")
    print()
    
    print("🎉 Leadership group setup complete!")
    print("The bot will now handle different commands based on the chat type.")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup leadership group for team')
    parser.add_argument('team_name', help='Name of the team')
    parser.add_argument('leadership_chat_id', help='Telegram chat ID of leadership group')
    
    args = parser.parse_args()
    
    setup_leadership_group(args.team_name, args.leadership_chat_id)

if __name__ == "__main__":
    main() 