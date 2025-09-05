#!/usr/bin/env python3
"""
Communication Service Interface

Defines the contract for communication services in the KICKAI system.
"""

from abc import ABC, abstractmethod
from typing import Any

from kickai.core.enums import ChatType


class ICommunicationService(ABC):
    """Interface for communication service operations."""

    @abstractmethod
    async def send_message(
        self, message: str, chat_type: str | ChatType, team_id: str, telegram_id: int | None = None
    ) -> bool:
        """
        Send a message to a specific chat type.

        Args:
            message: The message to send
            chat_type: The chat type (ChatType enum or string)
            team_id: The team ID
            telegram_id: Optional Telegram user ID

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        pass

    @abstractmethod
    async def send_announcement(self, announcement: str, team_id: str) -> bool:
        """
        Send an announcement to the team.

        Args:
            announcement: The announcement message
            team_id: The team ID

        Returns:
            bool: True if announcement sent successfully, False otherwise
        """
        pass

    @abstractmethod
    async def send_poll(self, question: str, options: str, team_id: str) -> bool:
        """
        Send a poll to the team.

        Args:
            question: The poll question
            options: Comma-separated poll options
            team_id: The team ID

        Returns:
            bool: True if poll sent successfully, False otherwise
        """
        pass

    @abstractmethod
    async def send_bulk_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Send multiple messages in bulk.

        Args:
            messages: List of message dictionaries with chat_id and content

        Returns:
            List of send results for each message
        """
        pass

    @abstractmethod
    async def create_invite_link(
        self, chat_id: str, expire_date: int | None = None, member_limit: int | None = None
    ) -> str:
        """
        Create an invite link for a chat.

        Args:
            chat_id: Chat identifier to create invite for
            expire_date: Optional expiration timestamp
            member_limit: Optional member limit for the link

        Returns:
            Generated invite link URL
        """
        pass

    @abstractmethod
    async def get_chat_info(self, chat_id: str) -> dict[str, Any]:
        """
        Get information about a chat.

        Args:
            chat_id: Chat identifier

        Returns:
            Dictionary containing chat information
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if communication service is available.

        Returns:
            True if service is operational
        """
        pass
