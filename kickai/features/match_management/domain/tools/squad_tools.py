#!/usr/bin/env python3
"""
Squad Management Tools

This module provides tools for squad selection and management.
"""

from loguru import logger
from pydantic import BaseModel
from typing import List, Optional, Union

from kickai.core.dependency_container import get_container
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    format_tool_error,
    sanitize_input,
    validate_required_input,
    create_json_response,
)


class GetAvailablePlayersForMatchInput(BaseModel):
    """Input model for get_available_players_for_match tool."""

    team_id: str
    user_id: str
    match_id: str


class SelectSquadInput(BaseModel):
    """Input model for select_squad tool."""

    team_id: str
    user_id: str
    match_id: str
    squad_size: Optional[int] = None


class GetMatchInput(BaseModel):
    """Input model for get_match tool."""

    team_id: str
    user_id: str
    match_id: str


@tool("get_available_players_for_match", result_as_answer=True)
def get_available_players_for_match(team_id: str, telegram_id: Union[str, int], match_id: str) -> str:
    """Get list of available players for a specific match.
    
    Retrieves players who have marked themselves as available
    for a specific match, useful for squad selection.
    
    :param team_id: Team ID (required, available from context)
    :type team_id: str
    :param telegram_id: Telegram ID (required, accepts string or int)
    :type telegram_id: Union[str, int]
    :param match_id: Match ID to check availability for
    :type match_id: str
    :returns: JSON string with list of available players or error
    :rtype: str
    :raises Exception: When match service unavailable or query fails
    
    .. note::
       Only shows players who have explicitly marked availability
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        # Convert telegram_id to int for consistency
        if isinstance(telegram_id, str):
            try:
                telegram_id_int = int(telegram_id)
            except ValueError:
                return create_json_response("error", message=f"Invalid telegram_id format: {telegram_id}")
        else:
            telegram_id_int = int(telegram_id)
        match_id = sanitize_input(match_id, max_length=50)

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return create_json_response("error", message="Match service not available")

        # Get available players for match
        success, message = match_service.get_available_players_for_match_sync(
            team_id=team_id, match_id=match_id
        )

        if success:
            data = f"""👥 Available Players for Match

{message}

💡 Use /squad [match_id] to select the squad for this match"""
            return create_json_response("success", data=data)
        else:
            return create_json_response("error", message=f"Failed to get available players: {message}")

    except Exception as e:
        logger.error(f"Failed to get available players for match: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get available players for match: {e}")


@tool("select_squad", result_as_answer=True)
def select_squad(
    team_id: str, telegram_id: Union[str, int], match_id: str, squad_size: Optional[int] = None
) -> str:
    """Select optimal squad for a match.
    
    Selects the best available squad for a match based on player
    availability, positions, and tactical requirements.
    
    :param team_id: Team ID (required, available from context)
    :type team_id: str
    :param telegram_id: Telegram ID (required, available from context)
    :type telegram_id: Union[str, int]
    :param match_id: Match ID to select squad for
    :type match_id: str
    :param squad_size: Optional squad size, defaults to optimal size
    :type squad_size: Optional[int]
    :returns: JSON string with selected squad details or error
    :rtype: str
    :raises Exception: When squad service unavailable or selection fails
    
    .. example::
       >>> result = select_squad("KTI", "123456", "MATCH001", 11)
       >>> print(result)
       '{"status": "success", "data": "Squad Selected Successfully!..."}
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        telegram_id = sanitize_input(str(telegram_id), max_length=50)
        match_id = sanitize_input(match_id, max_length=50)

        # Get squad service
        container = get_container()
        squad_service = container.get_service("SquadService")

        if not squad_service:
            return create_json_response("error", message="Squad service not available")

        # Select squad
        success, message = squad_service.select_squad_sync(
            team_id=team_id, match_id=match_id, squad_size=squad_size
        )

        if success:
            data = f"""⚽ Squad Selected Successfully!

{message}

💡 Use /squad [match_id] to view or modify the squad selection"""
            return create_json_response("success", data=data)
        else:
            return create_json_response("error", message=f"Failed to select squad: {message}")

    except Exception as e:
        logger.error(f"Failed to select squad: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to select squad: {e}")


@tool("get_match", result_as_answer=True)
def get_match(team_id: str, telegram_id: Union[str, int], match_id: str) -> str:
    """Get match details and information.
    
    Retrieves comprehensive information about a specific match
    including date, time, venue, and current status.
    
    :param team_id: Team ID (required, available from context)
    :type team_id: str
    :param telegram_id: Telegram ID (required, available from context)
    :type telegram_id: Union[str, int]
    :param match_id: Match ID to get details for
    :type match_id: str
    :returns: JSON string with match details or error
    :rtype: str
    :raises Exception: When match service unavailable or retrieval fails
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        telegram_id = sanitize_input(str(telegram_id), max_length=50)
        match_id = sanitize_input(match_id, max_length=50)

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return create_json_response("error", message="Match service not available")

        # Get match details
        success, message = match_service.get_match_sync(
            team_id=team_id, match_id=match_id
        )

        if success:
            data = f"""🏆 Match Details

{message}

💡 Use /match [match_id] to view detailed match information"""
            return create_json_response("success", data=data)
        else:
            return create_json_response("error", message=f"Failed to get match details: {message}")

    except Exception as e:
        logger.error(f"Failed to get match: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get match: {e}")


@tool("get_all_players", result_as_answer=True)
def get_all_players(team_id: str, telegram_id: Union[str, int]) -> str:
    """Get all players in the team for squad selection reference.
    
    Retrieves complete roster of all team players with their status,
    position, and contact information for squad selection purposes.
    
    :param team_id: Team ID (required, available from context)
    :type team_id: str
    :param telegram_id: Telegram ID (required, accepts string or int)
    :type telegram_id: Union[str, int]
    :returns: JSON string with all players list or error
    :rtype: str
    :raises Exception: When player service unavailable or retrieval fails
    
    .. note::
       Shows all players regardless of availability status
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        # Convert telegram_id to int for consistency
        if isinstance(telegram_id, str):
            try:
                telegram_id_int = int(telegram_id)
            except ValueError:
                return create_json_response("error", message=f"Invalid telegram_id format: {telegram_id}")
        else:
            telegram_id_int = int(telegram_id)

        # Get player service
        container = get_container()
        player_service = container.get_service("PlayerService")

        if not player_service:
            return create_json_response("error", message="Player service not available")

        # Get all players
        players = player_service.get_all_players_sync(team_id=team_id)

        if not players:
            return create_json_response("success", data="📋 No players found in the team.")

        # Format response
        result = "👥 All Team Players\n\n"

        for player in players:
            status_emoji = "✅" if player.status and player.status.lower() == "active" else "⏳"
            result += f"{status_emoji} {player.name}\n"
            result += f"   • Position: {player.position or 'Not assigned'}\n"
            result += f"   • Status: {player.status.title() if player.status else 'Unknown'}\n"
            result += f"   • Player ID: {player.player_id or 'Not assigned'}\n"
            result += f"   • Phone: {player.phone_number or 'Not provided'}\n\n"

        result += "💡 Use /players to view all team players for squad selection"
        return create_json_response("success", data=result)

    except Exception as e:
        logger.error(f"Failed to get all players: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get all players: {e}")
