#!/usr/bin/env python3
"""
Availability Management Tools - Native CrewAI Implementation

This module provides tools for managing player availability for matches using ONLY CrewAI native patterns.
"""

import asyncio

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.match_management.domain.entities.availability import AvailabilityStatus
from kickai.features.match_management.domain.services.availability_service import (
    AvailabilityService,
)


@tool("mark_availability")
def mark_availability(
    telegram_id: int,
    team_id: str,
    chat_type: str,
    match_id: str,
    player_id: str,
    status: str,
    reason: str = ""
) -> str:
    """
    Mark player availability for a match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to mark availability for
        player_id (str): Player ID marking availability
        status (str): Availability status (available, unavailable, maybe)
        reason (str): Optional reason for availability status


    :return: Availability status and team summary
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to mark availability."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to mark availability."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to mark availability."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to mark availability."

    if not player_id or player_id.strip() == "":
        return "❌ Player ID is required to mark availability."

    if not status or status.strip() == "":
        return "❌ Availability status is required (available, unavailable, maybe)."

    try:
        # Validate status
        valid_statuses = ["available", "unavailable", "maybe"]
        status_lower = status.strip().lower()
        if status_lower not in valid_statuses:
            return f"❌ Invalid status '{status}'. Valid options: available, unavailable, maybe"

        # Get service using simple container access
        container = get_container()
        availability_service = container.get_service(AvailabilityService)

        if not availability_service:
            return "❌ Availability service is temporarily unavailable. Please try again later."

        # Convert status string to enum
        availability_status = AvailabilityStatus(status_lower)

        # Mark availability
        availability = asyncio.run(
            availability_service.mark_availability(
                match_id=match_id.strip(),
                player_id=player_id.strip(),
                status=availability_status,
                reason=reason.strip() if reason and reason.strip() != "" else None,
            )
        )

        # Get availability summary for the match
        summary = asyncio.run(availability_service.get_availability_summary(match_id.strip()))

        # Format as simple string response
        result = "✅ Availability Updated\\n\\n"
        result += f"• Match: {match_id}\\n"
        result += f"• Player: {player_id}\\n"
        result += f"• Status: {availability.status_emoji} {status_lower.title()}\\n"

        if reason and reason.strip() != "":
            result += f"• Reason: {reason.strip()}\\n"

        result += "\\n📊 Team Availability Summary:\\n"
        result += f"• Available: {summary['available']} players\\n"
        result += f"• Unavailable: {summary['unavailable']} players\\n"
        result += f"• Maybe: {summary['maybe']} players\\n"
        result += f"• Pending: {summary['pending']} players\\n\\n"
        result += "💡 Tip: You can update your availability anytime before squad selection."

        return result

    except Exception as e:
        logger.error(f"Failed to mark availability: {e}")
        return f"❌ Failed to mark availability: {e!s}"


@tool("get_availability")
def get_availability(telegram_id: int, team_id: str, chat_type: str, match_id: str) -> str:
    """
    Get availability information for a match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to get availability for


    :return: Availability information and player lists
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get availability."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get availability."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get availability."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to get availability."

    try:
        # Get service using simple container access
        container = get_container()
        availability_service = container.get_service(AvailabilityService)

        if not availability_service:
            return "❌ Availability service is temporarily unavailable. Please try again later."

        # Get availability summary
        summary = asyncio.run(availability_service.get_availability_summary(match_id.strip()))

        # Get availability records by status
        available_players = asyncio.run(availability_service.get_available_players(match_id.strip()))
        unavailable_players = asyncio.run(availability_service.get_unavailable_players(match_id.strip()))
        maybe_players = asyncio.run(availability_service.get_maybe_players(match_id.strip()))
        pending_players = asyncio.run(availability_service.get_pending_players(match_id.strip()))

        # Format as simple string response
        result = f"📊 Match Availability: {match_id}\\n\\n"
        result += f"Total Players: {summary['total_players']}\\n\\n"

        # Available players
        if available_players:
            result += f"✅ Available ({len(available_players)}):\\n"
            for availability in available_players:
                result += f"• {availability.player_id}\\n"
            result += "\\n"

        # Unavailable players
        if unavailable_players:
            result += f"❌ Unavailable ({len(unavailable_players)}):\\n"
            for availability in unavailable_players:
                result += f"• {availability.player_id}"
                if availability.reason:
                    result += f" - {availability.reason}"
                result += "\\n"
            result += "\\n"

        # Maybe players
        if maybe_players:
            result += f"❓ Maybe ({len(maybe_players)}):\\n"
            for availability in maybe_players:
                result += f"• {availability.player_id}"
                if availability.reason:
                    result += f" - {availability.reason}"
                result += "\\n"
            result += "\\n"

        # Pending players
        if pending_players:
            result += f"⏳ Pending ({len(pending_players)}):\\n"
            for availability in pending_players:
                result += f"• {availability.player_id}\\n"
            result += "\\n"

        result += "📋 Actions:\\n"
        result += "• Use /markattendance [match_id] [status] to mark your availability"

        return result

    except Exception as e:
        logger.error(f"Failed to get availability: {e}")
        return f"❌ Failed to get availability: {e!s}"


@tool("get_player_availability_history")
def get_player_availability_history(
    telegram_id: int,
    team_id: str,
    chat_type: str,
    player_id: str,
    limit: str = "10"
) -> str:
    """
    Get availability history for a player.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        player_id (str): Player ID to get history for
        limit (str): Maximum number of records to return (default: 10)


    :return: Player availability history and statistics
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get availability history."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get availability history."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get availability history."

    if not player_id or player_id.strip() == "":
        return "❌ Player ID is required to get availability history."

    try:
        # Convert limit to int if provided
        try:
            limit_int = int(limit) if limit and limit.strip() != "" else 10
        except ValueError:
            limit_int = 10

        # Get service using simple container access
        container = get_container()
        availability_service = container.get_service(AvailabilityService)

        if not availability_service:
            return "❌ Availability service is temporarily unavailable. Please try again later."

        # Get player history
        history = asyncio.run(availability_service.get_player_history(player_id.strip(), limit_int))

        if not history:
            return f"📈 Availability History\\n\\nNo availability records found for player {player_id}."

        # Calculate statistics
        total_matches = len(history)
        available_count = len([a for a in history if a.is_available])
        unavailable_count = len([a for a in history if a.is_unavailable])
        maybe_count = len([a for a in history if a.is_maybe])

        availability_rate = (available_count / total_matches) * 100 if total_matches > 0 else 0

        # Reliability rating
        if availability_rate >= 90:
            reliability = "⭐⭐⭐⭐⭐ (Excellent)"
        elif availability_rate >= 80:
            reliability = "⭐⭐⭐⭐ (Good)"
        elif availability_rate >= 70:
            reliability = "⭐⭐⭐ (Fair)"
        elif availability_rate >= 60:
            reliability = "⭐⭐ (Poor)"
        else:
            reliability = "⭐ (Very Poor)"

        # Format as simple string response
        result = f"📈 Availability History for {player_id}\\n\\n"
        result += f"Last {len(history)} matches:\\n\\n"

        for availability in history:
            result += f"{availability.status_emoji} Match {availability.match_id} - {availability.status.value.title()}\\n"
            if availability.reason:
                result += f"  Reason: {availability.reason}\\n"

        result += "\\n📊 Statistics:\\n"
        result += f"• Availability Rate: {availability_rate:.1f}% ({available_count}/{total_matches} matches)\\n"
        result += f"• Available: {available_count} matches\\n"
        result += f"• Unavailable: {unavailable_count} matches\\n"
        result += f"• Maybe: {maybe_count} matches\\n"
        result += f"• Reliability Rating: {reliability}"

        return result

    except Exception as e:
        logger.error(f"Failed to get player availability history: {e}")
        return f"❌ Failed to get player availability history: {e!s}"


@tool("get_available_players_for_match")
def get_available_players_for_match(telegram_id: int, team_id: str, chat_type: str, match_id: str) -> str:
    """
    Get players available for a specific match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to get available players for


    :return: List of available players for the match
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
        availability_service = container.get_service(AvailabilityService)

        if not availability_service:
            return "❌ Availability service is temporarily unavailable. Please try again later."

        # Get available players
        available_players = asyncio.run(availability_service.get_available_players(match_id.strip()))

        if not available_players:
            return f"👥 Available Players for Match {match_id}\\n\\nNo players are currently marked as available for this match."

        # Format as simple string response
        result = f"👥 Available Players for Match {match_id}\\n\\n"

        for availability in available_players:
            result += f"✅ {availability.player_id}\\n"

        result += f"\\nTotal Available: {len(available_players)} players\\n\\n"
        result += "📋 These players are ready for squad selection."

        return result

    except Exception as e:
        logger.error(f"Failed to get available players: {e}")
        return f"❌ Failed to get available players: {e!s}"
