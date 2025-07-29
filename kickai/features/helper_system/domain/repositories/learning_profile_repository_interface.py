"""
Learning Profile Repository Interface

Abstract interface for managing learning profiles in the Helper System.
"""

from abc import ABC, abstractmethod
from typing import Any

from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile


class LearningProfileRepositoryInterface(ABC):
    """Abstract interface for learning profile repository operations."""

    @abstractmethod
    async def get_profile(self, user_id: str, team_id: str) -> LearningProfile | None:
        """
        Get a user's learning profile.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            LearningProfile if found, None otherwise
        """
        pass

    @abstractmethod
    async def save_profile(self, profile: LearningProfile) -> LearningProfile:
        """
        Save a learning profile.

        Args:
            profile: The learning profile to save

        Returns:
            The saved learning profile
        """
        pass

    @abstractmethod
    async def update_profile(
        self, user_id: str, team_id: str, updates: dict[str, Any]
    ) -> LearningProfile | None:
        """
        Update a learning profile with specific fields.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            updates: Dictionary of fields to update

        Returns:
            Updated LearningProfile if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_command_usage(self, user_id: str, team_id: str, command: str) -> None:
        """
        Update command usage statistics for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            command: The command that was used
        """
        pass

    @abstractmethod
    async def add_help_request(
        self, user_id: str, team_id: str, help_request: "HelpRequest"
    ) -> None:
        """
        Add a help request to a user's profile.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            help_request: The help request to add
        """
        pass

    @abstractmethod
    async def get_team_profiles(self, team_id: str) -> list[LearningProfile]:
        """
        Get all learning profiles for a team.

        Args:
            team_id: The team's ID

        Returns:
            List of learning profiles for the team
        """
        pass

    @abstractmethod
    async def get_active_profiles(
        self, team_id: str, days_threshold: int = 7
    ) -> list[LearningProfile]:
        """
        Get active learning profiles for a team.

        Args:
            team_id: The team's ID
            days_threshold: Number of days to consider "active"

        Returns:
            List of active learning profiles
        """
        pass

    @abstractmethod
    async def delete_profile(self, user_id: str, team_id: str) -> bool:
        """
        Delete a learning profile.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def get_profiles_by_experience_level(
        self, team_id: str, level: str
    ) -> list[LearningProfile]:
        """
        Get profiles by experience level.

        Args:
            team_id: The team's ID
            level: The experience level to filter by

        Returns:
            List of learning profiles with the specified level
        """
        pass

    @abstractmethod
    async def get_most_active_users(self, team_id: str, limit: int = 10) -> list[LearningProfile]:
        """
        Get the most active users in a team.

        Args:
            team_id: The team's ID
            limit: Maximum number of users to return

        Returns:
            List of most active learning profiles
        """
        pass
