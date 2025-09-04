"""
User repository interfaces following Interface Segregation Principle.

These interfaces are split into focused, cohesive contracts for user operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from kickai.core.value_objects import TeamId, UserId

from .repository_base import IRepository


class IUserRegistrationRepository(ABC):
    """User registration operations."""

    @abstractmethod
    async def get_user_registration(
        self, user_id: UserId, team_id: TeamId
    ) -> dict[str, Any] | None:
        """Get user registration information."""
        pass

    @abstractmethod
    async def create_user_registration(
        self, user_id: UserId, team_id: TeamId, registration_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create user registration."""
        pass

    @abstractmethod
    async def update_user_registration(
        self, user_id: UserId, team_id: TeamId, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update user registration."""
        pass


class IUserPermissionRepository(ABC):
    """User permission operations."""

    @abstractmethod
    async def get_user_permissions(self, user_id: UserId, team_id: TeamId) -> list[str]:
        """Get user permissions for a team."""
        pass

    @abstractmethod
    async def set_user_permissions(
        self, user_id: UserId, team_id: TeamId, permissions: list[str]
    ) -> bool:
        """Set user permissions for a team."""
        pass

    @abstractmethod
    async def add_user_permission(self, user_id: UserId, team_id: TeamId, permission: str) -> bool:
        """Add single permission to user."""
        pass

    @abstractmethod
    async def remove_user_permission(
        self, user_id: UserId, team_id: TeamId, permission: str
    ) -> bool:
        """Remove single permission from user."""
        pass


class IUserRepository(IUserRegistrationRepository, IUserPermissionRepository, IRepository):
    """
    Complete user repository interface.

    This combines all user-related interfaces for backward compatibility
    while maintaining the option to use specific interfaces for focused dependencies.
    """

    pass
