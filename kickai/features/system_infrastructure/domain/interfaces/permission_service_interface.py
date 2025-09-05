#!/usr/bin/env python3
"""
Permission Service Interface

Defines the contract for permission and authorization services.
"""

from abc import ABC, abstractmethod

from kickai.core.enums import ChatType
from kickai.features.system_infrastructure.domain.services.permission_service import UserPermissions


class IPermissionService(ABC):
    """Interface for permission service operations."""

    @abstractmethod
    async def get_user_permissions(self, telegram_id: str, team_id: str) -> UserPermissions:
        """
        Get comprehensive permissions for a user.

        Args:
            telegram_id: User identifier (typically Telegram ID)
            team_id: Team identifier

        Returns:
            UserPermissions object with all permission flags
        """
        pass

    @abstractmethod
    async def check_permission(
        self, telegram_id: str, team_id: str, permission: str, chat_type: ChatType | None = None
    ) -> bool:
        """
        Check if user has a specific permission.

        Args:
            telegram_id: User identifier
            team_id: Team identifier
            permission: Permission name to check
            chat_type: Chat context if relevant

        Returns:
            True if user has the permission
        """
        pass

    @abstractmethod
    async def is_player(self, telegram_id: str, team_id: str) -> bool:
        """
        Check if user is registered as a player.

        Args:
            telegram_id: User identifier
            team_id: Team identifier

        Returns:
            True if user is a player
        """
        pass

    @abstractmethod
    async def is_team_member(self, telegram_id: str, team_id: str) -> bool:
        """
        Check if user is a team member.

        Args:
            telegram_id: User identifier
            team_id: Team identifier

        Returns:
            True if user is a team member
        """
        pass

    @abstractmethod
    async def is_leadership(self, telegram_id: str, team_id: str) -> bool:
        """
        Check if user has leadership privileges.

        Args:
            telegram_id: User identifier
            team_id: Team identifier

        Returns:
            True if user has leadership access
        """
        pass

    @abstractmethod
    async def is_admin(self, telegram_id: str, team_id: str) -> bool:
        """
        Check if user has admin privileges.

        Args:
            telegram_id: User identifier
            team_id: Team identifier

        Returns:
            True if user is an admin
        """
        pass

    @abstractmethod
    async def get_user_roles(self, telegram_id: str, team_id: str) -> list[str]:
        """
        Get all roles assigned to a user.

        Args:
            telegram_id: User identifier
            team_id: Team identifier

        Returns:
            List of role names
        """
        pass

    @abstractmethod
    async def validate_chat_access(
        self, telegram_id: str, team_id: str, chat_type: ChatType
    ) -> bool:
        """
        Validate if user can access a specific chat type.

        Args:
            telegram_id: User identifier
            team_id: Team identifier
            chat_type: Chat type to validate access for

        Returns:
            True if access is allowed
        """
        pass
