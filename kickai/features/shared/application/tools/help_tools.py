#!/usr/bin/env python3
"""
Help Tools - Clean Architecture Application Layer

This module provides CrewAI tools for help functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""


from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ChatType
from kickai.features.shared.domain.interfaces.help_service_interface import IHelpService


@tool("show_help_commands")
async def show_help_commands(chat_type: str, username: str = "user") -> str:
    """
    Provide comprehensive system guidance and available features.

    Delivers contextual help information tailored to user's role and
    access level, enabling effective system navigation and usage.

    Use when: User needs guidance or feature discovery
    Required: Valid user context
    Context: User assistance workflow

    Returns: Comprehensive help information summary
    """
    try:
        # Validate and normalize inputs
        chat_type_enum, error_msg = _validate_chat_type(chat_type)
        if error_msg:
            return error_msg

        username = str(username).strip() if username else "user"
        if not username:
            username = "user"

        logger.info(f"🔧 Help request from user '{username}' in {chat_type_enum.value} chat")

        # Get domain service with centralized error handling
        help_service = _get_help_service()
        if not help_service:
            return "❌ Help service is currently unavailable. Please try again later."

        # Execute business logic with comprehensive error handling
        try:
            help_content = help_service.generate_help_content(chat_type_enum, username)
            formatted_message = help_service.format_help_message(help_content)

            logger.info(
                f"✅ Generated help message for '{username}' in {chat_type_enum.value} chat"
            )
            return formatted_message

        except Exception as e:
            logger.warning(f"⚠️ Help content generation failed for user '{username}': {e}")
            return (
                f"⚠️ Unable to generate personalized help content: {e!s}\n\n"
                "Please try '/help' again or contact team leadership for assistance."
            )

    except Exception as e:
        logger.error(f"❌ Unexpected error in show_help_commands: {e}")
        return (
            f"❌ Sorry, an unexpected error occurred while generating help information.\n\n"
            f"Error details: {e!s}\n\n"
            "Please contact team leadership for assistance."
        )


def _get_help_service() -> IHelpService | None:
    """
    Get help service instance with comprehensive error handling.

    Returns:
        IHelpService instance or None if unavailable
    """
    try:
        container = get_container()
        help_service = container.get_service(IHelpService)
        if not help_service:
            logger.error("❌ Help service not registered in container")
            return None
        return help_service
    except Exception as e:
        logger.error(f"❌ Failed to get help service: {e}")
        return None


def _normalize_chat_type(chat_type: str) -> ChatType:
    """
    Normalize chat type string to enum with proper error handling.

    Args:
        chat_type: Chat type as string

    Returns:
        ChatType enum value

    Raises:
        ValueError: If chat_type cannot be normalized
    """
    if not chat_type:
        return ChatType.MAIN

    try:
        # Map common variations to enum values
        chat_type_lower = str(chat_type).lower().strip()

        if chat_type_lower in {"leadership", "admin"}:
            return ChatType.LEADERSHIP
        elif chat_type_lower in {"private", "direct", "dm"}:
            return ChatType.PRIVATE
        elif chat_type_lower in {"main", "group", "team"}:
            return ChatType.MAIN
        else:
            # For unknown types, default to MAIN but log the attempt
            logger.warning(f"Unknown chat type '{chat_type}', defaulting to MAIN")
            return ChatType.MAIN

    except Exception as e:
        logger.error(f"❌ Error normalizing chat_type '{chat_type}': {e}")
        raise ValueError(f"Invalid chat type: {chat_type}") from e


def _validate_chat_type(chat_type: str) -> tuple[ChatType, str | None]:
    """
    Validate and normalize chat type with error message generation.

    Args:
        chat_type: Chat type string to validate

    Returns:
        Tuple of (ChatType enum, error message or None)
    """
    if not chat_type or not chat_type.strip():
        return ChatType.MAIN, "❌ Chat type is required"

    try:
        return _normalize_chat_type(chat_type), None
    except ValueError:
        valid_types = ", ".join([ct.value for ct in ChatType])
        return ChatType.MAIN, f"❌ Invalid chat type '{chat_type}'. Valid options: {valid_types}"


@tool("show_help_final")
async def show_help_final(chat_type: str, username: str = "user") -> str:
    """
    Deliver complete system assistance information.

    Provides comprehensive help content with full context and
    feature guidance for effective system utilization.

    Use when: Complete system overview is needed
    Required: Valid user context
    Context: Comprehensive assistance workflow

    Returns: Complete system help information
    """
    # Delegate to main help response tool
    return await show_help_commands(chat_type, username)


@tool("show_help_usage")
async def show_help_usage(command: str, username: str = "user") -> str:
    """
    Provide targeted assistance for specific system feature.

    Delivers detailed guidance for particular functionality,
    enabling users to understand and effectively use specific features.

    Use when: Specific feature guidance is needed
    Required: Valid feature identifier
    Context: Feature-specific assistance workflow

    Returns: Detailed feature usage guidance
    """
    try:
        # Validate and sanitize inputs
        if not command or not str(command).strip():
            return "❌ Command name is required and cannot be empty"

        command = str(command).strip()
        username = str(username).strip() if username else "user"
        if not username:
            username = "user"

        # Basic command validation for security
        if len(command) > 100 or any(char in command for char in ["<", ">", "&", '"', "'"]):
            logger.warning(f"Suspicious command format from user '{username}': {command}")
            return "❌ Invalid command format. Please use standard command names."

        logger.info(f"🔧 Command help request from '{username}' for command: '{command}'")

        # Return specific command help with improved formatting
        return (
            f"📚 Command Help: {command}\n\n"
            f"For comprehensive help with all available commands, use '/help'.\n\n"
            f"If you need specific guidance with '{command}', please contact team leadership "
            f"or ask in the appropriate chat channel."
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error getting command help: {e}")
        return (
            f"❌ Unable to retrieve command help at this time.\n\n"
            f"Please try '/help' for general assistance.\n\n"
            f"Error details: {e!s}"
        )


@tool("show_help_welcome")
async def show_help_welcome(username: str = "user", chat_type: str = "main") -> str:
    """
    Deliver personalized welcome message for new users.

    Provides friendly introduction to system capabilities and
    initial guidance for effective onboarding experience.

    Use when: User first-time interaction or system introduction
    Required: Valid user identifier
    Context: User onboarding workflow

    Returns: Personalized welcome message with guidance
    """
    try:
        # Validate and sanitize inputs
        username = str(username).strip() if username else "user"
        if not username:
            username = "user"

        # Basic username validation for security
        if len(username) > 100 or any(char in username for char in ["<", ">", "&", '"', "'"]):
            logger.warning(f"Suspicious username format: {username}")
            username = "user"

        # Normalize chat type with fallback
        try:
            chat_type_enum = _normalize_chat_type(str(chat_type) if chat_type else "main")
        except ValueError:
            chat_type_enum = ChatType.MAIN

        logger.info(f"🔧 Welcome message request from '{username}' in {chat_type_enum.value} chat")

        # Get domain service with centralized error handling
        help_service = _get_help_service()
        if not help_service:
            # Provide fallback welcome message
            return (
                f"🎉 Welcome to KICKAI, {username}!\n\n"
                f"👋 Use '/help' to get started and see available commands.\n\n"
                f"💡 Note: Help service is temporarily unavailable, but basic functionality is active."
            )

        # Generate personalized welcome message with comprehensive error handling
        try:
            welcome_content = help_service.generate_welcome_message(username, chat_type_enum)
            logger.info(f"✅ Generated personalized welcome message for '{username}'")
            return welcome_content

        except Exception as e:
            logger.warning(f"⚠️ Welcome message generation failed for '{username}': {e}")
            return (
                f"🎉 Welcome to KICKAI, {username}!\n\n"
                f"👋 Use '/help' to get started and see available commands.\n\n"
                f"⚠️ Unable to generate personalized welcome content at this time."
            )

    except Exception as e:
        logger.error(f"❌ Unexpected error generating welcome message: {e}")
        return (
            f"🎉 Welcome to KICKAI!\n\n"
            f"👋 Use '/help' to get started and see available commands.\n\n"
            f"❌ Error generating personalized message: {e!s}"
        )


@tool("get_system_commands")
async def get_system_commands(chat_type: str, username: str = "user") -> str:
    """
    Retrieve available system features based on user permissions.

    Provides contextual listing of accessible functionality
    tailored to user's role and authorization level.

    Use when: Feature discovery or capability review is needed
    Required: Valid user context and permissions
    Context: System capability exploration workflow

    Returns: Contextual feature availability summary
    """
    try:
        # Validate and normalize inputs
        chat_type_enum, error_msg = _validate_chat_type(chat_type)
        if error_msg:
            return error_msg

        username = str(username).strip() if username else "user"
        if not username:
            username = "user"

        # Basic username validation for security
        if len(username) > 100:
            username = username[:100]

        logger.info(
            f"🔧 Available commands request from '{username}' in {chat_type_enum.value} chat"
        )

        # Get domain service with centralized error handling
        help_service = _get_help_service()
        if not help_service:
            return (
                "❌ Help service is currently unavailable.\n\n"
                "Please try '/help' later or contact team leadership for assistance."
            )

        # Generate help content with comprehensive error handling
        try:
            help_content = help_service.generate_help_content(chat_type_enum, username)
        except Exception as e:
            logger.warning(f"⚠️ Help content generation failed for '{username}': {e}")
            return (
                f"⚠️ Unable to retrieve personalized command list: {e!s}\n\n"
                f"Please try '/help' for general assistance."
            )

        # Format command list with improved structure
        try:
            commands_text = f"📋 Available Commands ({chat_type_enum.value} chat):\n\n"

            # Safety check for commands attribute
            if not hasattr(help_content, "commands") or not help_content.commands:
                return (
                    f"📋 Available Commands ({chat_type_enum.value} chat):\n\n"
                    f"⚠️ No commands currently available for your context.\n\n"
                    f"Please contact team leadership for assistance."
                )

            for cmd in help_content.commands:
                commands_text += f"🔸 {cmd.name} - {cmd.description}\n"
                if hasattr(cmd, "examples") and cmd.examples:
                    commands_text += f"   Example: {cmd.examples[0]}\n"
                commands_text += "\n"

            commands_text += "\n💡 Use '/help' for detailed information about each command."

            logger.info(
                f"✅ Generated commands list for '{username}' ({len(help_content.commands)} commands)"
            )
            return commands_text

        except Exception as e:
            logger.error(f"❌ Error formatting commands for '{username}': {e}")
            return (
                f"❌ Error formatting command list: {e!s}\n\n"
                f"Please try '/help' for general assistance."
            )

    except Exception as e:
        logger.error(f"❌ Unexpected error getting available commands: {e}")
        return (
            f"❌ Unable to retrieve available commands at this time.\n\n"
            f"Please try '/help' later or contact team leadership.\n\n"
            f"Error details: {e!s}"
        )
