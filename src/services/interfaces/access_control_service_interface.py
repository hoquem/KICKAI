"""
Access Control Service Interface

This module defines the interface for access control and permission checking operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class ChatType(Enum):
    """Chat types for permission checking."""
    MAIN = "main"
    LEADERSHIP = "leadership"
    PRIVATE = "private"


class UserRole(Enum):
    """User roles for permission checking."""
    PLAYER = "player"
    CAPTAIN = "captain"
    ADMIN = "admin"
    UNKNOWN = "unknown"


class IAccessControlService(ABC):
    """Interface for access control and permission checking operations."""
    
    @abstractmethod
    async def get_user_role(self, user_id: str, team_id: str) -> UserRole:
        """
        Get the role of a user in a team.
        
        Args:
            user_id: The user ID to check
            team_id: The team ID to check in
            
        Returns:
            UserRole enum value
        """
        pass
    
    @abstractmethod
    async def can_execute_command(self, command: str, user_id: str, 
                                chat_id: str, team_id: str) -> bool:
        """
        Check if a user can execute a specific command.
        
        Args:
            command: The command to check
            user_id: The user ID to check
            chat_id: The chat ID where command is executed
            team_id: The team ID context
            
        Returns:
            True if user can execute command, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_chat_type(self, chat_id: str) -> ChatType:
        """
        Get the type of a chat.
        
        Args:
            chat_id: The chat ID to check
            
        Returns:
            ChatType enum value
        """
        pass
    
    @abstractmethod
    async def is_leadership_chat(self, chat_id: str) -> bool:
        """
        Check if a chat is a leadership chat.
        
        Args:
            chat_id: The chat ID to check
            
        Returns:
            True if leadership chat, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_permissions(self, user_id: str, team_id: str) -> List[str]:
        """
        Get the permissions of a user in a team.
        
        Args:
            user_id: The user ID to check
            team_id: The team ID to check in
            
        Returns:
            List of permission strings
        """
        pass 