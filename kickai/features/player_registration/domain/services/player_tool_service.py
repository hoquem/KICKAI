#!/usr/bin/env python3
"""
Player Tool Service

This service layer provides simplified interfaces for player tools,
extracting complex business logic from tools and providing clean, testable operations.
"""

from dataclasses import dataclass
from typing import Any, Optional

from loguru import logger

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
    position: Optional[str] = None

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
    player_id: Optional[str]
    phone_number: Optional[str]
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
            result += f"👤 {player.full_name}\n"
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

    def _get_invite_service(self) -> Optional[InviteLinkService]:
        """Get the invite link service (optional)."""
        return self.container.get_service(InviteLinkService)

    async def add_player_with_invite_link(
        self,
        context: PlayerToolContext,
        request: AddPlayerRequest
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
                request.name,
                request.phone,
                request.position,
                context.team_id
            )

            if not success:
                raise ToolExecutionError("add_player", f"Failed to add player: {message}")

            # Extract player ID and check if existing player
            player_id, is_existing_player = self._extract_player_info(message)

            # Generate invite link
            invite_link = await self._generate_invite_link(
                context.team_id,
                request,
                player_id
            )

            # Format response
            return self._format_add_player_response(
                request,
                player_id,
                is_existing_player,
                invite_link,
                message
            )

        except (ServiceNotAvailableError, ToolExecutionError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            # Convert unexpected errors to ToolExecutionError
            raise handle_error_gracefully(e, "add_player_with_invite_link",
                                        team_id=context.team_id, user_id=context.user_id)

    def _extract_player_info(self, message: str) -> tuple[str, bool]:
        """Extract player ID and existing player status from service message."""
        import re

        # Try different patterns for player ID extraction
        player_id_match = re.search(r"ID: (\w+)", message) or re.search(r"Player ID: (\w+)", message)
        player_id = player_id_match.group(1) if player_id_match else "Unknown"

        # Check if this is an existing player
        is_existing_player = "Already Exists" in message

        return player_id, is_existing_player

    async def _generate_invite_link(
        self,
        team_id: str,
        request: AddPlayerRequest,
        player_id: str
    ) -> Optional[str]:
        """Generate invite link for the player."""
        invite_service = self._get_invite_service()
        if not invite_service:
            logger.warning("Invite service not available - cannot generate invite link")
            return None

        try:
            # Get team configuration for main chat ID
            team_service = self._get_team_service()
            team = await team_service.get_team(team_id=team_id)

            if not team or not team.main_chat_id:
                logger.warning(f"Team {team_id} configuration incomplete - no main chat ID")
                return None

            invite_result = await invite_service.create_player_invite_link(
                team_id=team_id,
                player_name=request.name,
                player_phone=request.phone,
                player_position=request.position,
                main_chat_id=team.main_chat_id,
                player_id=player_id,
            )

            return invite_result.get('invite_link')

        except Exception as e:
            logger.error(f"Error creating invite link: {e}")
            return None

    def _format_add_player_response(
        self,
        request: AddPlayerRequest,
        player_id: str,
        is_existing_player: bool,
        invite_link: Optional[str],
        original_message: str
    ) -> str:
        """Format the add player response message."""
        if is_existing_player:
            base_message = f"""{original_message}

🔗 Invite Link for Main Chat:
{invite_link or 'Could not generate invite link'}

📋 Next Steps:
1. Share this invite link with {request.name}
2. They can join the main chat using the link
3. Player is already registered - no need to register again
4. Contact admin if their status needs updating"""
        else:
            base_message = f"""✅ Player Added Successfully!

👤 Player Details:
• Name: {request.name}
• Phone: {request.phone}
• Position: {request.position}
• Player ID: {player_id}
• Status: Pending Approval

🔗 Invite Link for Main Chat:
{invite_link or 'Could not generate invite link'}

📋 Next Steps:
1. Share this invite link with {request.name}
2. They can join the main chat using the link
3. Once they join, they can register with /register
4. Use /approve to approve and activate their registration

💡 Tip: The player will need to register with /register after joining the chat."""

        if invite_link:
            base_message += """

🔒 Security:
• Link expires in 7 days
• One-time use only
• Automatically tracked in system"""
        else:
            base_message += """

⚠️ Note: Could not generate invite link. Please contact the system administrator."""

        return base_message

    async def get_player_status_by_telegram_id(
        self,
        context: PlayerToolContext
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
                context.user_id,
                context.team_id
            )

            if not player:
                raise ToolExecutionError(
                    "get_player_status",
                    f"Player not found for user ID {context.user_id} in team {context.team_id}"
                )

            return PlayerStatusResponse(
                full_name=player.full_name,
                position=player.position,
                status=player.status,
                player_id=player.player_id,
                phone_number=player.phone_number,
                is_active=player.status.lower() == "active"
            )

        except (ServiceNotAvailableError, ToolExecutionError):
            raise
        except Exception as e:
            raise handle_error_gracefully(e, "get_player_status_by_telegram_id",
                                        team_id=context.team_id, user_id=context.user_id)

    async def get_player_status_by_phone(
        self,
        context: PlayerToolContext,
        phone: str
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

            phone = sanitize_input(phone, max_length=20)
            player_service = self._get_player_service()

            # Get player by phone
            player = await player_service.get_player_by_phone(phone, context.team_id)

            if not player:
                raise ToolExecutionError(
                    "get_player_status",
                    f"Player not found for phone {phone} in team {context.team_id}"
                )

            return PlayerStatusResponse(
                full_name=player.full_name,
                position=player.position,
                status=player.status,
                player_id=player.player_id,
                phone_number=player.phone_number,
                is_active=player.status.lower() == "active"
            )

        except (ServiceNotAvailableError, ToolExecutionError, PlayerValidationError):
            raise
        except Exception as e:
            raise handle_error_gracefully(e, "get_player_status_by_phone",
                                        team_id=context.team_id, phone=phone)

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
            logger.info(f"🔍 DATABASE QUERY RESULT: Found {len(players) if players else 0} active players in team {context.team_id}")

            if players:
                player_names = [p.full_name for p in players]
                logger.info(f"🔍 ACTUAL PLAYER NAMES FROM DB: {player_names}")
            else:
                logger.info(f"🔍 DATABASE RETURNED: Empty list - no active players in team {context.team_id}")
                logger.info("🚨 ANTI-HALLUCINATION: Returning 'no players found' - DO NOT ADD FAKE PLAYERS")

            response = ActivePlayersResponse(players=players or [], team_id=context.team_id)

            # Additional validation to prevent fake players
            if players:
                fake_player_indicators = ["Farhan Fuad", "03FF", "+447479958935", "Saim", "John Smith", "Jane Doe"]
                response_text = response.format_display()

                for fake_indicator in fake_player_indicators:
                    if fake_indicator in response_text:
                        logger.error(f"🚨 CRITICAL ERROR: Response contains fake player indicator: {fake_indicator}")
                        logger.error("🚨 THIS SHOULD NEVER HAPPEN - SERVICE IS ONLY RETURNING DATABASE DATA")
                        logger.error(f"🚨 Response: {response_text!r}")

            return response

        except ServiceNotAvailableError:
            raise
        except Exception as e:
            raise handle_error_gracefully(e, "get_active_players", team_id=context.team_id)

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

            player_id = sanitize_input(player_id, max_length=20)
            player_service = self._get_player_service()

            # Approve player
            result = await player_service.approve_player(player_id, context.team_id)

            # Check if result indicates success (starts with ✅)
            if result.startswith("✅"):
                # Extract player name from the result string
                try:
                    player_name = result.split("Player ")[1].split(" approved")[0]
                except (IndexError, AttributeError):
                    player_name = "Unknown"

                return f"""✅ Player Approved and Activated Successfully!

👤 Player Details:
• Name: {player_name}
• Player ID: {player_id}
• Status: Active

🎉 The player is now approved, activated, and can participate in team activities."""
            else:
                # Result contains error message
                raise ToolExecutionError("approve_player", f"Failed to approve player: {result}")

        except (ServiceNotAvailableError, ToolExecutionError, PlayerValidationError):
            raise
        except Exception as e:
            raise handle_error_gracefully(e, "approve_player",
                                        team_id=context.team_id, player_id=player_id)
