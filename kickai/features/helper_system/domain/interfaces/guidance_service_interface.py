"""
Guidance Service Interface

Abstract interface for guidance service operations.
"""

from abc import ABC, abstractmethod
from typing import Any


class IGuidanceService(ABC):
    """Abstract interface for guidance service operations."""

    @abstractmethod
    async def get_command_help(self, command_name: str, user_level: str = "beginner") -> str:
        """
        Get contextual help for a command based on user level.

        Args:
            command_name: The command to get help for
            user_level: The user's experience level

        Returns:
            Formatted help content
        """
        pass

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
    async def format_help_response(self, help_data: dict[str, Any]) -> str:
        """
        Format help response with emojis and clear structure.

        Args:
            help_data: Dictionary containing help information

        Returns:
            Formatted help response
        """
        pass

    @abstractmethod
    async def get_contextual_tips(self, current_command: str, user_level: str) -> list[str]:
        """
        Get contextual tips based on current command and user level.

        Args:
            current_command: The command being used
            user_level: The user's experience level

        Returns:
            List of contextual tips
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

    @abstractmethod
    async def get_best_practices(self, feature: str, user_level: str) -> list[str]:
        """
        Get best practices for a specific feature.

        Args:
            feature: The feature to get best practices for
            user_level: The user's experience level

        Returns:
            List of best practices
        """
        pass
