"""
Telegram-specific tools for KICKAI system.

This module provides tools for Telegram-specific operations.
"""

import logging

from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService
from crewai.tools import tool
from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response
from typing import Optional

logger = logging.getLogger(__name__)


class SendTelegramMessageInput(BaseModel):
    """Input model for send_telegram_message tool."""

    chat_id: str
    text: str
    team_id: Optional[str] = None


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def send_telegram_message(chat_id: str, text: str, team_id: Optional[str] = None) -> str:
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
            return create_json_response(ResponseStatus.ERROR, message=f"Telegram service not available")

        # Send the message (async)
        await telegram_service.send_message(chat_id, text)
        logger.info(f"✅ Telegram message sent to chat {chat_id}")
        return create_json_response(ResponseStatus.SUCCESS, data=f"Telegram message sent to chat {chat_id}")

    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to send Telegram message: {e!s}")
