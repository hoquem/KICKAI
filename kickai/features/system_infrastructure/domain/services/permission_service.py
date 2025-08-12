#!/usr/bin/env python3
"""
Centralized Permission Service for KICKAI

This service provides a single source of truth for all permission checks,
integrating chat-based role assignment with command permissions.
"""

from loguru import logger

from kickai.core.enums import ChatType, PermissionLevel, UserRole
from kickai.core.interfaces.player_repositories import IPlayerRepository
from kickai.core.interfaces.team_repositories import ITeamRepository
from kickai.core.value_objects.entity_context import EntityContext, UserRegistration


class UserPermissions:
    """User permissions information."""

    def __init__(
        self,
        is_player: bool = False,
        is_team_member: bool = False,
        is_admin: bool = False,
        roles: list[str] | None = None,
        permissions: list[PermissionLevel] | None = None,
    ):
        self.is_player = is_player
        self.is_team_member = is_team_member
        self.is_admin = is_admin
        self.roles = roles or []
        self.permissions = permissions or []

    def has_permission(self, permission: PermissionLevel) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def has_any_role(self) -> bool:
        """Check if user has any role."""
        return self.is_player or self.is_team_member

    def primary_role(self) -> str:
        """Get the primary role of the user."""
        if self.is_team_member:
            return "team_member"
        elif self.is_player:
            return "player"
        else:
            return "unregistered"


class PermissionService:
    """Service for managing user permissions and access control."""

    def __init__(
        self,
        player_repository: IPlayerRepository,
        team_repository: ITeamRepository,
    ):
        self.player_repository = player_repository
        self.team_repository = team_repository
        self.logger = logger

    async def get_user_role_in_chat(self, telegram_id: str, team_id: str, chat_type: str):
        """
        Get user's role in a specific chat context.

        :param telegram_id: User's Telegram ID
        :type telegram_id: str
        :param team_id: Team ID
        :type team_id: str
        :param chat_type: Type of chat (main_chat, leadership_chat, private)
        :type chat_type: str
        :return: User's role in the chat context
        :rtype: str
        """
        try:
            # Get user permissions
            user_perms = await self.get_user_permissions(telegram_id, team_id)

            # Determine role based on chat type and permissions
            if chat_type == ChatType.MAIN.value:
                # In main chat, prioritize player role
                if user_perms.is_player:
                    return UserRole.PLAYER.value
                elif user_perms.is_team_member:
                    return UserRole.TEAM_MEMBER.value
                else:
                    return "unregistered"
            elif chat_type == ChatType.LEADERSHIP.value:
                # In leadership chat, prioritize team member role
                if user_perms.is_team_member:
                    return UserRole.TEAM_MEMBER.value
                elif user_perms.is_player:
                    return "player"
                else:
                    return "unregistered"
            else:
                # Private chat - use actual roles
                return user_perms.primary_role()

        except Exception as e:
            self.logger.error(f"Error getting user role in chat: {e}")
            return "unregistered"

    async def get_user_permissions(self, telegram_id: str, team_id: str) -> UserPermissions:
        """
        Get comprehensive user permissions for a team.

        :param telegram_id: User's Telegram ID
        :type telegram_id: str
        :param team_id: Team ID
        :type team_id: str
        :return: UserPermissions object with user's permissions
        :rtype: UserPermissions
        """
        try:
            # Check if user is a player
            player = await self.player_repository.get_by_telegram_id(telegram_id, team_id)
            is_player = player is not None

            # Check if user is a team member
            team_member = await self.team_repository.get_team_member_by_telegram_id(telegram_id, team_id)
            is_team_member = team_member is not None

            # Determine admin status
            is_admin = False
            if team_member:
                is_admin = team_member.is_admin

            # Build roles list
            roles = []
            if is_player:
                roles.append(UserRole.PLAYER.value)
            if is_team_member:
                roles.append(UserRole.TEAM_MEMBER.value)
            if is_admin:
                roles.append(UserRole.ADMIN.value)

            # Determine permissions based on roles
            permissions = []
            if is_player:
                permissions.extend([
                    PermissionLevel.PLAYER_BASIC,
                    PermissionLevel.PLAYER_ADVANCED,
                ])
            if is_team_member:
                permissions.extend([
                    PermissionLevel.TEAM_MEMBER_BASIC,
                    PermissionLevel.TEAM_MEMBER_ADVANCED,
                ])
            if is_admin:
                permissions.extend([
                    PermissionLevel.ADMIN_BASIC,
                    PermissionLevel.ADMIN_ADVANCED,
                ])

            return UserPermissions(
                is_player=is_player,
                is_team_member=is_team_member,
                is_admin=is_admin,
                roles=roles,
                permissions=permissions,
            )

        except Exception as e:
            self.logger.error(f"Error getting user permissions: {e}")
            return UserPermissions()

    async def check_permission(
        self, context: EntityContext, required_permission: PermissionLevel
    ) -> bool:
        """
        Check if user has a specific permission.

        :param context: Entity context with user information
        :type context: EntityContext
        :param required_permission: Permission level required
        :type required_permission: PermissionLevel
        :return: True if user has the required permission
        :rtype: bool
        """
        try:
            user_perms = await self.get_user_permissions(context.telegram_id.value, context.team_id.value)
            return user_perms.has_permission(required_permission)

        except Exception as e:
            self.logger.error(f"Error checking permission: {e}")
            return False

    async def require_permission(
        self, context: EntityContext, required_permission: PermissionLevel
    ) -> None:
        """
        Require a specific permission, raise exception if not met.

        :param context: Entity context with user information
        :type context: EntityContext
        :param required_permission: Permission level required
        :type required_permission: PermissionLevel
        :raises PermissionError: If user lacks required permission
        """
        if not await self.check_permission(context, required_permission):
            raise PermissionError(
                context.telegram_id.value,
                f"access {required_permission.value}",
                f"User {context.telegram_id.value} lacks {required_permission.value} permission"
            )

    async def get_user_role(self, telegram_id: str, team_id: str) -> str:
        """
        Get user's primary role in a team.

        :param telegram_id: User's Telegram ID
        :type telegram_id: str
        :param team_id: Team ID
        :type team_id: str
        :return: User's primary role
        :rtype: str
        """
        try:
            user_perms = await self.get_user_permissions(telegram_id, team_id)
            return user_perms.primary_role()

        except Exception as e:
            self.logger.error(f"Error getting user role: {e}")
            return "unregistered"

    async def is_user_registered(self, telegram_id: str, team_id: str) -> bool:
        """
        Check if user is registered in the team.

        :param telegram_id: User's Telegram ID
        :type telegram_id: str
        :param team_id: Team ID
        :type team_id: str
        :return: True if user is registered
        :rtype: bool
        """
        try:
            user_perms = await self.get_user_permissions(telegram_id, team_id)
            return user_perms.has_any_role()

        except Exception as e:
            self.logger.error(f"Error checking user registration: {e}")
            return False

    async def get_user_registration_context(self, telegram_id: str, team_id: str) -> UserRegistration:
        """
        Get user registration context.

        :param telegram_id: User's Telegram ID
        :type telegram_id: str
        :param team_id: Team ID
        :type team_id: str
        :return: UserRegistration object
        :rtype: UserRegistration
        """
        try:
            user_perms = await self.get_user_permissions(telegram_id, team_id)

            return UserRegistration(
                is_registered=user_perms.has_any_role(),
                is_player=user_perms.is_player,
                is_team_member=user_perms.is_team_member,
                is_admin=user_perms.is_admin,
                is_leadership=user_perms.is_admin,  # Admin users are considered leadership
            )

        except Exception as e:
            self.logger.error(f"Error getting user registration context: {e}")
            return UserRegistration.unregistered()

    async def validate_user_access(
        self, context: EntityContext, required_permission: PermissionLevel
    ) -> bool:
        """
        Validate user access for a specific operation.


            context: Entity context with user information
            required_permission: Permission level required


    :return: True if user has access
    :rtype: str  # TODO: Fix type
        """
        try:
            # Check if user is registered
            if not await self.is_user_registered(context.telegram_id.value, context.team_id.value):
                self.logger.warning(f"Unregistered user {context.telegram_id.value} attempted access")
                return False

            # Check specific permission
            return await self.check_permission(context, required_permission)

        except Exception as e:
            self.logger.error(f"Error validating user access: {e}")
            return False

    async def get_user_permissions_summary(self, telegram_id: str, team_id: str) -> dict[str, any]:
        """
        Get a summary of user permissions.


            telegram_id: User's Telegram ID
            team_id: Team ID


    :return: Dictionary with permission summary
    :rtype: str  # TODO: Fix type
        """
        try:
            user_perms = await self.get_user_permissions(telegram_id, team_id)

            return {
                "telegram_id": telegram_id,
                "team_id": team_id,
                "is_registered": user_perms.has_any_role(),
                "is_player": user_perms.is_player,
                "is_team_member": user_perms.is_team_member,
                "is_admin": user_perms.is_admin,
                "primary_role": user_perms.primary_role(),
                "roles": user_perms.roles,
                "permissions": [perm.value for perm in user_perms.permissions],
            }

        except Exception as e:
            self.logger.error(f"Error getting user permissions summary: {e}")
            return {
                "telegram_id": telegram_id,
                "team_id": team_id,
                "is_registered": False,
                "is_player": False,
                "is_team_member": False,
                "is_admin": False,
                "primary_role": "unregistered",
                "roles": [],
                "permissions": [],
            }


class PermissionError(Exception):
    """Raised when a user lacks required permissions."""

    def __init__(self, telegram_id: str, action: str, reason: str = "Insufficient permissions"):
        self.telegram_id = telegram_id
        self.action = action
        self.reason = reason
        super().__init__(f"Permission denied for user {telegram_id}: {reason}")
