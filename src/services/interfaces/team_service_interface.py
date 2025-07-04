"""
Team Service Interface

This module defines the interface for team management operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ...database.models import Team, TeamStatus, TeamMember, BotMapping


class ITeamService(ABC):
    """Interface for team management operations."""
    
    @abstractmethod
    async def create_team(self, name: str, description: Optional[str] = None,
                         settings: Optional[Dict[str, Any]] = None) -> Team:
        """Create a new team with validation."""
        pass
    
    @abstractmethod
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        pass
    
    @abstractmethod
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get a team by name."""
        pass
    
    @abstractmethod
    async def update_team(self, team_id: str, **updates) -> Team:
        """Update a team with validation."""
        pass
    
    @abstractmethod
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        pass
    
    @abstractmethod
    async def get_all_teams(self, status: Optional[TeamStatus] = None) -> List[Team]:
        """Get all teams, optionally filtered by status."""
        pass
    
    @abstractmethod
    async def add_team_member(self, team_id: str, user_id: str, role: str = "player",
                            permissions: Optional[List[str]] = None) -> TeamMember:
        """Add a member to a team."""
        pass
    
    @abstractmethod
    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        pass
    
    @abstractmethod
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        pass
    
    @abstractmethod
    async def create_bot_mapping(self, team_name: str, bot_username: str, 
                               chat_id: str, bot_token: str) -> BotMapping:
        """Create a bot mapping for a team."""
        pass
    
    @abstractmethod
    async def get_bot_mapping(self, team_name: str) -> Optional[BotMapping]:
        """Get bot mapping for a team."""
        pass 