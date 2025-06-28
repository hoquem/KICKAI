#!/usr/bin/env python3
"""
Add Test Users for KICKAI
Adds test users to the database for real user testing
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_supabase_client():
    """Get Supabase client."""
    try:
        from src.tools.supabase_tools import get_supabase_client
        return get_supabase_client()
    except ImportError:
        from tools.supabase_tools import get_supabase_client
        return get_supabase_client()

def add_test_users():
    """Add test users to the database."""
    try:
        supabase = get_supabase_client()
        
        # Test users data
        test_users = [
            {
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                'telegram_user_id': '1581500055',  # Your user ID
                'telegram_username': 'mahmud',
                'role': 'captain',
                'is_active': True
            },
            {
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                'telegram_user_id': '123456789',  # Test user 1
                'telegram_username': 'testuser1',
                'role': 'player',
                'is_active': True
            },
            {
                'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                'telegram_user_id': '987654321',  # Test user 2
                'telegram_username': 'testuser2',
                'role': 'player',
                'is_active': True
            }
        ]
        
        print("👥 Adding test users to database...")
        
        for user in test_users:
            try:
                # Check if user already exists
                existing = supabase.table('team_members').select('*').eq('telegram_user_id', user['telegram_user_id']).eq('team_id', user['team_id']).execute()
                
                if existing.data:
                    logger.info(f"✅ User {user['telegram_username']} already exists")
                else:
                    # Insert new user
                    result = supabase.table('team_members').insert(user).execute()
                    if result.data:
                        logger.info(f"✅ Added user: {user['telegram_username']} (Role: {user['role']})")
                    else:
                        logger.error(f"❌ Failed to add user: {user['telegram_username']}")
                        
            except Exception as e:
                logger.error(f"❌ Error adding user {user['telegram_username']}: {e}")
        
        print("\n📋 Current team members:")
        members = supabase.table('team_members').select('*').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').eq('is_active', True).execute()
        
        for member in members.data:
            print(f"   👤 {member['telegram_username']} (ID: {member['telegram_user_id']}, Role: {member['role']})")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")

def main():
    """Main function."""
    print("👥 KICKAI Test Users Setup")
    print("=" * 30)
    
    add_test_users()
    
    print("\n✅ Test users setup completed!")
    print("\n💡 Next steps:")
    print("   1. Deploy to Railway")
    print("   2. Invite users to Telegram groups")
    print("   3. Test bot commands")

if __name__ == "__main__":
    main() 