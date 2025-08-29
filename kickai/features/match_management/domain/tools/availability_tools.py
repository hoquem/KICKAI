#!/usr/bin/env python3
"""
Availability Management Tools

This module provides tools for managing player availability for matches.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio
import logging
from typing import Optional

from crewai.tools import tool
from kickai.core.dependency_container import get_container
from kickai.utils.tool_validation import create_tool_response

from kickai.features.match_management.domain.entities.availability import AvailabilityStatus
from kickai.features.match_management.domain.services.availability_service import (
    AvailabilityService,
)

logger = logging.getLogger(__name__)


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def mark_availability(
    match_id: str,
    player_id: str,
    status: str,  # available, unavailable, maybe
    reason: Optional[str] = None,
) -> str:
    """Mark player availability for a match.
    
    Records a player's availability status for a specific match
    with optional reason for unavailability.
    
    :param match_id: The unique match identifier
    :type match_id: str
    :param player_id: The player ID (format: 01MH)
    :type player_id: str
    :param status: Availability status (available, unavailable, maybe)
    :type status: str
    :param reason: Optional reason for unavailability or uncertainty
    :type reason: Optional[str]
    :returns: JSON string with updated availability and team summary
    :rtype: str
    :raises ValueError: When status is not valid
    :raises Exception: When availability service fails
    
    .. example::
       >>> result = mark_availability("MATCH001", "01MH", "available")
       >>> print(result)
       '{"status": "success", "data": "Availability Updated..."}
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)

        # Convert status string to enum
        try:
            availability_status = AvailabilityStatus(status.lower())
        except ValueError:
            return create_tool_response(False, f"Invalid status: {status}. Valid options: available, unavailable, maybe")

        # Mark availability
        availability = await availability_service.mark_availability(
            match_id=match_id,
            player_id=player_id,
            status=availability_status,
            reason=reason,
        )

        # Get availability summary for the match
        summary = await availability_service.get_availability_summary(match_id)

        result = [
            "Availability Updated",
            "",
            f"Match: {match_id}",
            f"Your Status: {availability.status_emoji} {availability_status.value.title()}",
        ]

        if reason:
            result.append(f"Reason: {reason}")

        result.extend([
            "",
            "📊 Team Availability",
            f"• Available: {summary['available']} players",
            f"• Unavailable: {summary['unavailable']} players",
            f"• Maybe: {summary['maybe']} players",
            f"• Pending: {summary['pending']} players",
            "",
            "💡 Tip: You can update your availability anytime before squad selection",
        ])

        return create_tool_response(True, "Operation completed successfully", data="\n".join(result))

    except Exception as e:
        logger.error(f"Failed to mark availability: {e}")
        return create_tool_response(False, f"Error marking availability: {e!s}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_availability(match_id: str) -> str:
    """Get availability information for a match.
    
    Retrieves comprehensive availability status for all players
    for a specific match, grouped by status.
    
    :param match_id: The unique match identifier
    :type match_id: str
    :returns: JSON string with detailed availability breakdown
    :rtype: str
    :raises Exception: When availability service fails
    
    .. note::
       Shows players grouped by status: Available, Unavailable,
       Maybe, and Pending (not yet responded)
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)

        # Get availability summary
        summary = await availability_service.get_availability_summary(match_id)

        # Get availability records by status
        available_players = await availability_service.get_available_players(match_id)
        unavailable_players = await availability_service.get_unavailable_players(match_id)
        maybe_players = await availability_service.get_maybe_players(match_id)
        pending_players = await availability_service.get_pending_players(match_id)

        result = [
            f"📊 Match Availability: {match_id}",
            "",
            f"Total Players: {summary['total_players']}",
            "",
        ]

        # Available players
        if available_players:
            result.append(f"✅ Available ({len(available_players)}):")
            for availability in available_players:
                result.append(f"• {availability.player_id}")
            result.append("")

        # Unavailable players
        if unavailable_players:
            result.append(f"❌ Unavailable ({len(unavailable_players)}):")
            for availability in unavailable_players:
                result.append(f"• {availability.player_id}")
                if availability.reason:
                    result.append(f"  - Reason: {availability.reason}")
            result.append("")

        # Maybe players
        if maybe_players:
            result.append(f"❓ Maybe ({len(maybe_players)}):")
            for availability in maybe_players:
                result.append(f"• {availability.player_id}")
                if availability.reason:
                    result.append(f"  - Reason: {availability.reason}")
            result.append("")

        # Pending players
        if pending_players:
            result.append(f"⏳ Pending ({len(pending_players)}):")
            for availability in pending_players:
                result.append(f"• {availability.player_id}")
            result.append("")

        result.append("📋 Actions")
        result.append("• /markattendance [match_id] [status] - Mark your availability")

        return create_tool_response(True, "Operation completed successfully", data="\n".join(result))

    except Exception as e:
        logger.error(f"Failed to get availability: {e}")
        return create_tool_response(False, f"Error getting availability: {e!s}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_player_availability_history(
    player_id: str,
    limit: int = 10,
) -> str:
    """Get availability history for a player.
    
    Retrieves historical availability records for a player
    including statistics and reliability rating.
    
    :param player_id: The player ID (format: 01MH)
    :type player_id: str
    :param limit: Maximum number of matches to retrieve, defaults to 10
    :type limit: int
    :returns: JSON string with availability history and statistics
    :rtype: str
    :raises Exception: When availability service fails
    
    .. note::
       Includes availability rate calculation and reliability
       rating from 1-5 stars based on historical attendance
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)
        history = await availability_service.get_player_history(player_id, limit)

        if not history:
            return create_tool_response(True, "Operation completed successfully", data=f"📈 Availability History\n\nNo availability records found for player {player_id}.")

        result = [
            f"📈 Availability History for {player_id}",
            "",
            f"Last {len(history)} matches:",
            "",
        ]

        for availability in history:
            result.append(
                f"{availability.status_emoji} Match {availability.match_id} - {availability.status.value.title()}"
            )
            if availability.reason:
                result.append(f"  - Reason: {availability.reason}")

        # Calculate statistics
        total_matches = len(history)
        available_count = len([a for a in history if a.is_available])
        unavailable_count = len([a for a in history if a.is_unavailable])
        maybe_count = len([a for a in history if a.is_maybe])

        availability_rate = (available_count / total_matches) * 100 if total_matches > 0 else 0

        result.extend([
            "",
            "📊 Statistics",
            f"• Availability Rate: {availability_rate:.1f}% ({available_count}/{total_matches} matches)",
            f"• Available: {available_count} matches",
            f"• Unavailable: {unavailable_count} matches",
            f"• Maybe: {maybe_count} matches",
        ])

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

        result.append(f"• Reliability Rating: {reliability}")

        return create_tool_response(True, "Operation completed successfully", data="\n".join(result))

    except Exception as e:
        logger.error(f"Failed to get player availability history: {e}")
        return create_tool_response(False, f"Error getting availability history: {e!s}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def send_availability_reminders(match_id: str) -> str:
    """Send availability reminders for a match.
    
    Sends reminder notifications to all players who have not yet
    responded to availability requests for a specific match.
    
    :param match_id: The unique match identifier
    :type match_id: str
    :returns: JSON string with reminder status and count
    :rtype: str
    :raises Exception: When reminder service fails
    
    .. note::
       Only sends reminders to players with pending status
    """
    try:
        container = get_container()
        availability_service: AvailabilityService = container.get_service(AvailabilityService)
        success = await availability_service.send_availability_reminders(match_id)

        if success:
            pending_players = await availability_service.get_pending_players(match_id)
            message = f"Reminders sent to {len(pending_players)} players who haven't responded to availability requests for match {match_id}."
            return create_tool_response(True, "Operation completed successfully", data=f"Reminders Sent\n\n{message}")
        else:
            return create_tool_response(False, f"Unable to send availability reminders for match {match_id}.")

    except Exception as e:
        logger.error(f"Failed to send reminders: {e}")
        return create_tool_response(False, f"Error sending reminders: {e!s}")
