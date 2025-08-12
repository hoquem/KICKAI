#!/usr/bin/env python3
"""
Player Tools

This module provides tools for player management operations.
"""

from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from typing import List, Optional, Union
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
    validate_context_requirements,
    log_tool_execution,
    create_tool_response,
    ToolValidationError,
    ToolExecutionError,
)


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


@tool("approve_player")
@tool_error_handler
def approve_player(team_id: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.

    Args:
        team_id: Team ID (required) - available from context
        player_id: The player ID to approve (M001MH format)

    Returns:
        JSON string with success/error status and data
    """
    # Validate inputs
    team_id = validate_team_id(team_id)
    player_id = validate_player_id(player_id)
    
    # Log tool execution start
    inputs = {'team_id': team_id, 'player_id': player_id}
    log_tool_execution("approve_player", inputs, True)
    
    # Get service
    container = get_container()
    player_service = container.get_service(PlayerService)

    if not player_service:
        raise ToolExecutionError("PlayerService is not available")

    # Approve player
    result = player_service.approve_player_sync(player_id, team_id)

    # Check if result indicates success (starts with ✅)
    if result.startswith("✅"):
        # Extract player name from the result string
        # Expected format: "✅ Player {name} approved and activated successfully"
        try:
            player_name = result.split("Player ")[1].split(" approved")[0]
        except (IndexError, AttributeError):
            player_name = "Unknown"

        return create_json_response("success", data={
            'message': 'Player Approved and Activated Successfully',
            'player_name': player_name,
            'player_id': player_id,
            'status': 'Active'
        })
    else:
        # Result contains error message - remove ❌ prefix if present
        error_message = result.replace("❌ ", "")
        raise ToolExecutionError(f"Failed to approve player: {error_message}")


@tool("get_my_status")
@tool_error_handler
def get_my_status(telegram_id: Union[str, int], team_id: str, chat_type: str) -> str:
    """
    Get the current user's status (player or team member based on chat type).

    Args:
        telegram_id: The Telegram ID of the user whose status is to be retrieved (accepts string or int).
        team_id: The ID of the team the user belongs to.
        chat_type: The chat type - determines whether to look up player or team member status.

    Returns:
        JSON string with user status information (player or team member) or error message
    """
    # Validate inputs - convert telegram_id to int first for consistency
    team_id = validate_team_id(team_id)
    
    # Convert telegram_id to int for consistency with database/service layer
    if isinstance(telegram_id, str):
        try:
            telegram_id_int = int(telegram_id)
        except ValueError:
            raise ToolValidationError(f"Invalid telegram_id format: {telegram_id}")
    else:
        telegram_id_int = int(telegram_id)
    
    # Log tool execution start
    inputs = {'team_id': team_id, 'telegram_id': telegram_id_int, 'chat_type': chat_type}
    log_tool_execution("get_my_status", inputs, True)
    
    # Get services from container
    container = get_container()
    player_service = container.get_service(PlayerService)
    
    if not player_service:
        raise ToolExecutionError("PlayerService is not available")

    # Route based on chat type
    if chat_type.lower() in ["leadership", "leadership_chat"]:
        # Get team member information for leadership chat
        try:
            team_member_service = container.get_service("TeamMemberService")
            
            if not team_member_service:
                raise ToolExecutionError("TeamMemberService is not available")
            
            # Get team member status
            status = team_member_service.get_my_status_sync(str(telegram_id_int), team_id)
            return create_json_response("success", data={'status': status})
            
        except Exception as e:
            logger.error(f"Failed to get team member status: {e}")
            raise ToolExecutionError(f"Failed to get team member status: {e}")
    
    else:
        # Get player information for main chat
        player = player_service.get_player_by_telegram_id_sync(telegram_id_int, team_id)

        if player:
            # Format the status response
            status_emoji = "✅" if player.status and player.status.lower() == "active" else "⏳"
            status_text = player.status.title() if player.status else "Unknown"
            
            player_data = {
                'name': player.name or "Not provided",
                'position': player.position or "Not assigned", 
                'status': status_text,
                'status_emoji': status_emoji,
                'player_id': player.player_id or "Not assigned",
                'phone': player.phone_number or "Not provided",
                'is_pending': player.status and player.status.lower() == "pending"
            }
            
            if player.status and player.status.lower() == "pending":
                player_data['note'] = "Your registration is pending approval by team leadership."

            return create_json_response("success", data=player_data)
        else:
            raise ToolExecutionError(f"Player not found for telegram ID {telegram_id_int} in team {team_id}")


@tool("get_player_status")
def get_player_status(team_id: str, telegram_id: str, phone: str) -> str:
    """
    Get player status by phone number.

    Args:
        team_id: Team ID (required) - available from context
        telegram_id: Telegram ID (required) - available from context
        phone: The player's phone number

    Returns:
        JSON string with player status or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(phone, "Phone")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        # Sanitize inputs
        phone = sanitize_input(phone, max_length=20)
        team_id = sanitize_input(team_id, max_length=20)
        telegram_id = sanitize_input(str(telegram_id), max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get player status
        player = player_service.get_player_by_phone_sync(phone, team_id)

        if not player:
            return create_json_response("error", message=f"Player not found for phone {phone} in team {team_id}")

        # Format response
        status_emoji = "✅" if player.status.lower() == "active" else "⏳"
        status_text = player.status.title()

        player_data = {
            'name': player.name,
            'position': player.position,
            'status': status_text,
            'status_emoji': status_emoji,
            'player_id': player.player_id or "Not assigned",
            'phone': player.phone_number or "Not provided"
        }

        if player.status.lower() == "pending":
            player_data['note'] = "This player's registration is pending approval by team leadership."

        return create_json_response("success", data=player_data)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_player_status: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get player status: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get player status: {e}")


@tool("get_all_players")
def get_all_players(team_id: str, telegram_id: Union[str, int]) -> str:
    """
    Get all players in the team.

    Args:
        team_id: Team ID (required) - available from context
        telegram_id: Telegram ID (required) - available from context (accepts string or int)

    Returns:
        JSON string with list of all players or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        # Convert telegram_id to int for consistency
        if isinstance(telegram_id, str):
            try:
                telegram_id_int = int(telegram_id)
            except ValueError:
                return create_json_response("error", message=f"Invalid telegram_id format: {telegram_id}")
        else:
            telegram_id_int = int(telegram_id)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get all players
        players = player_service.get_all_players_sync(team_id)

        if not players:
            return create_json_response("success", data={'message': 'No players found in the team', 'players': []})

        # Format response
        players_data = []
        for player in players:
            status_emoji = "✅" if player.status.lower() == "active" else "⏳"
            players_data.append({
                'name': player.name,
                'position': player.position,
                'status': player.status.title(),
                'status_emoji': status_emoji,
                'player_id': player.player_id or 'Not assigned',
                'phone': player.phone_number or 'Not provided'
            })

        return create_json_response("success", data={'message': 'All Players in Team', 'players': players_data})

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_all_players: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get all players: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get all players: {e}")


@tool("get_active_players")
def get_active_players(team_id: str, telegram_id: str) -> str:
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
        telegram_id: Telegram ID (required) - available from context

    Returns:
        JSON string with EXACT database results - List of active players or "No active players found" message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        telegram_id = sanitize_input(str(telegram_id), max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get active players from database
        players = player_service.get_active_players_sync(team_id)

        # Log the actual database results for debugging
        logger.info(
            f"🔍 DATABASE QUERY RESULT: Found {len(players) if players else 0} active players in team {team_id}"
        )
        if players:
            player_names = [p.name for p in players]
            logger.info(f"🔍 ACTUAL PLAYER NAMES FROM DB: {player_names}")
        else:
            logger.info(f"🔍 DATABASE RETURNED: Empty list - no active players in team {team_id}")

        if not players:
            # 🚨 CRITICAL: If database has no players, DO NOT INVENT ANY
            logger.info(
                "🚨 ANTI-HALLUCINATION: Returning 'no players found' message - DO NOT ADD FAKE PLAYERS"
            )
            return create_json_response("success", data={
                'message': 'No active players found in the team',
                'players': []
            })

        # Format response with actual database data only
        logger.info(f"🔍 FORMATTING {len(players)} REAL PLAYERS FROM DATABASE")
        players_data = []
        
        for player in players:
            logger.info(f"🔍 PROCESSING REAL PLAYER: {player.name} (ID: {player.player_id})")
            player_data = {
                'name': player.name,
                'position': player.position,
                'player_id': player.player_id or 'Not assigned',
                'phone': player.phone_number or 'Not provided'
            }
            players_data.append(player_data)

        result_data = {
            'message': 'Active Players in Team',
            'players': players_data
        }

        # 🚨 CRITICAL: This exact output must be returned by the agent without any modifications
        logger.info(f"🚨 FINAL TOOL OUTPUT (EXACT): {result_data!r}")
        logger.info("🚨 AGENT MUST RETURN THIS EXACTLY - NO FAKE PLAYERS ALLOWED")

        # Additional validation: Check for specific fake players in the result
        fake_player_indicators = [
            "Farhan Fuad",
            "03FF",
            "+447479958935",
            "Saim",
            "John Smith",
            "Jane Doe",
        ]
        result_str = str(result_data)
        for fake_indicator in fake_player_indicators:
            if fake_indicator in result_str:
                logger.error(
                    f"🚨 CRITICAL ERROR: Tool output contains fake player indicator: {fake_indicator}"
                )
                logger.error("🚨 THIS SHOULD NEVER HAPPEN - TOOL IS ONLY RETURNING DATABASE DATA")
                logger.error(f"🚨 Result: {result_str!r}")

        return create_json_response("success", data=result_data)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_active_players: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get active players: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get active players: {e}")


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


@tool("get_player_match")
def get_player_match(match_id: str, team_id: str) -> str:
    """
    Get match details by match ID. Requires: match_id, team_id

    Args:
        match_id: The match ID to retrieve
        team_id: Team ID (required)

    Returns:
        JSON string with match details or error message
    """
    try:
        # Handle JSON string input using utility functions
        match_id = extract_single_value(match_id, "match_id")
        team_id = extract_single_value(team_id, "team_id")

        # Validate inputs using utility functions
        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

        # Sanitize inputs
        match_id = sanitize_input(match_id, max_length=20)
        team_id = sanitize_input(team_id, max_length=20)

        # Get services from container
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            raise ServiceNotAvailableError("MatchService")

        # Get match details
        match = match_service.get_match_sync(match_id, team_id)

        if not match:
            return create_json_response("error", message=f"Match {match_id} not found in team {team_id}")

        # Format match details
        match_data = {
            'match_id': match.get("match_id", "N/A"),
            'date': match.get("date", "N/A"),
            'time': match.get("time", "N/A"),
            'location': match.get("location", "N/A"),
            'opponent': match.get("opponent", "N/A"),
            'status': match.get("status", "N/A")
        }
        
        return create_json_response("success", data=match_data)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_match: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get match: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get match: {e}")


@tool("list_team_members_and_players")
def list_team_members_and_players(team_id: str) -> str:
    """
    List all team members and players for a team. Requires: team_id

    Args:
        team_id: Team ID

    Returns:
        JSON string with list of team members and players or error message
    """
    try:
        # Handle JSON string input using utility functions
        team_id = extract_single_value(team_id, "team_id")

        # Validate input using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ ", ""))

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
        players = player_service.get_all_players_sync(team_id)
        team_members = team_service.get_team_members_sync(team_id)

        # Format team members
        team_members_data = []
        if team_members:
            for member in team_members:
                team_members_data.append({
                    'name': member.name,
                    'role': member.role.title()
                })

        # Format players
        players_data = []
        if players:
            for player in players:
                status_emoji = "✅" if player.status.lower() == "active" else "⏰"
                players_data.append({
                    'name': player.name,
                    'position': player.position,
                    'status': player.status.title(),
                    'status_emoji': status_emoji,
                    'player_id': player.player_id if player.player_id else None
                })

        result_data = {
            'team_id': team_id,
            'team_members': team_members_data,
            'players': players_data
        }

        return create_json_response("success", data=result_data)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_team_members_and_players: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to list team members and players: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to list team members and players: {e}")
