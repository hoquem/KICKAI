#!/usr/bin/env python3
"""
Match Management Commands

This module registers all match management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

import logging
from datetime import datetime, time

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.dependency_container import get_container
from kickai.core.enums import ChatType
from kickai.features.match_management.domain.entities.attendance import AttendanceStatus
from kickai.features.match_management.domain.entities.availability import AvailabilityStatus
from kickai.features.match_management.domain.services.attendance_service import AttendanceService
from kickai.features.match_management.domain.services.availability_service import (
    AvailabilityService,
)
from kickai.features.match_management.domain.services.match_service import MatchService

logger = logging.getLogger(__name__)

# ============================================================================
# MATCH MANAGEMENT COMMANDS
# ============================================================================


@command(
    name="/creatematch",
    description="Create a new match (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/creatematch", "/creatematch vs Team B 2024-01-15 14:00"],
    parameters={
        "opponent": "Opponent team name",
        "date": "Match date (YYYY-MM-DD)",
        "time": "Match time (HH:MM)",
        "venue": "Match venue (Home/Away)",
        "competition": "Competition type (Friendly, League, Cup)",
    },
    help_text="""
⚽ Create Match (Leadership Only)

Create a new match in the system.

Usage:
• /creatematch - Start match creation process
• /creatematch [opponent] [date] [time] - Create match with details
• /creatematch [opponent] [date] [time] [venue] [competition] - Create match with all details

Examples:
/creatematch vs Arsenal 2024-01-15 14:00
/creatematch vs Chelsea 2024-01-20 15:30 Away League
/creatematch vs Spurs 2024-01-25 19:00 Home Cup

What happens:
1. New match record is created
2. Match is announced to all players
3. Availability tracking is enabled
4. Squad selection becomes available

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_creatematch_command(update, context, **kwargs):
    """Handle /creatematch command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if len(args) < 3:
            return "❌ **Insufficient arguments**. Usage: `/creatematch [opponent] [date] [time] [venue] [competition]`"

        opponent = args[0]
        date_str = args[1]
        time_str = args[2]
        venue = args[3] if len(args) > 3 else "Home"
        competition = args[4] if len(args) > 4 else "League Match"

        # Parse date and time
        try:
            match_date = datetime.strptime(date_str, "%Y-%m-%d")
            match_time = time.fromisoformat(time_str)
        except ValueError as e:
            return f"❌ **Invalid date/time format**: {e}. Use YYYY-MM-DD for date and HH:MM for time."

        # Get services
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ **Service unavailable**: Match service not available."

        # Create match
        team_id = "KTI"  # Default team ID - should come from context
        created_by = str(update.effective_user.id) if update.effective_user else ""

        match = await match_service.create_match(
            team_id=team_id,
            opponent=opponent,
            match_date=match_date,
            match_time=match_time,
            venue=venue,
            competition=competition,
            created_by=created_by,
        )

        return f"""✅ **Match Created Successfully**

🏆 **Match Details**
• **Opponent**: {match.opponent}
• **Date**: {match.formatted_date}
• **Time**: {match.formatted_time}
• **Venue**: {match.venue}
• **Competition**: {match.competition}
• **Match ID**: {match.match_id}

📋 **Next Steps**:
• Players will be notified automatically
• Availability requests will be sent 7 days before
• Squad selection will open 3 days before match"""

    except Exception as e:
        logger.error(f"Error in /creatematch command: {e}")
        return f"❌ **Error creating match**: {e!s}"


@command(
    name="/listmatches",
    description="List all matches for the team",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="match_management",
    chat_type=ChatType.MAIN,
    examples=["/listmatches", "/listmatches scheduled", "/listmatches completed"],
    parameters={
        "status": "Match status filter (all, upcoming, past)",
    },
    help_text="""
📋 List Matches

View all matches for the team with optional status filtering.

Usage:
• /listmatches - List all matches
• /listmatches [status] - List matches with specific status

Status Options:
• all - All matches (default)
• upcoming - Upcoming matches
• past - Past matches

Examples:
/listmatches
/listmatches upcoming
/listmatches past

What you'll see:
• Match details (opponent, date, time, venue)
• Match status and competition type
• Match ID for reference

💡 Use /matchdetails [match_id] to get detailed information about a specific match.
    """,
)
async def handle_listmatches_command(update, context, **kwargs):
    """Handle /listmatches command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        status = args[0] if args else "all"
        limit = 10

        # Get services
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ **Service unavailable**: Match service not available."

        # Get matches
        team_id = "KTI"  # Default team ID - should come from context

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
            return f"{title}\n\nNo matches found."

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

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error in /listmatches command: {e}")
        return f"❌ **Error listing matches**: {e!s}"


@command(
    name="/matchdetails",
    description="Get detailed information about a specific match",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="match_management",
    chat_type=ChatType.MAIN,
    examples=["/matchdetails", "/matchdetails MATCH123"],
    parameters={
        "match_id": "Match ID to get details for",
    },
    help_text="""
⚽ Match Details

Get detailed information about a specific match.

Usage:
• /matchdetails - Get details for the most recent match
• /matchdetails [match_id] - Get details for specific match

Examples:
/matchdetails
/matchdetails MATCH123

What you'll see:
• Complete match information
• Date, time, venue, and competition
• Match status and score (if available)
• Squad information (if selected)

💡 Use /listmatches to see all available matches and their IDs.
    """,
)
async def handle_matchdetails_command(update, context, **kwargs):
    """Handle /matchdetails command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if not args:
            return "❌ **Missing match ID**. Usage: `/matchdetails [match_id]`"

        match_id = args[0]

        # Get services
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return "❌ **Service unavailable**: Match service not available."

        # Get match details
        match = await match_service.get_match(match_id)
        if not match:
            return f"❌ **Match not found**: {match_id}"

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

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error in /matchdetails command: {e}")
        return f"❌ **Error getting match details**: {e!s}"


@command(
    name="/markattendance",
    description="Mark your availability for a match",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="match_management",
    chat_type=ChatType.MAIN,
    examples=["/markattendance MATCH123 available", "/markattendance MATCH123 unavailable Work"],
    parameters={
        "match_id": "Match ID to mark availability for",
        "status": "Availability status (available, unavailable, maybe)",
        "reason": "Optional reason for status",
    },
    help_text="""
✅ Mark Availability

Mark your availability for an upcoming match.

Usage:
• /markattendance [match_id] [status] - Mark availability
• /markattendance [match_id] [status] [reason] - Mark availability with reason

Status Options:
• available - You can play
• unavailable - You cannot play
• maybe - You're not sure yet

Examples:
/markattendance MATCH123 available
/markattendance MATCH123 unavailable "Work commitment"
/markattendance MATCH123 maybe "Will confirm by Thursday"

What happens:
1. Your availability is recorded
2. Team managers can see your status
3. You can update your status anytime before squad selection

💡 Use /attendance [match_id] to see current availability for the match.
    """,
)
async def handle_markattendance_command(update, context, **kwargs):
    """Handle /markattendance command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if len(args) < 2:
            return "❌ **Insufficient arguments**. Usage: `/markattendance [match_id] [status] [reason]`"

        match_id = args[0]
        status = args[1]
        reason = " ".join(args[2:]) if len(args) > 2 else None

        # Get services
        container = get_container()
        availability_service = container.get_service(AvailabilityService)

        if not availability_service:
            return "❌ **Service unavailable**: Availability service not available."

        # Mark availability
        player_id = str(update.effective_user.id) if update.effective_user else "unknown"

        try:
            availability_status = AvailabilityStatus(status.lower())
        except ValueError:
            return f"❌ **Invalid status**: {status}. Valid options: available, unavailable, maybe"

        availability = await availability_service.mark_availability(
            match_id=match_id,
            player_id=player_id,
            status=availability_status,
            reason=reason,
        )

        # Get availability summary
        summary = await availability_service.get_availability_summary(match_id)

        result = [
            "✅ **Availability Updated**",
            "",
            f"**Match**: {match_id}",
            f"**Your Status**: {availability.status_emoji} {availability_status.value.title()}",
        ]

        if reason:
            result.append(f"**Reason**: {reason}")

        result.extend([
            "",
            "📊 **Team Availability**",
            f"• Available: {summary['available']} players",
            f"• Unavailable: {summary['unavailable']} players",
            f"• Maybe: {summary['maybe']} players",
            f"• Pending: {summary['pending']} players",
            "",
            "💡 **Tip**: You can update your availability anytime before squad selection",
        ])

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error in /markattendance command: {e}")
        return f"❌ **Error marking availability**: {e!s}"


@command(
    name="/attendance",
    description="View match attendance information",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="match_management",
    chat_type=ChatType.MAIN,
    examples=["/attendance MATCH123"],
    parameters={
        "match_id": "Match ID to view attendance for",
    },
    help_text="""
📊 View Attendance

View current availability and attendance information for a match.

Usage:
• /attendance [match_id] - View attendance for specific match

Examples:
/attendance MATCH123

What you'll see:
• Current availability status for all players
• Number of available, unavailable, and pending players
• Individual player statuses and reasons

💡 Use /markattendance [match_id] [status] to mark your own availability.
    """,
)
async def handle_attendance_command(update, context, **kwargs):
    """Handle /attendance command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if not args:
            return "❌ **Missing match ID**. Usage: `/attendance [match_id]`"

        match_id = args[0]

        # Get services
        container = get_container()
        availability_service = container.get_service(AvailabilityService)

        if not availability_service:
            return "❌ **Service unavailable**: Availability service not available."

        # Get availability information
        summary = await availability_service.get_availability_summary(match_id)
        available_players = await availability_service.get_available_players(match_id)
        unavailable_players = await availability_service.get_unavailable_players(match_id)
        maybe_players = await availability_service.get_maybe_players(match_id)
        pending_players = await availability_service.get_pending_players(match_id)

        result = [
            f"📊 **Match Attendance: {match_id}**",
            "",
            f"**Total Players**: {summary['total_players']}",
            "",
        ]

        # Available players
        if available_players:
            result.append(f"✅ **Available** ({len(available_players)}):")
            for availability in available_players:
                result.append(f"• {availability.player_id}")
            result.append("")

        # Unavailable players
        if unavailable_players:
            result.append(f"❌ **Unavailable** ({len(unavailable_players)}):")
            for availability in unavailable_players:
                result.append(f"• {availability.player_id}")
                if availability.reason:
                    result.append(f"  - Reason: {availability.reason}")
            result.append("")

        # Maybe players
        if maybe_players:
            result.append(f"❓ **Maybe** ({len(maybe_players)}):")
            for availability in maybe_players:
                result.append(f"• {availability.player_id}")
                if availability.reason:
                    result.append(f"  - Reason: {availability.reason}")
            result.append("")

        # Pending players
        if pending_players:
            result.append(f"⏳ **Pending** ({len(pending_players)}):")
            for availability in pending_players:
                result.append(f"• {availability.player_id}")
            result.append("")

        result.append("📋 **Actions**")
        result.append("• /markattendance [match_id] [status] - Mark your availability")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error in /attendance command: {e}")
        return f"❌ **Error getting attendance**: {e!s}"


@command(
    name="/attendancehistory",
    description="View your attendance history",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="match_management",
    chat_type=ChatType.MAIN,
    examples=["/attendancehistory", "/attendancehistory 5"],
    parameters={
        "limit": "Number of matches to show (default: 10)",
    },
    help_text="""
📈 Attendance History

View your personal attendance history and statistics.

Usage:
• /attendancehistory - View last 10 matches
• /attendancehistory [limit] - View specific number of matches

Examples:
/attendancehistory
/attendancehistory 5

What you'll see:
• Your availability for recent matches
• Attendance statistics and reliability rating
• Performance trends over time

💡 This helps you track your commitment to the team.
    """,
)
async def handle_attendancehistory_command(update, context, **kwargs):
    """Handle /attendancehistory command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        limit = int(args[0]) if args and args[0].isdigit() else 10

        # Get services
        container = get_container()
        availability_service = container.get_service(AvailabilityService)

        if not availability_service:
            return "❌ **Service unavailable**: Availability service not available."

        # Get player history
        player_id = str(update.effective_user.id) if update.effective_user else "unknown"
        history = await availability_service.get_player_history(player_id, limit)

        if not history:
            return "📈 **Attendance History**\n\nNo availability records found for you."

        result = [
            "📈 **Your Attendance History**",
            "",
            f"**Last {len(history)} matches**:",
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
            "📊 **Statistics**",
            f"• **Availability Rate**: {availability_rate:.1f}% ({available_count}/{total_matches} matches)",
            f"• **Available**: {available_count} matches",
            f"• **Unavailable**: {unavailable_count} matches",
            f"• **Maybe**: {maybe_count} matches",
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

        result.append(f"• **Reliability Rating**: {reliability}")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error in /attendancehistory command: {e}")
        return f"❌ **Error getting attendance history**: {e!s}"


@command(
    name="/selectsquad",
    description="Select squad for a match (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/selectsquad", "/selectsquad MATCH123"],
    parameters={
        "match_id": "Match ID to select squad for",
        "player_ids": "List of player IDs to include in squad",
    },
    help_text="""
🏆 Select Squad (Leadership Only)

Select the squad for a specific match.

Usage:
• /selectsquad - Start squad selection process
• /selectsquad [match_id] - Select squad for specific match
• /selectsquad [match_id] [player_ids] - Select squad with specific players

Examples:
/selectsquad
/selectsquad MATCH123
/selectsquad MATCH123 JS, MW, SJ, AB

What happens:
1. Available players are listed
2. Squad is selected based on availability and tactics
3. Selected squad is announced
4. Players are notified of selection

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_selectsquad_command(update, context, **kwargs):
    """Handle /selectsquad command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if not args:
            return "❌ **Missing match ID**. Usage: `/selectsquad [match_id] [player_ids]`"

        match_id = args[0]
        player_ids = args[1:] if len(args) > 1 else []

        # Get services
        container = get_container()
        match_service = container.get_service(MatchService)
        availability_service = container.get_service(AvailabilityService)

        if not match_service or not availability_service:
            return "❌ **Service unavailable**: Required services not available."

        # Get match details
        match = await match_service.get_match(match_id)
        if not match:
            return f"❌ **Match not found**: {match_id}"

        if not match.is_upcoming:
            return "❌ **Cannot select squad**: Match is not in upcoming status"

        # TODO: Implement squad selection logic
        # This would integrate with the availability service to get available players
        # and then create a squad selection record

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

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error in /selectsquad command: {e}")
        return f"❌ **Error selecting squad**: {e!s}"


@command(
    name="/markmatchattendance",
    description="Mark actual match day attendance (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/markmatchattendance MATCH123 PLAYER001 attended"],
    parameters={
        "match_id": "Match ID to record attendance for",
        "player_id": "Player ID to record attendance for",
        "status": "Attendance status (attended, absent, late)",
        "reason": "Optional reason for status",
    },
    help_text="""
📊 Mark Match Attendance (Leadership Only)

Record actual attendance for a player at a match.

Usage:
• /markmatchattendance [match_id] [player_id] [status] - Record attendance
• /markmatchattendance [match_id] [player_id] [status] [reason] - Record attendance with reason

Status Options:
• attended - Player attended the match
• absent - Player was absent
• late - Player arrived late

Examples:
/markmatchattendance MATCH123 PLAYER001 attended
/markmatchattendance MATCH123 PLAYER002 absent "No show"
/markmatchattendance MATCH123 PLAYER003 late "Arrived 15 mins late"

What happens:
1. Attendance is recorded for the player
2. Match summary is updated
3. Statistics are calculated

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_markmatchattendance_command(update, context, **kwargs):
    """Handle /markmatchattendance command."""
    try:
        # Parse command arguments
        text = update.message.text if update.message else ""
        args = text.split()[1:] if len(text.split()) > 1 else []

        if len(args) < 3:
            return "❌ **Insufficient arguments**. Usage: `/markmatchattendance [match_id] [player_id] [status] [reason]`"

        match_id = args[0]
        player_id = args[1]
        status = args[2]
        reason = " ".join(args[3:]) if len(args) > 3 else None

        # Get services
        container = get_container()
        attendance_service = container.get_service(AttendanceService)

        if not attendance_service:
            return "❌ **Service unavailable**: Attendance service not available."

        # Record attendance
        recorded_by = str(update.effective_user.id) if update.effective_user else ""

        try:
            attendance_status = AttendanceStatus(status.lower())
        except ValueError:
            return f"❌ **Invalid status**: {status}. Valid options: attended, absent, late"

        attendance = await attendance_service.record_attendance(
            match_id=match_id,
            player_id=player_id,
            status=attendance_status,
            reason=reason,
            recorded_by=recorded_by,
        )

        # Get attendance summary
        summary = await attendance_service.get_attendance_summary(match_id)

        result = [
            "✅ **Match Attendance Recorded**",
            "",
            f"**Match**: {match_id}",
            f"**Player**: {player_id}",
            f"**Status**: {attendance.status_emoji} {attendance_status.value.title()}",
        ]

        if reason:
            result.append(f"**Reason**: {reason}")

        result.extend([
            f"**Recorded by**: {recorded_by or 'System'}",
            f"**Time**: {attendance.recorded_at.strftime('%H:%M')}",
            "",
            "📊 **Match Summary**",
            f"• Attended: {summary['attended']} players",
            f"• Absent: {summary['absent']} players",
            f"• Late: {summary['late']} players",
            f"• Pending: {summary['not_recorded']} players",
        ])

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error in /markmatchattendance command: {e}")
        return f"❌ **Error recording attendance**: {e!s}"
