#!/usr/bin/env python3
"""
Context Builder

Dedicated class for building execution contexts following the Single Responsibility Principle.
"""

from typing import Any

from loguru import logger

# Define the data class that was imported from user_flow_agent
from dataclasses import dataclass
from typing import Any

# Import centralized types
from kickai.core.types import TelegramMessage
from kickai.core.context_types import create_context_from_telegram_message
from kickai.core.enums import ChatType


class ContextBuilder:
    """Builds execution contexts for message processing."""

    def __init__(self, team_id: str):
        self.team_id = team_id

    async def build_execution_context(self, message: TelegramMessage, is_registered: bool,
                                    is_player: bool, is_team_member: bool) -> dict[str, Any]:
        """
        Build execution context for message processing.

        Args:
            message: Telegram message
            is_registered: Whether user is registered
            is_player: Whether user is a player
            is_team_member: Whether user is a team member

        Returns:
            Execution context dictionary
        """
        try:
            logger.info(f"🔧 ContextBuilder: Building context for {message.username}")

            # Create standardized context for CrewAI system
            standardized_context = create_context_from_telegram_message(
                user_id=message.user_id,
                team_id=message.team_id,
                chat_id=message.chat_id,
                chat_type=message.chat_type,
                message_text=message.text,
                username=message.username,
                telegram_name=message.username,  # Use username as telegram_name for now
                is_registered=is_registered,
                is_player=is_player,
                is_team_member=is_team_member,
            )

            # Convert to execution context for backward compatibility
            execution_context = standardized_context.to_dict()
            execution_context.update(
                {
                    "chat_type": message.chat_type.value,  # Add chat_type for simplified logic
                    "is_leadership_chat": message.chat_type == ChatType.LEADERSHIP,
                    "is_main_chat": message.chat_type == ChatType.MAIN,
                }
            )

            logger.info(f"🔧 ContextBuilder: Context built successfully for {message.username}")
            return execution_context

        except Exception as e:
            logger.error(f"❌ ContextBuilder: Error building context: {e}")
            # Return minimal context for error cases
            return {
                "user_id": message.user_id,
                "team_id": message.team_id,
                "chat_id": message.chat_id,
                "chat_type": message.chat_type.value,
                "message_text": message.text,
                "username": message.username,
                "is_registered": False,
                "is_player": False,
                "is_team_member": False,
                "is_leadership_chat": message.chat_type == ChatType.LEADERSHIP,
                "is_main_chat": message.chat_type == ChatType.MAIN,
            }

    def determine_user_status(self, message: TelegramMessage, is_player: bool,
                            is_team_member: bool) -> dict[str, bool]:
        """
        Determine user status based on chat type and registration status.

        Args:
            message: Telegram message
            is_player: Whether user is a player
            is_team_member: Whether user is a team member

        Returns:
            Dictionary with user status flags
        """
        try:
            # SIMPLIFIED LOGIC: Chat type determines user type
            if message.chat_type == ChatType.MAIN:
                # In main chat, treat as player
                is_registered = is_player
                is_team_member = False  # Force team member to False in main chat
                logger.info(
                    f"🔧 ContextBuilder: Main chat - treating as player, is_player={is_player}, is_registered={is_registered}"
                )
            elif message.chat_type == ChatType.LEADERSHIP:
                # In leadership chat, treat as team member
                is_registered = is_team_member
                is_player = False  # Force player to False in leadership chat
                logger.info(
                    f"🔧 ContextBuilder: Leadership chat - treating as team member, is_team_member={is_team_member}, is_registered={is_registered}"
                )
            else:
                # Unknown chat type, assume unregistered
                is_registered = False
                is_player = False
                is_team_member = False
                logger.warning(
                    f"⚠️ ContextBuilder: Unknown chat type {message.chat_type}, assuming unregistered"
                )

            return {
                "is_registered": is_registered,
                "is_player": is_player,
                "is_team_member": is_team_member
            }

        except Exception as e:
            logger.error(f"❌ ContextBuilder: Error determining user status: {e}")
            return {
                "is_registered": False,
                "is_player": False,
                "is_team_member": False
            }
