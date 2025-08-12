#!/usr/bin/env python3
"""
Communication Tools - Native CrewAI Implementation

This module provides tools for communication operations using ONLY CrewAI native patterns.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.communication.domain.services.communication_service import CommunicationService


@tool("send_message")
def send_message(telegram_id: int, team_id: str, chat_type: str, message: str) -> str:
    """
    Send a message to the team.

    :param telegram_id: Telegram ID of the user making the request
    :type telegram_id: int
    :param team_id: Team identifier for context and data isolation
    :type team_id: str
    :param chat_type: Chat context (main, leadership, private)
    :type chat_type: str
    :param message: Message content to send to team members
    :type message: str
    :return: Message delivery status with confirmation and message details
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to send a message."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to send a message."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to send a message."

    if not message or message.strip() == "":
        return "❌ Message content is required to send a message."

    try:
        # Get service using simple container access
        container = get_container()
        communication_service = container.get_service(CommunicationService)

        if not communication_service:
            return "❌ Communication service is temporarily unavailable. Please try again later."

        # Send message
        success = communication_service.send_message_sync(message.strip(), team_id.strip())

        if success:
            result = "✅ Message Sent Successfully\\n\\n"
            result += f"• Team: {team_id}\\n"
            result += f"• Message Length: {len(message.strip())} characters\\n\\n"
            result += "📢 Your message has been delivered to the team."
            return result
        else:
            return "❌ Failed to send message. Please check your connection and try again."

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return f"❌ Failed to send message: {e!s}"


@tool("send_announcement")
def send_announcement(telegram_id: int, team_id: str, chat_type: str, announcement: str) -> str:
    """
    Send an announcement to the team.

    :param telegram_id: Telegram ID of the user making the request
    :type telegram_id: int
    :param team_id: Team identifier for context and data isolation
    :type team_id: str
    :param chat_type: Chat context (main, leadership, private)
    :type chat_type: str
    :param announcement: Important announcement content to broadcast
    :type announcement: str
    :return: Announcement broadcast status with delivery confirmation to all team members
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to send an announcement."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to send an announcement."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to send an announcement."

    if not announcement or announcement.strip() == "":
        return "❌ Announcement content is required to send an announcement."

    try:
        # Get service using simple container access
        container = get_container()
        communication_service = container.get_service(CommunicationService)

        if not communication_service:
            return "❌ Communication service is temporarily unavailable. Please try again later."

        # Send announcement
        success = communication_service.send_announcement_sync(announcement.strip(), team_id.strip())

        if success:
            result = "📢 Announcement Sent Successfully\\n\\n"
            result += f"• Team: {team_id}\\n"
            result += f"• Announcement Length: {len(announcement.strip())} characters\\n\\n"
            result += "🔊 Your announcement has been broadcast to all team members."
            return result
        else:
            return "❌ Failed to send announcement. Please check your connection and try again."

    except Exception as e:
        logger.error(f"Failed to send announcement: {e}")
        return f"❌ Failed to send announcement: {e!s}"


@tool("send_poll")
def send_poll(telegram_id: int, team_id: str, chat_type: str, question: str, options: str) -> str:
    """
    Send a poll to the team.

    :param telegram_id: Telegram ID of the user making the request
    :type telegram_id: int
    :param team_id: Team identifier for context and data isolation
    :type team_id: str
    :param chat_type: Chat context (main, leadership, private)
    :type chat_type: str
    :param question: Poll question to ask team members
    :type question: str
    :param options: Comma-separated list of poll options (minimum 2 required)
    :type options: str
    :return: Poll creation status with voting instructions and option details
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to send a poll."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to send a poll."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to send a poll."

    if not question or question.strip() == "":
        return "❌ Poll question is required to send a poll."

    if not options or options.strip() == "":
        return "❌ Poll options are required to send a poll."

    try:
        # Parse options from comma-separated string
        option_list = [opt.strip() for opt in options.split(",") if opt.strip()]

        if len(option_list) < 2:
            return "❌ At least 2 poll options are required. Please provide comma-separated options."

        # Get service using simple container access
        container = get_container()
        communication_service = container.get_service(CommunicationService)

        if not communication_service:
            return "❌ Communication service is temporarily unavailable. Please try again later."

        # Send poll
        success = communication_service.send_poll_sync(question.strip(), option_list, team_id.strip())

        if success:
            result = "🗳️ Poll Sent Successfully\\n\\n"
            result += f"• Team: {team_id}\\n"
            result += f"• Question: {question.strip()}\\n"
            result += f"• Options: {len(option_list)} choices\\n"
            result += f"  - {', '.join(option_list)}\\n\\n"
            result += "📊 Team members can now vote on your poll."
            return result
        else:
            return "❌ Failed to send poll. Please check your connection and try again."

    except Exception as e:
        logger.error(f"Failed to send poll: {e}")
        return f"❌ Failed to send poll: {e!s}"
