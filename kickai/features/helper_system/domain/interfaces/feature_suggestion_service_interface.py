"""
Feature Suggestion Service Interface

Abstract interface for feature suggestion service operations.
"""

from abc import ABC, abstractmethod


class IFeatureSuggestionService(ABC):
    """Abstract interface for feature suggestion service operations."""

    @abstractmethod
    async def get_feature_suggestions(self, user_id: str, team_id: str) -> list[str]:
        """
        Get personalized feature suggestions for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            List of feature suggestions
        """
        pass

    @abstractmethod
    async def get_contextual_suggestions(
        self, user_id: str, team_id: str, current_context: str
    ) -> list[str]:
        """
        Get contextual suggestions based on current activity.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            current_context: Current activity context

        Returns:
            List of contextual suggestions
        """
        pass

    @abstractmethod
    async def get_workflow_suggestions(
        self, user_id: str, team_id: str, current_task: str
    ) -> list[str]:
        """
        Get workflow suggestions for a specific task.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            current_task: The current task being performed

        Returns:
            List of workflow suggestions
        """
        pass
