#!/usr/bin/env python3
"""
Team Member Management Service

Consolidated service for all team member operations to simplify tool dependencies
and provide a single interface for team member management workflows.
"""

from datetime import datetime
from typing import Optional, Tuple

from loguru import logger

from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.features.team_administration.domain.services.simplified_team_member_service import SimplifiedTeamMemberService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
from kickai.features.team_administration.domain.types import (
    TelegramUserId,
    TeamId,
    MemberId,
    PhoneNumber,
    TeamMemberCreationRequest,
    TeamMemberCreationResult,
    InviteLinkCreationResult,
    TeamMemberLookupRequest,
)
from kickai.features.team_administration.domain.exceptions import (
    TeamMemberNotFoundError,
    TeamMemberServiceUnavailableError,
    RepositoryUnavailableError,
    DuplicatePhoneNumberError,
)
from kickai.utils.constants import DEFAULT_MEMBER_ROLE


class TeamMemberManagementService:
    """
    Consolidated service for all team member operations.
    
    This service provides a single interface for tools, eliminating the need
    for tools to depend on multiple services directly.
    """

    def __init__(self, team_repository: TeamRepositoryInterface):
        """
        Initialize the management service with required dependencies.
        
        Args:
            team_repository: Repository for team and team member operations
        """
        self.team_repository = team_repository
        self.simplified_service = SimplifiedTeamMemberService(team_repository)
        self.team_member_service = TeamMemberService(team_repository)
        # Note: TeamService will be injected when needed to avoid circular dependencies

    async def create_team_member_with_invite(
        self, 
        request: TeamMemberCreationRequest
    ) -> TeamMemberCreationResult:
        """
        Create a new team member and generate an invite link.
        
        This is the primary method for team member creation workflows.
        
        Args:
            request: Team member creation request with all required data
            
        Returns:
            TeamMemberCreationResult with success status, member data, and invite link
        """
        try:
            logger.info(f"🔄 Creating team member: {request.member_name} for team {request.team_id}")
            
            # Create team member (or get existing)
            success, message, existing_member = await self.simplified_service.add_team_member_or_get_existing(
                name=request.member_name,
                phone=request.phone_number,
                role=request.role or DEFAULT_MEMBER_ROLE,
                team_id=request.team_id,
                email=None
            )
            
            if not success:
                return TeamMemberCreationResult(
                    success=False,
                    error_message=message
                )
            
            # Generate invite link
            invite_result = await self.create_invite_link_for_member(
                team_id=request.team_id,
                member_id=existing_member.member_id,  # Pass real member_id
                member_name=request.member_name,
                member_phone=request.phone_number,
                member_role=request.role or DEFAULT_MEMBER_ROLE
            )
            
            return TeamMemberCreationResult(
                success=True,
                member=existing_member,
                invite_link=invite_result.invite_link if invite_result.success else None,
                error_message=invite_result.error_message if not invite_result.success else None,
                member_id=existing_member.member_id if existing_member else None
            )
            
        except Exception as e:
            logger.error(f"❌ Error in create_team_member_with_invite: {e}")
            return TeamMemberCreationResult(
                success=False,
                error_message=str(e)
            )

    async def create_invite_link_for_member(
        self,
        team_id: TeamId,
        member_id: str,
        member_name: str,
        member_phone: PhoneNumber,
        member_role: str
    ) -> InviteLinkCreationResult:
        """
        Create an invite link for a team member.
        
        Args:
            team_id: Team identifier
            member_id: Member's ID (M01AB format)
            member_name: Member's name
            member_phone: Member's phone number
            member_role: Member's role
            
        Returns:
            InviteLinkCreationResult with invite link details
        """
        try:
            invite_result = await self.simplified_service.create_team_member_invite_link(
                member_name, member_phone, member_role, team_id, member_id
            )
            
            if invite_result.get("success"):
                return InviteLinkCreationResult(
                    success=True,
                    invite_link=invite_result["invite_link"],
                    member_id=invite_result.get("member_id"),
                    expires_at=invite_result.get("expires_at")
                )
            else:
                return InviteLinkCreationResult(
                    success=False,
                    error_message=invite_result.get("error", "Unknown error")
                )
                
        except Exception as e:
            logger.error(f"❌ Error creating invite link: {e}")
            return InviteLinkCreationResult(
                success=False,
                error_message=str(e)
            )

    async def get_team_member_by_telegram_id(
        self, 
        telegram_id: TelegramUserId, 
        team_id: TeamId
    ) -> Optional[TeamMember]:
        """
        Get a team member by their Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            team_id: Team identifier
            
        Returns:
            TeamMember if found, None otherwise
            
        Raises:
            TeamMemberServiceUnavailableError: If the service is not available
        """
        try:
            return await self.team_member_service.get_team_member_by_telegram_id(
                str(telegram_id), team_id
            )
        except Exception as e:
            logger.error(f"❌ Error getting team member by telegram_id {telegram_id}: {e}")
            raise TeamMemberServiceUnavailableError(f"Failed to lookup team member: {e}")

    async def get_team_member_by_phone(
        self, 
        phone_number: PhoneNumber, 
        team_id: TeamId
    ) -> Optional[TeamMember]:
        """
        Get a team member by their phone number.
        
        Args:
            phone_number: Phone number to search for
            team_id: Team identifier
            
        Returns:
            TeamMember if found, None otherwise
        """
        try:
            return await self.team_member_service.get_team_member_by_phone(
                phone_number, team_id
            )
        except Exception as e:
            logger.error(f"❌ Error getting team member by phone {phone_number}: {e}")
            return None

    async def update_team_member(self, member: TeamMember) -> bool:
        """
        Update a team member's information.
        
        Args:
            member: TeamMember object with updated information
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RepositoryUnavailableError: If the repository is not available
        """
        try:
            return await self.team_member_service.update_team_member(member)
        except Exception as e:
            logger.error(f"❌ Error updating team member {member.member_id}: {e}")
            raise RepositoryUnavailableError(f"Failed to update team member: {e}")

    async def check_phone_number_duplicate(
        self, 
        phone_number: PhoneNumber, 
        team_id: TeamId, 
        exclude_telegram_id: Optional[TelegramUserId] = None
    ) -> Optional[TeamMember]:
        """
        Check if a phone number is already registered to another team member.
        
        Args:
            phone_number: Phone number to check
            team_id: Team identifier
            exclude_telegram_id: Telegram ID to exclude from the search (for updates)
            
        Returns:
            TeamMember if duplicate found, None otherwise
            
        Raises:
            DuplicatePhoneNumberError: If phone number is already registered
        """
        existing_member = await self.get_team_member_by_phone(phone_number, team_id)
        
        if existing_member and (exclude_telegram_id is None or existing_member.telegram_id != exclude_telegram_id):
            raise DuplicatePhoneNumberError(phone_number, existing_member.name)
        
        return existing_member

    def get_team_repository(self) -> TeamRepositoryInterface:
        """
        Get the team repository for advanced operations.
        
        Returns:
            TeamRepositoryInterface instance
        """
        return self.team_repository