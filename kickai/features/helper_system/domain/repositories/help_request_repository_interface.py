"""
Help Request Repository Interface

Abstract interface for managing help requests in the Helper System.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from kickai.features.helper_system.domain.entities.help_request import HelpRequest
from kickai.features.helper_system.domain.value_objects.analytics_value_objects import (
    HelpRequestStatistics,
    PopularHelpTopic,
)


class HelpRequestRepositoryInterface(ABC):
    """Abstract interface for help request repository operations."""

    @abstractmethod
    async def create_help_request(self, help_request: HelpRequest) -> HelpRequest:
        """
        Create a new help request.

        Args:
            help_request: The help request to create

        Returns:
            The created help request
        """
        pass

    @abstractmethod
    async def get_help_request(self, request_id: str, team_id: str) -> HelpRequest | None:
        """
        Get a help request by ID.

        Args:
            request_id: The help request ID
            team_id: The team's ID

        Returns:
            HelpRequest if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_help_request(
        self, request_id: str, team_id: str, updates: dict
    ) -> HelpRequest | None:
        """
        Update a help request.

        Args:
            request_id: The help request ID
            team_id: The team's ID
            updates: Dictionary of fields to update

        Returns:
            Updated HelpRequest if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_help_requests(
        self, user_id: str, team_id: str, limit: int = 50
    ) -> list[HelpRequest]:
        """
        Get help requests for a specific user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            limit: Maximum number of requests to return

        Returns:
            List of help requests for the user
        """
        pass

    @abstractmethod
    async def get_team_help_requests(self, team_id: str, limit: int = 100) -> list[HelpRequest]:
        """
        Get all help requests for a team.

        Args:
            team_id: The team's ID
            limit: Maximum number of requests to return

        Returns:
            List of help requests for the team
        """
        pass

    @abstractmethod
    async def get_recent_help_requests(self, team_id: str, days: int = 7) -> list[HelpRequest]:
        """
        Get recent help requests for a team.

        Args:
            team_id: The team's ID
            days: Number of days to look back

        Returns:
            List of recent help requests
        """
        pass

    @abstractmethod
    async def get_help_requests_by_type(self, team_id: str, request_type: str) -> list[HelpRequest]:
        """
        Get help requests by type.

        Args:
            team_id: The team's ID
            request_type: Type of help request to filter by

        Returns:
            List of help requests of the specified type
        """
        pass

    @abstractmethod
    async def get_unresolved_help_requests(self, team_id: str) -> list[HelpRequest]:
        """
        Get unresolved help requests for a team.

        Args:
            team_id: The team's ID

        Returns:
            List of unresolved help requests
        """
        pass

    @abstractmethod
    async def mark_help_request_resolved(
        self, request_id: str, team_id: str, response: str, helpful: bool = None, rating: int = None
    ) -> HelpRequest | None:
        """
        Mark a help request as resolved.

        Args:
            request_id: The help request ID
            team_id: The team's ID
            response: The response provided
            helpful: Whether the response was helpful
            rating: User rating (1-5)

        Returns:
            Updated HelpRequest if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_help_request(self, request_id: str, team_id: str) -> bool:
        """
        Delete a help request.

        Args:
            request_id: The help request ID
            team_id: The team's ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def get_help_request_statistics(
        self, team_id: str, start_date: datetime = None, end_date: datetime = None
    ) -> HelpRequestStatistics:
        """
        Get help request statistics for a team.

        Args:
            team_id: The team's ID
            start_date: Start date for statistics (optional)
            end_date: End date for statistics (optional)

        Returns:
            HelpRequestStatistics value object
        """
        pass

    @abstractmethod
    async def get_popular_help_topics(
        self, team_id: str, limit: int = 10
    ) -> list[PopularHelpTopic]:
        """
        Get popular help topics for a team.

        Args:
            team_id: The team's ID
            limit: Maximum number of topics to return

        Returns:
            List of PopularHelpTopic value objects
        """
        pass
