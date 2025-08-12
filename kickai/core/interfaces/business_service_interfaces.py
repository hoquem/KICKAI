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
    TelegramId,
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

        :param name: Player name
        :type name: str
        :param phone: Player phone number
        :type phone: PhoneNumber
        :param position: Player position
        :type position: str
        :param team_id: Team identifier
        :type team_id: TeamId
        :param context: Registration context
        :type context: EntityContext
        :return: Registration result with player data
        :rtype: dict[str, Any]
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


            player_id: Player identifier
            team_id: Team identifier
            requester_context: Context of the requester


    :return: Player status information
    :rtype: str  # TODO: Fix type
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


            team_id: Team identifier
            requester_context: Context of the requester


    :return: List of active players
    :rtype: str  # TODO: Fix type
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


            player_id: Player to approve
            team_id: Team identifier
            approver_context: Context of the approver


    :return: True if approved successfully
    :rtype: str  # TODO: Fix type
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


            player_id: Player identifier
            team_id: Team identifier
            updates: Fields to update
            updater_context: Context of the updater


    :return: Updated player information
    :rtype: str  # TODO: Fix type
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


            name: Member name
            phone: Member phone number
            role: Member role
            team_id: Team identifier
            context: Addition context


    :return: Addition result with member data
    :rtype: str  # TODO: Fix type
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


            team_id: Team identifier
            requester_context: Context of the requester


    :return: List of team members
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def update_team_member(
        self,
        user_id: TelegramId,
        team_id: TeamId,
        updates: dict[str, Any],
        updater_context: EntityContext
    ) -> dict[str, Any]:
        """
        Update team member information.


            user_id: Member identifier
            team_id: Team identifier
            updates: Fields to update
            updater_context: Context of the updater


    :return: Updated member information
    :rtype: str  # TODO: Fix type
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


            team_id: Team identifier
            requester_context: Context of the requester


    :return: Team configuration
    :rtype: str  # TODO: Fix type
        """
        pass


class IUserService(ABC):
    """Service interface for user business operations."""

    @abstractmethod
    async def get_user_registration(
        self,
        user_id: TelegramId,
        team_id: TeamId
    ) -> UserRegistration:
        """
        Get user registration status.


            user_id: User identifier
            team_id: Team identifier


    :return: User registration status
    :rtype: str  # TODO: Fix type
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


            user_id: User identifier
            team_id: Team identifier
            chat_id: Chat identifier
            chat_type: Chat type
            username: Optional username


    :return: Complete entity context
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def update_user_permissions(
        self,
        user_id: TelegramId,
        team_id: TeamId,
        permissions: list[str],
        updater_context: EntityContext
    ) -> bool:
        """
        Update user permissions.


            user_id: User identifier
            team_id: Team identifier
            permissions: New permissions
            updater_context: Context of the updater


    :return: True if updated successfully
    :rtype: str  # TODO: Fix type
        """
        pass


class IValidationService(ABC):
    """Service interface for validation operations."""

    @abstractmethod
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate phone number format.


            phone: Phone number to validate


    :return: True if valid format
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    def validate_player_position(self, position: str) -> bool:
        """
        Validate player position.


            position: Position to validate


    :return: True if valid position
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    def validate_team_member_role(self, role: str) -> bool:
        """
        Validate team member role.


            role: Role to validate


    :return: True if valid role
    :rtype: str  # TODO: Fix type
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


            user_context: User context to check
            required_permissions: Required permissions


    :return: True if user has all required permissions
    :rtype: str  # TODO: Fix type
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


            data: Data to validate
            validation_rules: Validation rules to apply


    :return: List of validation error messages
    :rtype: str  # TODO: Fix type
        """
        pass


class INotificationService(ABC):
    """Service interface for notification operations."""

    @abstractmethod
    async def send_welcome_message(
        self,
        user_id: TelegramId,
        team_id: TeamId,
        message_type: str
    ) -> bool:
        """
        Send welcome message to user.


            user_id: User identifier
            team_id: Team identifier
            message_type: Type of welcome message


    :return: True if sent successfully
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def send_approval_notification(
        self,
        player_id: PlayerId,
        team_id: TeamId,
        approved_by: TelegramId
    ) -> bool:
        """
        Send approval notification.


            player_id: Approved player
            team_id: Team identifier
            approved_by: Who approved


    :return: True if sent successfully
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def send_registration_notification(
        self,
        new_member_id: TelegramId,
        team_id: TeamId,
        registration_type: str
    ) -> bool:
        """
        Send registration notification to leadership.


            new_member_id: New member/player
            team_id: Team identifier
            registration_type: "player" or "team_member"


    :return: True if sent successfully
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def send_error_notification(
        self,
        user_id: TelegramId,
        error_message: str,
        context: EntityContext
    ) -> bool:
        """
        Send error notification to user.


            user_id: User identifier
            error_message: Error message
            context: Error context


    :return: True if sent successfully
    :rtype: str  # TODO: Fix type
        """
        pass


class IAnalyticsService(ABC):
    """Service interface for analytics operations."""

    @abstractmethod
    async def track_user_action(
        self,
        user_id: TelegramId,
        action: str,
        context: EntityContext,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Track user action for analytics.


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


            team_id: Team identifier
            date_range: Optional date range filter


    :return: Analytics data
    :rtype: str  # TODO: Fix type
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


            team_id: Team identifier
            period: Time period for metrics


    :return: Engagement metrics
    :rtype: str  # TODO: Fix type
        """
        pass
