from typing import Optional, Set, List
#!/usr/bin/env python3
"""
Team Member Service

This module provides team member management functionality.
Team members represent administrative/management roles within a team.
This is separate from Players who represent football players.
"""

from datetime import datetime

from loguru import logger

from ..entities.team_member import TeamMember
from ..repositories.team_repository_interface import TeamRepositoryInterface


class TeamMemberService:
    """Service for managing team members (administrative/management roles)."""

    def __init__(self, team_repository: TeamRepositoryInterface):
        self.team_repository = team_repository
        self.logger = logger

    async def create_team_member(self, team_member: TeamMember) -> str:
        """Create a new team member."""
        try:
            # Validate team member data
            self._validate_team_member(team_member)

            # Set timestamps
            team_member.created_at = datetime.utcnow()
            team_member.updated_at = datetime.utcnow()

            # Save to repository
            member_id = await self.team_repository.create_team_member(team_member)
            self.logger.info(f"✅ Created team member: {team_member.name} ({member_id})")
            return member_id

        except Exception as e:
            self.logger.error(f"❌ Failed to create team member: {e}")
            raise

    async def get_team_member_by_id(self, member_id: str, team_id: str = None) -> Optional[TeamMember]:
        """Get a team member by ID.
        
        Args:
            member_id: The member ID to search for
            team_id: Optional team ID to narrow the search for better performance
        """
        try:
            return await self.team_repository.get_team_member_by_id(member_id, team_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by ID {member_id}: {e}")
            return None

    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by Telegram ID and team."""
        try:
            return await self.team_repository.get_team_member_by_telegram_id(team_id, telegram_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by Telegram ID {telegram_id}: {e}")
            return None

    async def get_team_member_by_phone(self, phone: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by phone number and team."""
        try:
            return await self.team_repository.get_team_member_by_phone(phone, team_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by phone {phone}: {e}")
            return None

    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all team members for a team."""
        try:
            members = await self.team_repository.get_team_members(team_id)
            self.logger.info(f"📊 Retrieved {len(members)} team members for team {team_id}")
            return members
        except Exception as e:
            self.logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []

    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members by specific role."""
        try:
            all_members = await self.get_team_members_by_team(team_id)
            return [member for member in all_members if member.role == role]
        except Exception as e:
            self.logger.error(f"❌ Failed to get team members by role {role}: {e}")
            return []

    async def update_team_member(self, team_member: TeamMember) -> bool:
        """Update a team member."""
        try:
            team_member.updated_at = datetime.utcnow()
            success = await self.team_repository.update_team_member(team_member)
            if success:
                self.logger.info(f"✅ Updated team member: {team_member.name}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Failed to update team member: {e}")
            return False

    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        try:
            success = await self.team_repository.delete_team_member(member_id)
            if success:
                self.logger.info(f"✅ Deleted team member: {member_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Failed to delete team member {member_id}: {e}")
            return False

    async def add_role_to_member(self, telegram_id: str, team_id: str, role: str) -> bool:
        """Add a role to a team member."""
        try:
            member = await self.get_team_member_by_telegram_id(telegram_id, team_id)
            if not member:
                self.logger.warning(f"⚠️ Team member not found: {telegram_id}")
                return False

            if member.role != role:
                member.role = role
                return await self.update_team_member(member)
            else:
                self.logger.info(f"ℹ️ Role {role} already exists for member {telegram_id}")
                return True

        except Exception as e:
            self.logger.error(f"❌ Failed to add role {role} to member {telegram_id}: {e}")
            return False

