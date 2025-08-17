#!/usr/bin/env python3
"""
Communication Tools

This module provides tools for communication and messaging operations.
Converted to sync functions for CrewAI compatibility using asyncio.run() bridge pattern.
"""

import asyncio
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.core.enums import ChatType, ResponseStatus
from crewai.tools import tool
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    validate_required_input,
    create_json_response,
)
from kickai.utils.tool_validation import (
    validate_message_content,
    validate_team_id,
    validate_chat_type,
    validate_context_requirements,
    log_tool_execution,
)


@tool("send_message", result_as_answer=True)
async def send_message(telegram_id: int, team_id: str, username: str, chat_type: str, message: str) -> str:
    """
    Send a message to a specific chat using CrewAI native parameter passing.
    
    Args:
        telegram_id: Telegram ID of the user sending the message
        team_id: The team ID
        username: Username of the user sending the message
        chat_type: The chat type (main or leadership)
        message: The message to send

    Returns:
        JSON response with success or error message

    """
    try:
        # Validate inputs
        message = extract_single_value(message, "message")
        message = validate_message_content(message)
        chat_type = validate_chat_type(chat_type)
        team_id = validate_team_id(team_id)
        
        # Convert validated string to ChatType enum
        chat_type_enum = ChatType(chat_type)
        
        # Prepare inputs for logging
        inputs = {'message': message, 'chat_type': chat_type, 'chat_type_enum': chat_type_enum.value, 'team_id': team_id}
        
        # Get services from container
        container = get_container()
        communication_service = container.get_service("CommunicationService")

        if not communication_service:
            return create_json_response(ResponseStatus.ERROR, message="CommunicationService is not available")

        # Send message using native async
        success = await communication_service.send_message(message, chat_type_enum, team_id)

        if not success:
            return create_json_response(ResponseStatus.ERROR, message="Failed to send message")

        log_tool_execution("send_message", inputs, True)
        return create_json_response(
            "success", 
            data={
                "message": "Message sent successfully",
                "chat_type": chat_type,
                "chat_type_enum": chat_type_enum.value,
                "team_id": team_id,
                "message_length": len(message)
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in send_message tool: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to send message")


@tool("send_announcement", result_as_answer=True)
async def send_announcement(telegram_id: int, team_id: str, username: str, chat_type: str, announcement: str) -> str:
    """
    Send an announcement to all team members.

    Args:
        telegram_id: Telegram ID of the user sending the announcement
        team_id: Team ID (required)
        username: Username of the user sending the announcement
        chat_type: Chat type context
        announcement: The announcement message

    Returns:
        JSON response with success or error message
    """
    try:
        # Handle JSON string input and validate
        announcement = extract_single_value(announcement, "announcement")
        team_id = extract_single_value(team_id, "team_id")
        
        # Validate inputs
        announcement = validate_message_content(announcement, max_length=4096)
        team_id = validate_team_id(team_id)
        
        # Prepare inputs for logging
        inputs = {'announcement': announcement, 'team_id': team_id}
        
        # Get services from container
        container = get_container()
        communication_service = container.get_service("CommunicationService")

        if not communication_service:
            return create_json_response(ResponseStatus.ERROR, message="CommunicationService is not available")

        # Send announcement using native async
        success = await communication_service.send_announcement(announcement, team_id)

        if not success:
            return create_json_response(ResponseStatus.ERROR, message="Failed to send announcement")

        log_tool_execution("send_announcement", inputs, True)
        return create_json_response(ResponseStatus.SUCCESS, data="Announcement sent successfully")

    except Exception as e:
        logger.error(f"❌ Error in send_announcement tool: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to send announcement")


@tool("send_poll", result_as_answer=True)
async def send_poll(telegram_id: int, team_id: str, username: str, chat_type: str, question: str, options: str) -> str:
    """
    Send a poll to team members.

    Args:
        telegram_id: Telegram ID of the user sending the poll
        team_id: Team ID (required)
        username: Username of the user sending the poll
        chat_type: Chat type context
        question: The poll question
        options: Comma-separated poll options

    Returns:
        JSON response with success or error message
    """
    try:
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
        
        # Prepare inputs for logging
        inputs = {'question': question, 'options': option_list, 'team_id': team_id}
        
        # Get services from container
        container = get_container()
        communication_service = container.get_service("CommunicationService")

        if not communication_service:
            return create_json_response(ResponseStatus.ERROR, message="CommunicationService is not available")

        # Send poll using native async
        success = await communication_service.send_poll(question, option_list, team_id)

        if not success:
            return create_json_response(ResponseStatus.ERROR, message="Failed to send poll")

        log_tool_execution("send_poll", inputs, True)
        return create_json_response(ResponseStatus.SUCCESS, data="Poll sent successfully")

    except Exception as e:
        logger.error(f"❌ Error in send_poll tool: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to send poll")