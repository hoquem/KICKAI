#!/usr/bin/env python3
"""
Player Tools

This module provides tools for player management operations.
Refactored to follow Single Try/Except Boundary Pattern and eliminate duplicate code.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio
from datetime import datetime
from loguru import logger
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.constants import (
    DEFAULT_PLAYER_POSITION,
    ERROR_MESSAGES,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_POSITION_LENGTH,
    MAX_TEAM_ID_LENGTH,
    MAX_USER_ID_LENGTH,
)
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    create_json_response,
    extract_single_value,
    format_tool_error,
    sanitize_input,
    validate_required_input,
)
from kickai.utils.tool_validation import (
    tool_error_handler,
    validate_team_id,
    validate_user_id,
    validate_player_id,
    validate_phone_number,
    validate_telegram_id,
    validate_string_input,
    validate_context_requirements,
    log_tool_execution,
    create_tool_response,
    ToolValidationError,
    ToolExecutionError,
)


# ============================================================================
# UTILITY FUNCTIONS - Extract common patterns
# ============================================================================

def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Serialize datetime object to ISO string for JSON compatibility.
    
    Args:
        dt: Datetime object to serialize, or None
        
    Returns:
        ISO formatted string if datetime provided, None otherwise
    """
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    # If it's already a string, return as-is
    return str(dt) if dt else None


def _get_service_from_container(service_class: type) -> Any:
    """
    Get service from container with standard error handling.
    
    Args:
        service_class: The service class to retrieve
        
    Returns:
        Service instance or None if not available
    """
    container = get_container()
    service = container.get_service(service_class)
    
    if not service:
        logger.warning(f"⚠️ {service_class.__name__} is not available")
        
    return service


def _create_player_data(player: Any, telegram_id: int, team_id: str) -> Dict[str, Any]:
    """
    Create standardized player data structure.
    
    Args:
        player: Player object from service
        telegram_id: User's Telegram ID
        team_id: Team identifier
        
    Returns:
        Standardized player data dictionary
    """
    return {
        "type": "player",
        "name": player.name or "Not provided",
        "position": player.position or "Not assigned",
        "status": player.status.title() if player.status else "Unknown",
        "player_id": player.player_id or "Not assigned",
        "phone_number": player.phone_number or "Not provided",
        "telegram_id": telegram_id,
        "team_id": team_id,
        "is_active": player.status and player.status.lower() == "active",
        "is_pending": player.status and player.status.lower() == "pending",
        "status_emoji": "✅" if player.status and player.status.lower() == "active" else "⏳"
    }


def _create_team_member_data(member: Any, telegram_id: int, team_id: str) -> Dict[str, Any]:
    """
    Create standardized team member data structure.
    
    Args:
        member: Team member object from service
        telegram_id: The user's telegram ID
        team_id: Team identifier
        
    Returns:
        Standardized team member data dictionary
    """
    return {
        "telegram_id": telegram_id,
        "team_id": team_id,
        "name": member.name if hasattr(member, 'name') else "Unknown",
        "role": member.role.title() if hasattr(member, 'role') and hasattr(member.role, 'title') else str(getattr(member, 'role', 'Member')).title(),
        "phone": getattr(member, 'phone', 'Not provided'),
        "email": getattr(member, 'email', 'Not provided'),
        "is_team_member": True,
        "is_player": False,
        "status": getattr(member, 'status', 'Active'),
        "type": "team_member",
        "created_at": _serialize_datetime(getattr(member, 'created_at', None)),
        "updated_at": _serialize_datetime(getattr(member, 'updated_at', None))
    }


def _parse_team_member_status(status_text: str, telegram_id: int, team_id: str) -> Dict[str, Any]:
    """
    Parse formatted team member status text into structured data.
    
    Args:
        status_text: Formatted status text from team member service
        telegram_id: Telegram ID for fallback
        team_id: Team ID for fallback
        
    Returns:
        Structured team member data
    """
    import re
    
    # Initialize with defaults
    team_member_data = {
        "type": "team_member",
        "name": "Unknown",
        "role": "Team Member",
        "phone": "Not set",
        "email": "Not set",
        "joined": "Unknown",
        "updated": "Unknown",
        "telegram_id": telegram_id,
        "team_id": team_id
    }
    
    try:
        # Parse each field using regex patterns
        patterns = {
            "name": r"📋 Name: (.+)",
            "role": r"🎭 Role: (.+)",
            "phone": r"📞 Phone: (.+)",
            "email": r"📧 Email: (.+)",
            "joined": r"📅 Joined: (.+)",
            "updated": r"🔄 Updated: (.+)"
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, status_text)
            if match:
                team_member_data[field] = match.group(1).strip()
                
    except Exception as e:
        logger.warning(f"Failed to parse team member status: {e}")
        # Return data with defaults if parsing fails
        
    return team_member_data


def _validate_standard_inputs(team_id: str, telegram_id: Union[str, int]) -> tuple[str, int]:
    """
    Validate standard tool inputs.
    
    Args:
        team_id: Team identifier
        telegram_id: Telegram ID (can be string or int)
        
    Returns:
        Tuple of (validated_team_id, validated_telegram_id_int)
        
    Raises:
        ToolValidationError: If validation fails
    """
    validated_team_id = validate_team_id(team_id)
    validated_telegram_id = validate_telegram_id(telegram_id)
    return validated_team_id, validated_telegram_id


def _log_tool_start(tool_name: str, inputs: Dict[str, Any]) -> None:
    """
    Log tool execution start with standard format.
    
    Args:
        tool_name: Name of the tool being executed
        inputs: Input parameters for logging
    """
    log_tool_execution(tool_name, inputs, True)


# ============================================================================
# INPUT MODELS
# ============================================================================

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


# ============================================================================
# TOOL FUNCTIONS - Following Single Try/Except Boundary Pattern
# ============================================================================

@tool("approve_player", result_as_answer=True)
async def approve_player(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.

    Args:
        telegram_id: Telegram ID of the approving user
        team_id: Team ID (required) - available from context
        username: Username of the approving user
        chat_type: Chat type context
        player_id: The player ID to approve (M001MH format)

    Returns:
        Success message or error
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)
        player_id = validate_player_id(player_id)
        
        # Log tool execution start
        _log_tool_start("approve_player", {'team_id': team_id, 'player_id': player_id})
        
        # Get service
        player_service = _get_service_from_container(PlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

        # Approve player
        result = await player_service.approve_player(player_id, team_id)

        # Check if result indicates success (starts with ✅)
        if result.startswith("✅"):
            # Extract player name from the result string
            # Expected format: "✅ Player {name} approved and activated successfully"
            player_name = result.split("Player ")[1].split(" approved")[0]

            return create_json_response(ResponseStatus.SUCCESS, data={
                'message': 'Player Approved and Activated Successfully',
                'player_name': player_name,
                'player_id': player_id,
                'status': 'Active'
            })
        else:
            # Result contains error message - remove ❌ prefix if present
            error_message = result.replace("❌ ", "")
            return create_json_response(ResponseStatus.ERROR, message=f"Failed to approve player: {error_message}")

    except Exception as e:
        logger.error(f"❌ Error in approve_player: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to approve player")


@tool("get_my_status", result_as_answer=True)
async def get_my_status(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get the current user's status (player or team member based on chat type).

    Args:
        telegram_id: The Telegram ID of the user whose status is to be retrieved.
        team_id: The ID of the team the user belongs to.
        username: Username of the user
        chat_type: The chat type - determines whether to look up player or team member status.

    Returns:
        User status information (player or team member) or error message
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)
        
        # Log tool execution start
        _log_tool_start("get_my_status", {'team_id': team_id, 'telegram_id': telegram_id_int, 'chat_type': chat_type})
        
        # Route based on chat type
        if chat_type.lower() in ["leadership", "leadership_chat"]:
            # Get team member information for leadership chat
            team_member_service = _get_service_from_container("TeamMemberService")
            
            if not team_member_service:
                return create_json_response(ResponseStatus.ERROR, message="TeamMemberService is not available")
            
            # Get team member by telegram ID
            team_member = await team_member_service.get_team_member_by_telegram_id(str(telegram_id_int), team_id)
            
            if team_member:
                # Create structured team member data
                team_member_data = _create_team_member_data(team_member, telegram_id_int, team_id)
            else:
                # Team member not found
                return create_tool_response(
                    success=False,
                    message="Team member not found",
                    data={
                        "telegram_id": telegram_id_int,
                        "team_id": team_id,
                        "is_team_member": False,
                        "is_player": False,
                        "status": "Not registered"
                    }
                )
            
            return create_tool_response(
                success=True,
                message="Team member status retrieved successfully",
                data=team_member_data
            )
        
        else:
            # Get player information for main chat
            player_service = _get_service_from_container(PlayerService)
            if not player_service:
                return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

            player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)

            if player:
                # Create structured player data
                player_data = _create_player_data(player, telegram_id_int, team_id)
                
                # Add pending note if applicable
                if player_data["is_pending"]:
                    player_data["note"] = "Your registration is pending approval by team leadership."
                
                return create_tool_response(
                    success=True,
                    message="Player status retrieved successfully",
                    data=player_data
                )
            else:
                return create_json_response(ResponseStatus.ERROR, message=f"Player not found for telegram ID {telegram_id_int} in team {team_id}")

    except Exception as e:
        logger.error(f"❌ Error in get_my_status: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to get user status")


@tool("get_player_status", result_as_answer=True)
async def get_player_status(telegram_id: int, team_id: str, username: str, chat_type: str, phone: str) -> str:
    """
    Get player status by phone number.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context
        phone: The player's phone number

    Returns:
        JSON response with player status or error message
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)
        phone = validate_phone_number(phone)

        # Log tool execution start
        _log_tool_start("get_player_status", {'team_id': team_id, 'telegram_id': telegram_id_int, 'phone': phone})

        # Get service
        player_service = _get_service_from_container(PlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

        # Get player status
        player = await player_service.get_player_by_phone(phone, team_id)

        if not player:
            return create_json_response(ResponseStatus.ERROR, message=f"Player not found for phone {phone} in team {team_id}")

        # Create structured player data
        player_data = _create_player_data(player, telegram_id_int, team_id)

        # Add pending note if applicable
        if player_data["is_pending"]:
            player_data["note"] = "This player's registration is pending approval by team leadership."

        return create_tool_response(
            success=True,
            message="Player status retrieved successfully",
            data=player_data
        )

    except Exception as e:
        logger.error(f"❌ Error in get_player_status: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to get player status")


@tool("get_all_players", result_as_answer=True)
async def get_all_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all players in the team.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context

    Returns:
        List of all players or error message
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ ", ""))

        # Sanitize and validate inputs
        team_id = sanitize_input(team_id, max_length=20)
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)

        # Get service
        player_service = _get_service_from_container(PlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

        # Get all players
        players = await player_service.get_all_players(team_id)

        if not players:
            return create_tool_response(
                success=True,
                message="No players found in the team",
                data={"players": [], "count": 0, "team_id": team_id}
            )

        # Create structured player data
        players_data = []
        for player in players:
            player_info = {
                "name": player.name,
                "position": player.position,
                "status": player.status.title(),
                "player_id": player.player_id or "Not assigned",
                "phone_number": player.phone_number or "Not provided",
                "is_active": player.status.lower() == "active",
                "status_emoji": "✅" if player.status.lower() == "active" else "⏳"
            }
            players_data.append(player_info)

        return create_tool_response(
            success=True,
            message=f"Retrieved {len(players)} players from team",
            data={
                "players": players_data,
                "count": len(players_data),
                "team_id": team_id,
                "telegram_id": telegram_id_int
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_all_players: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to get all players")


@tool("get_active_players", result_as_answer=True)
async def get_active_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all active players in the team.

    🎯 CONTEXT USAGE GUIDANCE:
    - MAIN CHAT: Primary tool for /list commands (focused player view for match planning)
    - PRIVATE CHAT: Personal player information requests
    - LEADERSHIP CHAT: Use list_team_members_and_players instead (comprehensive team oversight needed)
    
    📋 USE WHEN:
    - Player needs to see who's available for matches
    - Simple player list requests in main chat
    - Personal context queries about active players
    
    ❌ AVOID WHEN:
    - Leadership needs full team administrative view (use list_team_members_and_players)
    - Need to see both team members and players together
    - Administrative decisions requiring complete team roster

    🚨 CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:
    - This tool queries the ACTUAL DATABASE for active players
    - If the database returns NO players, return JSON with empty players array - DO NOT INVENT PLAYERS
    - The agent MUST return this tool's output EXACTLY as received - NO additions, NO modifications
    - NEVER create imaginary player data if the database is empty

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context

    Returns:
        JSON response with EXACT database results - List of active players or empty array
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)

        # Log tool execution start
        _log_tool_start("get_active_players", {'team_id': team_id, 'telegram_id': telegram_id_int})

        # Get service
        player_service = _get_service_from_container(PlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

        # Get active players from database
        players = await player_service.get_active_players(team_id)

        # Log the actual database results for debugging
        logger.info(
            f"🔍 DATABASE QUERY RESULT: Found {len(players) if players else 0} active players in team {team_id}"
        )

        if not players:
            # 🚨 CRITICAL: If database has no players, DO NOT INVENT ANY
            logger.info(f"🔍 DATABASE RETURNED: Empty list - no active players in team {team_id}")
            return create_tool_response(
                success=True,
                message="No active players found in the team",
                data={
                    "players": [],
                    "count": 0,
                    "team_id": team_id,
                    "telegram_id": telegram_id_int
                }
            )

        player_names = [p.name for p in players]
        logger.info(f"🔍 ACTUAL PLAYER NAMES FROM DB: {player_names}")
        # Create structured player data with actual database data only
        logger.info(f"🔍 FORMATTING {len(players)} REAL PLAYERS FROM DATABASE")
        players_data = []
        
        for player in players:
            logger.info(f"🔍 PROCESSING REAL PLAYER: {player.name} (ID: {player.player_id})")
            
            player_info = {
                "name": player.name,
                "position": player.position or "Not assigned",
                "player_id": player.player_id or "Not assigned", 
                "phone_number": player.phone_number or "Not provided",
                "status": "Active",
                "status_emoji": "✅"
            }
            
            players_data.append(player_info)

        # 🚨 CRITICAL: This exact output must be returned by the agent without any modifications
        logger.info(f"🚨 FINAL TOOL OUTPUT: {len(players_data)} real players from database")

        return create_tool_response(
            success=True,
            message=f"Retrieved {len(players)} active players from team",
            data={
                "players": players_data,
                "count": len(players_data),
                "team_id": team_id,
                "telegram_id": telegram_id_int
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in get_active_players: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to get active players")


def validate_tool_output_integrity(original_output: str, agent_response: str) -> bool:
    """
    Validate that the agent response matches the original tool output exactly.

    Args:
        original_output: The original tool output
        agent_response: The agent's response

    Returns:
        True if the outputs match exactly, False otherwise
    """
    # Remove any leading/trailing whitespace for comparison
    original_clean = original_output.strip()
    agent_clean = agent_response.strip()

    # Check for exact match
    if original_clean == agent_clean:
        return True

    # Log the difference for debugging
    logger.warning("Tool output integrity check failed:")
    logger.warning(f"Original: {original_clean!r}")
    logger.warning(f"Agent: {agent_clean!r}")

    return False


@tool("get_player_match", result_as_answer=True)
async def get_player_match(telegram_id: int, team_id: str, username: str, chat_type: str, match_id: str) -> str:
    """
    Get match details by match ID.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required)
        username: Username of the requesting user
        chat_type: Chat type context
        match_id: The match ID to retrieve

    Returns:
        JSON response with match details or error message
    """
    try:
        # Validate inputs
        match_id = validate_string_input(match_id, "Match ID", max_length=50)
        team_id = validate_team_id(team_id)

        # Log tool execution start
        _log_tool_start("get_player_match", {'match_id': match_id, 'team_id': team_id})

        # Get service
        match_service = _get_service_from_container("MatchService")
        if not match_service:
            return create_json_response(ResponseStatus.ERROR, message="MatchService is not available")

        # Get match details
        match = await match_service.get_match(match_id, team_id)

        if not match:
            return create_json_response(ResponseStatus.ERROR, message=f"Match {match_id} not found in team {team_id}")

        # Create structured match data
        match_data = {
            "match_id": match.get("match_id", "N/A"),
            "date": match.get("date", "N/A"),
            "time": match.get("time", "N/A"),
            "location": match.get("location", "N/A"),
            "opponent": match.get("opponent", "N/A"),
            "status": match.get("status", "N/A"),
            "team_id": team_id
        }

        return create_tool_response(
            success=True,
            message="Match details retrieved successfully",
            data=match_data
        )

    except Exception as e:
        logger.error(f"❌ Error in get_player_match: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to get match details")


@tool("list_team_members_and_players", result_as_answer=True)
async def list_team_members_and_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    List all team members and players for comprehensive team overview.

    🎯 CONTEXT USAGE GUIDANCE:
    - LEADERSHIP CHAT: Primary tool for /list commands (complete team management view)
    - ADMINISTRATIVE CONTEXT: Full team roster with roles and status
    - TEAM OVERSIGHT: When leaders need complete team visibility
    
    📋 USE WHEN:
    - Leadership needs comprehensive team overview
    - Administrative decisions requiring full team roster
    - /list commands in leadership chat
    - Team management and coordination tasks
    
    ❌ AVOID WHEN:
    - Main chat requests (use get_active_players for focused view)
    - Simple player availability queries
    - Match planning focus (active players sufficient)

    🎯 OPTIMAL FOR:
    - Leadership decision-making requiring complete team visibility
    - Team administration and member management
    - Comprehensive team status reports

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID
        username: Username of the requesting user
        chat_type: Chat type context

    Returns:
        JSON response with comprehensive list of team members and players or error message
    """
    try:
        # Validate input
        team_id = validate_team_id(team_id)

        # Log tool execution start
        _log_tool_start("list_team_members_and_players", {'team_id': team_id})

        # Get services
        player_service = _get_service_from_container(PlayerService)
        team_service = _get_service_from_container("TeamService")

        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

        if not team_service:
            return create_json_response(ResponseStatus.ERROR, message="TeamService is not available")

        # Get players and team members
        players = await player_service.get_all_players(team_id)
        team_members = await team_service.get_team_members(team_id)

        # Create structured team member data
        team_members_data = []
        if team_members:
            for member in team_members:
                # For listing, use member's telegram_id if available, otherwise use 0 as placeholder
                member_telegram_id = getattr(member, 'telegram_id', 0)
                if isinstance(member_telegram_id, str) and member_telegram_id.isdigit():
                    member_telegram_id = int(member_telegram_id)
                elif not isinstance(member_telegram_id, int):
                    member_telegram_id = 0
                    
                member_info = _create_team_member_data(member, member_telegram_id, team_id)
                team_members_data.append(member_info)

        # Create structured player data
        players_data = []
        if players:
            for player in players:
                player_info = {
                    "name": player.name,
                    "position": player.position or "Not assigned",
                    "status": player.status.title() if player.status else "Unknown",
                    "player_id": player.player_id or "Not assigned",
                    "status_emoji": "✅" if player.status and player.status.lower() == "active" else "⏰",
                    "is_active": player.status and player.status.lower() == "active",
                    "type": "player"
                }
                players_data.append(player_info)

        # Create summary data
        summary_data = {
            "team_id": team_id,
            "team_members": team_members_data,
            "players": players_data,
            "team_members_count": len(team_members_data),
            "players_count": len(players_data),
            "total_count": len(team_members_data) + len(players_data)
        }

        return create_tool_response(
            success=True,
            message=f"Retrieved team overview for {team_id}: {len(team_members_data)} team members, {len(players_data)} players",
            data=summary_data
        )

    except Exception as e:
        logger.error(f"❌ Error in list_team_members_and_players: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to list team members and players")

