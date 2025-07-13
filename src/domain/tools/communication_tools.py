"""
Communication tools for the KICKAI system.

This module provides LangChain tools for communication operations.
"""

import logging
import asyncio
import traceback
from typing import Any, Optional, List, Type, Dict
from pydantic import BaseModel, Field
import requests
from datetime import datetime

from crewai.tools import BaseTool
from domain.interfaces.command_operations import ICommandOperations
from core.settings import get_settings

logger = logging.getLogger(__name__)


class SendMessageInput(BaseModel):
    """Input for sending a message."""
    message: str = Field(description="The message to send")
    team_id: str = Field(description="The team ID")
    chat_id: Optional[str] = Field(default=None, description="The chat ID to send the message to (optional, will use context if not provided)")


class SendPollInput(BaseModel):
    """Input for sending a poll."""
    question: str = Field(description="The poll question")
    options: List[str] = Field(description="The poll options")
    team_id: str = Field(description="The team ID")


class SendAnnouncementInput(BaseModel):
    """Input for sending an announcement."""
    announcement: str = Field(description="The announcement message")
    team_id: str = Field(description="The team ID")


class SendMessageTool(BaseTool):
    """Tool to send a message to a chat via Telegram."""
    
    name: str = Field(default="send_message", description="Tool name")
    description: str = Field(default="Send a message to a specific chat via Telegram. Use this to respond to users or send notifications.", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=SendMessageInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    
    def __init__(self, **data):
        super().__init__(**data)
        self._telegram_context = None
        self._bot_token = None
        self._initialize_telegram_config()
    
    def _initialize_telegram_config(self):
        """Initialize Telegram configuration."""
        try:
            settings = get_settings()
            self._bot_token = settings.telegram_bot_token
            if not self._bot_token:
                logger.warning("No Telegram bot token configured - send_message tool will be limited")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram config: {e}")
    
    def set_telegram_context(self, context: Any):
        """Set the Telegram context for sending messages."""
        self._telegram_context = context
        logger.debug("Telegram context set for SendMessageTool")
    
    def _run(self, message: str, team_id: str = None, chat_id: str = None, **kwargs) -> str:
        """Send a message synchronously."""
        try:
            # Look for chat_id and team_id in kwargs/context if not provided
            actual_chat_id = chat_id or kwargs.get('chat_id')
            actual_team_id = team_id or kwargs.get('team_id')
            if not actual_chat_id and self._telegram_context and hasattr(self._telegram_context, 'effective_chat'):
                actual_chat_id = str(self._telegram_context.effective_chat.id)
                logger.info(f"[SEND_MESSAGE] Using chat ID from Telegram context: {actual_chat_id}")
            elif not actual_chat_id:
                # Fallback to main chat ID from settings
                settings = get_settings()
                actual_chat_id = settings.telegram_main_chat_id
                logger.info(f"[SEND_MESSAGE] Using main chat ID from settings: {actual_chat_id}")
            if not actual_team_id:
                settings = get_settings()
                actual_team_id = settings.default_team_id
                logger.info(f"[SEND_MESSAGE] Using default team ID from settings: {actual_team_id}")
            if not actual_chat_id:
                logger.error("[SEND_MESSAGE] No chat ID available")
                return "❌ No chat ID available for sending message"
            logger.info(f"[SEND_MESSAGE] Attempting to send message to chat {actual_chat_id}")
            logger.info(f"[SEND_MESSAGE] Message preview: {message[:100]}...")
            logger.info(f"[SEND_MESSAGE] Team ID: {actual_team_id}")
            # Try multiple methods to send the message
            result = self._send_via_telegram_api(actual_chat_id, message)
            if result:
                logger.info(f"[SEND_MESSAGE] ✅ Message sent successfully to chat {actual_chat_id}")
                return f"✅ Message sent successfully to chat {actual_chat_id}"
            else:
                logger.warning(f"[SEND_MESSAGE] ⚠️ Message could not be sent via Telegram API")
                return f"⚠️ Message logged but could not be sent via Telegram API to chat {actual_chat_id}"
        except Exception as e:
            logger.error(f"[SEND_MESSAGE] ❌ Error sending message: {e}", exc_info=True)
            return f"❌ Error sending message: {str(e)}"

    async def _arun(self, message: str, team_id: str = None, chat_id: str = None, **kwargs) -> str:
        """Send a message asynchronously."""
        return self._run(message, team_id, chat_id, **kwargs)
    
    def _send_via_telegram_api(self, chat_id: str, message: str) -> bool:
        """Send message via Telegram Bot API."""
        try:
            if not self._bot_token:
                logger.warning("[SEND_MESSAGE] No bot token available for Telegram API")
                return False
            
            # Prepare the message for Telegram
            formatted_message = self._format_message_for_telegram(message)
            
            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": formatted_message,
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": True
            }
            
            logger.debug(f"[SEND_MESSAGE] Sending to Telegram API: {url}")
            logger.debug(f"[SEND_MESSAGE] Data: {data}")
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"[SEND_MESSAGE] ✅ Telegram API success: {result.get('result', {}).get('message_id', 'unknown')}")
                    return True
                else:
                    logger.error(f"[SEND_MESSAGE] ❌ Telegram API error: {result.get('description', 'unknown error')}")
                    return False
            else:
                logger.error(f"[SEND_MESSAGE] ❌ Telegram API HTTP error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("[SEND_MESSAGE] ❌ Telegram API timeout")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"[SEND_MESSAGE] ❌ Telegram API request error: {e}")
            return False
        except Exception as e:
            logger.error(f"[SEND_MESSAGE] ❌ Unexpected error in Telegram API: {e}", exc_info=True)
            return False
    
    def _format_message_for_telegram(self, message: str) -> str:
        """Format message for Telegram MarkdownV2."""
        try:
            # Escape special characters for MarkdownV2
            escaped_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            formatted_message = message
            
            for char in escaped_chars:
                formatted_message = formatted_message.replace(char, f'\\{char}')
            
            # Ensure message doesn't exceed Telegram limits
            if len(formatted_message) > 4096:
                formatted_message = formatted_message[:4093] + "..."
                logger.warning("[SEND_MESSAGE] Message truncated due to Telegram length limit")
            
            return formatted_message
            
        except Exception as e:
            logger.error(f"[SEND_MESSAGE] Error formatting message: {e}")
            # Return original message if formatting fails
            return message[:4096] if len(message) > 4096 else message
    
    def _validate_chat_id(self, chat_id: str) -> bool:
        """Validate chat ID format."""
        try:
            # Chat IDs should be numeric strings (can be negative for groups)
            if not chat_id.lstrip('-').isdigit():
                logger.warning(f"[SEND_MESSAGE] Invalid chat ID format: {chat_id}")
                return False
            return True
        except Exception as e:
            logger.error(f"[SEND_MESSAGE] Error validating chat ID: {e}")
            return False
    
    def _log_message_attempt(self, chat_id: str, message: str, team_id: str):
        """Log message sending attempt."""
        logger.info(f"[SEND_MESSAGE] 📤 Sending message to chat {chat_id} (team: {team_id})")
        logger.info(f"[SEND_MESSAGE] 📝 Message length: {len(message)} characters")
        logger.info(f"[SEND_MESSAGE] 📝 Message preview: {message[:100]}...")


class SendPollTool(BaseTool):
    """Tool to send a poll via Telegram."""
    
    name: str = Field(default="send_poll", description="Tool name")
    description: str = Field(default="Send a poll to the team chat via Telegram", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=SendPollInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    
    def __init__(self, **data):
        super().__init__(**data)
        self._bot_token = None
        self._initialize_telegram_config()
    
    def _initialize_telegram_config(self):
        """Initialize Telegram configuration."""
        try:
            settings = get_settings()
            self._bot_token = settings.telegram_bot_token
            if not self._bot_token:
                logger.warning("No Telegram bot token configured - send_poll tool will be limited")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram config: {e}")
    
    def _run(self, question: str, options: List[str], team_id: str) -> str:
        """Send a poll synchronously."""
        try:
            logger.info(f"[SEND_POLL] Attempting to send poll to team {team_id}")
            logger.info(f"[SEND_POLL] Question: {question}")
            logger.info(f"[SEND_POLL] Options: {options}")
            
            # Get the main chat ID for the team
            settings = get_settings()
            chat_id = settings.telegram_main_chat_id
            if not chat_id:
                logger.warning(f"[SEND_POLL] No main chat configured for team {team_id}")
                return f"⚠️ Poll logged but no main chat configured for team {team_id}"
            
            # Send poll via Telegram API
            success = self._send_poll_via_telegram_api(chat_id, question, options)
            
            if success:
                logger.info(f"[SEND_POLL] ✅ Poll sent successfully to team {team_id}")
                return f"✅ Poll sent successfully to team {team_id}"
            else:
                logger.warning(f"[SEND_POLL] ⚠️ Poll could not be sent via Telegram API")
                return f"⚠️ Poll logged but could not be sent via Telegram API to team {team_id}"
                
        except Exception as e:
            logger.error(f"[SEND_POLL] ❌ Error sending poll: {e}", exc_info=True)
            return f"❌ Error sending poll: {str(e)}"
    
    async def _arun(self, question: str, options: List[str], team_id: str) -> str:
        """Send a poll asynchronously."""
        return self._run(question, options, team_id)
    
    def _send_poll_via_telegram_api(self, chat_id: str, question: str, options: List[str]) -> bool:
        """Send poll via Telegram Bot API."""
        try:
            if not self._bot_token:
                logger.warning("[SEND_POLL] No bot token available for Telegram API")
                return False
            
            # Validate options
            if len(options) < 2:
                logger.error("[SEND_POLL] Poll must have at least 2 options")
                return False
            
            if len(options) > 10:
                logger.warning("[SEND_POLL] Poll has more than 10 options, truncating")
                options = options[:10]
            
            # Send poll via Telegram Bot API
            url = f"https://api.telegram.org/bot{self._bot_token}/sendPoll"
            data = {
                "chat_id": chat_id,
                "question": question,
                "options": options,
                "is_anonymous": False,
                "allows_multiple_answers": False
            }
            
            logger.debug(f"[SEND_POLL] Sending to Telegram API: {url}")
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"[SEND_POLL] ✅ Telegram API success: {result.get('result', {}).get('message_id', 'unknown')}")
                    return True
                else:
                    logger.error(f"[SEND_POLL] ❌ Telegram API error: {result.get('description', 'unknown error')}")
                    return False
            else:
                logger.error(f"[SEND_POLL] ❌ Telegram API HTTP error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"[SEND_POLL] ❌ Error in Telegram API: {e}", exc_info=True)
            return False


class SendAnnouncementTool(BaseTool):
    """Tool to send an announcement via Telegram."""
    
    name: str = Field(default="send_announcement", description="Tool name")
    description: str = Field(default="Send an announcement to the team chat via Telegram", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=SendAnnouncementInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    
    def __init__(self, **data):
        super().__init__(**data)
        self._bot_token = None
        self._initialize_telegram_config()
    
    def _initialize_telegram_config(self):
        """Initialize Telegram configuration."""
        try:
            settings = get_settings()
            self._bot_token = settings.telegram_bot_token
            if not self._bot_token:
                logger.warning("No Telegram bot token configured - send_announcement tool will be limited")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram config: {e}")
    
    def _run(self, announcement: str, team_id: str) -> str:
        """Send an announcement synchronously."""
        try:
            logger.info(f"[SEND_ANNOUNCEMENT] Attempting to send announcement to team {team_id}")
            logger.info(f"[SEND_ANNOUNCEMENT] Announcement: {announcement[:100]}...")
            
            # Get the main chat ID for the team
            settings = get_settings()
            chat_id = settings.telegram_main_chat_id
            if not chat_id:
                logger.warning(f"[SEND_ANNOUNCEMENT] No main chat configured for team {team_id}")
                return f"⚠️ Announcement logged but no main chat configured for team {team_id}"
            
            # Format announcement
            formatted_announcement = self._format_announcement(announcement, team_id)
            
            # Send announcement via Telegram API
            success = self._send_announcement_via_telegram_api(chat_id, formatted_announcement)
            
            if success:
                logger.info(f"[SEND_ANNOUNCEMENT] ✅ Announcement sent successfully to team {team_id}")
                return f"✅ Announcement sent successfully to team {team_id}"
            else:
                logger.warning(f"[SEND_ANNOUNCEMENT] ⚠️ Announcement could not be sent via Telegram API")
                return f"⚠️ Announcement logged but could not be sent via Telegram API to team {team_id}"
                
        except Exception as e:
            logger.error(f"[SEND_ANNOUNCEMENT] ❌ Error sending announcement: {e}", exc_info=True)
            return f"❌ Error sending announcement: {str(e)}"
    
    async def _arun(self, announcement: str, team_id: str) -> str:
        """Send an announcement asynchronously."""
        return self._run(announcement, team_id)
    
    def _format_announcement(self, announcement: str, team_id: str) -> str:
        """Format announcement for Telegram."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted = f"""📢 **TEAM ANNOUNCEMENT**

{announcement}

---
*Sent on {timestamp}*
*Team: {team_id}*"""
            
            return formatted
            
        except Exception as e:
            logger.error(f"[SEND_ANNOUNCEMENT] Error formatting announcement: {e}")
            return announcement
    
    def _send_announcement_via_telegram_api(self, chat_id: str, announcement: str) -> bool:
        """Send announcement via Telegram Bot API."""
        try:
            if not self._bot_token:
                logger.warning("[SEND_ANNOUNCEMENT] No bot token available for Telegram API")
                return False
            
            # Escape special characters for MarkdownV2
            escaped_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            formatted_announcement = announcement
            
            for char in escaped_chars:
                formatted_announcement = formatted_announcement.replace(char, f'\\{char}')
            
            # Ensure message doesn't exceed Telegram limits
            if len(formatted_announcement) > 4096:
                formatted_announcement = formatted_announcement[:4093] + "..."
                logger.warning("[SEND_ANNOUNCEMENT] Announcement truncated due to Telegram length limit")
            
            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": formatted_announcement,
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": True
            }
            
            logger.debug(f"[SEND_ANNOUNCEMENT] Sending to Telegram API: {url}")
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"[SEND_ANNOUNCEMENT] ✅ Telegram API success: {result.get('result', {}).get('message_id', 'unknown')}")
                    return True
                else:
                    logger.error(f"[SEND_ANNOUNCEMENT] ❌ Telegram API error: {result.get('description', 'unknown error')}")
                    return False
            else:
                logger.error(f"[SEND_ANNOUNCEMENT] ❌ Telegram API HTTP error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"[SEND_ANNOUNCEMENT] ❌ Error in Telegram API: {e}", exc_info=True)
            return False 