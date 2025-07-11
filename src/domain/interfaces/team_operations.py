"""
Domain interface for team operations.

This interface defines the contract for team-related operations
without depending on the application layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class TeamInfo:
    """Team information data structure."""
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: str


class ITeamOperations(ABC):
    """Interface for team operations."""
    
    @abstractmethod
    async def create_team(self, name: str, description: Optional[str] = None) -> tuple[bool, str]:
        """Create a new team."""
        pass
    
    @abstractmethod
    async def delete_team(self, team_id: str) -> tuple[bool, str]:
        """Delete a team."""
        pass
    
    @abstractmethod
    async def list_teams(self) -> str:
        """List all teams."""
        pass
    
    @abstractmethod
    async def get_team_stats(self, team_id: str) -> str:
        """Get team statistics."""
        pass 