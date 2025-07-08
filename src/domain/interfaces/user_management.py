"""
Domain interface for user management operations.

This interface defines the contract for user-related operations
without depending on the infrastructure layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class UserRole:
    """User role information."""
    user_id: str
    team_id: str
    roles: List[str]
    is_active: bool = True


class IUserManagement(ABC):
    """Interface for user management operations."""
    
    @abstractmethod
    async def get_user_role(self, user_id: str, team_id: str) -> str:
        """Get the primary role of a user in a team."""
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: str, team_id: str) -> List[str]:
        """Get all roles of a user in a team."""
        pass
    
    @abstractmethod
    async def is_user_in_team(self, user_id: str, team_id: str) -> bool:
        """Check if a user is a member of a team."""
        pass
    
    @abstractmethod
    async def is_leadership_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if a chat is a leadership chat for a team."""
        pass 