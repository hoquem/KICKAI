#!/usr/bin/env python3
"""
Player Registration Command Handlers

This module provides command handlers for player registration operations.
These handlers delegate to the agent system for processing.
"""

import logging
from typing import Any, Dict

from kickai.core.command_registry import CommandResult
from kickai.core.context_manager import get_context
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.player_registration.domain.tools.player_tools import (
    add_player,
    approve_player,
    get_active_players,
    get_all_players,
    get_my_status,
    get_player_status,
)
from kickai.utils.tool_helpers import format_tool_error

logger = logging.getLogger(__name__)


async def handle_addplayer_command(update, context, **kwargs) -> CommandResult:
    """
    Handle /addplayer command.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional parameters
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Extract command parameters
        message_text = update.message.text
        parts = message_text.split()
        
        if len(parts) < 3:
            return CommandResult(
                success=False,
                message="❌ **Usage**: `/addplayer [name] [phone]`\n\n"
                "**Example**: `/addplayer John Smith +447123456789`\n\n"
                "💡 **Note**: Position can be set later by team members.",
                requires_agent=True
            )
        
        # Extract name and phone
        name = parts[1]
        phone = parts[2]
        
        # Get context information
        ctx = get_context()
        team_id = ctx.get("team_id", "")
        user_id = ctx.get("user_id", "")
        
        if not team_id:
            return CommandResult(
                success=False,
                message="❌ **Error**: Team ID not found in context. Please try again.",
                requires_agent=True
            )
        
        # Call the add_player tool
        result = add_player(
            team_id=team_id,
            user_id=user_id,
            name=name,
            phone=phone
        )
        
        return CommandResult(
            success=True,
            message=result,
            requires_agent=False
        )
        
    except Exception as e:
        logger.error(f"Error in handle_addplayer_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to add player: {str(e)}"),
            requires_agent=True
        )


async def handle_approve_command(update, context, **kwargs) -> CommandResult:
    """
    Handle /approve command.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional parameters
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Extract command parameters
        message_text = update.message.text
        parts = message_text.split()
        
        if len(parts) < 2:
            return CommandResult(
                success=False,
                message="❌ **Usage**: `/approve [player_id]`\n\n"
                "**Example**: `/approve MH123`\n\n"
                "💡 **Note**: This command is only available in the leadership chat.",
                requires_agent=True
            )
        
        # Extract player_id
        player_id = parts[1]
        
        # Get context information
        ctx = get_context()
        team_id = ctx.get("team_id", "")
        user_id = ctx.get("user_id", "")
        
        if not team_id:
            return CommandResult(
                success=False,
                message="❌ **Error**: Team ID not found in context. Please try again.",
                requires_agent=True
            )
        
        # Call the approve_player tool
        result = approve_player(
            team_id=team_id,
            user_id=user_id,
            player_id=player_id
        )
        
        return CommandResult(
            success=True,
            message=result,
            requires_agent=False
        )
        
    except Exception as e:
        logger.error(f"Error in handle_approve_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to approve player: {str(e)}"),
            requires_agent=True
        )


async def handle_reject_command(update, context, **kwargs) -> CommandResult:
    """
    Handle /reject command.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional parameters
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Extract command parameters
        message_text = update.message.text
        parts = message_text.split()
        
        if len(parts) < 2:
            return CommandResult(
                success=False,
                message="❌ **Usage**: `/reject [player_id] [reason]`\n\n"
                "**Example**: `/reject MH123 Insufficient experience`\n\n"
                "💡 **Note**: This command is only available in the leadership chat.",
                requires_agent=True
            )
        
        # Extract player_id and optional reason
        player_id = parts[1]
        reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason provided"
        
        # Get context information
        ctx = get_context()
        team_id = ctx.get("team_id", "")
        user_id = ctx.get("user_id", "")
        
        if not team_id:
            return CommandResult(
                success=False,
                message="❌ **Error**: Team ID not found in context. Please try again.",
                requires_agent=True
            )
        
        # For now, delegate to agent system for rejection logic
        return CommandResult(
            success=True,
            message=f"🔄 Processing rejection for player {player_id}...",
            requires_agent=True
        )
        
    except Exception as e:
        logger.error(f"Error in handle_reject_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to reject player: {str(e)}"),
            requires_agent=True
        )


async def handle_pending_command(update, context, **kwargs) -> CommandResult:
    """
    Handle /pending command.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional parameters
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Get context information
        ctx = get_context()
        team_id = ctx.get("team_id", "")
        user_id = ctx.get("user_id", "")
        
        if not team_id:
            return CommandResult(
                success=False,
                message="❌ **Error**: Team ID not found in context. Please try again.",
                requires_agent=True
            )
        
        # Call the get_all_players tool to get pending players
        result = get_all_players(
            team_id=team_id,
            user_id=user_id
        )
        
        return CommandResult(
            success=True,
            message=result,
            requires_agent=False
        )
        
    except Exception as e:
        logger.error(f"Error in handle_pending_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to get pending players: {str(e)}"),
            requires_agent=True
        )


async def handle_myinfo_command(update, context, **kwargs) -> CommandResult:
    """
    Handle /myinfo command.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional parameters
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Get context information
        ctx = get_context()
        team_id = ctx.get("team_id", "")
        user_id = ctx.get("user_id", "")
        chat_type = ctx.get("chat_type", "main_chat")
        
        if not team_id:
            return CommandResult(
                success=False,
                message="❌ **Error**: Team ID not found in context. Please try again.",
                requires_agent=True
            )
        
        # Call the get_my_status tool
        result = get_my_status(
            team_id=team_id,
            user_id=user_id,
            chat_type=chat_type
        )
        
        return CommandResult(
            success=True,
            message=result,
            requires_agent=False
        )
        
    except Exception as e:
        logger.error(f"Error in handle_myinfo_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to get player info: {str(e)}"),
            requires_agent=True
        )


async def handle_list_command(update, context, **kwargs) -> CommandResult:
    """
    Handle /list command.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional parameters
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Get context information
        ctx = get_context()
        team_id = ctx.get("team_id", "")
        user_id = ctx.get("user_id", "")
        chat_type = ctx.get("chat_type", "main_chat")
        
        if not team_id:
            return CommandResult(
                success=False,
                message="❌ **Error**: Team ID not found in context. Please try again.",
                requires_agent=True
            )
        
        # In main chat, show only active players
        # In leadership chat, show all players
        if chat_type == "main_chat":
            result = get_active_players(
                team_id=team_id,
                user_id=user_id
            )
        else:
            result = get_all_players(
                team_id=team_id,
                user_id=user_id
            )
        
        return CommandResult(
            success=True,
            message=result,
            requires_agent=False
        )
        
    except Exception as e:
        logger.error(f"Error in handle_list_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to get player list: {str(e)}"),
            requires_agent=True
        )


async def handle_status_command(update, context, **kwargs) -> CommandResult:
    """
    Handle /status command.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional parameters
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Extract command parameters
        message_text = update.message.text
        parts = message_text.split()
        
        if len(parts) < 2:
            return CommandResult(
                success=False,
                message="❌ **Usage**: `/status [phone]`\n\n"
                "**Example**: `/status +447123456789`\n\n"
                "💡 **Note**: Check the status of a player by phone number.",
                requires_agent=True
            )
        
        # Extract phone number
        phone = parts[1]
        
        # Get context information
        ctx = get_context()
        team_id = ctx.get("team_id", "")
        user_id = ctx.get("user_id", "")
        
        if not team_id:
            return CommandResult(
                success=False,
                message="❌ **Error**: Team ID not found in context. Please try again.",
                requires_agent=True
            )
        
        # Call the get_player_status tool
        result = get_player_status(
            team_id=team_id,
            user_id=user_id,
            phone=phone
        )
        
        return CommandResult(
            success=True,
            message=result,
            requires_agent=False
        )
        
    except Exception as e:
        logger.error(f"Error in handle_status_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to get player status: {str(e)}"),
            requires_agent=True
        ) 