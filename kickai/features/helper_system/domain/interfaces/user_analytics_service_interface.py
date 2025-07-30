"""
User Analytics Service Interface

Abstract interface for user analytics service operations.
"""

from abc import ABC, abstractmethod

from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile
from kickai.features.helper_system.domain.value_objects.analytics_value_objects import UserAnalytics


class IUserAnalyticsService(ABC):
    """Abstract interface for user analytics service operations."""

    @abstractmethod
    async def get_user_profile(self, user_id: str, team_id: str) -> LearningProfile | None:
        """
        Get user's learning profile, creating one if it doesn't exist.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            LearningProfile if found or created, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_analytics(self, user_id: str, team_id: str) -> UserAnalytics:
        """
        Get analytics for a specific user.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            UserAnalytics value object containing user analytics
        """
        pass

    @abstractmethod
    async def track_user_action(self, user_id: str, team_id: str, action: str) -> None:
        """
        Track a user action for analytics.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            action: The action being tracked
        """
        pass

    @abstractmethod
    async def track_command_usage(self, user_id: str, team_id: str, command: str) -> None:
        """
        Track command usage and update learning profile.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            command: The command that was used
        """
        pass
