#!/usr/bin/env python3
"""
Attendance Management Commands

This module handles non-match specific attendance tracking like training sessions,
events, and general RSVP functionality. Match-specific attendance is handled
by the match_management feature.
"""


from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# NON-MATCH ATTENDANCE COMMANDS
# ============================================================================


@command(
    name="/rsvp",
    description="RSVP for team events and training sessions",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    chat_type=ChatType.MAIN,
    feature="attendance_management",
    examples=["/rsvp", "/rsvp yes", "/rsvp no"],
    parameters={"status": "RSVP status (yes, no, maybe)"},
    help_text="""
✅ RSVP for Events

RSVP for team events, training sessions, and social activities.

Usage:
• /rsvp - Start RSVP process for upcoming events
• /rsvp yes - Confirm attendance
• /rsvp no - Decline attendance
• /rsvp maybe - Mark as tentative

What happens:
1. Your RSVP is recorded for the event
2. Event organizers are notified
3. You receive confirmation

💡 Note: For match attendance, use /markattendance in match management.
    """,
)
async def handle_rsvp_command(update, context, **kwargs):
    """Handle /rsvp command."""
    # This will be handled by the agent system
    return None


@command(
    name="/events",
    description="View upcoming team events and training",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    chat_type=ChatType.MAIN,
    feature="attendance_management",
    examples=["/events", "/events training"],
    parameters={"type": "Optional event type filter (training, social, etc.)"},
    help_text="""
📅 View Team Events

View upcoming team events, training sessions, and activities.

Usage:
• /events - Show all upcoming events
• /events training - Show only training sessions
• /events social - Show only social events

What you'll see:
• Event details and dates
• Location information
• RSVP status and counts
• Your current RSVP status

💡 Note: For matches, use /listmatches in match management.
    """,
)
async def handle_events_command(update, context, **kwargs):
    """Handle /events command."""
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
    parameters={"match_id": "Optional match ID for specific match"},
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
    """,
)
async def handle_attendanceexport_command(update, context, **kwargs):
    """Handle /attendanceexport command."""
    # This will be handled by the agent system
    return None
