#!/usr/bin/env python3
"""
Centralized Permission Service for KICKAI

This service provides a single source of truth for all permission checks,
integrating chat-based role assignment with command permissions.
"""

import logging
from dataclasses import dataclass

from kickai.core.enums import ChatType, PermissionLevel
from kickai.database.firebase_client import FirebaseClient

# TeamMemberService removed - using mock service instead
from kickai.features.team_administration.domain.services.chat_role_assignment_service import (
    ChatRoleAssignmentService,
)

logger = logging.getLogger(__name__)


@dataclass
class PermissionContext:
    """Context for permission checking."""
    user_id: str
    team_id: str
    chat_id: str
    chat_type: ChatType
    username: str | None = None

    def __post_init__(self):
        if self.chat_type is None:
            self.chat_type = self._determine_chat_type()

    def _determine_chat_type(self) -> ChatType:
        """Determine chat type based on chat ID or other context."""
        # This would be enhanced with actual chat mapping logic
        # For now, return a default
        return ChatType.MAIN


@dataclass
class UserPermissions:
    """User permissions information."""
    user_id: str
    team_id: str
    roles: list[str]
    chat_access: dict[str, bool]
    is_admin: bool
    is_player: bool
    is_team_member: bool
    is_first_user: bool
    can_access_main_chat: bool
    can_access_leadership_chat: bool


class PermissionService:
    """Centralized service for all permission checking."""

    def __init__(self, firebase_client: FirebaseClient = None):
        self.firebase_client = firebase_client
        if firebase_client:
            self.chat_role_service = ChatRoleAssignmentService(firebase_client)
        else:
            # Use mock chat role service when firebase_client is None
            self.chat_role_service = self._create_mock_chat_role_service()

        # Get services from dependency container instead of creating them directly
        try:
            from kickai.core.dependency_container import get_service
            from kickai.features.player_registration.domain.services.player_service import (
                PlayerService,
            )
            from kickai.features.team_administration.domain.services.team_service import TeamService

            self.player_service = get_service(PlayerService)
            self.team_service = get_service(TeamService)

            # For now, use a simple mock team member service until the full implementation is ready
            self.team_member_service = self._create_mock_team_member_service()

        except Exception as e:
            logger.warning(f"⚠️ Could not get services from dependency container: {e}")
            # Fallback to mock services
            self.player_service = None
            self.team_service = None
            self.team_member_service = self._create_mock_team_member_service()

        logger.info("✅ PermissionService initialized")

    def _create_mock_team_member_service(self):
        """Create a mock team member service for fallback."""
        class MockTeamMemberService:
            async def get_team_member_by_telegram_id(self, user_id: str, team_id: str):
                return None

            async def is_first_user(self, team_id: str):
                return False

        return MockTeamMemberService()

    def _create_mock_chat_role_service(self):
        """Create a mock chat role service for fallback."""
        class MockChatRoleService:
            async def assign_role_to_user(self, user_id: str, team_id: str, role: str, chat_type: str):
                return True

            async def get_user_role_in_chat(self, user_id: str, team_id: str, chat_type: str):
                return "player"

        return MockChatRoleService()

    async def get_user_permissions(self, user_id: str, team_id: str) -> UserPermissions:
        """
        Get comprehensive user permissions information.

        This is the single source of truth for user permissions.
        """
        try:
            # Get team member information
            team_member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)

            if team_member:
                # User exists as team member
                roles = team_member.roles
                chat_access = team_member.chat_access
                is_admin = "admin" in roles
                is_player = "player" in roles
                is_team_member = "team_member" in roles

                # Check if this is the first user
                is_first_user = await self.team_member_service.is_first_user(team_id)

                return UserPermissions(
                    user_id=user_id,
                    team_id=team_id,
                    roles=roles,
                    chat_access=chat_access,
                    is_admin=is_admin,
                    is_player=is_player,
                    is_team_member=is_team_member,
                    is_first_user=is_first_user,
                    can_access_main_chat=chat_access.get("main_chat", False),
                    can_access_leadership_chat=chat_access.get("leadership_chat", False)
                )
            else:
                # User not found - return default permissions
                return UserPermissions(
                    user_id=user_id,
                    team_id=team_id,
                    roles=[],
                    chat_access={},
                    is_admin=False,
                    is_player=False,
                    is_team_member=False,
                    is_first_user=False,
                    can_access_main_chat=False,
                    can_access_leadership_chat=False
                )

        except Exception as e:
            logger.error(f"Error getting user permissions for {user_id}: {e}")
            # Return default permissions on error
            return UserPermissions(
                user_id=user_id,
                team_id=team_id,
                roles=[],
                chat_access={},
                is_admin=False,
                is_player=False,
                is_team_member=False,
                is_first_user=False,
                can_access_main_chat=False,
                can_access_leadership_chat=False
            )

    async def can_execute_command(self, permission_level: PermissionLevel, context: PermissionContext) -> bool:
        """
        Check if user can execute a command with given permission level.

        This is the main permission checking method used by all commands.
        """
        try:
            # Get user permissions
            user_perms = await self.get_user_permissions(context.user_id, context.team_id)

            # Check permission level
            if permission_level == PermissionLevel.PUBLIC:
                return True  # Public commands are always allowed

            elif permission_level == PermissionLevel.PLAYER:
                # Player commands require player role and main chat access only
                if not user_perms.is_player:
                    return False

                # Must be in main chat only (not leadership chat)
                return context.chat_type == ChatType.MAIN

            elif permission_level == PermissionLevel.LEADERSHIP:
                # Leadership commands require leadership chat access
                if context.chat_type != ChatType.LEADERSHIP:
                    return False

                # Must have team member role or be admin
                return user_perms.is_team_member or user_perms.is_admin

            elif permission_level == PermissionLevel.ADMIN:
                # Admin commands require leadership chat access and admin role
                if context.chat_type != ChatType.LEADERSHIP:
                    return False

                return user_perms.is_admin

            return False

        except Exception as e:
            logger.error(f"Error checking command permissions: {e}")
            return False

    async def get_user_role(self, user_id: str, team_id: str) -> str:
        """
        Get the primary role of a user for backward compatibility.

        This method is used by existing code that expects a simple role string.
        """
        try:
            user_perms = await self.get_user_permissions(user_id, team_id)

            # Return the most significant role
            if user_perms.is_admin:
                return "admin"
            elif user_perms.is_team_member:
                return "team_member"
            elif user_perms.is_player:
                return "player"
            else:
                return "none"

        except Exception as e:
            logger.error(f"Error getting user role for {user_id}: {e}")
            return "none"

    async def require_permission(self, permission_level: PermissionLevel, context: PermissionContext) -> bool:
        """
        Require a specific permission level - throws exception if not met.

        Use this for critical operations that should fail fast.
        """
        if not await self.can_execute_command(permission_level, context):
            raise PermissionError(f"User {context.user_id} lacks {permission_level.value} permission")
        return True

    async def get_available_commands(self, context: PermissionContext) -> list[str]:
        """
        Get list of available commands for a user in the given context.

        This is used by the help system to show appropriate commands.
        """
        try:
            # Use centralized constants for command lists
            from kickai.core.constants import get_commands_for_permission_level

            available_commands = []

            # Get commands by permission level
            public_commands = get_commands_for_permission_level(PermissionLevel.PUBLIC)
            available_commands.extend([cmd.name for cmd in public_commands])

            if await self.can_execute_command(PermissionLevel.PLAYER, context):
                player_commands = get_commands_for_permission_level(PermissionLevel.PLAYER)
                available_commands.extend([cmd.name for cmd in player_commands])

            if await self.can_execute_command(PermissionLevel.LEADERSHIP, context):
                leadership_commands = get_commands_for_permission_level(PermissionLevel.LEADERSHIP)
                available_commands.extend([cmd.name for cmd in leadership_commands])

            if await self.can_execute_command(PermissionLevel.ADMIN, context):
                admin_commands = get_commands_for_permission_level(PermissionLevel.ADMIN)
                available_commands.extend([cmd.name for cmd in admin_commands])

            return available_commands

        except Exception as e:
            logger.error(f"Error getting available commands: {e}")
            return ["/help", "/start"]

    async def get_permission_denied_message(self, permission_level: PermissionLevel, context: PermissionContext) -> str:
        """
        Get a user-friendly message explaining why permission was denied.
        """
        try:
            user_perms = await self.get_user_permissions(context.user_id, context.team_id)

            if permission_level == PermissionLevel.PLAYER:
                if not user_perms.is_player:
                    return f"""❌ Access Denied

🔒 This command requires player access.
💡 Contact your team admin for access.

Your Role: {', '.join(user_perms.roles) if user_perms.roles else 'None'}"""
                else:
                    return """❌ Access Denied

🔒 Player commands are only available in the main team chat.
💡 Please use the main team chat for this function."""

            elif permission_level == PermissionLevel.LEADERSHIP:
                if context.chat_type != ChatType.LEADERSHIP:
                    return """❌ Access Denied

🔒 Leadership commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""
                else:
                    return f"""❌ Access Denied

🔒 This command requires leadership access.
💡 Contact your team admin for access.

Your Role: {', '.join(user_perms.roles) if user_perms.roles else 'None'}"""

            elif permission_level == PermissionLevel.ADMIN:
                if context.chat_type != ChatType.LEADERSHIP:
                    return """❌ Access Denied

🔒 Admin commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""
                else:
                    return f"""❌ Access Denied

🔒 This command requires admin access.
💡 Contact your team admin for access.

Your Role: {', '.join(user_perms.roles) if user_perms.roles else 'None'}"""

            return "❌ Access denied for this command."

        except Exception as e:
            logger.error(f"Error generating permission denied message: {e}")
            return "❌ Access denied for this command."

    async def is_first_user(self, team_id: str) -> bool:
        """Check if this would be the first user in the team."""
        return await self.team_member_service.is_first_user(team_id)

    async def promote_to_admin(self, user_id: str, team_id: str, promoted_by: str) -> bool:
        """Promote a user to admin role (only by existing admin)."""
        return await self.team_member_service.promote_to_admin(user_id, team_id, promoted_by)

    async def handle_last_admin_leaving(self, team_id: str) -> str | None:
        """Handle when the last admin leaves - promote longest-tenured leadership member."""
        return await self.team_member_service.handle_last_admin_leaving(team_id)

    async def is_user_registered(self, context: PermissionContext) -> bool:
        """Check if a user is already registered in the system."""
        try:
            user_perms = await self.get_user_permissions(context.user_id, context.team_id)
            return user_perms.is_player or user_perms.is_team_member or user_perms.is_admin
        except Exception as e:
            logger.error(f"Error checking if user is registered: {e}")
            return False


# Global instance for easy access
_permission_service: PermissionService | None = None


def get_permission_service(firebase_client: FirebaseClient = None) -> PermissionService:
    """Get the global permission service instance."""
    global _permission_service
    if _permission_service is None:
        if firebase_client is None:
            # Get Firebase client from dependency container
            try:
                from kickai.database.firebase_client import get_firebase_client
                firebase_client = get_firebase_client()
            except Exception as e:
                logger.warning(f"⚠️ Could not get Firebase client from dependency container: {e}")
                # Fallback to mock client
                firebase_client = None
        _permission_service = PermissionService(firebase_client)
    return _permission_service
