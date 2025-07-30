"""
Command Help Service Interface

Abstract interface for command help service operations.
"""

from abc import ABC, abstractmethod


class ICommandHelpService(ABC):
    """Abstract interface for command help service operations."""

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
    async def get_command_examples(self, command_name: str) -> list[str]:
        """
        Get examples for a specific command.

        Args:
            command_name: The command to get examples for

        Returns:
            List of command examples
        """
        pass

    @abstractmethod
    async def get_command_tips(self, command_name: str, user_level: str) -> list[str]:
        """
        Get tips for a specific command based on user level.

        Args:
            command_name: The command to get tips for
            user_level: The user's experience level

        Returns:
            List of command tips
        """
        pass

    @abstractmethod
    async def get_related_commands(self, command_name: str) -> list[str]:
        """
        Get related commands for a specific command.

        Args:
            command_name: The command to get related commands for

        Returns:
            List of related commands
        """
        pass
