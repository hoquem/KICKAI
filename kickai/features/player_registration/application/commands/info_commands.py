#!/usr/bin/env python3
"""
Information Query Commands

This module registers all information query related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""


from kickai.core.command_registry import CommandType, PermissionLevel, command


@command(
    name="/myinfo",
    description="Get your player information and status",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/myinfo"],
    help_text="""
👤 My Information

Get your personal player information and current status.

Usage:
/myinfo

What you'll see:
• Your player details (name, phone, position)
• Current registration status
• Team membership information
• Recent activity summary
• Contact information

💡 Need to update your info? Contact the team admin.
    """,
)
async def handle_myinfo_command(update, context, **kwargs):
    """Handle /myinfo command."""
    # This will be handled by the agent system
    return None


@command(
    name="/list",
    description="List all team players and their status",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/list"],
    help_text="""
📋 Team Players List

View all registered team players and their current status.

Usage:
/list

What you'll see:
• List of all team players
• Player names and positions
• Current status (active, pending, inactive)
• Contact information (if you have permission)
• Quick player count summary

💡 Note: In leadership chat, you'll see all players. In main chat, only active players are shown.
    """,
)
async def handle_list_command(update, context, **kwargs):
    """Handle /list command."""
    # This will be handled by the agent system
    return None


@command(
    name="/status",
    description="Check player status by phone number",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/status +447123456789"],
    parameters={"phone": "Phone number to check status for"},
    help_text="""
📊 Player Status Check

Check the status of a specific player by their phone number.

Usage:
/status [phone]

Example:
/status +447123456789

What you'll see:
• Player name and position
• Current registration status
• Team membership details
• Last activity information
• Contact details (if you have permission)

💡 Tip: You can also check your own status with /myinfo
    """,
)
async def handle_status_command(update, context, **kwargs):
    """Handle /status command."""
    # This will be handled by the agent system
    return None


@command(
    name="/stats",
    description="View team statistics and performance data",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/stats"],
    help_text="""
📈 Team Statistics

View comprehensive team statistics and performance data.

Usage:
/stats

What you'll see:
• Total team members count
• Active vs inactive players
• Position distribution
• Recent registration trends
• Team activity summary
• Performance metrics

💡 Leadership: You'll see additional admin statistics.
    """,
)
async def handle_stats_command(update, context, **kwargs):
    """Handle /stats command."""
    # This will be handled by the agent system
    return None


@command(
    name="/performance",
    description="View detailed performance analytics",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="player_registration",
    examples=["/performance"],
    help_text="""
📊 Performance Analytics

View detailed performance analytics and trends.

Usage:
/performance

What you'll see:
• Individual player performance metrics
• Team performance trends
• Attendance statistics
• Match participation data
• Performance comparisons
• Improvement suggestions

💡 Leadership: You'll see comprehensive team analytics.
    """,
)
async def handle_performance_command(update, context, **kwargs):
    """Handle /performance command."""
    # This will be handled by the agent system
    return None
