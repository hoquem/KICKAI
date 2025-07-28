#!/usr/bin/env python3
"""
Communication Tools

This module provides tools for communication and messaging operations.
"""

from kickai.utils.crewai_tool_decorator import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    format_tool_success,
    validate_required_input,
)


@tool("send_message")
async def send_message(message: str, chat_type: str, team_id: str) -> str:
    """
    Send a message to a specific chat. Requires: message, chat_type, team_id

    Args:
        message: The message to send
        chat_type: The chat type (main_chat, leadership_chat)
        team_id: Team ID (required)

    Returns:
        Success or error message
    """
    try:
        # Handle JSON string input using utility functions
        message = extract_single_value(message, "message")
        chat_type = extract_single_value(chat_type, "chat_type")
        team_id = extract_single_value(team_id, "team_id")

        # Validate inputs using utility functions
        validation_error = validate_required_input(message, "Message")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(chat_type, "Chat Type")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Get services from container
        container = get_container()
        communication_service = container.get_service("CommunicationService")

        if not communication_service:
            raise ServiceNotAvailableError("CommunicationService")

        # Send message
        success = await communication_service.send_message(message, chat_type, team_id)

        if success:
            return format_tool_success("Message sent successfully")
        else:
            return format_tool_error("Failed to send message")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in send_message: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}", exc_info=True)
        return format_tool_error(f"Failed to send message: {e}")


@tool("send_announcement")
async def send_announcement(announcement: str, team_id: str) -> str:
    """
    Send an announcement to all team members. Requires: announcement, team_id

    Args:
        announcement: The announcement message
        team_id: Team ID (required)

    Returns:
        Success or error message
    """
    try:
        # Handle JSON string input using utility functions
        announcement = extract_single_value(announcement, "announcement")
        team_id = extract_single_value(team_id, "team_id")

        # Validate inputs using utility functions
        validation_error = validate_required_input(announcement, "Announcement")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Get services from container
        container = get_container()
        communication_service = container.get_service("CommunicationService")

        if not communication_service:
            raise ServiceNotAvailableError("CommunicationService")

        # Send announcement
        success = await communication_service.send_announcement(announcement, team_id)

        if success:
            return format_tool_success("Announcement sent successfully")
        else:
            return format_tool_error("Failed to send announcement")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in send_announcement: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to send announcement: {e}", exc_info=True)
        return format_tool_error(f"Failed to send announcement: {e}")


@tool("send_poll")
async def send_poll(question: str, options: str, team_id: str) -> str:
    """
    Send a poll to team members. Requires: question, options, team_id

    Args:
        question: The poll question
        options: Comma-separated poll options
        team_id: Team ID (required)

    Returns:
        Success or error message
    """
    try:
        # Handle JSON string input using utility functions
        question = extract_single_value(question, "question")
        options = extract_single_value(options, "options")
        team_id = extract_single_value(team_id, "team_id")

        # Validate inputs using utility functions
        validation_error = validate_required_input(question, "Question")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(options, "Options")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Get services from container
        container = get_container()
        communication_service = container.get_service("CommunicationService")

        if not communication_service:
            raise ServiceNotAvailableError("CommunicationService")

        # Parse options
        option_list = [opt.strip() for opt in options.split(",") if opt.strip()]

        # Send poll
        success = await communication_service.send_poll(question, option_list, team_id)

        if success:
            return format_tool_success("Poll sent successfully")
        else:
            return format_tool_error("Failed to send poll")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in send_poll: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to send poll: {e}", exc_info=True)
        return format_tool_error(f"Failed to send poll: {e}")
