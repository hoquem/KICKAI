#!/usr/bin/env python3
"""
Match Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for match management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import List, Optional
from crewai.tools import tool
from loguru import logger
from datetime import datetime, time

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.match_management.domain.services.match_service import MatchService
from kickai.utils.tool_helpers import create_json_response


@tool("list_matches", result_as_answer=True)
async def list_matches(telegram_id: int, team_id: str, username: str, chat_type: str, status: str = "all", limit: int = 10) -> str:
    """
    List matches for a team with optional status filter.

    This tool serves as the application boundary for match listing functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        status: Match status filter (upcoming, past, all)
        limit: Maximum number of matches to return

    Returns:
        JSON formatted list of matches
    """
    try:
        logger.info(f"📅 Match list request from {username} ({telegram_id}) in team {team_id}")

        # Get domain service from container and delegate to domain function
        container = get_container()
        match_service = container.get_service(MatchService)

        # Execute domain operation based on status
        if status == "upcoming":
            matches = await match_service.get_upcoming_matches(team_id, limit)
            title = f"📅 UPCOMING MATCHES (Next {len(matches)})"
        elif status == "past":
            matches = await match_service.get_past_matches(team_id, limit)
            title = f"📅 PAST MATCHES (Last {len(matches)})"
        else:
            matches = await match_service.list_matches(team_id, limit=limit)
            title = f"📅 ALL MATCHES (Last {len(matches)})"

        if not matches:
            return create_json_response(ResponseStatus.SUCCESS, data=f"{title}\n\nNo matches found.")

        # Format at application boundary
        result = [title, ""]
        for i, match in enumerate(matches, 1):
            result.append(
                f"{i}️⃣ {match.match_id} - vs {match.opponent}\n"
                f"   📅 {match.formatted_date}\n"
                f"   🕐 {match.formatted_time} | 🏟️ {match.venue}\n"
                f"   📊 Status: {match.status.value.title()}"
            )

        result.append("\n📋 QUICK ACTIONS")
        result.append("• /matchdetails [match_id] - View full details")
        result.append("• /markattendance [match_id] - Mark availability")

        logger.info(f"✅ Listed {len(matches)} matches for team {team_id}")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error listing matches for team {team_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to list matches: {e}")


@tool("create_match", result_as_answer=True)
async def create_match(
    telegram_id: int, 
    team_id: str, 
    username: str, 
    chat_type: str,
    opponent: str,
    match_date: str,  # YYYY-MM-DD format
    match_time_str: str,  # HH:MM format
    venue: str,
    competition: str = "League Match",
    notes: Optional[str] = None
) -> str:
    """
    Create a new match.

    This tool serves as the application boundary for match creation functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Creator's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        opponent: Name of the opposing team
        match_date: Match date in YYYY-MM-DD format
        match_time_str: Match time in HH:MM format
        venue: Match location/venue
        competition: Competition name
        notes: Optional match notes

    Returns:
        JSON formatted match creation result
    """
    try:
        logger.info(f"🏆 Match creation request from {username} ({telegram_id}) in team {team_id}")

        if not all([opponent, match_date, match_time_str, venue]):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Missing required fields: opponent, match_date, match_time, venue"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        match_service = container.get_service(MatchService)

        # Parse date and time at application boundary
        try:
            date_obj = datetime.strptime(match_date, "%Y-%m-%d")
            time_obj = time.fromisoformat(match_time_str)
        except ValueError as e:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Invalid date/time format: {e}"
            )

        # Execute domain operation
        created_match = await match_service.create_match(
            team_id=team_id,
            opponent=opponent,
            match_date=date_obj,
            match_time=time_obj,
            venue=venue,
            competition=competition,
            notes=notes,
            created_by=str(telegram_id)
        )

        # Format response at application boundary
        message = (
            "Match created successfully!\n\n"
            f"🏆 MATCH DETAILS\n• OPPONENT: {created_match.opponent}\n"
            f"• DATE: {created_match.formatted_date}\n• TIME: {created_match.formatted_time}\n"
            f"• VENUE: {created_match.venue}\n• COMPETITION: {created_match.competition}\n"
            f"• MATCH ID: {created_match.match_id}"
        )

        logger.info(f"✅ Match created successfully: {created_match.match_id}")
        return create_json_response(ResponseStatus.SUCCESS, data=message)

    except Exception as e:
        logger.error(f"❌ Error creating match: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to create match: {e}")


@tool("get_match_details", result_as_answer=True)
async def get_match_details(telegram_id: int, team_id: str, username: str, chat_type: str, match_id: str) -> str:
    """
    Get detailed match information.

    This tool serves as the application boundary for match details functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier

    Returns:
        JSON formatted match details
    """
    try:
        logger.info(f"🔍 Match details request for {match_id} from {username} ({telegram_id})")

        if not match_id:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID is required"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        match_service = container.get_service(MatchService)

        # Execute domain operation
        match = await match_service.get_match(match_id)
        
        if not match:
            return create_json_response(
                ResponseStatus.ERROR, 
                message=f"Match not found: {match_id}"
            )

        # Format response at application boundary
        result = [
            f"🏆 MATCH DETAILS: {match.match_id}",
            "",
            f"OPPONENT: {match.opponent}",
            f"DATE: {match.formatted_date}",
            f"TIME: {match.formatted_time}",
            f"VENUE: {match.venue}",
            f"COMPETITION: {match.competition}",
            f"STATUS: {match.status.value.title()}",
        ]

        if match.notes:
            result.append(f"NOTES: {match.notes}")

        if hasattr(match, 'result') and match.result:
            result.append("")
            result.append("📊 MATCH RESULT")
            result.append(f"SCORE: {match.result.home_score} - {match.result.away_score}")
            if hasattr(match.result, 'scorers') and match.result.scorers:
                result.append(f"SCORERS: {', '.join(match.result.scorers)}")
            if hasattr(match.result, 'notes') and match.result.notes:
                result.append(f"NOTES: {match.result.notes}")

        result.append("")
        result.append("📋 ACTIONS")
        result.append("• /markattendance [match_id] - Mark availability")
        result.append("• /selectsquad [match_id] - Select final squad (Leadership only)")

        logger.info(f"✅ Retrieved match details for {match_id}")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error getting match details for {match_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get match details: {e}")


@tool("record_match_result", result_as_answer=True)
async def record_match_result(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    match_id: str,
    home_score: int,
    away_score: int,
    scorers: Optional[List[str]] = None,
    assists: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> str:
    """
    Record match result.

    This tool serves as the application boundary for match result recording functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Recorder's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier
        home_score: Home team score
        away_score: Away team score
        scorers: Optional list of goal scorers
        assists: Optional list of assist providers
        notes: Optional match notes

    Returns:
        JSON formatted result confirmation
    """
    try:
        logger.info(f"📊 Match result recording for {match_id} from {username} ({telegram_id})")

        if not match_id or home_score is None or away_score is None:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID, home_score, and away_score are required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="MatchService is not available"
            )

        # Execute domain operation
        updated_match = await match_service.record_match_result(
            match_id=match_id,
            home_score=home_score,
            away_score=away_score,
            scorers=scorers or [],
            assists=assists or [],
            notes=notes,
            recorded_by=str(telegram_id)
        )

        # Format response at application boundary
        result = [
            "🏆 MATCH RESULT RECORDED",
            "",
            f"MATCH: vs {updated_match.opponent}",
            f"DATE: {updated_match.formatted_date}",
            f"SCORE: {home_score} - {away_score}",
        ]

        if scorers:
            result.append(f"SCORERS: {', '.join(scorers)}")
        if assists:
            result.append(f"ASSISTS: {', '.join(assists)}")
        if notes:
            result.append(f"NOTES: {notes}")

        result.append("")
        result.append("Match result has been recorded and match status updated to completed.")

        logger.info(f"✅ Match result recorded for {match_id}: {home_score}-{away_score}")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error recording match result for {match_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to record match result: {e}")


@tool("select_squad", result_as_answer=True)
async def select_squad(telegram_id: int, team_id: str, username: str, chat_type: str, match_id: str, player_ids: Optional[List[str]] = None) -> str:
    """
    Select squad for a match.

    This tool serves as the application boundary for squad selection functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Selector's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier
        player_ids: Optional list of player IDs to include in squad

    Returns:
        JSON formatted squad selection result
    """
    try:
        logger.info(f"👥 Squad selection request for {match_id} from {username} ({telegram_id})")

        if not match_id:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID is required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="MatchService is not available"
            )

        # Execute domain operation
        match = await match_service.get_match(match_id)
        
        if not match:
            return create_json_response(
                ResponseStatus.ERROR, 
                message=f"Match not found: {match_id}"
            )

        if hasattr(match, 'is_upcoming') and not match.is_upcoming:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Cannot select squad: Match is not in upcoming status"
            )

        # Format response at application boundary (placeholder implementation)
        result = [
            f"👥 SQUAD SELECTION: {match.match_id}",
            "",
            f"MATCH: vs {match.opponent}",
            f"DATE: {match.formatted_date}",
            f"TIME: {match.formatted_time}",
            "",
            "📋 SQUAD SELECTION",
            "Squad selection functionality will be implemented in the next phase.",
            "",
            "AVAILABLE PLAYERS: To be determined from availability data",
            "SELECTED SQUAD: To be selected",
            "",
            "📋 ACTIONS",
            "• /markattendance [match_id] - Mark availability",
            "• /attendance [match_id] - View current availability",
        ]

        logger.info(f"✅ Squad selection initiated for {match_id}")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error selecting squad for {match_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to select squad: {e}")


@tool("get_available_players_for_match", result_as_answer=True)
async def get_available_players_for_match(telegram_id: int, team_id: str, username: str, chat_type: str, match_id: str) -> str:
    """
    Get available players for a specific match.

    This tool serves as the application boundary for match availability functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        match_id: The unique match identifier

    Returns:
        JSON formatted available players list
    """
    try:
        logger.info(f"👥 Available players request for {match_id} from {username} ({telegram_id})")

        if not match_id:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Match ID is required"
            )

        # Get required services from container (application boundary)
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="MatchService is not available"
            )

        # Execute domain operation
        match = await match_service.get_match(match_id)
        
        if not match:
            return create_json_response(
                ResponseStatus.ERROR, 
                message=f"Match not found: {match_id}"
            )

        # Format response at application boundary (placeholder implementation)
        result = [
            f"👥 AVAILABLE PLAYERS: {match.match_id}",
            "",
            f"MATCH: vs {match.opponent}",
            f"DATE: {match.formatted_date}",
            f"TIME: {match.formatted_time}",
            "",
            "📋 PLAYER AVAILABILITY",
            "Player availability functionality will be integrated with attendance management.",
            "",
            "AVAILABLE: To be determined from attendance data",
            "UNAVAILABLE: To be determined from attendance data",
            "PENDING RESPONSE: To be determined from attendance data",
            "",
            "📋 ACTIONS",
            "• /markattendance [match_id] - Mark availability",
            "• /selectsquad [match_id] - Select squad (Leadership only)",
        ]

        logger.info(f"✅ Available players list generated for {match_id}")
        return create_json_response(ResponseStatus.SUCCESS, data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error getting available players for {match_id}: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get available players: {e}")