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
            self.logger.info(f"✅ Created team member: {team_member.full_name} ({member_id})")
            return member_id

        except Exception as e:
            self.logger.error(f"❌ Failed to create team member: {e}")
            raise

    async def get_team_member_by_id(self, member_id: str) -> TeamMember | None:
        """Get a team member by ID."""
        try:
            return await self.team_repository.get_team_member_by_id(member_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by ID {member_id}: {e}")
            return None

    async def get_team_member_by_telegram_id(self, user_id: str, team_id: str) -> TeamMember | None:
        """Get a team member by Telegram ID and team."""
        try:
            return await self.team_repository.get_team_member_by_telegram_id(team_id, user_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by Telegram ID {user_id}: {e}")
            return None

    async def get_team_members_by_team(self, team_id: str) -> list[TeamMember]:
        """Get all team members for a team."""
        try:
            members = await self.team_repository.get_team_members(team_id)
            self.logger.info(f"📊 Retrieved {len(members)} team members for team {team_id}")
            return members
        except Exception as e:
            self.logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []

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
            success = await self.team_repository.update_team_member(team_member)
            if success:
                self.logger.info(f"✅ Updated team member: {team_member.full_name}")
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

    async def add_role_to_member(self, user_id: str, team_id: str, role: str) -> bool:
        """Add a role to a team member."""
        try:
            member = await self.get_team_member_by_telegram_id(user_id, team_id)
            if not member:
                self.logger.warning(f"⚠️ Team member not found: {user_id}")
                return False

            if member.role != role:
                member.role = role
                return await self.update_team_member(member)
            else:
                self.logger.info(f"ℹ️ Role {role} already exists for member {user_id}")
                return True

        except Exception as e:
            self.logger.error(f"❌ Failed to add role {role} to member {user_id}: {e}")
            return False

    async def remove_role_from_member(self, user_id: str, team_id: str, role: str) -> bool:
        """Remove a role from a team member."""
        try:
            member = await self.get_team_member_by_telegram_id(user_id, team_id)
            if not member:
                self.logger.warning(f"⚠️ Team member not found: {user_id}")
                return False

            if member.role == role:
                member.role = "Team Member"  # Reset to default role
                return await self.update_team_member(member)
            else:
                self.logger.info(f"ℹ️ Role {role} not found for member {user_id}")
                return True

        except Exception as e:
            self.logger.error(f"❌ Failed to remove role {role} from member {user_id}: {e}")
            return False

    async def promote_to_admin(self, user_id: str, team_id: str, promoted_by: str) -> bool:
        """Promote a team member to admin role."""
        try:
            member = await self.get_team_member_by_telegram_id(user_id, team_id)
            if not member:
                self.logger.warning(f"⚠️ Team member not found: {user_id}")
                return False

            member.is_admin = True
            if member.role != "Club Administrator":
                member.role = "Club Administrator"

            success = await self.update_team_member(member)
            if success:
                self.logger.info(f"👑 Promoted {member.full_name} to admin by {promoted_by}")
            return success

        except Exception as e:
            self.logger.error(f"❌ Failed to promote member {user_id} to admin: {e}")
            return False

    async def is_first_user(self, team_id: str) -> bool:
        """Check if this would be the first user in the team."""
        try:
            members = await self.get_team_members_by_team(team_id)
            return len(members) == 0
        except Exception as e:
            self.logger.error(f"❌ Failed to check if first user for team {team_id}: {e}")
            return False

    async def get_my_status(self, user_id: str, team_id: str) -> str:
        """
        Get current user's team member status and information.

        Args:
            user_id: The user's Telegram ID
            team_id: The team ID

        Returns:
            User's team member status and information as a formatted string
        """
        try:
            team_member = await self.get_team_member_by_telegram_id(user_id, team_id)

            if team_member:
                return self._format_team_member_status(team_member)

            # User not found as team member
            return f"""❌ Team Member Not Found

🔍 User ID: {user_id}
🏢 Team ID: {team_id}

💡 You may need to be added as a team member by your team admin."""

        except Exception as e:
            self.logger.error(f"Error getting team member status for user {user_id}: {e}")
            return f"❌ Error retrieving your team member status: {e!s}"

    def _format_team_member_status(self, team_member: TeamMember) -> str:
        """Format team member status information."""
        role_text = team_member.role if team_member.role else "No role assigned"
        admin_status = "👑 Admin" if team_member.is_admin else "👤 Team Member"

        return f"""👥 Team Member Information

📋 Name: {team_member.full_name or team_member.first_name or "Not set"}
🔑 User ID: {team_member.user_id}
{admin_status}
🎭 Role: {role_text}
🏢 Team: {team_member.team_id}
📱 Phone: {team_member.phone_number or "Not set"}
📧 Email: {team_member.email or "Not set"}

📅 Joined: {team_member.created_at.strftime("%Y-%m-%d") if team_member.created_at else "Unknown"}
🔄 Updated: {team_member.updated_at.strftime("%Y-%m-%d") if team_member.updated_at else "Unknown"}"""

    def _validate_team_member(self, team_member: TeamMember) -> None:
        """Validate team member data."""
        if not team_member.team_id:
            raise ValueError("Team ID cannot be empty")
        if not team_member.user_id:
            raise ValueError("User ID cannot be empty")
        if not team_member.role:
            raise ValueError("Team member must have a role")

        # Validate that no "player" role exists (handled by Player entity)
        if team_member.role == "player":
            raise ValueError("Team members cannot have 'player' role - use Player entity instead")

        # Validate user_id format
        if not team_member.user_id.startswith("user_"):
            raise ValueError(
                f"Invalid user_id format: {team_member.user_id}. Must start with 'user_'"
            )

    # Synchronous methods for CrewAI tools
    def get_my_status_sync(self, user_id: str, team_id: str) -> str:
        """Synchronous version of get_my_status for CrewAI tools."""
        try:
            # Import here to avoid circular imports
            import asyncio
            
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.get_my_status(user_id, team_id))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(self.get_my_status(user_id, team_id))
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get status for user {user_id}: {e}")
            return f"❌ Error retrieving status: {e!s}"

    def get_team_members_by_team_sync(self, team_id: str) -> list[TeamMember]:
        """Synchronous version of get_team_members_by_team for CrewAI tools."""
        try:
            # Import here to avoid circular imports
            import asyncio
            
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.get_team_members_by_team(team_id))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(self.get_team_members_by_team(team_id))
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []

    def get_team_members_by_role_sync(self, team_id: str, role: str) -> list[TeamMember]:
        """Synchronous version of get_team_members_by_role for CrewAI tools."""
        try:
            # Import here to avoid circular imports
            import asyncio
            
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.get_team_members_by_role(team_id, role))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(self.get_team_members_by_role(team_id, role))
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get team members by role {role}: {e}")
            return []
