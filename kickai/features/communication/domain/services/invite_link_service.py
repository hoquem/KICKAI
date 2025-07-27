#!/usr/bin/env python3
"""
Invite Link Service

This module provides services for generating and managing unique Telegram invite links
for players and team members. Links are stored in Firestore for validation and one-time use.
"""

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from loguru import logger
from telegram.error import TelegramError
from telegram.ext import Application

from kickai.database.interfaces import DataStoreInterface


class InviteLinkService:
    """Service for creating and managing secure invite links."""

    def __init__(self, bot_token: str = None, database: DataStoreInterface = None):
        self.database = database
        self.collection_name = "kickai_invite_links"
        self.bot_token = bot_token
        self._bot = None
        
        # Validate database is provided
        if self.database is None:
            raise ValueError("Database interface is required for InviteLinkService")
        
        # Get secret key from environment variable
        self._secret_key = os.getenv("KICKAI_INVITE_SECRET_KEY")
        if not self._secret_key:
            raise ValueError(
                "KICKAI_INVITE_SECRET_KEY environment variable is required for secure invite links"
            )

    def _get_bot(self):
        """Get or create bot instance."""
        if not self.bot_token:
            raise ValueError("Bot token not available for InviteLinkService")

        if not self._bot:
            self._bot = Application.builder().token(self.bot_token).build()

        return self._bot

    def set_bot_token(self, bot_token: str):
        """Set the bot token for this service."""
        self.bot_token = bot_token
        self._bot = None  # Reset bot instance

    def is_bot_configured(self) -> bool:
        """Check if the bot is properly configured for creating invite links."""
        try:
            if not self.bot_token:
                return False

            # Test if we can create a bot instance
            app = self._get_bot()
            return hasattr(app, "bot") and hasattr(app.bot, "create_chat_invite_link")
        except Exception:
            return False

    def _generate_secure_invite_data(self, player_data: dict) -> str:
        """
        Generate secure invite data with embedded player information.

        Args:
            player_data: Dictionary containing player information

        Returns:
            Base64 encoded and signed invite data
        """
        import base64

        # Create invite payload
        payload = {
            "player_id": player_data.get("player_id"),
            "player_name": player_data.get("player_name"),
            "player_phone": player_data.get("player_phone"),
            "team_id": player_data.get("team_id"),
            "invite_id": player_data.get("invite_id"),
            "expires_at": player_data.get("expires_at"),
            "created_at": player_data.get("created_at"),
        }

        # Convert to JSON and encode
        json_data = json.dumps(payload, sort_keys=True)
        data_bytes = json_data.encode("utf-8")

        # Create HMAC signature
        signature = hmac.new(
            self._secret_key.encode("utf-8"), data_bytes, hashlib.sha256
        ).hexdigest()

        # Combine data and signature
        combined_data = f"{json_data}.{signature}"

        # Base64 encode for URL safety
        return base64.urlsafe_b64encode(combined_data.encode("utf-8")).decode("utf-8")

    def _validate_secure_invite_data(self, invite_data: str) -> Optional[dict]:
        """
        Validate and decode secure invite data.

        Args:
            invite_data: Base64 encoded invite data

        Returns:
            Decoded player data if valid, None if invalid
        """
        import base64

        try:
            # Decode from base64
            decoded_bytes = base64.urlsafe_b64decode(invite_data.encode("utf-8"))
            combined_data = decoded_bytes.decode("utf-8")

            # Split data and signature
            if "." not in combined_data:
                return None

            json_data, signature = combined_data.rsplit(".", 1)

            # Verify HMAC signature
            expected_signature = hmac.new(
                self._secret_key.encode("utf-8"), json_data.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("❌ Invalid invite link signature")
                return None

            # Parse JSON data
            payload = json.loads(json_data)

            # Check expiration
            expires_at = datetime.fromisoformat(payload["expires_at"])
            if datetime.now() > expires_at:
                logger.warning("❌ Invite link expired")
                return None

            return payload

        except Exception as e:
            logger.error(f"❌ Error validating invite data: {e}")
            return None

    async def create_player_invite_link(
        self,
        team_id: str,
        player_name: str,
        player_phone: str,
        player_position: str,
        main_chat_id: str,
        player_id: str = None,
    ) -> Dict[str, Any]:
        """
        Create a secure invite link for a player to join the main chat.

        Args:
            team_id: Team ID
            player_name: Player's name
            player_phone: Player's phone number
            player_position: Player's position
            main_chat_id: Main chat ID
            player_id: Player ID (optional, will be generated if not provided)

        Returns:
            Dict containing invite link details
        """
        try:
            # Validate bot token is available
            if not self.bot_token:
                raise ValueError("Bot token not available for creating invite links")

            # Validate chat ID
            if not main_chat_id or not main_chat_id.strip():
                raise ValueError("Main chat ID is required for creating invite links")

            # Generate unique invite link ID
            invite_id = str(uuid.uuid4())

            # Generate player ID if not provided
            if not player_id:
                from kickai.utils.football_id_generator import generate_football_player_id

                # Split name into first and last name for football ID generation
                name_parts = player_name.strip().split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                else:
                    first_name = name_parts[0] if name_parts else "Unknown"
                    last_name = first_name

                player_id = generate_football_player_id(first_name, last_name, "Player", team_id)

            # Create Telegram invite link
            invite_link = await self._create_telegram_invite_link(main_chat_id, invite_id)

            # Prepare player data for secure embedding
            player_data = {
                "player_id": player_id,
                "player_name": player_name,
                "player_phone": player_phone,
                "player_position": player_position,
                "team_id": team_id,
                "invite_id": invite_id,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            }

            # Generate secure invite data
            secure_data = self._generate_secure_invite_data(player_data)

            # Store invite link in Firestore
            invite_data = {
                "invite_id": invite_id,
                "team_id": team_id,
                "chat_id": main_chat_id,
                "chat_type": "main",
                "invite_link": invite_link,
                "secure_data": secure_data,  # Store the secure data
                "player_id": player_id,
                "player_name": player_name,
                "player_phone": player_phone,
                "player_position": player_position,
                "status": "active",
                "created_at": player_data["created_at"],
                "expires_at": player_data["expires_at"],
                "used_at": None,
                "used_by": None,
                "used_by_username": None,
            }

            await self.database.create_document(self.collection_name, invite_data, invite_id)

            logger.info(f"✅ Created secure player invite link: {invite_id} for {player_name}")

            return {
                "invite_id": invite_id,
                "invite_link": invite_link,
                "player_id": player_id,
                "player_name": player_name,
                "expires_at": player_data["expires_at"],
                "secure_data": secure_data,  # Include for validation
            }

        except Exception as e:
            logger.error(f"❌ Error creating player invite link: {e}")
            raise

    async def create_team_member_invite_link(
        self,
        team_id: str,
        member_name: str,
        member_phone: str,
        member_role: str,
        leadership_chat_id: str,
    ) -> Dict[str, Any]:
        """
        Create a secure invite link for a team member to join the leadership chat.

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
            # Validate bot token is available
            if not self.bot_token:
                raise ValueError("Bot token not available for creating invite links")

            # Validate chat ID
            if not leadership_chat_id or not leadership_chat_id.strip():
                raise ValueError("Leadership chat ID is required for creating invite links")

            # Generate unique invite link ID
            invite_id = str(uuid.uuid4())

            # Create Telegram invite link
            invite_link = await self._create_telegram_invite_link(leadership_chat_id, invite_id)

            # Prepare member data for secure embedding
            member_data = {
                "member_id": f"member_{team_id}_{member_phone}",
                "member_name": member_name,
                "member_phone": member_phone,
                "member_role": member_role,
                "team_id": team_id,
                "invite_id": invite_id,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            }

            # Generate secure invite data
            secure_data = self._generate_secure_invite_data(member_data)

            # Store invite link in Firestore
            invite_data = {
                "invite_id": invite_id,
                "team_id": team_id,
                "chat_id": leadership_chat_id,
                "chat_type": "leadership",
                "invite_link": invite_link,
                "secure_data": secure_data,  # Store the secure data
                "member_id": member_data["member_id"],
                "member_name": member_name,
                "member_phone": member_phone,
                "member_role": member_role,
                "status": "active",
                "created_at": member_data["created_at"],
                "expires_at": member_data["expires_at"],
                "used_at": None,
                "used_by": None,
                "used_by_username": None,
            }

            if self.database is None:
                raise ValueError("Database is not initialized in InviteLinkService")
            
            await self.database.create_document(self.collection_name, invite_data, invite_id)

            logger.info(f"✅ Created secure team member invite link: {invite_id} for {member_name}")

            return {
                "invite_id": invite_id,
                "invite_link": invite_link,
                "member_id": member_data["member_id"],
                "member_name": member_name,
                "expires_at": member_data["expires_at"],
                "secure_data": secure_data,  # Include for validation
            }

        except Exception as e:
            logger.error(f"❌ Error creating team member invite link: {e}")
            raise

    async def validate_and_use_invite_link(
        self, invite_link: str, user_id: str, username: str = None, secure_data: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Validate an invite link and mark it as used.

        Args:
            invite_link: The invite link to validate
            user_id: Telegram user ID of the person using the link
            username: Telegram username (optional)
            secure_data: Secure data from the invite link (optional)

        Returns:
            Dict containing invite details if valid, None if invalid
        """
        try:
            # If secure_data is provided, validate it directly
            if secure_data:
                player_data = self._validate_secure_invite_data(secure_data)
                if not player_data:
                    logger.warning("❌ Invalid secure invite data")
                    return None

                invite_id = player_data["invite_id"]
            else:
                # Fallback to old method - extract invite ID from link
                invite_id = self._extract_invite_id_from_link(invite_link)
                if not invite_id:
                    logger.warning(f"❌ Invalid invite link format: {invite_link}")
                    return None

            # Get invite data from Firestore
            invite_data = await self.database.get_document(self.collection_name, invite_id)
            if not invite_data:
                logger.warning(f"❌ Invite link not found: {invite_id}")
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
                    "used_by_username": username,
                },
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
                {"status": "revoked", "revoked_at": datetime.now().isoformat()},
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
                {"field": "status", "operator": "==", "value": "active"},
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
            app = self._get_bot()
            invite_link = await app.bot.create_chat_invite_link(
                chat_id=int(chat_id),
                name=f"KICKAI Invite {invite_id[:8]}",  # Short name for the link
                creates_join_request=False,  # Direct join, no approval needed
                expire_date=int((datetime.now() + timedelta(days=7)).timestamp()),  # 7 days
                member_limit=1,  # One-time use
            )

            return invite_link.invite_link

        except TelegramError as e:
            logger.error(f"❌ Telegram API error creating invite link: {e}")
            raise
        except AttributeError as e:
            logger.error(f"❌ Bot not properly configured for invite links: {e}")
            raise ValueError("Bot not properly configured for creating invite links")
        except Exception as e:
            logger.error(f"❌ Error creating Telegram invite link: {e}")
            raise

    def _extract_invite_id_from_link(self, invite_link: str) -> Optional[str]:
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
                {"field": "status", "operator": "==", "value": "active"},
            ]

            expired_links = await self.database.query_documents(self.collection_name, filters)

            # Mark them as expired
            for link in expired_links:
                await self.database.update_document(
                    self.collection_name, link["invite_id"], {"status": "expired"}
                )

            logger.info(f"✅ Cleaned up {len(expired_links)} expired invite links")
            return len(expired_links)

        except Exception as e:
            logger.error(f"❌ Error cleaning up expired links: {e}")
            return 0
