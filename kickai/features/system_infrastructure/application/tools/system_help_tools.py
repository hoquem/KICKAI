#!/usr/bin/env python3
"""
System Help Tools - Clean Architecture Application Layer

This module provides CrewAI tools for system infrastructure help functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Optional
from crewai.tools import tool
from loguru import logger

from kickai.features.system_infrastructure.domain.services.bot_status_service import BotStatusService
from kickai.utils.tool_validation import create_tool_response, validate_required_input, sanitize_input
from kickai.utils.constants import MAX_TEAM_ID_LENGTH, MAX_USER_ID_LENGTH


@tool("get_version_info", result_as_answer=True)
async def get_version_info(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get bot version and system information.

    This tool serves as the application boundary for version info functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: User's Telegram ID or dictionary with all parameters
        team_id: Team ID for context
        username: Username for logging
        chat_type: Chat type context

    Returns:
        JSON formatted version information including bot details, system status, 
        capabilities, and technical stack information
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(False, "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(False, "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(False, "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(False, "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(False, "Valid chat_type is required"
            )
        
        logger.info(f"📱 Version info request from user {username} ({telegram_id}) in team {team_id}")

        # Get domain service (pure business logic)
        bot_status_service = BotStatusService()
        version_info = bot_status_service.get_version_info()

        if version_info.get("status") == "error":
            return create_tool_response(False, f"Error retrieving version information: {version_info.get('error', 'Unknown error')}"
            )

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
• 6-Agent CrewAI System
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

        logger.info(f"✅ Version info retrieved successfully for {username}")
        return create_tool_response(True, "Operation completed successfully", data=response)

    except Exception as e:
        logger.error(f"❌ Error getting version info: {e}")
        return create_tool_response(False, f"Error retrieving version information: {e!s}")


@tool("get_system_available_commands", result_as_answer=True)
async def get_system_available_commands(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    is_registered: bool = False,
    is_player: bool = False,
    is_team_member: bool = False,
) -> str:
    """
    Get list of available commands for a user in the given chat type.

    This tool serves as the application boundary for command listing functionality.
    It handles framework concerns and delegates business logic to command registry services.

    Args:
        telegram_id: User's Telegram ID or dictionary with all parameters
        team_id: Team ID for context
        username: Username for logging
        chat_type: Chat type ("main", "leadership", "private")
        is_registered: Whether the user is registered in the system
        is_player: Whether the user is a registered player
        is_team_member: Whether the user is a team member

    Returns:
        JSON formatted list of available commands grouped by permission level
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            is_registered = params.get('is_registered', False)
            is_player = params.get('is_player', False)
            is_team_member = params.get('is_team_member', False)
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(False, "Invalid telegram_id format"
                    )
                    
            # Boolean conversion for optional parameters
            if isinstance(is_registered, str):
                is_registered = is_registered.lower() in ('true', '1', 'yes')
            if isinstance(is_player, str):
                is_player = is_player.lower() in ('true', '1', 'yes')
            if isinstance(is_team_member, str):
                is_team_member = is_team_member.lower() in ('true', '1', 'yes')
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(False, "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(False, "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(False, "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(False, "Valid chat_type is required"
            )
        
        logger.info(
            f"📋 Available commands request from {username} ({telegram_id}) in {chat_type} chat, "
            f"registered={is_registered}, player={is_player}, member={is_team_member}"
        )

        # Import command registry (framework dependency at application boundary)
        from kickai.core.command_registry_initializer import get_initialized_command_registry
        from kickai.core.enums import ChatType, PermissionLevel

        # Get the command registry
        registry = get_initialized_command_registry()

        # Convert chat_type string to enum
        chat_type_enum = None
        if chat_type.lower() in ["main", "main_chat"]:
            chat_type_enum = ChatType.MAIN
        elif chat_type.lower() in ["leadership", "leadership_chat"]:
            chat_type_enum = ChatType.LEADERSHIP
        else:
            return create_tool_response(False, f"Invalid chat type: {chat_type}. Must be 'main' or 'leadership'"
            )

        # Get commands for this chat type
        commands = registry.get_commands_by_chat_type(chat_type)

        if not commands:
            return create_tool_response(False, f"No commands found for chat type: {chat_type}"
            )

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
        public_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PUBLIC]
        player_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PLAYER]
        leadership_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.LEADERSHIP]
        admin_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.ADMIN]

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
            if chat_type.lower() in ["main", "main_chat"]:
                response += "📞 To access more commands, contact team leadership to be added as a player.\n\n"
            elif chat_type.lower() in ["leadership", "leadership_chat"]:
                response += "📝 To access more commands, ask team leadership to add you as a player.\n\n"

        response += "💡 Tip: You can also ask me questions in natural language!"

        logger.info(
            f"✅ Retrieved {len(available_commands)} commands for {chat_type} (filtered from {len(commands)} total)"
        )
        return create_tool_response(True, "Operation completed successfully", data=response)

    except Exception as e:
        logger.error(f"❌ Error getting available commands: {e}")
        return create_tool_response(False, f"Error retrieving available commands: {e!s}")