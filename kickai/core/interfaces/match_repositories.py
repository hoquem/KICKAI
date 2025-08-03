"""
Match repository interfaces following Interface Segregation Principle.

These interfaces are split into focused, cohesive contracts for match operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from kickai.core.value_objects import TeamId, PlayerId
from .repository_base import IRepository


class IMatchReadRepository(ABC):
    """Read operations for match data."""
    
    @abstractmethod
    async def get_upcoming_matches(
        self, 
        team_id: TeamId,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get upcoming matches for a team."""
        pass
    
    @abstractmethod
    async def get_match_by_id(
        self, 
        match_id: str, 
        team_id: TeamId
    ) -> Optional[Dict[str, Any]]:
        """Get match by ID."""
        pass
    
    @abstractmethod
    async def get_past_matches(
        self, 
        team_id: TeamId,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get past matches for a team."""
        pass


class IMatchWriteRepository(ABC):
    """Write operations for match data."""
    
    @abstractmethod
    async def create_match(
        self, 
        match_data: Dict[str, Any], 
        team_id: TeamId
    ) -> Dict[str, Any]:
        """Create new match."""
        pass
    
    @abstractmethod
    async def update_match(
        self, 
        match_id: str, 
        team_id: TeamId,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update match information."""
        pass
    
    @abstractmethod
    async def cancel_match(
        self, 
        match_id: str, 
        team_id: TeamId,
        reason: str
    ) -> bool:
        """Cancel a match."""
        pass


class IMatchAvailabilityRepository(ABC):
    """Player availability operations for matches."""
    
    @abstractmethod
    async def get_player_availability(
        self, 
        match_id: str, 
        team_id: TeamId
    ) -> List[Dict[str, Any]]:
        """Get player availability for a match."""
        pass
    
    @abstractmethod
    async def set_player_availability(
        self, 
        match_id: str, 
        player_id: PlayerId,
        team_id: TeamId,
        availability: str
    ) -> bool:
        """Set player availability for a match."""
        pass
    
    @abstractmethod
    async def get_availability_summary(
        self, 
        match_id: str, 
        team_id: TeamId
    ) -> Dict[str, int]:
        """Get availability summary (available, unavailable, pending counts)."""
        pass


class IMatchRepository(
    IMatchReadRepository,
    IMatchWriteRepository, 
    IMatchAvailabilityRepository,
    IRepository
):
    """
    Complete match repository interface.
    
    This combines all match-related interfaces for backward compatibility
    while maintaining the option to use specific interfaces for focused dependencies.
    """
    pass