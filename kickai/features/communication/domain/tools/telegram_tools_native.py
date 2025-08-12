#!/usr/bin/env python3
"""
Telegram Tools - Native CrewAI Implementation

This module provides tools for Telegram-specific operations using ONLY CrewAI native patterns.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService


@tool("send_telegram_message")
def send_telegram_message(telegram_id: int, team_id: str, chat_type: str, chat_id: str, text: str) -> str:
    """
    Send a message to a specific Telegram chat.

    :param telegram_id: Telegram ID of the user making the request
    :type telegram_id: int
    :param team_id: Team identifier for context and data isolation
    :type team_id: str
    :param chat_type: Chat context (main, leadership, private)
    :type chat_type: str
    :param chat_id: Telegram chat ID to send message to
    :type chat_id: str
    :param text: Message text to send
    :type text: str
    :return: Message sending status
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to send Telegram message."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to send Telegram message."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to send Telegram message."

    if not chat_id or chat_id.strip() == "":
        return "❌ Chat ID is required to send Telegram message."

    if not text or text.strip() == "":
        return "❌ Message text is required to send Telegram message."

    try:
        # Get service using simple container access
        container = get_container()
        telegram_service = container.get_service(TelegramBotService)

        if not telegram_service:
            return "❌ Telegram service is temporarily unavailable. Please try again later."

        # Send message
        success = telegram_service.send_message_sync(chat_id.strip(), text.strip())

        if success:
            result = "✅ Telegram Message Sent Successfully!\\n\\n"
            result += f"• Chat ID: {chat_id}\\n"
            result += f"• Team: {team_id}\\n"
            result += f"• Message Length: {len(text.strip())} characters\\n\\n"
            result += "📱 Message delivered via Telegram."
            return result
        else:
            return "❌ Failed to send Telegram message. Please check the chat ID and try again."

    except Exception as e:
        logger.error(f"Failed to send Telegram message for team {team_id}: {e}")
        return f"❌ Failed to send Telegram message: {e!s}"
