#!/usr/bin/env python3
"""
Message Service Interface

Defines the contract for message management services.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class IMessageService(ABC):
    """Interface for message service operations."""

    @abstractmethod
    async def create_message(
        self,
        chat_id: str,
        user_id: str,
        content: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Create and store a message.
        
        Args:
            chat_id: Chat identifier where message was sent
            user_id: User who sent the message
            content: Message content
            message_type: Type of message (text, command, etc.)
            
        Returns:
            Created message data
        """
        pass

    @abstractmethod
    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a message by ID.
        
        Args:
            message_id: Message identifier
            
        Returns:
            Message data if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_chat_messages(
        self,
        chat_id: str,
        limit: int = 50,
        before_timestamp: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a chat.
        
        Args:
            chat_id: Chat identifier
            limit: Maximum number of messages to return
            before_timestamp: Get messages before this timestamp
            
        Returns:
            List of message data
        """
        pass

    @abstractmethod
    async def mark_message_processed(self, message_id: str) -> bool:
        """
        Mark a message as processed.
        
        Args:
            message_id: Message identifier
            
        Returns:
            True if successfully marked
        """
        pass

    @abstractmethod
    async def get_unprocessed_messages(
        self,
        chat_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get unprocessed messages.
        
        Args:
            chat_id: Optional chat filter
            
        Returns:
            List of unprocessed messages
        """
        pass