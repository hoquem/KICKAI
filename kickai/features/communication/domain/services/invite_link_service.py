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
from typing import Any

from loguru import logger
from telegram.error import TelegramError
from telegram.ext import Application

from kickai.database.interfaces import DataStoreInterface


class InviteLinkService:
    """Service for creating and managing secure invite links."""

    def __init__(self, bot_token: str | None = None, database: DataStoreInterface = None):
        self.database = database
        self.collection_name = (
            "kickai_invite_links"  # TODO: Use constant from firestore_constants.py
        )
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

    def _detect_mock_environment(self) -> bool:
        """
        Detect if running in mock testing environment.


    :return: True if in mock environment, False otherwise
    :rtype: str  # TODO: Fix type
        """
        try:
            # Check for mock server running on localhost:8001
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 8001))
            sock.close()
            if result == 0:
                logger.info("🧪 Mock environment detected: localhost:8001 is available")
                return True

            # Check for MOCK_TELEGRAM_BASE_URL environment variable
            mock_url = os.getenv("MOCK_TELEGRAM_BASE_URL")
            if mock_url:
                logger.info(f"🧪 Mock environment detected: MOCK_TELEGRAM_BASE_URL={mock_url}")
                return True

            # Check for test-specific configuration
            if os.getenv("KICKAI_TEST_MODE") == "true":
                logger.info("🧪 Mock environment detected: KICKAI_TEST_MODE=true")
                return True

            return False

        except Exception as e:
            logger.debug(f"Error detecting mock environment: {e}")
            return False

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


            player_data: Dictionary containing player information


    :return: Base64 encoded and signed invite data
    :rtype: str  # TODO: Fix type
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

    def _validate_secure_invite_data(self, invite_data: str) -> dict | None:
        """
        Validate and decode secure invite data.


            invite_data: Base64 encoded invite data


    :return: Decoded player data if valid, None if invalid
    :rtype: str  # TODO: Fix type
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
        player_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a secure invite link for a player to join the main chat.


            team_id: Team ID
            player_name: Player's name
            player_phone: Player's phone number
            player_position: Player's position
            main_chat_id: Main chat ID
            player_id: Player ID (optional, will be generated if not provided)


    :return: Dict containing invite link details
    :rtype: str  # TODO: Fix type
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
                from kickai.utils.id_generator import generate_member_id

                # Generate simple member ID
                player_id = generate_member_id(player_name)

            # Create Telegram invite link (or mock invite link)
            if self._detect_mock_environment():
                invite_link = self._create_mock_invite_link(invite_id, "player", main_chat_id, team_id)
                logger.info(f"🧪 Created mock player invite link: {invite_link}")
            else:
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
                "is_mock": self._detect_mock_environment(),  # Flag for mock environment
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
    ) -> dict[str, Any]:
        """
        Create a secure invite link for a team member to join the leadership chat.


            team_id: Team ID
            member_name: Team member's name
            member_phone: Team member's phone number
            member_role: Team member's role
            leadership_chat_id: Leadership chat ID


    :return: Dict containing invite link details
    :rtype: str  # TODO: Fix type
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

            # Create Telegram invite link (or mock invite link)
            if self._detect_mock_environment():
                invite_link = self._create_mock_invite_link(invite_id, "team_member", leadership_chat_id, team_id)
                logger.info(f"🧪 Created mock team member invite link: {invite_link}")
            else:
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
                "is_mock": self._detect_mock_environment(),  # Flag for mock environment
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
        self, invite_link: str, user_id: str, username: str | None = None, secure_data: str | None = None
    ) -> dict[str, Any] | None:
        """
        Validate an invite link and mark it as used.


            invite_link: The invite link to validate
            user_id: Telegram user ID of the person using the link
            username: Telegram username (optional)
            secure_data: Secure data from the invite link (optional)


    :return: Dict containing invite details if valid, None if invalid
    :rtype: str  # TODO: Fix type
        """
        try:
            invite_id = None

            # Method 1: If secure_data is provided, validate it directly
            if secure_data:
                player_data = self._validate_secure_invite_data(secure_data)
                if not player_data:
                    logger.warning("❌ Invalid secure invite data")
                    return None
                invite_id = player_data["invite_id"]

            # Method 2: Try to extract invite_id directly from link (for mock links)
            if not invite_id and invite_link:
                invite_id = self._extract_invite_id_from_mock_link(invite_link)

            # Method 3: Extract invite ID from real Telegram link
            if not invite_id and invite_link:
                invite_id = self._extract_invite_id_from_link(invite_link)

            # Method 4: Check if invite_link is actually an invite_id directly
            if not invite_id and invite_link:
                # Sometimes invite_link might be passed as invite_id directly
                if len(invite_link) == 36 and invite_link.count('-') == 4:  # UUID format
                    invite_id = invite_link

            if not invite_id:
                logger.warning(f"❌ Could not extract invite_id from: {invite_link}")
                return None

            logger.info(f"🔗 Looking up invite_id: {invite_id}")

            # Get invite data from Firestore
            invite_data = await self.database.get_document(self.collection_name, invite_id)
            if not invite_data:
                logger.warning(f"❌ Invite link not found: {invite_id}")
                return None

            # Check if link is already used
            if invite_data["status"] != "active":
                logger.warning(f"❌ Invite link already used: {invite_id} (status: {invite_data['status']})")
                return None

            # Check expiration
            expires_at = datetime.fromisoformat(invite_data["expires_at"])
            if datetime.now() > expires_at:
                logger.warning(f"❌ Invite link expired: {invite_id}")
                # Mark as expired
                await self.database.update_document(
                    self.collection_name,
                    invite_id,
                    {"status": "expired"}
                )
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


            invite_id: The invite ID to revoke


    :return: True if successful, False otherwise
    :rtype: str  # TODO: Fix type
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


            team_id: Team ID


    :return: List of active invite links
    :rtype: str  # TODO: Fix type
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

    def _create_mock_invite_link(self, invite_id: str, invite_type: str, chat_id: str, team_id: str) -> str:
        """
        Create a mock invite link for testing environment.


            invite_id: Unique invite ID
            invite_type: Type of invite ("player" or "team_member")
            chat_id: Chat ID for the invite
            team_id: Team ID


    :return: Mock invite link URL
    :rtype: str  # TODO: Fix type
        """
        mock_base_url = os.getenv("MOCK_TELEGRAM_BASE_URL", "http://localhost:8001")

        # Create mock invite link in the specified format
        mock_link = f"{mock_base_url}/?invite={invite_id}&type={invite_type}&chat={chat_id}&team={team_id}"

        # Store in database with mock flag
        return mock_link

    async def _create_telegram_invite_link(self, chat_id: str, invite_id: str) -> str:
        """
        Create a Telegram invite link using the bot API.


            chat_id: Chat ID to create invite link for
            invite_id: Unique invite ID for reference


    :return: The generated invite link
    :rtype: str  # TODO: Fix type
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

    def _extract_invite_id_from_mock_link(self, invite_link: str) -> str | None:
        """
        Extract invite ID from a mock invite link.


            invite_link: Mock invite link (e.g., http://localhost:8001/?invite=abc123&type=player&chat=123&team=KTI)


    :return: The invite ID if found, None otherwise
    :rtype: str  # TODO: Fix type
        """
        try:
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(invite_link)
            if parsed.hostname in ['localhost', '127.0.0.1'] and parsed.query:
                query_params = parse_qs(parsed.query)
                invite_id = query_params.get('invite', [None])[0]
                if invite_id:
                    logger.info(f"🔗 Extracted invite_id from mock link: {invite_id}")
                    return invite_id

            return None

        except Exception as e:
            logger.error(f"❌ Error extracting invite ID from mock link: {e}")
            return None

    def _extract_invite_id_from_link(self, invite_link: str) -> str | None:
        """
        Extract invite ID from a Telegram invite link.


            invite_link: The invite link


    :return: The invite ID if found, None otherwise
    :rtype: str  # TODO: Fix type
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


    :return: Number of links cleaned up
    :rtype: str  # TODO: Fix type
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

    # Synchronous methods for CrewAI tools
    def create_player_invite_link_sync(
        self,
        team_id: str,
        player_name: str,
        player_phone: str,
        player_position: str,
        main_chat_id: str,
        player_id: str | None = None,
    ) -> dict[str, Any]:
        """Synchronous version of create_player_invite_link for CrewAI tools."""
        try:
            # Import here to avoid circular imports
            import asyncio

            # Check if we're already in an event loop
            try:
                asyncio.get_running_loop()
                # We're in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.create_player_invite_link(
                        team_id, player_name, player_phone, player_position, main_chat_id, player_id
                    ))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(self.create_player_invite_link(
                    team_id, player_name, player_phone, player_position, main_chat_id, player_id
                ))

        except Exception as e:
            logger.error(f"❌ Failed to create player invite link: {e}")
            return {"error": f"Failed to create invite link: {e!s}"}
