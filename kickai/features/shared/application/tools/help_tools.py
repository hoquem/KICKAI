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
from kickai.features.shared.domain.services.help_service import HelpService
# Removed unused import: create_tool_response (now returning formatted text directly)


@tool("show_help_commands")
async def show_help_commands(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Show comprehensive help and available commands based on user's context.

    This tool serves as the application boundary for help functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username  
        chat_type: Chat type (main/leadership/private)

    Returns:
        Formatted help text string for direct display
    """
    try:
        # Validate required parameters at application boundary
        if not all([chat_type, telegram_id, team_id, username]):
            return "❌ Error: Missing required parameters for help generation. Please try again."

        # Simple type conversion
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🔧 Help request from user {username} ({telegram_id_int}) in {chat_type} chat for team {team_id}"
        )

        # Normalize chat type to enum
        chat_type_enum = _normalize_chat_type(chat_type)

        # Get domain service (pure business logic)
        help_service = HelpService()
        
        # Execute pure business logic
        help_content = help_service.generate_help_content(chat_type_enum, username)
        formatted_message = help_service.format_help_message(help_content)

        logger.info(f"✅ Generated help message for {username} in {chat_type} chat")
        
        # Return formatted text directly (no JSON wrapper)
        return formatted_message

    except Exception as e:
        logger.error(f"❌ Error generating help response: {e}")
        return f"❌ Sorry, I couldn't generate the help information right now. Error: {str(e)}\n\nPlease contact team leadership for assistance."


def _normalize_chat_type(chat_type: str) -> ChatType:
    """
    Normalize chat type string to enum with proper error handling.
    
    Args:
        chat_type: Chat type as string
        
    Returns:
        ChatType enum value
    """
    try:
        chat_type_str = str(chat_type) if chat_type is not None else "main"
        
        # Map common variations to enum values
        chat_type_lower = chat_type_str.lower().strip()
        
        if chat_type_lower in ["leadership", "admin"]:
            return ChatType.LEADERSHIP
        elif chat_type_lower in ["private", "direct", "dm"]:
            return ChatType.PRIVATE
        else:
            return ChatType.MAIN
            
    except Exception as e:
        logger.error(f"❌ Error normalizing chat_type '{chat_type}': {e}")
        return ChatType.MAIN


@tool("show_help_final")
async def show_help_final(
    chat_type: str,
    telegram_id: int,
    team_id: str, 
    username: str
) -> str:
    """
    Show final comprehensive help response with full context information.
    
    Args:
        chat_type: Chat type context
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        
    Returns:
        Formatted help text for direct display
    """
    # Delegate to main help response tool
    return await show_help_commands(telegram_id, team_id, username, chat_type)


@tool("show_help_usage")
async def show_help_usage(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    command: str = ""
) -> str:
    """
    Show detailed usage help for a specific command.
    
    This tool serves as the application boundary for command-specific help.
    It handles framework concerns and delegates to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)
        command: Specific command to get help for
        
    Returns:
        Formatted command help text for direct display
    """
    try:
        logger.info(f"🔧 Command help request from {username} for command: {command}")
        
        # For now, return specific command help or delegate to main help
        if command:
            return f"📚 **Command Help: {command}**\n\nFor detailed help with all commands, use `/help`.\n\nIf you need specific assistance with {command}, please contact team leadership."
        else:
            # No specific command, show general help
            return await show_help_commands(telegram_id, team_id, username, chat_type)
        
    except Exception as e:
        logger.error(f"❌ Error getting command help: {e}")
        return f"❌ Unable to retrieve command help. Please try '/help' for general assistance.\n\nError: {str(e)}"


@tool("show_help_welcome")
async def show_help_welcome(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Show welcome message for new users or first-time interactions.
    
    This tool serves as the application boundary for welcome message functionality.
    It handles framework concerns and delegates to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)
        
    Returns:
        Formatted welcome message text for direct display
    """
    try:
        logger.info(f"🔧 Welcome message request from {username}")
        
        # Get domain service
        help_service = HelpService()
        chat_type_enum = _normalize_chat_type(chat_type)
        
        # Generate personalized welcome message
        welcome_content = help_service.generate_welcome_message(username, chat_type_enum)
        
        logger.info(f"✅ Generated welcome message for {username}")
        
        # Return formatted welcome text directly
        return welcome_content
        
    except Exception as e:
        logger.error(f"❌ Error generating welcome message: {e}")
        return f"🎉 Welcome to KICKAI, {username}!\n\n👋 Use '/help' to get started and see available commands."


@tool("get_system_commands")
async def get_system_commands(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get a list of available system commands based on user context and permissions.
    
    This tool serves as the application boundary for command listing functionality.
    It handles framework concerns and delegates to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)
        
    Returns:
        Formatted available commands list for direct display
    """
    try:
        logger.info(f"🔧 Available commands request from {username}")
        
        # Use help service to generate command list
        help_service = HelpService()
        chat_type_enum = _normalize_chat_type(chat_type)
        
        # Generate help content and extract commands
        help_content = help_service.generate_help_content(chat_type_enum, username)
        
        # Format as simple command list
        commands_text = f"📋 **Available Commands ({chat_type} chat):**\n\n"
        
        for cmd in help_content.commands:
            commands_text += f"🔸 **{cmd.name}** - {cmd.description}\n"
            if cmd.examples:
                commands_text += f"   Example: `{cmd.examples[0]}`\n"
            commands_text += "\n"
        
        commands_text += f"\n💡 Use '/help' for detailed information about each command."
        
        logger.info(f"✅ Generated available commands list for {username}")
        
        return commands_text
        
    except Exception as e:
        logger.error(f"❌ Error getting available commands: {e}")
        return f"❌ Unable to retrieve available commands right now.\n\nPlease use '/help' for assistance.\n\nError: {str(e)}"