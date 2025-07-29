#!/usr/bin/env python3
"""
Communication Commands

This module registers all communication related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# Note: /broadcast command has been removed as it's not needed for now
# Team announcements can be made using /announce command instead


@command(
    name="/announce",
    description="Make an announcement to the team (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="communication",
    examples=["/announce Important match this weekend!"],
    parameters={"message": "Announcement message to send to the team"},
    help_text="""
📢 Team Announcement (Leadership Only)

Make an important announcement to all team members.

Usage:
/announce [message]

Example:
/announce Important match this weekend!

What happens:
1. Announcement is sent to the main team chat
2. All team members are notified
3. Message is formatted for clarity
4. Announcement is logged for record keeping

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_announce_command(update, context, **kwargs):
    """Handle /announce command."""
    # This will be handled by the agent system
    return None


@command(
    name="/remind",
    description="Send a reminder to team members (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="communication",
    examples=["/remind Don't forget training tomorrow at 7pm"],
    parameters={"message": "Reminder message to send"},
    help_text="""
⏰ Send Reminder (Leadership Only)

Send a reminder message to team members.

Usage:
/remind [message]

Example:
/remind Don't forget training tomorrow at 7pm

What happens:
1. Reminder is sent to the main team chat
2. Team members receive notification
3. Message is clearly marked as a reminder
4. Reminder is logged for tracking

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_remind_command(update, context, **kwargs):
    """Handle /remind command."""
    # This will be handled by the agent system
    return None
