#!/usr/bin/env python3
"""
Standalone script to add leadership chat members as team admins in Firestore.

This script:
1. Connects to Telegram using the bot token
2. Gets the list of administrators in the leadership chat
3. Adds each admin as a team member in Firestore with admin role
4. Provides a summary of the operation

Usage:
    python scripts/add_leadership_admins_standalone.py
"""

import asyncio
import os
import sys
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
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

from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
import firebase_admin
from firebase_admin import credentials, firestore

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def get_team_id_from_firestore() -> str:
    """
    Get the first available team_id from Firestore.
    This ensures we use a real team from the database instead of hardcoded values.
    """
    try:
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred = credentials.Certificate('credentials/firebase_credentials_testing.json')
            firebase_admin.initialize_app(cred)
        
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


@dataclass
class ChatMember:
    """Represents a chat member with admin status."""
    user_id: int
    username: str
    first_name: str
    last_name: str
    is_admin: bool
    status: str


class LeadershipAdminAdder:
    """Handles adding leadership chat admins to Firestore."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        
        # Initialize Firebase first to get bot configuration
        self._initialize_firebase()
        
        # Get bot configuration from Firestore
        self._get_bot_config()
        
        if not self.bot_token:
            raise ValueError("Bot token not found in team settings")
        if not self.leadership_chat_id:
            raise ValueError("Leadership chat ID not found in team settings")
        
        self.bot = Bot(token=self.bot_token)
        
        logger.info(f"Initialized LeadershipAdminAdder for team: {team_id}")
        logger.info(f"Leadership chat ID: {self.leadership_chat_id}")
    
    def _get_bot_config(self):
        """Get bot configuration from team settings in Firestore."""
        try:
            # Query team document
            team_doc = self.db.collection('kickai_teams').document(self.team_id).get()
            
            if team_doc.exists:
                team_data = team_doc.to_dict()
                
                # Bot configuration is now in explicit fields
                self.bot_token = team_data.get('bot_token')
                self.leadership_chat_id = team_data.get('leadership_chat_id')
                self.main_chat_id = team_data.get('main_chat_id')
                
                logger.info(f"Retrieved bot config from team {self.team_id}:")
                logger.info(f"  Bot Token: {self.bot_token[:20]}..." if self.bot_token else "  Bot Token: Not found")
                logger.info(f"  Leadership Chat ID: {self.leadership_chat_id}")
            else:
                raise ValueError(f"No team document found for team {self.team_id}")
                
        except Exception as e:
            logger.error(f"Error getting bot config: {e}")
            raise
    
    def _initialize_firebase(self):
        """Initialize Firebase client."""
        try:
            # Check if Firebase app is already initialized
            try:
                firebase_admin.get_app()
                logger.info("✅ Using existing Firebase app")
            except ValueError:
                logger.info("🔄 Initializing new Firebase app...")
                
                # Get credentials from environment
                firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
                if firebase_creds_json:
                    creds_dict = json.loads(firebase_creds_json)
                    cred = credentials.Certificate(creds_dict)
                    firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase initialized with credentials from environment")
                else:
                    firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
                    if firebase_creds_file:
                        cred = credentials.Certificate(firebase_creds_file)
                        firebase_admin.initialize_app(cred)
                        logger.info(f"✅ Firebase initialized with credentials from file: {firebase_creds_file}")
                    else:
                        raise RuntimeError("No Firebase credentials found. Please set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE environment variables.")
            
            self.db = firestore.client()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            raise
    
    async def get_chat_administrators(self) -> List[ChatMember]:
        """Get all administrators from the leadership chat."""
        try:
            logger.info("Fetching chat administrators...")
            admins = await self.bot.get_chat_administrators(chat_id=self.leadership_chat_id)
            
            chat_members = []
            for admin in admins:
                member = ChatMember(
                    user_id=admin.user.id,
                    username=admin.user.username or "",
                    first_name=admin.user.first_name or "",
                    last_name=admin.user.last_name or "",
                    is_admin=admin.status in ['creator', 'administrator'],
                    status=admin.status
                )
                chat_members.append(member)
                logger.info(f"Found admin: {member.first_name} {member.last_name} (@{member.username}) - Status: {member.status}")
            
            logger.info(f"Found {len(chat_members)} chat members")
            return chat_members
            
        except TelegramError as e:
            logger.error(f"Error fetching chat administrators: {e}")
            raise
    
    async def check_existing_team_members(self) -> List[Dict[str, Any]]:
        """Check for existing team members in Firestore."""
        try:
            collection_name = f"kickai_{self.team_id}_team_members"
            existing_members = []
            
            # Query existing team members
            docs = self.db.collection(collection_name).where("team_id", "==", self.team_id).stream()
            for doc in docs:
                member_data = doc.to_dict()
                member_data['id'] = doc.id
                existing_members.append(member_data)
            
            logger.info(f"Found {len(existing_members)} existing team members")
            return existing_members
            
        except Exception as e:
            logger.error(f"Error checking existing team members: {e}")
            return []
    
    async def add_team_member(self, member: ChatMember) -> bool:
        """Add a team member to Firestore."""
        try:
            collection_name = f"kickai_{self.team_id}_team_members"
            
            # Check if member already exists
            existing_docs = self.db.collection(collection_name).where("telegram_id", "==", member.user_id).stream()
            existing_members = list(existing_docs)
            
            if existing_members:
                logger.info(f"Team member already exists: {member.first_name} {member.last_name}")
                return True
            
            # Create new team member document
            member_data = {
                "team_id": self.team_id,
                "telegram_id": member.user_id,
                "username": member.username,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "full_name": f"{member.first_name} {member.last_name}".strip(),
                "role": "admin" if member.is_admin else "member",
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "leadership_chat_admin"
            }
            
            # Add to Firestore
            doc_ref = self.db.collection(collection_name).add(member_data)
            logger.info(f"✅ Added team member: {member.first_name} {member.last_name} (ID: {doc_ref[1].id})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding team member {member.first_name}: {e}")
            return False
    
    async def run(self) -> Dict[str, Any]:
        """Run the complete process."""
        try:
            logger.info("🚀 Starting leadership admin addition process...")
            
            # Get chat administrators
            chat_members = await self.get_chat_administrators()
            
            # Check existing team members
            existing_members = await self.check_existing_team_members()
            
            # Add new team members
            added_count = 0
            failed_count = 0
            
            for member in chat_members:
                if member.is_admin:  # Only add admins
                    success = await self.add_team_member(member)
                    if success:
                        added_count += 1
                    else:
                        failed_count += 1
            
            # Summary
            summary = {
                "team_id": self.team_id,
                "total_chat_members": len(chat_members),
                "admin_members": len([m for m in chat_members if m.is_admin]),
                "existing_team_members": len(existing_members),
                "added_team_members": added_count,
                "failed_additions": failed_count,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("📊 Summary:")
            logger.info(f"   Team ID: {summary['team_id']}")
            logger.info(f"   Total Chat Members: {summary['total_chat_members']}")
            logger.info(f"   Admin Members: {summary['admin_members']}")
            logger.info(f"   Existing Team Members: {summary['existing_team_members']}")
            logger.info(f"   Added Team Members: {summary['added_team_members']}")
            logger.info(f"   Failed Additions: {summary['failed_additions']}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error in leadership admin addition process: {e}")
            raise


async def main():
    """Main function."""
    try:
        # Get team ID from Firestore or environment
        team_id = await get_team_id_from_firestore()
        if team_id == "fallback_team":
            # Fallback to environment variable
            team_id = os.getenv('TELEGRAM_TEAM_ID', 'fallback_team')
        
        logger.info(f"🎯 Starting Leadership Admin Addition for Team: {team_id}")
        
        # Create adder instance
        adder = LeadershipAdminAdder(team_id)
        
        # Run the process
        summary = await adder.run()
        
        logger.info("✅ Leadership admin addition process completed successfully!")
        return summary
        
    except Exception as e:
        logger.error(f"❌ Failed to complete leadership admin addition: {e}")
        return None


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, format="{time} | {level} | {message}", level="INFO")
    
    # Run the script
    result = asyncio.run(main())
    
    if result:
        print("\n" + "="*50)
        print("SUCCESS: Leadership admin addition completed!")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("ERROR: Leadership admin addition failed!")
        print("="*50)
        sys.exit(1) 