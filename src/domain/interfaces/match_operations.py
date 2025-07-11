"""
Domain interface for match operations.

This interface defines the contract for match-related operations
without depending on the application layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class MatchInfo:
    """Match information data structure."""
    id: str
    opponent: str
    date: str
    time: str
    venue: str
    competition: str
    team_id: str
    status: str
    result: Optional[str] = None


class IMatchOperations(ABC):
    """Interface for match operations."""
    
    @abstractmethod
    async def create_match(self, opponent: str, date: str, time: str, venue: str, competition: str, team_id: str) -> tuple[bool, str]:
        """Create a new match."""
        pass
    
    @abstractmethod
    async def list_matches(self, team_id: str) -> str:
        """List all matches for a team."""
        pass
    
    @abstractmethod
    async def get_match(self, match_id: str, team_id: str) -> Optional[MatchInfo]:
        """Get match information."""
        pass
    
    @abstractmethod
    async def update_match(self, match_id: str, updates: Dict[str, Any], team_id: str) -> tuple[bool, str]:
        """Update match information."""
        pass
    
    @abstractmethod
    async def delete_match(self, match_id: str, team_id: str) -> tuple[bool, str]:
        """Delete a match."""
        pass
    
    @abstractmethod
    async def record_match_result(self, match_id: str, result: str, team_id: str) -> tuple[bool, str]:
        """Record match result."""
        pass
    
    @abstractmethod
    async def attend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Mark player attendance for a match."""
        pass
    
    @abstractmethod
    async def unattend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Cancel player attendance for a match."""
        pass 