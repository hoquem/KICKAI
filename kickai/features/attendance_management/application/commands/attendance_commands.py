#!/usr/bin/env python3
"""
Attendance Management Commands

This module registers all attendance management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# ATTENDANCE MANAGEMENT COMMANDS
# ============================================================================

@command(
    name="/markattendance",
    description="Mark attendance for a match",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="attendance_management",
    examples=["/markattendance", "/markattendance yes", "/markattendance no"],
    parameters={
        "status": "Attendance status (yes, no, maybe)"
    },
    help_text="""
✅ Mark Attendance

Mark your attendance for an upcoming match.

Usage:
• /markattendance - Start attendance marking process
• /markattendance yes - Confirm attendance
• /markattendance no - Decline attendance
• /markattendance maybe - Mark as tentative

What happens:
1. Your attendance is recorded
2. Team leadership is notified
3. Squad selection is updated
4. You receive confirmation

💡 Tip: Mark attendance early to help with squad planning.
    """
)
async def handle_markattendance_command(update, context, **kwargs):
    """Handle /markattendance command."""
    # This will be handled by the agent system
    return None


@command(
    name="/attendance",
    description="View attendance for matches",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="attendance_management",
    examples=["/attendance", "/attendance MATCH123"],
    parameters={
        "match_id": "Optional match ID for specific match"
    },
    help_text="""
📊 View Attendance

View attendance information for matches.

Usage:
• /attendance - Show attendance for next match
• /attendance MATCH123 - Show attendance for specific match

What you'll see:
• Match details
• Number of confirmed attendees
• Number of declines
• Number of tentative responses
• List of players and their status

💡 Tip: Use this to check team availability for matches.
    """
)
async def handle_attendance_command(update, context, **kwargs):
    """Handle /attendance command."""
    # This will be handled by the agent system
    return None


@command(
    name="/attendancehistory",
    description="View your attendance history",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="attendance_management",
    examples=["/attendancehistory", "/attendancehistory 2024"],
    parameters={
        "year": "Optional year to filter (e.g., 2024)"
    },
    help_text="""
📈 Attendance History

View your personal attendance history and statistics.

Usage:
• /attendancehistory - Show all your attendance history
• /attendancehistory 2024 - Show history for specific year

What you'll see:
• List of matches you attended
• List of matches you missed
• Attendance percentage
• Performance trends
• Season statistics

💡 Tip: Track your attendance to improve team reliability.
    """
)
async def handle_attendancehistory_command(update, context, **kwargs):
    """Handle /attendancehistory command."""
    # This will be handled by the agent system
    return None


@command(
    name="/attendanceexport",
    description="Export attendance data (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="attendance_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/attendanceexport", "/attendanceexport MATCH123"],
    parameters={
        "match_id": "Optional match ID for specific match"
    },
    help_text="""
📋 Export Attendance (Leadership Only)

Export attendance data for analysis and reporting.

Usage:
• /attendanceexport - Export all attendance data
• /attendanceexport MATCH123 - Export data for specific match

What you'll get:
• CSV file with attendance data
• Player names and attendance status
• Match details and dates
• Summary statistics

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_attendanceexport_command(update, context, **kwargs):
    """Handle /attendanceexport command."""
    # This will be handled by the agent system
    return None


@command(
    name="/attendancealerts",
    description="Manage attendance alerts (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="attendance_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/attendancealerts", "/attendancealerts enable", "/attendancealerts disable"],
    parameters={
        "action": "Action to perform (enable, disable, configure)"
    },
    help_text="""
🔔 Attendance Alerts (Leadership Only)

Manage automatic attendance reminders and alerts.

Usage:
• /attendancealerts - Show current alert settings
• /attendancealerts enable - Enable automatic reminders
• /attendancealerts disable - Disable automatic reminders

Alert types:
• Match reminders (24h before)
• Attendance deadline reminders
• Low attendance warnings
• Squad selection notifications

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_attendancealerts_command(update, context, **kwargs):
    """Handle /attendancealerts command."""
    # This will be handled by the agent system
    return None
