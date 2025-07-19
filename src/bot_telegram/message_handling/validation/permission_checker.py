"""
Permission Checker

This module provides permission checking logic for messages.
"""

import logging
from typing import Tuple
from core.context_manager import UserContext

logger = logging.getLogger(__name__)


class PermissionChecker:
    """Handles permission checking for messages."""
    
    @staticmethod
    def check_user_registration(user_context: UserContext) -> Tuple[bool, str]:
        """Check if user is registered."""
        if not user_context.is_registered_player:
            return False, "User not registered"
        return True, "User registered"
    
    @staticmethod
    def check_chat_permissions(user_context: UserContext) -> Tuple[bool, str]:
        """Check chat-based permissions using centralized permission service."""
        try:
            from features.system_infrastructure.domain.services.permission_service import (
                get_permission_service, PermissionContext
            )
            from enums import ChatType
            
            permission_service = get_permission_service()
            permission_context = PermissionContext(
                user_id=user_context.user_id,
                team_id=user_context.team_id or "KAI",  # Default team ID
                chat_id=user_context.chat_id,
                chat_type=ChatType.LEADERSHIP if user_context.is_leadership_chat else ChatType.MAIN,
                username=user_context.username
            )
            
            # Check if user has any permissions in this context
            user_perms = permission_service.get_user_permissions(user_context.user_id, permission_context.team_id)
            
            if user_perms.roles or user_context.is_registered_player:
                return True, "Chat permissions valid"
            else:
                return False, "No permissions in this chat"
                
        except Exception as e:
            logger.error(f"Error checking chat permissions: {e}")
            return True, "Chat permissions valid (fallback)"
    
    @staticmethod
    def check_command_permissions(command_name: str, user_context: UserContext) -> Tuple[bool, str]:
        """Check command-specific permissions using centralized permission service."""
        try:
            from features.system_infrastructure.domain.services.permission_service import (
                get_permission_service, PermissionContext
            )
            from enums import ChatType, PermissionLevel
            
            # Map command names to permission levels
            command_permissions = {
                # Public commands
                "/help": PermissionLevel.PUBLIC,
                "/start": PermissionLevel.PUBLIC,
                
                # Player commands
                "/list": PermissionLevel.PLAYER,
                "/myinfo": PermissionLevel.PLAYER,
                "/update": PermissionLevel.PLAYER,
                "/status": PermissionLevel.PLAYER,
                "/register": PermissionLevel.PLAYER,
                "/listmatches": PermissionLevel.PLAYER,
                "/getmatch": PermissionLevel.PLAYER,
                "/stats": PermissionLevel.PLAYER,
                "/payment_status": PermissionLevel.PLAYER,
                "/pending_payments": PermissionLevel.PLAYER,
                "/payment_history": PermissionLevel.PLAYER,
                "/payment_help": PermissionLevel.PLAYER,
                "/financial_dashboard": PermissionLevel.PLAYER,
                "/attend": PermissionLevel.PLAYER,
                "/unattend": PermissionLevel.PLAYER,
                
                # Leadership commands
                "/add": PermissionLevel.LEADERSHIP,
                "/remove": PermissionLevel.LEADERSHIP,
                "/approve": PermissionLevel.LEADERSHIP,
                "/reject": PermissionLevel.LEADERSHIP,
                "/pending": PermissionLevel.LEADERSHIP,
                "/checkfa": PermissionLevel.LEADERSHIP,
                "/dailystatus": PermissionLevel.LEADERSHIP,
                "/background": PermissionLevel.LEADERSHIP,
                "/remind": PermissionLevel.LEADERSHIP,
                "/newmatch": PermissionLevel.LEADERSHIP,
                "/updatematch": PermissionLevel.LEADERSHIP,
                "/deletematch": PermissionLevel.LEADERSHIP,
                "/record_result": PermissionLevel.LEADERSHIP,
                "/invitelink": PermissionLevel.LEADERSHIP,
                "/broadcast": PermissionLevel.LEADERSHIP,
                "/create_match_fee": PermissionLevel.LEADERSHIP,
                "/create_membership_fee": PermissionLevel.LEADERSHIP,
                "/create_fine": PermissionLevel.LEADERSHIP,
                "/payment_stats": PermissionLevel.LEADERSHIP,
                "/announce": PermissionLevel.LEADERSHIP,
                "/injure": PermissionLevel.LEADERSHIP,
                "/suspend": PermissionLevel.LEADERSHIP,
                "/recover": PermissionLevel.LEADERSHIP,
                "/refund_payment": PermissionLevel.LEADERSHIP,
                "/record_expense": PermissionLevel.LEADERSHIP,
                
                # Admin commands
                "/promote": PermissionLevel.ADMIN,
            }
            
            permission_level = command_permissions.get(command_name, PermissionLevel.PLAYER)
            
            permission_service = get_permission_service()
            permission_context = PermissionContext(
                user_id=user_context.user_id,
                team_id=user_context.team_id or "KAI",  # Default team ID
                chat_id=user_context.chat_id,
                chat_type=ChatType.LEADERSHIP if user_context.is_leadership_chat else ChatType.MAIN,
                username=user_context.username
            )
            
            can_execute = permission_service.can_execute_command(permission_level, permission_context)
            
            if can_execute:
                return True, "Command permissions valid"
            else:
                return False, f"Command {command_name} requires {permission_level.value} permission"
                
        except Exception as e:
            logger.error(f"Error checking command permissions: {e}")
            return True, "Command permissions valid (fallback)"
    
    @staticmethod
    def check_feature_permissions(feature: str, user_context: UserContext) -> Tuple[bool, str]:
        """Check feature-specific permissions."""
        feature_permissions = {
            "player_management": ["leadership", "admin"],
            "match_management": ["leadership", "admin"],
            "payment_management": ["leadership", "admin"],
            "system_administration": ["admin"],
            "basic_queries": ["public", "player", "leadership", "admin"]
        }
        
        required_permissions = feature_permissions.get(feature, ["player"])
        
        # Check if user has any of the required permissions
        for permission in required_permissions:
            if permission == "public":
                return True, "Feature accessible to public"
            
            # Check user's actual permissions (simplified)
            if user_context.is_registered_player and permission == "player":
                return True, "Feature accessible to players"
            
            if user_context.is_leadership_chat and permission in ["leadership", "admin"]:
                return True, "Feature accessible to leadership"
        
        return False, f"Feature {feature} requires {', '.join(required_permissions)} permission" 