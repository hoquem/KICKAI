#!/usr/bin/env python3
"""
Script to add leadership chat members as team admins in Firestore.

This script:
1. Connects to Telegram using the bot token from Firestore
2. Gets the list of administrators in the leadership chat
3. Adds each admin as a team member in Firestore with admin role
4. Uses the proper domain model and follows established patterns

Usage:
    python scripts/add_leadership_admins.py [team_id]
"""

import asyncio
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram import Bot
from telegram.error import TelegramError
from loguru import logger

from kickai.database.firebase_client import get_firebase_client
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.utils.user_id_generator import generate_user_id


class LeadershipAdminAdder:
    """Handles adding leadership chat admins to Firestore."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.firebase_client = get_firebase_client()
        
        # Bot configuration
        self.bot_token = None
        self.leadership_chat_id = None
        self.bot = None
        
        logger.info(f"Initialized LeadershipAdminAdder for team: {team_id}")
    
    async def _load_bot_config(self):
        """Load bot configuration from Firestore team document."""
        try:
            # Get team document from Firestore
            team_doc = await self.firebase_client.get_document(
                collection='kickai_teams',
                document_id=self.team_id
            )
            
            if not team_doc:
                raise ValueError(f"Team {self.team_id} not found in Firestore")
            
            self.bot_token = team_doc.get('bot_token')
            self.leadership_chat_id = team_doc.get('leadership_chat_id')
            
            if not self.bot_token:
                raise ValueError(f"Bot token not found for team {self.team_id}")
            if not self.leadership_chat_id:
                raise ValueError(f"Leadership chat ID not found for team {self.team_id}")
            
            self.bot = Bot(token=self.bot_token)
            
            logger.info(f"Bot configuration loaded for team: {self.team_id}")
            logger.info(f"Leadership chat ID: {self.leadership_chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to load bot configuration: {e}")
            raise
    
    async def get_chat_administrators(self) -> List[Dict[str, Any]]:
        """Get all administrators from the leadership chat."""
        try:
            logger.info("Fetching chat administrators...")
            admins = await self.bot.get_chat_administrators(chat_id=self.leadership_chat_id)
            
            chat_members = []
            for admin in admins:
                # Skip the bot itself
                if admin.user.is_bot:
                    continue
                    
                member_data = {
                    'user_id': admin.user.id,
                    'username': admin.user.username or "",
                    'first_name': admin.user.first_name or "",
                    'last_name': admin.user.last_name or "",
                    'is_admin': admin.status in ['creator', 'administrator'],
                    'status': admin.status
                }
                chat_members.append(member_data)
                logger.info(f"Found admin: {member_data['first_name']} {member_data['last_name']} (@{member_data['username']}) - Status: {member_data['status']}")
            
            logger.info(f"Found {len(chat_members)} chat members (excluding bot)")
            return chat_members
            
        except TelegramError as e:
            logger.error(f"Error fetching chat administrators: {e}")
            raise
    
    async def check_existing_team_members(self) -> List[Dict[str, Any]]:
        """Check for existing team members in Firestore."""
        try:
            collection_name = f"kickai_{self.team_id}_team_members"
            existing_members = await self.firebase_client.query_documents(
                collection=collection_name,
                filters=[{"field": "team_id", "operator": "==", "value": self.team_id}]
            )
            
            logger.info(f"Found {len(existing_members)} existing team members")
            return existing_members
            
        except Exception as e:
            logger.error(f"Error checking existing team members: {e}")
            raise
    
    async def add_team_member(self, member_data: Dict[str, Any]) -> bool:
        """Add a chat member as a team member in Firestore using the domain model."""
        try:
            # Create TeamMember entity using the domain model
            team_member = TeamMember.create_from_telegram(
                team_id=self.team_id,
                telegram_id=member_data['user_id'],
                first_name=member_data['first_name'],
                last_name=member_data['last_name'],
                username=member_data['username'],
                is_admin=member_data['is_admin']
            )
            
            # Determine role based on status
            if member_data['status'] == 'creator':
                team_member.role = "Club Administrator"
            elif member_data['status'] == 'administrator':
                team_member.role = "Team Manager"
            else:
                team_member.role = "Team Member"
            
            # Set source
            team_member.source = "leadership_chat_admin_script"
            
            # Convert to dictionary for storage
            team_member_dict = team_member.to_dict()
            
            # Add to Firestore
            collection_name = f"kickai_{self.team_id}_team_members"
            doc_id = team_member.user_id  # Use the generated user_id as document ID
            
            await self.firebase_client.create_document(
                collection=collection_name,
                data=team_member_dict,
                document_id=doc_id
            )
            
            logger.info(f"✅ Added team member: {team_member.get_display_name()} as {team_member.role}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding team member {member_data.get('first_name', 'Unknown')}: {e}")
            return False
    
    async def run(self) -> Dict[str, Any]:
        """Main execution method."""
        logger.info("🚀 Starting leadership admin addition process...")
        
        try:
            # Load bot configuration from Firestore
            await self._load_bot_config()
            
            # Get chat administrators
            chat_members = await self.get_chat_administrators()
            
            # Check existing team members
            existing_members = await self.check_existing_team_members()
            existing_telegram_ids = {member.get('telegram_id') for member in existing_members}
            
            # Filter out existing members
            new_members = [member for member in chat_members if str(member['user_id']) not in existing_telegram_ids]
            
            if not new_members:
                logger.info("ℹ️ No new members to add - all chat admins are already team members")
                return {
                    "success": True,
                    "total_chat_members": len(chat_members),
                    "existing_team_members": len(existing_members),
                    "new_members_added": 0,
                    "errors": []
                }
            
            logger.info(f"📝 Found {len(new_members)} new members to add")
            
            # Add new members
            added_count = 0
            errors = []
            
            for member in new_members:
                success = await self.add_team_member(member)
                if success:
                    added_count += 1
                else:
                    errors.append(f"Failed to add {member.get('first_name', 'Unknown')} {member.get('last_name', '')}")
            
            # Summary
            logger.info("📊 Summary:")
            logger.info(f"   Total chat members: {len(chat_members)}")
            logger.info(f"   Existing team members: {len(existing_members)}")
            logger.info(f"   New members added: {added_count}")
            logger.info(f"   Errors: {len(errors)}")
            
            if errors:
                logger.warning("⚠️ Some members could not be added:")
                for error in errors:
                    logger.warning(f"   - {error}")
            
            return {
                "success": len(errors) == 0,
                "total_chat_members": len(chat_members),
                "existing_team_members": len(existing_members),
                "new_members_added": added_count,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"❌ Error in leadership admin addition process: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_chat_members": 0,
                "existing_team_members": 0,
                "new_members_added": 0,
                "errors": [str(e)]
            }
        
        finally:
            if self.bot:
                await self.bot.close()


async def main():
    """Main function."""
    logger.info("🤖 Leadership Admin Addition Script")
    logger.info("=" * 50)
    
    # Get team ID from command line argument or use default
    if len(sys.argv) > 1:
        team_id = sys.argv[1]
    else:
        team_id = 'KTI'  # Default to KTI if not specified
    
    logger.info(f"Team ID: {team_id}")
    
    try:
        # Create and run the adder
        adder = LeadershipAdminAdder(team_id)
        result = await adder.run()
        
        if result["success"]:
            logger.info("✅ Leadership admin addition completed successfully!")
        else:
            logger.error("❌ Leadership admin addition completed with errors!")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the script
    result = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success", False) else 1) 