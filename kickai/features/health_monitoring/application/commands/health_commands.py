#!/usr/bin/env python3
"""
Health Monitoring Commands

This module registers all health monitoring related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# Note: System administration commands have been removed as they're not needed for now:
# - /logs - Log viewing functionality
# - /restart - System restart functionality  
# - /config - Configuration management
# - /backup - Backup functionality
# - /maintenance - Maintenance mode management
# - /diagnostics - System diagnostics

# These commands can be added back later if system administration features are required


@command(
    name="/healthcheck",
    description="Perform system health check (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="health_monitoring",
    chat_type=ChatType.LEADERSHIP,
    examples=["/healthcheck", "/healthcheck detailed"],
    parameters={"level": "Optional detail level (basic, detailed, full)"},
    help_text="""
🏥 System Health Check (Leadership Only)

Perform a comprehensive system health check.

Usage:
• /healthcheck - Basic health check
• /healthcheck detailed - Detailed health check
• /healthcheck full - Full system diagnostics

What's checked:
• Database connectivity
• LLM service status
• Telegram bot status
• Agent system health
• Memory and performance
• Error logs and alerts

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_healthcheck_command(update, context, **kwargs):
    """Handle /healthcheck command."""
    # This will be handled by the agent system
    return None


@command(
    name="/systemstatus",
    description="Show system status and performance metrics",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="health_monitoring",
    examples=["/systemstatus", "/systemstatus performance"],
    parameters={"metric": "Optional metric to focus on (performance, errors, usage)"},
    help_text="""
📊 System Status

View system status and performance metrics.

Usage:
• /systemstatus - Show general system status
• /systemstatus performance - Show performance metrics
• /systemstatus errors - Show recent errors
• /systemstatus usage - Show usage statistics

What you'll see:
• System uptime and status
• Performance metrics
• Error rates and logs
• Resource usage
• Service availability

💡 Tip: Monitor system health for optimal performance.
    """,
)
async def handle_systemstatus_command(update, context, **kwargs):
    """Handle /systemstatus command."""
    # This will be handled by the agent system
    return None


@command(
    name="/alerts",
    description="Manage system alerts (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="health_monitoring",
    chat_type=ChatType.LEADERSHIP,
    examples=["/alerts", "/alerts enable", "/alerts disable"],
    parameters={"action": "Action to perform (enable, disable, configure)"},
    help_text="""
🚨 System Alerts (Leadership Only)

Manage system alerts and notifications.

Usage:
• /alerts - Show current alert settings
• /alerts enable - Enable all alerts
• /alerts disable - Disable all alerts

Alert types:
• System errors and warnings
• Performance degradation
• Service outages
• Security alerts
• Usage thresholds

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_alerts_command(update, context, **kwargs):
    """Handle /alerts command."""
    # This will be handled by the agent system
    return None
