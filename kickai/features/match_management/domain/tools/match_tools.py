#!/usr/bin/env python3
"""
Match Management Tools

This module provides tools for match management operations.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio
from typing import List, Optional
from loguru import logger
from datetime import datetime, time

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.core.enums import ResponseStatus
from crewai.tools import tool
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    validate_required_input,
    create_json_response,
)

from kickai.features.match_management.domain.services.match_service import MatchService


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def list_matches(team_id: str, status: str = "all", limit: int = 10) -> str:
    """List matches for a team with optional status filter.
    
    Retrieves and formats a list of team matches, optionally filtered
    by status (upcoming, past, or all matches).
    
    :param team_id: Team ID (required)
    :type team_id: str
    :param status: Match status filter (upcoming, past, all), defaults to "all"
    :type status: str
    :param limit: Maximum number of matches to return, defaults to 10
    :type limit: int
    :returns: JSON string with formatted list of matches or error message
    :rtype: str
    :raises ServiceNotAvailableError: When MatchService is not available
    :raises Exception: When match listing fails
    
    .. note::
       Returns matches sorted by date with quick action commands included
    """
    try:
        # Handle JSON string input using utility functions
        team_id = extract_single_value(team_id, "team_id")
        status = extract_single_value(status, "status") if isinstance(status, str) else status
        limit = extract_single_value(limit, "limit") if isinstance(limit, str) else limit

        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Get services from container
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return create_json_response(ResponseStatus.ERROR, message="MatchService not available")

        # Get matches based on status
        if status == "upcoming":
            matches = await match_service.get_upcoming_matches(team_id, limit)
            title = f"📅 **Upcoming Matches** (Next {len(matches)})"
        elif status == "past":
            matches = await match_service.get_past_matches(team_id, limit)
            title = f"📅 **Past Matches** (Last {len(matches)})"
        else:
            matches = await match_service.list_matches(team_id, limit=limit)
            title = f"📅 **All Matches** (Last {len(matches)})"

        if not matches:
            return create_json_response(ResponseStatus.SUCCESS, data=f"{title}\n\nNo matches found.")

        result = [title, ""]
        for i, match in enumerate(matches, 1):
            result.append(
                f"{i}️⃣ **{match.match_id}** - vs {match.opponent}\n"
                f"   📅 {match.formatted_date}\n"
                f"   🕐 {match.formatted_time} | 🏟️ {match.venue}\n"
                f"   📊 Status: {match.status.value.title()}"
            )

        result.append("\n📋 **Quick Actions**")
        result.append("• /matchdetails [match_id] - View full details")
        result.append("• /markattendance [match_id] - Mark availability")

        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_matches: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to list matches: {e}", exc_info=True)
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to list matches: {e}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def create_match(
    team_id: str,
    opponent: str,
    match_date: str,  # YYYY-MM-DD format
    match_time_str: str,  # HH:MM format
    venue: str,
    competition: str = "League Match",
    notes: Optional[str] = None,
    created_by: str = "",
) -> str:
    """Create a new match.
    
    Creates a new match entry in the system with specified details.
    
    :param team_id: The team identifier
    :type team_id: str
    :param opponent: Name of the opposing team
    :type opponent: str
    :param match_date: Match date in YYYY-MM-DD format
    :type match_date: str
    :param match_time_str: Match time in HH:MM format
    :type match_time_str: str
    :param venue: Match location/venue
    :type venue: str
    :param competition: Competition name, defaults to "League Match"
    :type competition: str
    :param notes: Optional match notes
    :type notes: Optional[str]
    :param created_by: User ID of match creator
    :type created_by: str
    :returns: JSON string with created match details or error message
    :rtype: str
    :raises Exception: When match creation fails or date/time parsing fails
    
    .. example::
       >>> result = create_match("KTI", "City FC", "2024-03-15", "18:00", "Home Stadium")
       >>> print(result)
       '{"status": "success", "data": "Match created successfully!..."}
    """
    
    try:
        # Parse date and time
        date_obj = datetime.strptime(match_date, "%Y-%m-%d")
        time_obj = time.fromisoformat(match_time_str)

        # Create match via service
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response(ResponseStatus.ERROR, message="Match service not available")

        created_match = await match_service.create_match(
                team_id=team_id,
                opponent=opponent,
                match_date=date_obj,
                match_time=time_obj,
                venue=venue,
                competition=competition,
                notes=notes,
                created_by=created_by,
            )

        message = (
            "Match created successfully!\n\n"
            f"🏆 **Match Details**\n• **Opponent**: {created_match.opponent}\n"
            f"• **Date**: {created_match.formatted_date}\n• **Time**: {created_match.formatted_time}\n"
            f"• **Venue**: {created_match.venue}\n• **Competition**: {created_match.competition}\n"
            f"• **Match ID**: {created_match.match_id}"
        )
        return create_json_response(ResponseStatus.SUCCESS, data=message)
    except Exception as e:
        logger.error(f"Failed to create match: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Error creating match: {e!s}")


# Removed list_matches_sync - duplicate of list_matches with no actual sync behavior
# Use list_matches directly instead


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_match_details(match_id: str) -> str:
    """Get detailed match information.
    
    Retrieves comprehensive details about a specific match including
    venue, time, competition, status, and results if available.
    
    :param match_id: The unique match identifier
    :type match_id: str
    :returns: JSON string with match details or error message
    :rtype: str
    :raises Exception: When match not found or service fails
    
    .. note::
       Includes match result and scorer information if match is completed
    """
    
    try:
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response(ResponseStatus.ERROR, message="Match service not available")

        match = await match_service.get_match(match_id)
        if not match:
            return create_json_response(ResponseStatus.ERROR, message=f"Match not found: {match_id}")

        result = [
            f"🏆 **Match Details: {match.match_id}**",
            "",
            f"**Opponent**: {match.opponent}",
            f"**Date**: {match.formatted_date}",
            f"**Time**: {match.formatted_time}",
            f"**Venue**: {match.venue}",
            f"**Competition**: {match.competition}",
            f"**Status**: {match.status.value.title()}",
        ]

        if match.notes:
            result.append(f"**Notes**: {match.notes}")

        if match.result:
            result.append("")
            result.append("📊 **Match Result**")
            result.append(f"**Score**: {match.result.home_score} - {match.result.away_score}")
            if match.result.scorers:
                result.append(f"**Scorers**: {', '.join(match.result.scorers)}")
            if match.result.notes:
                result.append(f"**Notes**: {match.result.notes}")

        result.append("")
        result.append("📋 **Actions**")
        result.append("• /markattendance [match_id] - Mark availability")
        result.append("• /selectsquad [match_id] - Select final squad (Leadership only)")

        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))
    except Exception as e:
        logger.error(f"Failed to get match details: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Error getting match details: {e!s}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def select_squad_tool(match_id: str, player_ids: Optional[List[str]] = None) -> str:
    """Select squad for a match.
    
    Initiates squad selection process for an upcoming match.
    Currently returns placeholder for future implementation.
    
    :param match_id: The unique match identifier
    :type match_id: str
    :param player_ids: Optional list of player IDs to include in squad
    :type player_ids: Optional[List[str]]
    :returns: JSON string with squad selection status or error message
    :rtype: str
    :raises Exception: When match not found or not in upcoming status
    
    .. note::
       Full squad selection functionality to be implemented in next phase
    """
    
    try:
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response(ResponseStatus.ERROR, message="Match service not available")

        match = await match_service.get_match(match_id)
        if not match:
            return create_json_response(ResponseStatus.ERROR, message=f"Match not found: {match_id}")

        if not match.is_upcoming:
            return create_json_response(ResponseStatus.ERROR, message="Cannot select squad: Match is not in upcoming status")

        result = [
            f"👥 **Squad Selection: {match.match_id}**",
            "",
            f"**Match**: vs {match.opponent}",
            f"**Date**: {match.formatted_date}",
            f"**Time**: {match.formatted_time}",
            "",
            "📋 **Squad Selection**",
            "Squad selection functionality will be implemented in the next phase.",
            "",
            "**Available Players**: To be determined from availability data",
            "**Selected Squad**: To be selected",
            "",
            "📋 **Actions**",
            "• /markattendance [match_id] - Mark availability",
            "• /attendance [match_id] - View current availability",
        ]

        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))
    except Exception as e:
        logger.error(f"Failed to select squad: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Error selecting squad: {e!s}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def record_match_result(
    match_id: str,
    home_score: int,
    away_score: int,
    scorers: Optional[List[str]] = None,
    assists: Optional[List[str]] = None,
    notes: Optional[str] = None,
    recorded_by: str = "",
) -> str:
    """Record match result.
    
    Records the final result of a completed match including score,
    scorers, assists, and additional notes.
    
    :param match_id: The unique match identifier
    :type match_id: str
    :param home_score: Home team score
    :type home_score: int
    :param away_score: Away team score
    :type away_score: int
    :param scorers: Optional list of goal scorers
    :type scorers: Optional[List[str]]
    :param assists: Optional list of assist providers
    :type assists: Optional[List[str]]
    :param notes: Optional match notes or highlights
    :type notes: Optional[str]
    :param recorded_by: User ID of person recording result
    :type recorded_by: str
    :returns: JSON string with confirmation or error message
    :rtype: str
    :raises Exception: When match not found, already completed, or recording fails
    
    .. example::
       >>> result = record_match_result("MATCH001", 2, 1, ["01MH", "02JD"])
       >>> print(result)
       '{"status": "success", "data": "Match Result Recorded..."}
    """
    
    try:
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response(ResponseStatus.ERROR, message="Match service not available")

        match = await match_service.get_match(match_id)
        if not match:
            return create_json_response(ResponseStatus.ERROR, message=f"Match not found: {match_id}")

        if match.is_completed:
            return create_json_response(ResponseStatus.ERROR, message="Match already completed: Result already recorded")

        updated_match = await match_service.record_match_result(
                match_id=match_id,
                home_score=home_score,
                away_score=away_score,
                scorers=scorers or [],
                assists=assists or [],
                notes=notes,
                recorded_by=recorded_by,
            )

        result = [
            "🏆 **Match Result Recorded**",
            "",
            f"**Match**: vs {updated_match.opponent}",
            f"**Date**: {updated_match.formatted_date}",
            f"**Score**: {home_score} - {away_score}",
        ]

        if scorers:
            result.append(f"**Scorers**: {', '.join(scorers)}")
        if assists:
            result.append(f"**Assists**: {', '.join(assists)}")
        if notes:
            result.append(f"**Notes**: {notes}")

        result.append("")
        result.append("Match result has been recorded and match status updated to completed.")

        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))
    except Exception as e:
        logger.error(f"Failed to record match result: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Error recording match result: {e!s}")
