#!/usr/bin/env python3
"""
Match Management Tools

This module provides tools for match management operations.
Converted to sync functions for CrewAI compatibility.
"""

from typing import List, Optional
from loguru import logger
from datetime import datetime, time
import asyncio

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    format_tool_success,
    validate_required_input,
    create_json_response,
)

from kickai.features.match_management.domain.services.match_service import MatchService


@tool("list_matches")
def list_matches(team_id: str, status: str = "all", limit: int = 10) -> str:
    """
    List matches for a team with optional status filter. Requires: team_id

    Args:
        team_id: Team ID (required)
        status: Match status filter (upcoming, past, all) - default: all
        limit: Maximum number of matches to return - default: 10

    Returns:
        Formatted list of matches or error message
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
            raise ServiceNotAvailableError("MatchService")

        # Get matches based on status (sync calls via asyncio.run)
        if status == "upcoming":
            matches = asyncio.run(match_service.get_upcoming_matches(team_id, limit))
            title = f"📅 **Upcoming Matches** (Next {len(matches)})"
        elif status == "past":
            matches = asyncio.run(match_service.get_past_matches(team_id, limit))
            title = f"📅 **Past Matches** (Last {len(matches)})"
        else:
            matches = asyncio.run(match_service.list_matches(team_id, limit=limit))
            title = f"📅 **All Matches** (Last {len(matches)})"

        if not matches:
            return create_json_response("success", data=f"{title}\n\nNo matches found.")

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

        return create_json_response("success", data="\n".join(result))

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_matches: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to list matches: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to list matches: {e}")


@tool("create_match")
def create_match(
    team_id: str,
    opponent: str,
    match_date: str,  # YYYY-MM-DD format
    match_time_str: str,  # HH:MM format
    venue: str,
    competition: str = "League Match",
    notes: Optional[str] = None,
    created_by: str = "",
) -> str:
    """Create a new match."""
    try:
        # Parse date and time
        date_obj = datetime.strptime(match_date, "%Y-%m-%d")
        time_obj = time.fromisoformat(match_time_str)

        # Create match via service
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response("error", message="Match service not available")

        created_match = asyncio.run(
            match_service.create_match(
                team_id=team_id,
                opponent=opponent,
                match_date=date_obj,
                match_time=time_obj,
                venue=venue,
                competition=competition,
                notes=notes,
                created_by=created_by,
            )
        )

        message = (
            "Match created successfully!\n\n"
            f"🏆 **Match Details**\n• **Opponent**: {created_match.opponent}\n"
            f"• **Date**: {created_match.formatted_date}\n• **Time**: {created_match.formatted_time}\n"
            f"• **Venue**: {created_match.venue}\n• **Competition**: {created_match.competition}\n"
            f"• **Match ID**: {created_match.match_id}"
        )
        return create_json_response("success", data=message)
    except Exception as e:
        logger.error(f"Failed to create match: {e}")
        return create_json_response("error", message=f"Error creating match: {e!s}")


@tool("list_matches_sync")
def list_matches_sync(team_id: str, status: str = "all", limit: int = 10) -> str:
    """List matches for a team (sync wrapper)."""
    try:
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response("error", message="Match service not available")

        if status == "upcoming":
            matches = asyncio.run(match_service.get_upcoming_matches(team_id, limit))
            title = f"📅 **Upcoming Matches** (Next {len(matches)})"
        elif status == "past":
            matches = asyncio.run(match_service.get_past_matches(team_id, limit))
            title = f"📅 **Past Matches** (Last {len(matches)})"
        else:
            matches = asyncio.run(match_service.list_matches(team_id, limit=limit))
            title = f"📅 **All Matches** (Last {len(matches)})"

        if not matches:
            return create_json_response("success", data=f"{title}\n\nNo matches found.")

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

        return create_json_response("success", data="\n".join(result))
    except Exception as e:
        logger.error(f"Failed to list matches: {e}")
        return create_json_response("error", message=f"Error listing matches: {e!s}")


@tool("get_match_details")
def get_match_details(match_id: str) -> str:
    """Get detailed match information."""
    try:
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response("error", message="Match service not available")

        match = asyncio.run(match_service.get_match(match_id))
        if not match:
            return create_json_response("error", message=f"Match not found: {match_id}")

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

        return create_json_response("success", data="\n".join(result))
    except Exception as e:
        logger.error(f"Failed to get match details: {e}")
        return create_json_response("error", message=f"Error getting match details: {e!s}")


@tool("select_squad_tool")
def select_squad_tool(match_id: str, player_ids: Optional[List[str]] = None) -> str:
    """Select squad for a match."""
    try:
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response("error", message="Match service not available")

        match = asyncio.run(match_service.get_match(match_id))
        if not match:
            return create_json_response("error", message=f"Match not found: {match_id}")

        if not match.is_upcoming:
            return create_json_response("error", message="Cannot select squad: Match is not in upcoming status")

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

        return create_json_response("success", data="\n".join(result))
    except Exception as e:
        logger.error(f"Failed to select squad: {e}")
        return create_json_response("error", message=f"Error selecting squad: {e!s}")


@tool("record_match_result")
def record_match_result(
    match_id: str,
    home_score: int,
    away_score: int,
    scorers: Optional[List[str]] = None,
    assists: Optional[List[str]] = None,
    notes: Optional[str] = None,
    recorded_by: str = "",
) -> str:
    """Record match result."""
    try:
        container = get_container()
        match_service: MatchService = container.get_service(MatchService)
        if not match_service:
            return create_json_response("error", message="Match service not available")

        match = asyncio.run(match_service.get_match(match_id))
        if not match:
            return create_json_response("error", message=f"Match not found: {match_id}")

        if match.is_completed:
            return create_json_response("error", message="Match already completed: Result already recorded")

        updated_match = asyncio.run(
            match_service.record_match_result(
                match_id=match_id,
                home_score=home_score,
                away_score=away_score,
                scorers=scorers or [],
                assists=assists or [],
                notes=notes,
                recorded_by=recorded_by,
            )
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

        return create_json_response("success", data="\n".join(result))
    except Exception as e:
        logger.error(f"Failed to record match result: {e}")
        return create_json_response("error", message=f"Error recording match result: {e!s}")
