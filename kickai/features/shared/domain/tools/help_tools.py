#!/usr/bin/env python3
"""
Help Tools - CrewAI Native Implementation

This module provides tools for help and command information using CrewAI's
native parameter passing mechanism. Tools receive parameters directly via
function signatures following CrewAI best practices.
"""

import os
from typing import Dict, List

from loguru import logger

# Import constants and enums properly
from kickai.core.enums import ChatType as ChatTypeEnum, PermissionLevel
import kickai.core.constants as constants_module
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    create_json_response,
    extract_single_value,
    format_tool_error,
    validate_required_input,
)


@tool("FINAL_HELP_RESPONSE")
def final_help_response(
    chat_type: str,
    telegram_id: str, 
    team_id: str,
    username: str
) -> str:
    """
    Generate a comprehensive help response for users based on their chat type and context.

    This tool should be used when users ask for help, show commands, or need guidance.
    The response should be tailored to the specific chat type (main chat vs leadership chat)
    and include all relevant commands with descriptions.

    Args:
        chat_type: Chat type (main/leadership)
        telegram_id: User's Telegram ID
        team_id: Team ID 
        username: User's username

    Returns:
        Formatted help response string
    """
    try:
        # Validate required parameters
        if not all([chat_type, telegram_id, team_id, username]):
            return create_json_response("error", message="Missing required parameters for help generation")

        logger.info(
            f"🔧 [TOOL DEBUG] Generating help for chat_type: {chat_type}, user: {telegram_id}, team: {team_id}, username: {username}"
        )

        # Normalize chat type to enum
        chat_type_enum = constants_module.normalize_chat_type(chat_type)

        # Get commands from the command registry instead of constants
        try:
            from kickai.core.command_registry_initializer import get_initialized_command_registry

            registry = get_initialized_command_registry()

            # Get commands available for this chat type from the registry
            commands = []
            for cmd_name, cmd_metadata in registry._commands.items():
                # Check if command is available for this chat type
                if hasattr(cmd_metadata, "chat_type") and cmd_metadata.chat_type == chat_type_enum:
                    commands.append(cmd_metadata)
                elif hasattr(cmd_metadata, "feature"):
                    # Fallback: check if command should be available based on feature
                    if cmd_metadata.feature in ["shared"]:
                        commands.append(cmd_metadata)

            logger.info(
                f"🔧 [TOOL DEBUG] Found {len(commands)} commands for {chat_type_enum.value}"
            )

            # Format the help message
            help_message = _format_help_message(chat_type_enum, commands, username)

            logger.info(f"✅ [TOOL DEBUG] Generated help message for {username}")
            return create_json_response("success", data=help_message)

        except Exception as e:
            logger.error(f"❌ [TOOL DEBUG] Error getting command registry: {e}")
            return create_json_response("error", message=f"Failed to retrieve command information: {e}")

    except Exception as e:
        logger.error(f"❌ [TOOL DEBUG] Error in FINAL_HELP_RESPONSE: {e}")
        return create_json_response("error", message=f"Failed to generate help response: {e}")


def _format_help_message(chat_type: ChatTypeEnum, commands: list, username: str) -> str:
    """Format the help message with commands organized by category."""
    try:
        # Get chat type display name
        chat_display_name = constants_module.get_chat_type_display_name(chat_type)

        # Start building the message
        message_parts = [
            "🤖 KICKAI Help System",
            f"Your Context: {chat_display_name.upper()} (User: {username})",
            f"📋 Available Commands for {chat_display_name}:",
            "",
        ]

        # Group commands by feature/category
        command_categories = _group_commands_by_category(commands)

        # Add each category
        for category, category_commands in command_categories.items():
            if category_commands:
                message_parts.append(f"{category}:")
                for cmd in category_commands:
                    message_parts.append(f"• {cmd.name} - {cmd.description}")
                message_parts.append("")

        # Add footer
        message_parts.extend(
            [
                "💡 Use /help [command] for detailed help on any command.",
                "---",
                "💡 Need more help?",
                "• Type /help [command] for detailed help",
                "• Contact team admin for support",
            ]
        )

        return "\n".join(message_parts)

    except Exception as e:
        logger.error(f"Error formatting help message: {e}", exc_info=True)
        return f"❌ Error formatting help message: {e!s}"


def _group_commands_by_category(commands: list) -> Dict[str, list]:
    """Group commands by their feature/category."""
    categories = {
        "Player Commands": [],
        "Leadership Commands": [],
        "Match Management": [],
        "Payments": [],
        "Communication": [],
        "Team Administration": [],
        "System": [],
    }

    # Map features to display categories
    feature_to_category = {
        "player_registration": "Player Commands",
        "match_management": "Match Management",
        "attendance_management": "Team Administration",  # Move attendance commands to Team Administration
        "communication": "Communication",
        "team_administration": "Team Administration",
        "system_infrastructure": "System",
        "shared": "System",
    }

    for cmd in commands:
        # Special handling for /update and /list commands - move to Team Administration
        if cmd.name in ["/update", "/list"]:
            category = "Team Administration"
        else:
            category = feature_to_category.get(cmd.feature, "System")
        categories[category].append(cmd)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


@tool("get_available_commands")
def get_available_commands(chat_type: str) -> str:
    """
    Get all available commands for the current chat type.

    Args:
        chat_type: Chat type (main/leadership/private)

    Returns:
        List of available commands with descriptions
    """
    try:
        # Normalize chat type
        chat_type_enum = constants_module.normalize_chat_type(chat_type)

        from kickai.core.command_registry_initializer import get_initialized_command_registry
        registry = get_initialized_command_registry()
        commands = registry.get_commands_by_chat_type(chat_type_enum.value)

        # Format response
        if not commands:
            return create_json_response("success", data=f"No commands available for chat type: {chat_type}")

        response_parts = [f"Available commands for {constants_module.get_chat_type_display_name(chat_type_enum)}:"]

        for cmd in commands:
            response_parts.append(f"• {cmd.name} - {cmd.description}")

        return create_json_response("success", data="\n".join(response_parts))

    except Exception as e:
        logger.error(f"Error getting available commands: {e}", exc_info=True)
        return create_json_response("error", message=f"Error getting commands: {e!s}")


@tool("get_command_help")
def get_command_help(command_name: str, chat_type: str) -> str:
    """
    Get detailed help for a specific command.

    Args:
        command_name: Name of the command (with or without /)
        chat_type: Chat type context for command availability

    Returns:
        Detailed help message for the command
    """
    try:
        # Validate command name input
        validation_error = validate_required_input(command_name, "Command Name")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ Error: ", ""))

        # Normalize command name
        if not command_name.startswith("/"):
            command_name = f"/{command_name}"

        # Normalize chat type
        chat_type_enum = constants_module.normalize_chat_type(chat_type)

        from kickai.core.command_registry_initializer import get_initialized_command_registry
        registry = get_initialized_command_registry()
        command = registry.get_command(command_name)

        if not command:
            return create_json_response("error", message=f"Command {command_name} not found or not available in {chat_type} chat.")

        # Format detailed help
        help_text = f"""
📋 COMMAND HELP: {command_name.upper()}

📝 Description: {command.description}

🎯 Usage: {command.examples[0] if command.examples else command_name}

📋 Permission Level: {command.permission_level.value}

📋 Available In: {', '.join([ct.value for ct in command.chat_types])}

💡 Examples:
"""
        if command.examples:
            for example in command.examples:
                help_text += f"• {example}\n"
        else:
            help_text += "• No specific examples available\n"

        return create_json_response("success", data=help_text)

    except Exception as e:
        logger.error(f"Error getting command help: {e}")
        return create_json_response("error", message=f"Failed to get command help: {e}")


@tool("get_welcome_message")
def get_welcome_message(username: str, chat_type: str, team_id: str) -> str:
    """
    Generate a welcome message for users.

    Args:
        username: User's username
        chat_type: Chat type (main/leadership/private)
        team_id: Team ID

    Returns:
        Welcome message for the user
    """
    try:
        # Normalize chat type
        chat_type_enum = constants_module.normalize_chat_type(chat_type)

        # Generate welcome message based on chat type
        if chat_type_enum == ChatTypeEnum.MAIN:
            welcome_message = f"""
🎉 WELCOME TO THE TEAM, {username.upper()}!

👋 Welcome to KICKAI! We're excited to have you join our football community!

⚽ WHAT YOU CAN DO HERE:
• Register as a player with /register [player_id]
• Check your status with /myinfo
• See available commands with /help
• View active players with /list

🔗 GETTING STARTED:
1. Register as a player - Use /register followed by your player ID
2. Check your status - Use /myinfo to see your current registration
3. Explore commands - Use /help to see all available options

📱 NEED HELP?
• Type /help for command information
• Contact team leadership for assistance
• Check pinned messages for important updates

Welcome aboard! Let's make this team amazing! ⚽🔥
            """
        elif chat_type_enum == ChatTypeEnum.LEADERSHIP:
            welcome_message = f"""
🎉 WELCOME TO LEADERSHIP, {username.upper()}!

👥 Welcome to the KICKAI Leadership Team! You're now part of our administrative team.

🛠️ ADMINISTRATIVE FEATURES:
• Manage players with /add, /approve, /listmembers
• Handle team operations with /announce, /remind
• Monitor team activity and performance
• Coordinate with other leadership members

📋 LEADERSHIP RESPONSIBILITIES:
• Player registration and approval
• Team communication and announcements
• Match organization and coordination
• Team policy enforcement

🔗 GETTING STARTED:
1. Review team policies and procedures
2. Familiarize yourself with admin commands
3. Coordinate with other leadership members
4. Monitor team activity and engagement

📱 ADMIN TOOLS:
• Use /help for command information
• Check /listmembers for team overview
• Use /announce for team communications
• Monitor system status and health

Welcome to the leadership team! Let's lead this team to success! 🏆⚽
            """
        else:  # Private chat
            welcome_message = f"""
🎉 WELCOME, {username.upper()}!

👋 Welcome to KICKAI! You're now connected to our football team management system.

⚽ PERSONAL FEATURES:
• Check your status with /myinfo
• Update your information with /update
• View your match history and attendance
• Access personalized team information

🔗 GETTING STARTED:
1. Check your current status - Use /myinfo
2. Update your information - Use /update if needed
3. Explore available commands - Use /help
4. Connect with the team community

📱 PERSONAL ASSISTANCE:
• Type /help for available commands
• Contact team leadership for support
• Check your personal dashboard
• Review your team participation

Welcome to the KICKAI family! We're here to support your football journey! ⚽💪
            """

        return create_json_response("success", data=welcome_message.strip())

    except Exception as e:
        logger.error(f"Error generating welcome message: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to generate welcome message: {e}")