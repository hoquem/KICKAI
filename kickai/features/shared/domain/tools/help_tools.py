#!/usr/bin/env python3
"""
Help Tools

This module provides tools for help and command information.
"""

import os

# Import command-related functions directly from the constants.py file to avoid circular imports
import sys

from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
exec(open('kickai/core/constants.py').read())
from kickai.core.enums import ChatType as ChatTypeEnum
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    validate_required_input,
)


@tool("FINAL_HELP_RESPONSE")
def final_help_response(chat_type: str, user_id: str, team_id: str, username: str) -> str:
    """
    Generate a comprehensive help response for users based on their chat type and context.

    This tool should be used when users ask for help, show commands, or need guidance.
    The response should be tailored to the specific chat type (main chat vs leadership chat)
    and include all relevant commands with descriptions.

    Args:
        chat_type: Chat type (string or enum) from the available context parameters
        user_id: User ID from the available context parameters
        team_id: Team ID from the available context parameters
        username: Username from the available context parameters

    Returns:
        Formatted help response string

    Example:
        If context provides "chat_type: main, user_id: 12345, team_id: TEST, username: John",
        call this tool with chat_type="main", user_id="12345", team_id="TEST", username="John"
    """
    try:
        # Validate inputs - these should NOT be None, they must come from context
        validation_error = validate_required_input(chat_type, "Chat Type")
        if validation_error:
            return format_tool_error(
                "Chat Type is required and must be provided from available context"
            )

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return format_tool_error(
                "User ID is required and must be provided from available context"
            )

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return format_tool_error(
                "Team ID is required and must be provided from available context"
            )

        validation_error = validate_required_input(username, "Username")
        if validation_error:
            return format_tool_error(
                "Username is required and must be provided from available context"
            )

        logger.info(
            f"🔧 [TOOL DEBUG] Generating help for chat_type: {chat_type}, user: {user_id}, team: {team_id}, username: {username}"
        )

        # Normalize chat type to enum
        chat_type_enum = normalize_chat_type(chat_type)

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

        except Exception as e:
            logger.warning(f"Failed to get commands from registry, falling back to constants: {e}")
            # Fallback to constants if registry fails
            commands = get_commands_for_chat_type(chat_type_enum)

        # Generate help message
        help_message = _format_help_message(chat_type_enum, commands, username)

        logger.info(f"🔧 [TOOL DEBUG] Final response preview: {help_message[:100]}...")

        return help_message

    except Exception as e:
        logger.error(f"Error generating help response: {e}", exc_info=True)
        return format_tool_error(f"Failed to generate help response: {e}")


def _format_help_message(chat_type: ChatTypeEnum, commands: list, username: str) -> str:
    """Format the help message with commands organized by category."""
    try:
        # Get chat type display name
        chat_display_name = get_chat_type_display_name(chat_type)

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


def _group_commands_by_category(commands: list) -> dict[str, list]:
    """Group commands by their feature/category."""
    categories = {
        "Player Commands": [],
        "Leadership Commands": [],
        "Match Management": [],
        "Payments": [],
        "Communication": [],
        "Team Administration": [],
        "System": [],
        "Health & Monitoring": [],
    }

    # Map features to display categories
    feature_to_category = {
        "player_registration": "Player Commands",
        "match_management": "Match Management",
        "attendance_management": "Team Administration",  # Move attendance commands to Team Administration
        "payment_management": "Payments",
        "communication": "Communication",
        "team_administration": "Team Administration",
        "health_monitoring": "Health & Monitoring",
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
    Get all available commands for a specific chat type.

    Args:
        chat_type: The chat type (main_chat, leadership_chat, or private)

    Returns:
        List of available commands with descriptions
    """
    try:
        # Handle JSON string input using utility function
        chat_type = extract_single_value(chat_type, "chat_type")

        # Validate input
        validation_error = validate_required_input(chat_type, "Chat Type")
        if validation_error:
            return validation_error

        # Normalize chat type
        chat_type_enum = normalize_chat_type(chat_type)

        # Get commands
        commands = constants_module.get_commands_for_chat_type(chat_type_enum)

        # Format response
        if not commands:
            return f"No commands available for chat type: {chat_type}"

        response_parts = [f"Available commands for {get_chat_type_display_name(chat_type_enum)}:"]

        for cmd in commands:
            response_parts.append(f"• {cmd.name} - {cmd.description}")

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error getting available commands: {e}", exc_info=True)
        return format_tool_error(f"Error getting commands: {e!s}")


@tool("get_command_help")
def get_command_help(command_name: str, chat_type: str = "main") -> str:
    """
    Get detailed help for a specific command.

    Args:
        command_name: Name of the command (with or without /)
        chat_type: Chat type (main, leadership, private)

    Returns:
        Detailed help message for the command
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(command_name, "Command Name")
        if validation_error:
            return format_tool_error(validation_error)

        validation_error = validate_required_input(chat_type, "Chat Type")
        if validation_error:
            return format_tool_error(validation_error)

        # Normalize command name
        if not command_name.startswith("/"):
            command_name = f"/{command_name}"

        # Normalize chat type
        chat_type_enum = normalize_chat_type(chat_type)

        # Get command details
        command = get_command_by_name(command_name)

        if not command:
            return f"❌ Command {command_name} not found or not available in {chat_type} chat."

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

        return help_text

    except Exception as e:
        logger.error(f"Error getting command help: {e}")
        return format_tool_error(f"Failed to get command help: {e}")


@tool("get_new_member_welcome_message")
def get_new_member_welcome_message(
    username: str,
    chat_type: str,
    team_id: str,
    user_id: str
) -> str:
    """
    Generate a welcome message for new members joining the chat.

    Args:
        username: New member's username
        chat_type: Chat type (main, leadership, private)
        team_id: Team ID
        user_id: User ID

    Returns:
        Welcome message for the new member
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(username, "Username")
        if validation_error:
            return format_tool_error(validation_error)

        validation_error = validate_required_input(chat_type, "Chat Type")
        if validation_error:
            return format_tool_error(validation_error)

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return format_tool_error(validation_error)

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return format_tool_error(validation_error)

        # Normalize chat type
        chat_type_enum = normalize_chat_type(chat_type)

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
• View pending players with /pending
• Schedule training with /scheduletraining
• Manage matches with /creatematch, /squadselect
• Send announcements with /announce

📋 QUICK START:
1. View pending players - Use /pending to see who needs approval
2. Add new players - Use /add [name] [phone] [position]
3. Approve players - Use /approve [player_id]
4. Explore admin commands - Use /help for full list

🎯 TEAM MANAGEMENT:
• Player registration and approval
• Training session management
• Match scheduling and squad selection
• Team communication and announcements

Welcome to the leadership team! Let's build something great together! 👥🌟
            """
        else:  # PRIVATE
            welcome_message = f"""
🎉 WELCOME, {username.upper()}!

👋 Welcome to KICKAI! You're now connected to our football management system.

⚽ AVAILABLE COMMANDS:
• Get help with /help
• Check your status with /myinfo
• Register as a player with /register

🔗 NEXT STEPS:
1. Join the main team chat for full access
2. Register as a player or team member
3. Start participating in team activities

Welcome! We're glad to have you on board! ⚽
            """

        return welcome_message

    except Exception as e:
        logger.error(f"Error generating new member welcome message: {e}")
        return format_tool_error(f"Failed to generate welcome message: {e}")
