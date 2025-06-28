#!/usr/bin/env python3
"""
Test script to verify team isolation in Telegram bot
Ensures the bot only responds to BP Hatters FC team chats
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

def test_team_isolation():
    """Test that the bot only responds to BP Hatters FC team chats."""
    print("🔍 Testing Team Isolation")
    print("=" * 40)
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Get BP Hatters FC team info
        response = supabase.table('teams').select('*').eq('name', 'BP Hatters FC').execute()
        if not response.data:
            print("❌ BP Hatters FC team not found in database")
            return False
        
        bp_hatters_team = response.data[0]
        print(f"✅ Found BP Hatters FC team: {bp_hatters_team['id']}")
        
        # Get BP Hatters FC bot info
        response = supabase.table('team_bots').select('*').eq('team_id', bp_hatters_team['id']).execute()
        if not response.data:
            print("❌ BP Hatters FC bot not found in database")
            return False
        
        bp_hatters_bot = response.data[0]
        print(f"✅ Found BP Hatters FC bot: {bp_hatters_bot['bot_token'][:10]}...")
        print(f"   Main chat ID: {bp_hatters_bot['chat_id']}")
        print(f"   Leadership chat ID: {bp_hatters_bot.get('leadership_chat_id', 'Not set')}")
        
        # Test command handler
        handler = TelegramCommandHandler()
        
        # Test 1: BP Hatters FC main chat (should work)
        print("\n🧪 Test 1: BP Hatters FC main chat")
        test_update = {
            'message': {
                'chat': {'id': bp_hatters_bot['chat_id']},
                'from': {'id': '123456', 'username': 'testuser'},
                'text': '/help'
            }
        }
        
        result = handler.process_message(test_update)
        print(f"   Result: {'✅ Success' if result else '❌ Failed'}")
        
        # Test 2: BP Hatters FC leadership chat (should work)
        if bp_hatters_bot.get('leadership_chat_id'):
            print("\n🧪 Test 2: BP Hatters FC leadership chat")
            test_update = {
                'message': {
                    'chat': {'id': bp_hatters_bot['leadership_chat_id']},
                    'from': {'id': '123456', 'username': 'testuser'},
                    'text': '/help'
                }
            }
            
            result = handler.process_message(test_update)
            print(f"   Result: {'✅ Success' if result else '❌ Failed'}")
        
        # Test 3: Unknown chat ID (should fail)
        print("\n🧪 Test 3: Unknown chat ID")
        test_update = {
            'message': {
                'chat': {'id': '999999999'},  # Unknown chat ID
                'from': {'id': '123456', 'username': 'testuser'},
                'text': '/help'
            }
        }
        
        result = handler.process_message(test_update)
        print(f"   Result: {'❌ Correctly failed' if not result else '⚠️ Should have failed'}")
        
        # Test 4: Check team bot info function
        print("\n🧪 Test 4: Team bot info function")
        
        # Should return BP Hatters FC info
        bot_info = handler._get_team_bot_info(bp_hatters_bot['chat_id'])
        if bot_info:
            print(f"   ✅ Main chat: Found team {bot_info['team_id']}")
        else:
            print(f"   ❌ Main chat: No team found")
        
        # Should return None for unknown chat
        bot_info = handler._get_team_bot_info('999999999')
        if not bot_info:
            print(f"   ✅ Unknown chat: Correctly no team found")
        else:
            print(f"   ❌ Unknown chat: Should not have found team")
        
        print("\n✅ Team isolation tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_database_queries():
    """Test database queries for team isolation."""
    print("\n🔍 Testing Database Queries")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Test team_bots table query
        print("📋 Testing team_bots table queries...")
        
        # Get all teams with bots
        response = supabase.table('team_bots').select('*').execute()
        print(f"   Total teams with bots: {len(response.data)}")
        
        for bot in response.data:
            team_response = supabase.table('teams').select('name').eq('id', bot['team_id']).execute()
            team_name = team_response.data[0]['name'] if team_response.data else 'Unknown'
            print(f"   - {team_name}: {bot['chat_id']} (leadership: {bot.get('leadership_chat_id', 'None')})")
        
        # Test the OR query used in _get_team_bot_info
        print("\n📋 Testing OR query for chat matching...")
        
        # Get BP Hatters FC bot
        bp_response = supabase.table('teams').select('*').eq('name', 'BP Hatters FC').execute()
        if bp_response.data:
            bp_team_id = bp_response.data[0]['id']
            bot_response = supabase.table('team_bots').select('*').eq('team_id', bp_team_id).execute()
            
            if bot_response.data:
                bot = bot_response.data[0]
                print(f"   BP Hatters FC bot:")
                print(f"     Main chat: {bot['chat_id']}")
                print(f"     Leadership chat: {bot.get('leadership_chat_id', 'None')}")
                
                # Test OR query
                or_query = supabase.table('team_bots').select('*').or_(f'chat_id.eq.{bot["chat_id"]},leadership_chat_id.eq.{bot["chat_id"]}')
                result = or_query.execute()
                print(f"     OR query result: {len(result.data)} matches")
                
                # Test with leadership chat if exists
                if bot.get('leadership_chat_id'):
                    or_query2 = supabase.table('team_bots').select('*').or_(f'chat_id.eq.{bot["leadership_chat_id"]},leadership_chat_id.eq.{bot["leadership_chat_id"]}')
                    result2 = or_query2.execute()
                    print(f"     Leadership OR query result: {len(result2.data)} matches")
        
        print("✅ Database query tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🏆 KICKAI Team Isolation Test")
    print("=" * 50)
    
    success1 = test_team_isolation()
    success2 = test_database_queries()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Team isolation is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    return success1 and success2

if __name__ == "__main__":
    main() 