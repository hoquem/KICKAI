"""
Access Control Service for KICKAI

This service handles access control and permissions for team members.
"""

import logging
from typing import List
from database.models_improved import TeamMember
from core.exceptions import AccessDeniedError

logger = logging.getLogger(__name__)


class AccessControlService:
    """Service for managing access control and permissions."""
    
    def __init__(self):
        self.leadership_roles = {'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer'}
        logger.info("✅ AccessControlService initialized")
    
    def has_permission(self, member: TeamMember, permission: str) -> bool:
        """Check if a team member has a specific permission."""
        try:
            # Check if member has any leadership role
            if any(role in self.leadership_roles for role in member.roles):
                return True
            
            # Add specific permission checks here
            if permission == "view_team":
                return True
            elif permission == "edit_team":
                return "captain" in member.roles or "manager" in member.roles
            elif permission == "manage_players":
                return "captain" in member.roles or "manager" in member.roles
            elif permission == "access_leadership_chat":
                return member.chat_access.get('leadership_chat', False)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking permission: {e}")
            return False
    
    def require_permission(self, member: TeamMember, permission: str) -> None:
        """Require a specific permission, raise AccessDeniedError if not granted."""
        if not self.has_permission(member, permission):
            raise AccessDeniedError(f"Access denied: {permission} permission required")
    
    def get_accessible_chats(self, member: TeamMember) -> List[str]:
        """Get list of chat types the member has access to."""
        accessible_chats = []
        
        if member.chat_access.get('general_chat', True):
            accessible_chats.append('general_chat')
        
        if member.chat_access.get('leadership_chat', False):
            accessible_chats.append('leadership_chat')
        
        if member.chat_access.get('match_chat', False):
            accessible_chats.append('match_chat')
        
        return accessible_chats
    
    def is_leadership_member(self, member: TeamMember) -> bool:
        """Check if a member has any leadership role."""
        return any(role in self.leadership_roles for role in member.roles)
    
    def can_manage_team(self, member: TeamMember) -> bool:
        """Check if a member can manage team settings."""
        return "captain" in member.roles or "manager" in member.roles or "admin" in member.roles
    
    def can_manage_players(self, member: TeamMember) -> bool:
        """Check if a member can manage players."""
        return "captain" in member.roles or "manager" in member.roles or "coach" in member.roles
    
    def can_view_sensitive_data(self, member: TeamMember) -> bool:
        """Check if a member can view sensitive team data."""
        return self.is_leadership_member(member)
    
    def validate_role_assignment(self, current_member: TeamMember, target_role: str) -> bool:
        """Validate if a member can assign a specific role."""
        # Only captains and managers can assign roles
        if not self.can_manage_team(current_member):
            return False
        
        # Prevent assigning admin role unless current member is admin
        if target_role == "admin" and "admin" not in current_member.roles:
            return False
        
        return True
    
    def is_leadership_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if a chat ID corresponds to the leadership chat for a team."""
        try:
            # Check against environment variables for known chat IDs
            import os
            from core.settings import get_settings
            
            settings = get_settings()
            
            # Check if this is the leadership chat
            if str(settings.telegram_leadership_chat_id) == str(chat_id):
                return True
            
            # Fallback to environment variable
            leadership_chat_id = os.getenv("TELEGRAM_LEADERSHIP_CHAT_ID")
            if leadership_chat_id:
                return str(chat_id) == str(leadership_chat_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking leadership chat: {e}")
            return False
    
    def is_main_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if a chat ID corresponds to the main chat for a team."""
        try:
            # Check against environment variables for known chat IDs
            import os
            from core.settings import get_settings
            
            settings = get_settings()
            
            # Check if this is the main chat
            if str(settings.telegram_main_chat_id) == str(chat_id):
                return True
            
            # Fallback to environment variable
            main_chat_id = os.getenv("TELEGRAM_MAIN_CHAT_ID")
            if main_chat_id:
                return str(chat_id) == str(main_chat_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking main chat: {e}")
            return False
    
    def _is_leadership_chat_by_name(self, chat_id: str) -> bool:
        """Fallback method to check if chat is leadership by name pattern."""
        try:
            # This is a fallback method - in practice, we'd check chat title
            # For now, return False as default
            return False
        except Exception as e:
            logger.error(f"Error in leadership chat name check: {e}")
            return False 