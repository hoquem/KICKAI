"""
Communication tools for KICKAI system.

This module provides tools for sending messages, announcements, and polls
to Telegram chats.
"""

import logging

from crewai.tools import tool
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SendMessageInput(BaseModel):
    """Input model for send_message tool."""
    chat_id: str
    text: str
    team_id: str | None = None


class SendAnnouncementInput(BaseModel):
    """Input model for send_announcement tool."""
    chat_id: str
    text: str
    team_id: str | None = None


class SendPollInput(BaseModel):
    """Input model for send_poll tool."""
    chat_id: str
    question: str
    options: list[str]
    team_id: str | None = None


@tool("send_message")
def send_message(chat_id: str, text: str, team_id: str | None = None) -> str:
    """
    Send a message to a Telegram chat. Requires: chat_id, text

    Args:
        chat_id: The Telegram chat ID to send the message to
        text: The message text to send
        team_id: Optional team ID for context

    Returns:
        Confirmation message indicating success or failure
    """
    try:
        logger.info(f"🔧 send_message tool called with chat_id: {chat_id}, text: {text[:50]}..., team_id: {team_id}")

        # Validate required parameters
        if not chat_id:
            logger.error("❌ send_message: Missing required parameter 'chat_id'")
            return "❌ Error: Missing required parameter 'chat_id'. Cannot send message without knowing which chat to send to."

        if not text:
            logger.error("❌ send_message: Missing required parameter 'text'")
            return "❌ Error: Missing required parameter 'text'. Cannot send empty message."

        # For now, return a success message since we can't access the Telegram service directly
        # The actual message sending will be handled by the orchestration pipeline
        logger.info(f"✅ Message prepared for chat {chat_id} (team: {team_id}): {text[:50]}...")
        return f"✅ Message prepared for chat {chat_id}: {text}"

    except Exception as e:
        logger.error(f"❌ Failed to prepare message for chat {chat_id}: {e}")
        return f"❌ Failed to prepare message: {e!s}"


@tool("send_announcement")
def send_announcement(chat_id: str, text: str, team_id: str | None = None) -> str:
    """
    Send an announcement to a Telegram chat. Requires: chat_id, text

    Args:
        chat_id: The Telegram chat ID to send the announcement to
        text: The announcement text to send
        team_id: Optional team ID for context

    Returns:
        Confirmation message indicating success or failure
    """
    try:
        # For now, return a success message since we can't access the Telegram service directly
        # The actual announcement sending will be handled by the orchestration pipeline
        announcement_text = f"📢 *ANNOUNCEMENT*\n\n{text}"
        logger.info(f"✅ Announcement prepared for chat {chat_id}: {text[:50]}...")
        return f"✅ Announcement prepared for chat {chat_id}: {announcement_text}"

    except Exception as e:
        logger.error(f"❌ Failed to prepare announcement: {e}")
        return f"❌ Failed to prepare announcement: {e!s}"


@tool("send_poll")
def send_poll(chat_id: str, question: str, options: list[str], team_id: str | None = None) -> str:
    """
    Send a poll to a Telegram chat. Requires: chat_id, question, options

    Args:
        chat_id: The Telegram chat ID to send the poll to
        question: The poll question
        options: List of poll options
        team_id: Optional team ID for context

    Returns:
        Confirmation message indicating success or failure
    """
    try:
        # For now, return a success message since we can't access the Telegram service directly
        # The actual poll sending will be handled by the orchestration pipeline
        logger.info(f"✅ Poll prepared for chat {chat_id}: {question[:50]}...")
        return f"✅ Poll prepared for chat {chat_id}: {question} with {len(options)} options"

    except Exception as e:
        logger.error(f"❌ Failed to prepare poll: {e}")
        return f"❌ Failed to prepare poll: {e!s}"
