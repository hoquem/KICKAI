"""
Player repository interfaces following Interface Segregation Principle.

These interfaces are split into focused, cohesive contracts for player operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set

from kickai.core.value_objects import PhoneNumber, PlayerId, TeamId, UserId

from .repository_base import IRepository


class IPlayerReadRepository(ABC):
    """Read-only operations for player data."""

    @abstractmethod
    async def get_by_phone(
        self,
        phone: PhoneNumber,
        team_id: TeamId
    ) -> Optional[Dict[str, Any]]:
        """Get player by phone number and team."""
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UserId,
        team_id: TeamId
    ) -> Optional[Dict[str, Any]]:
        """Get player by user ID and team."""
        pass

    @abstractmethod
    async def get_active_players(
        self,
        team_id: TeamId
    ) -> List[Dict[str, Any]]:
        """Get all active players for a team."""
        pass


class IPlayerWriteRepository(ABC):
    """Write operations for player data."""

    @abstractmethod
    async def create_player(
        self,
        player_data: Dict[str, Any],
        team_id: TeamId
    ) -> Dict[str, Any]:
        """Create new player."""
        pass

    @abstractmethod
    async def update_player(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update player information."""
        pass

    @abstractmethod
    async def set_player_status(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        status: str
    ) -> bool:
        """Set player status."""
        pass


class IPlayerApprovalRepository(ABC):
    """Player approval operations."""

    @abstractmethod
    async def get_pending_approvals(
        self,
        team_id: TeamId
    ) -> List[Dict[str, Any]]:
        """Get players pending approval."""
        pass

    @abstractmethod
    async def approve_player(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        approved_by: UserId
    ) -> bool:
        """Approve player registration."""
        pass


class IPlayerRepository(
    IPlayerReadRepository,
    IPlayerWriteRepository,
    IPlayerApprovalRepository,
    IRepository
):
    """
    Complete player repository interface.

    This combines all player-related interfaces for backward compatibility
    while maintaining the option to use specific interfaces for focused dependencies.
    """
    pass
