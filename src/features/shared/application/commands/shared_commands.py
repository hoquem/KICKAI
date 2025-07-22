#!/usr/bin/env python3
"""
Shared Commands

This module registers shared/common commands that are available across all features.
These commands provide basic functionality that doesn't belong to a specific feature.
"""

from src.core.command_registry import command, CommandType, PermissionLevel
from src.core.enums import ChatType


# ============================================================================
# SHARED COMMANDS
# ============================================================================

@command(
    name="/start",
    description="Start the bot and show welcome message",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/start"],
    help_text="""
🚀 Start Bot

Start the KICKAI bot and get a welcome message.

Usage:
/start

What happens:
1. Bot welcomes you to the system
2. Shows available commands for your role
3. Provides basic usage instructions
4. Sets up your user session

💡 Tip: Use this command when you first join or need a refresher.
    """
)
async def handle_start_command(update, context, **kwargs):
    """Handle /start command."""
    # This will be handled by the agent system
    return None


@command(
    name="/info",
    description="Show your user information and status",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/info", "/myinfo"],
    help_text="""
👤 User Information

View your personal information and status in the system.

Usage:
• /info - Show your information
• /myinfo - Alternative command (same as /info)

What you'll see:
• Your name and user ID
• Registration date and status
• Team membership details
• Permission level
• Recent activity

💡 Tip: Use this to check your account status and permissions.
    """
)
async def handle_info_command(update, context, **kwargs):
    """Handle /info command."""
    # This will be handled by the agent system
    return None


@command(
    name="/myinfo",
    description="Show your user information and status (alias for /info)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/myinfo"],
    help_text="""
👤 My Information

View your personal information and status in the system.

Usage:
/myinfo

What you'll see:
• Your name and user ID
• Registration date and status
• Team membership details
• Permission level
• Recent activity

💡 Tip: This is an alias for the /info command.
    """
)
async def handle_myinfo_command(update, context, **kwargs):
    """Handle /myinfo command."""
    # This will be handled by the agent system
    return None


@command(
    name="/list",
    description="List team members or players",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/list", "/list players", "/list members"],
    parameters={
        "type": "Optional type to list (players, members, all)"
    },
    help_text="""
📋 List Team

List team members or players based on your current chat.

Usage:
• /list - List based on current chat context
• /list players - List all players
• /list members - List all team members

What you'll see:
• List of team members/players
• Their roles and status
• Registration dates
• Contact information (if permitted)

💡 Tip: The list content depends on your current chat and permissions.
    """
)
async def handle_list_command(update, context, **kwargs):
    """Handle /list command."""
    # This will be handled by the agent system
    return None


@command(
    name="/status",
    description="Check status of a player or yourself",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/status", "/status MH123", "/status +447123456789"],
    parameters={
        "identifier": "Player ID, phone number, or leave empty for yourself"
    },
    help_text="""
📊 Status Check

Check the status of a player or yourself.

Usage:
• /status - Check your own status
• /status MH123 - Check status by player ID
• /status +447123456789 - Check status by phone number

What you'll see:
• Player name and ID
• Registration status
• Team membership
• Recent activity
• Permission level

💡 Tip: Use this to check player availability and status.
    """
)
async def handle_status_command(update, context, **kwargs):
    """Handle /status command."""
    # This will be handled by the agent system
    return None


@command(
    name="/ping",
    description="Test bot connectivity and response time",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/ping"],
    help_text="""
🏓 Ping Test

Test bot connectivity and response time.

Usage:
/ping

What happens:
1. Bot responds with "pong"
2. Response time is measured
3. System status is briefly checked
4. Confirms bot is operational

💡 Tip: Use this to verify the bot is working properly.
    """
)
async def handle_ping_command(update, context, **kwargs):
    """Handle /ping command."""
    # This will be handled by the agent system
    return None


@command(
    name="/version",
    description="Show bot version and system information",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/version"],
    help_text="""
📱 Version Information

Show bot version and system information.

Usage:
/version

What you'll see:
• Bot version number
• System architecture
• Last update date
• Feature availability
• System status

💡 Tip: Use this to check if you're running the latest version.
    """
)
async def handle_version_command(update, context, **kwargs):
    """Handle /version command."""
    # This will be handled by the agent system
    return None 