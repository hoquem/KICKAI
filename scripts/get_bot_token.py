#!/usr/bin/env python3
"""
Simple script to get bot token from Firestore teams collection.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_env_file()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import firebase_admin
from firebase_admin import credentials, firestore
from loguru import logger

async def get_team_id_from_firestore() -> str:
    """
    Get the first available team_id from Firestore.
    This ensures we use a real team from the database instead of hardcoded values.
    """
    try:
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
            if firebase_creds_file:
                cred = credentials.Certificate(firebase_creds_file)
                firebase_admin.initialize_app(cred)
            else:
                raise RuntimeError("No Firebase credentials found.")
        
        db = firestore.client()
        
        # Get all teams from Firestore
        teams_ref = db.collection('kickai_teams')
        teams = teams_ref.stream()
        
        teams_list = list(teams)
        if not teams_list:
            logger.warning("No teams found in Firestore, using fallback team_id")
            return "fallback_team"
        
        # Use the first available team
        team_id = teams_list[0].id
        logger.info(f"Using team_id from Firestore: {team_id}")
        return team_id
        
    except Exception as e:
        logger.error(f"Failed to get team_id from Firestore: {e}")
        logger.warning("Using fallback team_id due to error")
        return "fallback_team"


async def get_bot_config():
    """Get bot configuration from Firestore teams collection."""
    try:
        # Initialize Firebase
        try:
            firebase_admin.get_app()
            logger.info("✅ Using existing Firebase app")
        except ValueError:
            logger.info("🔄 Initializing new Firebase app...")
            
            # Get credentials from environment
            firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
            if firebase_creds_file:
                cred = credentials.Certificate(firebase_creds_file)
                firebase_admin.initialize_app(cred)
                logger.info(f"✅ Firebase initialized with credentials from file: {firebase_creds_file}")
            else:
                raise RuntimeError("No Firebase credentials found.")
        
        db = firestore.client()
        
        # Get team ID from Firestore or environment
        team_id = await get_team_id_from_firestore()
        if team_id == "fallback_team":
            # Fallback to environment variable
            team_id = os.getenv('TEAM_ID', 'fallback_team')
        
        # Query team document
        team_doc = db.collection('kickai_teams').document(team_id).get()
        
        if team_doc.exists:
            team_data = team_doc.to_dict()
            
            # Bot configuration is now in explicit fields only
            bot_token = team_data.get('bot_token')
            main_chat_id = team_data.get('main_chat_id')
            leadership_chat_id = team_data.get('leadership_chat_id')
            bot_username = team_data.get('bot_id')
            
            logger.info(f"Found team {team_id}:")
            logger.info(f"  Team Name: {team_data.get('name', 'N/A')}")
            logger.info(f"  Bot Token: {bot_token[:20]}..." if bot_token else "  Bot Token: Not found")
            logger.info(f"  Main Chat ID: {main_chat_id or 'Not found'}")
            logger.info(f"  Leadership Chat ID: {leadership_chat_id or 'Not found'}")
            logger.info(f"  Bot Username: {bot_username or 'Not found'}")
            
            return {
                'team_id': team_id,
                'team_name': team_data.get('name', 'N/A'),
                'bot_token': bot_token,
                'main_chat_id': main_chat_id,
                'leadership_chat_id': leadership_chat_id,
                'bot_username': bot_username,
                'settings': team_data.get('settings', {})
            }
        else:
            logger.warning(f"No team document found for team {team_id}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Error getting bot config: {e}")
        return None


async def main():
    """Main function."""
    try:
        logger.info("🔍 Getting bot configuration from Firestore teams collection...")
        config = await get_bot_config()
        
        if config:
            print("\n" + "="*50)
            print("BOT CONFIGURATION FOUND:")
            print("="*50)
            print(f"Team ID: {config.get('team_id', 'N/A')}")
            print(f"Team Name: {config.get('team_name', 'N/A')}")
            print(f"Bot Token: {config.get('bot_token', 'N/A')[:20]}..." if config.get('bot_token') else "Bot Token: Not found")
            print(f"Bot Username: {config.get('bot_username', 'N/A')}")
            print(f"Main Chat ID: {config.get('main_chat_id', 'N/A')}")
            print(f"Leadership Chat ID: {config.get('leadership_chat_id', 'N/A')}")
            print("="*50)
            
            print("✅ Bot configuration retrieved from Firestore")
            print("📝 Note: Bot configuration is now stored in Firestore teams collection")
            print("📝 Use team explicit fields (bot_token, main_chat_id, leadership_chat_id) for bot configuration")
            return config
        else:
            print("\n" + "="*50)
            print("ERROR: No bot configuration found!")
            print("="*50)
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to get bot configuration: {e}")
        return None


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, format="{time} | {level} | {message}", level="INFO")
    
    # Run the script
    result = asyncio.run(main())
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1) 