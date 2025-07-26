#!/usr/bin/env python3
"""
System Infrastructure Commands

This module registers all system infrastructure related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# SYSTEM INFRASTRUCTURE COMMANDS
# ============================================================================

@command(
    name="/systemstatus",
    description="Show comprehensive system status (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="system_infrastructure",
    chat_type=ChatType.LEADERSHIP,
    examples=["/systemstatus", "/systemstatus detailed"],
    parameters={
        "level": "Optional detail level (basic, detailed, full)"
    },
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
    """
)
async def handle_systemstatus_command(update, context, **kwargs):
    """Handle /systemstatus command."""
    # This will be handled by the agent system
    return None


@command(
    name="/config",
    description="View and manage system configuration (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="system_infrastructure",
    chat_type=ChatType.LEADERSHIP,
    examples=["/config", "/config show", "/config validate"],
    parameters={
        "action": "Action to perform (show, validate, update)"
    },
    help_text="""
⚙️ System Configuration (Leadership Only)

View and manage system configuration settings.

Usage:
• /config - Show current configuration
• /config show - Display all configuration values
• /config validate - Validate configuration settings
• /config update - Start configuration update process

Configuration areas:
• Database settings
• LLM provider settings
• Telegram bot settings
• Agent configuration
• Logging settings
• Security settings

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_config_command(update, context, **kwargs):
    """Handle /config command."""
    # This will be handled by the agent system
    return None


@command(
    name="/backup",
    description="Create system backup (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="system_infrastructure",
    chat_type=ChatType.LEADERSHIP,
    examples=["/backup", "/backup full", "/backup data"],
    parameters={
        "type": "Backup type (full, data, config)"
    },
    help_text="""
💾 System Backup (Leadership Only)

Create system backups for data protection and recovery.

Usage:
• /backup - Create standard backup
• /backup full - Create full system backup
• /backup data - Backup data only
• /backup config - Backup configuration only

Backup types:
• full - Complete system backup
• data - Database and user data
• config - Configuration files
• logs - System logs

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_backup_command(update, context, **kwargs):
    """Handle /backup command."""
    # This will be handled by the agent system
    return None


@command(
    name="/maintenance",
    description="Manage system maintenance mode (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="system_infrastructure",
    chat_type=ChatType.LEADERSHIP,
    examples=["/maintenance", "/maintenance enable", "/maintenance disable"],
    parameters={
        "action": "Action to perform (enable, disable, status)"
    },
    help_text="""
🔧 System Maintenance (Leadership Only)

Manage system maintenance mode for updates and repairs.

Usage:
• /maintenance - Show maintenance status
• /maintenance enable - Enable maintenance mode
• /maintenance disable - Disable maintenance mode

Maintenance mode:
• Limits system functionality
• Shows maintenance message to users
• Allows safe system updates
• Prevents data corruption

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_maintenance_command(update, context, **kwargs):
    """Handle /maintenance command."""
    # This will be handled by the agent system
    return None


@command(
    name="/diagnostics",
    description="Run system diagnostics (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="system_infrastructure",
    chat_type=ChatType.LEADERSHIP,
    examples=["/diagnostics", "/diagnostics network", "/diagnostics performance"],
    parameters={
        "area": "Diagnostic area (network, performance, security, all)"
    },
    help_text="""
🔍 System Diagnostics (Leadership Only)

Run comprehensive system diagnostics for troubleshooting.

Usage:
• /diagnostics - Run basic diagnostics
• /diagnostics network - Network connectivity tests
• /diagnostics performance - Performance analysis
• /diagnostics security - Security checks
• /diagnostics all - Complete diagnostic suite

Diagnostic areas:
• Network connectivity
• Database performance
• LLM service health
• Memory usage
• Security vulnerabilities
• Configuration issues

💡 Note: This command is only available in the leadership chat.
    """
)
async def handle_diagnostics_command(update, context, **kwargs):
    """Handle /diagnostics command."""
    # This will be handled by the agent system
    return None
