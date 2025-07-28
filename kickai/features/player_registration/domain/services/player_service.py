#!/usr/bin/env python3
"""
Player Service

This module provides player management functionality.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.constants import (DEFAULT_CREATED_BY,
    DEFAULT_PLAYER_POSITION,
    DEFAULT_PLAYER_STATUS,
    ERROR_MESSAGES,
    PHONE_PATTERN,
    SUCCESS_MESSAGES,
    VALID_PLAYER_POSITIONS,
)

from ..entities.player import Player
from ..repositories.player_repository_interface import PlayerRepositoryInterface

logger = logging.getLogger(__name__)


@dataclass
class PlayerCreateParams:
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

        # Generate user_id from phone number as a fallback
        import hashlib

        # Create a user_id from phone number if no telegram_id available
        phone_hash = hashlib.md5(params.phone.encode()).hexdigest()[:8]
        user_id = f"user_{phone_hash}"

        # Generate football-specific player ID
        from kickai.utils.football_id_generator import generate_football_player_id

        # Parse name into first and last name
        name_parts = params.name.strip().split()
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = name_parts[-1] if len(name_parts) > 1 else "Player"

        # Get existing player IDs for collision detection
        existing_players = await self.player_repository.get_all_players(params.team_id)
        existing_ids = {player.player_id for player in existing_players if player.player_id}

        player_id = generate_football_player_id(
            first_name=first_name,
            last_name=last_name,
            position=params.position,
            team_id=params.team_id,
            existing_ids=existing_ids,
        )

        player = Player(
            user_id=user_id,
            team_id=params.team_id,
            full_name=params.name,
            phone_number=params.phone,
            position=params.position,
            player_id=player_id,
            status="pending",
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

        # Validate phone number format (improved validation)
        import re

        if not re.match(PHONE_PATTERN, phone.strip()):
            raise ValueError(ERROR_MESSAGES["INVALID_PHONE"])

        # Validate position only if provided (not default)
        if position and position.strip() and position.lower() != DEFAULT_PLAYER_POSITION.lower():
            if position.lower() not in VALID_PLAYER_POSITIONS:
                raise ValueError(ERROR_MESSAGES["INVALID_POSITION"])

        # Validate name length
        if len(name.strip()) < 2:
            raise ValueError("Player name must be at least 2 characters long")

        # Validate team_id format (basic validation)
        if len(team_id.strip()) < 2:
            raise ValueError("Team ID must be at least 2 characters long")

    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        """Get a player by ID."""
        return await self.player_repository.get_player_by_id(player_id, team_id)

    async def get_player_by_phone(self, *, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number."""
        return await self.player_repository.get_player_by_phone(phone, team_id)

    async def get_player_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[Player]:
        """Get a player by Telegram ID."""
        try:
            # Use the database client directly since repository might not have this method
            from kickai.core.dependency_container import get_container

            container = get_container()
            database = container.get_database()

            # Call the firebase client method directly
            player_data = await database.get_player_by_telegram_id(telegram_id, team_id)
            if player_data:
                # Convert to Player entity
                from datetime import datetime

                from ..entities.player import Player

                return Player(
                    user_id=player_data.get("user_id", ""),
                    team_id=player_data.get("team_id", ""),
                    telegram_id=player_data.get("telegram_id"),
                    player_id=player_data.get("player_id"),
                    first_name=player_data.get("first_name"),
                    last_name=player_data.get("last_name"),
                    full_name=player_data.get("full_name"),
                    username=player_data.get("username"),
                    position=player_data.get("position"),
                    phone_number=player_data.get("phone_number"),
                    status=player_data.get("status", "pending"),
                    created_at=datetime.fromisoformat(player_data["created_at"])
                    if player_data.get("created_at")
                    else None,
                    updated_at=datetime.fromisoformat(player_data["updated_at"])
                    if player_data.get("updated_at")
                    else None,
                )
            return None
        except Exception as e:
            logger.error(f"Error getting player by telegram_id {telegram_id}: {e}")
            return None

    async def get_players_by_team(self, *, team_id: str, status: Optional[str] = None) -> List[Player]:
        """Get players for a team, optionally filtered by status."""
        players = await self.player_repository.get_all_players(team_id)

        if status:
            players = [player for player in players if player.status == status]

        return players

    async def get_all_players(self, team_id: str) -> List[Player]:
        """Get all players for a team (alias for get_players_by_team)."""
        return await self.get_players_by_team(team_id=team_id)

    async def get_active_players(self, team_id: str) -> List[Player]:
        """Get active players for a team."""
        return await self.get_players_by_team(team_id=team_id, status="active")

    async def update_player_status(self, player_id: str, status: str, team_id: str) -> Player:
        """Update a player's status."""
        player = await self.player_repository.get_player_by_id(player_id, team_id)
        if not player:
            raise ValueError(f"Player with ID {player_id} not found")

        player.status = status
        player.updated_at = datetime.now()

        return await self.player_repository.update_player(player)

    async def get_player_with_team_info(self, player_id: str, team_id: str) -> Dict[str, Any]:
        """Get player information including team details."""
        player = await self.get_player_by_id(player_id, team_id)
        if not player:
            return {}

        # Get team information using team service
        team = await self.team_service.get_team_by_id(player.team_id)
        team_name = team.name if team else "Unknown Team"

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
            return f"""❌ Player Not Found

🔍 User ID: {user_id}
🏢 Team ID: {team_id}

💡 You may need to register as a player using /register command."""

        except Exception as e:
            logger.error(f"Error getting player status for {user_id}: {e}")
            return f"❌ Error retrieving your player status: {e!s}"

    def _format_player_status(self, player: Player) -> str:
        """Format player status information."""
        status_emoji = {
            "pending": "⏳",
            "approved": "✅",
            "active": "🟢",
            "inactive": "🔴",
            "rejected": "❌",
        }

        emoji = status_emoji.get(player.status, "❓")

        return f"""👤 Player Information

📋 Name: {player.full_name or player.first_name or 'Not set'}
📱 Phone: {player.phone_number or 'Not set'}
⚽ Position: {player.position or 'Not set'}
🏷️ Player ID: {player.player_id or 'Not assigned'}
{emoji} Status: {player.status.title()}
🏢 Team: {player.team_id}

📅 Created: {player.created_at.strftime('%Y-%m-%d') if player.created_at else 'Unknown'}
🔄 Updated: {player.updated_at.strftime('%Y-%m-%d') if player.updated_at else 'Unknown'}"""

    # Methods needed by reminder service and other components
    async def update_player(self, player_id: str, team_id: str, **updates) -> Player:
        """Update a player with the given updates."""
        player = await self.player_repository.get_player_by_id(player_id, team_id)
        if not player:
            raise ValueError(f"Player with ID {player_id} not found")

        # Apply updates to player object
        for key, value in updates.items():
            if hasattr(player, key):
                setattr(player, key, value)

        player.updated_at = datetime.now()
        return await self.player_repository.update_player(player)

    async def add_player(
        self, name: str, phone: str, position: Optional[str] = None, team_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """Add a new player to the team with simplified ID generation."""
        try:
            # Check if player already exists
            existing_player = await self.get_player_by_phone(phone=phone, team_id=team_id)
            if existing_player:
                # Player already exists - return success with existing player info and invite link
                player_id = existing_player.player_id or "Unknown"
                status_info = f"Status: {existing_player.status.title()}" if existing_player.status else "Status: Unknown"
                
                success_message = f"""✅ Player Already Exists!

📋 Name: {existing_player.full_name or name}
📱 Phone: {phone}
⚽ Position: {existing_player.position or position or DEFAULT_PLAYER_POSITION}  
🏷️ Player ID: {player_id}
🏢 Team: {team_id}
📊 {status_info}

💡 This player is already registered in the system. You can use the invite link below to add them to the chat."""
                
                return True, success_message

            # Get existing player IDs for collision detection
            existing_players = await self.player_repository.get_all_players(team_id)
            existing_ids = {player.player_id for player in existing_players if player.player_id}

            # Generate simple player ID using new generator
            from kickai.utils.simple_id_generator import generate_simple_player_id

            player_id = generate_simple_player_id(name, team_id, existing_ids)

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
        except Exception as e:
            logger.error(f"Error adding player {name}: {e}")
            return False, f"❌ Failed to add player: {e!s}"

    async def approve_player(self, player_id: str, team_id: str) -> str:
        """Approve a player for team participation and activate them."""
        try:
            player = await self.update_player_status(player_id, "active", team_id)
            return f"✅ Player {player.full_name} approved and activated successfully"
        except Exception as e:
            logger.error(f"Error approving player {player_id}: {e}")
            return f"❌ Failed to approve player: {e!s}"

    async def _create_player_with_id(self, params: PlayerCreateParams, player_id: str) -> Player:
        """Create a new player with a specific ID."""
        # Validate input parameters
        self._validate_player_input(params.name, params.phone, params.position, params.team_id)

        # Generate user_id from phone number as a fallback
        import hashlib

        phone_hash = hashlib.md5(params.phone.encode()).hexdigest()[:8]
        user_id = f"user_{phone_hash}"

        # Create player with the provided ID
        player = Player(
            user_id=user_id,
            team_id=params.team_id,
            full_name=params.name,
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
                return f"❌ No player found with phone {phone} in team {team_id}"
        except Exception as e:
            logger.error(f"Error getting player status for phone {phone}: {e}")
            return f"❌ Error retrieving player status: {e!s}"
