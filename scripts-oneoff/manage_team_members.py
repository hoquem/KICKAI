#!/usr/bin/env python3
"""
Team Member Management Script

This script provides comprehensive functionality for managing team members in the
kickai_<team_id>_team_members collection. It can add new team members, validate
existing ones, and ensure they are properly added to the team's leadership chat.

Features:
- Add new team members with validation
- Check if team members are in leadership chat
- Get Telegram information for team members
- Validate existing team member data
- List all team members with their status
- Remove team members (with confirmation)

Usage:
    python scripts-oneoff/manage_team_members.py --action add --team-id KTI --name "John Smith" --phone "+1234567890" --role "admin"
    python scripts-oneoff/manage_team_members.py --action list --team-id KTI
    python scripts-oneoff/manage_team_members.py --action validate --team-id KTI
    python scripts-oneoff/manage_team_members.py --action remove --team-id KTI --telegram-id "123456789"
"""

import asyncio
import os
import sys
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from src.database.firebase_client import FirebaseClient
from src.config.environment import get_environment_config
from src.features.team_administration.domain.entities.team_member import TeamMember


@dataclass
class TeamMemberInfo:
    """Information about a team member."""
    name: str
    phone: str
    role: str
    telegram_username: Optional[str] = None
    telegram_id: Optional[str] = None
    user_id: Optional[str] = None


class TeamMemberManager:
    """Manages team members in Firestore and validates their presence in Telegram."""
    
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
        self.collection_name = f"kickai_{team_id}_team_members"
        
        logger.info(f"Initialized TeamMemberManager for team: {team_id}")
        logger.info(f"Collection: {self.collection_name}")
        logger.info(f"Leadership chat ID: {self.leadership_chat_id}")
    
    async def get_leadership_chat_members(self) -> List[Dict[str, Any]]:
        """Get all members from the leadership chat."""
        try:
            logger.info("Fetching leadership chat members...")
            members = await self.bot.get_chat_members(chat_id=self.leadership_chat_id)
            
            chat_members = []
            for member in members:
                chat_member = {
                    'user_id': member.user.id,
                    'username': member.user.username or "",
                    'first_name': member.user.first_name or "",
                    'last_name': member.user.last_name or "",
                    'full_name': f"{member.user.first_name or ''} {member.user.last_name or ''}".strip(),
                    'status': member.status,
                    'is_admin': member.status in ['creator', 'administrator']
                }
                chat_members.append(chat_member)
                logger.info(f"Found member: {chat_member['full_name']} (@{chat_member['username']}) - Status: {chat_member['status']}")
            
            logger.info(f"Found {len(chat_members)} members in leadership chat")
            return chat_members
            
        except TelegramError as e:
            logger.error(f"Error fetching leadership chat members: {e}")
            raise
    
    async def get_team_members_from_firestore(self) -> List[Dict[str, Any]]:
        """Get all team members from Firestore."""
        try:
            team_members = await self.firebase_client.query_documents(
                collection=self.collection_name,
                filters=[("team_id", "==", self.team_id)]
            )
            
            logger.info(f"Found {len(team_members)} team members in Firestore")
            return team_members
            
        except Exception as e:
            logger.error(f"Error fetching team members from Firestore: {e}")
            raise
    
    async def find_telegram_user_by_phone(self, phone: str, chat_members: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find a Telegram user by phone number (requires manual matching)."""
        logger.info(f"Looking for user with phone: {phone}")
        logger.info("Note: Phone number matching requires manual verification as Telegram doesn't expose phone numbers")
        
        # Show available members for manual selection
        logger.info("Available leadership chat members:")
        for i, member in enumerate(chat_members, 1):
            logger.info(f"  {i}. {member['full_name']} (@{member['username']}) - ID: {member['user_id']}")
        
        return None
    
    async def add_team_member(self, member_info: TeamMemberInfo) -> bool:
        """Add a new team member to Firestore."""
        try:
            # Get leadership chat members
            chat_members = await self.get_leadership_chat_members()
            
            # Check if team member already exists
            existing_members = await self.firebase_client.query_documents(
                collection=self.collection_name,
                filters=[
                    ("team_id", "==", self.team_id),
                    ("phone", "==", member_info.phone)
                ]
            )
            
            if existing_members:
                logger.warning(f"⚠️ Team member with phone {member_info.phone} already exists")
                for member in existing_members:
                    logger.info(f"   - Name: {member.get('name')}")
                    logger.info(f"   - Telegram ID: {member.get('telegram_id')}")
                    logger.info(f"   - Roles: {member.get('roles', [])}")
                return False
            
            # Create team member document
            team_member_data = {
                "team_id": self.team_id,
                "name": member_info.name,
                "phone": member_info.phone,
                "role": member_info.role,
                "telegram_username": member_info.telegram_username,
                "telegram_id": member_info.telegram_id,
                "user_id": member_info.user_id or member_info.telegram_id,
                "roles": [member_info.role.lower()],
                "status": "active",
                "is_admin": member_info.role.lower() in ['admin', 'manager', 'captain'],
                "chat_status": "unknown",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "registration_source": "team_member_manager_script"
            }
            
            # Add to Firestore
            doc_id = f"{self.team_id}_{member_info.telegram_id or member_info.phone}"
            
            await self.firebase_client.add_document(
                collection=self.collection_name,
                document_id=doc_id,
                data=team_member_data
            )
            
            logger.info(f"✅ Added team member: {member_info.name}")
            logger.info(f"   - Document ID: {doc_id}")
            logger.info(f"   - Phone: {member_info.phone}")
            logger.info(f"   - Role: {member_info.role}")
            logger.info(f"   - Telegram ID: {member_info.telegram_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding team member {member_info.name}: {e}")
            return False
    
    async def validate_team_members(self) -> Dict[str, Any]:
        """Validate all team members against leadership chat membership."""
        try:
            logger.info("🔍 Starting team member validation...")
            
            # Get team members from Firestore
            firestore_members = await self.get_team_members_from_firestore()
            
            # Get leadership chat members
            chat_members = await self.get_leadership_chat_members()
            chat_member_ids = {str(member['user_id']) for member in chat_members}
            chat_member_usernames = {member['username'] for member in chat_members if member['username']}
            
            validation_results = {
                'total_members': len(firestore_members),
                'in_chat': 0,
                'not_in_chat': 0,
                'missing_telegram_info': 0,
                'details': []
            }
            
            for member in firestore_members:
                member_detail = {
                    'name': member.get('name', 'Unknown'),
                    'phone': member.get('phone', 'Unknown'),
                    'telegram_id': member.get('telegram_id'),
                    'telegram_username': member.get('telegram_username'),
                    'role': member.get('role', 'Unknown'),
                    'in_chat': False,
                    'issues': []
                }
                
                # Check if member is in leadership chat
                if member.get('telegram_id') and member['telegram_id'] in chat_member_ids:
                    member_detail['in_chat'] = True
                    validation_results['in_chat'] += 1
                elif member.get('telegram_username') and member['telegram_username'] in chat_member_usernames:
                    member_detail['in_chat'] = True
                    validation_results['in_chat'] += 1
                else:
                    member_detail['in_chat'] = False
                    validation_results['not_in_chat'] += 1
                    member_detail['issues'].append("Not in leadership chat")
                
                # Check for missing Telegram information
                if not member.get('telegram_id') and not member.get('telegram_username'):
                    validation_results['missing_telegram_info'] += 1
                    member_detail['issues'].append("Missing Telegram information")
                
                validation_results['details'].append(member_detail)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Error validating team members: {e}")
            raise
    
    async def list_team_members(self) -> List[Dict[str, Any]]:
        """List all team members with their details."""
        try:
            team_members = await self.get_team_members_from_firestore()
            
            logger.info(f"📋 Team Members for {self.team_id}:")
            logger.info("=" * 80)
            
            for i, member in enumerate(team_members, 1):
                logger.info(f"{i}. {member.get('name', 'Unknown')}")
                logger.info(f"   📞 Phone: {member.get('phone', 'Unknown')}")
                logger.info(f"   🏷️  Role: {member.get('role', 'Unknown')}")
                logger.info(f"   📱 Telegram ID: {member.get('telegram_id', 'Unknown')}")
                logger.info(f"   👤 Username: @{member.get('telegram_username', 'Unknown')}")
                logger.info(f"   📊 Status: {member.get('status', 'Unknown')}")
                logger.info(f"   📅 Created: {member.get('created_at', 'Unknown')}")
                logger.info("")
            
            return team_members
            
        except Exception as e:
            logger.error(f"❌ Error listing team members: {e}")
            raise
    
    async def remove_team_member(self, telegram_id: str) -> bool:
        """Remove a team member from Firestore."""
        try:
            # Find the team member
            existing_members = await self.firebase_client.query_documents(
                collection=self.collection_name,
                filters=[
                    ("team_id", "==", self.team_id),
                    ("telegram_id", "==", telegram_id)
                ]
            )
            
            if not existing_members:
                logger.error(f"❌ No team member found with Telegram ID: {telegram_id}")
                return False
            
            member = existing_members[0]
            logger.info(f"Found team member to remove: {member.get('name')} ({telegram_id})")
            
            # Delete the document
            doc_id = f"{self.team_id}_{telegram_id}"
            await self.firebase_client.delete_document(
                collection=self.collection_name,
                document_id=doc_id
            )
            
            logger.info(f"✅ Removed team member: {member.get('name')} ({telegram_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing team member: {e}")
            return False
    
    async def close(self):
        """Close the bot connection."""
        await self.bot.close()


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Team Member Management Script")
    parser.add_argument("--action", required=True, choices=["add", "list", "validate", "remove"],
                       help="Action to perform")
    parser.add_argument("--team-id", required=True, help="Team ID")
    parser.add_argument("--name", help="Team member name (for add action)")
    parser.add_argument("--phone", help="Phone number (for add action)")
    parser.add_argument("--role", help="Role (for add action)")
    parser.add_argument("--telegram-id", help="Telegram ID (for add/remove actions)")
    parser.add_argument("--telegram-username", help="Telegram username (for add action)")
    parser.add_argument("--user-id", help="User ID (for add action)")
    
    args = parser.parse_args()
    
    logger.info("🤖 Team Member Management Script")
    logger.info("=" * 50)
    logger.info(f"Team ID: {args.team_id}")
    logger.info(f"Action: {args.action}")
    
    try:
        manager = TeamMemberManager(args.team_id)
        
        if args.action == "add":
            if not all([args.name, args.phone, args.role]):
                logger.error("❌ Name, phone, and role are required for add action")
                return
            
            member_info = TeamMemberInfo(
                name=args.name,
                phone=args.phone,
                role=args.role,
                telegram_username=args.telegram_username,
                telegram_id=args.telegram_id,
                user_id=args.user_id
            )
            
            success = await manager.add_team_member(member_info)
            if success:
                logger.info("✅ Team member added successfully!")
            else:
                logger.error("❌ Failed to add team member")
        
        elif args.action == "list":
            await manager.list_team_members()
        
        elif args.action == "validate":
            results = await manager.validate_team_members()
            
            logger.info("📊 Validation Results:")
            logger.info(f"   Total members: {results['total_members']}")
            logger.info(f"   In leadership chat: {results['in_chat']}")
            logger.info(f"   Not in leadership chat: {results['not_in_chat']}")
            logger.info(f"   Missing Telegram info: {results['missing_telegram_info']}")
            
            if results['details']:
                logger.info("\n📋 Detailed Results:")
                for detail in results['details']:
                    status = "✅" if detail['in_chat'] else "❌"
                    logger.info(f"{status} {detail['name']} ({detail['phone']})")
                    if detail['issues']:
                        for issue in detail['issues']:
                            logger.info(f"   ⚠️  {issue}")
        
        elif args.action == "remove":
            if not args.telegram_id:
                logger.error("❌ Telegram ID is required for remove action")
                return
            
            success = await manager.remove_team_member(args.telegram_id)
            if success:
                logger.info("✅ Team member removed successfully!")
            else:
                logger.error("❌ Failed to remove team member")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    
    finally:
        if 'manager' in locals():
            await manager.close()
    
    return 0


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the script
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 