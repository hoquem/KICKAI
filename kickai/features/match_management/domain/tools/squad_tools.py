#!/usr/bin/env python3
"""
Squad Management Tools

This module provides tools for squad selection and management.
"""


from crewai.tools import tool
from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.tool_helpers import (
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
    squad_size: int | None = None

class GetMatchInput(BaseModel):
    """Input model for get_match tool."""

    team_id: str
    user_id: str
    match_id: str

@tool("get_available_players_for_match")
def get_available_players_for_match(team_id: str, telegram_id: int, match_id: str) -> str:
    """
    Get list of available players for a specific match.


        team_id: Team ID (required) - available from context
        telegram_id: Telegram ID (required) - available from context
        match_id: Match ID to check availability for


    :return: JSON response with available players data
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        match_id = sanitize_input(match_id, max_length=50)
        
        # Validate telegram_id as positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return json_error(f"Invalid telegram_id: {telegram_id}. Must be a positive integer.", "Invalid input")

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return json_error("Match service not available", "Service unavailable")

        # Get available players for match
        success, message = match_service.get_available_players_for_match_sync(
            team_id=team_id, match_id=match_id
        )

        if success:
            data = {
                'team_id': team_id,
                'match_id': match_id,
                'telegram_id': telegram_id,
                'status': 'available_players_retrieved',
                'message': message
            }

            ui_format = f"""👥 Available Players for Match

{message}

💡 Use /squad [match_id] to select the squad for this match"""

            return json_response(data, ui_format=ui_format)
        else:
            return json_error(f"Failed to get available players: {message}", "Operation failed")

    except Exception as e:
        logger.error(f"Failed to get available players for match: {e}", exc_info=True)
        return json_error(f"Failed to get available players for match: {e}", "Operation failed")

@tool("select_squad")
def select_squad(
    team_id: str, telegram_id: int, match_id: str, squad_size: int | None = None
) -> str:
    """
    Select optimal squad for a match based on availability and tactical requirements.


        team_id: Team ID (required) - available from context
        telegram_id: Telegram ID (required) - available from context
        match_id: Match ID to select squad for
        squad_size: Squad size (optional) - defaults to optimal size


    :return: JSON response with selected squad details
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        # Validate telegram_id as positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return json_error(f"Invalid telegram_id: {telegram_id}. Must be a positive integer.", "Invalid input")
        match_id = sanitize_input(match_id, max_length=50)

        # Get squad service
        container = get_container()
        squad_service = container.get_service("SquadService")

        if not squad_service:
            return json_error("Squad service not available", "Service unavailable")

        # Select squad
        success, message = squad_service.select_squad_sync(
            team_id=team_id, match_id=match_id, squad_size=squad_size
        )

        if success:
            data = {
                'team_id': team_id,
                'match_id': match_id,
                'telegram_id': telegram_id,
                'squad_size': squad_size,
                'status': 'squad_selected',
                'message': message
            }

            ui_format = f"""⚽ Squad Selected Successfully!

{message}

💡 Use /squad [match_id] to view or modify the squad selection"""

            return json_response(data, ui_format=ui_format)
        else:
            return json_error(f"Failed to select squad: {message}", "Operation failed")

    except Exception as e:
        logger.error(f"Failed to select squad: {e}", exc_info=True)
        return json_error(f"Failed to select squad: {e}", "Operation failed")

@tool("get_match")
def get_match(team_id: str, telegram_id: int, match_id: str) -> str:
    """
    Get match details and information.


        team_id: Team ID (required) - available from context
        telegram_id: Telegram ID (required) - available from context
        match_id: Match ID to get details for


    :return: JSON response with match details
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        # Validate telegram_id as positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            return json_error(f"Invalid telegram_id: {telegram_id}. Must be a positive integer.", "Invalid input")
        match_id = sanitize_input(match_id, max_length=50)

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return json_error("Match service not available", "Service unavailable")

        # Get match details
        success, message = match_service.get_match_sync(
            team_id=team_id, match_id=match_id
        )

        if success:
            data = {
                'team_id': team_id,
                'match_id': match_id,
                'telegram_id': telegram_id,
                'status': 'match_details_retrieved',
                'message': message
            }

            ui_format = f"""🏆 Match Details

{message}

💡 Use /match [match_id] to view detailed match information"""

            return json_response(data, ui_format=ui_format)
        else:
            return json_error(f"Failed to get match details: {message}", "Operation failed")

    except Exception as e:
        logger.error(f"Failed to get match: {e}", exc_info=True)
        return json_error(f"Failed to get match: {e}", "Operation failed")

@tool("get_all_players")
def get_all_players(team_id: str, telegram_id: int) -> str:
    """
    Get all players in the team for squad selection reference.


        team_id: Team ID (required) - available from context
        telegram_id: Telegram ID (required) - available from context


    :return: JSON response with all players data
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return json_error(validation_error, "Validation failed")

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        # Convert telegram_id to int for consistency
        if isinstance(telegram_id, str):
            try:
                telegram_id = int(telegram_id)
            except ValueError:
                return json_error(f"Invalid telegram_id format: {telegram_id}", "Validation failed")
        else:
            telegram_id = int(telegram_id)

        # Get player service
        container = get_container()
        player_service = container.get_service("PlayerService")

        if not player_service:
            return json_error("Player service not available", "Service unavailable")

        # Get all players
        players = player_service.get_all_players_sync(team_id=team_id)

        if not players:
            data = {
                'team_id': team_id,
                'telegram_id': telegram_id,
                'players': [],
                'count': 0
            }
            return json_response(data, ui_format="📋 No players found in the team.")

        # Format response
        players_data = []
        ui_format = "👥 All Team Players\n\n"

        for player in players:
            status_emoji = "✅" if player.status and player.status.lower() == "active" else "⏳"
            ui_format += f"{status_emoji} {player.name}\n"
            ui_format += f"   • Position: {player.position or 'Not assigned'}\n"
            ui_format += f"   • Status: {player.status.title() if player.status else 'Unknown'}\n"
            ui_format += f"   • Player ID: {player.player_id or 'Not assigned'}\n"
            ui_format += f"   • Phone: {player.phone_number or 'Not provided'}\n\n"

            players_data.append({
                'name': player.name,
                'position': player.position or 'Not assigned',
                'status': player.status or 'Unknown',
                'player_id': player.player_id or 'Not assigned',
                'phone_number': player.phone_number or 'Not provided'
            })

        ui_format += "💡 Use /players to view all team players for squad selection"

        data = {
            'team_id': team_id,
            'telegram_id': telegram_id,
            'players': players_data,
            'count': len(players_data)
        }

        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"Failed to get all players: {e}", exc_info=True)
        return json_error(f"Failed to get all players: {e}", "Operation failed")
