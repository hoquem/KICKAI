"""
Business service interfaces for domain operations.

These interfaces define contracts for business logic services, enabling
clean separation between application and domain layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from kickai.core.value_objects import (
    EntityContext,
    PhoneNumber,
    PlayerId,
    TeamId,
    UserId,
    UserRegistration,
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
        context: EntityContext
    ) -> dict[str, Any]:
        """
        Register a new player.

        Args:
            name: Player name
            phone: Player phone number
            position: Player position
            team_id: Team identifier
            context: Registration context

        Returns:
            Registration result with player data
        """
        pass

    @abstractmethod
    async def get_player_status(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        requester_context: EntityContext
    ) -> dict[str, Any]:
        """
        Get player status information.

        Args:
            player_id: Player identifier
            team_id: Team identifier
            requester_context: Context of the requester

        Returns:
            Player status information
        """
        pass

    @abstractmethod
    async def get_active_players(
        self,
        team_id: TeamId,
        requester_context: EntityContext
    ) -> list[dict[str, Any]]:
        """
        Get list of active players.

        Args:
            team_id: Team identifier
            requester_context: Context of the requester

        Returns:
            List of active players
        """
        pass

    @abstractmethod
    async def approve_player(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        approver_context: EntityContext
    ) -> bool:
        """
        Approve player registration.

        Args:
            player_id: Player to approve
            team_id: Team identifier
            approver_context: Context of the approver

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
        updater_context: EntityContext
    ) -> dict[str, Any]:
        """
        Update player information.

        Args:
            player_id: Player identifier
            team_id: Team identifier
            updates: Fields to update
            updater_context: Context of the updater

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
        context: EntityContext
    ) -> dict[str, Any]:
        """
        Add new team member.

        Args:
            name: Member name
            phone: Member phone number
            role: Member role
            team_id: Team identifier
            context: Addition context

        Returns:
            Addition result with member data
        """
        pass

    @abstractmethod
    async def get_team_members(
        self,
        team_id: TeamId,
        requester_context: EntityContext
    ) -> list[dict[str, Any]]:
        """
        Get list of team members.

        Args:
            team_id: Team identifier
            requester_context: Context of the requester

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
        updater_context: EntityContext
    ) -> dict[str, Any]:
        """
        Update team member information.

        Args:
            user_id: Member identifier
            team_id: Team identifier
            updates: Fields to update
            updater_context: Context of the updater

        Returns:
            Updated member information
        """
        pass

    @abstractmethod
    async def get_team_configuration(
        self,
        team_id: TeamId,
        requester_context: EntityContext
    ) -> dict[str, Any]:
        """
        Get team configuration.

        Args:
            team_id: Team identifier
            requester_context: Context of the requester

        Returns:
            Team configuration
        """
        pass


class IUserService(ABC):
    """Service interface for user business operations."""

    @abstractmethod
    async def get_user_registration(
        self,
        user_id: UserId,
        team_id: TeamId
    ) -> UserRegistration:
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
    async def create_entity_context(
        self,
        user_id: str,
        team_id: str,
        chat_id: str,
        chat_type: str,
        username: str | None = None
    ) -> EntityContext:
        """
        Create entity context for a user.

        Args:
            user_id: User identifier
            team_id: Team identifier
            chat_id: Chat identifier
            chat_type: Chat type
            username: Optional username

        Returns:
            Complete entity context
        """
        pass

    @abstractmethod
    async def update_user_permissions(
        self,
        user_id: UserId,
        team_id: TeamId,
        permissions: list[str],
        updater_context: EntityContext
    ) -> bool:
        """
        Update user permissions.

        Args:
            user_id: User identifier
            team_id: Team identifier
            permissions: New permissions
            updater_context: Context of the updater

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
        user_context: EntityContext,
        required_permissions: list[str]
    ) -> bool:
        """
        Validate user has required permissions.

        Args:
            user_context: User context to check
            required_permissions: Required permissions

        Returns:
            True if user has all required permissions
        """
        pass

    @abstractmethod
    def get_validation_errors(
        self,
        data: dict[str, Any],
        validation_rules: dict[str, Any]
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
        self,
        user_id: UserId,
        team_id: TeamId,
        message_type: str
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
        self,
        player_id: PlayerId,
        team_id: TeamId,
        approved_by: UserId
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
        self,
        new_member_id: UserId,
        team_id: TeamId,
        registration_type: str
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
        self,
        user_id: UserId,
        error_message: str,
        context: EntityContext
    ) -> bool:
        """
        Send error notification to user.

        Args:
            user_id: User identifier
            error_message: Error message
            context: Error context

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
        context: EntityContext,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Track user action for analytics.

        Args:
            user_id: User identifier
            action: Action performed
            context: Action context
            metadata: Optional metadata
        """
        pass

    @abstractmethod
    async def get_team_analytics(
        self,
        team_id: TeamId,
        date_range: dict[str, Any] | None = None
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
        self,
        team_id: TeamId,
        period: str = "week"
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
