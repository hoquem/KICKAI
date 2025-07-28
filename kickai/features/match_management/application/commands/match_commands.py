#!/usr/bin/env python3
"""
Match Management Commands

This module registers all match management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

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
    # This will be handled by the agent system
    return None


@command(
    name="/listmatches",
    description="List all matches for the team",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="match_management",
    chat_type=ChatType.MAIN,
    examples=["/listmatches", "/listmatches scheduled", "/listmatches completed"],
    parameters={
        "status": "Match status filter (all, scheduled, completed, cancelled)",
    },
    help_text="""
📋 List Matches

View all matches for the team with optional status filtering.

Usage:
• /listmatches - List all matches
• /listmatches [status] - List matches with specific status

Status Options:
• all - All matches (default)
• scheduled - Upcoming matches
• completed - Finished matches
• cancelled - Cancelled matches

Examples:
/listmatches
/listmatches scheduled
/listmatches completed

What you'll see:
• Match details (opponent, date, time, venue)
• Match status and competition type
• Match ID for reference

💡 Use /matchdetails [match_id] to get detailed information about a specific match.
    """,
)
async def handle_listmatches_command(update, context, **kwargs):
    """Handle /listmatches command."""
    # This will be handled by the agent system
    return None


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
    # This will be handled by the agent system
    return None


@command(
    name="/updatematch",
    description="Update match information (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/updatematch", "/updatematch MATCH123"],
    parameters={
        "match_id": "Match ID to update",
        "updates": "Fields to update (opponent, date, time, venue, status, score)",
    },
    help_text="""
🔄 Update Match (Leadership Only)

Update match information and details.

Usage:
• /updatematch - Start match update process
• /updatematch [match_id] - Update specific match
• /updatematch [match_id] [updates] - Update match with specific changes

Updateable Fields:
• opponent - Opponent team name
• date - Match date (YYYY-MM-DD)
• time - Match time (HH:MM)
• venue - Match venue (Home/Away)
• status - Match status (scheduled, completed, cancelled)
• score - Match score (e.g., "2-1")

Examples:
/updatematch
/updatematch MATCH123
/updatematch MATCH123 score:2-1 status:completed

What happens:
1. Match details are updated
2. Changes are logged and tracked
3. Players are notified of updates
4. Match status is updated in system

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_updatematch_command(update, context, **kwargs):
    """Handle /updatematch command."""
    # This will be handled by the agent system
    return None


@command(
    name="/deletematch",
    description="Delete a match (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/deletematch", "/deletematch MATCH123"],
    parameters={
        "match_id": "Match ID to delete",
    },
    help_text="""
🗑️ Delete Match (Leadership Only)

Delete a match from the system.

Usage:
• /deletematch - Start match deletion process
• /deletematch [match_id] - Delete specific match

Examples:
/deletematch
/deletematch MATCH123

What happens:
1. Match is permanently deleted
2. All associated data is removed
3. Players are notified of cancellation
4. System is updated accordingly

⚠️ Warning: This action cannot be undone!

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_deletematch_command(update, context, **kwargs):
    """Handle /deletematch command."""
    # This will be handled by the agent system
    return None


@command(
    name="/availableplayers",
    description="Get list of available players for a match",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="match_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/availableplayers", "/availableplayers MATCH123"],
    parameters={
        "match_id": "Match ID to check availability for",
    },
    help_text="""
👥 Available Players (Leadership Only)

Get list of available players for a specific match.

Usage:
• /availableplayers - Check availability for most recent match
• /availableplayers [match_id] - Check availability for specific match

Examples:
/availableplayers
/availableplayers MATCH123

What you'll see:
• List of all available players
• Player details (name, position, status)
• Total count of available players
• Next steps for squad selection

💡 Use this before selecting a squad to see who's available.
    """,
)
async def handle_availableplayers_command(update, context, **kwargs):
    """Handle /availableplayers command."""
    # This will be handled by the agent system
    return None
