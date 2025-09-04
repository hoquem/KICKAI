#!/usr/bin/env python3
"""
Team Member Service Interface

Defines the contract for team member management services.
"""

from abc import ABC, abstractmethod

from kickai.features.team_administration.domain.entities.team_member import TeamMember


class ITeamMemberService(ABC):
    """Interface for team member service operations."""

    @abstractmethod
    async def create_team_member(self, team_member: TeamMember) -> TeamMember:
        """
        Create a new team member.

        Args:
            team_member: Team member entity to create

        Returns:
            Created team member entity
        """
        pass

    @abstractmethod
    async def get_team_member_by_id(self, member_id: str) -> TeamMember | None:
        """
        Get a team member by ID.

        Args:
            member_id: Team member identifier

        Returns:
            Team member entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_team_member_by_telegram_id(
        self, telegram_id: int, team_id: str
    ) -> TeamMember | None:
        """
        Get a team member by Telegram ID.

        Args:
            telegram_id: Telegram user ID
            team_id: Team identifier

        Returns:
            Team member entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_team_member_by_phone(self, phone_number: str, team_id: str) -> TeamMember | None:
        """
        Get a team member by phone number.

        Args:
            phone_number: Phone number to search for
            team_id: Team identifier

        Returns:
            Team member entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_members_by_telegram_id(self, telegram_id: int) -> list[TeamMember]:
        """
        Get all team members for a Telegram ID (across teams).

        Args:
            telegram_id: Telegram user ID

        Returns:
            List of team member entities
        """
        pass

    @abstractmethod
    async def get_team_members(self, team_id: str) -> list[TeamMember]:
        """
        Get all members of a team.

        Args:
            team_id: Team identifier

        Returns:
            List of team member entities
        """
        pass

    @abstractmethod
    async def update_team_member(self, team_member: TeamMember) -> TeamMember:
        """
        Update an existing team member.

        Args:
            team_member: Updated team member entity

        Returns:
            Updated team member entity
        """
        pass

    @abstractmethod
    async def activate_team_member(self, telegram_id: int, team_id: str) -> TeamMember | None:
        """
        Activate a team member (change status from pending to active).

        Args:
            telegram_id: Telegram user ID
            team_id: Team identifier

        Returns:
            Activated team member if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_team_member(self, member_id: str) -> bool:
        """
        Delete a team member.

        Args:
            member_id: Team member identifier

        Returns:
            True if successfully deleted
        """
        pass

    @abstractmethod
    async def search_team_members(self, team_id: str, search_term: str) -> list[TeamMember]:
        """
        Search team members by name, phone, or email.

        Args:
            team_id: Team identifier
            search_term: Search term to match against

        Returns:
            List of matching team member entities
        """
        pass

    @abstractmethod
    async def find_team_member_by_identifier(self, identifier: str, team_id: str) -> TeamMember | None:
        """
        Find a team member by various identifiers (ID, name, phone, username).

        Args:
            identifier: Member identifier (ID, name, phone, or username)
            team_id: Team identifier

        Returns:
            Team member entity if found, None otherwise
        """
        pass
