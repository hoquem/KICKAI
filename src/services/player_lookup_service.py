"""
Player Lookup Service

This service provides minimal player lookup functionality to break circular dependencies
between services that only need basic player information.
"""

import logging
from typing import Optional

from database.interfaces import DataStoreInterface

logger = logging.getLogger(__name__)


class PlayerLookupService:
    """Service for minimal player lookup operations."""
    
    def __init__(self, data_store: DataStoreInterface):
        self._data_store = data_store
    
    async def get_player_team_id(self, player_id: str) -> Optional[str]:
        """
        Get the team ID for a player.
        
        Args:
            player_id: The player ID
            
        Returns:
            The team ID if found, None otherwise
        """
        try:
            player_data = await self._data_store.get_document('players', player_id)
            if player_data:
                return player_data.get('team_id')
            return None
        except Exception as e:
            logger.error(f"Failed to get team ID for player {player_id}: {e}")
            return None
    
    async def player_exists(self, player_id: str) -> bool:
        """
        Check if a player exists.
        
        Args:
            player_id: The player ID
            
        Returns:
            True if player exists, False otherwise
        """
        try:
            player_data = await self._data_store.get_document('players', player_id)
            return player_data is not None
        except Exception as e:
            logger.error(f"Failed to check if player {player_id} exists: {e}")
            return False 