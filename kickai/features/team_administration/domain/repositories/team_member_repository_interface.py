#!/usr/bin/env python3
"""
Team Member Repository Interface

This module defines the interface for team member data access operations.
"""

from abc import ABC, abstractmethod

from kickai.features.team_administration.domain.entities.team_member import TeamMember


class TeamMemberRepositoryInterface(ABC):
    """Interface for team member data access operations."""

    @abstractmethod
    async def create_team_member(self, team_member: TeamMember) -> TeamMember:
        """Create a new team member."""
        pass

    @abstractmethod
    async def get_team_member_by_id(self, member_id: str, team_id: str) -> TeamMember | None:
        """Get a team member by ID."""
        pass

    @abstractmethod
    async def get_team_member_by_telegram_id(
        self, telegram_id: int, team_id: str
    ) -> TeamMember | None:
        """Get a team member by Telegram ID."""
        pass

    @abstractmethod
    async def get_team_member_by_phone(self, phone_number: str, team_id: str) -> TeamMember | None:
        """Get a team member by phone number."""
        pass

    @abstractmethod
    async def get_team_members(self, team_id: str) -> list[TeamMember]:
        """Get all team members for a team."""
        pass

    @abstractmethod
    async def get_team_members_by_status(self, team_id: str, status: str) -> list[TeamMember]:
        """Get team members by status."""
        pass

    @abstractmethod
    async def update_team_member(self, team_member: TeamMember) -> TeamMember:
        """Update an existing team member."""
        pass

    @abstractmethod
    async def delete_team_member(self, member_id: str, team_id: str) -> bool:
        """Delete a team member."""
        pass

    @abstractmethod
    async def activate_team_member(self, telegram_id: int, team_id: str) -> TeamMember | None:
        """Activate a team member (change status from pending to active)."""
        pass

    @abstractmethod
    async def search_team_members(self, team_id: str, search_term: str) -> list[TeamMember]:
        """Search team members by name, phone, or email."""
        pass

    @abstractmethod
    async def update_team_member_field(
        self, telegram_id: int, team_id: str, field: str, value: str
    ) -> bool:
        """Update a single field for a team member."""
        pass

    @abstractmethod
    async def update_team_member_multiple_fields(
        self, telegram_id: int, team_id: str, updates: dict[str, str]
    ) -> bool:
        """Update multiple fields for a team member."""
        pass
