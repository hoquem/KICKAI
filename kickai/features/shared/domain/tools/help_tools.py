#!/usr/bin/env python3
"""
Help Tools - CrewAI Native Implementation

This module provides tools for help and command information using CrewAI's
native parameter passing mechanism. Tools receive parameters directly via
function signatures following CrewAI best practices.
"""

from loguru import logger

import kickai.core.constants as constants_module
from kickai.core.enums import ChatType as ChatTypeEnum
from crewai.tools import tool
from kickai.utils.tool_validation import create_tool_response, validate_required_input
from kickai.utils.tool_validation import create_tool_response


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def help_response(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Generate a comprehensive help response for users based on their chat type and context.

    This tool should be used when users ask for help, show commands, or need guidance.
    The response should be tailored to the specific chat type (main chat vs leadership chat)
    and include all relevant commands with descriptions.

    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership)

    Returns:
        Formatted help response string
    """
    try:
        # Validate required parameters
        if not all([chat_type, telegram_id, team_id, username]):
            return create_tool_response(False, "Missing required parameters for help generation")

        logger.info(
            f"🔧 [TOOL DEBUG] Generating help for chat_type: {chat_type}, user: {telegram_id}, team: {team_id}, username: {username}"
        )

        # Normalize chat type
        chat_type_enum = _normalize_chat_type(chat_type)

        # Get commands from registry
        commands = _get_commands_for_chat_type(chat_type_enum)

        # Format the help message
        help_message = _format_help_message(chat_type_enum, commands, username)

        logger.info(f"✅ [TOOL DEBUG] Generated help message for {username}")
        return create_tool_response(True, "Operation completed successfully", data=help_message)

    except Exception as e:
        logger.error(f"❌ [TOOL DEBUG] Error in help_response: {e}")
        return create_tool_response(False, f"Failed to generate help response: {e}")


def _normalize_chat_type(chat_type: str) -> ChatTypeEnum:
    """Normalize chat type string to enum with proper error handling."""
    try:
        # Ensure chat_type is a string
        chat_type_str = str(chat_type) if chat_type is not None else "main"
        chat_type_enum = constants_module.normalize_chat_type(chat_type_str)

        # Validate that we got an enum
        if not hasattr(chat_type_enum, 'value'):
            logger.warning(f"⚠️ normalize_chat_type returned invalid type: {type(chat_type_enum)}, value: {chat_type_enum}")
            return ChatTypeEnum.MAIN  # Default fallback

        logger.debug(f"🔧 [TOOL DEBUG] Normalized chat_type: {chat_type_str} -> {chat_type_enum}")
        return chat_type_enum

    except Exception as e:
        logger.error(f"❌ Error normalizing chat_type '{chat_type}': {e}")
        return ChatTypeEnum.MAIN  # Default fallback


def _get_commands_for_chat_type(chat_type_enum: ChatTypeEnum) -> list:
    """Get commands available for the specified chat type."""
    from kickai.core.command_registry_initializer import get_initialized_command_registry

    registry = get_initialized_command_registry()

    # Get commands available for this chat type from the registry
    commands = []
    for cmd_metadata in registry._commands.values():
        # Check if command is available for this chat type
        if hasattr(cmd_metadata, "chat_type") and cmd_metadata.chat_type == chat_type_enum.value:
            commands.append(cmd_metadata)
        elif hasattr(cmd_metadata, "feature"):
            # Fallback: check if command should be available based on feature
            if cmd_metadata.feature in ["shared"]:
                commands.append(cmd_metadata)

    logger.info(f"🔧 [TOOL DEBUG] Found {len(commands)} commands for {chat_type_enum.value}")
    return commands


def _format_help_message(chat_type: ChatTypeEnum, commands: list, username: str) -> str:
    """Format the help message with commands organized by category."""
    try:
        # Get chat type display name safely
        try:
            chat_display_name = constants_module.get_chat_type_display_name(chat_type)
        except AttributeError as e:
            # Debug information to understand the issue
            logger.warning(f"⚠️ AttributeError in get_chat_type_display_name: {e}, chat_type={chat_type}, type={type(chat_type)}")
            # Fallback if chat_type is not a proper enum or has issues
            if hasattr(chat_type, 'value'):
                chat_display_name = chat_type.value.title()
            elif isinstance(chat_type, str):
                chat_display_name = chat_type.title()
            else:
                chat_display_name = str(chat_type).title()

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

# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_available_commands(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all available commands for the current chat type.

    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)

    Returns:
        JSON response with list of available commands and descriptions

    """
    try:
        # Normalize chat type
        chat_type_enum = _normalize_chat_type(chat_type)

        from kickai.core.command_registry_initializer import get_initialized_command_registry
        registry = get_initialized_command_registry()
        commands = registry.get_commands_by_chat_type(chat_type_enum.value)

        # Get chat display name
        chat_display_name = constants_module.get_chat_type_display_name(chat_type_enum)

        # Format response
        if not commands:
            return create_tool_response(
                success=True,
                message=f"No commands available for {chat_display_name} chat",
                data={
                    "chat_type": chat_type,
                    "chat_display_name": chat_display_name,
                    "commands": [],
                    "count": 0
                }
            )


        # Create structured command data
        commands_data = []
        for cmd in commands:
            # Convert permission level enum to string value
            permission_level = getattr(cmd, 'permission_level', 'unknown')
            if hasattr(permission_level, 'value'):
                permission_level = permission_level.value

            command_info = {
                "name": cmd.name,
                "description": cmd.description,
                "feature": getattr(cmd, 'feature', 'unknown'),
                "permission_level": permission_level,
                "examples": getattr(cmd, 'examples', [])
            }
            commands_data.append(command_info)

        return create_tool_response(
            success=True,
            message=f"Retrieved {len(commands)} available commands for {chat_display_name} chat",
            data={
                "chat_type": chat_type,
                "chat_display_name": chat_display_name,
                "commands": commands_data,
                "count": len(commands_data)
            }
        )

    except Exception as e:
        logger.error(f"Error getting available commands: {e}", exc_info=True)
        return create_tool_response(
            success=False,
            message=f"Error getting commands: {e!s}",
            data={"chat_type": chat_type, "error": str(e)}
        )


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_command_help(telegram_id: int, team_id: str, username: str, chat_type: str, command_name: str) -> str:
    """
    Get detailed help for a specific command.

    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type context for command availability
        command_name: Name of the command (with or without /)

    Returns:
        Detailed help message for the command
    """
    try:
        # Validate command name input
        validation_error = validate_required_input(command_name, "Command Name")
        if validation_error:
            return create_tool_response(False, validation_error.replace("❌ Error: ", ""))

        # Normalize command name
        if not command_name.startswith("/"):
            command_name = f"/{command_name}"

        # Normalize chat type
        chat_type_enum = _normalize_chat_type(chat_type)

        from kickai.core.command_registry_initializer import get_initialized_command_registry
        registry = get_initialized_command_registry()
        command = registry.get_command(command_name)

        if not command:
            return create_tool_response(False, f"Command {command_name} not found or not available in {chat_type_enum.value} chat.")

        # Format detailed help
        # Handle permission level safely
        permission_level = getattr(command, 'permission_level', 'unknown')
        if hasattr(permission_level, 'value'):
            permission_level = permission_level.value

        # Handle chat types safely - CommandMetadata has chat_type (string), not chat_types (list of enums)
        available_in = "All chats"
        if hasattr(command, 'chat_type') and command.chat_type:
            available_in = command.chat_type.title()

        help_text = f"""
📋 COMMAND HELP: {command_name.upper()}

📝 Description: {command.description}

🎯 Usage: {command.examples[0] if command.examples else command_name}

📋 Permission Level: {permission_level}

📋 Available In: {available_in}

💡 Examples:
"""
        if command.examples:
            for example in command.examples:
                help_text += f"• {example}\n"
        else:
            help_text += "• No specific examples available\n"

        return create_tool_response(True, "Operation completed successfully", data=help_text)

    except Exception as e:
        logger.error(f"Error getting command help: {e}")
        return create_tool_response(False, f"Failed to get command help: {e}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_welcome_message(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Generate a welcome message for users.

    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)

    Returns:
        Welcome message for the user
    """
    try:
        # Normalize chat type
        chat_type_enum = _normalize_chat_type(chat_type)

        # Generate welcome message based on chat type
        if chat_type_enum == ChatTypeEnum.MAIN:
            welcome_message = f"""
🎉 WELCOME TO THE TEAM, {username.upper()}!

👋 Welcome to KICKAI! We're excited to have you join our football community!

⚽ WHAT YOU CAN DO HERE:
• Check your status with /myinfo
• See available commands with /help
• View active players with /list
• Ask leadership to add you as a player

🔗 GETTING STARTED:
1. Ask leadership to add you - Team leaders can add you using /addplayer
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

        return create_tool_response(True, "Operation completed successfully", data=welcome_message.strip())

    except Exception as e:
        logger.error(f"Error generating welcome message: {e}", exc_info=True)
        return create_tool_response(False, f"Failed to generate welcome message: {e}")
