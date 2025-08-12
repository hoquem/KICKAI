#!/usr/bin/env python3
"""
Registration Service

This module provides the registration service for handling player and team member registration workflows.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from kickai.core.interfaces.player_repositories import (
    IPlayerRepository,
)
from kickai.core.interfaces.team_repositories import (
    TeamRepositoryInterface,
)
from kickai.features.player_registration.domain.entities.player import Player
from kickai.features.team_administration.domain.entities.team_member import TeamMember
from kickai.utils.simple_id_generator import SimpleIDGenerator


class RegistrationService:
    """Service for handling player and team member registration workflows."""

    def __init__(
        self,
        player_repository: IPlayerRepository,
        team_repository: TeamRepositoryInterface,
        team_id: str,
    ):
        self.player_repository = player_repository
        self.team_repository = team_repository
        self.team_id = team_id
        self.id_generator = SimpleIDGenerator()

    async def create_pending_player(
        self,
        name: str,
        phone: str,
        position: str,
        invited_by: str
    ) -> dict[str, Any]:
        """
        Create a pending player registration.


            name: Player's full name
            phone: Player's phone number
            position: Player's position
            invited_by: ID of team member who invited the player


    :return: Dictionary with player details and invite link
    :rtype: str  # TODO: Fix type
        """
        try:
            # Validate phone number
            from kickai.utils.phone_utils import is_valid_phone
            if not is_valid_phone(phone):
                raise ValueError(f"Invalid phone number format: {phone}")

            # Check if player already exists
            existing_player = await self.player_repository.get_player_by_phone(phone, self.team_id)
            if existing_player:
                raise ValueError(f"Player with phone {phone} already exists")

            # Generate player ID
            player_id = self.id_generator.generate_player_id(name, self.team_id)

            # Create pending player
            player = Player(
                player_id=player_id,
                team_id=self.team_id,
                full_name=name,
                phone_number=phone,
                position=position,
                status="pending",
                created_at=datetime.now(),
                source="registration_service",
            )

            # Save to repository
            await self.player_repository.create_player(player)

            # Generate invite link
            invite_link = self._generate_invite_link(phone)

            logger.info(f"✅ Created pending player {player_id} for team {self.team_id}")

            return {
                "player_id": player_id,
                "name": name,
                "phone": phone,
                "position": position,
                "status": "pending",
                "invite_link": invite_link,
                "invited_by": invited_by,
            }

        except Exception as e:
            logger.error(f"❌ Failed to create pending player: {e}")
            raise

    async def create_pending_team_member(
        self,
        name: str,
        phone: str,
        role: str,
        invited_by: str
    ) -> dict[str, Any]:
        """
        Create a pending team member registration.


            name: Member's full name
            phone: Member's phone number
            role: Member's role
            invited_by: ID of admin who invited the member


    :return: Dictionary with member details and invite link
    :rtype: str  # TODO: Fix type
        """
        try:
            # Validate phone number
            from kickai.utils.phone_utils import is_valid_phone
            if not is_valid_phone(phone):
                raise ValueError(f"Invalid phone number format: {phone}")

            # Check if member already exists
            existing_member = await self.team_repository.get_team_member_by_phone(phone, self.team_id)
            if existing_member:
                raise ValueError(f"Team member with phone {phone} already exists")

            # Generate member ID
            member_id = self.id_generator.generate_team_member_id(name, self.team_id)

            # Create pending team member
            team_member = TeamMember(
                member_id=member_id,
                team_id=self.team_id,
                full_name=name,
                phone_number=phone,
                role=role,
                status="pending",
                created_at=datetime.now(),
                source="registration_service",
            )

            # Save to repository
            await self.team_repository.create_team_member(team_member)

            # Generate invite link
            invite_link = self._generate_invite_link(phone)

            logger.info(f"✅ Created pending team member {member_id} for team {self.team_id}")

            return {
                "member_id": member_id,
                "name": name,
                "phone": phone,
                "role": role,
                "status": "pending",
                "invite_link": invite_link,
                "invited_by": invited_by,
            }

        except Exception as e:
            logger.error(f"❌ Failed to create pending team member: {e}")
            raise

    async def complete_player_registration(
        self,
        phone: str,
        telegram_id: int,
        telegram_username: str
    ) -> dict[str, Any]:
        """
        Complete player registration by linking Telegram account.


            phone: Player's phone number
            telegram_id: Player's Telegram ID
            telegram_username: Player's Telegram username


    :return: Dictionary with updated player details
    :rtype: str  # TODO: Fix type
        """
        try:
            # Find pending player by phone
            player = await self.player_repository.get_player_by_phone(phone, self.team_id)
            if not player:
                raise ValueError(f"No pending player found with phone {phone}")

            if player.status != "pending":
                raise ValueError(f"Player {player.player_id} is not in pending status")

            # Update player with Telegram information
            player.telegram_id = telegram_id
            player.username = telegram_username
            player.status = "active"
            player.updated_at = datetime.now()

            # Save updated player
            await self.player_repository.update_player(player)

            logger.info(f"✅ Completed player registration for {player.player_id}")

            return {
                "player_id": player.player_id,
                "name": player.name,
                "phone": player.phone_number,
                "position": player.position,
                "status": "active",
                "telegram_id": telegram_id,
                "telegram_username": telegram_username,
            }

        except Exception as e:
            logger.error(f"❌ Failed to complete player registration: {e}")
            raise

    async def complete_team_member_registration(
        self,
        phone: str,
        telegram_id: int,
        telegram_username: str
    ) -> dict[str, Any]:
        """
        Complete team member registration by linking Telegram account.


            phone: Member's phone number
            telegram_id: Member's Telegram ID
            telegram_username: Member's Telegram username


    :return: Dictionary with updated member details
    :rtype: str  # TODO: Fix type
        """
        try:
            # Find pending team member by phone
            member = await self.team_repository.get_team_member_by_phone(phone, self.team_id)
            if not member:
                raise ValueError(f"No pending team member found with phone {phone}")

            if member.status != "pending":
                raise ValueError(f"Team member {member.member_id} is not in pending status")

            # Update member with Telegram information
            member.telegram_id = telegram_id
            member.username = telegram_username
            member.status = "active"
            member.updated_at = datetime.now()

            # Save updated member
            await self.team_repository.update_team_member(member)

            logger.info(f"✅ Completed team member registration for {member.member_id}")

            return {
                "member_id": member.member_id,
                "name": member.name,
                "phone": member.phone_number,
                "role": member.role,
                "status": "active",
                "telegram_id": telegram_id,
                "telegram_username": telegram_username,
            }

        except Exception as e:
            logger.error(f"❌ Failed to complete team member registration: {e}")
            raise

    async def approve_player(self, player_id: str, approved_by: str) -> dict[str, Any]:
        """
        Approve a pending player.


            player_id: Player ID to approve
            approved_by: ID of team member who approved


    :return: Dictionary with approved player details
    :rtype: str  # TODO: Fix type
        """
        try:
            # Get player
            player = await self.player_repository.get_player_by_id(player_id, self.team_id)
            if not player:
                raise ValueError(f"Player {player_id} not found")

            if player.status != "pending":
                raise ValueError(f"Player {player_id} is not in pending status")

            # Update player status
            player.status = "approved"
            player.updated_at = datetime.now()
            player.approved_by = approved_by
            player.approved_at = datetime.now()

            # Save updated player
            await self.player_repository.update_player(player)

            logger.info(f"✅ Approved player {player_id} by {approved_by}")

            return {
                "player_id": player.player_id,
                "name": player.name,
                "phone": player.phone_number,
                "position": player.position,
                "status": "approved",
                "approved_by": approved_by,
                "approved_at": player.approved_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to approve player: {e}")
            raise

    async def reject_player(
        self,
        player_id: str,
        rejected_by: str,
        reason: str
    ) -> dict[str, Any]:
        """
        Reject a pending player.


            player_id: Player ID to reject
            rejected_by: ID of team member who rejected
            reason: Reason for rejection


    :return: Dictionary with rejected player details
    :rtype: str  # TODO: Fix type
        """
        try:
            # Get player
            player = await self.player_repository.get_player_by_id(player_id, self.team_id)
            if not player:
                raise ValueError(f"Player {player_id} not found")

            if player.status != "pending":
                raise ValueError(f"Player {player_id} is not in pending status")

            # Update player status
            player.status = "rejected"
            player.updated_at = datetime.now()
            player.rejected_by = rejected_by
            player.rejected_at = datetime.now()
            player.rejection_reason = reason

            # Save updated player
            await self.player_repository.update_player(player)

            logger.info(f"❌ Rejected player {player_id} by {rejected_by}: {reason}")

            return {
                "player_id": player.player_id,
                "name": player.name,
                "phone": player.phone_number,
                "position": player.position,
                "status": "rejected",
                "rejected_by": rejected_by,
                "rejected_at": player.rejected_at.isoformat(),
                "rejection_reason": reason,
            }

        except Exception as e:
            logger.error(f"❌ Failed to reject player: {e}")
            raise

    async def get_pending_players(self) -> list[dict[str, Any]]:
        """
        Get all pending players.


    :return: List of pending player dictionaries
    :rtype: str  # TODO: Fix type
        """
        try:
            players = await self.player_repository.get_players_by_status(self.team_id, "pending")

            return [
                {
                    "player_id": player.player_id,
                    "name": player.name,
                    "phone": player.phone_number,
                    "position": player.position,
                    "status": player.status,
                    "invited_by": getattr(player, 'invited_by', None),
                    "created_at": player.created_at.isoformat() if player.created_at else None,
                }
                for player in players
            ]

        except Exception as e:
            logger.error(f"❌ Failed to get pending players: {e}")
            return []

    async def get_pending_team_members(self) -> list[dict[str, Any]]:
        """
        Get all pending team members.


    :return: List of pending team member dictionaries
    :rtype: str  # TODO: Fix type
        """
        try:
            members = await self.team_repository.get_team_members_by_status(self.team_id, "pending")

            return [
                {
                    "member_id": member.member_id,
                    "name": member.name,
                    "phone": member.phone_number,
                    "role": member.role,
                    "status": member.status,
                    "invited_by": getattr(member, 'invited_by', None),
                    "created_at": member.created_at.isoformat() if member.created_at else None,
                }
                for member in members
            ]

        except Exception as e:
            logger.error(f"❌ Failed to get pending team members: {e}")
            return []

    def _generate_invite_link(self, phone: str) -> str:
        """
        Generate invite link for phone number.


            phone: Phone number to generate link for


    :return: Invite link URL
    :rtype: str  # TODO: Fix type
        """
        # Extract last 4 digits for invite code
        phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        invite_code = phone_clean[-4:]

        # Generate invite link
        return f"https://t.me/kickai_bot?start=invite_{invite_code}"
