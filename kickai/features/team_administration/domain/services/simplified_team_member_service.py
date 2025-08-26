from typing import Dict, Optional, Tuple
#!/usr/bin/env python3
"""
Simplified Team Member Service

This module provides simplified team member management functionality
for the new /addmember command that only requires name and phone number.
"""

from datetime import datetime

from loguru import logger

from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.features.team_administration.domain.repositories.team_member_repository_interface import (
    TeamMemberRepositoryInterface,
)
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.features.team_administration.domain.exceptions import (
    TeamNotFoundError,
    TeamServiceUnavailableError,
    LeadershipChatNotConfiguredError,
    InviteLinkServiceUnavailableError,
    InviteLinkCreationError,
)
from kickai.utils.constants import (
    DEFAULT_MEMBER_ROLE,
    DEFAULT_MEMBER_STATUS,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
)
from kickai.utils.simple_id_generator import generate_simple_team_member_id


class SimplifiedTeamMemberService:
    """Simplified service for team member management."""

    def __init__(self, team_member_repository: TeamMemberRepositoryInterface, team_service: TeamService, invite_service: InviteLinkService):
        self.team_member_repository = team_member_repository
        self.team_service = team_service
        self.invite_service = invite_service
        self.logger = logger

    async def add_team_member_or_get_existing(
        self, name: str, phone: str, role: str = None, team_id: str = None, email: str = None
    ) -> Tuple[bool, str, Optional[TeamMember]]:
        """
        Add a new team member with simplified ID generation, or return existing member if duplicate.

        Args:
            name: Team member's full name
            phone: Team member's phone number
            role: Team member's role (optional, can be set later)
            team_id: Team ID
            email: Team member's email address (optional)

        Returns:
            Tuple of (success, message, existing_member_or_none)
        """
        try:
            # Check if team member already exists
            existing_member = await self.get_team_member_by_phone(phone=phone, team_id=team_id)
            if existing_member:
                # Return existing member for invite link generation
                return True, f"Team member {existing_member.name} already exists with ID: {existing_member.member_id}", existing_member

            # Get existing team member IDs for collision detection
            existing_members = await self.team_member_repository.get_team_members(team_id)
            existing_ids = {member.member_id for member in existing_members if member.member_id}

            # Generate simple team member ID
            member_id = generate_simple_team_member_id(name, team_id, existing_ids)

            # Create team member entity
            team_member = TeamMember(
                member_id=member_id,
                team_id=team_id,
                name=name,
                phone_number=phone,
                email=email,
                role=role or DEFAULT_MEMBER_ROLE,
                status=DEFAULT_MEMBER_STATUS,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Save to repository
            await self.team_member_repository.create_team_member(team_member)

            return True, SUCCESS_MESSAGES["MEMBER_ADDED"].format(name=name, member_id=member_id), team_member
        except Exception as e:
            logger.error(f"Error adding team member {name}: {e}")
            return False, f"❌ Failed to add team member: {e!s}", None

    async def add_team_member(
        self, name: str, phone: str, role: str = None, team_id: str = None, email: str = None
    ) -> Tuple[bool, str]:
        """
        Backward compatibility method - adds team member or returns error for duplicates.
        
        Args:
            name: Team member's full name
            phone: Team member's phone number
            role: Team member's role (optional, can be set later)
            team_id: Team ID
            email: Team member's email address (optional)

        Returns:
            Tuple of (success, message)
        """
        success, message, existing_member = await self.add_team_member_or_get_existing(name, phone, role, team_id, email)
        return success, message

    async def get_team_member_by_phone(self, phone: str, team_id: str) -> Optional[TeamMember]:
        """Get team member by phone number using phonenumbers library for flexible matching."""
        try:
            # Use phonenumbers library for proper phone matching
            from kickai.utils.phone_utils import get_phone_variants, normalize_phone

            # Normalize the search phone number
            normalized_search_phone = normalize_phone(phone)
            if not normalized_search_phone:
                logger.warning(f"Could not normalize phone number: {phone}")
                return None

            # Get all possible variants of the search phone number
            search_variants = get_phone_variants(phone)

            members = await self.team_member_repository.get_team_members(team_id)

            for member in members:
                if not member.phone_number:
                    continue

                # Normalize the member's phone number
                normalized_member_phone = normalize_phone(member.phone_number)
                if not normalized_member_phone:
                    continue

                # Check for exact match with normalized numbers
                if normalized_member_phone == normalized_search_phone:
                    logger.info(
                        f"Found team member by phone: {member.name} ({normalized_member_phone})"
                    )
                    return member

                # Check for match with any variant
                member_variants = get_phone_variants(member.phone_number)
                for search_variant in search_variants:
                    if search_variant in member_variants:
                        logger.info(
                            f"Found team member by phone variant: {member.name} ({normalized_member_phone})"
                        )
                        return member

            logger.info(
                f"No team member found for phone: {phone} (normalized: {normalized_search_phone})"
            )
            return None

        except Exception as e:
            logger.error(f"Error getting team member by phone {phone}: {e}")
            return None

    async def create_team_member_invite_link(
        self, name: str, phone: str, role: str, team_id: str, member_id: str
    ) -> dict:
        """
        Create an invite link for a team member to join the leadership chat.

        Args:
            name: Team member's name
            phone: Team member's phone number
            role: Team member's role
            team_id: Team ID
            member_id: Team member's ID (M01AB format)

        Returns:
            Dict containing invite link details
        """
        try:
            logger.info(f"🔗 Starting invite link creation for {name} (team: {team_id})")
            
            # Get team configuration
            logger.debug(f"🔍 Looking up team configuration for team_id: {team_id}")
            team = await self.team_service.get_team(team_id=team_id)

            if not team:
                raise TeamNotFoundError(team_id)
            
            if not team.leadership_chat_id:
                raise LeadershipChatNotConfiguredError(team_id)
            
            logger.info(f"✅ Team found: {team.name}, leadership_chat_id: {team.leadership_chat_id}")

            logger.info(f"🔗 Creating invite link via service for member: {name}")

            # Create invite link
            invite_result = await self.invite_service.create_team_member_invite_link(
                team_id=team_id,
                member_id=member_id,  # Pass real member_id
                member_name=name,
                member_phone=phone,
                member_role=role,
                leadership_chat_id=team.leadership_chat_id,
            )

            logger.info(f"✅ Invite link created successfully for {name}")
            return {
                "success": True,
                "invite_link": invite_result["invite_link"],
                "member_id": invite_result.get("member_id"),
                "expires_at": invite_result["expires_at"],
            }

        except (TeamServiceUnavailableError, TeamNotFoundError, LeadershipChatNotConfiguredError, 
                InviteLinkServiceUnavailableError) as e:
            logger.error(f"❌ Error creating team member invite link for {name}: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"❌ Unexpected error creating team member invite link for {name}: {e}")
            logger.exception("Full stack trace:")
            raise InviteLinkCreationError(str(e))
