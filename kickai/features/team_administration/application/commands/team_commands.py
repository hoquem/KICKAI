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
    name="/addmember",
    description="Add a team member (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=["/addmember", "/addmember Sarah Johnson +447987654321 Assistant Coach"],
    parameters={
        "name": "Team member's full name",
        "phone": "Team member's phone number",
        "role": "Team member's role (Coach, Assistant Coach, Manager, etc.)",
    },
    help_text="""
👔 Add Team Member (Leadership Only)

Add a new team member (coach, manager, etc.) to the team.

Usage:
/addmember [name] [phone] [role]

Example:
/addmember Sarah Johnson +447987654321 Assistant Coach

Valid Roles:
• Coach
• Assistant Coach
• Manager
• Assistant Manager
• Admin
• Coordinator
• Volunteer

What happens:
1. Team member is added to the system
2. Unique invite link is generated
3. Member can join leadership chat
4. Member gets access to admin commands

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_addmember_command(update, context, **kwargs):
    """Handle /addmember command."""
    # This will be handled by the agent system
    return None


# Commands removed: /createteam, /teamstatus, /updateteam, /listmembers
# /list command will handle listing all players and members in leadership chat
# /update command will handle updating team member information
