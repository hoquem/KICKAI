"""
Communication tools for KICKAI system.

This module provides tools for sending messages, announcements, and polls
to Telegram chats.
"""

import logging

from crewai.tools import tool
from pydantic import BaseModel

from src.core.context_types import StandardizedContext

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
def send_message(context: dict, text: str) -> str:
    """
    Send a message to a Telegram chat. Requires: context and text
    
    Args:
        context: Dictionary containing chat information (will be converted to StandardizedContext)
        text: The message text to send
    
    Returns:
        Confirmation message indicating success or failure
    """
    try:
        logger.info(f"🔧 send_message tool called with context keys: {list(context.keys()) if isinstance(context, dict) else 'not a dict'}")
        logger.info(f"🔧 send_message tool called with text: {text[:50]}...")
        
        # Convert dictionary to StandardizedContext with validation
        if isinstance(context, dict):
            # Validate that critical fields are present
            required_fields = ['user_id', 'team_id', 'chat_id', 'chat_type', 'message_text', 'username', 'is_registered', 'is_player', 'is_team_member']
            missing_fields = [field for field in required_fields if field not in context or context[field] is None]
            
            if missing_fields:
                # Try to provide a more helpful error message
                if 'chat_id' in missing_fields:
                    logger.error(f"❌ send_message: Missing chat_id in context. Available fields: {list(context.keys())}")
                    return f"❌ Error: Missing required field 'chat_id' in context. Cannot send message without knowing which chat to send to. Available context fields: {list(context.keys())}"
                else:
                    logger.error(f"❌ send_message: Missing required fields: {missing_fields}")
                    return f"❌ Error: Missing required context fields: {missing_fields}. Cannot send message without proper context."
            
            try:
                standardized_context = StandardizedContext.from_dict(context)
                logger.info(f"✅ send_message: Successfully created StandardizedContext with chat_id: {standardized_context.chat_id}")
            except ValueError as e:
                logger.error(f"❌ send_message: StandardizedContext validation failed: {e}")
                return f"❌ Error: Invalid context data - {str(e)}"
        else:
            logger.warning(f"⚠️ send_message: Context is not a dict, type: {type(context)}")
            standardized_context = context

        chat_id = standardized_context.chat_id
        team_id = standardized_context.team_id

        # For now, return a success message since we can't access the Telegram service directly
        # The actual message sending will be handled by the orchestration pipeline
        logger.info(f"✅ Message prepared for chat {chat_id} (team: {team_id}): {text[:50]}...")
        return f"✅ Message prepared for chat {chat_id}: {text}"

    except Exception as e:
        logger.error(f"❌ Failed to prepare message for chat {context.get('chat_id', 'unknown') if isinstance(context, dict) else 'unknown'}: {e}")
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
