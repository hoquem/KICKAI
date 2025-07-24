#!/usr/bin/env python3
"""
Help Tools for KICKAI

This module provides tools for generating help responses and command information.
"""

import logging

from crewai.tools import tool

from kickai.core.constants import (
    get_chat_type_display_name,
    get_command_by_name,
    get_commands_for_chat_type,
    normalize_chat_type,
)
from kickai.core.enums import ChatType as ChatTypeEnum

logger = logging.getLogger(__name__)


@tool("FINAL_HELP_RESPONSE")
def final_help_response(chat_type: str, user_id: str, team_id: str, username: str = "Unknown") -> str:
    """
    Generate a comprehensive help response for users based on their chat type and context.

    This tool should be used when users ask for help, show commands, or need guidance.
    The response should be tailored to the specific chat type (main chat vs leadership chat)
    and include all relevant commands with descriptions.

    Args:
        context: Dictionary containing:
            - chat_type: Chat type (string or enum)
            - user_id: User ID
            - team_id: Team ID
            - username: Username (optional)
            - message_text: Original message (optional)

    Returns:
        Formatted help response string
    """
    try:
        # Parameters are now passed explicitly - no context extraction needed
        logger.info(f"🔧 [TOOL DEBUG] Generating help for chat_type: {chat_type}, user: {user_id}, team: {team_id}")

        # Normalize chat type to enum
        chat_type_enum = normalize_chat_type(chat_type)

        # Get commands for this chat type
        commands = get_commands_for_chat_type(chat_type_enum)

        # Generate help message
        help_message = _format_help_message(chat_type_enum, commands, username)

        logger.info(f"🔧 [TOOL DEBUG] Final response preview: {help_message[:100]}...")

        return help_message

    except Exception as e:
        logger.error(f"Error generating help response: {e}", exc_info=True)
        return f"❌ Error generating help: {e!s}"


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
                ""
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
            message_parts.extend([
                "💡 Use /help [command] for detailed help on any command.",
                "---",
                "💡 Need more help?",
                "• Type /help [command] for detailed help",
                "• Contact team admin for support"
            ])

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
        "Attendance": [],
        "Payments": [],
        "Communication": [],
        "Team Administration": [],
        "System": [],
        "Health & Monitoring": []
    }

    # Map features to display categories
    feature_to_category = {
        "player_registration": "Player Commands",
        "match_management": "Match Management",
        "attendance_management": "Attendance",
        "payment_management": "Payments",
        "communication": "Communication",
        "team_administration": "Team Administration",
        "health_monitoring": "Health & Monitoring",
        "system_infrastructure": "System",
        "shared": "System"
    }

    for cmd in commands:
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
        # Normalize chat type
        chat_type_enum = normalize_chat_type(chat_type)

        # Get commands
        commands = get_commands_for_chat_type(chat_type_enum)

        # Format response
        if not commands:
            return f"No commands available for chat type: {chat_type}"

        response_parts = [f"Available commands for {get_chat_type_display_name(chat_type_enum)}:"]

        for cmd in commands:
            response_parts.append(f"• {cmd.name} - {cmd.description}")

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error getting available commands: {e}", exc_info=True)
        return f"❌ Error getting commands: {e!s}"


@tool("get_command_help")
def get_command_help(command_name: str, chat_type: str = "main") -> str:
    """
    Get detailed help for a specific command.

    Args:
        command_name: The command name (e.g., /register, /help)
        chat_type: The chat type context

    Returns:
        Detailed help information for the command
    """
    try:
        # Get command definition
        cmd = get_command_by_name(command_name)

        if not cmd:
            return f"❌ Command '{command_name}' not found."

        # Check if command is available in this chat type
        chat_type_enum = normalize_chat_type(chat_type)
        if chat_type_enum not in cmd.chat_types:
            return f"❌ Command '{command_name}' is not available in {get_chat_type_display_name(chat_type_enum)}."

        # Build detailed help
        help_parts = [
            f"📖 Help for {cmd.name}",
            f"Description: {cmd.description}",
            f"Permission Level: {cmd.permission_level.value}",
            f"Available in: {', '.join(get_chat_type_display_name(ct) for ct in cmd.chat_types)}",
            f"Feature: {cmd.feature}",
            ""
        ]

        if cmd.examples:
            help_parts.append("Examples:")
            for example in cmd.examples:
                help_parts.append(f"• {example}")
            help_parts.append("")

        help_parts.append("💡 Use this command in the appropriate chat type.")

        return "\n".join(help_parts)

    except Exception as e:
        logger.error(f"Error getting command help: {e}", exc_info=True)
        return f"❌ Error getting command help: {e!s}"
