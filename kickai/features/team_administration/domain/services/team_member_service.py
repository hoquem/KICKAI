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
from ..repositories.team_member_repository_interface import TeamMemberRepositoryInterface


class TeamMemberService:
    """Service for managing team members (administrative/management roles)."""

    def __init__(self, team_member_repository: TeamMemberRepositoryInterface):
        self.team_member_repository = team_member_repository
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
            created_member = await self.team_member_repository.create_team_member(team_member)
            member_id = created_member.member_id
            self.logger.info(f"✅ Created team member: {team_member.name} ({member_id})")
            return member_id

        except Exception as e:
            self.logger.error(f"❌ Failed to create team member: {e}")
            raise

    async def get_team_member_by_id(self, member_id: str, team_id: str = None) -> TeamMember | None:
        """Get a team member by ID.

        Args:
            member_id: The member ID to search for
            team_id: Optional team ID to narrow the search for better performance
        """
        try:
            return await self.team_member_repository.get_team_member_by_id(member_id, team_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by ID {member_id}: {e}")
            return None

    async def get_team_member_by_telegram_id(
        self, telegram_id: int, team_id: str
    ) -> TeamMember | None:
        """Get a team member by Telegram ID and team."""
        try:
            return await self.team_member_repository.get_team_member_by_telegram_id(
                team_id, telegram_id
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by Telegram ID {telegram_id}: {e}")
            return None

    async def get_team_member_by_phone(self, phone: str, team_id: str) -> TeamMember | None:
        """Get a team member by phone number and team."""
        try:
            return await self.team_member_repository.get_team_member_by_phone(phone, team_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by phone {phone}: {e}")
            return None

    async def get_team_members_by_team(self, team_id: str) -> list[TeamMember]:
        """Get all team members for a team."""
        try:
            members = await self.team_member_repository.get_team_members(team_id)
            self.logger.info(f"📊 Retrieved {len(members)} team members for team {team_id}")
            return members
        except Exception as e:
            self.logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []

    async def get_team_members(self, team_id: str) -> list[TeamMember]:
        """Get all team members for a team (alias for get_team_members_by_team)."""
        return await self.get_team_members_by_team(team_id)

    async def get_team_members_by_role(self, team_id: str, role: str) -> list[TeamMember]:
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
            updated_member = await self.team_member_repository.update_team_member(team_member)
            success = updated_member is not None
            if success:
                self.logger.info(f"✅ Updated team member: {team_member.name}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Failed to update team member: {e}")
            return False

    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        try:
            success = await self.team_member_repository.delete_team_member(
                member_id, ""
            )  # team_id will be inferred from member_id
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

    async def find_team_member_by_identifier(self, identifier: str, team_id: str) -> TeamMember | None:
        """Find a team member by various identifiers (ID, name, phone, username)."""
        try:
            # First try by member ID
            try:
                member = await self.get_team_member_by_id(identifier, team_id)
                if member:
                    self.logger.info(f"✅ Found team member by ID: {identifier}")
                    return member
            except Exception:
                pass

            # Try by phone number
            try:
                member = await self.get_team_member_by_phone(identifier, team_id)
                if member:
                    self.logger.info(f"✅ Found team member by phone: {identifier}")
                    return member
            except Exception:
                pass

            # Try by telegram ID if it's numeric
            try:
                if identifier.isdigit():
                    telegram_id = int(identifier)
                    member = await self.get_team_member_by_telegram_id(telegram_id, team_id)
                    if member:
                        self.logger.info(f"✅ Found team member by telegram ID: {identifier}")
                        return member
            except Exception:
                pass

            # Finally, search by name or username
            try:
                all_members = await self.get_team_members_by_team(team_id)
                identifier_lower = identifier.lower()
                
                for member in all_members:
                    # Check name match
                    if member.name and identifier_lower in member.name.lower():
                        self.logger.info(f"✅ Found team member by name: {identifier}")
                        return member
                    
                    # Check username match (if available)
                    if hasattr(member, 'telegram_username') and member.telegram_username:
                        if identifier_lower in member.telegram_username.lower():
                            self.logger.info(f"✅ Found team member by username: {identifier}")
                            return member
                    
                    # Check username field (alternative field name)
                    if hasattr(member, 'username') and member.username:
                        if identifier_lower in member.username.lower():
                            self.logger.info(f"✅ Found team member by username: {identifier}")
                            return member

            except Exception as e:
                self.logger.warning(f"⚠️ Failed to search members by name/username: {e}")

            self.logger.info(f"🔍 No team member found for identifier: {identifier}")
            return None

        except Exception as e:
            self.logger.error(f"❌ Failed to find team member by identifier {identifier}: {e}")
            return None
