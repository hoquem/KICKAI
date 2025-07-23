#!/usr/bin/env python3
"""
Invite Link Service

This module provides services for generating and managing unique Telegram invite links
for players and team members. Links are stored in Firestore for validation and one-time use.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from loguru import logger
from telegram import Bot
from telegram.error import TelegramError

from database.interfaces import DataStoreInterface


class InviteLinkService:
    """Service for managing Telegram invite links."""

    def __init__(self, database: DataStoreInterface, bot_token: str = None):
        self.database = database
        self.bot_token = bot_token
        self.bot = None  # Lazy initialize
        self.collection_name = "kickai_invite_links"

    def _get_bot(self):
        """Lazy initialize the bot instance."""
        if self.bot is None:
            if not self.bot_token:
                raise ValueError("Bot token not available for InviteLinkService")
            self.bot = Bot(token=self.bot_token)
        return self.bot

    def set_bot_token(self, bot_token: str):
        """Set the bot token (called after loading from Firestore)."""
        self.bot_token = bot_token
        self.bot = None  # Reset bot instance to use new token

    async def create_player_invite_link(self, team_id: str, player_name: str, player_phone: str,
                                      player_position: str, main_chat_id: str) -> dict[str, Any]:
        """
        Create a unique invite link for a player to join the main chat.
        
        Args:
            team_id: Team ID
            player_name: Player's name
            player_phone: Player's phone number
            player_position: Player's position
            main_chat_id: Main chat ID
            
        Returns:
            Dict containing invite link details
        """
        try:
            # Generate unique invite link ID
            invite_id = str(uuid.uuid4())

            # Create Telegram invite link
            invite_link = await self._create_telegram_invite_link(main_chat_id, invite_id)

            # Store invite link in Firestore
            invite_data = {
                "invite_id": invite_id,
                "team_id": team_id,
                "chat_id": main_chat_id,
                "chat_type": "main",
                "invite_link": invite_link,
                "player_name": player_name,
                "player_phone": player_phone,
                "player_position": player_position,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),  # 7 days expiry
                "used_at": None,
                "used_by": None
            }

            await self.database.create_document(self.collection_name, invite_data, invite_id)

            logger.info(f"✅ Created player invite link: {invite_id} for {player_name}")

            return {
                "invite_id": invite_id,
                "invite_link": invite_link,
                "player_name": player_name,
                "expires_at": invite_data["expires_at"]
            }

        except Exception as e:
            logger.error(f"❌ Error creating player invite link: {e}")
            raise

    async def create_team_member_invite_link(self, team_id: str, member_name: str,
                                           member_phone: str, member_role: str,
                                           leadership_chat_id: str) -> dict[str, Any]:
        """
        Create a unique invite link for a team member to join the leadership chat.
        
        Args:
            team_id: Team ID
            member_name: Team member's name
            member_phone: Team member's phone number
            member_role: Team member's role
            leadership_chat_id: Leadership chat ID
            
        Returns:
            Dict containing invite link details
        """
        try:
            # Generate unique invite link ID
            invite_id = str(uuid.uuid4())

            # Create Telegram invite link
            invite_link = await self._create_telegram_invite_link(leadership_chat_id, invite_id)

            # Store invite link in Firestore
            invite_data = {
                "invite_id": invite_id,
                "team_id": team_id,
                "chat_id": leadership_chat_id,
                "chat_type": "leadership",
                "invite_link": invite_link,
                "member_name": member_name,
                "member_phone": member_phone,
                "member_role": member_role,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),  # 7 days expiry
                "used_at": None,
                "used_by": None
            }

            await self.database.create_document(self.collection_name, invite_data, invite_id)

            logger.info(f"✅ Created team member invite link: {invite_id} for {member_name}")

            return {
                "invite_id": invite_id,
                "invite_link": invite_link,
                "member_name": member_name,
                "expires_at": invite_data["expires_at"]
            }

        except Exception as e:
            logger.error(f"❌ Error creating team member invite link: {e}")
            raise

    async def validate_and_use_invite_link(self, invite_link: str, user_id: str,
                                         username: str = None) -> dict[str, Any] | None:
        """
        Validate an invite link and mark it as used.
        
        Args:
            invite_link: The invite link to validate
            user_id: Telegram user ID of the person using the link
            username: Telegram username (optional)
            
        Returns:
            Dict containing invite details if valid, None if invalid
        """
        try:
            # Extract invite ID from link
            invite_id = self._extract_invite_id_from_link(invite_link)
            if not invite_id:
                logger.warning(f"❌ Invalid invite link format: {invite_link}")
                return None

            # Get invite data from Firestore
            invite_data = await self.database.get_document(self.collection_name, invite_id)
            if not invite_data:
                logger.warning(f"❌ Invite link not found: {invite_id}")
                return None

            # Check if link is expired
            expires_at = datetime.fromisoformat(invite_data["expires_at"])
            if datetime.now() > expires_at:
                logger.warning(f"❌ Invite link expired: {invite_id}")
                return None

            # Check if link is already used
            if invite_data["status"] != "active":
                logger.warning(f"❌ Invite link already used: {invite_id}")
                return None

            # Mark link as used
            await self.database.update_document(
                self.collection_name,
                invite_id,
                {
                    "status": "used",
                    "used_at": datetime.now().isoformat(),
                    "used_by": user_id,
                    "used_by_username": username
                }
            )

            logger.info(f"✅ Invite link used: {invite_id} by {user_id}")

            return invite_data

        except Exception as e:
            logger.error(f"❌ Error validating invite link: {e}")
            return None

    async def revoke_invite_link(self, invite_id: str) -> bool:
        """
        Revoke an invite link (mark as revoked).
        
        Args:
            invite_id: The invite ID to revoke
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.database.update_document(
                self.collection_name,
                invite_id,
                {
                    "status": "revoked",
                    "revoked_at": datetime.now().isoformat()
                }
            )

            logger.info(f"✅ Invite link revoked: {invite_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error revoking invite link: {e}")
            return False

    async def get_active_invite_links(self, team_id: str) -> list:
        """
        Get all active invite links for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of active invite links
        """
        try:
            filters = [
                {"field": "team_id", "operator": "==", "value": team_id},
                {"field": "status", "operator": "==", "value": "active"}
            ]

            links = await self.database.query_documents(self.collection_name, filters)
            return links

        except Exception as e:
            logger.error(f"❌ Error getting active invite links: {e}")
            return []

    async def _create_telegram_invite_link(self, chat_id: str, invite_id: str) -> str:
        """
        Create a Telegram invite link using the bot API.
        
        Args:
            chat_id: Chat ID to create invite link for
            invite_id: Unique invite ID for reference
            
        Returns:
            The generated invite link
        """
        try:
            # Create invite link with custom parameters
            bot = self._get_bot()
            invite_link = await bot.create_chat_invite_link(
                chat_id=int(chat_id),
                name=f"KICKAI Invite {invite_id[:8]}",  # Short name for the link
                creates_join_request=False,  # Direct join, no approval needed
                expire_date=int((datetime.now() + timedelta(days=7)).timestamp()),  # 7 days
                member_limit=1  # One-time use
            )

            return invite_link.invite_link

        except TelegramError as e:
            logger.error(f"❌ Telegram API error creating invite link: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error creating Telegram invite link: {e}")
            raise

    def _extract_invite_id_from_link(self, invite_link: str) -> str | None:
        """
        Extract invite ID from a Telegram invite link.
        
        Args:
            invite_link: The invite link
            
        Returns:
            The invite ID if found, None otherwise
        """
        try:
            # Telegram invite links have format: https://t.me/+[invite_hash]
            # We need to extract the invite_hash and look it up in Firestore
            # For now, we'll use a simple approach - extract the hash part
            if "t.me/+" in invite_link:
                invite_hash = invite_link.split("t.me/+")[1]
                # We'll need to query Firestore to find the invite_id by invite_hash
                # This is a simplified version - in practice, you might want to store
                # the invite_hash in the document for easier lookup
                return invite_hash
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting invite ID from link: {e}")
            return None

    async def cleanup_expired_links(self) -> int:
        """
        Clean up expired invite links from Firestore.
        
        Returns:
            Number of links cleaned up
        """
        try:
            # Get all expired links
            filters = [
                {"field": "expires_at", "operator": "<", "value": datetime.now().isoformat()},
                {"field": "status", "operator": "==", "value": "active"}
            ]

            expired_links = await self.database.query_documents(self.collection_name, filters)

            # Mark them as expired
            for link in expired_links:
                await self.database.update_document(
                    self.collection_name,
                    link["invite_id"],
                    {"status": "expired"}
                )

            logger.info(f"✅ Cleaned up {len(expired_links)} expired invite links")
            return len(expired_links)

        except Exception as e:
            logger.error(f"❌ Error cleaning up expired links: {e}")
            return 0
