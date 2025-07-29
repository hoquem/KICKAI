#!/usr/bin/env python3
"""
Team Administration Commands

This module registers all team administration related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# Note: /createteam command has been removed as it's not needed for now
# Teams are created through the setup process and configuration


@command(
    name="/teamstatus",
    description="Show team status and configuration (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=["/teamstatus"],
    help_text="""
📊 Team Status (Leadership Only)

Show current team status, configuration, and statistics.

Usage:
/teamstatus

What you'll see:
• Team name and ID
• Number of registered players
• Number of team members
• Team configuration settings
• Recent activity summary

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_teamstatus_command(update, context, **kwargs):
    """Handle /teamstatus command."""
    # This will be handled by the agent system
    return None


@command(
    name="/updateteam",
    description="Update team configuration (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=["/updateteam name New Team Name", "/updateteam description Updated description"],
    parameters={
        "setting": "Setting to update (name, description, etc.)",
        "value": "New value for the setting",
    },
    help_text="""
⚙️ Update Team (Leadership Only)

Update team configuration settings.

Usage:
/updateteam [setting] [value]

Examples:
• /updateteam name New Team Name
• /updateteam description Updated team description

Available settings:
• name - Team name
• description - Team description
• location - Team location
• contact - Contact information

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_updateteam_command(update, context, **kwargs):
    """Handle /updateteam command."""
    # This will be handled by the agent system
    return None


