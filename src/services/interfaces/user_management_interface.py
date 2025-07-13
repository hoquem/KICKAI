"""
User Management Interface

This interface defines the contract for user management services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IUserManagement(ABC):
    """Interface for user management services."""
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information.
        
        Args:
            user_id: The user ID
            
        Returns:
            User information dictionary or None if not found
        """
        pass
    
    @abstractmethod
    async def update_user_info(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update user information.
        
        Args:
            user_id: The user ID
            updates: Dictionary of updates to apply
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get user roles.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of user roles
        """
        pass 