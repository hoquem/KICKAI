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
from kickai.utils.tool_validation import create_tool_response


@tool("help_response", result_as_answer=True)
async def help_response(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Generate a comprehensive help response for users based on their chat type and context.

    This tool serves as the application boundary for help functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username  
        chat_type: Chat type (main/leadership/private)

    Returns:
        JSON formatted help response string
    """
    try:
        # Validate required parameters at application boundary
        if not all([chat_type, telegram_id, team_id, username]):
            return create_tool_response(
                False, 
                "Missing required parameters for help generation"
            )

        logger.info(
            f"🔧 Help request from user {username} ({telegram_id}) in {chat_type} chat for team {team_id}"
        )

        # Normalize chat type to enum
        chat_type_enum = _normalize_chat_type(chat_type)

        # Get domain service (pure business logic)
        help_service = HelpService()
        
        # Execute pure business logic
        help_content = help_service.generate_help_content(chat_type_enum, username)
        formatted_message = help_service.format_help_message(help_content)

        logger.info(f"✅ Generated help message for {username} in {chat_type} chat")
        
        return create_tool_response(
            True, 
            f"Help information for {username}",
            {"help_content": formatted_message}
        )

    except Exception as e:
        logger.error(f"❌ Error generating help response: {e}")
        return create_tool_response(
            False, 
            f"Failed to generate help response: {e}"
        )


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


@tool("FINAL_HELP_RESPONSE", result_as_answer=True)
async def FINAL_HELP_RESPONSE(
    chat_type: str,
    telegram_id: int,
    team_id: str, 
    username: str
) -> str:
    """
    Final help response tool - maintains compatibility with existing system.
    
    Args:
        chat_type: Chat type context
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        
    Returns:
        JSON formatted help response
    """
    # Delegate to main help response tool
    return await help_response(telegram_id, team_id, username, chat_type)


@tool("get_command_help", result_as_answer=True)
async def get_command_help(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    command: str = ""
) -> str:
    """
    Get detailed help for a specific command.
    
    This tool serves as the application boundary for command-specific help.
    It handles framework concerns and delegates to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)
        command: Specific command to get help for
        
    Returns:
        JSON formatted command help response
    """
    try:
        logger.info(f"🔧 Command help request from {username} for command: {command}")
        
        # Import and use the domain function directly
        from kickai.features.shared.domain.tools.help_tools import get_command_help as domain_get_command_help
        
        # Call the domain function
        result = await domain_get_command_help(telegram_id, team_id, username, chat_type, command)
        
        logger.info(f"✅ Generated command help for {username}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting command help: {e}")
        return create_tool_response(
            False,
            "Unable to retrieve command help. Please try '/help' for general assistance."
        )


@tool("get_welcome_message", result_as_answer=True)
async def get_welcome_message(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Generate a welcome message for new users or first-time interactions.
    
    This tool serves as the application boundary for welcome message functionality.
    It handles framework concerns and delegates to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)
        
    Returns:
        JSON formatted welcome message
    """
    try:
        logger.info(f"🔧 Welcome message request from {username}")
        
        # Get domain service
        help_service = HelpService()
        chat_type_enum = _normalize_chat_type(chat_type)
        
        # Generate personalized welcome message
        welcome_content = help_service.generate_welcome_message(username, chat_type_enum)
        
        logger.info(f"✅ Generated welcome message for {username}")
        
        return create_tool_response(
            True,
            f"Welcome message for {username}",
            {"welcome_content": welcome_content}
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating welcome message: {e}")
        return create_tool_response(
            False,
            "Welcome to KICKAI! Use '/help' to get started."
        )


@tool("get_available_commands", result_as_answer=True)
async def get_available_commands(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get a list of available commands based on user context and permissions.
    
    This tool serves as the application boundary for command listing functionality.
    It handles framework concerns and delegates to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type (main/leadership/private)
        
    Returns:
        JSON formatted available commands list
    """
    try:
        logger.info(f"🔧 Available commands request from {username}")
        
        # Import and use the domain function directly
        from kickai.features.shared.domain.tools.help_tools import get_available_commands as domain_get_available_commands
        
        # Call the domain function
        result = await domain_get_available_commands(telegram_id, team_id, username, chat_type)
        
        logger.info(f"✅ Generated available commands list for {username}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting available commands: {e}")
        return create_tool_response(
            False,
            "Unable to retrieve available commands. Use '/help' for assistance."
        )