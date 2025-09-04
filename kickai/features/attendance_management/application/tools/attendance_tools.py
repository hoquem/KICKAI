#!/usr/bin/env python3
"""
Attendance Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for attendance management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Any

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.attendance_management.domain.entities.attendance import (
    AttendanceResponseMethod,
    AttendanceStatus,
)
from kickai.features.attendance_management.domain.services.attendance_service import (
    AttendanceService,
)
from kickai.utils.tool_validation import create_tool_response

# Status mapping constants
STATUS_MAPPING = {
    "available": AttendanceStatus.AVAILABLE,
    "unavailable": AttendanceStatus.UNAVAILABLE,
    "maybe": AttendanceStatus.MAYBE,
    "tentative": AttendanceStatus.MAYBE,
}

ATTENDANCE_STATUS_MAPPING = {
    "present": AttendanceStatus.AVAILABLE,
    "absent": AttendanceStatus.UNAVAILABLE,
}

STATUS_EMOJI = {
    AttendanceStatus.AVAILABLE: "✅",
    AttendanceStatus.UNAVAILABLE: "❌",
    AttendanceStatus.MAYBE: "❓",
}


def _get_attendance_service() -> AttendanceService:
    """Get attendance service from container with error handling."""
    try:
        container = get_container()
        service = container.get_service(AttendanceService)
        if not service:
            raise ValueError("Attendance service not found in container")
        return service
    except Exception as e:
        logger.error(f"Failed to get attendance service: {e}")
        raise


def _format_attendance_record(attendance: Any, include_notes: bool = True) -> str:
    """Format a single attendance record consistently with null safety."""
    try:
        status = getattr(attendance, "status", None)
        match_id = getattr(attendance, "match_id", "Unknown")
        created_at = getattr(attendance, "created_at", None)
        notes = getattr(attendance, "notes", None)

        lines = [
            f"{STATUS_EMOJI.get(status, '📊')} {match_id}",
            f"   📅 {created_at.strftime('%Y-%m-%d %H:%M') if created_at else 'N/A'}",
            f"   📊 Status: {status.value.title() if status and hasattr(status, 'value') else 'Unknown'}",
        ]

        if include_notes and notes:
            lines.append(f"   💬 Notes: {notes}")

        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"Error formatting attendance record: {e}")
        return f"📊 {getattr(attendance, 'match_id', 'Unknown')} - Formatting Error"


@tool("mark_availability_match")
async def mark_availability_match(
    telegram_id: str, team_id: str, match_id: str, status: str, notes: str | None = None
) -> str:
    """
    Mark player availability for a specific match.

    Business operation to record player availability status for upcoming matches.
    Updates attendance records and provides confirmation to player.

    Use when: Player needs to indicate their availability for a match
    Required: Player must be registered, match must exist

    Returns: Confirmation of availability status with match details
    """
    try:
        # Input validation with enhanced security
        if not telegram_id or not str(telegram_id).strip():
            return create_tool_response(False, "User identification is required")

        if not team_id or not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not match_id or not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        if not status or not status.strip():
            return create_tool_response(False, "Status is required")

        # Convert telegram_id to int with validation
        try:
            telegram_id_int = int(telegram_id)
            if telegram_id_int <= 0:
                return create_tool_response(False, "Invalid user ID format")
        except (ValueError, TypeError):
            return create_tool_response(False, "Invalid user ID format")

        logger.info(f"📊 Availability marking for {match_id} from player {telegram_id_int}")

        # Map string status to enum
        attendance_status = STATUS_MAPPING.get(status.lower())
        if not attendance_status:
            return create_tool_response(
                False, f"Invalid status. Use: {', '.join(STATUS_MAPPING.keys())}"
            )

        # Get required services from container with error handling
        try:
            attendance_service = _get_attendance_service()
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return create_tool_response(False, "Service temporarily unavailable")

        # Execute domain operation
        attendance = await attendance_service.mark_attendance(
            player_id=str(telegram_id_int),
            match_id=match_id,
            status=attendance_status,
            team_id=team_id,
            response_method=AttendanceResponseMethod.COMMAND,
            notes=notes,
            marked_by=str(telegram_id_int),
        )

        # Format response using constants
        message = f"""📊 Availability Marked

{STATUS_EMOJI.get(attendance_status, "📊")} Status: {attendance_status.value.title()}
🏆 Match ID: {match_id}
👤 Player: {telegram_id_int}
📅 Marked: {attendance.created_at.strftime('%Y-%m-%d %H:%M')}"""

        if notes:
            message += f"\n💬 Notes: {notes}"

        message += "\n\n✅ Your availability has been recorded successfully!"

        logger.info(
            f"✅ Availability marked for player {telegram_id_int}: {match_id} - {attendance_status.value}"
        )
        return create_tool_response(True, "Operation completed successfully", data=message)

    except Exception as e:
        logger.error(f"❌ Error marking availability for {match_id}: {e}")
        # Avoid exposing internal error details to users
        error_msg = "Failed to mark availability. Please try again or contact support."
        if "not found" in str(e).lower():
            error_msg = f"Match {match_id} not found"
        elif "permission" in str(e).lower() or "access" in str(e).lower():
            error_msg = "Insufficient permissions to mark availability"
        return create_tool_response(False, error_msg)


@tool("get_availability_all")
async def get_availability_all(telegram_id: str, team_id: str, match_id: str) -> str:
    """
    Get comprehensive match availability summary.

    Business operation to display all player availability responses for a match.
    Shows counts and lists of available, unavailable, and tentative players.

    Use when: Need to view team availability status for match planning
    Required: Match must exist, user must have access to team data

    Returns: Complete availability breakdown with player lists and statistics
    """
    try:
        # Input validation with enhanced security
        if not telegram_id or not str(telegram_id).strip():
            return create_tool_response(False, "User identification is required")

        if not team_id or not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not match_id or not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        # Convert telegram_id to int with validation
        try:
            telegram_id_int = int(telegram_id)
            if telegram_id_int <= 0:
                return create_tool_response(False, "Invalid user ID format")
        except (ValueError, TypeError):
            return create_tool_response(False, "Invalid user ID format")

        logger.info(f"📊 Availability query for {match_id} from player {telegram_id_int}")

        # Get required services from container
        attendance_service = _get_attendance_service()

        # Execute domain operation
        attendance_summary = await attendance_service.get_match_attendance_summary(match_id)

        if not attendance_summary:
            return create_tool_response(
                True,
                "Operation completed successfully",
                data=f"📊 Match Availability: {match_id}\n\nNo availability responses recorded yet.",
            )

        # Format response at application boundary
        result = [
            f"📊 Match Availability: {match_id}",
            "",
            f"✅ Available: {attendance_summary.available_count} players",
            f"❌ Unavailable: {attendance_summary.unavailable_count} players",
            f"❓ Maybe/Tentative: {attendance_summary.maybe_count} players",
            f"⏳ No Response: {attendance_summary.no_response_count} players",
            "",
            f"📊 Total Responses: {attendance_summary.total_responses}/{attendance_summary.total_players}",
        ]

        if attendance_summary.available_players:
            result.extend(["", "✅ Available Players:"])
            result.extend([f"• {player}" for player in attendance_summary.available_players])

        if attendance_summary.unavailable_players:
            result.extend(["", "❌ Unavailable Players:"])
            result.extend([f"• {player}" for player in attendance_summary.unavailable_players])

        result.extend(
            [
                "",
                "📋 Actions",
                "• /markattendance [match_id] [status] - Update your availability",
                "• /selectsquad [match_id] - Select squad (Leadership only)",
            ]
        )

        logger.info(f"✅ Availability summary retrieved for {match_id}")
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result)
        )

    except Exception as e:
        logger.error(f"❌ Error getting availability for {match_id}: {e}")
        return create_tool_response(False, f"Failed to get availability: {e}")


@tool("get_player_availability_history")
async def get_player_availability_history(
    telegram_id: str, team_id: str, player_id: str | None = None
) -> str:
    """
    Get comprehensive player attendance history with statistics.

    Business operation to display player's availability patterns and response history.
    Provides insights into player reliability and engagement patterns.

    Use when: Need to review player availability patterns or response history
    Required: Player must exist, requestor must have appropriate access

    Returns: Detailed availability history with statistics and insights
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        # Default to requesting user if no specific player_id provided
        target_player_id = player_id or str(telegram_id_int)

        logger.info(
            f"📊 Availability history request for player {target_player_id} from {telegram_id_int}"
        )

        # Get required services from container
        attendance_service = _get_attendance_service()

        # Execute domain operation
        history = await attendance_service.get_player_attendance_history(target_player_id, team_id)

        if not history:
            return create_tool_response(
                True,
                "Operation completed successfully",
                data=f"📊 Availability History\n\nNo availability history found for player {target_player_id}.",
            )

        # Calculate statistics
        total_matches = len(history)
        available_count = len([h for h in history if h.status == AttendanceStatus.AVAILABLE])
        unavailable_count = len([h for h in history if h.status == AttendanceStatus.UNAVAILABLE])
        maybe_count = len([h for h in history if h.status == AttendanceStatus.MAYBE])

        availability_rate = (available_count / total_matches * 100) if total_matches > 0 else 0

        # Format response
        result = [
            f"📊 Availability History: {target_player_id}",
            "",
            f"📅 Recent Responses (Last {len(history)} matches):",
            "",
        ]

        for attendance in history:
            result.append(_format_attendance_record(attendance))
            result.append("")

        result.extend(
            [
                "📊 Statistics",
                f"• Total Matches: {total_matches}",
                f"• Available: {available_count} ({availability_rate:.1f}%)",
                f"• Unavailable: {unavailable_count}",
                f"• Maybe: {maybe_count}",
                "",
                "📋 Actions",
                "• /markattendance [match_id] [status] - Mark new availability",
                "• /availability [match_id] - View match availability",
            ]
        )

        logger.info(
            f"✅ Availability history retrieved for player {target_player_id}: {total_matches} matches"
        )
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result)
        )

    except Exception as e:
        logger.error(f"❌ Error getting availability history for {target_player_id}: {e}")
        return create_tool_response(False, f"Failed to get availability history: {e}")


@tool("record_attendance_match")
async def record_attendance_match(
    telegram_id: str,
    team_id: str,
    match_id: str,
    player_id: str,
    status: str,
    notes: str | None = None,
) -> str:
    """
    Record actual match attendance for completed matches.

    Business operation to log player's actual presence or absence at matches.
    Used by administrators to track attendance after matches are completed.

    Use when: Recording post-match attendance for completed matches
    Required: Administrator privileges, match must exist, player must be registered

    Returns: Confirmation of recorded attendance with details
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(
            f"📊 Attendance recording for {match_id}, player {player_id} from {telegram_id_int}"
        )

        if not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        if not player_id.strip():
            return create_tool_response(False, "Player ID is required")

        if not status.strip():
            return create_tool_response(False, "Status is required")

        # Map string status to enum for actual attendance
        attendance_status = ATTENDANCE_STATUS_MAPPING.get(status.lower())
        if not attendance_status:
            return create_tool_response(
                False,
                f"Invalid attendance status. Use: {', '.join(ATTENDANCE_STATUS_MAPPING.keys())}",
            )

        # Get required services from container
        attendance_service = _get_attendance_service()

        # Execute domain operation
        attendance = await attendance_service.mark_attendance(
            player_id=player_id,
            match_id=match_id,
            status=attendance_status,
            team_id=team_id,
            response_method=AttendanceResponseMethod.ADMIN,
            notes=notes,
            marked_by=str(telegram_id_int),
        )

        # Format response
        status_text = "Present" if attendance_status == AttendanceStatus.AVAILABLE else "Absent"
        status_emoji = "✅" if attendance_status == AttendanceStatus.AVAILABLE else "❌"

        message = f"""📊 Attendance Recorded

{status_emoji} Status: {status_text}
🏆 Match ID: {match_id}
👤 Player: {player_id}
🔧 Recorded by: {telegram_id_int}
📅 Recorded: {attendance.created_at.strftime('%Y-%m-%d %H:%M')}"""

        if notes:
            message += f"\n💬 Notes: {notes}"

        message += "\n\n✅ Attendance has been recorded successfully!"

        logger.info(f"✅ Attendance recorded: {player_id} - {match_id} - {status_text}")
        return create_tool_response(True, "Operation completed successfully", data=message)

    except Exception as e:
        logger.error(f"❌ Error recording attendance for {match_id}, player {player_id}: {e}")
        return create_tool_response(False, f"Failed to record attendance: {e}")


@tool("get_match_attendance")
async def get_match_attendance(telegram_id: str, team_id: str, match_id: str) -> str:
    """
    Get complete match attendance information with detailed records.

    Business operation to display comprehensive attendance data for a specific match.
    Shows all player responses with timestamps, notes, and response methods.

    Use when: Need detailed match attendance records for analysis or reporting
    Required: Match must exist, user must have access to team data

    Returns: Complete attendance records with player details and summary statistics
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"📊 Match attendance query for {match_id} from player {telegram_id_int}")

        if not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        # Get required services from container
        attendance_service = _get_attendance_service()

        # Execute domain operation
        attendance_records = await attendance_service.get_match_attendance(match_id)

        if not attendance_records:
            return create_tool_response(
                True,
                "Operation completed successfully",
                data=f"📊 Match Attendance: {match_id}\n\nNo attendance records found.",
            )

        # Group records by status
        available = [r for r in attendance_records if r.status == AttendanceStatus.AVAILABLE]
        unavailable = [r for r in attendance_records if r.status == AttendanceStatus.UNAVAILABLE]
        maybe = [r for r in attendance_records if r.status == AttendanceStatus.MAYBE]

        # Format response
        result = [f"📊 Match Attendance: {match_id}", ""]

        if available:
            result.append("✅ Available/Present:")
            for record in available:
                result.append(f"• {record.player_id}")
                if record.notes:
                    result.append(f"  💬 {record.notes}")
            result.append("")

        if unavailable:
            result.append("❌ Unavailable/Absent:")
            for record in unavailable:
                result.append(f"• {record.player_id}")
                if record.notes:
                    result.append(f"  💬 {record.notes}")
            result.append("")

        if maybe:
            result.append("❓ Maybe/Tentative:")
            for record in maybe:
                result.append(f"• {record.player_id}")
                if record.notes:
                    result.append(f"  💬 {record.notes}")
            result.append("")

        result.extend(
            [
                f"📊 Summary: {len(available)} available, {len(unavailable)} unavailable, {len(maybe)} maybe",
                "",
                "📋 Actions",
                "• /recordattendance [match_id] [player_id] [status] - Record actual attendance",
                "• /markattendance [match_id] [status] - Update your availability",
            ]
        )

        logger.info(
            f"✅ Match attendance retrieved for {match_id}: {len(attendance_records)} records"
        )
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result)
        )

    except Exception as e:
        logger.error(f"❌ Error getting match attendance for {match_id}: {e}")
        return create_tool_response(False, f"Failed to get match attendance: {e}")
