#!/usr/bin/env python3
"""
Simplified Team Member Service

This module provides simplified team member management functionality
for the new /addmember command that only requires name and phone number.
"""
from typing import Optional

from datetime import datetime

from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.features.team_administration.domain.repositories.team_repository_interface import (
    TeamRepositoryInterface,
)
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.constants import (
    DEFAULT_MEMBER_ROLE,
    DEFAULT_MEMBER_STATUS,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
)
from kickai.utils.simple_id_generator import generate_simple_team_member_id


class SimplifiedTeamMemberService:
    """Simplified service for team member management."""

    def __init__(self, team_repository: TeamRepositoryInterface):
        self.team_repository = team_repository
        self.logger = logger

    async def add_team_member(
        self, name: str, phone: str, role: str = None, team_id: str = None
    ) -> tuple[bool, str]:
        """
        Add a new team member with simplified ID generation.

        Args:
            name: Team member's full name
            phone: Team member's phone number
            role: Team member's role (optional, can be set later)
            team_id: Team ID

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if team member already exists
            existing_member = await self.get_team_member_by_phone(phone=phone, team_id=team_id)
            if existing_member:
                return False, ERROR_MESSAGES["MEMBER_EXISTS"].format(phone=phone, team_id=team_id)

            # Get existing team member IDs for collision detection
            existing_members = await self.team_repository.get_team_members_by_team(team_id)
            existing_ids = {member.user_id for member in existing_members if member.user_id}

            # Generate simple team member ID
            member_id = generate_simple_team_member_id(name, team_id, existing_ids)

            # Create team member entity
            team_member = TeamMember(
                user_id=member_id,
                team_id=team_id,
                full_name=name,
                phone_number=phone,
                role=role or DEFAULT_MEMBER_ROLE,
                status=DEFAULT_MEMBER_STATUS,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Save to repository
            await self.team_repository.create_team_member(team_member)

            return True, SUCCESS_MESSAGES["MEMBER_ADDED"].format(name=name, member_id=member_id)
        except Exception as e:
            logger.error(f"Error adding team member {name}: {e}")
            return False, f"❌ Failed to add team member: {e!s}"

    async def get_team_member_by_phone(self, phone: str, team_id: str) -> Optional[TeamMember]:
        """Get team member by phone number."""
        try:
            members = await self.team_repository.get_team_members_by_team(team_id)
            for member in members:
                if member.phone_number == phone:
                    return member
            return None
        except Exception as e:
            logger.error(f"Error getting team member by phone {phone}: {e}")
            return None

    async def create_team_member_invite_link(
        self, name: str, phone: str, role: str, team_id: str
    ) -> dict:
        """
        Create an invite link for a team member to join the leadership chat.

        Args:
            name: Team member's name
            phone: Team member's phone number
            role: Team member's role
            team_id: Team ID

        Returns:
            Dict containing invite link details
        """
        try:
            # Get team configuration
            team_service = get_container().get_service(TeamService)
            team = await team_service.get_team(team_id=team_id)

            if not team or not team.leadership_chat_id:
                raise ValueError("Team not found or no leadership chat configured")

            # Get invite link service
            invite_service = get_container().get_service(InviteLinkService)
            if not invite_service:
                raise ValueError("Invite link service not available")

            # Create invite link
            invite_result = await invite_service.create_team_member_invite_link(
                team_id=team_id,
                member_name=name,
                member_phone=phone,
                member_role=role,
                leadership_chat_id=team.leadership_chat_id,
            )

            return {
                "success": True,
                "invite_link": invite_result["invite_link"],
                "member_id": invite_result.get("member_id"),
                "expires_at": invite_result["expires_at"],
            }

        except Exception as e:
            logger.error(f"Error creating team member invite link: {e}")
            return {"success": False, "error": str(e)}
