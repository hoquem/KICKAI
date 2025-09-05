#!/usr/bin/env python3
"""
System Help Tools - Clean Architecture Application Layer

This module provides CrewAI tools for system infrastructure help functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.system_infrastructure.domain.services.bot_status_service import (
    BotStatusService,
)


@tool("get_version_info")
async def get_version_info(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str
) -> str:
    """
    Retrieve bot version and system information.

    Provides comprehensive information about bot capabilities, technical
    stack, and current operational status for system awareness.

    Use when: System information inquiry is needed
    Required: Basic system access
    Context: System information workflow

    Returns: Bot version and system status details
    """
    try:
        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"📱 Version info request from user {telegram_username} ({telegram_id_int}) in team {team_id}"
        )

        # Get domain service via dependency injection
        container = get_container()
        bot_status_service = container.get_service(BotStatusService)
        if not bot_status_service:
            return "❌ Bot status service is not available"

        version_info = bot_status_service.get_version_info()

        if version_info.get("status") == "error":
            return f"❌ Error retrieving version information: {version_info.get('error', 'Unknown error')}"

        # Format the response at application boundary
        response = f"""📱 KICKAI Bot Version Information

🤖 Bot Details:
• Name: {version_info.get("name", "KICKAI Bot")}
• Version: {version_info.get("version", "Unknown")}
• Description: {version_info.get("description", "AI-powered football team management bot")}

⏰ System Status:
• Last Updated: {version_info.get("timestamp", "Unknown")}
• Status: ✅ Active and Running

💡 Features:
• 5-Agent CrewAI System
• Intelligent Message Processing
• Context-Aware Responses
• Multi-Chat Support
• Advanced Team Management

🎯 Current Capabilities:
• Player Registration & Management
• Team Administration
• Match Scheduling
• Attendance Tracking
• Communication Tools

🔧 Technical Stack:
• AI Engine: CrewAI with Google Gemini/OpenAI/Ollama
• Database: Firebase Firestore
• Bot Platform: Telegram Bot API
• Architecture: Clean Architecture with Dependency Injection

💪 Ready to help with all your football team management needs!"""

        logger.info(f"✅ Version info retrieved successfully for {telegram_username}")
        return response

    except Exception as e:
        logger.error(f"❌ Error getting version info: {e}")
        return f"❌ Error retrieving version information: {e!s}"


@tool("get_system_commands")
async def get_system_commands(
    telegram_id: str,
    team_id: str,
    telegram_username: str,
    chat_type: str,
    is_registered: bool = False,
    is_player: bool = False,
    is_team_member: bool = False,
) -> str:
    """
    Retrieve available commands for user permission level.

    Provides comprehensive list of accessible system commands based on
    user registration status, roles, and current chat context.

    Use when: Command guidance for user capabilities is needed
    Required: Basic system access
    Context: User assistance workflow

    Returns: Available commands grouped by permission level
    """
    try:
        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"📋 Available commands request from {telegram_username} ({telegram_id_int}) in {chat_type} chat, "
            f"registered={is_registered}, player={is_player}, member={is_team_member}"
        )

        # Import command registry (framework dependency at application boundary)
        from kickai.core.command_registry_initializer import get_initialized_command_registry
        from kickai.core.enums import PermissionLevel

        # Get the command registry
        registry = get_initialized_command_registry()

        # Get commands for this chat type (registry validates chat_type)
        commands = registry.get_commands_by_chat_type(chat_type)

        if not commands:
            return f"❌ No commands found for chat type: {chat_type}"

        # Filter commands based on user registration status (business logic at application boundary)
        available_commands = []

        for cmd in commands:
            # Always show public commands
            if cmd.permission_level == PermissionLevel.PUBLIC:
                available_commands.append(cmd)
            # Show player commands only if user is registered as player
            elif cmd.permission_level == PermissionLevel.PLAYER and is_player:
                available_commands.append(cmd)
            # Show leadership commands only if user is team member
            elif cmd.permission_level == PermissionLevel.LEADERSHIP and is_team_member:
                available_commands.append(cmd)
            # Show admin commands only if user is team member
            elif cmd.permission_level == PermissionLevel.ADMIN and is_team_member:
                available_commands.append(cmd)

        # Group filtered commands by permission level
        public_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PUBLIC
        ]
        player_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PLAYER
        ]
        leadership_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.LEADERSHIP
        ]
        admin_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.ADMIN
        ]

        # Build response (formatting at application boundary)
        response = f"📋 Available Commands for {chat_type.replace('_', ' ').title()}\n\n"

        if public_commands:
            response += "🌐 Public Commands (Available to everyone):\n"
            for cmd in public_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        if player_commands:
            response += "👤 Player Commands (Available to registered players):\n"
            for cmd in player_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        if leadership_commands:
            response += "👔 Leadership Commands (Available to team leadership):\n"
            for cmd in leadership_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        if admin_commands:
            response += "🔧 Admin Commands (Available to team admins):\n"
            for cmd in admin_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        # Add registration guidance for unregistered users
        if not is_registered:
            guidance = (
                "📞 To access more commands, contact team leadership to be added as a player.\n\n"
                if chat_type.lower() in ["main", "main_chat"]
                else "📝 To access more commands, ask team leadership to add you as a player.\n\n"
            )
            response += guidance

        response += "💡 Tip: You can also ask me questions in natural language!"

        logger.info(
            f"✅ Retrieved {len(available_commands)} commands for {chat_type} (filtered from {len(commands)} total)"
        )
        return response

    except Exception as e:
        logger.error(f"❌ Error getting available commands: {e}")
        return f"❌ Error retrieving available commands: {e!s}"
