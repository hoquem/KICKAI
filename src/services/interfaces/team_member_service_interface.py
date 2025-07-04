"""
Team Member Service Interface

This module defines the interface for team member management operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ...database.models import TeamMember


class ITeamMemberService(ABC):
    """Interface for team member management operations."""
    
    @abstractmethod
    async def add_member(self, team_id: str, user_id: str, role: str = "player",
                        permissions: Optional[List[str]] = None) -> TeamMember:
        """
        Add a member to a team.
        
        Args:
            team_id: The team ID
            user_id: The user ID to add
            role: The role for the member
            permissions: Optional list of permissions
            
        Returns:
            TeamMember object
        """
        pass
    
    @abstractmethod
    async def remove_member(self, team_id: str, user_id: str) -> bool:
        """
        Remove a member from a team.
        
        Args:
            team_id: The team ID
            user_id: The user ID to remove
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_member(self, team_id: str, user_id: str) -> Optional[TeamMember]:
        """
        Get a team member by user ID.
        
        Args:
            team_id: The team ID
            user_id: The user ID to get
            
        Returns:
            TeamMember object or None if not found
        """
        pass
    
    @abstractmethod
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """
        Get all members of a team.
        
        Args:
            team_id: The team ID
            
        Returns:
            List of TeamMember objects
        """
        pass
    
    @abstractmethod
    async def update_member_role(self, team_id: str, user_id: str, new_role: str) -> TeamMember:
        """
        Update the role of a team member.
        
        Args:
            team_id: The team ID
            user_id: The user ID to update
            new_role: The new role
            
        Returns:
            Updated TeamMember object
        """
        pass
    
    @abstractmethod
    async def update_member_permissions(self, team_id: str, user_id: str, 
                                      permissions: List[str]) -> TeamMember:
        """
        Update the permissions of a team member.
        
        Args:
            team_id: The team ID
            user_id: The user ID to update
            permissions: The new permissions list
            
        Returns:
            Updated TeamMember object
        """
        pass 