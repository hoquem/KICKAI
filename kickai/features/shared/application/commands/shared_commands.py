#!/usr/bin/env python3
"""
Shared Commands Module

This module contains shared/common commands that are available across different chat types.
"""

from loguru import logger

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.context_types import create_context_from_telegram_message
from kickai.core.enums import ChatType
from typing import List, Optional

# ============================================================================
# SHARED COMMANDS
# ============================================================================


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
    """,
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
    """,
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
    parameters={"type": "Optional type to list (players, members, all)"},
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
    """,
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
    parameters={"identifier": "Player ID, phone number, or leave empty for yourself"},
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
    """,
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
    """,
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
    """,
)
async def handle_version_command(update, context, **kwargs):
    """Handle /version command."""
    # This will be handled by the agent system
    return None


@command(
    name="/update",
    description="Update your information (context-aware for players/team members)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=[
        "/update phone 07123456789",
        "/update position midfielder",
        "/update email admin@example.com",
    ],
    parameters={
        "field": "Field to update (phone, position, email, role, etc.)",
        "value": "New value for the field",
    },
    help_text="""
📝 Update Command (Context-Aware)

Update your personal information. The available fields depend on your role and chat type.

Main Chat (Players):
• phone - Your contact phone number
• position - Your football position
• email - Your email address
• emergency_contact_name - Emergency contact name
• emergency_contact_phone - Emergency contact phone
• medical_notes - Medical information

Leadership Chat (Team Members):
• phone - Your contact phone number
• email - Your email address
• emergency_contact_name - Emergency contact name
• emergency_contact_phone - Emergency contact phone
• role - Your administrative role (requires admin approval)

Usage:
/update [field] [new value]

Examples:
• /update phone 07123456789
• /update position midfielder
• /update email admin@example.com
• /update role Assistant Coach

💡 Need help? Try /update without arguments to see available fields.
    """,
)
async def handle_update_command_wrapper(update, context, **kwargs):
    """Handle /update command with context-aware routing."""
    try:
        # Extract command arguments
        message_text = update.message.text
        command_parts = message_text.split()
        command_args = command_parts[1:] if len(command_parts) > 1 else []

        # Create user context
        user_context = create_context_from_telegram_message(
            telegram_id=str(update.effective_user.id),
            team_id=kwargs.get("team_id", "UNKNOWN"),
            chat_id=str(update.effective_chat.id),
            chat_type=kwargs.get("chat_type", ChatType.MAIN),
            message_text=message_text,
            username=update.effective_user.username or update.effective_user.first_name,
            telegram_name=update.effective_user.first_name,
            is_registered=True,  # Assuming registered users can use /update
            is_player=kwargs.get("chat_type") == ChatType.MAIN,
            is_team_member=kwargs.get("chat_type") == ChatType.LEADERSHIP,
        )

        # Route to the appropriate handler
        from kickai.features.shared.domain.commands.update_command_handler import (
            handle_update_command,
        )

        result = await handle_update_command(
            user_context, command_args, kwargs.get("crewai_system")
        )

        return result.message if result.success else f"❌ {result.message}"

    except Exception as e:
        logger.error(f"Error handling /update command: {e}")
        return "❌ Sorry, I encountered an error processing your update request. Please try again."
