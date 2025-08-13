#!/usr/bin/env python3
"""
Help Commands

This module registers help-related commands with the command registry.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from typing import List, Optional


@command(
    name="/help",
    description="Show context-aware help information",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    examples=["/help", "/help /addplayer", "/help /announce"],
    parameters={"command": "Optional command name for detailed help (e.g., /help /addplayer)"},
    help_text="""
📚 Help System

Get help information about available commands.

Usage:
• /help - Show all available commands for your role
• /help [command] - Get detailed help for a specific command

Examples:
• /help - List all commands you can use
• /help /addplayer - Get detailed help for adding players
• /help /announce - Get help for announcements (leadership only)

What you'll see:
• Commands available in your current chat
• Permission requirements for each command
• Usage examples and parameters
• Detailed explanations

💡 Tip: Commands shown depend on your role and current chat type.
    """,
)
async def handle_help_command(update, context, **kwargs):
    """Handle /help command."""
    # This will be handled by the agent system
    return None
