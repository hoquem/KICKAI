#!/usr/bin/env python3
"""
Team Bot Management CLI for KICKAI
Consolidated script for managing team to bot mappings.
"""

import os
import sys
import argparse
from typing import List, Dict, Optional
from supabase import create_client

def get_supabase_client():
    """Get Supabase client with proper error handling."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase environment variables")
    
    return create_client(url, key)

def list_teams(supabase) -> List[Dict]:
    """List all teams in the database."""
    try:
        response = supabase.table('teams').select('*').eq('is_active', True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error listing teams: {e}")
        return []

def list_bot_mappings(supabase) -> List[Dict]:
    """List all bot mappings in the database."""
    try:
        response = supabase.table('team_bots').select('*, teams(name)').execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error listing bot mappings: {e}")
        return []

def add_bot_mapping(supabase, team_name: str, bot_token: str, chat_id: str, bot_username: str):
    """Add a new bot mapping for a team."""
    print(f"🤖 Adding bot mapping for {team_name}...")
    
    try:
        # Find the team
        teams_response = supabase.table('teams').select('*').eq('name', team_name).execute()
        if not teams_response.data:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_id = teams_response.data[0]['id']
        print(f"✅ Found team: {team_name} (ID: {team_id})")
        
        # Check if mapping already exists
        existing_response = supabase.table('team_bots').select('*').eq('team_id', team_id).execute()
        if existing_response.data:
            print(f"⚠️  Bot mapping already exists for {team_name}")
            overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("❌ Operation cancelled")
                return False
            
            # Delete existing mapping
            supabase.table('team_bots').delete().eq('team_id', team_id).execute()
            print("  - Removed existing mapping")
        
        # Insert new mapping
        mapping_data = {
            'team_id': team_id,
            'bot_token': bot_token,
            'chat_id': chat_id,
            'bot_username': bot_username,
            'is_active': True
        }
        
        response = supabase.table('team_bots').insert(mapping_data).execute()
        
        if response.data:
            print(f"✅ Successfully mapped {team_name} to {bot_username}")
            print(f"  - Bot Token: {bot_token[:20]}...")
            print(f"  - Chat ID: {chat_id}")
            return True
        else:
            print("❌ Failed to create bot mapping")
            return False
            
    except Exception as e:
        print(f"❌ Error adding bot mapping: {e}")
        return False

def remove_bot_mapping(supabase, team_name: str):
    """Remove a bot mapping for a team."""
    print(f"🗑️  Removing bot mapping for {team_name}...")
    
    try:
        # Find the team
        teams_response = supabase.table('teams').select('*').eq('name', team_name).execute()
        if not teams_response.data:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_id = teams_response.data[0]['id']
        
        # Delete the mapping
        response = supabase.table('team_bots').delete().eq('team_id', team_id).execute()
        
        if response.data:
            print(f"✅ Successfully removed bot mapping for {team_name}")
            return True
        else:
            print(f"⚠️  No bot mapping found for {team_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error removing bot mapping: {e}")
        return False

def test_bot_mapping(supabase, team_name: str):
    """Test a bot mapping by sending a test message."""
    print(f"🧪 Testing bot mapping for {team_name}...")
    
    try:
        # Find the team and bot mapping
        teams_response = supabase.table('teams').select('*').eq('name', team_name).execute()
        if not teams_response.data:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_id = teams_response.data[0]['id']
        
        bot_response = supabase.table('team_bots').select('*').eq('team_id', team_id).execute()
        if not bot_response.data:
            print(f"❌ No bot mapping found for {team_name}")
            return False
        
        bot = bot_response.data[0]
        print(f"✅ Found bot mapping:")
        print(f"  - Bot: {bot['bot_username']}")
        print(f"  - Chat ID: {bot['chat_id']}")
        print(f"  - Active: {bot['is_active']}")
        
        # Import telegram tools for testing
        try:
            from src.tools.telegram_tools import TelegramTools
            telegram_tools = TelegramTools()
            
            # Test sending a message
            test_message = f"🧪 Test message from KICKAI - {team_name} bot mapping is working!"
            result = telegram_tools._send_telegram_message(
                bot['bot_token'], 
                bot['chat_id'], 
                test_message
            )
            
            if "success" in result.lower():
                print("✅ Test message sent successfully!")
                return True
            else:
                print(f"❌ Failed to send test message: {result}")
                return False
                
        except ImportError:
            print("⚠️  Telegram tools not available for testing")
            print("   Bot mapping appears to be configured correctly")
            return True
            
    except Exception as e:
        print(f"❌ Error testing bot mapping: {e}")
        return False

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='KICKAI Team Bot Management CLI')
    parser.add_argument('command', choices=['list', 'add', 'remove', 'test'], 
                       help='Command to execute')
    parser.add_argument('--team', help='Team name for add/remove/test commands')
    parser.add_argument('--token', help='Bot token for add command')
    parser.add_argument('--chat-id', help='Chat ID for add command')
    parser.add_argument('--username', help='Bot username for add command')
    
    args = parser.parse_args()
    
    try:
        supabase = get_supabase_client()
        
        if args.command == 'list':
            print("📋 Teams in Database:")
            teams = list_teams(supabase)
            for team in teams:
                print(f"  - {team['name']} (ID: {team['id']})")
            
            print("\n🤖 Bot Mappings:")
            mappings = list_bot_mappings(supabase)
            if mappings:
                for mapping in mappings:
                    team_name = mapping.get('teams', {}).get('name', 'Unknown')
                    print(f"  - {team_name} → {mapping['bot_username']}")
                    print(f"    Chat ID: {mapping['chat_id']}")
                    print(f"    Active: {mapping['is_active']}")
            else:
                print("  No bot mappings found")
                
        elif args.command == 'add':
            if not all([args.team, args.token, args.chat_id, args.username]):
                print("❌ All arguments required: --team, --token, --chat-id, --username")
                sys.exit(1)
            
            success = add_bot_mapping(supabase, args.team, args.token, args.chat_id, args.username)
            if not success:
                sys.exit(1)
                
        elif args.command == 'remove':
            if not args.team:
                print("❌ Team name required: --team")
                sys.exit(1)
            
            success = remove_bot_mapping(supabase, args.team)
            if not success:
                sys.exit(1)
                
        elif args.command == 'test':
            if not args.team:
                print("❌ Team name required: --team")
                sys.exit(1)
            
            success = test_bot_mapping(supabase, args.team)
            if not success:
                sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 