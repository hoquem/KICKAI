"""
Team Member Service for KICKAI

This service handles all team member operations with dependency injection
and clean architecture principles.
"""

import logging
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass

from src.database.models_improved import TeamMember
from src.database.firebase_client import FirebaseClient
from src.core.exceptions import DatabaseError, ValidationError
from .interfaces.team_member_service_interface import ITeamMemberService

logger = logging.getLogger(__name__)


@dataclass
class TeamMemberServiceConfig:
    """Configuration for TeamMemberService."""
    require_roles: bool = True
    leadership_roles: set = None
    
    def __post_init__(self):
        if self.leadership_roles is None:
            self.leadership_roles = {'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer'}


class TeamMemberService(ITeamMemberService):
    """Service for managing team members with dependency injection."""
    
    def __init__(self, firebase_client: FirebaseClient, config: Optional[TeamMemberServiceConfig] = None):
        self.firebase_client = firebase_client
        self.config = config or TeamMemberServiceConfig()
        logger.info("✅ TeamMemberService initialized")
    
    async def create_team_member(self, team_member: TeamMember) -> str:
        """Create a new team member."""
        try:
            # Validate telegram_id uniqueness
            if team_member.telegram_id:
                existing = await self.get_team_member_by_telegram_id(team_member.telegram_id, team_member.team_id)
                if existing:
                    raise ValidationError(f"Team member with telegram_id {team_member.telegram_id} already exists")
            
            member_id = await self.firebase_client.create_team_member(team_member)
            logger.info(f"✅ Created team member: {team_member.user_id} with roles {team_member.roles}")
            return member_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create team member: {e}")
            raise DatabaseError(f"Failed to create team member: {str(e)}")
    
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        try:
            return await self.firebase_client.get_team_member(member_id)
        except Exception as e:
            logger.error(f"❌ Failed to get team member {member_id}: {e}")
            return None
    
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by telegram_id and team_id."""
        try:
            team_members = await self.firebase_client.get_team_members_by_team(team_id)
            for member in team_members:
                if member.telegram_id == telegram_id:
                    return member
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get team member by telegram_id {telegram_id}: {e}")
            return None
    
    async def update_team_member(self, team_member: TeamMember) -> bool:
        """Update a team member."""
        try:
            success = await self.firebase_client.update_team_member(team_member)
            if success:
                logger.info(f"✅ Updated team member: {team_member.user_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to update team member {team_member.user_id}: {e}")
            return False
    
    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        try:
            success = await self.firebase_client.delete_team_member(member_id)
            if success:
                logger.info(f"✅ Deleted team member: {member_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to delete team member {member_id}: {e}")
            return False
    
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all team members for a team."""
        try:
            return await self.firebase_client.get_team_members_by_team(team_id)
        except Exception as e:
            logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []
    
    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members by role."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            return [member for member in team_members if member.has_role(role)]
        except Exception as e:
            logger.error(f"❌ Failed to get team members by role {role}: {e}")
            return []
    
    async def get_leadership_members(self, team_id: str) -> List[TeamMember]:
        """Get all leadership members (with any leadership role)."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            return [member for member in team_members if member.has_any_leadership_role()]
        except Exception as e:
            logger.error(f"❌ Failed to get leadership members for team {team_id}: {e}")
            return []
    
    async def get_players(self, team_id: str) -> List[TeamMember]:
        """Get all team members who are players."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            return [member for member in team_members if member.is_player()]
        except Exception as e:
            logger.error(f"❌ Failed to get players for team {team_id}: {e}")
            return []
    
    async def add_role_to_member(self, member_id: str, role: str) -> bool:
        """Add a role to a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                return False
            
            if role not in member.roles:
                member.roles.append(role)
                member.updated_at = datetime.now()
                return await self.update_team_member(member)
            
            return True  # Role already exists
        except Exception as e:
            logger.error(f"❌ Failed to add role {role} to member {member_id}: {e}")
            return False
    
    async def remove_role_from_member(self, member_id: str, role: str) -> bool:
        """Remove a role from a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                return False
            
            if role in member.roles:
                member.roles.remove(role)
                member.updated_at = datetime.now()
                
                # Ensure member still has at least one role
                if not member.roles and self.config.require_roles:
                    raise ValidationError("Team member must have at least one role")
                
                return await self.update_team_member(member)
            
            return True  # Role doesn't exist
        except Exception as e:
            logger.error(f"❌ Failed to remove role {role} from member {member_id}: {e}")
            return False
    
    async def update_chat_access(self, member_id: str, chat_type: str, has_access: bool) -> bool:
        """Update chat access for a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                return False
            
            member.chat_access[chat_type] = has_access
            member.updated_at = datetime.now()
            return await self.update_team_member(member)
        except Exception as e:
            logger.error(f"❌ Failed to update chat access for member {member_id}: {e}")
            return False
    
    def is_leadership_role(self, role: str) -> bool:
        """Check if a role is a leadership role."""
        return role in self.config.leadership_roles
    
    def get_leadership_roles(self) -> set:
        """Get all leadership roles."""
        return self.config.leadership_roles.copy()
    
    async def validate_member_roles(self, member: TeamMember) -> List[str]:
        """Validate team member roles and return any issues."""
        issues = []
        
        # Check if member has at least one role
        if not member.roles and self.config.require_roles:
            issues.append("Team member must have at least one role")
        
        # Check for invalid roles
        invalid_roles = set(member.roles) - self.config.leadership_roles - {'player'}
        if invalid_roles:
            issues.append(f"Invalid roles: {invalid_roles}")
        
        return issues 