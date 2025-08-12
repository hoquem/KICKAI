#!/usr/bin/env python3
"""
Player Tool Service

This service layer provides simplified interfaces for player tools,
extracting complex business logic from tools and providing clean, testable operations.
"""

from dataclasses import dataclass
from typing import Any

from loguru import logger

from kickai.core.exceptions import (
    PlayerValidationError,
)
from kickai.core.interfaces.player_repositories import IPlayerRepository
from kickai.core.value_objects.entity_context import EntityContext
from kickai.utils.constants import (
    DEFAULT_PLAYER_POSITION,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_POSITION_LENGTH,
)
from kickai.utils.tool_helpers import sanitize_input


@dataclass
class PlayerToolContext:
    """Context object containing validated parameters for player tool operations."""
    team_id: str
    user_id: str

    def __post_init__(self):
        """Validate context after initialization."""
        if not self.team_id or not self.team_id.strip():
            raise PlayerValidationError(["Team ID is required"])
        if not self.user_id or not self.user_id.strip():
            raise PlayerValidationError(["User ID is required"])


@dataclass
class AddPlayerRequest:
    """Request object for adding a player."""
    name: str
    phone: str
    position: str | None = None

    def __post_init__(self):
        """Validate and sanitize the request after initialization."""
        if not self.name or not self.name.strip():
            raise PlayerValidationError(["Player name is required"])
        if not self.phone or not self.phone.strip():
            raise PlayerValidationError(["Player phone number is required"])

        # Sanitize inputs
        self.name = sanitize_input(self.name, max_length=MAX_NAME_LENGTH)
        self.phone = sanitize_input(self.phone, max_length=MAX_PHONE_LENGTH)
        self.position = (
            sanitize_input(self.position, max_length=MAX_POSITION_LENGTH)
            if self.position
            else DEFAULT_PLAYER_POSITION
        )


@dataclass
class PlayerStatusResponse:
    """Response object for player status queries."""
    full_name: str
    position: str
    status: str
    player_id: str | None
    phone_number: str | None
    is_active: bool

    def format_display(self) -> str:
        """Format the player status for display."""
        status_emoji = "✅" if self.is_active else "⏳"
        status_text = self.status.title()

        result = f"""👤 Player Information

Name: {self.name}
Position: {self.position}
Status: {status_emoji} {status_text}
Player ID: {self.player_id or 'Not assigned'}
Phone: {self.phone_number or 'Not provided'}"""

        if not self.is_active and self.status.lower() == "pending":
            result += "\n\n⏳ Note: This player's registration is pending approval by team leadership."

        return result


@dataclass
class ActivePlayersResponse:
    """Response object for active players query."""
    players: list[Any]
    team_id: str

    def format_display(self) -> str:
        """Format the active players list for display."""
        if not self.players:
            return "📋 No active players found in the team."

        result = "✅ Active Players in Team\n\n"

        for player in self.players:
            result += f"👤 {player.name}\n"
            result += f"   • Position: {player.position}\n"
            result += f"   • Player ID: {player.player_id or 'Not assigned'}\n"
            result += f"   • Phone: {player.phone_number or 'Not provided'}\n\n"

        return result


class PlayerToolService:
    """Service for player-related tool operations."""

    def __init__(self, player_repository: IPlayerRepository):
        self.player_repository = player_repository
        self.logger = logger

    async def get_player_status(self, context: EntityContext) -> dict[str, Any]:
        """
        Get player status for a user.


            context: User context with telegram_id and team_id


    :return: Dictionary with player status information
    :rtype: str  # TODO: Fix type
        """
        try:
            if not self._validate_context(context):
                return {
                    "success": False,
                    "message": "❌ Invalid context provided.",
                    "error": "Context validation failed",
                }

            # Get player by telegram_id
            player = await self.player_repository.get_by_telegram_id(
                team_id=context.team_id.value, telegram_id=context.telegram_id.value
            )

            if not player:
                return {
                    "success": False,
                    "message": "❌ You are not registered as a player in this team.",
                    "error": "Player not found",
                }

            return {
                "success": True,
                "message": "✅ Player status retrieved successfully!",
                "player": {
                    "name": player.name,
                    "position": player.position,
                    "status": player.status,
                    "phone_number": player.phone_number,
                    "email": player.email,
                    "is_active": player.is_active,
                    "is_approved": player.is_approved,
                },
            }

        except Exception as e:
            self.logger.error(f"Error getting player status: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while getting player status.",
                "error": str(e),
            }

    async def update_player_info(self, context: EntityContext, field: str, value: str) -> dict[str, Any]:
        """
        Update player information.


            context: User context with telegram_id and team_id
            field: Field to update
            value: New value


    :return: Dictionary with update result
    :rtype: str  # TODO: Fix type
        """
        try:
            if not self._validate_context(context):
                return {
                    "success": False,
                    "message": "❌ Invalid context provided.",
                    "error": "Context validation failed",
                }

            # Get player by telegram_id
            player = await self.player_repository.get_by_telegram_id(
                team_id=context.team_id.value, telegram_id=context.telegram_id.value
            )

            if not player:
                return {
                    "success": False,
                    "message": "❌ You are not registered as a player in this team.",
                    "error": "Player not found",
                }

            # Validate field is updatable
            if not self._is_field_updatable(field):
                return {
                    "success": False,
                    "message": f"❌ Field '{field}' cannot be updated.",
                    "error": "Invalid field",
                }

            # Update the player
            updated_player = await self.player_repository.update_player(
                player_id=player.player_id,
                team_id=context.team_id.value,
                telegram_id=context.telegram_id.value,
                updates={field: value},
            )

            if updated_player:
                return {
                    "success": True,
                    "message": "✅ Player information updated successfully!",
                    "updated_field": field,
                    "new_value": value,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Failed to update player information.",
                    "error": "Update failed",
                }

        except Exception as e:
            self.logger.error(f"Error updating player info: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while updating player information.",
                "error": str(e),
            }

    async def get_player_list(self, context: EntityContext) -> dict[str, Any]:
        """
        Get list of all players in the team.


            context: User context with telegram_id and team_id


    :return: Dictionary with player list
    :rtype: str  # TODO: Fix type
        """
        try:
            if not self._validate_context(context):
                return {
                    "success": False,
                    "message": "❌ Invalid context provided.",
                    "error": "Context validation failed",
                }

            # Get all players for the team
            players = await self.player_repository.get_all_players(context.team_id.value)

            if not players:
                return {
                    "success": True,
                    "message": "📋 No players found in this team.",
                    "players": [],
                    "count": 0,
                }

            # Format player list
            player_list = []
            for player in players:
                player_list.append({
                    "name": player.name,
                    "position": player.position,
                    "status": player.status,
                    "is_active": player.is_active,
                })

            return {
                "success": True,
                "message": f"📋 Found {len(player_list)} players in the team.",
                "players": player_list,
                "count": len(player_list),
            }

        except Exception as e:
            self.logger.error(f"Error getting player list: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while getting player list.",
                "error": str(e),
            }

    async def get_player_by_telegram_id(self, context: EntityContext) -> dict[str, Any]:
        """
        Get player information by Telegram ID.


            context: User context with telegram_id and team_id


    :return: Dictionary with player information
    :rtype: str  # TODO: Fix type
        """
        try:
            if not self._validate_context(context):
                return {
                    "success": False,
                    "message": "❌ Invalid context provided.",
                    "error": "Context validation failed",
                }

            # Get player by telegram_id
            player = await self.player_repository.get_by_telegram_id(
                context.team_id.value, context.telegram_id.value
            )

            if not player:
                return {
                    "success": False,
                    "message": f"Player not found for Telegram ID {context.telegram_id.value} in team {context.team_id.value}",
                    "error": "Player not found",
                }

            return {
                "success": True,
                "message": "✅ Player information retrieved successfully!",
                "player": {
                    "name": player.name,
                    "position": player.position,
                    "status": player.status,
                    "phone_number": player.phone_number,
                    "email": player.email,
                    "is_active": player.is_active,
                    "is_approved": player.is_approved,
                },
            }

        except Exception as e:
            self.logger.error(f"Error getting player by telegram_id: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while getting player information.",
                "error": str(e),
            }

    async def approve_player(self, context: EntityContext, player_telegram_id: str) -> dict[str, Any]:
        """
        Approve a player (admin only).


            context: User context with telegram_id and team_id
            player_telegram_id: Telegram ID of player to approve


    :return: Dictionary with approval result
    :rtype: str  # TODO: Fix type
        """
        try:
            if not self._validate_context(context):
                return {
                    "success": False,
                    "message": "❌ Invalid context provided.",
                    "error": "Context validation failed",
                }

            # Get player to approve
            player = await self.player_repository.get_by_telegram_id(
                context.team_id.value, player_telegram_id
            )

            if not player:
                return {
                    "success": False,
                    "message": f"Player not found for Telegram ID {player_telegram_id}",
                    "error": "Player not found",
                }

            # Approve the player
            approved_player = await self.player_repository.approve_player(
                player_id=player.player_id,
                team_id=context.team_id.value,
                telegram_id=player_telegram_id,
            )

            if approved_player:
                return {
                    "success": True,
                    "message": f"✅ Player {player.name} approved successfully!",
                    "player_name": player.name,
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Failed to approve player.",
                    "error": "Approval failed",
                }

        except Exception as e:
            self.logger.error(f"Error approving player: {e}")
            return {
                "success": False,
                "message": "❌ An error occurred while approving player.",
                "error": str(e),
            }

    def _validate_context(self, context: EntityContext) -> bool:
        """Validate that context has required fields."""
        if not context or not context.telegram_id or not context.team_id:
            return False
        return True

    def _is_field_updatable(self, field: str) -> bool:
        """Check if a field can be updated."""
        updatable_fields = {
            "name",
            "phone_number",
            "email",
            "position",
            "preferred_foot",
            "jersey_number",
            "emergency_contact",
            "medical_notes",
        }
        return field in updatable_fields
