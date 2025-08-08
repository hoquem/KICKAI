#!/usr/bin/env python3
"""
Squad Management Tools

This module provides tools for squad selection and management.
"""

from loguru import logger
from pydantic import BaseModel
from typing import List, Optional

from kickai.core.dependency_container import get_container
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    format_tool_error,
    sanitize_input,
    validate_required_input,
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


@tool("get_available_players_for_match")
def get_available_players_for_match(team_id: str, user_id: str, match_id: str) -> str:
    """
    Get list of available players for a specific match.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        match_id: Match ID to check availability for

    Returns:
        List of available players or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        match_id = sanitize_input(match_id, max_length=50)

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return format_tool_error("Match service not available")

        # Get available players for match
        success, message = match_service.get_available_players_for_match_sync(
            team_id=team_id, match_id=match_id
        )

        if success:
            return f"""👥 Available Players for Match

{message}

💡 Use /squad [match_id] to select the squad for this match"""
        else:
            return format_tool_error(f"Failed to get available players: {message}")

    except Exception as e:
        logger.error(f"Failed to get available players for match: {e}", exc_info=True)
        return format_tool_error(f"Failed to get available players for match: {e}")


@tool("select_squad")
def select_squad(
    team_id: str, user_id: str, match_id: str, squad_size: Optional[int] = None
) -> str:
    """
    Select optimal squad for a match based on availability and tactical requirements.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        match_id: Match ID to select squad for
        squad_size: Squad size (optional) - defaults to optimal size

    Returns:
        Selected squad details or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        match_id = sanitize_input(match_id, max_length=50)

        # Get squad service
        container = get_container()
        squad_service = container.get_service("SquadService")

        if not squad_service:
            return format_tool_error("Squad service not available")

        # Select squad
        success, message = squad_service.select_squad_sync(
            team_id=team_id, match_id=match_id, squad_size=squad_size
        )

        if success:
            return f"""⚽ Squad Selected Successfully!

{message}

💡 Use /squad [match_id] to view or modify the squad selection"""
        else:
            return format_tool_error(f"Failed to select squad: {message}")

    except Exception as e:
        logger.error(f"Failed to select squad: {e}", exc_info=True)
        return format_tool_error(f"Failed to select squad: {e}")


@tool("get_match")
def get_match(team_id: str, user_id: str, match_id: str) -> str:
    """
    Get match details and information.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        match_id: Match ID to get details for

    Returns:
        Match details or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        match_id = sanitize_input(match_id, max_length=50)

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return format_tool_error("Match service not available")

        # Get match details
        success, message = match_service.get_match_sync(
            team_id=team_id, match_id=match_id
        )

        if success:
            return f"""🏆 Match Details

{message}

💡 Use /match [match_id] to view detailed match information"""
        else:
            return format_tool_error(f"Failed to get match details: {message}")

    except Exception as e:
        logger.error(f"Failed to get match: {e}", exc_info=True)
        return format_tool_error(f"Failed to get match: {e}")


@tool("get_all_players")
def get_all_players(team_id: str, user_id: str) -> str:
    """
    Get all players in the team for squad selection reference.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context

    Returns:
        All players list or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)

        # Get player service
        container = get_container()
        player_service = container.get_service("PlayerService")

        if not player_service:
            return format_tool_error("Player service not available")

        # Get all players
        success, message = player_service.get_all_players_sync(team_id=team_id)

        if success:
            return f"""👥 All Team Players

{message}

💡 Use /players to view all team players for squad selection"""
        else:
            return format_tool_error(f"Failed to get all players: {message}")

    except Exception as e:
        logger.error(f"Failed to get all players: {e}", exc_info=True)
        return format_tool_error(f"Failed to get all players: {e}")
