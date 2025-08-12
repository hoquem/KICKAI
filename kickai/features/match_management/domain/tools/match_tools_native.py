#!/usr/bin/env python3
"""
Match Tools - Native CrewAI Implementation

This module provides tools for match management operations using ONLY CrewAI native patterns.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.match_management.domain.services.match_service import MatchService


@tool("list_matches")
def list_matches(telegram_id: int, team_id: str, chat_type: str, status: str = "", limit: str = "10") -> str:
    """
    List matches for a team.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        status (str): Optional status filter (upcoming, completed, cancelled)
        limit (str): Maximum number of matches to return (default: 10)


    :return: List of matches for the team with match details and status information
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to list matches."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to list matches."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to list matches."

    try:
        # Convert limit to int if provided
        try:
            limit_int = int(limit) if limit and limit.strip() != "" else 10
        except ValueError:
            limit_int = 10

        # Get service using simple container access
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ Match service is temporarily unavailable. Please try again later."

        # Get matches
        matches = match_service.get_matches_sync(
            team_id,
            status=status.strip() if status and status.strip() != "" else None,
            limit=limit_int
        )

        if not matches:
            filter_text = f" with status '{status}'" if status and status.strip() != "" else ""
            return f"📅 Matches (Team: {team_id})\\n\\nNo matches found{filter_text}."

        # Format as simple string response
        filter_text = f" - {status.title()}" if status and status.strip() != "" else ""
        result = f"📅 Matches{filter_text} (Team: {team_id})\\n\\n"

        for match in matches:
            status_emoji = "🟢" if match.status == "upcoming" else "🔴" if match.status == "completed" else "🟡"
            date_text = match.date.strftime('%Y-%m-%d %H:%M') if match.date else 'TBD'
            result += f"{status_emoji} {match.opponent} - {date_text}\\n"
            result += f"   📍 {match.location}\\n"
            result += f"   📊 Status: {match.status.title()}\\n\\n"

        result += f"Total Matches: {len(matches)}"
        return result

    except Exception as e:
        logger.error(f"Failed to list matches: {e}")
        return f"❌ Failed to list matches: {e!s}"


@tool("create_match")
def create_match(telegram_id: int, team_id: str, chat_type: str, opponent: str, date: str, location: str) -> str:
    """
    Create a new match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        opponent (str): Opponent team name
        date (str): Match date (YYYY-MM-DD HH:MM format)
        location (str): Match location


    :return: Match creation status and match details including match ID
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to create match."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to create match."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to create match."

    if not opponent or opponent.strip() == "":
        return "❌ Opponent name is required to create match."

    if not date or date.strip() == "":
        return "❌ Match date is required to create match."

    if not location or location.strip() == "":
        return "❌ Match location is required to create match."

    try:
        # Get service using simple container access
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ Match service is temporarily unavailable. Please try again later."

        # Create match
        match = match_service.create_match_sync(team_id, opponent.strip(), date.strip(), location.strip())

        if match:
            # Format as simple string response
            date_text = match.date.strftime('%Y-%m-%d %H:%M') if match.date else 'TBD'
            result = "✅ Match Created Successfully!\\n\\n"
            result += f"• Match ID: {match.match_id}\\n"
            result += f"• Opponent: {match.opponent}\\n"
            result += f"• Date: {date_text}\\n"
            result += f"• Location: {match.location}\\n"
            result += f"• Status: {match.status.title()}\\n"
            result += f"• Team: {team_id}\\n\\n"
            result += "🎯 Use this Match ID for squad selection and attendance tracking."
            return result
        else:
            return "❌ Failed to create match. Please check your inputs and try again."

    except Exception as e:
        logger.error(f"Failed to create match: {e}")
        return f"❌ Failed to create match: {e!s}"


@tool("get_match_details")
def get_match_details(telegram_id: int, team_id: str, chat_type: str, match_id: str) -> str:
    """
    Get detailed information about a specific match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to get details for


    :return: Detailed match information including opponent, date, location, and status
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get match details."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get match details."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get match details."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to get match details."

    try:
        # Get service using simple container access
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ Match service is temporarily unavailable. Please try again later."

        # Get match details
        match = match_service.get_match_sync(match_id, team_id)

        if match:
            # Format as simple string response
            date_text = match.date.strftime('%Y-%m-%d %H:%M') if match.date else 'TBD'
            result = "⚽ Match Details\\n\\n"
            result += f"• Match ID: {match.match_id}\\n"
            result += f"• Opponent: {match.opponent}\\n"
            result += f"• Date: {date_text}\\n"
            result += f"• Location: {match.location}\\n"
            result += f"• Status: {match.status.title()}\\n"
            result += f"• Team: {team_id}\\n"

            if hasattr(match, 'squad_size') and match.squad_size:
                result += f"• Squad Size: {match.squad_size}\\n"

            if hasattr(match, 'notes') and match.notes:
                result += f"• Notes: {match.notes}\\n"

            return result
        else:
            return f"❌ Match '{match_id}' not found in team '{team_id}'."

    except Exception as e:
        logger.error(f"Failed to get match details: {e}")
        return f"❌ Failed to get match details: {e!s}"


@tool("select_squad")
def select_squad(telegram_id: int, team_id: str, chat_type: str, match_id: str, player_ids: str) -> str:
    """
    Select squad for a match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID for squad selection
        player_ids (str): Comma-separated list of player IDs to include in squad


    :return: Squad selection status and selected player list with positions
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

    if not player_ids or player_ids.strip() == "":
        return "❌ Player IDs are required to select squad."

    try:
        # Parse player IDs from comma-separated string
        player_id_list = [pid.strip() for pid in player_ids.split(",") if pid.strip()]

        if not player_id_list:
            return "❌ At least one player ID is required to select squad."

        # Get service using simple container access
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ Match service is temporarily unavailable. Please try again later."

        # Select squad
        success = match_service.select_squad_sync(match_id, team_id, player_id_list)

        if success:
            result = "✅ Squad Selected Successfully!\\n\\n"
            result += f"• Match ID: {match_id}\\n"
            result += f"• Team: {team_id}\\n"
            result += f"• Squad Size: {len(player_id_list)} players\\n"
            result += f"• Selected Players: {', '.join(player_id_list)}\\n\\n"
            result += "🎯 Squad is now set for the match. Players will be notified of their selection."
            return result
        else:
            return "❌ Failed to select squad. Please check that the match exists and try again."

    except Exception as e:
        logger.error(f"Failed to select squad: {e}")
        return f"❌ Failed to select squad: {e!s}"


@tool("record_match_result")
def record_match_result(telegram_id: int, team_id: str, chat_type: str, match_id: str, result: str, score: str = "") -> str:
    """
    Record the result of a match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to record result for
        result (str): Match result (win, loss, draw)
        score (str): Optional score in format "2-1"


    :return: Match result recording status and updated match information
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to record match result."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to record match result."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to record match result."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to record match result."

    if not result or result.strip() == "":
        return "❌ Match result is required (win, loss, or draw)."

    try:
        # Validate result
        valid_results = ["win", "loss", "draw"]
        result_lower = result.strip().lower()
        if result_lower not in valid_results:
            return f"❌ Invalid result '{result}'. Valid results are: win, loss, draw."

        # Get service using simple container access
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ Match service is temporarily unavailable. Please try again later."

        # Record match result
        success = match_service.record_result_sync(
            match_id,
            team_id,
            result_lower,
            score.strip() if score and score.strip() != "" else None
        )

        if success:
            # Format as simple string response
            result_emoji = "🏆" if result_lower == "win" else "😔" if result_lower == "loss" else "🤝"
            result_text = f"{result_emoji} Match Result Recorded!\\n\\n"
            result_text += f"• Match ID: {match_id}\\n"
            result_text += f"• Team: {team_id}\\n"
            result_text += f"• Result: {result_lower.title()}\\n"

            if score and score.strip() != "":
                result_text += f"• Score: {score.strip()}\\n"

            result_text += "\\n📊 Match result has been recorded and will be included in team statistics."
            return result_text
        else:
            return "❌ Failed to record match result. Please check that the match exists and try again."

    except Exception as e:
        logger.error(f"Failed to record match result: {e}")
        return f"❌ Failed to record match result: {e!s}"
