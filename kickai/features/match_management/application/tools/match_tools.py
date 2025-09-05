#!/usr/bin/env python3
"""
Match Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for match management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from datetime import datetime, time
from typing import Any

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.match_management.domain.interfaces.match_service_interface import IMatchService
from kickai.utils.tool_validation import create_tool_response


def _get_match_service() -> IMatchService:
    """Get match service from container with error handling."""
    try:
        container = get_container()
        service = container.get_service(IMatchService)
        if not service:
            raise ValueError("Match service not found in container")
        return service
    except Exception as e:
        logger.error(f"Failed to get match service: {e}")
        raise


def _format_match_summary(match: Any, index: int | None = None) -> str:
    """Format match summary consistently with null safety."""
    try:
        prefix = f"{index}️⃣ " if index else ""
        match_id = getattr(match, "match_id", "Unknown")
        opponent = getattr(match, "opponent", "TBD")
        formatted_date = getattr(match, "formatted_date", "TBD")
        formatted_time = getattr(match, "formatted_time", "TBD")
        venue = getattr(match, "venue", "TBD")
        status = getattr(match, "status", None)

        status_text = status.value.title() if status and hasattr(status, "value") else "Unknown"

        return (
            f"{prefix}{match_id} - vs {opponent}\n"
            f"   📅 {formatted_date}\n"
            f"   🕐 {formatted_time} | 🏟️ {venue}\n"
            f"   📊 Status: {status_text}"
        )
    except Exception as e:
        logger.warning(f"Error formatting match summary: {e}")
        return f"{prefix if index else ''}Match formatting error"


def _validate_date_time(
    match_date: str, match_time_str: str
) -> tuple[datetime | None, time | None, str]:
    """Validate and parse date and time strings with enhanced validation.

    Returns: (date_obj, time_obj, error_message)
    """
    if not match_date or not isinstance(match_date, str):
        return None, None, "Match date must be provided in YYYY-MM-DD format"

    if not match_time_str or not isinstance(match_time_str, str):
        return None, None, "Match time must be provided in HH:MM format"

    try:
        # Enhanced date validation
        date_obj = datetime.strptime(match_date.strip(), "%Y-%m-%d")

        # Validate date is not in the past (with some tolerance for today)
        today = datetime.now().date()
        if date_obj.date() < today:
            return None, None, "Match date cannot be in the past"

        # Enhanced time validation
        time_obj = time.fromisoformat(match_time_str.strip())

        return date_obj, time_obj, ""
    except ValueError as e:
        logger.warning(f"Date/time validation failed: {e}")
        return None, None, "Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time"


@tool("list_matches_all")
async def list_matches_all(
    telegram_id: str, team_id: str, status: str = "all", limit: int = 10
) -> str:
    """
    Retrieve comprehensive team match schedule with filtering options.

    Business operation to display team's match schedule including upcoming, past,
    or all matches with opponent details, venue information, and current status.

    Use when: Reviewing overall match schedule and planning season strategy
    Required: User must have team access, valid team must exist

    Returns: Formatted match schedule with comprehensive details and action items
    """
    try:
        # Input validation with enhanced security
        if not telegram_id or not str(telegram_id).strip():
            return create_tool_response(False, "User identification is required")

        if not team_id or not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        # Convert telegram_id to int with validation
        try:
            telegram_id_int = int(telegram_id)
            if telegram_id_int <= 0:
                return create_tool_response(False, "Invalid user ID format")
        except (ValueError, TypeError):
            return create_tool_response(False, "Invalid user ID format")

        # Validate limit parameter
        if limit < 1 or limit > 50:  # Reasonable bounds for performance
            limit = 10  # Default fallback

        logger.info(f"📅 Match list request from player {telegram_id_int} in team {team_id}")

        # Get match service with error handling
        try:
            match_service = _get_match_service()
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return create_tool_response(False, "Match service temporarily unavailable")

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
            return create_tool_response(
                True, "Operation completed successfully", data=f"{title}\n\nNo matches found."
            )

        # Format response
        result = [title, ""]
        for i, match in enumerate(matches, 1):
            result.append(_format_match_summary(match, i))

        result.extend(
            [
                "",
                "📋 QUICK ACTIONS",
                "• /matchdetails [match_id] - View full details",
                "• /markattendance [match_id] - Mark availability",
            ]
        )

        logger.info(f"✅ Listed {len(matches)} matches for team {team_id}")
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result)
        )

    except Exception as e:
        logger.error(f"❌ Error listing matches for team {team_id}: {e}")
        return create_tool_response(False, f"Failed to list matches: {e}")


@tool("create_match")
async def create_match(
    telegram_id: str,
    team_id: str,
    opponent: str,
    match_date: str,
    match_time_str: str,
    venue: str,
    competition: str = "League Match",
    notes: str | None = None,
) -> str:
    """
    Schedule official match with comprehensive details and preparation workflow.

    Business operation to create comprehensive match records including opponent details,
    venue, competition type, and scheduling information for team preparation.

    Use when: Confirming competition fixtures and official match schedules
    Required: Leadership privileges, all match details must be provided

    Returns: Match creation confirmation with comprehensive details and unique match ID
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"🏆 Match creation request from player {telegram_id_int} in team {team_id}")

        # Enhanced input validation with security checks
        if not telegram_id or not str(telegram_id).strip():
            return create_tool_response(False, "User identification is required")

        if not team_id or not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not opponent or not opponent.strip():
            return create_tool_response(False, "Opponent name is required")

        if not match_date or not match_date.strip():
            return create_tool_response(False, "Match date is required")

        if not match_time_str or not match_time_str.strip():
            return create_tool_response(False, "Match time is required")

        if not venue or not venue.strip():
            return create_tool_response(False, "Venue is required")

        # Validate field lengths for security
        if len(opponent) > 100:
            return create_tool_response(False, "Opponent name is too long (maximum 100 characters)")

        if len(venue) > 200:
            return create_tool_response(False, "Venue name is too long (maximum 200 characters)")

        if len(competition) > 100:
            return create_tool_response(
                False, "Competition name is too long (maximum 100 characters)"
            )

        if notes and len(notes) > 500:
            return create_tool_response(False, "Notes are too long (maximum 500 characters)")

        # Parse date and time
        date_obj, time_obj, error_msg = _validate_date_time(match_date, match_time_str)
        if error_msg:
            return create_tool_response(False, error_msg)

        # Get match service
        match_service = _get_match_service()

        # Execute domain operation
        created_match = await match_service.create_match(
            team_id=team_id,
            opponent=opponent,
            match_date=date_obj,
            match_time=time_obj,
            venue=venue,
            competition=competition,
            notes=notes,
            created_by=str(telegram_id_int),
        )

        # Format response
        message = f"""🏆 MATCH CREATED SUCCESSFULLY

• OPPONENT: {created_match.opponent}
• DATE: {created_match.formatted_date}
• TIME: {created_match.formatted_time}
• VENUE: {created_match.venue}
• COMPETITION: {created_match.competition}
• MATCH ID: {created_match.match_id}

✅ Match has been scheduled and is ready for availability collection."""

        logger.info(f"✅ Match created successfully: {created_match.match_id}")
        return create_tool_response(True, "Match created successfully", data=message)

    except Exception as e:
        logger.error(f"❌ Error creating match: {e}")
        return create_tool_response(False, f"Failed to create match: {e}")


@tool("get_match_details")
async def get_match_details(telegram_id: str, team_id: str, match_id: str) -> str:
    """
    Retrieve comprehensive match information for preparation and coordination.

    Business operation to provide complete match details including opponent information,
    venue, timing, competition type, and current status for team coordination.

    Use when: Need complete match information for preparation or planning
    Required: Match must exist, user must have team access

    Returns: Comprehensive match information with preparation insights and action items
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"🔍 Match details request for {match_id} from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        # Get match service
        match_service = _get_match_service()

        # Execute domain operation
        match = await match_service.get_match(match_id)

        if not match:
            return create_tool_response(False, f"Match not found: {match_id}")

        # Format response
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

        # Add match result if available
        if hasattr(match, "result") and match.result:
            result.extend(
                [
                    "",
                    "📊 MATCH RESULT",
                    f"SCORE: {match.result.home_score} - {match.result.away_score}",
                ]
            )

            if hasattr(match.result, "scorers") and match.result.scorers:
                result.append(f"SCORERS: {', '.join(match.result.scorers)}")
            if hasattr(match.result, "notes") and match.result.notes:
                result.append(f"NOTES: {match.result.notes}")

        result.extend(
            [
                "",
                "📋 ACTIONS",
                "• /markattendance [match_id] - Mark availability",
                "• /selectsquad [match_id] - Select final squad (Leadership only)",
            ]
        )

        logger.info(f"✅ Retrieved match details for {match_id}")
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result)
        )

    except Exception as e:
        logger.error(f"❌ Error getting match details for {match_id}: {e}")
        return create_tool_response(False, f"Failed to get match details: {e}")


@tool("record_match_result")
async def record_match_result(
    telegram_id: str,
    team_id: str,
    match_id: str,
    home_score: int,
    away_score: int,
    scorers: list[str] | None = None,
    assists: list[str] | None = None,
    notes: str | None = None,
) -> str:
    """
    Record official match result with comprehensive scoring details.

    Business operation to capture final match outcomes including scores, goal scorers,
    assists, and match notes for historical records and performance analysis.

    Use when: Recording final match outcomes after completion
    Required: Leadership privileges, match must exist, scores must be provided

    Returns: Match result confirmation with comprehensive outcome details
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"📊 Match result recording for {match_id} from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        if home_score is None or away_score is None:
            return create_tool_response(False, "Both home_score and away_score are required")

        # Get match service
        match_service = _get_match_service()

        # Execute domain operation
        updated_match = await match_service.record_match_result(
            match_id=match_id,
            home_score=home_score,
            away_score=away_score,
            scorers=scorers or [],
            assists=assists or [],
            notes=notes,
            recorded_by=str(telegram_id_int),
        )

        # Format response
        result = [
            "✅ MATCH RESULT RECORDED",
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

        result.extend(["", "Match result has been recorded and match status updated to completed."])

        logger.info(f"✅ Match result recorded for {match_id}: {home_score}-{away_score}")
        return create_tool_response(
            True, "Match result recorded successfully", data="\n".join(result)
        )

    except Exception as e:
        logger.error(f"❌ Error recording match result for {match_id}: {e}")
        return create_tool_response(False, f"Failed to record match result: {e}")


@tool("select_squad_match")
async def select_squad_match(
    telegram_id: str, team_id: str, match_id: str, player_ids: list[str] | None = None
) -> str:
    """
    Finalize match squad selection from available players for tactical preparation.

    Business operation to enable team leadership to select the final playing squad
    from available players considering positions, availability, and tactical requirements.

    Use when: Finalizing match squad after availability collection
    Required: Leadership privileges, match must exist and be upcoming

    Returns: Squad selection confirmation with player details and tactical insights
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"👥 Squad selection request for {match_id} from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        # Get match service
        match_service = _get_match_service()

        # Execute domain operation
        match = await match_service.get_match(match_id)

        if not match:
            return create_tool_response(False, f"Match not found: {match_id}")

        if hasattr(match, "is_upcoming") and not match.is_upcoming:
            return create_tool_response(
                False, "Cannot select squad: Match is not in upcoming status"
            )

        # Format response (placeholder implementation)
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
            "• /availability [match_id] - View current availability",
        ]

        logger.info(f"✅ Squad selection initiated for {match_id}")
        return create_tool_response(True, "Squad selection initiated", data="\n".join(result))

    except Exception as e:
        logger.error(f"❌ Error selecting squad for {match_id}: {e}")
        return create_tool_response(False, f"Failed to select squad: {e}")


@tool("list_squad_available")
async def list_squad_available(telegram_id: str, team_id: str, match_id: str) -> str:
    """
    Retrieve players available for match selection and squad planning.

    Business operation to provide comprehensive availability status for all team players
    including confirmed available, unavailable, and pending responses for squad planning.

    Use when: Squad planning and selection preparation is needed
    Required: Match must exist, user must have team access

    Returns: Player availability status summary with squad planning insights
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"👥 Available players request for {match_id} from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        # Get match service
        match_service = _get_match_service()

        # Execute domain operation
        match = await match_service.get_match(match_id)

        if not match:
            return create_tool_response(False, f"Match not found: {match_id}")

        # Format response (placeholder implementation)
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
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result)
        )

    except Exception as e:
        logger.error(f"❌ Error getting available players for {match_id}: {e}")
        return create_tool_response(False, f"Failed to get available players: {e}")
