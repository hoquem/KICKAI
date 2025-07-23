#!/usr/bin/env python3
"""
Script to add leadership chat members as team admins in Firestore.

This script:
1. Connects to Telegram using the bot token
2. Gets the list of administrators in the leadership chat
3. Adds each admin as a team member in Firestore with admin role
4. Provides a summary of the operation

Usage:
    python scripts-oneoff/add_leadership_admins.py
"""

import asyncio
import os
import sys
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from src.database.firebase_client import FirebaseClient
from src.config.environment import get_environment_config


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
        self.env_config = get_environment_config()
        self.bot_token = self.env_config.get('TELEGRAM_BOT_TOKEN')
        self.leadership_chat_id = self.env_config.get('TELEGRAM_LEADERSHIP_CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
        if not self.leadership_chat_id:
            raise ValueError("TELEGRAM_LEADERSHIP_CHAT_ID not found in environment")
        
        self.bot = Bot(token=self.bot_token)
        self.firebase_client = FirebaseClient()
        
        logger.info(f"Initialized LeadershipAdminAdder for team: {team_id}")
        logger.info(f"Leadership chat ID: {self.leadership_chat_id}")
    
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
            existing_members = await self.firebase_client.query_documents(
                collection=collection_name,
                filters=[("team_id", "==", self.team_id)]
            )
            
            logger.info(f"Found {len(existing_members)} existing team members")
            return existing_members
            
        except Exception as e:
            logger.error(f"Error checking existing team members: {e}")
            raise
    
    async def add_team_member(self, member: ChatMember) -> bool:
        """Add a chat member as a team member in Firestore."""
        try:
            # Determine role based on status
            if member.status == 'creator':
                role = "Team Owner"
            elif member.status == 'administrator':
                role = "Team Administrator"
            else:
                role = "Team Member"
            
            # Create team member document
            team_member_data = {
                "team_id": self.team_id,
                "telegram_id": str(member.user_id),
                "username": member.username,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "full_name": f"{member.first_name} {member.last_name}".strip(),
                "role": role,
                "status": "active",
                "is_admin": member.is_admin,
                "chat_status": member.status,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "registration_source": "leadership_chat_admin_script"
            }
            
            # Add to Firestore
            collection_name = f"kickai_{self.team_id}_team_members"
            doc_id = f"{self.team_id}_{member.user_id}"
            
            await self.firebase_client.add_document(
                collection=collection_name,
                document_id=doc_id,
                data=team_member_data
            )
            
            logger.info(f"✅ Added team member: {member.first_name} {member.last_name} as {role}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding team member {member.first_name} {member.last_name}: {e}")
            return False
    
    async def run(self) -> Dict[str, Any]:
        """Main execution method."""
        logger.info("🚀 Starting leadership admin addition process...")
        
        try:
            # Get chat administrators
            chat_members = await self.get_chat_administrators()
            
            # Check existing team members
            existing_members = await self.check_existing_team_members()
            existing_telegram_ids = {member.get('telegram_id') for member in existing_members}
            
            # Filter out existing members
            new_members = [member for member in chat_members if str(member.user_id) not in existing_telegram_ids]
            
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
                    errors.append(f"Failed to add {member.first_name} {member.last_name}")
            
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
            await self.bot.close()


async def main():
    """Main function."""
    logger.info("🤖 Leadership Admin Addition Script")
    logger.info("=" * 50)
    
    # Get team ID from environment
    env_config = get_environment_config()
    team_id = env_config.get('TEAM_ID', 'KTI')  # Default to KTI if not specified
    
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