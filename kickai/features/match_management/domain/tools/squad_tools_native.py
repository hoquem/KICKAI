#!/usr/bin/env python3
"""
Squad Management Tools - Native CrewAI Implementation

This module provides tools for squad selection and management using ONLY CrewAI native patterns.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container


@tool("get_available_players_for_match")
def get_available_players_for_match(telegram_id: int, team_id: str, chat_type: str, match_id: str) -> str:
    """
    Get list of available players for a specific match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to check availability for


    :return: Available players data for the match
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get available players."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get available players."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get available players."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to get available players."

    try:
        # Get service using simple container access
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return "❌ Match service is temporarily unavailable. Please try again later."

        # Get available players for match
        success, message = match_service.get_available_players_for_match_sync(
            team_id=team_id.strip(),
            match_id=match_id.strip()
        )

        if success:
            # Format as simple string response
            result = f"👥 Available Players for Match {match_id}\\n\\n"
            result += f"{message}\\n\\n"
            result += f"💡 Use /squad {match_id} to select the squad for this match."
            return result
        else:
            return f"❌ Failed to get available players: {message}"

    except Exception as e:
        logger.error(f"Failed to get available players for match: {e}")
        return f"❌ Failed to get available players for match: {e!s}"


@tool("select_squad")
def select_squad(
    telegram_id: int,
    team_id: str,
    chat_type: str,
    match_id: str,
    squad_size: str = ""
) -> str:
    """
    Select optimal squad for a match based on availability and tactical requirements.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to select squad for
        squad_size (str): Squad size (optional) - defaults to optimal size


    :return: Selected squad details
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to select squad."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to select squad."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to select squad."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to select squad."

    try:
        # Convert squad_size to int if provided
        squad_size_int = None
        if squad_size and squad_size.strip() != "":
            try:
                squad_size_int = int(squad_size.strip())
            except ValueError:
                return f"❌ Invalid squad size '{squad_size}'. Please provide a valid number."

        # Get service using simple container access
        container = get_container()
        squad_service = container.get_service("SquadService")

        if not squad_service:
            return "❌ Squad service is temporarily unavailable. Please try again later."

        # Select squad
        success, message = squad_service.select_squad_sync(
            team_id=team_id.strip(),
            match_id=match_id.strip(),
            squad_size=squad_size_int
        )

        if success:
            # Format as simple string response
            result = "⚽ Squad Selected Successfully!\\n\\n"
            result += f"• Match ID: {match_id}\\n"
            result += f"• Team: {team_id}\\n"
            if squad_size_int:
                result += f"• Squad Size: {squad_size_int} players\\n"
            result += f"\\n{message}\\n\\n"
            result += f"💡 Use /squad {match_id} to view or modify the squad selection."
            return result
        else:
            return f"❌ Failed to select squad: {message}"

    except Exception as e:
        logger.error(f"Failed to select squad: {e}")
        return f"❌ Failed to select squad: {e!s}"


@tool("get_all_players")
def get_all_players(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Get all players in the team for squad selection reference.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)


    :return: All players data for squad selection
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get all players."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get all players."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get all players."

    try:
        # Get service using simple container access
        container = get_container()
        player_service = container.get_service("PlayerService")

        if not player_service:
            return "❌ Player service is temporarily unavailable. Please try again later."

        # Get all players
        players = player_service.get_all_players_sync(team_id=team_id.strip())

        if not players:
            return f"📋 All Team Players (Team: {team_id})\\n\\nNo players found in the team."

        # Format as simple string response
        result = f"👥 All Team Players (Team: {team_id})\\n\\n"

        for player in players:
            status_emoji = "✅" if player.status and player.status.lower() == "active" else "⏳"
            result += f"{status_emoji} {player.name}\\n"
            result += f"   • Position: {player.position or 'Not assigned'}\\n"
            result += f"   • Status: {player.status.title() if player.status else 'Unknown'}\\n"
            result += f"   • Player ID: {player.player_id or 'Not assigned'}\\n"
            if player.phone_number:
                result += f"   • Phone: {player.phone_number}\\n"
            result += "\\n"

        result += f"Total Players: {len(players)}\\n\\n"
        result += "💡 Use these players for squad selection in upcoming matches."

        return result

    except Exception as e:
        logger.error(f"Failed to get all players: {e}")
        return f"❌ Failed to get all players: {e!s}"
