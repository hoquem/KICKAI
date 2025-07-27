"""
Telegram-specific tools for KICKAI system.

This module provides tools for Telegram-specific operations.
"""

import logging

from crewai.tools import tool
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService

logger = logging.getLogger(__name__)


class SendTelegramMessageInput(BaseModel):
    """Input model for send_telegram_message tool."""

    chat_id: str
    text: str
    team_id: str | None = None


@tool("send_telegram_message")
def send_telegram_message(chat_id: str, text: str, team_id: str | None = None) -> str:
    """
    Send a message to a Telegram chat using the Telegram bot service. Requires: chat_id, text

    Args:
        chat_id: The Telegram chat ID to send the message to
        text: The message text to send
        team_id: Optional team ID for context

    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        telegram_service = container.get_service(TelegramBotService)

        if not telegram_service:
            logger.error("❌ TelegramBotService not available")
            return "❌ Telegram service not available"

        # Send the message
        telegram_service.send_message(chat_id, text)
        logger.info(f"✅ Telegram message sent to chat {chat_id}")
        return f"✅ Telegram message sent to chat {chat_id}"

    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message: {e}")
        return f"❌ Failed to send Telegram message: {e!s}"
