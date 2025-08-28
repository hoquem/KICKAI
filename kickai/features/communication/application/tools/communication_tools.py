#!/usr/bin/env python3
"""
Communication Tools - Clean Architecture Application Layer

This module provides CrewAI tools for communication functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.communication.domain.services.communication_service import CommunicationService
from kickai.utils.tool_helpers import create_json_response


@tool("send_message", result_as_answer=True)
async def send_message(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    target_chat: str = None
) -> str:
    """
    Send a message to a specific chat or broadcast to team.

    This tool serves as the application boundary for message sending functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Sender's Telegram ID
        team_id: Team ID (required)
        username: Sender's username for logging
        chat_type: Chat type context
        message: Message content to send
        target_chat: Target chat identifier (optional)

    Returns:
        JSON formatted response with message sending result
    """
    try:
        logger.info(f"📤 Message send request from {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not message or not message.strip():
            return create_json_response(
                ResponseStatus.ERROR,
                message="Message content is required"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        communication_service = container.get_service(CommunicationService)
        
        # Execute domain operation
        success = await communication_service.send_message(message, chat_type, team_id)
        
        if not success:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Failed to send message"
            )
        
        response_data = {
            "message_sent": True,
            "sender": username,
            "message_content": message[:100] + "..." if len(message) > 100 else message,
            "target_chat": chat_type,
            "team_id": team_id,
            "message": f"✅ Message sent successfully by {username}"
        }

        logger.info(f"✅ Message sent by {username}")
        return create_json_response(ResponseStatus.SUCCESS, data=response_data)

    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to send message: {e}")


@tool("send_announcement", result_as_answer=True)
async def send_announcement(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    announcement: str
) -> str:
    """
    Send an announcement to the team.

    This tool serves as the application boundary for announcement functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Sender's Telegram ID (admin/leadership)
        team_id: Team ID (required)
        username: Sender's username for logging
        chat_type: Chat type context (should be 'leadership')
        announcement: Announcement content

    Returns:
        JSON formatted response with announcement sending result
    """
    try:
        logger.info(f"📢 Announcement from {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not announcement or not announcement.strip():
            return create_json_response(
                ResponseStatus.ERROR,
                message="Announcement content is required"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        communication_service = container.get_service(CommunicationService)
        
        # Execute domain operation
        success = await communication_service.send_announcement(announcement, team_id)
        
        if not success:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Failed to send announcement"
            )
        
        response_data = {
            "announcement_sent": True,
            "sender": username,
            "announcement_content": announcement[:100] + "..." if len(announcement) > 100 else announcement,
            "team_id": team_id,
            "broadcast_to": "all_team_members",
            "message": f"📢 Announcement sent successfully by {username}"
        }

        logger.info(f"✅ Announcement sent by {username}")
        return create_json_response(ResponseStatus.SUCCESS, data=response_data)

    except Exception as e:
        logger.error(f"❌ Error sending announcement: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to send announcement: {e}")


@tool("send_poll", result_as_answer=True)
async def send_poll(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    poll_question: str,
    poll_options: str
) -> str:
    """
    Send a poll to the team for voting.

    This tool serves as the application boundary for poll functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Sender's Telegram ID (admin/leadership)
        team_id: Team ID (required)
        username: Sender's username for logging
        chat_type: Chat type context (should be 'leadership')
        poll_question: The poll question
        poll_options: Poll options (comma-separated)

    Returns:
        JSON formatted response with poll creation result
    """
    try:
        logger.info(f"🗳️ Poll creation request from {username} ({telegram_id}) in team {team_id}")

        # Validate inputs at application boundary
        if not poll_question or not poll_question.strip():
            return create_json_response(
                ResponseStatus.ERROR,
                message="Poll question is required"
            )
        
        if not poll_options or not poll_options.strip():
            return create_json_response(
                ResponseStatus.ERROR,
                message="Poll options are required"
            )

        # Parse poll options
        options_list = [opt.strip() for opt in poll_options.split(',') if opt.strip()]
        
        if len(options_list) < 2:
            return create_json_response(
                ResponseStatus.ERROR,
                message="At least 2 poll options are required"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        communication_service = container.get_service(CommunicationService)
        
        # Execute domain operation
        success = await communication_service.send_poll(poll_question, poll_options, team_id)
        
        if not success:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Failed to send poll"
            )
        
        response_data = {
            "poll_created": True,
            "sender": username,
            "poll_question": poll_question,
            "poll_options": options_list,
            "team_id": team_id,
            "voters": "all_team_members",
            "message": f"🗳️ Poll created successfully by {username}: {poll_question}"
        }

        logger.info(f"✅ Poll created by {username}")
        return create_json_response(ResponseStatus.SUCCESS, data=response_data)

    except Exception as e:
        logger.error(f"❌ Error creating poll: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to create poll: {e}")