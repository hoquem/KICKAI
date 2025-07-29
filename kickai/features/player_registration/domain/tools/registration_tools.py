#!/usr/bin/env python3
"""
Player Registration Tools

This module provides tools for player registration operations.
Note: The register_player tool has been removed in favor of the /addplayer + invite link workflow.
"""

from kickai.utils.crewai_tool_decorator import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.utils.tool_helpers import (
    ERROR_MESSAGES,
    ServiceNotAvailableError,
    format_tool_error,
    sanitize_input,
    validate_required_input,
)

# Constants for input validation
MAX_NAME_LENGTH = 100
MAX_PHONE_LENGTH = 20
MAX_POSITION_LENGTH = 50
MAX_TEAM_ID_LENGTH = 10
MAX_USER_ID_LENGTH = 20
DEFAULT_PLAYER_POSITION = "utility"

# Note: The register_player tool has been removed as the /register command is no longer used.
# The current workflow uses /addplayer (leadership) + invite links + phone linking.

# This file is kept for potential future use but the register_player tool has been removed
# as the /register command is no longer part of the system workflow.

# The current workflow is:
# 1. Leadership uses /addplayer to create player records
# 2. Players join via invite links
# 3. Players link their phone numbers to existing records
# 4. Players use /update to modify their details


class RegisterPlayerInput(BaseModel):
    """Input model for register_player tool."""

    player_name: str
    phone_number: str
    position: str
    team_id: str


class TeamMemberRegistrationInput(BaseModel):
    """Input model for team_member_registration tool."""

    player_name: str
    phone_number: str
    position: str
    team_id: str


class RegistrationGuidanceInput(BaseModel):
    """Input model for registration_guidance tool."""

    user_id: str
    team_id: str


@tool("register_player")
def register_player(player_name: str, phone_number: str, position: str, team_id: str) -> str:
    """
    Register a new player in the main chat. Requires: player_name, phone_number, position, team_id

    Args:
        player_name: The name of the player to register
        phone_number: The player's phone number
        position: The player's position
        team_id: Team ID (required)

    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        registration_service = container.get_service(PlayerRegistrationService)

        if not registration_service:
            logger.error("❌ PlayerRegistrationService not available")
            return "❌ Registration service not available"

        # Register the player (handle async operation)
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        player = loop.run_until_complete(
            registration_service.register_player(player_name, phone_number, position, team_id)
        )

        if player:
            logger.info(f"✅ Player registered: {player_name} ({position})")
            return f"✅ Player registered successfully: {player_name} ({position})"
        else:
            logger.error(f"❌ Failed to register player: {player_name}")
            return f"❌ Failed to register player: {player_name}"

    except Exception as e:
        logger.error(f"❌ Failed to register player: {e}")
        return f"❌ Failed to register player: {e!s}"


@tool("register_team_member")
def register_team_member(player_name: str, phone_number: str, role: str, team_id: str) -> str:
    """
    Register a new team member with enhanced onboarding feedback. 
    Requires: player_name, phone_number, role, team_id

    Args:
        player_name: The name of the team member to register
        phone_number: The team member's phone number
        role: The team member's role (coach, manager, assistant, coordinator, volunteer, admin)
        team_id: Team ID (required)

    Returns:
        Enhanced confirmation message with next steps
    """
    try:
        container = get_container()
        registration_service = container.get_service(PlayerRegistrationService)

        if not registration_service:
            logger.error("❌ PlayerRegistrationService not available")
            return "❌ Registration service not available. Please try again later."

        # Register the team member (using the same service but with role instead of position)
        member = registration_service.register_player(player_name, phone_number, role, team_id)

        if member:
            logger.info(f"✅ Team member registered: {player_name} ({role})")
            
            # Enhanced success message for onboarding
            success_msg = f"""
🎉 **TEAM MEMBER REGISTERED!**

✅ **Details:**
• **Name:** {player_name}
• **Role:** {role.title()}
• **Status:** Active

🚀 **Next Steps:**
• Access administrative features immediately
• Join leadership chat for team coordination
• Contact existing leadership for orientation

Welcome to the team! 🤝
            """
            return success_msg.strip()
        else:
            logger.error(f"❌ Failed to register team member: {player_name}")
            return f"❌ Registration failed for {player_name}. Please verify the information and try again."

    except Exception as e:
        logger.error(f"❌ Failed to register team member: {e}")
        return f"❌ Registration failed: {e!s}\n\nPlease check your information and try again."


@tool("team_member_registration")
def team_member_registration(
    player_name: str, phone_number: str, position: str, team_id: str, user_id: str = None
) -> str:
    """
    Register a new team member. Requires: player_name, phone_number, position, team_id

    Args:
        player_name: The name of the player to register
        phone_number: The player's phone number
        position: The player's position (will be used as role for team member)
        team_id: The team ID to register the player for
        user_id: Optional user ID (telegram_id), defaults to phone_number if not provided

    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        from kickai.features.team_administration.domain.services.team_service import TeamService

        team_service = container.get_service(TeamService)

        if not team_service:
            logger.error("❌ TeamService not available")
            return "❌ Team service not available"

        # Use user_id if provided, otherwise use phone_number as fallback
        actual_user_id = user_id if user_id else phone_number

        # Register the team member using TeamService (run async operation synchronously)
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        team_member = loop.run_until_complete(
            team_service.add_team_member(
                team_id=team_id,
                user_id=actual_user_id,
                role=position,  # Use position as role
                name=player_name,
                phone=phone_number,
            )
        )

        if team_member:
            logger.info(f"✅ Team member registered: {player_name} for team {team_id}")
            return f"✅ Team member registered successfully: {player_name} for team {team_id}"
        else:
            logger.error(f"❌ Failed to register team member: {player_name}")
            return f"❌ Failed to register team member: {player_name}"

    except Exception as e:
        logger.error(f"❌ Failed to register team member: {e}")
        return f"❌ Failed to register team member: {e!s}"


@tool("registration_guidance")
def registration_guidance(user_id: str, team_id: str) -> str:
    """
    Provide registration guidance to a user. Requires: user_id, team_id

    Args:
        user_id: The user ID to provide guidance to
        team_id: Team ID (required)

    Returns:
        Registration guidance message
    """
    try:
        container = get_container()
        registration_service = container.get_service(PlayerRegistrationService)

        if not registration_service:
            logger.error("❌ PlayerRegistrationService not available")
            return "❌ Registration service not available"

        # Get registration guidance
        guidance = registration_service.get_registration_guidance(user_id, team_id)

        logger.info(f"✅ Registration guidance provided to user {user_id}")
        return guidance

    except Exception as e:
        logger.error(f"❌ Failed to provide registration guidance: {e}")
        return f"❌ Failed to provide registration guidance: {e!s}"
