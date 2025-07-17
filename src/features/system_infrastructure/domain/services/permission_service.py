#!/usr/bin/env python3
"""
Centralized Permission Service for KICKAI

This service provides a single source of truth for all permission checks,
integrating chat-based role assignment with command permissions.
"""

import logging
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass
from enum import Enum

from database.firebase_client import FirebaseClient
from features.team_administration.domain.services.chat_role_assignment_service import ChatRoleAssignmentService, ChatType
from features.player_registration.domain.services.team_member_service import TeamMemberService
from features.player_registration.domain.services.player_service import PlayerService

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for commands."""
    PUBLIC = "public"
    PLAYER = "player"
    LEADERSHIP = "leadership"
    ADMIN = "admin"


class ChatType(Enum):
    """Chat types for permission checking."""
    MAIN = "main_chat"
    LEADERSHIP = "leadership_chat"
    PRIVATE = "private"


@dataclass
class PermissionContext:
    """Context for permission checking."""
    user_id: str
    team_id: str
    chat_id: str
    chat_type: ChatType
    username: Optional[str] = None
    
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
    roles: List[str]
    chat_access: Dict[str, bool]
    is_admin: bool
    is_player: bool
    is_team_member: bool
    is_first_user: bool
    can_access_main_chat: bool
    can_access_leadership_chat: bool


class PermissionService:
    """Centralized service for all permission checking."""
    
    def __init__(self, firebase_client: FirebaseClient):
        self.firebase_client = firebase_client
        self.chat_role_service = ChatRoleAssignmentService(firebase_client)
        self.team_member_service = TeamMemberService(firebase_client)
        self.player_service = PlayerService(firebase_client)
        logger.info("✅ PermissionService initialized")
    
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
                # Player commands require player role and appropriate chat access
                if not user_perms.is_player:
                    return False
                
                # Must be in main chat or leadership chat
                return context.chat_type in [ChatType.MAIN, ChatType.LEADERSHIP]
            
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
    
    async def get_available_commands(self, context: PermissionContext) -> List[str]:
        """
        Get list of available commands for a user in the given context.
        
        This is used by the help system to show appropriate commands.
        """
        try:
            available_commands = []
            
            # Always available
            available_commands.extend([
                "/help",
                "/start"
            ])
            
            # Check each permission level
            if await self.can_execute_command(PermissionLevel.PLAYER, context):
                available_commands.extend([
                    "/list",
                    "/myinfo",
                    "/update",
                    "/status",
                    "/register",
                    "/listmatches",
                    "/getmatch",
                    "/stats",
                    "/payment_status",
                    "/pending_payments",
                    "/payment_history",
                    "/payment_help",
                    "/financial_dashboard",
                    "/attend",
                    "/unattend"
                ])
            
            if await self.can_execute_command(PermissionLevel.LEADERSHIP, context):
                available_commands.extend([
                    "/add",
                    "/remove",
                    "/approve",
                    "/reject",
                    "/pending",
                    "/checkfa",
                    "/dailystatus",
                    "/background",
                    "/remind",
                    "/newmatch",
                    "/updatematch",
                    "/deletematch",
                    "/record_result",
                    "/invitelink",
                    "/broadcast",
                    "/create_match_fee",
                    "/create_membership_fee",
                    "/create_fine",
                    "/payment_stats",
                    "/announce",
                    "/injure",
                    "/suspend",
                    "/recover",
                    "/refund_payment",
                    "/record_expense"
                ])
            
            if await self.can_execute_command(PermissionLevel.ADMIN, context):
                available_commands.extend([
                    "/approve",
                    "/reject",
                    "/pending",
                    "/checkfa",
                    "/dailystatus",
                    "/backgroundtasks",
                    "/remind",
                    "/promote",
                    "/newmatch",
                    "/updatematch",
                    "/deletematch",
                    "/record_result",
                    "/invitelink",
                    "/broadcast",
                    "/create_match_fee",
                    "/create_membership_fee",
                    "/create_fine",
                    "/payment_stats",
                    "/announce",
                    "/injure",
                    "/suspend",
                    "/recover",
                    "/refund_payment",
                    "/record_expense"
                ])
            
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
                    return f"""❌ **Access Denied**

🔒 This command requires player access.
💡 Contact your team admin for access.

Your Role: {', '.join(user_perms.roles) if user_perms.roles else 'None'}"""
                else:
                    return f"""❌ **Access Denied**

🔒 Player commands are only available in main chat or leadership chat.
💡 Please use the appropriate team chat for this function."""
            
            elif permission_level == PermissionLevel.LEADERSHIP:
                if context.chat_type != ChatType.LEADERSHIP:
                    return f"""❌ **Access Denied**

🔒 Leadership commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""
                else:
                    return f"""❌ **Access Denied**

🔒 This command requires leadership access.
💡 Contact your team admin for access.

Your Role: {', '.join(user_perms.roles) if user_perms.roles else 'None'}"""
            
            elif permission_level == PermissionLevel.ADMIN:
                if context.chat_type != ChatType.LEADERSHIP:
                    return f"""❌ **Access Denied**

🔒 Admin commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""
                else:
                    return f"""❌ **Access Denied**

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
    
    async def handle_last_admin_leaving(self, team_id: str) -> Optional[str]:
        """Handle when the last admin leaves - promote longest-tenured leadership member."""
        return await self.team_member_service.handle_last_admin_leaving(team_id)


# Global instance for easy access
_permission_service: Optional[PermissionService] = None


def get_permission_service(firebase_client: FirebaseClient = None) -> PermissionService:
    """Get the global permission service instance."""
    global _permission_service
    if _permission_service is None:
        if firebase_client is None:
            firebase_client = FirebaseClient()
        _permission_service = PermissionService(firebase_client)
    return _permission_service 