#!/usr/bin/env python3
"""
Communication Tools

This module provides tools for communication and messaging operations.
"""

from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    format_tool_success,
    validate_required_input,
)
from kickai.utils.tool_validation import (
    tool_error_handler,
    validate_message_content,
    validate_team_id,
    validate_chat_type,
    validate_context_requirements,
    log_tool_execution,
    create_tool_response,
    ToolValidationError,
    ToolExecutionError,
)


@tool("send_message")
@tool_error_handler
async def send_message(message: str) -> str:
    """
    Send a message to a specific chat. The tool automatically accesses context from Task.config.

    Args:
        message: The message to send

    Returns:
        Success or error message
    """
    # Validate context requirements
    context = validate_context_requirements("send_message", ['chat_type', 'team_id'])
    
    # Extract and validate context values
    chat_type = validate_chat_type(context['chat_type'])
    team_id = validate_team_id(context['team_id'])
    
    # Handle JSON string input and validate message
    message = extract_single_value(message, "message")
    message = validate_message_content(message)
    
    # Log tool execution start
    inputs = {'message': message, 'chat_type': chat_type, 'team_id': team_id}
    log_tool_execution("send_message", inputs, True)
    
    # Get services from container
    container = get_container()
    communication_service = container.get_service("CommunicationService")

    if not communication_service:
        raise ToolExecutionError("CommunicationService is not available")

    # Send message
    success = await communication_service.send_message(message, chat_type, team_id)

    if success:
        return create_tool_response(True, "Message sent successfully")
    else:
        raise ToolExecutionError("Failed to send message")


@tool("send_announcement")
@tool_error_handler
async def send_announcement(announcement: str, team_id: str) -> str:
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

    # Send announcement
    success = await communication_service.send_announcement(announcement, team_id)

    if success:
        return create_tool_response(True, "Announcement sent successfully")
    else:
        raise ToolExecutionError("Failed to send announcement")


@tool("send_poll")
@tool_error_handler
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

    # Send poll
    success = await communication_service.send_poll(question, option_list, team_id)

    if success:
        return create_tool_response(True, "Poll sent successfully")
    else:
        raise ToolExecutionError("Failed to send poll")
