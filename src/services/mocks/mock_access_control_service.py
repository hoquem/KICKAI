"""
Mock Access Control Service

This module provides a mock implementation of the AccessControlService interface
for testing purposes.
"""

from typing import Dict, Any, List, Optional
import logging

from ..interfaces.access_control_service_interface import IAccessControlService, UserRole, ChatType


class MockAccessControlService(IAccessControlService):
    """Mock implementation of AccessControlService for testing."""
    
    def __init__(self):
        self._user_roles: Dict[str, Dict[str, UserRole]] = {}
        self._chat_types: Dict[str, ChatType] = {}
        self._user_permissions: Dict[str, Dict[str, List[str]]] = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_user_role(self, user_id: str, team_id: str) -> UserRole:
        """Get the role of a user in a team."""
        team_roles = self._user_roles.get(team_id, {})
        role = team_roles.get(user_id, UserRole.UNKNOWN)
        self.logger.info(f"Mock: User {user_id} role in team {team_id}: {role}")
        return role
    
    async def can_execute_command(self, command: str, user_id: str, 
                                chat_id: str, team_id: str) -> bool:
        """Check if a user can execute a specific command."""
        user_role = await self.get_user_role(user_id, team_id)
        chat_type = await self.get_chat_type(chat_id)
        
        # Simple mock logic
        if user_role == UserRole.ADMIN:
            return True
        elif user_role == UserRole.CAPTAIN and chat_type == ChatType.LEADERSHIP:
            return True
        elif user_role == UserRole.PLAYER and chat_type == ChatType.MAIN:
            return command in ["/myinfo", "/status", "/help"]
        
        self.logger.info(f"Mock: User {user_id} can execute {command}: False")
        return False
    
    async def get_chat_type(self, chat_id: str) -> ChatType:
        """Get the type of a chat."""
        chat_type = self._chat_types.get(chat_id, ChatType.MAIN)
        self.logger.info(f"Mock: Chat {chat_id} type: {chat_type}")
        return chat_type
    
    async def is_leadership_chat(self, chat_id: str) -> bool:
        """Check if a chat is a leadership chat."""
        chat_type = await self.get_chat_type(chat_id)
        return chat_type == ChatType.LEADERSHIP
    
    async def get_user_permissions(self, user_id: str, team_id: str) -> List[str]:
        """Get the permissions of a user in a team."""
        team_permissions = self._user_permissions.get(team_id, {})
        permissions = team_permissions.get(user_id, [])
        self.logger.info(f"Mock: User {user_id} permissions in team {team_id}: {permissions}")
        return permissions
    
    def set_user_role(self, user_id: str, team_id: str, role: UserRole):
        """Set a user's role for testing."""
        if team_id not in self._user_roles:
            self._user_roles[team_id] = {}
        self._user_roles[team_id][user_id] = role
    
    def set_chat_type(self, chat_id: str, chat_type: ChatType):
        """Set a chat's type for testing."""
        self._chat_types[chat_id] = chat_type
    
    def set_user_permissions(self, user_id: str, team_id: str, permissions: List[str]):
        """Set a user's permissions for testing."""
        if team_id not in self._user_permissions:
            self._user_permissions[team_id] = {}
        self._user_permissions[team_id][user_id] = permissions
    
    def reset(self):
        """Reset the mock service state."""
        self._user_roles.clear()
        self._chat_types.clear()
        self._user_permissions.clear()
        self.logger.info("Mock: Access control service reset") 