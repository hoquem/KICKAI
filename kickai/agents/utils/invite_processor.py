#!/usr/bin/env python3
"""
Invite processing utilities.

Handles invite link validation and processing for the KICKAI system.
"""

from typing import Any, Optional
from loguru import logger

from kickai.agents.config.message_router_config import (
    ERROR_MESSAGES,
    WARNING_MESSAGES,
    LOG_MESSAGES,
)


class InviteProcessor:
    """
    Handles invite link processing and validation.
    
    Extracts new members and invite context from raw Telegram updates.
    """

    @staticmethod
    def is_new_chat_members_event(raw_update: Any) -> bool:
        """
        Check if the update is a new chat members event.

        Args:
            raw_update: Raw Telegram update object

        Returns:
            True if this is a new chat members event, False otherwise
        """
        try:
            # ALL business logic here
            return (
                hasattr(raw_update, "message")
                and raw_update.message
                and hasattr(raw_update.message, "new_chat_members")
                and raw_update.message.new_chat_members
            )
            
        except Exception as e:
            logger.error(f"❌ Error in is_new_chat_members_event: {e}")
            return False

    @staticmethod
    def extract_new_members(raw_update: Any) -> list:
        """
        Extract new members from the update.

        Args:
            raw_update: Raw Telegram update object

        Returns:
            List of new chat members
        """
        try:
            # ALL business logic here
            if not InviteProcessor.is_new_chat_members_event(raw_update):
                return []

            return raw_update.message.new_chat_members
            
        except Exception as e:
            logger.error(f"❌ Error in extract_new_members: {e}")
            return []

    @staticmethod
    def extract_invite_context(raw_update: Any) -> Optional[dict]:
        """
        Extract invite context from the update.

        Args:
            raw_update: Raw Telegram update object

        Returns:
            Dictionary with invite context or None if not available
        """
        try:
            # ALL business logic here
            if not InviteProcessor.is_new_chat_members_event(raw_update):
                return None

            message = raw_update.message
            context = {}

            # Extract chat information
            if hasattr(message, "chat") and message.chat:
                context["chat_id"] = getattr(message.chat, "id", None)
                context["chat_type"] = getattr(message.chat, "type", None)
                context["chat_title"] = getattr(message.chat, "title", None)

            # Extract from_user information (who sent the invite)
            if hasattr(message, "from_user") and message.from_user:
                context["from_user_id"] = getattr(message.from_user, "id", None)
                context["from_username"] = getattr(message.from_user, "username", None)

            # Extract invite link information
            if hasattr(message, "invite_link") and message.invite_link:
                context["invite_link"] = getattr(message.invite_link, "invite_link", None)
                context["invite_link_creator"] = getattr(message.invite_link, "creator", None)

            return context if context else None
            
        except Exception as e:
            logger.error(f"❌ Error in extract_invite_context: {e}")
            return None

    @staticmethod
    def validate_invite_link(invite_link: str) -> tuple[bool, Optional[str]]:
        """
        Validate an invite link format.

        Args:
            invite_link: The invite link to validate

        Returns:
            Tuple of (is_valid, error_message_or_none)
        """
        try:
            # ALL business logic here
            if not invite_link or not isinstance(invite_link, str):
                return False, "Invalid invite link format"

            # Basic Telegram invite link validation
            if not invite_link.startswith("https://t.me/joinchat/"):
                return False, "Invalid Telegram invite link format"

            # Check minimum length
            if len(invite_link) < 30:
                return False, "Invite link too short"

            # Check for valid characters
            valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
            invite_code = invite_link.split("/")[-1]
            if not all(c in valid_chars for c in invite_code):
                return False, "Invalid characters in invite link"

            return True, None
            
        except Exception as e:
            logger.error(f"❌ Error in validate_invite_link: {e}")
            return False, "Invite link validation failed"

    @staticmethod
    def process_invite_event(raw_update: Any) -> Optional[dict]:
        """
        Process a complete invite event from raw update.

        Args:
            raw_update: Raw Telegram update object

        Returns:
            Dictionary with processed invite information or None if invalid
        """
        try:
            # ALL business logic here
            if not InviteProcessor.is_new_chat_members_event(raw_update):
                return None

            # Extract new members
            new_members = InviteProcessor.extract_new_members(raw_update)
            if not new_members:
                logger.warning(WARNING_MESSAGES["NO_NEW_MEMBERS_FOUND"])
                return None

            # Extract context
            context = InviteProcessor.extract_invite_context(raw_update)
            if not context:
                logger.warning(WARNING_MESSAGES["NO_INVITE_CONTEXT_FOUND"])
                return None

            # Process each new member
            processed_members = []
            for member in new_members:
                try:
                    member_info = {
                        "user_id": getattr(member, "id", None),
                        "username": getattr(member, "username", None),
                        "first_name": getattr(member, "first_name", None),
                        "last_name": getattr(member, "last_name", None),
                        "is_bot": getattr(member, "is_bot", False),
                    }
                    processed_members.append(member_info)
                except Exception as e:
                    logger.warning(WARNING_MESSAGES["MEMBER_PROCESSING_ERROR"].format(error=str(e)))
                    continue

            # Combine all information
            result = {
                "new_members": processed_members,
                "context": context,
                "timestamp": getattr(raw_update.message, "date", None),
            }

            logger.info(LOG_MESSAGES["INVITE_EVENT_PROCESSED"].format(
                member_count=len(processed_members),
                chat_id=context.get("chat_id"),
                from_user=context.get("from_username")
            ))

            return result
            
        except Exception as e:
            logger.error(f"❌ Error in process_invite_event: {e}")
            return None
