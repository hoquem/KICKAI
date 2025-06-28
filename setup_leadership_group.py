#!/usr/bin/env python3
"""
Setup Leadership Group for BP Hatters FC
Creates a separate Telegram group for team leadership and updates database schema
Updated for dual-channel architecture support
"""

import os
import requests
import json
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_telegram_bot_token() -> str:
    """Get the bot token for BP Hatters FC from database or environment."""
    # For now, we'll use the environment variable
    # Later we can fetch from database
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
    return token

def get_supabase_client():
    """Get Supabase client for database operations."""
    try:
        from supabase import create_client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        return create_client(url, key)
    except ImportError:
        print("⚠️  Supabase client not available. Install with: pip install supabase")
        return None
    except Exception as e:
        print(f"❌ Error creating Supabase client: {e}")
        return None

def create_telegram_group(bot_token: str, group_name: str, description: str = "") -> Optional[str]:
    """
    Create a new Telegram group using the bot.
    Note: This is a simplified approach - in practice, you'd create the group manually
    and then get the chat ID.
    """
    print(f"📱 Creating Telegram group: {group_name}")
    print(f"📝 Description: {description}")
    print("\n🔧 Manual Steps Required:")
    print("1. Open Telegram and create a new group")
    print(f"2. Name it: {group_name}")
    print(f"3. Add description: {description}")
    print("4. Add @bphatters_bot to the group")
    print("5. Make the bot an admin (required for commands)")
    print("6. Send a message in the group")
    print("7. Get the chat ID using the command below")
    
    return None

def get_chat_id(bot_token: str) -> Optional[str]:
    """Get chat ID for the most recent group the bot was added to."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            # Find the most recent group chat
            for update in reversed(data['result']):
                if 'message' in update and 'chat' in update['message']:
                    chat = update['message']['chat']
                    if chat.get('type') == 'group' or chat.get('type') == 'supergroup':
                        chat_id = chat['id']
                        chat_title = chat.get('title', 'Unknown')
                        print(f"✅ Found group: {chat_title} (ID: {chat_id})")
                        return str(chat_id)
        
        print("❌ No group chats found in recent updates")
        print("💡 Make sure to send a message in the new group after adding the bot")
        return None
        
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")
        return None

def update_database_schema():
    """Update database schema to support dual-chat architecture."""
    print("\n🗄️ Updating Database Schema...")
    
    # SQL to add leadership_chat_id column to team_bots table
    sql_commands = [
        """
        -- Add leadership_chat_id column to team_bots table
        ALTER TABLE team_bots 
        ADD COLUMN IF NOT EXISTS leadership_chat_id VARCHAR(255);
        """,
        """
        -- Add leadership_chat_id column to teams table as backup
        ALTER TABLE teams 
        ADD COLUMN IF NOT EXISTS leadership_chat_id VARCHAR(255);
        """,
        """
        -- Add telegram_user_id column to team_members table
        ALTER TABLE team_members 
        ADD COLUMN IF NOT EXISTS telegram_user_id VARCHAR(100);
        """,
        """
        -- Add command_logs table for tracking bot commands
        CREATE TABLE IF NOT EXISTS command_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
            chat_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            username VARCHAR(100),
            command VARCHAR(100) NOT NULL,
            arguments TEXT,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        -- Add indexes for performance
        CREATE INDEX IF NOT EXISTS idx_command_logs_team_id ON command_logs(team_id);
        CREATE INDEX IF NOT EXISTS idx_command_logs_chat_id ON command_logs(chat_id);
        CREATE INDEX IF NOT EXISTS idx_command_logs_command ON command_logs(command);
        CREATE INDEX IF NOT EXISTS idx_command_logs_executed_at ON command_logs(executed_at);
        CREATE INDEX IF NOT EXISTS idx_team_members_telegram_user_id ON team_members(telegram_user_id);
        """
    ]
    
    print("📋 SQL Commands to run in Supabase:")
    for i, sql in enumerate(sql_commands, 1):
        print(f"\n--- Command {i} ---")
        print(sql.strip())
    
    print("\n💡 Run these commands in your Supabase SQL Editor")

def update_team_bot_mapping(leadership_chat_id: str):
    """Update the team_bots table with the leadership chat ID."""
    print(f"\n🔄 Updating team bot mapping with leadership chat ID: {leadership_chat_id}")
    
    # Try to update via Supabase if available
    supabase = get_supabase_client()
    if supabase:
        try:
            response = supabase.table('team_bots').update({
                'leadership_chat_id': leadership_chat_id
            }).eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').execute()
            
            if response.data:
                print("✅ Successfully updated team_bots table via Supabase")
                return
            else:
                print("⚠️  No rows updated via Supabase")
        except Exception as e:
            print(f"⚠️  Error updating via Supabase: {e}")
    
    # Fallback to SQL command
    sql = f"""
    -- Update BP Hatters FC with leadership chat ID
    UPDATE team_bots 
    SET leadership_chat_id = '{leadership_chat_id}'
    WHERE team_id = '0854829d-445c-4138-9fd3-4db562ea46ee';
    """
    
    print("📋 SQL Command to run in Supabase:")
    print(sql.strip())

def add_leadership_members():
    """Add leadership team members to the database."""
    print("\n👥 Adding Leadership Team Members...")
    
    leadership_members = [
        {
            'name': 'Alex Johnson',
            'role': 'admin',
            'phone': '+447123456789',
            'telegram_username': 'alex_admin'
        },
        {
            'name': 'Ben Smith',
            'role': 'manager',
            'phone': '+447123456790',
            'telegram_username': 'ben_manager'
        },
        {
            'name': 'Charlie Brown',
            'role': 'secretary',
            'phone': '+447123456791',
            'telegram_username': 'charlie_secretary'
        },
        {
            'name': 'David Wilson',
            'role': 'treasurer',
            'phone': '+447123456792',
            'telegram_username': 'david_treasurer'
        },
        {
            'name': 'Ethan Davis',
            'role': 'helper',
            'phone': '+447123456793',
            'telegram_username': 'ethan_helper'
        }
    ]
    
    supabase = get_supabase_client()
    if supabase:
        try:
            for member in leadership_members:
                # First, create or get the player
                player_response = supabase.table('players').upsert({
                    'name': member['name'],
                    'phone_number': member['phone'],
                    'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                    'is_active': True
                }).execute()
                
                if player_response.data:
                    player_id = player_response.data[0]['id']
                    
                    # Then create the team member record
                    member_response = supabase.table('team_members').upsert({
                        'team_id': '0854829d-445c-4138-9fd3-4db562ea46ee',
                        'player_id': player_id,
                        'phone': member['phone'],
                        'role': member['role'],
                        'telegram_username': member['telegram_username'],
                        'is_active': True
                    }).execute()
                    
                    if member_response.data:
                        print(f"✅ Added {member['name']} as {member['role']}")
                    else:
                        print(f"⚠️  Failed to add team member record for {member['name']}")
                else:
                    print(f"⚠️  Failed to add player record for {member['name']}")
        except Exception as e:
            print(f"❌ Error adding leadership members: {e}")
    else:
        print("📋 SQL Commands to add leadership members:")
        for member in leadership_members:
            sql = f"""
            -- First, create or update the player
            INSERT INTO players (name, phone_number, team_id, is_active)
            VALUES ('{member['name']}', '{member['phone']}', '0854829d-445c-4138-9fd3-4db562ea46ee', TRUE)
            ON CONFLICT (phone_number) DO UPDATE SET
                name = EXCLUDED.name,
                team_id = EXCLUDED.team_id,
                is_active = TRUE
            RETURNING id;
            
            -- Then, create or update the team member record
            INSERT INTO team_members (team_id, player_id, phone, role, telegram_username, is_active)
            SELECT '0854829d-445c-4138-9fd3-4db562ea46ee', id, '{member['phone']}', '{member['role']}', '{member['telegram_username']}', TRUE
            FROM players WHERE phone_number = '{member['phone']}'
            ON CONFLICT (team_id, phone) DO UPDATE SET
                role = EXCLUDED.role,
                telegram_username = EXCLUDED.telegram_username,
                updated_at = NOW();
            """
            print(f"\n--- {member['name']} ---")
            print(sql.strip())

def create_command_handlers():
    """Create the command handler structure for the bot."""
    print("\n🤖 Creating Command Handler Structure...")
    
    commands = [
        # Fixture Management
        ("/newfixture", "Create a new fixture", "admin,secretary"),
        ("/deletefixture", "Delete a fixture", "admin,secretary"),
        ("/updatefixture", "Update fixture details", "admin,secretary"),
        ("/listfixtures", "List all fixtures", "admin,secretary,manager"),
        
        # Availability Management
        ("/sendavailability", "Send availability poll", "admin,secretary,manager"),
        ("/checkavailability", "Check availability status", "admin,secretary,manager"),
        
        # Squad Management
        ("/selectsquad", "Select squad for fixture", "admin,manager"),
        ("/announcesquad", "Announce squad to team", "admin,secretary,manager"),
        
        # Payment Management
        ("/createpayment", "Create payment link", "admin,treasurer"),
        ("/sendpayment", "Send payment reminder", "admin,treasurer"),
        ("/checkpayments", "Check payment status", "admin,treasurer"),
        
        # Team Management
        ("/addmember", "Add team member", "admin"),
        ("/removemember", "Remove team member", "admin"),
        ("/updaterole", "Update member role", "admin"),
        ("/listmembers", "List team members", "admin,secretary,manager"),
        
        # Help
        ("/help", "Show available commands", "all"),
        ("/status", "Show team status", "admin,secretary,manager")
    ]
    
    print("📋 Commands for Leadership Group:")
    for command, description, roles in commands:
        print(f"  {command:<15} - {description:<30} [{roles}]")
    
    print("\n💡 These commands will only work in the leadership group")
    print("💡 Natural language will work in the main team group")

def test_dual_channel_setup():
    """Test the dual-channel setup."""
    print("\n🧪 Testing Dual-Channel Setup...")
    
    supabase = get_supabase_client()
    if not supabase:
        print("⚠️  Cannot test without Supabase connection")
        return
    
    try:
        # Test team_bots table
        response = supabase.table('team_bots').select('*').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').execute()
        if response.data:
            bot_data = response.data[0]
            print(f"✅ Team bot found: {bot_data.get('bot_username', 'Unknown')}")
            if bot_data.get('leadership_chat_id'):
                print(f"✅ Leadership chat ID: {bot_data['leadership_chat_id']}")
            else:
                print("⚠️  Leadership chat ID not set")
        else:
            print("❌ No team bot found")
        
        # Test team_members table with player names
        response = supabase.table('team_members').select('*, players(name)').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').in_('role', ['admin', 'secretary', 'manager', 'treasurer']).execute()
        if response.data:
            print(f"✅ Found {len(response.data)} leadership members")
            for member in response.data:
                player_name = member.get('players', {}).get('name', 'Unknown') if member.get('players') else 'Unknown'
                print(f"   - {player_name} ({member['role']})")
        else:
            print("⚠️  No leadership members found")
        
        # Test command_logs table
        response = supabase.table('command_logs').select('*').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').limit(5).execute()
        if response.data:
            print(f"✅ Found {len(response.data)} command logs")
        else:
            print("ℹ️  No command logs found (normal for new setup)")
            
    except Exception as e:
        print(f"❌ Error testing setup: {e}")

def main():
    """Main setup function."""
    print("🏆 BP Hatters FC Leadership Group Setup")
    print("=" * 50)
    
    # Get bot token
    try:
        bot_token = get_telegram_bot_token()
        print(f"✅ Bot token found: {bot_token[:10]}...")
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Create leadership group
    group_name = "BP Hatters FC - Leadership"
    description = "Private management group for BP Hatters FC team leadership"
    create_telegram_group(bot_token, group_name, description)
    
    # Get chat ID
    print(f"\n🔍 Getting chat ID for {group_name}...")
    print("💡 After creating the group and adding the bot, run:")
    print(f"   curl -s 'https://api.telegram.org/bot{bot_token}/getUpdates' | python -m json.tool")
    
    # Update database schema
    update_database_schema()
    
    # Add leadership members
    add_leadership_members()
    
    # Create command handlers
    create_command_handlers()
    
    # Test setup
    test_dual_channel_setup()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Create the leadership Telegram group manually")
    print("2. Add @bphatters_bot to the group")
    print("3. Make the bot an admin")
    print("4. Send a message in the group")
    print("5. Get the chat ID using the curl command above")
    print("6. Run the SQL commands in Supabase")
    print("7. Update the team_bots table with the leadership chat ID")
    print("8. Test the dual-chat architecture")
    print("\n💡 After setup, you can test with:")
    print("   python test_dual_chat_architecture.py")

if __name__ == "__main__":
    main() 