import logging

from kickai.features.player_registration.domain.repositories.player_repository_interface import (
    PlayerRepositoryInterface,
)

logger = logging.getLogger(__name__)


class PlayerLookupService:
    """Service for player lookup operations using repository pattern."""

    def __init__(self, player_repository: PlayerRepositoryInterface):
        self._player_repository = player_repository

    async def get_player_team_id(self, player_id: str, team_id: str) -> str | None:
        """
        Get team ID for a player using repository pattern.

        Args:
            player_id: Player identifier
            team_id: Team identifier to scope the search

        Returns:
            Team ID if player exists, None otherwise
        """
        try:
            player = await self._player_repository.get_player_by_id(player_id, team_id)
            if player:
                return player.team_id
            return None
        except Exception as e:
            logger.error(f"Failed to get team ID for player {player_id}: {e}")
            return None

    async def player_exists(self, player_id: str, team_id: str) -> bool:
        """
        Check if a player exists using repository pattern.

        Args:
            player_id: Player identifier
            team_id: Team identifier to scope the search

        Returns:
            True if player exists, False otherwise
        """
        try:
            player = await self._player_repository.get_player_by_id(player_id, team_id)
            return player is not None
        except Exception as e:
            logger.error(f"Failed to check if player {player_id} exists: {e}")
            return False
