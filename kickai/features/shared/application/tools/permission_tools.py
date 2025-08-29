#!/usr/bin/env python3
"""
Permission Tools - Clean Architecture Application Layer

This module provides CrewAI tools for permission handling and error messaging.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.features.shared.domain.tools.permission_tools import (
    permission_denied_message as domain_permission_denied_message,
    command_not_available as domain_command_not_available,
)
from kickai.utils.tool_validation import create_tool_response
from kickai.utils.tool_validation import create_tool_response


@tool("permission_denied_message", result_as_answer=True)
async def permission_denied_message(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    command_attempted: str,
    required_permission: str = "Unknown"
) -> str:
    """
    Generate a user-friendly permission denied message.
    
    This tool serves as the application boundary for permission denied messaging.
    It handles framework concerns and delegates business logic to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type where command was attempted
        command_attempted: The command that was denied
        required_permission: The permission level required
        
    Returns:
        JSON formatted user-friendly permission denied message
    """
    try:
        logger.info(f"🔧 [PERMISSION_TOOL] Processing permission denied for {username}, command: {command_attempted}")
        
        # Execute domain operation
        result = await domain_permission_denied_message(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            command_attempted=command_attempted,
            required_permission=required_permission
        )
        
        logger.info(f"✅ [PERMISSION_TOOL] Permission denied message generated for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [PERMISSION_TOOL] Error generating permission denied message: {e}")
        return create_tool_response(
            False,
            f"❌ Access denied for {command_attempted}. Contact team admin for support."
        )


@tool("command_not_available", result_as_answer=True)
async def command_not_available(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    command_attempted: str
) -> str:
    """
    Generate a message for commands that are not available in the current context.
    
    This tool serves as the application boundary for command not found messaging.
    It handles framework concerns and delegates business logic to the domain service.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team ID
        username: User's username
        chat_type: Chat type where command was attempted
        command_attempted: The command that was not found
        
    Returns:
        JSON formatted user-friendly command not available message
    """
    try:
        logger.info(f"🔧 [COMMAND_TOOL] Processing command not available for {username}, command: {command_attempted}")
        
        # Execute domain operation
        result = await domain_command_not_available(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            command_attempted=command_attempted
        )
        
        logger.info(f"✅ [COMMAND_TOOL] Command not available message generated for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [COMMAND_TOOL] Error generating command not available message: {e}")
        return create_tool_response(
            False,
            f"❓ Command {command_attempted} not found. Use /help for available commands."
        )