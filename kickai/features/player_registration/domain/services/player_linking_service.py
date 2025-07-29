#!/usr/bin/env python3
"""
Player Linking Service

This module provides phone number linking functionality to connect Telegram users
to existing Firestore player records.
"""

from datetime import datetime

from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.entities.player import Player
from kickai.utils.phone_validation import (
    normalize_phone_number,
    validate_phone_number,
)


class PlayerLinkingService:
    """Service for linking Telegram users to existing player records via phone numbers."""

    def __init__(self, team_id: str):
        self.team_id = team_id
        self.container = get_container()

    async def link_telegram_user_by_phone(
        self, phone: str, telegram_id: str, username: str = None
    ) -> Player | None:
        """
        Link a Telegram user to an existing player record using phone number.

        Args:
            phone: Phone number to search for
            telegram_id: Telegram user ID to link
            username: Telegram username (optional)

        Returns:
            Player object if successfully linked, None otherwise
        """
        try:
            logger.info(f"🔗 Attempting to link telegram_id={telegram_id} to phone={phone}")

            # Get player service from container using the correct method
            from kickai.features.player_registration.domain.services.player_service import (
                PlayerService,
            )

            try:
                player_service = self.container.get_service(PlayerService)
            except RuntimeError as e:
                logger.error(f"❌ Player service not available: {e}")
                return None
            except Exception as e:
                logger.error(f"❌ Unexpected error getting player service: {e}")
                return None

            if not player_service:
                logger.error("❌ Player service returned None")
                return None

            # Find existing player by phone number
            existing_player = await player_service.get_player_by_phone(
                phone=phone, team_id=self.team_id
            )
            if not existing_player:
                logger.info(f"❌ No player found with phone={phone} in team={self.team_id}")
                return None

            # Check if player already has telegram_id
            if existing_player.telegram_id:
                if existing_player.telegram_id == str(telegram_id):
                    logger.info(f"✅ Player already linked to telegram_id={telegram_id}")
                    return existing_player
                else:
                    logger.warning(
                        f"⚠️ Player {existing_player.player_id} already linked to different telegram_id={existing_player.telegram_id}"
                    )
                    return None

            # Update player with telegram information
            updated_player = await self._update_player_telegram_info(
                player_id=existing_player.player_id, telegram_id=str(telegram_id), username=username
            )

            if updated_player:
                logger.info(
                    f"✅ Successfully linked player {existing_player.player_id} to telegram_id={telegram_id}"
                )
                return updated_player
            else:
                logger.error(
                    f"❌ Failed to update player {existing_player.player_id} with telegram info"
                )
                return None

        except Exception as e:
            logger.error(f"❌ Error linking telegram user by phone: {e}")
            return None

    async def _update_player_telegram_info(
        self, player_id: str, telegram_id: str, username: str = None
    ) -> Player | None:
        """Update player record with Telegram information."""
        try:
            # Get database client
            database = self.container.get_database()
            if not database:
                logger.error("❌ Database not available")
                return None

            # Prepare update data
            update_data = {"telegram_id": telegram_id, "updated_at": datetime.now().isoformat()}

            if username:
                update_data["username"] = username

            # Update the player record
            success = await database.update_player(player_id, update_data, self.team_id)
            if not success:
                logger.error(f"❌ Failed to update player {player_id} in database")
                return None

            # Get updated player record
            from kickai.features.player_registration.domain.services.player_service import (
                PlayerService,
            )

            try:
                player_service = self.container.get_service(PlayerService)
                if player_service:
                    updated_player = await player_service.get_player_by_id(player_id, self.team_id)
                    return updated_player
            except RuntimeError as e:
                logger.error(f"❌ Player service not available for getting updated player: {e}")
            except Exception as e:
                logger.error(f"❌ Unexpected error getting player service for updated player: {e}")

            return None

        except Exception as e:
            logger.error(f"❌ Error updating player telegram info: {e}")
            return None

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number format using enhanced international validation.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return False

        # Use the enhanced phone validation utility
        result = validate_phone_number(phone)
        return result.is_valid

    @staticmethod
    def normalize_phone_number(phone: str) -> str:
        """
        Normalize phone number to international format using enhanced validation.

        Args:
            phone: Phone number to normalize

        Returns:
            Normalized phone number in international format
        """
        if not phone:
            return ""

        # Use the enhanced phone validation utility
        return normalize_phone_number(phone)

    async def get_pending_players_without_telegram_id(self) -> list[Player]:
        """Get all pending players that don't have telegram_id set."""
        try:
            # Get player service using factory method
            player_service = self._get_player_service()

            if not player_service:
                logger.error(f"❌ Player service returned None for team {self.team_id}")
                return []

            # Get all players for the team
            try:
                all_players = await player_service.get_all_players(self.team_id)
            except Exception as e:
                logger.error(
                    f"❌ Error fetching players for team {self.team_id}, "
                    f"operation: get_pending_players_without_telegram_id, error: {e}"
                )
                return []

            # Filter for pending players without telegram_id
            pending_players = [
                player
                for player in all_players
                if player.status == "pending" and not player.telegram_id
            ]

            logger.info(f"📋 Found {len(pending_players)} pending players without telegram_id")
            return pending_players

        except Exception as e:
            logger.error(f"❌ Unexpected error in get_pending_players_without_telegram_id: {e}")
            import traceback

            logger.debug(f"❌ Traceback: {traceback.format_exc()}")
            return []

    async def create_linking_prompt_message(self, telegram_id: str) -> str:
        """
        Create a message prompting the user to provide their phone number for linking.

        Args:
            telegram_id: Telegram user ID

        Returns:
            Formatted prompt message
        """
        # Input validation
        if not isinstance(telegram_id, str):
            logger.warning(f"⚠️ Invalid telegram_id type: {type(telegram_id)}, expected str")
            telegram_id = str(telegram_id) if telegram_id else ""
        
        # Sanitize telegram_id
        telegram_id = telegram_id.strip()
        
        pending_count = len(await self.get_pending_players_without_telegram_id())

        if pending_count == 0:
            return """👋 Welcome to KICKAI!

I don't see any pending player records that need linking. 

📞 Contact Team Leadership
You need to be added as a player by someone in the team's leadership.

💡 What to do:
1. Reach out to someone in the team's leadership chat
2. Ask them to add you as a player using the /addplayer command
3. They'll send you an invite link to join the main chat
4. Once added, you can register with your full details

💬 Need Help?
Contact the team admin in the leadership chat."""

        return """🔗 Link Your Account

I found pending player record(s) that need to be linked to your Telegram account.

📱 To link your account, please share your phone number:

**Option 1: Share Contact**
Click the "📱 Share My Phone Number" button below

**Option 2: Type Manually**
Send your phone number in international format:
Example: +447123456789

✅ Once linked, you'll have access to all team features!

💬 Need Help?
Contact the team admin in the leadership chat."""

    def _get_player_service(self):
        """Get player service instance with proper error handling."""
        try:
            from kickai.features.player_registration.domain.services.player_service import (
                PlayerService,
            )
            
            try:
                return self.container.get_service(PlayerService)
            except RuntimeError as e:
                logger.error(
                    f"❌ Player service not available for team {self.team_id}, "
                    f"operation: get_pending_players_without_telegram_id, error: {e}"
                )
                return None
            except Exception as e:
                logger.error(
                    f"❌ Unexpected error getting player service for team {self.team_id}, "
                    f"operation: get_pending_players_without_telegram_id, error: {e}"
                )
                return None
        except Exception as e:
            logger.error(
                f"❌ Error importing PlayerService for team {self.team_id}, "
                f"operation: get_pending_players_without_telegram_id, error: {e}"
            )
            return None
