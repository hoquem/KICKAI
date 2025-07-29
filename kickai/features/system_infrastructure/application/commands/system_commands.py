#!/usr/bin/env python3
"""
System Infrastructure Commands

This module registers all system infrastructure related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# Note: System administration commands have been removed as they're not needed for now:
# - /config - Configuration management
# - /backup - Backup functionality
# - /maintenance - Maintenance mode management
# - /diagnostics - System diagnostics

# These commands can be added back later if system administration features are required


@command(
    name="/systemstatus",
    description="Show comprehensive system status (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="system_infrastructure",
    chat_type=ChatType.LEADERSHIP,
    examples=["/systemstatus", "/systemstatus detailed"],
    parameters={"level": "Optional detail level (basic, detailed, full)"},
    help_text="""
🔧 System Status (Leadership Only)

Show comprehensive system infrastructure status.

Usage:
• /systemstatus - Basic system status
• /systemstatus detailed - Detailed system status
• /systemstatus full - Full system diagnostics

What's checked:
• Database connectivity and health
• LLM service availability
• Telegram bot status
• Agent system health
• Memory and performance metrics
• Error logs and system alerts
• Configuration status

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_systemstatus_command(update, context, **kwargs):
    """Handle /systemstatus command."""
    # This will be handled by the agent system
    return None
