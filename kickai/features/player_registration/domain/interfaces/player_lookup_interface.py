
"""
Player Lookup Interface

This interface provides a minimal contract for looking up player information
without creating circular dependencies between services.
"""

from abc import ABC, abstractmethod


class IPlayerLookup(ABC):
    """Interface for player lookup operations."""

    @abstractmethod
    async def get_player_team_id(self, player_id: str) -> str | None:
        """
        Get the team ID for a player.


            player_id: The player ID


    :return: The team ID if found, None otherwise
    :rtype: str  # TODO: Fix type
        """
        pass

    @abstractmethod
    async def player_exists(self, player_id: str) -> bool:
        """
        Check if a player exists.


            player_id: The player ID


    :return: True if player exists, False otherwise
    :rtype: str  # TODO: Fix type
        """
        pass
