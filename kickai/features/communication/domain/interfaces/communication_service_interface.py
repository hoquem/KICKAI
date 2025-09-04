#!/usr/bin/env python3
"""
Communication Service Interface

Defines the contract for communication services in the KICKAI system.
"""

from abc import ABC, abstractmethod
from typing import Any


class ICommunicationService(ABC):
    """Interface for communication service operations."""

    @abstractmethod
    async def send_message(
        self,
        chat_id: str,
        message: str,
        parse_mode: str | None = None,
        reply_markup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send a message to a chat.

        Args:
            chat_id: Target chat identifier
            message: Message content to send
            parse_mode: Message parsing mode (HTML, Markdown, etc.)
            reply_markup: Optional reply markup for interactive messages

        Returns:
            Dictionary containing send result and message info
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
