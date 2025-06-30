#!/usr/bin/env python3
"""
Team Bot Management Script
Manages the mapping between teams and their Telegram bots.
"""

import os
import argparse
import logging
from typing import List, Dict
from dotenv import load_dotenv
from firebase_admin import firestore
from src.tools.firebase_tools import get_firebase_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_firebase_client():
    """Get Firebase client with proper error handling."""
    try:
        return get_firebase_client()
    except Exception as e:
        logger.error(f"Failed to get Firebase client: {e}")
        raise

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

def add_bot_mapping(firebase, team_name: str, bot_token: str, chat_id: str, bot_username: str):
    """Add a new bot mapping for a team."""
    try:
        # Find team by name
        teams_ref = firebase.collection('teams')
        team_query = teams_ref.where('name', '==', team_name)
        team_response = team_query.get()
        
        if not team_response:
            logger.error(f"Team '{team_name}' not found")
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
            logger.info(f"Removed existing bot mapping for team '{team_name}'")
        
        # Create new mapping
        mapping_data = {
            'team_id': team_id,
            'bot_token': bot_token,
            'chat_id': chat_id,
            'bot_username': bot_username,
            'created_at': firestore.SERVER_TIMESTAMP,
            'is_active': True
        }
        
        new_mapping_ref = firebase.collection('team_bots').document()
        new_mapping_ref.set(mapping_data)
        
        logger.info(f"Successfully added bot mapping for team '{team_name}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add bot mapping: {e}")
        return False

def remove_bot_mapping(firebase, team_name: str):
    """Remove bot mapping for a team."""
    try:
        # Find team by name
        teams_ref = firebase.collection('teams')
        team_query = teams_ref.where('name', '==', team_name)
        team_response = team_query.get()
        
        if not team_response:
            logger.error(f"Team '{team_name}' not found")
            return False
        
        team_doc = team_response[0]
        team_id = team_doc.id
        
        # Find and remove bot mapping
        bots_ref = firebase.collection('team_bots')
        mapping_query = bots_ref.where('team_id', '==', team_id)
        mapping_response = mapping_query.get()
        
        if not mapping_response:
            logger.error(f"No bot mapping found for team '{team_name}'")
            return False
        
        # Remove mapping
        mapping_doc = mapping_response[0]
        mapping_ref = firebase.collection('team_bots').document(mapping_doc.id)
        mapping_ref.delete()
        
        logger.info(f"Successfully removed bot mapping for team '{team_name}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to remove bot mapping: {e}")
        return False

def test_bot_mapping(firebase, team_name: str):
    """Test bot mapping for a team."""
    try:
        # Find team by name
        teams_ref = firebase.collection('teams')
        team_query = teams_ref.where('name', '==', team_name)
        team_response = team_query.get()
        
        if not team_response:
            logger.error(f"Team '{team_name}' not found")
            return False
        
        team_doc = team_response[0]
        team_id = team_doc.id
        
        # Find bot mapping
        bots_ref = firebase.collection('team_bots')
        bot_query = bots_ref.where('team_id', '==', team_id)
        bot_response = bot_query.get()
        
        if not bot_response:
            logger.error(f"No bot mapping found for team '{team_name}'")
            return False
        
        bot_doc = bot_response[0]
        bot_data = bot_doc.to_dict()
        
        logger.info(f"Bot mapping for team '{team_name}':")
        logger.info(f"  Bot Username: {bot_data.get('bot_username', 'N/A')}")
        logger.info(f"  Chat ID: {bot_data.get('chat_id', 'N/A')}")
        logger.info(f"  Active: {bot_data.get('is_active', False)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to test bot mapping: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Manage team bot mappings')
    parser.add_argument('action', choices=['list', 'add', 'remove', 'test'],
                       help='Action to perform')
    parser.add_argument('--team', help='Team name')
    parser.add_argument('--token', help='Bot token')
    parser.add_argument('--chat-id', help='Chat ID')
    parser.add_argument('--username', help='Bot username')
    
    args = parser.parse_args()
    
    try:
        firebase = get_firebase_client()
        
        if args.action == 'list':
            print("\n=== Teams ===")
            teams = list_teams(firebase)
            for team in teams:
                print(f"• {team['name']} (ID: {team['id']})")
            
            print("\n=== Bot Mappings ===")
            mappings = list_bot_mappings(firebase)
            for mapping in mappings:
                print(f"• {mapping['team_name']} -> @{mapping.get('bot_username', 'N/A')}")
        
        elif args.action == 'add':
            if not all([args.team, args.token, args.chat_id, args.username]):
                print("Error: --team, --token, --chat-id, and --username are required for add action")
                return
            
            success = add_bot_mapping(firebase, args.team, args.token, args.chat_id, args.username)
            if success:
                print(f"Successfully added bot mapping for team '{args.team}'")
            else:
                print(f"Failed to add bot mapping for team '{args.team}'")
        
        elif args.action == 'remove':
            if not args.team:
                print("Error: --team is required for remove action")
                return
            
            success = remove_bot_mapping(firebase, args.team)
            if success:
                print(f"Successfully removed bot mapping for team '{args.team}'")
            else:
                print(f"Failed to remove bot mapping for team '{args.team}'")
        
        elif args.action == 'test':
            if not args.team:
                print("Error: --team is required for test action")
                return
            
            success = test_bot_mapping(firebase, args.team)
            if not success:
                print(f"Failed to test bot mapping for team '{args.team}'")
    
    except Exception as e:
        logger.error(f"Script failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 