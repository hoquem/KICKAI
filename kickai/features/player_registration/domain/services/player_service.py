#!/usr/bin/env python3
"""
Player Service

This module provides player management functionality.
"""

# Standard library
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Local application
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.constants import (
    DEFAULT_CREATED_BY,
    DEFAULT_PLAYER_POSITION,
    DEFAULT_PLAYER_STATUS,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
    VALID_PLAYER_POSITIONS,
)

from ..entities.player import Player
from ..repositories.player_repository_interface import PlayerRepositoryInterface

# Constants
MIN_NAME_LENGTH = 2
MIN_TEAM_ID_LENGTH = 2
PLAYER_ID_PREFIX = "M"
DEFAULT_STATUS = "pending"
ACTIVE_STATUS = "active"

# Status Emojis
STATUS_EMOJIS = {
    "pending": "⏳",
    "approved": "✅",
    "active": "🟢",
    "inactive": "🔴",
    "rejected": "❌",
}

# Default Values
DEFAULT_VALUES = {
    "TEAM_NAME": "Unknown Team",
    "NOT_SET": "Not set",
    "NOT_ASSIGNED": "Not assigned",
    "UNKNOWN": "Unknown",
    "DATE_FORMAT": "%Y-%m-%d",
}

# Error Messages
ERROR_TEMPLATES = {
    "NAME_TOO_SHORT": "Player name must be at least {} characters long",
    "TEAM_ID_TOO_SHORT": "Team ID must be at least {} characters long",
    "PLAYER_NOT_FOUND": "Player with ID {} not found",
    "LEGACY_PLAYER_ID": "Legacy player_id format detected: {}. Treating as None.",
    "TELEGRAM_ID_ERROR": "Error getting player by telegram_id {}: {}",
    "PLAYER_STATUS_ERROR": "Error getting player status for {}: {}",
    "ADD_PLAYER_ERROR": "Error adding player {}: {}",
    "APPROVE_PLAYER_ERROR": "Error approving player {}: {}",
    "PLAYER_STATUS_PHONE_ERROR": "Error getting player status for phone {}: {}",
}

# Success Messages
SUCCESS_TEMPLATES = {
    "PLAYER_APPROVED": "✅ Player {} approved and activated successfully",
    "PLAYER_ALREADY_EXISTS": """✅ Player Already Exists!

📋 Name: {}
📱 Phone: {}
⚽ Position: {}
🏷️ Player ID: {}
🏢 Team: {}
📊 Status: {}

💡 This player is already registered in the system. You can use the invite link below to add them to the chat.""",
    "PLAYER_NOT_FOUND_STATUS": """❌ Player Not Found

📱 Telegram ID: {}
🏢 Team ID: {}

💡 Ask team leadership to add you as a player using /addplayer command.""",
    "PLAYER_STATUS_ERROR": "❌ Error retrieving your player status: {}",
    "NO_PLAYER_FOUND": "❌ No player found with phone {} in team {}",
    "PLAYER_STATUS_RETRIEVAL_ERROR": "❌ Error retrieving player status: {}",
}

logger = logging.getLogger(__name__)


@dataclass
class PlayerCreateParams:
    """Parameters for creating a new player."""

    name: str
    phone: str
    position: str = DEFAULT_PLAYER_POSITION
    team_id: str = ""
    created_by: str = DEFAULT_CREATED_BY


class PlayerService:
    """Service for managing players."""

    def __init__(self, player_repository: PlayerRepositoryInterface, team_service: TeamService):
        self.player_repository = player_repository
        self.team_service = team_service

    async def create_player(self, params: PlayerCreateParams) -> Player:
        """Create a new player."""
        # Validate input parameters
        self._validate_player_input(params.name, params.phone, params.position, params.team_id)

        # Generate simple player ID
        from kickai.utils.id_generator import generate_player_id

        # Get existing player IDs for collision detection
        existing_players = await self.player_repository.get_all_players(params.team_id)
        existing_ids = {player.player_id for player in existing_players if player.player_id}

        player_id = generate_player_id(params.name, params.team_id, existing_ids)

        player = Player(
            team_id=params.team_id,
            name=params.name,
            phone_number=params.phone,
            position=params.position,
            player_id=player_id,
            status=DEFAULT_STATUS,
        )
        return await self.player_repository.create_player(player)

    def _validate_player_input(self, name: str, phone: str, position: str, team_id: str) -> None:
        """Validate player input parameters."""
        if not name or not name.strip():
            raise ValueError(ERROR_MESSAGES["NAME_REQUIRED"])
        if not phone or not phone.strip():
            raise ValueError(ERROR_MESSAGES["PHONE_REQUIRED"])
        if not team_id or not team_id.strip():
            raise ValueError(ERROR_MESSAGES["TEAM_ID_REQUIRED"])

        # Validate phone number format using phonenumbers library
        from kickai.utils.phone_utils import is_valid_phone

        if not is_valid_phone(phone.strip()):
            raise ValueError(ERROR_MESSAGES["INVALID_PHONE"])

        # Validate position only if provided (not default)
        if position and position.strip() and position.lower() != DEFAULT_PLAYER_POSITION.lower():
            if position.lower() not in VALID_PLAYER_POSITIONS:
                raise ValueError(ERROR_MESSAGES["INVALID_POSITION"])

        # Validate name length
        if len(name.strip()) < MIN_NAME_LENGTH:
            raise ValueError(ERROR_TEMPLATES["NAME_TOO_SHORT"].format(MIN_NAME_LENGTH))

        # Validate team_id format (basic validation)
        if len(team_id.strip()) < MIN_TEAM_ID_LENGTH:
            raise ValueError(ERROR_TEMPLATES["TEAM_ID_TOO_SHORT"].format(MIN_TEAM_ID_LENGTH))

    async def get_player_by_id(self, player_id: str, team_id: str) -> Player | None:
        """Get a player by ID."""
        return await self.player_repository.get_player_by_id(player_id, team_id)

    async def get_player_by_phone(self, *, phone: str, team_id: str) -> Player | None:
        """Get a player by phone number."""
        return await self.player_repository.get_player_by_phone(phone, team_id)

    async def get_player_by_telegram_id(
        self, telegram_id: str | int, team_id: str
    ) -> Player | None:
        """Get a player by Telegram ID."""
        try:
            # Use the database client directly since repository might not have this method
            from kickai.core.dependency_container import get_container

            container = get_container()
            database = container.get_database()

            # Call the firebase client method directly
            player_data = await database.get_player_by_telegram_id(telegram_id, team_id)
            if player_data:
                return self._create_player_from_data(player_data)
            return None
        except Exception as e:
            logger.error(ERROR_TEMPLATES["TELEGRAM_ID_ERROR"].format(telegram_id, e))
            return None

    def _create_player_from_data(self, player_data: dict[str, Any]) -> Player:
        """Create a Player entity from database data."""
        # Handle legacy player_id formats - if it doesn't start with 'M', treat as None
        player_id = player_data.get("player_id")
        if player_id and not player_id.startswith(PLAYER_ID_PREFIX):
            logger.warning(ERROR_TEMPLATES["LEGACY_PLAYER_ID"].format(player_id))
            player_id = None

        return Player(
            team_id=player_data.get("team_id", ""),
            telegram_id=player_data.get("telegram_id"),
            player_id=player_id,  # Use cleaned player_id
            name=player_data.get("name") or player_data.get("full_name"),
            username=player_data.get("username"),
            position=player_data.get("position"),
            phone_number=player_data.get("phone_number"),
            status=player_data.get("status", DEFAULT_STATUS),
            created_at=self._parse_datetime(player_data.get("created_at")),
            updated_at=self._parse_datetime(player_data.get("updated_at")),
        )

    def _parse_datetime(self, dt_value: Any) -> datetime | None:
        """Parse datetime value handling both string and datetime objects."""
        if not dt_value:
            return None

        # If it's already a datetime object (from Firestore), return it
        if isinstance(dt_value, datetime):
            return dt_value

        # If it's a string, parse it
        if isinstance(dt_value, str):
            try:
                return datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
            except ValueError:
                return None

        return None

    async def get_players_by_team(self, *, team_id: str, status: str | None = None) -> list[Player]:
        """Get players for a team, optionally filtered by status."""
        players = await self.player_repository.get_all_players(team_id)

        if status:
            players = [player for player in players if player.status == status]

        return players

    async def get_all_players(self, team_id: str) -> list[Player]:
        """Get all players for a team (alias for get_players_by_team)."""
        return await self.get_players_by_team(team_id=team_id)

    async def get_active_players(self, team_id: str) -> list[Player]:
        """Get active players for a team."""
        return await self.get_players_by_team(team_id=team_id, status=ACTIVE_STATUS)

    async def update_player_status(self, player_id: str, status: str, team_id: str) -> Player:
        """Update a player's status."""
        player = await self.player_repository.get_player_by_id(player_id, team_id)
        if not player:
            raise ValueError(ERROR_TEMPLATES["PLAYER_NOT_FOUND"].format(player_id))

        player.status = status
        player.updated_at = datetime.now()

        return await self.player_repository.update_player(player)

    async def get_player_with_team_info(self, player_id: str, team_id: str) -> dict[str, Any]:
        """Get player information including team details."""
        player = await self.get_player_by_id(player_id, team_id)
        if not player:
            return {}

        # Get team information using team service
        team = await self.team_service.get_team_by_id(player.team_id)
        team_name = team.name if team else DEFAULT_VALUES["TEAM_NAME"]

        return {"player": player, "team_name": team_name, "team_id": player.team_id}

    async def delete_player(self, player_id: str, team_id: str) -> bool:
        """Delete a player."""
        return await self.player_repository.delete_player(player_id, team_id)

    async def get_my_status(self, user_id: str, team_id: str) -> str:
        """
        Get current user's player status and information.
        This method handles players only - team members are handled by TeamMemberService.

        Args:
            user_id: The user's Telegram ID
            team_id: The team ID

        Returns:
            User's player status and information as a formatted string
        """
        try:
            player = await self.get_player_by_telegram_id(user_id, team_id)

            if player:
                return self._format_player_status(player)

            # User not found as player
            return SUCCESS_TEMPLATES["PLAYER_NOT_FOUND_STATUS"].format(user_id, team_id)

        except Exception as e:
            logger.error(ERROR_TEMPLATES["PLAYER_STATUS_ERROR"].format(user_id, e))
            return SUCCESS_TEMPLATES["PLAYER_STATUS_ERROR"].format(e)

    def _format_player_status(self, player: Player) -> str:
        """Format player status information."""
        emoji = STATUS_EMOJIS.get(player.status, "❓")

        return f"""👤 Player Information

📋 Name: {player.name or DEFAULT_VALUES['NOT_SET']}
📱 Phone: {player.phone_number or DEFAULT_VALUES['NOT_SET']}
⚽ Position: {player.position or DEFAULT_VALUES['NOT_SET']}
🏷️ Player ID: {player.player_id or DEFAULT_VALUES['NOT_ASSIGNED']}
{emoji} Status: {player.status.title()}
🏢 Team: {player.team_id}

📅 Created: {player.created_at.strftime(DEFAULT_VALUES['DATE_FORMAT']) if player.created_at else DEFAULT_VALUES['UNKNOWN']}
🔄 Updated: {player.updated_at.strftime(DEFAULT_VALUES['DATE_FORMAT']) if player.updated_at else DEFAULT_VALUES['UNKNOWN']}"""

    # Methods needed by reminder service and other components
    async def update_player(self, player_id: str, team_id: str, **updates) -> Player:
        """Update a player with the given updates."""
        player = await self.player_repository.get_player_by_id(player_id, team_id)
        if not player:
            raise ValueError(ERROR_TEMPLATES["PLAYER_NOT_FOUND"].format(player_id))

        # Apply updates to player object
        for key, value in updates.items():
            if hasattr(player, key):
                setattr(player, key, value)

        player.updated_at = datetime.now()
        return await self.player_repository.update_player(player)

    async def add_player(
        self, name: str, phone: str, position: str | None = None, team_id: str | None = None
    ) -> tuple[bool, str]:
        """Add a new player to the team with simplified ID generation."""
        try:
            # Check if player already exists
            existing_player = await self.get_player_by_phone(phone=phone, team_id=team_id)
            if existing_player:
                return self._handle_existing_player(existing_player, name, phone, position, team_id)

            # Create new player
            return await self._create_new_player(name, phone, position, team_id)

        except Exception as e:
            logger.error(ERROR_TEMPLATES["ADD_PLAYER_ERROR"].format(name, e))
            return False, f"❌ Failed to add player: {e!s}"

    def _handle_existing_player(
        self, existing_player: Player, name: str, phone: str, position: str | None, team_id: str
    ) -> tuple[bool, str]:
        """Handle case where player already exists."""
        player_id = existing_player.player_id or DEFAULT_VALUES["NOT_ASSIGNED"]
        status_info = (
            f"Status: {existing_player.status.title()}"
            if existing_player.status
            else "Status: Unknown"
        )

        success_message = SUCCESS_TEMPLATES["PLAYER_ALREADY_EXISTS"].format(
            existing_player.name or name,
            phone,
            existing_player.position or position or DEFAULT_PLAYER_POSITION,
            player_id,
            team_id,
            status_info,
        )

        return True, success_message

    async def _create_new_player(
        self, name: str, phone: str, position: str | None, team_id: str
    ) -> tuple[bool, str]:
        """Create a new player."""
        # Get existing player IDs for collision detection
        existing_players = await self.player_repository.get_all_players(team_id)
        existing_ids = {player.player_id for player in existing_players if player.player_id}

        # Generate simple player ID using new generator
        from kickai.utils.id_generator import generate_player_id

        player_id = generate_player_id(name, team_id, existing_ids)

        # Create player parameters with the generated ID
        params = PlayerCreateParams(
            name=name,
            phone=phone,
            position=position or DEFAULT_PLAYER_POSITION,
            team_id=team_id,
            created_by=DEFAULT_CREATED_BY,
        )

        # Create the player directly with the correct ID
        await self._create_player_with_id(params, player_id)

        return True, SUCCESS_MESSAGES["PLAYER_ADDED"].format(name=name, player_id=player_id)

    async def approve_player(self, player_id: str, team_id: str) -> str:
        """Approve a player for team participation and activate them."""
        try:
            player = await self.update_player_status(player_id, ACTIVE_STATUS, team_id)
            return SUCCESS_TEMPLATES["PLAYER_APPROVED"].format(player.name)
        except Exception as e:
            logger.error(ERROR_TEMPLATES["APPROVE_PLAYER_ERROR"].format(player_id, e))
            return f"❌ Failed to approve player: {e!s}"

    async def _create_player_with_id(self, params: PlayerCreateParams, player_id: str) -> Player:
        """Create a new player with a specific ID."""
        # Validate input parameters
        self._validate_player_input(params.name, params.phone, params.position, params.team_id)

        # Create player with the provided ID
        player = Player(
            team_id=params.team_id,
            name=params.name,
            phone_number=params.phone,
            position=params.position,
            player_id=player_id,  # Use the provided ID
            status=DEFAULT_PLAYER_STATUS,
        )
        return await self.player_repository.create_player(player)

    async def get_player_status(self, phone: str, team_id: str) -> str:
        """Get player status by phone number."""
        try:
            player = await self.get_player_by_phone(phone=phone, team_id=team_id)
            if player:
                return self._format_player_status(player)
            else:
                return SUCCESS_TEMPLATES["NO_PLAYER_FOUND"].format(phone, team_id)
        except Exception as e:
            logger.error(ERROR_TEMPLATES["PLAYER_STATUS_PHONE_ERROR"].format(phone, e))
            return SUCCESS_TEMPLATES["PLAYER_STATUS_RETRIEVAL_ERROR"].format(e)
