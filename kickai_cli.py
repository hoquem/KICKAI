#!/usr/bin/env python3
"""
KICKAI CLI Tool
Command-line interface for managing teams, bots, and system configuration.
"""

import os
import argparse
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from firebase_admin import firestore
from src.tools.firebase_tools import get_firebase_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_teams(firebase) -> List[Dict]:
    """List all active teams."""
    try:
        teams_ref = firebase.collection('teams')
        query = teams_ref.where('is_active', '==', True)
        response = query.get()
        
        teams = []
        for doc in response:
            team_data = doc.to_dict()
            team_data['id'] = doc.id
            teams.append(team_data)
        
        return teams
    except Exception as e:
        logger.error(f"Failed to list teams: {e}")
        return []

def list_bot_mappings(firebase) -> List[Dict]:
    """List all bot mappings."""
    try:
        bots_ref = firebase.collection('team_bots')
        response = bots_ref.get()
        
        mappings = []
        for doc in response:
            mapping_data = doc.to_dict()
            mapping_data['id'] = doc.id
            
            # Get team name
            team_ref = firebase.collection('teams').document(mapping_data['team_id'])
            team_doc = team_ref.get()
            if team_doc.exists:
                team_data = team_doc.to_dict()
                mapping_data['team_name'] = team_data.get('name', 'Unknown')
            else:
                mapping_data['team_name'] = 'Unknown'
            
            mappings.append(mapping_data)
        
        return mappings
    except Exception as e:
        logger.error(f"Failed to list bot mappings: {e}")
        return []

def add_team(firebase, name: str, description: str = "", telegram_group: str = ""):
    """Add a new team."""
    try:
        team_data = {
            'name': name,
            'description': description,
            'telegram_group': telegram_group,
            'created_at': datetime.now(),
            'is_active': True
        }
        
        team_ref = firebase.collection('teams').document()
        team_ref.set(team_data)
        team_id = team_ref.id
        
        print(f"✅ Team '{name}' created with ID: {team_id}")
        return team_id
        
    except Exception as e:
        print(f"❌ Failed to create team: {e}")
        return None

def add_bot_mapping(firebase, team_name: str, bot_token: str, chat_id: str, bot_username: str, leadership_chat_id: Optional[str] = None):
    """Add a bot mapping for a team."""
    try:
        # Find team by name
        teams_ref = firebase.collection('teams')
        team_query = teams_ref.where('name', '==', team_name)
        team_response = team_query.get()
        
        if not team_response:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_doc = team_response[0]
        team_id = team_doc.id
        
        # Check if mapping already exists
        bots_ref = firebase.collection('team_bots')
        existing_query = bots_ref.where('team_id', '==', team_id)
        existing_response = existing_query.get()
        
        if existing_response:
            # Update existing mapping
            existing_doc = existing_response[0]
            existing_ref = firebase.collection('team_bots').document(existing_doc.id)
            existing_ref.delete()
            print(f"Removed existing bot mapping for team '{team_name}'")
        
        # Create new mapping
        mapping_data = {
            'team_id': team_id,
            'bot_token': bot_token,
            'chat_id': chat_id,
            'bot_username': bot_username,
            'leadership_chat_id': leadership_chat_id,
            'created_at': datetime.now(),
            'is_active': True
        }
        
        new_mapping_ref = firebase.collection('team_bots').document()
        new_mapping_ref.set(mapping_data)
        
        print(f"✅ Bot mapping added for team '{team_name}'")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add bot mapping: {e}")
        return False

def setup_dual_channel(firebase, team_name: str, leadership_chat_id: str):
    """Set up dual channel configuration for a team."""
    try:
        # Find team by name
        teams_ref = firebase.collection('teams')
        team_query = teams_ref.where('name', '==', team_name)
        team_response = team_query.get()
        
        if not team_response:
            print(f"❌ Team '{team_name}' not found")
            return False
        
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
            
            print(f"✅ Dual channel setup completed for team '{team_name}'")
            print(f"   Main chat: {bot_doc.to_dict().get('chat_id', 'N/A')}")
            print(f"   Leadership chat: {leadership_chat_id}")
            return True
        else:
            print(f"❌ No bot mapping found for team '{team_name}'")
            return False
            
    except Exception as e:
        print(f"❌ Failed to setup dual channel: {e}")
        return False

def add_team_member(firebase, team_name: str, member_name: str, role: str, phone: str = "", telegram_username: str = ""):
    """Add a member to a team."""
    try:
        if not firebase:
            print("❌ Firebase client not available")
            return False
        
        # Find team by name
        teams_ref = firebase.collection('teams')
        team_query = teams_ref.where('name', '==', team_name)
        team_response = team_query.get()
        
        if not team_response:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_doc = team_response[0]
        team_id = team_doc.id
        
        # Check if member already exists
        members_ref = firebase.collection('team_members')
        existing_query = members_ref.where('team_id', '==', team_id).where('name', '==', member_name)
        existing_response = existing_query.get()
        
        if existing_response:
            print(f"⚠️ Member '{member_name}' already exists in team '{team_name}'")
            return False
        
        # Add new member
        member_data = {
            'team_id': team_id,
            'name': member_name,
            'role': role,
            'phone_number': phone,
            'telegram_username': telegram_username,
            'joined_at': datetime.now(),
            'is_active': True
        }
        
        member_ref = firebase.collection('team_members').document()
        member_ref.set(member_data)
        
        print(f"✅ Member '{member_name}' added to team '{team_name}' as {role}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add team member: {e}")
        return False

def test_team_setup(firebase, team_name: str):
    """Test team setup and configuration."""
    try:
        if not firebase:
            print("❌ Firebase client not available")
            return False
        
        # Check team exists
        teams_ref = firebase.collection('teams')
        team_query = teams_ref.where('name', '==', team_name)
        team_response = team_query.get()
        
        if not team_response:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        team_doc = team_response[0]
        team_id = team_doc.id
        team_data = team_doc.to_dict()
        
        print(f"✅ Team found: {team_name} (ID: {team_id})")
        print(f"   Description: {team_data.get('description', 'No description')}")
        print(f"   Telegram Group: {team_data.get('telegram_group', 'Not set')}")
        
        # Check bot mapping
        bots_ref = firebase.collection('team_bots')
        bot_query = bots_ref.where('team_id', '==', team_id)
        bot_response = bot_query.get()
        
        if bot_response:
            bot_data = bot_response[0].to_dict()
            print(f"✅ Bot mapping found:")
            print(f"   Bot Username: @{bot_data.get('bot_username', 'N/A')}")
            print(f"   Main Chat ID: {bot_data.get('chat_id', 'N/A')}")
            print(f"   Leadership Chat ID: {bot_data.get('leadership_chat_id', 'Not set')}")
        else:
            print("❌ No bot mapping found")
        
        # Check members
        members_ref = firebase.collection('team_members')
        members_query = members_ref.where('team_id', '==', team_id).where('is_active', '==', True)
        members_response = members_query.get()
        
        member_count = len(list(members_response))
        print(f"✅ Team members: {member_count} active members")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test team setup: {e}")
        return False

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='KICKAI CLI - Team and Bot Management')
    parser.add_argument('command', choices=['teams', 'bots', 'add-team', 'add-bot', 'setup-dual', 'add-member', 'test', 'system'],
                       help='Command to execute')
    
    # Team commands
    parser.add_argument('--name', help='Team name')
    parser.add_argument('--description', help='Team description')
    parser.add_argument('--telegram-group', help='Telegram group ID')
    
    # Bot commands
    parser.add_argument('--token', help='Bot token')
    parser.add_argument('--chat-id', help='Chat ID')
    parser.add_argument('--username', help='Bot username')
    parser.add_argument('--leadership-chat-id', help='Leadership chat ID')
    
    # Member commands
    parser.add_argument('--team', help='Team name (for member operations)')
    parser.add_argument('--member-name', help='Member name')
    parser.add_argument('--role', help='Member role')
    parser.add_argument('--phone', help='Phone number')
    parser.add_argument('--telegram-username', help='Telegram username')
    
    args = parser.parse_args()
    
    # Initialize Firebase client
    try:
        firebase = get_firebase_client()
    except Exception as e:
        print(f"❌ Error creating Firebase client: {e}")
        firebase = None
    
    if not firebase and args.command not in ['system']:
        print("❌ Firebase client not available")
        return
    
    if args.command == 'teams':
        teams = list_teams(firebase)
        if teams:
            print("\n📋 Teams:")
            for team in teams:
                print(f"• {team['name']} (ID: {team['id']})")
                print(f"  Description: {team.get('description', 'No description')}")
        else:
            print("No teams found")
    
    elif args.command == 'bots':
        bots = list_bot_mappings(firebase)
        if bots:
            print("\n🤖 Bot Mappings:")
            for bot in bots:
                print(f"• {bot['team_name']} -> @{bot.get('bot_username', 'N/A')}")
                print(f"  Chat ID: {bot.get('chat_id', 'N/A')}")
                print(f"  Leadership Chat: {bot.get('leadership_chat_id', 'Not set')}")
        else:
            print("No bot mappings found")
    
    elif args.command == 'add-team':
        if not args.name:
            print("❌ --name is required for add-team command")
            return
        
        add_team(firebase, args.name, args.description or "", args.telegram_group or "")
    
    elif args.command == 'add-bot':
        if not all([args.name, args.token, args.chat_id, args.username]):
            print("❌ --name, --token, --chat-id, and --username are required for add-bot command")
            return
        
        add_bot_mapping(firebase, args.name, args.token, args.chat_id, args.username, args.leadership_chat_id)
    
    elif args.command == 'setup-dual':
        if not all([args.name, args.leadership_chat_id]):
            print("❌ --name and --leadership-chat-id are required for setup-dual command")
            return
        
        setup_dual_channel(firebase, args.name, args.leadership_chat_id)
    
    elif args.command == 'add-member':
        if not all([args.team, args.member_name, args.role]):
            print("❌ --team, --member-name, and --role are required for add-member command")
            return
        
        add_team_member(firebase, args.team, args.member_name, args.role, args.phone or "", args.telegram_username or "")
    
    elif args.command == 'test':
        if not args.name:
            print("❌ --name is required for test command")
            return
        
        test_team_setup(firebase, args.name)
    
    elif args.command == 'system':
        print("🔧 KICKAI System Information")
        print(f"Python version: {os.sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        
        # Check Firebase connection
        if firebase:
            print("✅ Firebase connection: Available")
        else:
            print("❌ Firebase connection: Not available")

if __name__ == "__main__":
    main() 