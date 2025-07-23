#!/usr/bin/env python3
"""
Match Management Commands

This module registers all match management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from src.core.command_registry import CommandType, PermissionLevel, command
from src.core.enums import ChatType

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
        "time": "Match time (HH:MM)"
    },
    help_text="""
⚽ Create Match (Leadership Only)

Create a new match in the system.

Usage:
• /creatematch - Start match creation process
• /creatematch [opponent] [date] [time] - Create match with details

Example:
/creatematch vs Team B 2024-01-15 14:00

What happens:
1. New match record is created
2. Match is announced to all players
3. Attendance tracking is enabled
4. Squad selection becomes available

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_creatematch_command(update, context, **kwargs):
    """Handle /creatematch command."""
    # This will be handled by the agent system
    return None


@command(
    name="/listmatches",
    description="List all matches",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="match_management",
    examples=["/listmatches", "/listmatches upcoming"],
    parameters={
        "filter": "Optional filter (upcoming, past, all)"
    },
    help_text="""
📅 List Matches

View all matches in the system.

Usage:
• /listmatches - Show all matches
• /listmatches upcoming - Show upcoming matches only
• /listmatches past - Show past matches only

What you'll see:
• Match details (opponent, date, time)
• Match status (scheduled, in progress, completed)
• Attendance information
• Squad selection status

💡 Tip: Use filters to focus on relevant matches.
    """
)
async def handle_listmatches_command(update, context, **kwargs):
    """Handle /listmatches command."""
    # This will be handled by the agent system
    return None


@command(
    name="/matchdetails",
    description="Show detailed match information",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="match_management",
    examples=["/matchdetails", "/matchdetails MATCH123"],
    parameters={
        "match_id": "Optional match ID for specific match"
    },
    help_text="""
📋 Match Details

Get detailed information about a specific match.

Usage:
• /matchdetails - Show details for next match
• /matchdetails [match_id] - Show details for specific match

What you'll see:
• Match date, time, and location
• Opponent information
• Squad selection
• Attendance list
• Match status and updates

💡 Tip: Use this to get comprehensive match information.
    """
)
async def handle_matchdetails_command(update, context, **kwargs):
    """Handle /matchdetails command."""
    # This will be handled by the agent system
    return None


@command(
    name="/selectsquad",
    description="Select squad for a match (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/selectsquad", "/selectsquad MATCH123"],
    parameters={
        "match_id": "Optional match ID for specific match"
    },
    help_text="""
👥 Select Squad (Leadership Only)

Select the squad for an upcoming match.

Usage:
• /selectsquad - Select squad for next match
• /selectsquad [match_id] - Select squad for specific match

What happens:
1. Available players are listed
2. You can select players for the squad
3. Squad is finalized and announced
4. Selected players are notified

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_selectsquad_command(update, context, **kwargs):
    """Handle /selectsquad command."""
    # This will be handled by the agent system
    return None


@command(
    name="/updatematch",
    description="Update match details (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/updatematch MATCH123 date 2024-01-16", "/updatematch MATCH123 time 15:00"],
    parameters={
        "match_id": "Match ID to update",
        "field": "Field to update (date, time, location, etc.)",
        "value": "New value for the field"
    },
    help_text="""
✏️ Update Match (Leadership Only)

Update match details and information.

Usage:
/updatematch [match_id] [field] [value]

Examples:
• /updatematch MATCH123 date 2024-01-16
• /updatematch MATCH123 time 15:00
• /updatematch MATCH123 location New Stadium

Available fields:
• date - Match date
• time - Match time
• location - Match location
• status - Match status

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_updatematch_command(update, context, **kwargs):
    """Handle /updatematch command."""
    # This will be handled by the agent system
    return None
