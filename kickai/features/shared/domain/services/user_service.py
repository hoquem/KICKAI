#!/usr/bin/env python3
"""
User Service - Pure Business Logic

This service provides user-related business logic without any framework dependencies.
It handles user status, lookups, and information aggregation across players and team members.
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass
class UserStatus:
    """User status information structure."""

    user_type: str
    telegram_id: int
    team_id: str
    name: str | None = None
    position: str | None = None
    role: str | None = None
    status: str | None = None
    is_admin: bool | None = None
    is_registered: bool = False


# Protocol for player data
class PlayerData(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def position(self) -> str | None:
        ...

    @property
    def status(self) -> str:
        ...


# Protocol for team member data
class TeamMemberData(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def role(self) -> str:
        ...

    @property
    def is_admin(self) -> bool:
        ...


# Repository interfaces for dependency inversion
class UserRepositoryInterface(Protocol):
    @abstractmethod
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> PlayerData | None:
        """Get player by telegram ID."""
        pass

    @abstractmethod
    async def get_team_member_by_telegram_id(
        self, telegram_id: int, team_id: str
    ) -> TeamMemberData | None:
        """Get team member by telegram ID."""
        pass


class UserService:
    """Pure domain service for user functionality."""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def get_user_status(self, telegram_id: int, team_id: str) -> UserStatus:
        """
        Get comprehensive user status by looking up both player and team member records.

        Args:
            telegram_id: User's Telegram ID
            team_id: Team ID to search in

        Returns:
            UserStatus with complete user information
        """
        # Check if user is a player
        player = await self.user_repository.get_player_by_telegram_id(telegram_id, team_id)

        if player:
            return UserStatus(
                user_type="Player",
                telegram_id=telegram_id,
                team_id=team_id,
                name=player.name,
                position=player.position,
                status=player.status.title() if player.status else "Unknown",
                is_registered=True,
            )

        # Check if user is a team member
        team_member = await self.user_repository.get_team_member_by_telegram_id(
            telegram_id, team_id
        )

        if team_member:
            return UserStatus(
                user_type="Team Member",
                telegram_id=telegram_id,
                team_id=team_id,
                name=team_member.name,
                position="N/A",  # Team members don't have positions
                role=team_member.role.title() if team_member.role else "Member",
                status="Active",  # Team members are typically active
                is_admin=team_member.is_admin,
                is_registered=True,
            )

        # User not found in either collection
        return UserStatus(
            user_type="Not Registered",
            telegram_id=telegram_id,
            team_id=team_id,
            is_registered=False,
        )

    def format_user_status_message(self, user_status: UserStatus) -> str:
        """
        Format user status into a user-friendly message.

        Args:
            user_status: The user status to format

        Returns:
            Formatted user status message
        """
        if user_status.user_type == "Player":
            return f"""👤 USER STATUS: Player

📱 Telegram ID: {user_status.telegram_id}
🏆 Team ID: {user_status.team_id}
📋 Player Info: {user_status.name} ({user_status.position or 'Position not set'})
✅ Status: {user_status.status}"""
        elif user_status.user_type == "Team Member":
            return f"""👤 USER STATUS: Team Member

📱 Telegram ID: {user_status.telegram_id}
🏆 Team ID: {user_status.team_id}
📋 Member Info: {user_status.name}
👑 Role: {user_status.role}
✅ Admin: {'Yes' if user_status.is_admin else 'No'}"""
        else:
            return f"""👤 USER STATUS: Not Registered

📱 Telegram ID: {user_status.telegram_id}
🏆 Team ID: {user_status.team_id}
ℹ️ Info: User is not registered as a player or team member"""
