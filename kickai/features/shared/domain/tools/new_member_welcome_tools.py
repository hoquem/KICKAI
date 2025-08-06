#!/usr/bin/env python3
"""
New Member Welcome Tools

This module provides tools for generating welcome messages for new members joining the chat.
"""

from loguru import logger

from kickai.core.constants import normalize_chat_type
from kickai.core.welcome_message_templates import generate_welcome_message
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.security_utils import sanitize_username
from kickai.utils.tool_helpers import (
    format_tool_error,
    validate_required_input,
)


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

        # Sanitize username to prevent injection attacks
        safe_username = sanitize_username(username)

        # Normalize chat type
        chat_type_enum = normalize_chat_type(chat_type)

        # Generate welcome message using configurable templates
        try:
            welcome_message = generate_welcome_message(
                username=safe_username,
                chat_type=chat_type_enum,
                team_id=team_id,
                user_id=user_id
            )
            return welcome_message
        except Exception as template_error:
            logger.error(f"❌ Error generating welcome message with template: {template_error}")
            # Fallback to basic welcome message
            return f"""👋 Welcome to the team, {safe_username}!

🎉 We're excited to have you join our football community!

📋 **Getting Started:**
• Link your phone number to connect your account
• Use `/help` to see available commands
• Contact team leadership for assistance
• Check pinned messages for important updates

Welcome aboard! ⚽"""

    except Exception as e:
        logger.error(f"Error generating new member welcome message: {e}")
        return format_tool_error(f"Failed to generate welcome message: {e}")
