#!/usr/bin/env python3
"""
Attendance Management Tools

This module provides tools for player attendance and availability management.
These tools integrate with the attendance service and provide CrewAI agents
with the ability to track and manage player availability for matches.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from kickai.utils.crewai_tool_decorator import tool

from kickai.core.dependency_container import get_container
from kickai.features.attendance_management.domain.entities.attendance import (
    AttendanceStatus,
    AttendanceResponseMethod,
)
from kickai.features.attendance_management.domain.services.attendance_service import AttendanceService
from kickai.features.match_management.domain.services.match_service import MatchService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    format_tool_success,
    sanitize_input,
    validate_required_input,
)

logger = logging.getLogger(__name__)


@tool("mark_attendance")
def mark_attendance(
    team_id: str,
    user_id: str,
    status: str,
    match_id: str = None,
    notes: str = None
) -> str:
    """
    Mark player attendance for a match.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context  
        status: Attendance status (yes, no, maybe)
        match_id: Optional specific match ID (defaults to next match)
        notes: Optional notes about availability
    
    Returns:
        Confirmation message with attendance details
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(status, "Status")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=50)
        status = sanitize_input(status.lower(), max_length=20)
        match_id = sanitize_input(match_id, max_length=50) if match_id else None
        notes = sanitize_input(notes, max_length=500) if notes else None

        # Validate status
        status_mapping = {
            "yes": AttendanceStatus.YES,
            "no": AttendanceStatus.NO,
            "maybe": AttendanceStatus.MAYBE,
            "available": AttendanceStatus.YES,
            "unavailable": AttendanceStatus.NO,
            "tentative": AttendanceStatus.MAYBE,
        }

        if status not in status_mapping:
            return format_tool_error(
                f"Invalid status '{status}'. Valid options: yes, no, maybe, available, unavailable, tentative"
            )

        attendance_status = status_mapping[status]

        # Get services
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        player_service = container.get_service(PlayerService)
        match_service = container.get_service(MatchService)

        if not attendance_service:
            return format_tool_error("Attendance service not available. Please try again later.")

        if not player_service:
            return format_tool_error("Player service not available. Please try again later.")

        # Get player information
        player = player_service.get_player_by_telegram_id(user_id, team_id)
        if not player:
            return format_tool_error(f"Player not found for user {user_id} in team {team_id}")

        player_id = player.player_id

        # Determine match ID if not provided
        if not match_id:
            if match_service:
                # Get next upcoming match
                matches = match_service.list_matches(team_id)
                upcoming_matches = [
                    m for m in matches 
                    if m.status == "scheduled" and 
                    datetime.fromisoformat(m.date.replace('Z', '+00:00')) > datetime.utcnow()
                ]
                
                if upcoming_matches:
                    # Sort by date and get the next match
                    upcoming_matches.sort(key=lambda m: datetime.fromisoformat(m.date.replace('Z', '+00:00')))
                    match_id = upcoming_matches[0].id
                else:
                    return format_tool_error("No upcoming matches found. Please specify a match ID.")
            else:
                return format_tool_error("Match service not available. Please specify a match ID.")

        # Mark attendance
        attendance = attendance_service.mark_attendance(
            player_id=player_id,
            match_id=match_id,
            team_id=team_id,
            status=attendance_status,
            response_method=AttendanceResponseMethod.COMMAND,
            notes=notes,
        )

        # Format response
        status_emoji = attendance.get_status_emoji()
        status_display = attendance.get_status_display()

        response = f"""
✅ **ATTENDANCE MARKED SUCCESSFULLY!**

👤 **Player:** {player.full_name}
📋 **Match ID:** {match_id}
{status_emoji} **Status:** {status_display}
🕐 **Recorded:** {datetime.utcnow().strftime('%H:%M on %d/%m/%Y')}
"""

        if attendance.match_opponent:
            response += f"⚽ **Match:** vs {attendance.match_opponent}\n"

        if attendance.match_date:
            match_date = datetime.fromisoformat(attendance.match_date.replace('Z', '+00:00'))
            response += f"📅 **Date:** {match_date.strftime('%A, %d %B %Y at %H:%M')}\n"

        if notes:
            response += f"📝 **Notes:** {notes}\n"

        response += f"""
📊 **Next Steps:**
• Use `/attendance {match_id}` to see all responses
• Use `/markattendance` to update your status
• Contact team leadership if you have questions

💡 **Tip:** You can change your response anytime before the match.
        """

        logger.info(f"Attendance marked for player {player_id} and match {match_id}: {status}")
        return response.strip()

    except Exception as e:
        logger.error(f"Failed to mark attendance: {e}")
        return format_tool_error(f"Failed to mark attendance: {e!s}")


@tool("get_match_attendance")
def get_match_attendance(team_id: str, user_id: str, match_id: str = None) -> str:
    """
    Get attendance summary for a match.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        match_id: Optional specific match ID (defaults to next match)
    
    Returns:
        Detailed attendance summary for the match
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=50)
        match_id = sanitize_input(match_id, max_length=50) if match_id else None

        # Get services
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        match_service = container.get_service(MatchService)

        if not attendance_service:
            return format_tool_error("Attendance service not available. Please try again later.")

        # Determine match ID if not provided
        if not match_id:
            if match_service:
                matches = match_service.list_matches(team_id)
                upcoming_matches = [
                    m for m in matches 
                    if m.status == "scheduled" and 
                    datetime.fromisoformat(m.date.replace('Z', '+00:00')) > datetime.utcnow()
                ]
                
                if upcoming_matches:
                    upcoming_matches.sort(key=lambda m: datetime.fromisoformat(m.date.replace('Z', '+00:00')))
                    match_id = upcoming_matches[0].id
                else:
                    return format_tool_error("No upcoming matches found. Please specify a match ID.")
            else:
                return format_tool_error("Match service not available. Please specify a match ID.")

        # Get match information
        match = None
        if match_service:
            match = match_service.get_match(match_id)

        # Get attendance summary
        summary = attendance_service.get_match_attendance_summary(match_id, team_id)
        attendance_records = attendance_service.get_attendance_by_match(match_id, team_id)

        # Format response
        response = f"📊 **MATCH ATTENDANCE SUMMARY**\n\n"

        if match:
            match_date = datetime.fromisoformat(match.date.replace('Z', '+00:00'))
            response += f"""📋 **Match Details:**
• **Match ID:** {match_id}
• **Opponent:** {match.opponent}
• **Date:** {match_date.strftime('%A, %d %B %Y')}
• **Time:** {match_date.strftime('%H:%M')}
• **Venue:** {match.home_away or 'TBD'}

"""

        response += f"""📈 **Attendance Statistics:**
• **Total Players:** {summary.total_players}
• **Response Rate:** {summary.response_rate}%

✅ **Available:** {summary.available_count} players
❌ **Unavailable:** {summary.unavailable_count} players
❔ **Maybe:** {summary.maybe_count} players
⏳ **No Response:** {summary.no_response_count} players

"""

        if attendance_records:
            response += "👥 **Player Responses:**\n"
            
            # Group by status
            by_status = {}
            for attendance in attendance_records:
                status = attendance.status
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(attendance)

            # Show available players
            if AttendanceStatus.YES.value in by_status:
                response += "\n✅ **Available Players:**\n"
                for attendance in by_status[AttendanceStatus.YES.value]:
                    response += f"• {attendance.player_name or attendance.player_id}"
                    if attendance.notes:
                        response += f" - {attendance.notes}"
                    response += "\n"

            # Show unavailable players
            if AttendanceStatus.NO.value in by_status:
                response += "\n❌ **Unavailable Players:**\n"
                for attendance in by_status[AttendanceStatus.NO.value]:
                    response += f"• {attendance.player_name or attendance.player_id}"
                    if attendance.notes:
                        response += f" - {attendance.notes}"
                    response += "\n"

            # Show maybe players
            if AttendanceStatus.MAYBE.value in by_status:
                response += "\n❔ **Maybe Players:**\n"
                for attendance in by_status[AttendanceStatus.MAYBE.value]:
                    response += f"• {attendance.player_name or attendance.player_id}"
                    if attendance.notes:
                        response += f" - {attendance.notes}"
                    response += "\n"

            # Show no response players
            if AttendanceStatus.NOT_RESPONDED.value in by_status:
                response += "\n⏳ **No Response Yet:**\n"
                for attendance in by_status[AttendanceStatus.NOT_RESPONDED.value]:
                    response += f"• {attendance.player_name or attendance.player_id}\n"

        response += f"""
📋 **Actions:**
• Use `/markattendance yes/no/maybe` to mark your attendance
• Use `/selectsquad {match_id}` to select match squad (Leadership)
• Use `/remind` to send attendance reminders (Leadership)
        """

        return response.strip()

    except Exception as e:
        logger.error(f"Failed to get match attendance: {e}")
        return format_tool_error(f"Failed to get match attendance: {e!s}")


@tool("get_player_attendance_history")
def get_player_attendance_history(team_id: str, user_id: str, year: str = None) -> str:
    """
    Get player's attendance history and statistics.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        year: Optional year filter (e.g., "2024")
    
    Returns:
        Player's attendance history and statistics
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=50)
        year_filter = None
        if year:
            try:
                year_filter = int(sanitize_input(year, max_length=4))
            except ValueError:
                return format_tool_error(f"Invalid year format: {year}")

        # Get services
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        player_service = container.get_service(PlayerService)

        if not attendance_service:
            return format_tool_error("Attendance service not available. Please try again later.")

        if not player_service:
            return format_tool_error("Player service not available. Please try again later.")

        # Get player information
        player = player_service.get_player_by_telegram_id(user_id, team_id)
        if not player:
            return format_tool_error(f"Player not found for user {user_id} in team {team_id}")

        player_id = player.player_id

        # Get attendance statistics
        stats = attendance_service.get_player_attendance_stats(player_id, team_id, year_filter)
        attendance_records = attendance_service.get_attendance_by_player(player_id, team_id)

        # Filter by year if specified
        if year_filter:
            year_str = str(year_filter)
            attendance_records = [
                a for a in attendance_records
                if a.match_date and a.match_date.startswith(year_str)
            ]

        # Format response
        year_text = f" ({year_filter})" if year_filter else ""
        response = f"""📈 **ATTENDANCE HISTORY{year_text}**

👤 **Player:** {player.full_name}
📊 **Statistics:**
• **Total Matches:** {stats.get('total_matches', 0)}
• **Attended:** {stats.get('attended', 0)} matches
• **Missed:** {stats.get('missed', 0)} matches
• **Maybe Responses:** {stats.get('maybe_responses', 0)}
• **No Responses:** {stats.get('no_responses', 0)}
• **Attendance Rate:** {stats.get('attendance_rate', 0)}%
• **Response Rate:** {stats.get('response_rate', 0)}%

"""

        if attendance_records:
            # Sort by match date (most recent first)
            attendance_records.sort(
                key=lambda a: a.match_date or "0000-00-00", 
                reverse=True
            )

            response += "📋 **Recent Matches:**\n"
            for attendance in attendance_records[:10]:  # Show last 10 matches
                status_emoji = attendance.get_status_emoji()
                status_display = attendance.get_status_display()
                
                match_info = ""
                if attendance.match_opponent:
                    match_info += f"vs {attendance.match_opponent}"
                if attendance.match_date:
                    try:
                        match_date = datetime.fromisoformat(attendance.match_date.replace('Z', '+00:00'))
                        match_info += f" on {match_date.strftime('%d/%m/%Y')}"
                    except:
                        pass

                response += f"• {status_emoji} {status_display} - {match_info or attendance.match_id}\n"

            if len(attendance_records) > 10:
                response += f"\n... and {len(attendance_records) - 10} more matches\n"

        response += f"""
🎯 **Performance Insights:**
"""

        # Add performance insights
        if stats.get('total_matches', 0) > 0:
            attendance_rate = stats.get('attendance_rate', 0)
            if attendance_rate >= 80:
                response += "• 🌟 Excellent attendance! You're a reliable team player.\n"
            elif attendance_rate >= 60:
                response += "• 👍 Good attendance! Keep up the consistent participation.\n"
            elif attendance_rate >= 40:
                response += "• 📈 Room for improvement. Try to attend more matches.\n"
            else:
                response += "• 📉 Low attendance. Consider improving your availability.\n"

            response_rate = stats.get('response_rate', 0)
            if response_rate >= 90:
                response += "• 📱 Great at responding! You help with match planning.\n"
            elif response_rate < 70:
                response += "• ⏰ Try to respond to match invitations more quickly.\n"

        response += f"""
📋 **Actions:**
• Use `/markattendance` to mark availability for upcoming matches
• Use `/attendance` to see team attendance for matches
        """

        return response.strip()

    except Exception as e:
        logger.error(f"Failed to get player attendance history: {e}")
        return format_tool_error(f"Failed to get player attendance history: {e!s}")


@tool("initialize_match_attendance")
def initialize_match_attendance(team_id: str, user_id: str, match_id: str) -> str:
    """
    Initialize attendance tracking for a match (Leadership only).
    Creates attendance records for all active players.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        match_id: Match ID to initialize attendance for
    
    Returns:
        Confirmation message with initialization details
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=50)
        match_id = sanitize_input(match_id, max_length=50)

        # Get services
        container = get_container()
        attendance_service = container.get_service(AttendanceService)
        match_service = container.get_service(MatchService)

        if not attendance_service:
            return format_tool_error("Attendance service not available. Please try again later.")

        # Get match information
        match = None
        if match_service:
            match = match_service.get_match(match_id)
            if not match:
                return format_tool_error(f"Match {match_id} not found")

        # Initialize attendance for all active players
        attendance_records = attendance_service.initialize_match_attendance(match_id, team_id)

        if not attendance_records:
            return format_tool_error("Failed to initialize attendance. No active players found.")

        # Format response
        response = f"""✅ **ATTENDANCE INITIALIZED SUCCESSFULLY!**

📋 **Match Details:**
• **Match ID:** {match_id}
"""

        if match:
            match_date = datetime.fromisoformat(match.date.replace('Z', '+00:00'))
            response += f"""• **Opponent:** {match.opponent}
• **Date:** {match_date.strftime('%A, %d %B %Y')}
• **Time:** {match_date.strftime('%H:%M')}
"""

        response += f"""
👥 **Attendance Setup:**
• **Players Added:** {len(attendance_records)}
• **Initial Status:** All players set to "No Response"
• **Collection Started:** Players can now mark their attendance

📋 **Next Steps:**
• Use `/announce` to notify players about the match
• Use `/attendance {match_id}` to track responses
• Use `/remind` to send attendance reminders
• Players can use `/markattendance` to respond

💡 **Tip:** Players will be automatically notified to mark their attendance.
        """

        logger.info(f"Attendance initialized for match {match_id} with {len(attendance_records)} players")
        return response.strip()

    except Exception as e:
        logger.error(f"Failed to initialize match attendance: {e}")
        return format_tool_error(f"Failed to initialize match attendance: {e!s}")


@tool("get_team_attendance_summary")
def get_team_attendance_summary(team_id: str, user_id: str) -> str:
    """
    Get overall team attendance summary and statistics.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
    
    Returns:
        Team attendance summary with key metrics
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=50)

        # Get services
        container = get_container()
        attendance_service = container.get_service(AttendanceService)

        if not attendance_service:
            return format_tool_error("Attendance service not available. Please try again later.")

        # Get team attendance summary
        summary = attendance_service.get_team_attendance_summary(team_id)

        if not summary or summary.get('total_records', 0) == 0:
            return format_tool_error("No attendance data found for this team.")

        # Format response
        response = f"""📊 **TEAM ATTENDANCE SUMMARY**

🏆 **Team:** {team_id.upper()}
📈 **Overall Statistics:**
• **Total Records:** {summary.get('total_records', 0)}
• **Responded:** {summary.get('responded_count', 0)} responses
• **Available:** {summary.get('available_count', 0)} attendances
• **Response Rate:** {summary.get('overall_response_rate', 0)}%
• **Attendance Rate:** {summary.get('overall_attendance_rate', 0)}%

🎯 **Team Performance:**
"""

        # Add performance insights
        response_rate = summary.get('overall_response_rate', 0)
        attendance_rate = summary.get('overall_attendance_rate', 0)

        if response_rate >= 80:
            response += "• 📱 Excellent response rate! Team is very engaged.\n"
        elif response_rate >= 60:
            response += "• 👍 Good response rate. Most players respond promptly.\n"
        else:
            response += "• ⏰ Low response rate. Consider sending more reminders.\n"

        if attendance_rate >= 70:
            response += "• 🌟 High attendance rate! Team commitment is strong.\n"
        elif attendance_rate >= 50:
            response += "• 📈 Moderate attendance. Room for improvement.\n"
        else:
            response += "• 📉 Low attendance rate. May need to address availability issues.\n"

        response += f"""
📋 **Management Actions:**
• Use `/attendance MATCH_ID` to check specific match attendance
• Use `/remind` to send attendance reminders
• Use `/attendancealerts` to configure automatic reminders
• Use `/attendanceexport` to export attendance data

💡 **Tips for Improvement:**
• Send match notifications early
• Follow up with non-respondents
• Consider flexible match scheduling
• Recognize consistent attendees
        """

        return response.strip()

    except Exception as e:
        logger.error(f"Failed to get team attendance summary: {e}")
        return format_tool_error(f"Failed to get team attendance summary: {e!s}")