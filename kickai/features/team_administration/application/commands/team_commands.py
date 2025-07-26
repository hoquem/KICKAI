#!/usr/bin/env python3
"""
Team Administration Commands

This module registers all team administration related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# TEAM MANAGEMENT COMMANDS
# ============================================================================

@command(
    name="/createteam",
    description="Create a new team (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=["/createteam", "/createteam My Team Name"],
    parameters={
        "team_name": "Name of the team to create"
    },
    help_text="""
🏆 Create Team (Leadership Only)

Create a new team in the KICKAI system.

Usage:
• /createteam - Start team creation process
• /createteam [team_name] - Create team with specific name

Example:
/createteam My Team Name

What happens:
1. New team record is created in the database
2. Team configuration is initialized
3. You become the team administrator
4. Team chat channels are set up

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_createteam_command(update, context, **kwargs):
    """Handle /createteam command."""
    # This will be handled by the agent system
    return None


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
    """
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
        "value": "New value for the setting"
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
    """
)
async def handle_updateteam_command(update, context, **kwargs):
    """Handle /updateteam command."""
    # This will be handled by the agent system
    return None


@command(
    name="/listmembers",
    description="List all team members (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=["/listmembers"],
    help_text="""
👥 List Team Members (Leadership Only)

List all team members with their roles and status.

Usage:
/listmembers

What you'll see:
• All team members (players and staff)
• Their roles and permissions
• Registration dates
• Current status (active, inactive, etc.)

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_listmembers_command(update, context, **kwargs):
    """Handle /listmembers command."""
    # This will be handled by the agent system
    return None
