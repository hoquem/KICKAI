#!/usr/bin/env python3
"""
Player Tools

This module provides tools for player management operations.
"""
from typing import Optional



from kickai.utils.crewai_tool_decorator import tool
from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import (
    ServiceNotAvailableError, 
    PlayerValidationError, 
    ToolExecutionError,
    KickAIError
)
from kickai.features.player_registration.domain.services.player_tool_service import (
    PlayerToolService,
    PlayerToolContext,
    AddPlayerRequest
)
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.utils.constants import (
    DEFAULT_PLAYER_POSITION,
    ERROR_MESSAGES,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_POSITION_LENGTH,
    MAX_TEAM_ID_LENGTH,
    MAX_USER_ID_LENGTH,
)
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    sanitize_input,
    validate_required_input,
)


class AddPlayerInput(BaseModel):
    """Input model for add_player tool."""

    name: str
    phone: str
    position: str
    team_id: str


class ApprovePlayerInput(BaseModel):
    """Input model for approve_player tool."""

    player_id: str
    team_id: str


class GetPlayerStatusInput(BaseModel):
    """Input model for get_player_status tool."""

    player_id: str
    team_id: str


class GetMatchInput(BaseModel):
    """Input model for get_match tool."""

    match_id: str
    team_id: str


@tool("add_player")
async def add_player(
    team_id: str, user_id: str, name: str, phone: str, position: Optional[str] = None
) -> str:
    """
    Add a new player to the team with simplified ID generation.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        name: Player's full name
        phone: Player's phone number
        position: Player's position (optional, can be set later)

    Returns:
        Success message with invite link or error
    """
    try:
        # Validate and sanitize inputs through service layer
        context = PlayerToolContext(
            team_id=sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH),
            user_id=sanitize_input(user_id, max_length=MAX_USER_ID_LENGTH)
        )
        
        request = AddPlayerRequest(
            name=name,
            phone=phone,
            position=position
        )
        
        # Use service layer for business logic
        tool_service = PlayerToolService()
        return await tool_service.add_player_with_invite_link(context, request)
        
    except (PlayerValidationError, ServiceNotAvailableError, ToolExecutionError) as e:
        logger.error(f"Player tool error in add_player: {e}")
        return format_tool_error(str(e.user_message if hasattr(e, 'user_message') else e))
    except Exception as e:
        logger.error(f"Unexpected error in add_player: {e}", exc_info=True)
        return format_tool_error(f"Failed to add player: {e}")


@tool("approve_player")
async def approve_player(team_id: str, user_id: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        player_id: The player ID to approve

    Returns:
        Success message or error
    """
    try:
        # Validate and sanitize inputs through service layer
        context = PlayerToolContext(
            team_id=sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH),
            user_id=sanitize_input(user_id, max_length=MAX_USER_ID_LENGTH)
        )
        
        # Use service layer for business logic
        tool_service = PlayerToolService()
        return await tool_service.approve_player(context, player_id)
        
    except (PlayerValidationError, ServiceNotAvailableError, ToolExecutionError) as e:
        logger.error(f"Player tool error in approve_player: {e}")
        return format_tool_error(str(e.user_message if hasattr(e, 'user_message') else e))
    except Exception as e:
        logger.error(f"Unexpected error in approve_player: {e}", exc_info=True)
        return format_tool_error(f"Failed to approve player: {e}")


@tool("get_my_status")
async def get_my_status(team_id: str, user_id: str) -> str:
    """
    Get the current status of the requesting user.

    This tool requires team_id and user_id parameters which should be provided from the available context.

    Args:
        team_id: Team ID from the available context parameters
        user_id: User ID (telegram user ID) from the available context parameters

    Returns:
        User's current status or error message

    Example:
        If context provides "team_id: TEST, user_id: 12345",
        call this tool with team_id="TEST" and user_id="12345"
    """
    try:
        # Validate and sanitize inputs through service layer
        context = PlayerToolContext(
            team_id=sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH),
            user_id=sanitize_input(user_id, max_length=MAX_USER_ID_LENGTH)
        )
        
        # Use service layer for business logic
        tool_service = PlayerToolService()
        status_response = await tool_service.get_player_status_by_telegram_id(context)
        return status_response.format_display()
        
    except (PlayerValidationError, ServiceNotAvailableError, ToolExecutionError) as e:
        logger.error(f"Player tool error in get_my_status: {e}")
        return format_tool_error(str(e.user_message if hasattr(e, 'user_message') else e))
    except Exception as e:
        logger.error(f"Unexpected error in get_my_status: {e}", exc_info=True)
        return format_tool_error(f"Failed to get player status: {e}")


@tool("get_player_status")
async def get_player_status(team_id: str, user_id: str, phone: str) -> str:
    """
    Get player status by phone number.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        phone: The player's phone number

    Returns:
        Player status or error message
    """
    try:
        # Validate and sanitize inputs through service layer
        context = PlayerToolContext(
            team_id=sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH),
            user_id=sanitize_input(user_id, max_length=MAX_USER_ID_LENGTH)
        )
        
        # Use service layer for business logic
        tool_service = PlayerToolService()
        status_response = await tool_service.get_player_status_by_phone(context, phone)
        return status_response.format_display()
        
    except (PlayerValidationError, ServiceNotAvailableError, ToolExecutionError) as e:
        logger.error(f"Player tool error in get_player_status: {e}")
        return format_tool_error(str(e.user_message if hasattr(e, 'user_message') else e))
    except Exception as e:
        logger.error(f"Unexpected error in get_player_status: {e}", exc_info=True)
        return format_tool_error(f"Failed to get player status: {e}")


@tool("get_all_players")
async def get_all_players(team_id: str, user_id: str) -> str:
    """
    Get all players in the team.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context

    Returns:
        List of all players or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get all players
        players = await player_service.get_all_players(team_id)

        if not players:
            return "📋 No players found in the team."

        # Format response
        result = "📋 All Players in Team\n\n"

        for player in players:
            status_emoji = "✅" if player.status.lower() == "active" else "⏳"
            result += f"{status_emoji} **{player.full_name}**\n"
            result += f"   • Position: {player.position}\n"
            result += f"   • Status: {player.status.title()}\n"
            result += f"   • Player ID: {player.player_id or 'Not assigned'}\n"
            result += f"   • Phone: {player.phone_number or 'Not provided'}\n\n"

        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_all_players: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get all players: {e}", exc_info=True)
        return format_tool_error(f"Failed to get all players: {e}")


@tool("get_active_players")
async def get_active_players(team_id: str, user_id: str) -> str:
    """
    Get all active players in the team.

    🚨 CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:
    - This tool queries the ACTUAL DATABASE for active players
    - If the database returns NO players, return "No active players found" - DO NOT INVENT PLAYERS
    - DO NOT add fake players like "John Smith", "Saim", or any other fictional names
    - The agent MUST return this tool's output EXACTLY as received - NO additions, NO modifications
    - NEVER create imaginary player data if the database is empty

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context

    Returns:
        EXACT database results - List of active players or "No active players found" message
    """
    try:
        # Validate and sanitize inputs through service layer
        context = PlayerToolContext(
            team_id=sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH),
            user_id=sanitize_input(user_id, max_length=MAX_USER_ID_LENGTH)
        )
        
        # Use service layer for business logic (includes comprehensive anti-hallucination logging)
        tool_service = PlayerToolService()
        active_players_response = await tool_service.get_active_players(context)
        
        # Get formatted result from service
        result = active_players_response.format_display()
        
        # 🚨 CRITICAL: This exact output must be returned by the agent without any modifications
        logger.info(f"🚨 FINAL TOOL OUTPUT (EXACT): {result!r}")
        logger.info(f"🚨 AGENT MUST RETURN THIS EXACTLY - NO FAKE PLAYERS ALLOWED")
        
        return result
        
    except (PlayerValidationError, ServiceNotAvailableError, ToolExecutionError) as e:
        logger.error(f"Player tool error in get_active_players: {e}")
        return format_tool_error(str(e.user_message if hasattr(e, 'user_message') else e))
    except Exception as e:
        logger.error(f"Unexpected error in get_active_players: {e}", exc_info=True)
        return format_tool_error(f"Failed to get active players: {e}")


@tool("validate_tool_output_integrity")
def validate_tool_output_integrity(original_output: str, agent_response: str) -> bool:
    """
    Validate that the agent response maintains the integrity of the original tool output.
    
    Args:
        original_output: The original output from the tool
        agent_response: The agent's response that should preserve tool output
        
    Returns:
        True if integrity is maintained, False otherwise
    """
    try:
        # Check if the agent response contains the essential information from the original output
        original_lower = original_output.lower()
        response_lower = agent_response.lower()
        
        # Extract key information patterns from original output
        key_patterns = []
        
        # Look for success indicators
        if "✅" in original_output or "success" in original_lower:
            key_patterns.append("success")
            
        # Look for error indicators
        if "❌" in original_output or "error" in original_lower or "failed" in original_lower:
            key_patterns.append("error")
            
        # Look for specific data patterns (names, IDs, etc.)
        import re
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        id_pattern = r'\b[A-Z]{2,5}\b'
        
        names = re.findall(name_pattern, original_output)
        ids = re.findall(id_pattern, original_output)
        
        key_patterns.extend(names)
        key_patterns.extend(ids)
        
        # Check if response contains key patterns
        integrity_maintained = True
        for pattern in key_patterns:
            if pattern.lower() not in response_lower:
                integrity_maintained = False
                break
                
        return integrity_maintained
        
    except Exception as e:
        logger.error(f"❌ Error validating tool output integrity: {e}")
        return False


@tool("get_pending_players")
async def get_pending_players(team_id: str, user_id: str) -> str:
    """
    Get all pending players awaiting approval in the team.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context

    Returns:
        List of pending players or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get pending players using the service
        from kickai.features.player_registration.domain.services.player_registration_service import (
            PlayerRegistrationService,
        )
        
        registration_service = PlayerRegistrationService()
        pending_players = await registration_service.get_pending_players(team_id=team_id)

        if not pending_players:
            return "📋 No pending players found in the team."

        # Format response
        result = "📋 Pending Players Awaiting Approval\n\n"

        for player in pending_players:
            result += f"⏳ **{player.full_name}**\n"
            result += f"   • Player ID: {player.player_id or 'Not assigned'}\n"
            result += f"   • Position: {player.position}\n"
            result += f"   • Phone: {player.phone_number or 'Not provided'}\n"
            result += f"   • Status: {player.status.title()}\n"
            if player.created_at:
                result += f"   • Registered: {player.created_at}\n"
            result += "\n"

        result += "💡 To approve a player, use: `/approve [player_id]`\n"
        result += "💡 To reject a player, use: `/reject [player_id] [reason]`"

        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_pending_players: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get pending players: {e}", exc_info=True)
        return format_tool_error(f"Failed to get pending players: {e}")


@tool("get_match")
async def get_match(match_id: str, team_id: str) -> str:
    """
    Get match details by match ID. Requires: match_id, team_id

    Args:
        match_id: The match ID to retrieve
        team_id: Team ID (required)

    Returns:
        Match details or error message
    """
    try:
        # Handle JSON string input using utility functions
        match_id = extract_single_value(match_id, "match_id")
        team_id = extract_single_value(team_id, "team_id")

        # Validate inputs using utility functions
        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        match_id = sanitize_input(match_id, max_length=20)
        team_id = sanitize_input(team_id, max_length=20)

        # Get services from container
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            raise ServiceNotAvailableError("MatchService")

        # Get match details
        match = await match_service.get_match(match_id, team_id)

        if not match:
            return format_tool_error(f"Match {match_id} not found in team {team_id}")

        # Format match details
        return f"""📋 Match Details

🏆 Match ID: {match.get('match_id', 'N/A')}
📅 Date: {match.get('date', 'N/A')}
⏰ Time: {match.get('time', 'N/A')}
📍 Location: {match.get('location', 'N/A')}
👥 Opponent: {match.get('opponent', 'N/A')}
📊 Status: {match.get('status', 'N/A')}"""

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_match: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get match: {e}", exc_info=True)
        return format_tool_error(f"Failed to get match: {e}")


@tool("list_team_members_and_players")
async def list_team_members_and_players(team_id: str) -> str:
    """
    List all team members and players for a team. Requires: team_id

    Args:
        team_id: Team ID

    Returns:
        List of team members and players or error message
    """
    try:
        # Handle JSON string input using utility functions
        team_id = extract_single_value(team_id, "team_id")

        # Validate input using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Sanitize input
        team_id = sanitize_input(team_id, max_length=20)

        # Get services from container
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service("TeamService")  # Assuming TeamService is available

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        if not team_service:
            raise ServiceNotAvailableError("TeamService")

        # Get players and team members
        players = await player_service.get_all_players(team_id)
        team_members = await team_service.get_team_members(team_id)

        result = f"📋 Team Overview for {team_id}\n\n"

        # Add team members section
        if team_members:
            result += "👔 Team Members:\n"
            for member in team_members:
                result += f"• {member.full_name} - {member.role.title()}\n"
            result += "\n"
        else:
            result += "👔 No team members found\n\n"

        # Add players section
        if players:
            result += "👥 Players:\n"
            for player in players:
                status_emoji = "✅" if player.status.lower() == "active" else "⏳"
                player_id_display = f" (ID: {player.player_id})" if player.player_id else ""
                result += f"• {player.full_name} - {player.position} {status_emoji} {player.status.title()}{player_id_display}\n"
        else:
            result += "👥 No players found"

        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_team_members_and_players: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to list team members and players: {e}", exc_info=True)
        return format_tool_error(f"Failed to list team members and players: {e}")
