"""
Team repository interfaces following Interface Segregation Principle.

These interfaces are split into focused, cohesive contracts for team operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from kickai.core.value_objects import TeamId, TelegramId

from .repository_base import IRepository


class ITeamConfigRepository(ABC):
    """Team configuration operations."""

    @abstractmethod
    async def get_team_config(self, team_id: TeamId) -> dict[str, Any] | None:
        """Get team configuration."""
        pass

    @abstractmethod
    async def update_team_config(
        self,
        team_id: TeamId,
        config_updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update team configuration."""
        pass


class ITeamMemberReadRepository(ABC):
    """Read operations for team members."""

    @abstractmethod
    async def get_team_members(self, team_id: TeamId) -> list[dict[str, Any]]:
        """Get all team members."""
        pass

    @abstractmethod
    async def get_team_member_by_user_id(
        self,
        user_id: TelegramId,
        team_id: TeamId
    ) -> dict[str, Any] | None:
        """Get team member by user ID."""
        pass


class ITeamMemberWriteRepository(ABC):
    """Write operations for team members."""

    @abstractmethod
    async def add_team_member(
        self,
        member_data: dict[str, Any],
        team_id: TeamId
    ) -> dict[str, Any]:
        """Add new team member."""
        pass

    @abstractmethod
    async def update_team_member(
        self,
        user_id: TelegramId,
        team_id: TeamId,
        updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update team member information."""
        pass

    @abstractmethod
    async def remove_team_member(
        self,
        user_id: TelegramId,
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


# Legacy interface alias for backward compatibility
# This interface is defined in features/team_administration but imported by core modules
from kickai.features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
