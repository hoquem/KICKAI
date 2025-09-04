"""
Business service interfaces for domain operations.

These interfaces define contracts for business logic services, enabling
clean separation between application and domain layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from kickai.core.value_objects import (
    PhoneNumber,
    PlayerId,
    TeamId,
    UserId,
)


class IPlayerService(ABC):
    """Service interface for player business operations."""

    @abstractmethod
    async def register_player(
        self,
        name: str,
        phone: PhoneNumber,
        position: str,
        team_id: TeamId,
        telegram_id: str,
        username: str,
        chat_type: str,
    ) -> dict[str, Any]:
        """
        Register a new player.

        Args:
            name: Player name
            phone: Player phone number
            position: Player position
            team_id: Team identifier
            telegram_id: Requesting user's Telegram ID
            username: Requesting user's username
            chat_type: Chat type context

        Returns:
            Registration result with player data
        """
        pass

    @abstractmethod
    async def get_player_status(
        self, player_id: PlayerId, team_id: TeamId, telegram_id: str, username: str, chat_type: str
    ) -> dict[str, Any]:
        """
        Get player status information.

        Args:
            player_id: Player identifier
            team_id: Team identifier
            telegram_id: Requesting user's Telegram ID
            username: Requesting user's username
            chat_type: Chat type context

        Returns:
            Player status information
        """
        pass

    @abstractmethod
    async def get_active_players(
        self, team_id: TeamId, telegram_id: str, username: str, chat_type: str
    ) -> list[dict[str, Any]]:
        """
        Get list of active players.

        Args:
            team_id: Team identifier
            telegram_id: Requesting user's Telegram ID
            username: Requesting user's username
            chat_type: Chat type context

        Returns:
            List of active players
        """
        pass

    @abstractmethod
    async def approve_player(
        self, player_id: PlayerId, team_id: TeamId, telegram_id: str, username: str, chat_type: str
    ) -> bool:
        """
        Approve player registration.

        Args:
            player_id: Player to approve
            team_id: Team identifier
            telegram_id: Approver's Telegram ID
            username: Approver's username
            chat_type: Chat type context

        Returns:
            True if approved successfully
        """
        pass

    @abstractmethod
    async def update_player_information(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        updates: dict[str, Any],
        telegram_id: str,
        username: str,
        chat_type: str,
    ) -> dict[str, Any]:
        """
        Update player information.

        Args:
            player_id: Player identifier
            team_id: Team identifier
            updates: Fields to update
            telegram_id: Updater's Telegram ID
            username: Updater's username
            chat_type: Chat type context

        Returns:
            Updated player information
        """
        pass


class ITeamService(ABC):
    """Service interface for team business operations."""

    @abstractmethod
    async def add_team_member(
        self,
        name: str,
        phone: PhoneNumber,
        role: str,
        team_id: TeamId,
        telegram_id: str,
        username: str,
        chat_type: str,
    ) -> dict[str, Any]:
        """
        Add new team member.

        Args:
            name: Member name
            phone: Member phone number
            role: Member role
            team_id: Team identifier
            telegram_id: Requesting user's Telegram ID
            username: Requesting user's username
            chat_type: Chat type context

        Returns:
            Addition result with member data
        """
        pass

    @abstractmethod
    async def get_team_members(
        self, team_id: TeamId, telegram_id: str, username: str, chat_type: str
    ) -> list[dict[str, Any]]:
        """
        Get list of team members.

        Args:
            team_id: Team identifier
            telegram_id: Requesting user's Telegram ID
            username: Requesting user's username
            chat_type: Chat type context

        Returns:
            List of team members
        """
        pass

    @abstractmethod
    async def update_team_member(
        self,
        user_id: UserId,
        team_id: TeamId,
        updates: dict[str, Any],
        telegram_id: str,
        username: str,
        chat_type: str,
    ) -> dict[str, Any]:
        """
        Update team member information.

        Args:
            user_id: Member identifier
            team_id: Team identifier
            updates: Fields to update
            telegram_id: Updater's Telegram ID
            username: Updater's username
            chat_type: Chat type context

        Returns:
            Updated member information
        """
        pass

    @abstractmethod
    async def get_team_configuration(
        self, team_id: TeamId, telegram_id: str, username: str, chat_type: str
    ) -> dict[str, Any]:
        """
        Get team configuration.

        Args:
            team_id: Team identifier
            telegram_id: Requesting user's Telegram ID
            username: Requesting user's username
            chat_type: Chat type context

        Returns:
            Team configuration
        """
        pass


class IUserService(ABC):
    """Service interface for user business operations."""

    @abstractmethod
    async def get_user_registration(self, user_id: UserId, team_id: TeamId) -> dict[str, Any]:
        """
        Get user registration status.

        Args:
            user_id: User identifier
            team_id: Team identifier

        Returns:
            User registration status
        """
        pass

    @abstractmethod
    async def update_user_permissions(
        self,
        user_id: UserId,
        team_id: TeamId,
        permissions: list[str],
        telegram_id: str,
        username: str,
        chat_type: str,
    ) -> bool:
        """
        Update user permissions.

        Args:
            user_id: User identifier
            team_id: Team identifier
            permissions: New permissions
            telegram_id: Updater's Telegram ID
            username: Updater's username
            chat_type: Chat type context

        Returns:
            True if updated successfully
        """
        pass


class IValidationService(ABC):
    """Service interface for validation operations."""

    @abstractmethod
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid format
        """
        pass

    @abstractmethod
    def validate_player_position(self, position: str) -> bool:
        """
        Validate player position.

        Args:
            position: Position to validate

        Returns:
            True if valid position
        """
        pass

    @abstractmethod
    def validate_team_member_role(self, role: str) -> bool:
        """
        Validate team member role.

        Args:
            role: Role to validate

        Returns:
            True if valid role
        """
        pass

    @abstractmethod
    def validate_user_permissions(
        self,
        telegram_id: str,
        team_id: str,
        username: str,
        chat_type: str,
        required_permissions: list[str],
    ) -> bool:
        """
        Validate user has required permissions.

        Args:
            telegram_id: User's Telegram ID
            team_id: Team identifier
            username: User's username
            chat_type: Chat type context
            required_permissions: Required permissions

        Returns:
            True if user has all required permissions
        """
        pass

    @abstractmethod
    def get_validation_errors(
        self, data: dict[str, Any], validation_rules: dict[str, Any]
    ) -> list[str]:
        """
        Get validation errors for data.

        Args:
            data: Data to validate
            validation_rules: Validation rules to apply

        Returns:
            List of validation error messages
        """
        pass


class INotificationService(ABC):
    """Service interface for notification operations."""

    @abstractmethod
    async def send_welcome_message(
        self, user_id: UserId, team_id: TeamId, message_type: str
    ) -> bool:
        """
        Send welcome message to user.

        Args:
            user_id: User identifier
            team_id: Team identifier
            message_type: Type of welcome message

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    async def send_approval_notification(
        self, player_id: PlayerId, team_id: TeamId, approved_by: UserId
    ) -> bool:
        """
        Send approval notification.

        Args:
            player_id: Approved player
            team_id: Team identifier
            approved_by: Who approved

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    async def send_registration_notification(
        self, new_member_id: UserId, team_id: TeamId, registration_type: str
    ) -> bool:
        """
        Send registration notification to leadership.

        Args:
            new_member_id: New member/player
            team_id: Team identifier
            registration_type: "player" or "team_member"

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    async def send_error_notification(
        self, user_id: UserId, error_message: str, telegram_id: str, username: str, chat_type: str
    ) -> bool:
        """
        Send error notification to user.

        Args:
            user_id: User identifier
            error_message: Error message
            telegram_id: User's Telegram ID
            username: User's username
            chat_type: Chat type context

        Returns:
            True if sent successfully
        """
        pass


class IAnalyticsService(ABC):
    """Service interface for analytics operations."""

    @abstractmethod
    async def track_user_action(
        self,
        user_id: UserId,
        action: str,
        telegram_id: str,
        username: str,
        chat_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Track user action for analytics.

        Args:
            user_id: User identifier
            action: Action performed
            telegram_id: User's Telegram ID
            username: User's username
            chat_type: Chat type context
            metadata: Optional metadata
        """
        pass

    @abstractmethod
    async def get_team_analytics(
        self, team_id: TeamId, date_range: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Get team analytics data.

        Args:
            team_id: Team identifier
            date_range: Optional date range filter

        Returns:
            Analytics data
        """
        pass

    @abstractmethod
    async def get_user_engagement_metrics(
        self, team_id: TeamId, period: str = "week"
    ) -> dict[str, Any]:
        """
        Get user engagement metrics.

        Args:
            team_id: Team identifier
            period: Time period for metrics

        Returns:
            Engagement metrics
        """
        pass
