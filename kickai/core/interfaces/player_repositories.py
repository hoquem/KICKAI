"""
Player repository interfaces following Interface Segregation Principle.

These interfaces are split into focused, cohesive contracts for player operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from kickai.core.value_objects import PhoneNumber, PlayerId, TeamId, TelegramId

from .repository_base import IRepository


class IPlayerReadRepository(ABC):
    """Read-only operations for player data."""

    @abstractmethod
    async def get_by_phone(
        self,
        phone: PhoneNumber,
        team_id: TeamId
    ) -> dict[str, Any] | None:
        """Get player by phone number and team."""
        pass

    @abstractmethod
    async def get_by_telegram_id(
        self,
        user_id: TelegramId,
        team_id: TeamId
    ) -> dict[str, Any] | None:
        """Get player by telegram ID and team."""
        pass

    @abstractmethod
    async def get_active_players(
        self,
        team_id: TeamId
    ) -> list[dict[str, Any]]:
        """Get all active players for a team."""
        pass


class IPlayerWriteRepository(ABC):
    """Write operations for player data."""

    @abstractmethod
    async def create_player(
        self,
        player_data: dict[str, Any],
        team_id: TeamId
    ) -> dict[str, Any]:
        """Create new player."""
        pass

    @abstractmethod
    async def update_player(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        updates: dict[str, Any]
    ) -> dict[str, Any] | None:
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
    ) -> list[dict[str, Any]]:
        """Get players pending approval."""
        pass

    @abstractmethod
    async def approve_player(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        approved_by: TelegramId
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
