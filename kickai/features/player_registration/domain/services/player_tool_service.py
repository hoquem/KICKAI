#!/usr/bin/env python3
"""
Player Tool Service

This service layer provides simplified interfaces for player tools,
extracting complex business logic from tools and providing clean, testable operations.
"""

# Standard library
import re
from dataclasses import dataclass
from typing import Any

# Third-party
from loguru import logger

# Local application
from kickai.core.dependency_container import get_container
from kickai.core.exceptions import (
    PlayerValidationError,
    ServiceNotAvailableError,
    ToolExecutionError,
    handle_error_gracefully,
)
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.constants import (
    DEFAULT_PLAYER_POSITION,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_POSITION_LENGTH,
)
from kickai.utils.tool_helpers import sanitize_input

# Constants
MAX_PLAYER_ID_LENGTH = 20
MAX_PHONE_VALIDATION_LENGTH = 20

# Message Templates
MESSAGES = {
    "PLAYER_ADDED_SUCCESS": "✅ Player Added Successfully!",
    "PLAYER_DETAILS_HEADER": "👤 Player Details:",
    "INVITE_LINK_HEADER": "🔗 Invite Link for Main Chat:",
    "NEXT_STEPS_HEADER": "📋 Next Steps:",
    "SECURITY_HEADER": "🔒 Security:",
    "NOTE_HEADER": "⚠️ Note:",
    "PLAYER_APPROVED_SUCCESS": "✅ Player Approved and Activated Successfully!",
    "PLAYER_APPROVED_DETAILS": "👤 Player Details:",
    "PLAYER_ACTIVATED": "🎉 The player is now approved, activated, and can participate in team activities.",
    "COULD_NOT_GENERATE_LINK": "Could not generate invite link",
    "CONTACT_ADMIN_LINK": "Please contact the system administrator.",
    "LINK_EXPIRES_7_DAYS": "Link expires in 7 days",
    "ONE_TIME_USE": "One-time use only",
    "AUTOMATICALLY_TRACKED": "Automatically tracked in system",
    "UNKNOWN_PLAYER": "Unknown",
    "PLAYER_NOT_FOUND": "Player not found",
    "DATABASE_QUERY_RESULT": "DATABASE QUERY RESULT: Found {} active players in team {}",
    "ACTUAL_PLAYER_NAMES": "ACTUAL PLAYER NAMES FROM DB: {}",
    "DATABASE_EMPTY": "DATABASE RETURNED: Empty list - no active players in team {}",
}

# Log Messages
LOG_MESSAGES = {
    "INVITE_SERVICE_UNAVAILABLE": "Invite service not available - cannot generate invite link",
    "TEAM_CONFIG_INCOMPLETE": "Team {} configuration incomplete - no main chat ID",
    "ERROR_CREATING_INVITE": "Error creating invite link: {}",
    "DATABASE_QUERY_RESULT": "DATABASE QUERY RESULT: Found {} active players in team {}",
    "ACTUAL_PLAYER_NAMES": "ACTUAL PLAYER NAMES FROM DB: {}",
    "DATABASE_EMPTY": "DATABASE RETURNED: Empty list - no active players in team {}",
}


@dataclass
class PlayerToolContext:
    """Context object containing validated parameters for player tool operations."""

    team_id: str
    user_id: str

    def _post_init_(self):
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

    def _post_init_(self):
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

Name: {self.full_name}
Position: {self.position}
Status: {status_emoji} {status_text}
Player ID: {self.player_id or 'Not assigned'}
Phone: {self.phone_number or 'Not provided'}"""

        if not self.is_active and self.status.lower() == "pending":
            result += (
                "\n\n⏳ Note: This player's registration is pending approval by team leadership."
            )

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
    """
    Service layer for player tool operations.

    This service extracts complex business logic from tools and provides
    clean, testable interfaces for player operations.
    """

    def __init__(self):
        self.container = get_container()

    def _get_player_service(self) -> PlayerService:
        """Get the player service with error handling."""
        player_service = self.container.get_service(PlayerService)
        if not player_service:
            raise ServiceNotAvailableError("PlayerService")
        return player_service

    def _get_team_service(self) -> TeamService:
        """Get the team service with error handling."""
        team_service = self.container.get_service(TeamService)
        if not team_service:
            raise ServiceNotAvailableError("TeamService")
        return team_service

    def _get_invite_service(self, team_id: str) -> InviteLinkService | None:
        """Get the invite link service (team-specific only)."""
        try:
            if not team_id:
                logger.error("❌ Team ID is required for invite service")
                return None

            from kickai.database.firebase_client import get_firebase_client

            database = get_firebase_client()
            return InviteLinkService(database=database, team_id=team_id)
        except Exception as e:
            logger.error(f"❌ Error creating invite service: {e}")
            return None

    async def add_player_with_invite_link(
        self, context: PlayerToolContext, request: AddPlayerRequest
    ) -> str:
        """
        Add a player and generate an invite link.

        Args:
            context: Validated context containing team_id and user_id
            request: Validated request containing player details

        Returns:
            Formatted success message with invite link or error message

        Raises:
            ServiceNotAvailableError: If required services are unavailable
            ToolExecutionError: If the operation fails
        """
        try:
            player_service = self._get_player_service()

            # Add player with simplified ID generation
            success, message = await player_service.add_player(
                request.name, request.phone, request.position, context.team_id
            )

            if not success:
                raise ToolExecutionError("add_player", f"Failed to add player: {message}")

            # Extract player ID and check if existing player
            player_id, is_existing_player = self._extract_player_info(message)

            # Generate invite link
            invite_link = await self._generate_invite_link(context.team_id, request, player_id)

            # Format response
            return self._format_add_player_response(
                request, player_id, is_existing_player, invite_link, message
            )

        except Exception as e:
            raise handle_error_gracefully(
                e, "add_player_with_invite_link", team_id=context.team_id, user_id=context.user_id
            ) from None

    def _extract_player_info(self, message: str) -> tuple[str, bool]:
        """Extract player ID and existing player status from service message."""
        # Try different patterns for player ID extraction
        player_id_match = re.search(r"ID: (\w+)", message) or re.search(
            r"Player ID: (\w+)", message
        )
        player_id = player_id_match.group(1) if player_id_match else "Unknown"

        # Check if this is an existing player
        is_existing_player = "Already Exists" in message

        return player_id, is_existing_player

    async def _generate_invite_link(
        self, team_id: str, request: AddPlayerRequest, player_id: str
    ) -> str | None:
        """Generate invite link for the player."""
        invite_service = self._get_invite_service(team_id)
        if not invite_service:
            logger.warning(LOG_MESSAGES["INVITE_SERVICE_UNAVAILABLE"])
            return None

        try:
            # Get team configuration for main chat ID
            team_service = self._get_team_service()
            team = await team_service.get_team(team_id=team_id)

            if not team or not team.main_chat_id:
                logger.warning(LOG_MESSAGES["TEAM_CONFIG_INCOMPLETE"].format(team_id))
                return None

            invite_result = await invite_service.create_player_invite_link(
                team_id=team_id,
                player_name=request.name,
                player_phone=request.phone,
                player_position=request.position,
                main_chat_id=team.main_chat_id,
                player_id=player_id,
            )

            return invite_result.get("invite_link")

        except Exception as e:
            logger.error(LOG_MESSAGES["ERROR_CREATING_INVITE"].format(e))
            return None

    def _format_add_player_response(
        self,
        request: AddPlayerRequest,
        player_id: str,
        is_existing_player: bool,
        invite_link: str | None,
        original_message: str,
    ) -> str:
        """Format the add player response message."""
        if is_existing_player:
            return self._format_existing_player_response(request, invite_link, original_message)
        else:
            return self._format_new_player_response(request, player_id, invite_link)

    def _format_existing_player_response(
        self, request: AddPlayerRequest, invite_link: str | None, original_message: str
    ) -> str:
        """Format response for existing player."""
        base_message = f"""{original_message}

{MESSAGES['INVITE_LINK_HEADER']}
{invite_link or MESSAGES['COULD_NOT_GENERATE_LINK']}

{MESSAGES['NEXT_STEPS_HEADER']}
1. Share this invite link with {request.name}
2. They can join the main chat using the link
3. Player is already registered - no need to register again
4. Contact admin if their status needs updating"""

        return self._add_security_info(base_message, invite_link)

    def _format_new_player_response(
        self, request: AddPlayerRequest, player_id: str, invite_link: str | None
    ) -> str:
        """Format response for new player."""
        base_message = f"""{MESSAGES['PLAYER_ADDED_SUCCESS']}

{MESSAGES['PLAYER_DETAILS_HEADER']}
• Name: {request.name}
• Phone: {request.phone}
• Position: {request.position}
• Player ID: {player_id}
• Status: Pending Approval

{MESSAGES['INVITE_LINK_HEADER']}
{invite_link or MESSAGES['COULD_NOT_GENERATE_LINK']}

{MESSAGES['NEXT_STEPS_HEADER']}
1. Share this invite link with {request.name}
2. They can join the main chat using the link
3. Once they join, leadership can add them with /addplayer
4. Use /approve to approve and activate their registration

💡 Tip: Leadership will add the player using /addplayer after they join the chat."""

        return self._add_security_info(base_message, invite_link)

    def _add_security_info(self, base_message: str, invite_link: str | None) -> str:
        """Add security information to the response message."""
        if invite_link:
            base_message += f"""

{MESSAGES['SECURITY_HEADER']}
• {MESSAGES['LINK_EXPIRES_7_DAYS']}
• {MESSAGES['ONE_TIME_USE']}
• {MESSAGES['AUTOMATICALLY_TRACKED']}"""
        else:
            base_message += f"""

{MESSAGES['NOTE_HEADER']} {MESSAGES['CONTACT_ADMIN_LINK']}"""

        return base_message

    async def get_player_status_by_telegram_id(
        self, context: PlayerToolContext
    ) -> PlayerStatusResponse:
        """
        Get player status by telegram ID.

        Args:
            context: Validated context containing team_id and user_id

        Returns:
            PlayerStatusResponse object

        Raises:
            ServiceNotAvailableError: If required services are unavailable
            ToolExecutionError: If player not found or operation fails
        """
        try:
            player_service = self._get_player_service()

            # Get player by telegram ID
            player = await player_service.get_player_by_telegram_id(
                context.user_id, context.team_id
            )

            if not player:
                raise ToolExecutionError(
                    "get_player_status",
                    f"Player not found for user ID {context.user_id} in team {context.team_id}",
                )

            return self._create_player_status_response(player)

        except Exception as e:
            raise handle_error_gracefully(
                e,
                "get_player_status_by_telegram_id",
                team_id=context.team_id,
                user_id=context.user_id,
            ) from None

    async def get_player_status_by_phone(
        self, context: PlayerToolContext, phone: str
    ) -> PlayerStatusResponse:
        """
        Get player status by phone number.

        Args:
            context: Validated context containing team_id and user_id
            phone: Player's phone number

        Returns:
            PlayerStatusResponse object

        Raises:
            ServiceNotAvailableError: If required services are unavailable
            ToolExecutionError: If player not found or operation fails
        """
        try:
            if not phone or not phone.strip():
                raise PlayerValidationError(["Phone number is required"])

            phone = sanitize_input(phone, max_length=MAX_PHONE_VALIDATION_LENGTH)
            player_service = self._get_player_service()

            # Get player by phone
            player = await player_service.get_player_by_phone(phone=phone, team_id=context.team_id)

            if not player:
                raise ToolExecutionError(
                    "get_player_status",
                    f"Player not found for phone {phone} in team {context.team_id}",
                )

            return self._create_player_status_response(player)

        except Exception as e:
            raise handle_error_gracefully(
                e, "get_player_status_by_phone", team_id=context.team_id, phone=phone
            ) from None

    def _create_player_status_response(self, player: Any) -> PlayerStatusResponse:
        """Create a PlayerStatusResponse from a player object."""
        return PlayerStatusResponse(
            full_name=player.name,
            position=player.position,
            status=player.status,
            player_id=player.player_id,
            phone_number=player.phone_number,
            is_active=player.status.lower() == "active",
        )

    async def get_active_players(self, context: PlayerToolContext) -> ActivePlayersResponse:
        """
        Get all active players with comprehensive anti-hallucination logging.

        Args:
            context: Validated context containing team_id and user_id

        Returns:
            ActivePlayersResponse object

        Raises:
            ServiceNotAvailableError: If required services are unavailable
            ToolExecutionError: If operation fails
        """
        try:
            player_service = self._get_player_service()

            # Get active players from database
            players = await player_service.get_active_players(context.team_id)

            # Comprehensive anti-hallucination logging
            logger.info(
                LOG_MESSAGES["DATABASE_QUERY_RESULT"].format(
                    len(players) if players else 0, context.team_id
                )
            )

            if players:
                player_names = [p.name for p in players]
                logger.info(LOG_MESSAGES["ACTUAL_PLAYER_NAMES"].format(player_names))
            else:
                logger.info(LOG_MESSAGES["DATABASE_EMPTY"].format(context.team_id))

            response = ActivePlayersResponse(players=players or [], team_id=context.team_id)

            return response

        except Exception as e:
            raise handle_error_gracefully(
                e, "get_active_players", team_id=context.team_id
            ) from None

    async def approve_player(self, context: PlayerToolContext, player_id: str) -> str:
        """
        Approve a player for team participation.

        Args:
            context: Validated context containing team_id and user_id
            player_id: The player ID to approve

        Returns:
            Formatted success message or error

        Raises:
            ServiceNotAvailableError: If required services are unavailable
            ToolExecutionError: If operation fails
        """
        try:
            if not player_id or not player_id.strip():
                raise PlayerValidationError(["Player ID is required"])

            player_id = sanitize_input(player_id, max_length=MAX_PLAYER_ID_LENGTH)
            player_service = self._get_player_service()

            # Approve player
            result = await player_service.approve_player(player_id, context.team_id)

            # Check if result indicates success (starts with ✅)
            if result.startswith("✅"):
                player_name = self._extract_player_name_from_result(result)
                return self._format_approval_success_response(player_name, player_id)
            else:
                # Result contains error message
                raise ToolExecutionError("approve_player", f"Failed to approve player: {result}")

        except Exception as e:
            raise handle_error_gracefully(
                e, "approve_player", team_id=context.team_id, player_id=player_id
            ) from None

    def _extract_player_name_from_result(self, result: str) -> str:
        """Extract player name from approval result message."""
        try:
            # More robust parsing with multiple patterns
            patterns = [
                r"Player\s+([^,\s]+)\s+approved",
                r"Player\s+([^,\s]+)\s+has been approved",
                r"([^,\s]+)\s+has been approved",
                r"Player\s+([^,\s]+)\s+is now active",
            ]

            for pattern in patterns:
                match = re.search(pattern, result)
                if match:
                    return match.group(1)

            return MESSAGES["UNKNOWN_PLAYER"]
        except (IndexError, AttributeError):
            return MESSAGES["UNKNOWN_PLAYER"]

    def _format_approval_success_response(self, player_name: str, player_id: str) -> str:
        """Format the approval success response."""
        return f"""{MESSAGES['PLAYER_APPROVED_SUCCESS']}

{MESSAGES['PLAYER_APPROVED_DETAILS']}
• Name: {player_name}
• Player ID: {player_id}
• Status: Active

{MESSAGES['PLAYER_ACTIVATED']}"""
