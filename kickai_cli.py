#!/usr/bin/env python3
"""
KICKAI Comprehensive CLI Tool
Supports team management, bot management, dual-channel setup, and testing
"""

import os
import sys
import argparse
import subprocess
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Get Supabase client with proper error handling."""
    try:
        from supabase import create_client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("Missing Supabase environment variables")
        
        return create_client(url, key)
    except ImportError:
        print("❌ Supabase client not available. Install with: pip install supabase")
        return None
    except Exception as e:
        print(f"❌ Error creating Supabase client: {e}")
        return None

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

def add_team(supabase, name: str, description: str = "", telegram_group: str = ""):
    """Add a new team to the database."""
    print(f"🏆 Adding team: {name}")
    
    try:
        team_data = {
            'name': name,
            'description': description,
            'telegram_group': telegram_group,
            'is_active': True
        }
        
        response = supabase.table('teams').insert(team_data).execute()
        
        if response.data:
            team = response.data[0]
            print(f"✅ Successfully added team: {team['name']} (ID: {team['id']})")
            return team['id']
        else:
            print("❌ Failed to add team")
            return None
            
    except Exception as e:
        print(f"❌ Error adding team: {e}")
        return None

def add_bot_mapping(supabase, team_name: str, bot_token: str, chat_id: str, bot_username: str, leadership_chat_id: Optional[str] = None):
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
        
        if leadership_chat_id:
            mapping_data['leadership_chat_id'] = leadership_chat_id
        
        response = supabase.table('team_bots').insert(mapping_data).execute()
        
        if response.data:
            print(f"✅ Successfully mapped {team_name} to {bot_username}")
            print(f"  - Bot Token: {bot_token[:20]}...")
            print(f"  - Main Chat ID: {chat_id}")
            if leadership_chat_id:
                print(f"  - Leadership Chat ID: {leadership_chat_id}")
            return True
        else:
            print("❌ Failed to create bot mapping")
            return False
            
    except Exception as e:
        print(f"❌ Error adding bot mapping: {e}")
        return False

def setup_dual_channel(supabase, team_name: str, leadership_chat_id: str):
    """Setup dual-channel architecture for a team."""
    print(f"🔄 Setting up dual-channel for {team_name}...")
    
    try:
        # Find the team
        teams_response = supabase.table('teams').select('*').eq('name', team_name).execute()
        if not teams_response.data:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_id = teams_response.data[0]['id']
        
        # Update the bot mapping
        response = supabase.table('team_bots').update({
            'leadership_chat_id': leadership_chat_id
        }).eq('team_id', team_id).execute()
        
        if response.data:
            print(f"✅ Successfully updated {team_name} with leadership chat ID: {leadership_chat_id}")
            return True
        else:
            print(f"❌ No bot mapping found for {team_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up dual-channel: {e}")
        return False

def add_team_member(supabase, team_name: str, name: str, role: str, phone: str = "", telegram_username: str = ""):
    """Add a team member."""
    print(f"👤 Adding team member: {name} to {team_name}")
    
    try:
        if not supabase:
            print("❌ Database connection not available")
            return False
            
        # Find the team
        teams_response = supabase.table('teams').select('*').eq('name', team_name).execute()
        if not teams_response.data:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_id = teams_response.data[0]['id']
        
        # Add member
        member_data = {
            'team_id': team_id,
            'name': name,
            'role': role,
            'phone': phone,
            'telegram_username': telegram_username,
            'is_active': True
        }
        
        response = supabase.table('team_members').insert(member_data).execute()
        
        if response.data:
            print(f"✅ Successfully added {name} as {role}")
            return True
        else:
            print("❌ Failed to add team member")
            return False
            
    except Exception as e:
        print(f"❌ Error adding team member: {e}")
        return False

def test_bot_connection(team_name: str):
    """Test bot connection for a team."""
    print(f"🧪 Testing bot connection for {team_name}...")
    
    try:
        supabase = get_supabase_client()
        
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
        print(f"  - Main Chat ID: {bot['chat_id']}")
        print(f"  - Leadership Chat ID: {bot.get('leadership_chat_id', 'Not set')}")
        print(f"  - Active: {bot['is_active']}")
        
        # Test bot connection
        import requests
        url = f"https://api.telegram.org/bot{bot['bot_token']}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_data = bot_info['result']
                print(f"✅ Bot connection successful!")
                print(f"  - Name: {bot_data.get('first_name')}")
                print(f"  - Username: @{bot_data.get('username')}")
                print(f"  - ID: {bot_data.get('id')}")
                return True
            else:
                print(f"❌ Bot connection failed: {bot_info}")
                return False
        else:
            print(f"❌ Bot connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bot connection: {e}")
        return False

def run_sanity_check():
    """Run comprehensive sanity check."""
    print("🔍 Running comprehensive sanity check...")
    
    try:
        result = subprocess.run([sys.executable, 'sanity_check.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sanity check passed!")
            return True
        else:
            print("❌ Sanity check failed!")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running sanity check: {e}")
        return False

def start_bot(team_name: str = None):
    """Start the Telegram bot."""
    print("🤖 Starting Telegram bot...")
    
    try:
        if team_name:
            print(f"📱 Starting bot for team: {team_name}")
            # For now, the bot runner is hardcoded to BP Hatters FC
            # In the future, this could be made configurable
        
        result = subprocess.run([sys.executable, 'run_telegram_bot.py'], 
                              capture_output=False)
        
        if result.returncode == 0:
            print("✅ Bot started successfully!")
            return True
        else:
            print("❌ Bot failed to start!")
            return False
            
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False

def show_status():
    """Show system status."""
    print("📊 KICKAI System Status")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        if not supabase:
            print("❌ Cannot connect to database")
            return False
        
        # Teams
        teams = list_teams(supabase)
        print(f"🏆 Teams: {len(teams)}")
        for team in teams:
            print(f"  - {team['name']} ({'Active' if team['is_active'] else 'Inactive'})")
        
        # Bot mappings
        bots = list_bot_mappings(supabase)
        print(f"\n🤖 Bot Mappings: {len(bots)}")
        for bot in bots:
            team_name = bot.get('teams', {}).get('name', 'Unknown')
            print(f"  - {team_name}: {bot['bot_username']}")
            print(f"    Main: {bot['chat_id']}")
            if bot.get('leadership_chat_id'):
                print(f"    Leadership: {bot['leadership_chat_id']}")
        
        # Check if bot is running
        bot_running = False
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'] and 'run_telegram_bot.py' in ' '.join(proc.info['cmdline']):
                        bot_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            # Fallback: use subprocess to check
            try:
                result = subprocess.run(['pgrep', '-f', 'run_telegram_bot.py'], 
                                      capture_output=True, text=True)
                bot_running = result.returncode == 0
            except:
                bot_running = "Unknown (psutil not available)"
        
        print(f"\n🤖 Bot Process: {'✅ Running' if bot_running else '❌ Not running'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return False

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='KICKAI Comprehensive CLI Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Teams
    teams_parser = subparsers.add_parser('teams', help='Team management')
    teams_parser.add_argument('action', choices=['list', 'add'], help='Action to perform')
    teams_parser.add_argument('--name', help='Team name for add command')
    teams_parser.add_argument('--description', help='Team description for add command')
    teams_parser.add_argument('--telegram-group', help='Telegram group for add command')
    
    # Bots
    bots_parser = subparsers.add_parser('bots', help='Bot management')
    bots_parser.add_argument('action', choices=['list', 'add', 'test'], help='Action to perform')
    bots_parser.add_argument('--team', help='Team name')
    bots_parser.add_argument('--token', help='Bot token for add command')
    bots_parser.add_argument('--chat-id', help='Main chat ID for add command')
    bots_parser.add_argument('--username', help='Bot username for add command')
    bots_parser.add_argument('--leadership-chat-id', help='Leadership chat ID for add command')
    
    # Dual-channel
    dual_parser = subparsers.add_parser('dual-channel', help='Dual-channel setup')
    dual_parser.add_argument('--team', required=True, help='Team name')
    dual_parser.add_argument('--leadership-chat-id', required=True, help='Leadership chat ID')
    
    # Members
    members_parser = subparsers.add_parser('members', help='Team member management')
    members_parser.add_argument('action', choices=['add'], help='Action to perform')
    members_parser.add_argument('--team', required=True, help='Team name')
    members_parser.add_argument('--name', required=True, help='Member name')
    members_parser.add_argument('--role', required=True, help='Member role')
    members_parser.add_argument('--phone', help='Phone number')
    members_parser.add_argument('--telegram-username', help='Telegram username')
    
    # System
    system_parser = subparsers.add_parser('system', help='System management')
    system_parser.add_argument('action', choices=['status', 'sanity-check', 'start-bot'], help='Action to perform')
    system_parser.add_argument('--team', help='Team name for start-bot command')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        supabase = get_supabase_client()
        if not supabase and args.command not in ['system']:
            print("❌ Cannot connect to database")
            sys.exit(1)
        
        if args.command == 'teams':
            if args.action == 'list':
                print("📋 Teams in Database:")
                teams = list_teams(supabase)
                for team in teams:
                    print(f"  - {team['name']} (ID: {team['id']})")
                    
            elif args.action == 'add':
                if not args.name:
                    print("❌ Team name required: --name")
                    sys.exit(1)
                
                add_team(supabase, args.name, args.description or "", args.telegram_group or "")
        
        elif args.command == 'bots':
            if args.action == 'list':
                print("🤖 Bot Mappings:")
                mappings = list_bot_mappings(supabase)
                if mappings:
                    for mapping in mappings:
                        team_name = mapping.get('teams', {}).get('name', 'Unknown')
                        print(f"  - {team_name} → {mapping['bot_username']}")
                        print(f"    Main Chat: {mapping['chat_id']}")
                        print(f"    Leadership Chat: {mapping.get('leadership_chat_id', 'Not set')}")
                        print(f"    Active: {mapping['is_active']}")
                else:
                    print("  No bot mappings found")
                    
            elif args.action == 'add':
                if not all([args.team, args.token, args.chat_id, args.username]):
                    print("❌ All arguments required: --team, --token, --chat-id, --username")
                    sys.exit(1)
                
                add_bot_mapping(supabase, args.team, args.token, args.chat_id, args.username, args.leadership_chat_id)
                
            elif args.action == 'test':
                if not args.team:
                    print("❌ Team name required: --team")
                    sys.exit(1)
                
                test_bot_connection(args.team)
        
        elif args.command == 'dual-channel':
            setup_dual_channel(supabase, args.team, args.leadership_chat_id)
        
        elif args.command == 'members':
            if args.action == 'add':
                add_team_member(supabase, args.team, args.name, args.role, args.phone or "", args.telegram_username or "")
        
        elif args.command == 'system':
            if args.action == 'status':
                show_status()
            elif args.action == 'sanity-check':
                run_sanity_check()
            elif args.action == 'start-bot':
                start_bot(args.team)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 