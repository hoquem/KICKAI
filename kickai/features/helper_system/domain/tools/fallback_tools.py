#!/usr/bin/env python3
"""
Command Fallback Tools

This module provides tools for handling unrecognized commands and providing helpful fallback responses.
"""

from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    format_tool_error,
    sanitize_input,
    validate_required_input,
)


class FinalHelpResponseInput(BaseModel):
    """Input model for FINAL_HELP_RESPONSE tool."""

    team_id: str
    user_id: str
    chat_type: str
    username: str


@tool("FINAL_HELP_RESPONSE")
def final_help_response(
    team_id: str, user_id: str, chat_type: str, username: str
) -> str:
    """
    Generate a final help response with context-aware command information.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        chat_type: Chat type (required) - "main_chat" or "leadership_chat"
        username: Username (required) - available from context

    Returns:
        Context-aware help response or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(chat_type, "Chat Type")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(username, "Username")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        chat_type = sanitize_input(chat_type, max_length=20)
        username = sanitize_input(username, max_length=50)

        # Get help service
        container = get_container()
        help_service = container.get_service("HelpService")

        if not help_service:
            return format_tool_error("Help service not available")

        # Generate help response
        success, message = help_service.generate_final_help_response_sync(
            team_id=team_id,
            user_id=user_id,
            chat_type=chat_type,
            username=username,
        )

        if success:
            return message
        else:
            return format_tool_error(f"Failed to generate help response: {message}")

    except Exception as e:
        logger.error(f"Failed to generate final help response: {e}", exc_info=True)
        return format_tool_error(f"Failed to generate help response: {e}")
