"""
Application layer adapter for user management operations.

This adapter implements the domain interface by wrapping the application layer services.
"""

import logging
from typing import List

from ..interfaces.user_management import IUserManagement


class UserManagementAdapter(IUserManagement):
    """Adapter that wraps user management services to implement domain interface."""
    
    def __init__(self, team_member_service, access_control_service):
        """Initialize with the required services."""
        self.team_member_service = team_member_service
        self.access_control_service = access_control_service
        self.logger = logging.getLogger(__name__)
    
    async def get_user_role(self, user_id: str, team_id: str) -> str:
        """Get the primary role of a user in a team."""
        try:
            member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            if member and member.roles:
                return member.roles[0]  # Return first role
            return 'player'
        except Exception as e:
            self.logger.error(f"Error getting user role: {e}")
            return 'player'  # Default to player
    
    async def get_user_roles(self, user_id: str, team_id: str) -> List[str]:
        """Get all roles of a user in a team."""
        try:
            member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            if member and member.roles:
                return member.roles
            return ['player']
        except Exception as e:
            self.logger.error(f"Error getting user roles: {e}")
            return ['player']
    
    async def is_user_in_team(self, user_id: str, team_id: str) -> bool:
        """Check if a user is a member of a team."""
        try:
            member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            return member is not None
        except Exception as e:
            self.logger.error(f"Error checking user team membership: {e}")
            return False
    
    async def is_leadership_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if a chat is a leadership chat for a team."""
        try:
            return self.access_control_service.is_leadership_chat(chat_id, team_id)
        except Exception as e:
            self.logger.error(f"Error checking leadership chat: {e}")
            return False 