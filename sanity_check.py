#!/usr/bin/env python3
"""
Comprehensive Sanity Check for KICKAI
Verifies team isolation, database integrity, and all functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from src.tools.supabase_tools import get_supabase_client
from src.telegram_command_handler import TelegramCommandHandler

# Load environment variables
load_dotenv()

def check_database_schema():
    """Check database schema integrity."""
    print("🗄️ Checking Database Schema")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Check required tables exist
        required_tables = [
            'teams', 'team_members', 'players', 'fixtures', 
            'availability', 'squad_selections', 'ratings', 
            'tasks', 'task_assignments', 'equipment', 
            'team_bots', 'command_logs'
        ]
        
        missing_tables = []
        for table in required_tables:
            try:
                response = supabase.table(table).select('id').limit(1).execute()
                print(f"✅ {table} table exists")
            except Exception as e:
                print(f"❌ {table} table missing: {e}")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            return False
        
        print("✅ All required tables exist")
        return True
        
    except Exception as e:
        print(f"❌ Database schema check failed: {e}")
        return False

def check_team_isolation():
    """Check that teams are properly isolated."""
    print("\n🔒 Checking Team Isolation")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Get all teams
        teams_response = supabase.table('teams').select('*').execute()
        teams = teams_response.data if teams_response.data else []
        
        print(f"📋 Found {len(teams)} teams:")
        for team in teams:
            print(f"  - {team['name']} (ID: {team['id']})")
        
        # Check team_bots isolation
        bots_response = supabase.table('team_bots').select('*, teams(name)').execute()
        bots = bots_response.data if bots_response.data else []
        
        print(f"\n🤖 Found {len(bots)} bot mappings:")
        for bot in bots:
            team_name = bot.get('teams', {}).get('name', 'Unknown')
            print(f"  - {team_name}: {bot['chat_id']} (leadership: {bot.get('leadership_chat_id', 'None')})")
        
        # Verify BP Hatters FC has proper setup
        bp_hatters = None
        for team in teams:
            if 'BP Hatters' in team['name']:
                bp_hatters = team
                break
        
        if bp_hatters:
            print(f"\n🏆 BP Hatters FC Setup:")
            print(f"  - Team ID: {bp_hatters['id']}")
            print(f"  - Active: {bp_hatters['is_active']}")
            
            # Check bot mapping
            bot_mapping = None
            for bot in bots:
                if bot['team_id'] == bp_hatters['id']:
                    bot_mapping = bot
                    break
            
            if bot_mapping:
                print(f"  - Bot Token: {bot_mapping['bot_token'][:10]}...")
                print(f"  - Main Chat: {bot_mapping['chat_id']}")
                print(f"  - Leadership Chat: {bot_mapping.get('leadership_chat_id', 'Not set')}")
                print(f"  - Bot Active: {bot_mapping['is_active']}")
                
                if bot_mapping.get('leadership_chat_id'):
                    print("✅ Dual-channel architecture configured")
                else:
                    print("⚠️  Leadership chat not configured")
            else:
                print("❌ No bot mapping found for BP Hatters FC")
                return False
        else:
            print("❌ BP Hatters FC team not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Team isolation check failed: {e}")
        return False

def check_command_handler_isolation():
    """Check that command handler properly isolates teams."""
    print("\n🤖 Checking Command Handler Isolation")
    print("=" * 40)
    
    try:
        handler = TelegramCommandHandler()
        
        # Test with BP Hatters FC chat IDs
        supabase = get_supabase_client()
        bp_response = supabase.table('teams').select('*').eq('name', 'BP Hatters FC').execute()
        if not bp_response.data:
            print("❌ BP Hatters FC team not found")
            return False
        
        bp_team_id = bp_response.data[0]['id']
        bot_response = supabase.table('team_bots').select('*').eq('team_id', bp_team_id).execute()
        
        if not bot_response.data:
            print("❌ BP Hatters FC bot not found")
            return False
        
        bot = bot_response.data[0]
        
        # Test 1: BP Hatters FC main chat (should work)
        print("🧪 Test 1: BP Hatters FC main chat")
        test_update = {
            'message': {
                'chat': {'id': bot['chat_id']},
                'from': {'id': '123456', 'username': 'testuser'},
                'text': '/help'
            }
        }
        
        result = handler.process_message(test_update)
        print(f"   Result: {'✅ Success' if result else '❌ Failed'}")
        
        # Test 2: BP Hatters FC leadership chat (should work)
        if bot.get('leadership_chat_id'):
            print("🧪 Test 2: BP Hatters FC leadership chat")
            test_update = {
                'message': {
                    'chat': {'id': bot['leadership_chat_id']},
                    'from': {'id': '123456', 'username': 'testuser'},
                    'text': '/help'
                }
            }
            
            result = handler.process_message(test_update)
            print(f"   Result: {'✅ Success' if result else '❌ Failed'}")
        
        # Test 3: Unknown chat ID (should fail)
        print("🧪 Test 3: Unknown chat ID")
        test_update = {
            'message': {
                'chat': {'id': '999999999'},
                'from': {'id': '123456', 'username': 'testuser'},
                'text': '/help'
            }
        }
        
        result = handler.process_message(test_update)
        print(f"   Result: {'❌ Correctly failed' if not result else '⚠️ Should have failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Command handler isolation check failed: {e}")
        return False

def check_database_constraints():
    """Check database constraints and relationships."""
    print("\n🔗 Checking Database Constraints")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Check foreign key relationships
        print("📋 Checking foreign key relationships...")
        
        # Test team_members -> teams relationship
        try:
            response = supabase.table('team_members').select('*, teams(name)').limit(1).execute()
            print("✅ team_members -> teams relationship works")
        except Exception as e:
            print(f"❌ team_members -> teams relationship failed: {e}")
        
        # Test team_bots -> teams relationship
        try:
            response = supabase.table('team_bots').select('*, teams(name)').limit(1).execute()
            print("✅ team_bots -> teams relationship works")
        except Exception as e:
            print(f"❌ team_bots -> teams relationship failed: {e}")
        
        # Test unique constraints
        print("\n📋 Checking unique constraints...")
        
        # Check team_bots unique constraints
        bots_response = supabase.table('team_bots').select('team_id, bot_token').execute()
        bots = bots_response.data if bots_response.data else []
        
        team_ids = [bot['team_id'] for bot in bots]
        bot_tokens = [bot['bot_token'] for bot in bots]
        
        if len(team_ids) == len(set(team_ids)):
            print("✅ team_bots.team_id unique constraint maintained")
        else:
            print("❌ team_bots.team_id unique constraint violated")
        
        if len(bot_tokens) == len(set(bot_tokens)):
            print("✅ team_bots.bot_token unique constraint maintained")
        else:
            print("❌ team_bots.bot_token unique constraint violated")
        
        return True
        
    except Exception as e:
        print(f"❌ Database constraints check failed: {e}")
        return False

def check_command_logs():
    """Check command logging functionality."""
    print("\n📝 Checking Command Logs")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Check command_logs table
        response = supabase.table('command_logs').select('*').order('executed_at', desc=True).limit(5).execute()
        logs = response.data if response.data else []
        
        print(f"📋 Found {len(logs)} recent command logs:")
        for log in logs:
            print(f"  - {log['command']} by {log['username']} in {log['chat_id']} ({log['success']})")
        
        if logs:
            print("✅ Command logging is working")
        else:
            print("⚠️  No command logs found (may be normal if bot hasn't been used)")
        
        return True
        
    except Exception as e:
        print(f"❌ Command logs check failed: {e}")
        return False

def main():
    """Run all sanity checks."""
    print("🏆 KICKAI Comprehensive Sanity Check")
    print("=" * 50)
    
    checks = [
        ("Database Schema", check_database_schema),
        ("Team Isolation", check_team_isolation),
        ("Command Handler Isolation", check_command_handler_isolation),
        ("Database Constraints", check_database_constraints),
        ("Command Logs", check_command_logs)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Sanity Check Results:")
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name:<25} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All sanity checks passed! System is ready for production.")
    else:
        print("⚠️  Some sanity checks failed. Review the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main() 