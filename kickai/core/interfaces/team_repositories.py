"""
Team repository interfaces following Interface Segregation Principle.

These interfaces are split into focused, cohesive contracts for team operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from kickai.core.value_objects import UserId, TeamId
from .repository_base import IRepository


class ITeamConfigRepository(ABC):
    """Team configuration operations."""
    
    @abstractmethod
    async def get_team_config(self, team_id: TeamId) -> Optional[Dict[str, Any]]:
        """Get team configuration."""
        pass
    
    @abstractmethod
    async def update_team_config(
        self, 
        team_id: TeamId,
        config_updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update team configuration."""
        pass


class ITeamMemberReadRepository(ABC):
    """Read operations for team members."""
    
    @abstractmethod
    async def get_team_members(self, team_id: TeamId) -> List[Dict[str, Any]]:
        """Get all team members."""
        pass
    
    @abstractmethod
    async def get_team_member_by_user_id(
        self, 
        user_id: UserId, 
        team_id: TeamId
    ) -> Optional[Dict[str, Any]]:
        """Get team member by user ID."""
        pass


class ITeamMemberWriteRepository(ABC):
    """Write operations for team members."""
    
    @abstractmethod
    async def add_team_member(
        self, 
        member_data: Dict[str, Any], 
        team_id: TeamId
    ) -> Dict[str, Any]:
        """Add new team member."""
        pass
    
    @abstractmethod
    async def update_team_member(
        self, 
        user_id: UserId, 
        team_id: TeamId,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update team member information."""
        pass
    
    @abstractmethod
    async def remove_team_member(
        self, 
        user_id: UserId, 
        team_id: TeamId
    ) -> bool:
        """Remove team member."""
        pass


class ITeamRepository(
    ITeamConfigRepository,
    ITeamMemberReadRepository, 
    ITeamMemberWriteRepository,
    IRepository
):
    """
    Complete team repository interface.
    
    This combines all team-related interfaces for backward compatibility
    while maintaining the option to use specific interfaces for focused dependencies.
    """
    pass