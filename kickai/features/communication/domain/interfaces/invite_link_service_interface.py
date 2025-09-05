#!/usr/bin/env python3
"""
Invite Link Service Interface

Defines the contract for invite link management services.
"""

from abc import ABC, abstractmethod
from typing import Any


class IInviteLinkService(ABC):
    """Interface for invite link service operations."""

    @abstractmethod
    async def create_invite_link(
        self,
        team_id: str,
        member_id: str,
        member_name: str,
        member_phone: str,
        chat_type: str = "leadership",
        expires_hours: int = 48,
    ) -> dict[str, Any]:
        """
        Create an invite link for a team member.

        Args:
            team_id: Team identifier
            member_id: Member identifier
            member_name: Member's full name
            member_phone: Member's phone number
            chat_type: Type of chat to invite to
            expires_hours: Hours until link expires

        Returns:
            Dictionary containing invite link and metadata
        """
        pass

    @abstractmethod
    async def validate_invite_link(self, invite_link: str) -> dict[str, Any]:
        """
        Validate an invite link.

        Args:
            invite_link: The invite link to validate

        Returns:
            Dictionary containing validation result and invite data
        """
        pass

    @abstractmethod
    async def use_invite_link(
        self, invite_link: str, telegram_id: int, telegram_username: str
    ) -> dict[str, Any]:
        """
        Use (consume) an invite link.

        Args:
            invite_link: The invite link being used
            telegram_id: Telegram ID of the user using the link
            telegram_username: Telegram username of the user

        Returns:
            Dictionary containing usage result and member data
        """
        pass

    @abstractmethod
    async def revoke_invite_link(self, invite_link: str) -> bool:
        """
        Revoke an invite link.

        Args:
            invite_link: The invite link to revoke

        Returns:
            True if successfully revoked
        """
        pass

    @abstractmethod
    async def get_invite_info(self, invite_link: str) -> dict[str, Any] | None:
        """
        Get information about an invite link.

        Args:
            invite_link: The invite link to get info for

        Returns:
            Invite information if found, None otherwise
        """
        pass

    @abstractmethod
    async def cleanup_expired_invites(self, team_id: str) -> int:
        """
        Clean up expired invite links for a team.

        Args:
            team_id: Team identifier

        Returns:
            Number of expired invites cleaned up
        """
        pass
