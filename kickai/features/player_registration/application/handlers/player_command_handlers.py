#!/usr/bin/env python3
"""
Player Command Handlers

This module provides command handlers for player-related commands.
"""

import logging
from typing import Any, Dict, Optional

from loguru import logger

from kickai.core.context_types import get_context
from kickai.core.enums import ResponseStatus
from kickai.features.player_registration.application.commands.command_result import CommandResult
from kickai.features.player_registration.domain.tools.player_tools import (
    get_active_players,
    get_all_players,
    get_my_status,
)
from kickai.utils.tool_helpers import format_tool_error


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
                message="❌ Error: Team ID not found in context. Please try again.",
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
            message=format_tool_error(f"Failed to get player info: {e!s}"),
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
                message="❌ Error: Team ID not found in context. Please try again.",
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
            message=format_tool_error(f"Failed to get player list: {e!s}"),
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
                message="❌ Usage: /status [phone]\n\n"
                "Example: /status +447123456789\n\n"
                "💡 Note: Check the status of a player by phone number.\n\n"
                "🔧 Note: This command is now handled by the agent system for better accuracy.",
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
                message="❌ Error: Team ID not found in context. Please try again.",
                requires_agent=True
            )

        # Since we removed get_player_status tool, route this to the agent system
        # The agent will use get_all_players and filter by phone number
        return CommandResult(
            success=True,
            message=f"🔍 Searching for player with phone: {phone}\n\n"
                   f"📋 This request is being processed by the agent system for accurate results.",
            requires_agent=True
        )

    except Exception as e:
        logger.error(f"Error in handle_status_command: {e}")
        return CommandResult(
            success=False,
            message=format_tool_error(f"Failed to get player status: {e!s}"),
            requires_agent=True
        )
