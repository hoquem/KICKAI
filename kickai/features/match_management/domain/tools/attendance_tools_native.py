#!/usr/bin/env python3
"""
Attendance Tools - Native CrewAI Implementation

This module provides tools for managing match attendance using ONLY CrewAI native patterns.
"""

from datetime import time

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.match_management.domain.entities.attendance import AttendanceStatus
from kickai.features.match_management.domain.services.attendance_service import AttendanceService


@tool("record_attendance")
def record_attendance(
    telegram_id: int,
    team_id: str,
    chat_type: str,
    match_id: str,
    player_id: str,
    status: str,
    reason: str = "",
    recorded_by: str = "",
    arrival_time: str = ""
) -> str:
    """
    Record actual attendance for a player at a match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to record attendance for
        player_id (str): Player ID to record attendance for
        status (str): Attendance status (attended, absent, late)
        reason (str): Optional reason for attendance status
        recorded_by (str): Person recording the attendance
        arrival_time (str): Optional arrival time in HH:MM format


    :return: Attendance record and match summary
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to record attendance."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to record attendance."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to record attendance."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to record attendance."

    if not player_id or player_id.strip() == "":
        return "❌ Player ID is required to record attendance."

    if not status or status.strip() == "":
        return "❌ Attendance status is required (attended, absent, late)."

    try:
        # Validate status
        valid_statuses = ["attended", "absent", "late"]
        status_lower = status.strip().lower()
        if status_lower not in valid_statuses:
            return f"❌ Invalid status '{status}'. Valid options: attended, absent, late"

        # Get service using simple container access
        container = get_container()
        attendance_service = container.get_service(AttendanceService)

        if not attendance_service:
            return "❌ Attendance service is temporarily unavailable. Please try again later."

        # Convert status string to enum
        attendance_status = AttendanceStatus(status_lower)

        # Parse arrival time if provided
        arrival_time_obj = None
        if arrival_time and arrival_time.strip() != "":
            try:
                arrival_time_obj = time.fromisoformat(arrival_time.strip())
            except ValueError:
                return f"❌ Invalid arrival time format: {arrival_time}. Use HH:MM format (e.g., 14:30)."

        # Record attendance
        attendance = attendance_service.record_attendance(
            match_id=match_id.strip(),
            player_id=player_id.strip(),
            status=attendance_status,
            reason=reason.strip() if reason and reason.strip() != "" else None,
            recorded_by=recorded_by.strip() if recorded_by and recorded_by.strip() != "" else "System",
            arrival_time=arrival_time_obj,
        )

        # Get attendance summary for the match
        summary = attendance_service.get_attendance_summary(match_id.strip())

        # Format as simple string response
        result = "✅ Match Attendance Recorded\\n\\n"
        result += f"• Match: {match_id}\\n"
        result += f"• Player: {player_id}\\n"
        result += f"• Status: {attendance.status_emoji} {status_lower.title()}\\n"

        if reason and reason.strip() != "":
            result += f"• Reason: {reason.strip()}\\n"

        if arrival_time_obj:
            result += f"• Arrival Time: {attendance.formatted_arrival_time}\\n"

        result += f"• Recorded By: {recorded_by.strip() if recorded_by and recorded_by.strip() != '' else 'System'}\\n"
        result += f"• Time: {attendance.recorded_at.strftime('%H:%M')}\\n\\n"

        result += "📊 Match Summary:\\n"
        result += f"• Attended: {summary['attended']} players\\n"
        result += f"• Absent: {summary['absent']} players\\n"
        result += f"• Late: {summary['late']} players\\n"
        result += f"• Pending: {summary['not_recorded']} players"

        return result

    except Exception as e:
        logger.error(f"Failed to record attendance: {e}")
        return f"❌ Failed to record attendance: {e!s}"


@tool("get_match_attendance")
def get_match_attendance(telegram_id: int, team_id: str, chat_type: str, match_id: str) -> str:
    """
    Get attendance information for a match.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        match_id (str): Match ID to get attendance for


    :return: Attendance information and player lists
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get match attendance."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get match attendance."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get match attendance."

    if not match_id or match_id.strip() == "":
        return "❌ Match ID is required to get match attendance."

    try:
        # Get service using simple container access
        container = get_container()
        attendance_service = container.get_service(AttendanceService)

        if not attendance_service:
            return "❌ Attendance service is temporarily unavailable. Please try again later."

        # Get attendance summary
        summary = attendance_service.get_attendance_summary(match_id.strip())

        # Get attendance records by status
        attended_players = attendance_service.get_attended_players(match_id.strip())
        absent_players = attendance_service.get_absent_players(match_id.strip())
        late_players = attendance_service.get_late_players(match_id.strip())

        # Format as simple string response
        result = f"📊 Match Attendance: {match_id}\\n\\n"
        result += f"Total Players: {summary['total_players']}\\n\\n"

        # Attended players
        if attended_players:
            result += f"✅ Attended ({len(attended_players)}):\\n"
            for attendance in attended_players:
                result += f"• {attendance.player_id}"
                if attendance.arrival_time:
                    result += f" (Arrived: {attendance.formatted_arrival_time})"
                result += "\\n"
            result += "\\n"

        # Absent players
        if absent_players:
            result += f"❌ Absent ({len(absent_players)}):\\n"
            for attendance in absent_players:
                result += f"• {attendance.player_id}"
                if attendance.reason:
                    result += f" - {attendance.reason}"
                result += "\\n"
            result += "\\n"

        # Late players
        if late_players:
            result += f"⏰ Late ({len(late_players)}):\\n"
            for attendance in late_players:
                result += f"• {attendance.player_id}"
                if attendance.arrival_time:
                    result += f" (Arrived: {attendance.formatted_arrival_time})"
                if attendance.reason:
                    result += f" - {attendance.reason}"
                result += "\\n"
            result += "\\n"

        result += "📋 Actions:\\n"
        result += "• Use /markmatchattendance [match_id] [player_id] [status] to record attendance"

        return result

    except Exception as e:
        logger.error(f"Failed to get match attendance: {e}")
        return f"❌ Failed to get match attendance: {e!s}"


@tool("get_player_attendance_history")
def get_player_attendance_history(
    telegram_id: int,
    team_id: str,
    chat_type: str,
    player_id: str,
    limit: str = "10"
) -> str:
    """
    Get attendance history for a player.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        player_id (str): Player ID to get history for
        limit (str): Maximum number of records to return (default: 10)


    :return: Player attendance history and statistics
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get attendance history."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get attendance history."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get attendance history."

    if not player_id or player_id.strip() == "":
        return "❌ Player ID is required to get attendance history."

    try:
        # Convert limit to int if provided
        try:
            limit_int = int(limit) if limit and limit.strip() != "" else 10
        except ValueError:
            limit_int = 10

        # Get service using simple container access
        container = get_container()
        attendance_service = container.get_service(AttendanceService)

        if not attendance_service:
            return "❌ Attendance service is temporarily unavailable. Please try again later."

        # Get player attendance history
        history = attendance_service.get_player_attendance_history(player_id.strip(), limit_int)

        if not history:
            return f"📈 Attendance History\\n\\nNo attendance records found for player {player_id}."

        # Calculate statistics
        stats = attendance_service.calculate_attendance_stats(player_id.strip())

        # Format as simple string response
        result = f"📈 Attendance History for {player_id}\\n\\n"
        result += f"Last {len(history)} matches:\\n\\n"

        for attendance in history:
            result += f"{attendance.status_emoji} Match {attendance.match_id} - {attendance.status.value.title()}\\n"
            if attendance.arrival_time:
                result += f"  Arrived: {attendance.formatted_arrival_time}\\n"
            if attendance.reason:
                result += f"  Reason: {attendance.reason}\\n"

        result += "\\n📊 Statistics:\\n"
        result += f"• Attendance Rate: {stats['attendance_rate']}% ({stats['attended']}/{stats['total_matches']} matches)\\n"
        result += f"• Attended: {stats['attended']} matches\\n"
        result += f"• Absent: {stats['absent']} matches\\n"
        result += f"• Late: {stats['late']} matches\\n"
        result += f"• Reliability Rating: {stats['reliability_rating']}"

        return result

    except Exception as e:
        logger.error(f"Failed to get player attendance history: {e}")
        return f"❌ Failed to get player attendance history: {e!s}"
