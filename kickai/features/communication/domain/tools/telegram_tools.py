#!/usr/bin/env python3
"""
Telegram Tools

This module provides tools for Telegram-specific operations.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService
from kickai.utils.json_helper import json_error, json_response



@tool("send_telegram_message")
def send_telegram_message(chat_id: str, text: str, team_id: str) -> str:
    """
    Send a message to a specific Telegram chat.

    :param chat_id: Telegram chat ID to send message to
    :type chat_id: str
    :param text: Message text to send
    :type text: str
    :param team_id: Team ID (required) - available from context
    :type team_id: str
    :return: JSON response with message sending status
    :rtype: str
    """
    try:
        # Simple validation
        if not chat_id or not text or not team_id:
            return "❌ Chat ID, text, and team ID are required"

        # Get service
        container = get_container()
        telegram_service = container.get_service(TelegramBotService)

        if not telegram_service:
            return json_error(message="TelegramBotService is not available", error_type="Service unavailable")

        # Send message
        success = telegram_service.send_message_sync(chat_id, text)

        if success:
            data = {
                'chat_id': chat_id,
                'text': text,
                'team_id': team_id,
                'message_length': len(text),
                'status': 'message_sent'
            }

            ui_format = f"✅ **Message Sent Successfully!**\n\n📱 **Chat ID**: {chat_id}\n🏆 **Team ID**: {team_id}\n📝 **Message Length**: {len(text)} characters"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message="Failed to send Telegram message", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in send_telegram_message: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to send Telegram message for team {team_id}: {e}")
        return json_error(message=f"Failed to send Telegram message: {e!s}", error_type="Operation failed")
