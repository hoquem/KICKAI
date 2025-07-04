"""
Mock Team Member Service

This module provides a mock implementation of the TeamMemberService interface
for testing purposes.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..interfaces.team_member_service_interface import ITeamMemberService
from ...database.models import TeamMember


class MockTeamMemberService(ITeamMemberService):
    """Mock implementation of TeamMemberService for testing."""
    
    def __init__(self):
        self._members: Dict[str, List[TeamMember]] = {}
        self.logger = logging.getLogger(__name__)
    
    async def add_member(self, team_id: str, user_id: str, role: str = "player",
                        permissions: Optional[List[str]] = None) -> TeamMember:
        """Add a member to a team."""
        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            roles=[role],
            permissions=permissions or [],
            joined_at=datetime.now()
        )
        
        if team_id not in self._members:
            self._members[team_id] = []
        
        self._members[team_id].append(member)
        self.logger.info(f"Mock: Added member {user_id} to team {team_id}")
        return member
    
    async def remove_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        if team_id not in self._members:
            return False
        
        members = self._members[team_id]
        for i, member in enumerate(members):
            if member.user_id == user_id:
                del members[i]
                self.logger.info(f"Mock: Removed member {user_id} from team {team_id}")
                return True
        
        return False
    
    async def get_member(self, team_id: str, user_id: str) -> Optional[TeamMember]:
        """Get a team member by user ID."""
        if team_id not in self._members:
            return None
        
        for member in self._members[team_id]:
            if member.user_id == user_id:
                return member
        
        return None
    
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        members = self._members.get(team_id, [])
        self.logger.info(f"Mock: Retrieved {len(members)} members for team {team_id}")
        return members
    
    async def update_member_role(self, team_id: str, user_id: str, new_role: str) -> TeamMember:
        """Update the role of a team member."""
        member = await self.get_member(team_id, user_id)
        if not member:
            raise ValueError(f"Member not found: {user_id}")
        
        member.roles = [new_role]
        member.updated_at = datetime.now()
        self.logger.info(f"Mock: Updated member {user_id} role to {new_role}")
        return member
    
    async def update_member_permissions(self, team_id: str, user_id: str, 
                                      permissions: List[str]) -> TeamMember:
        """Update the permissions of a team member."""
        member = await self.get_member(team_id, user_id)
        if not member:
            raise ValueError(f"Member not found: {user_id}")
        
        member.permissions = permissions
        member.updated_at = datetime.now()
        self.logger.info(f"Mock: Updated member {user_id} permissions")
        return member
    
    def reset(self):
        """Reset the mock service state."""
        self._members.clear()
        self.logger.info("Mock: Team member service reset") 