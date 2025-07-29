#!/usr/bin/env python3
"""
Attendance Management Commands

This module registers all attendance management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# ATTENDANCE COMMANDS
# ============================================================================


@command(
    name="/attendance",
    description="View match attendance information",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="attendance_management",
    examples=["/attendance", "/attendance MATCH123"],
    parameters={"match_id": "Match ID to view attendance for"},
    help_text="""
📊 Attendance Information

View attendance information for matches.

Usage:
• /attendance - Show your attendance history
• /attendance [match_id] - Show attendance for specific match

Example:
/attendance MATCH123

What you'll see:
• Match details and date
• Attendance status (confirmed, declined, tentative)
• Response timestamp
• Any notes or comments

💡 Tip: Use this to check your attendance status for upcoming matches.
    """,
)
async def handle_attendance_command(update, context, **kwargs):
    """Handle /attendance command."""
    # This will be handled by the agent system
    return None


@command(
    name="/markattendance",
    description="Mark your attendance for a match",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="attendance_management",
    examples=["/markattendance MATCH123 confirmed", "/markattendance MATCH123 declined"],
    parameters={
        "match_id": "Match ID to mark attendance for",
        "status": "Attendance status (confirmed, declined, tentative)",
    },
    help_text="""
✅ Mark Attendance

Mark your attendance status for a specific match.

Usage:
/markattendance [match_id] [status]

Examples:
• /markattendance MATCH123 confirmed
• /markattendance MATCH123 declined
• /markattendance MATCH123 tentative

Status Options:
• confirmed - You will attend the match
• declined - You cannot attend the match
• tentative - You might attend (will confirm later)

What happens:
1. Your attendance is recorded for the match
2. Team leadership is notified of your response
3. You can update your status later if needed
4. Your response is tracked for team planning

💡 Tip: Respond early to help with team planning!
    """,
)
async def handle_markattendance_command(update, context, **kwargs):
    """Handle /markattendance command."""
    # This will be handled by the agent system
    return None


@command(
    name="/attendancehistory",
    description="View your attendance history",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="attendance_management",
    examples=["/attendancehistory", "/attendancehistory 2024"],
    parameters={"year": "Year to view history for (optional)"},
    help_text="""
📈 Attendance History

View your attendance history and statistics.

Usage:
• /attendancehistory - Show your recent attendance
• /attendancehistory [year] - Show attendance for specific year

Example:
/attendancehistory 2024

What you'll see:
• List of matches you've responded to
• Your attendance rate and statistics
• Response patterns and trends
• Summary of your participation

💡 Tip: Use this to track your team participation over time.
    """,
)
async def handle_attendancehistory_command(update, context, **kwargs):
    """Handle /attendancehistory command."""
    # This will be handled by the agent system
    return None


# Note: /attendanceexport command has been removed as it's not needed for now
# Export functionality can be added later if required
