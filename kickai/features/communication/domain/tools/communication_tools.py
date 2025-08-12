#!/usr/bin/env python3
"""
Communication Tools

This module provides tools for communication operations.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.communication.domain.services.communication_service import CommunicationService
from kickai.utils.json_helper import json_error, json_response



@tool("send_message")
def send_message(message: str, team_id: str) -> str:
    """
    Send a message to the team.

    :param message: Message content to send
    :type message: str
    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :return: JSON response with message sending status
    :rtype: str
    """
    try:
        # Simple validation
        if not message or not team_id:
            return "❌ Message and team ID are required"

        # Get service
        container = get_container()
        communication_service = container.get_service(CommunicationService)

        if not communication_service:
            return json_error(message="CommunicationService is not available", error_type="Service unavailable")

        # Send message
        success = communication_service.send_message_sync(message, team_id)

        if success:
            data = {
                'message': message,
                'team_id': team_id,
                'status': 'message_sent'
            }

            return json_response(data=data, ui_format="✅ Message sent successfully")
        else:
            return json_error(message="Failed to send message", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in send_message: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return json_error(message=f"Failed to send message: {e}", error_type="Operation failed")

@tool("send_announcement")
def send_announcement(announcement: str, team_id: str) -> str:
    """
    Send an announcement to the team.

    :param announcement: Announcement content to send
    :type announcement: str
    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :return: JSON response with announcement sending status
    :rtype: str
    """
    try:
        # Simple validation
        if not announcement or not team_id:
            return "❌ Announcement and team ID are required"

        # Get service
        container = get_container()
        communication_service = container.get_service(CommunicationService)

        if not communication_service:
            return json_error(message="CommunicationService is not available", error_type="Service unavailable")

        # Send announcement
        success = communication_service.send_announcement_sync(announcement, team_id)

        if success:
            data = {
                'announcement': announcement,
                'team_id': team_id,
                'status': 'announcement_sent'
            }

            return json_response(data=data, ui_format="✅ Announcement sent successfully")
        else:
            return json_error(message="Failed to send announcement", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in send_announcement: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to send announcement: {e}")
        return json_error(message=f"Failed to send announcement: {e}", error_type="Operation failed")

@tool("send_poll")
def send_poll(question: str, options: list, team_id: str) -> str:
    """
    Send a poll to the team.

    :param question: Poll question
    :type question: str
    :param options: List of poll options
    :type options: list
    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :return: JSON response with poll sending status
    :rtype: str
    """
    try:
        # Simple validation
        if not question or not team_id:
            return "❌ Question and team ID are required"

        if not options or not isinstance(options, list) or len(options) < 2:
            return "❌ At least 2 poll options are required"

        # Get service
        container = get_container()
        communication_service = container.get_service(CommunicationService)

        if not communication_service:
            return json_error(message="CommunicationService is not available", error_type="Service unavailable")

        # Send poll
        success = communication_service.send_poll_sync(question, options, team_id)

        if success:
            data = {
                'question': question,
                'options': options,
                'team_id': team_id,
                'status': 'poll_sent'
            }

            return json_response(data=data, ui_format="✅ Poll sent successfully")
        else:
            return json_error(message="Failed to send poll", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in send_poll: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to send poll: {e}")
        return json_error(message=f"Failed to send poll: {e}", error_type="Operation failed")
