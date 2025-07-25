"""
Player Lookup Interface

This interface provides a minimal contract for looking up player information
without creating circular dependencies between services.
"""

from typing import Union
from abc import ABC, abstractmethod


class IPlayerLookup(ABC):
    """Interface for player lookup operations."""

    @abstractmethod
    async def get_player_team_id(self, player_id: str) -> Union[str, None]:
        """
        Get the team ID for a player.

        Args:
            player_id: The player ID

        Returns:
            The team ID if found, None otherwise
        """
        pass

    @abstractmethod
    async def player_exists(self, player_id: str) -> bool:
        """
        Check if a player exists.

        Args:
            player_id: The player ID

        Returns:
            True if player exists, False otherwise
        """
        pass
