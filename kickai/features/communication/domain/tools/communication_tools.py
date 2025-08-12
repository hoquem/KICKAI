#!/usr/bin/env python3
"""
Communication Tools

This module provides tools for communication and messaging operations.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    format_tool_success,
    validate_required_input,
    create_json_response,
)
from kickai.utils.tool_validation import (
    tool_error_handler,
    validate_message_content,
    validate_team_id,
    validate_chat_type,
    validate_context_requirements,
    log_tool_execution,
    ToolValidationError,
    ToolExecutionError,
)


@tool("send_message")
@tool_error_handler
def send_message(message: str, chat_type: str, team_id: str) -> str:
    """
    Send a message to a specific chat using CrewAI native parameter passing.

    Args:
        message: The message to send
        chat_type: The chat type (main or leadership)
        team_id: The team ID

    Returns:
        Success or error message
    """
    # Validate inputs
    message = extract_single_value(message, "message")
    message = validate_message_content(message)
    chat_type = validate_chat_type(chat_type)
    team_id = validate_team_id(team_id)
    
    # Log tool execution start
    inputs = {'message': message, 'chat_type': chat_type, 'team_id': team_id}
    log_tool_execution("send_message", inputs, True)
    
    # Get services from container
    container = get_container()
    communication_service = container.get_service("CommunicationService")

    if not communication_service:
        raise ToolExecutionError("CommunicationService is not available")

    # Send message using sync wrapper
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, communication_service.send_message(message, chat_type, team_id))
                success = future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            success = asyncio.run(communication_service.send_message(message, chat_type, team_id))
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        raise ToolExecutionError(f"Failed to send message: {e}")

    if success:
        return create_json_response("success", data="Message sent successfully")
    else:
        raise ToolExecutionError("Failed to send message")


@tool("send_announcement")
@tool_error_handler
def send_announcement(announcement: str, team_id: str) -> str:
    """
    Send an announcement to all team members. Requires: announcement, team_id

    Args:
        announcement: The announcement message
        team_id: Team ID (required)

    Returns:
        Success or error message
    """
    # Handle JSON string input and validate
    announcement = extract_single_value(announcement, "announcement")
    team_id = extract_single_value(team_id, "team_id")
    
    # Validate inputs
    announcement = validate_message_content(announcement, max_length=4096)
    team_id = validate_team_id(team_id)
    
    # Log tool execution start
    inputs = {'announcement': announcement, 'team_id': team_id}
    log_tool_execution("send_announcement", inputs, True)
    
    # Get services from container
    container = get_container()
    communication_service = container.get_service("CommunicationService")

    if not communication_service:
        raise ToolExecutionError("CommunicationService is not available")

    # Send announcement using sync wrapper
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, communication_service.send_announcement(announcement, team_id))
                success = future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            success = asyncio.run(communication_service.send_announcement(announcement, team_id))
    except Exception as e:
        logger.error(f"❌ Error sending announcement: {e}")
        raise ToolExecutionError(f"Failed to send announcement: {e}")

    if success:
        return create_json_response("success", data="Announcement sent successfully")
    else:
        raise ToolExecutionError("Failed to send announcement")


@tool("send_poll")
@tool_error_handler
def send_poll(question: str, options: str, team_id: str) -> str:
    """
    Send a poll to team members. Requires: question, options, team_id

    Args:
        question: The poll question
        options: Comma-separated poll options
        team_id: Team ID (required)

    Returns:
        Success or error message
    """
    # Handle JSON string input and validate
    question = extract_single_value(question, "question")
    options = extract_single_value(options, "options")
    team_id = extract_single_value(team_id, "team_id")
    
    # Validate inputs
    question = validate_message_content(question, max_length=1024)
    team_id = validate_team_id(team_id)
    
    # Validate and parse options
    from kickai.utils.tool_validation import validate_list
    option_list = validate_list(options, "Options", min_items=2, max_items=10)
    
    # Log tool execution start
    inputs = {'question': question, 'options': option_list, 'team_id': team_id}
    log_tool_execution("send_poll", inputs, True)
    
    # Get services from container
    container = get_container()
    communication_service = container.get_service("CommunicationService")

    if not communication_service:
        raise ToolExecutionError("CommunicationService is not available")

    # Send poll using sync wrapper
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, communication_service.send_poll(question, option_list, team_id))
                success = future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            success = asyncio.run(communication_service.send_poll(question, option_list, team_id))
    except Exception as e:
        logger.error(f"❌ Error sending poll: {e}")
        raise ToolExecutionError(f"Failed to send poll: {e}")

    if success:
        return create_json_response("success", data="Poll sent successfully")
    else:
        raise ToolExecutionError("Failed to send poll")
