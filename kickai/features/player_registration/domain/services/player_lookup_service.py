import logging

from kickai.database.interfaces import DataStoreInterface
from typing import Optional

logger = logging.getLogger(__name__)


class PlayerLookupService:
    def __init__(self, data_store: DataStoreInterface):
        self._data_store = data_store

    async def get_player_team_id(self, player_id: str) -> Optional[str]:
        try:
            player_data = await self._data_store.get_document("players", player_id)
            if player_data:
                return player_data.get("team_id")
            return None
        except Exception as e:
            logger.error(f"Failed to get team ID for player {player_id}: {e}")
            return None

    async def player_exists(self, player_id: str) -> bool:
        try:
            player_data = await self._data_store.get_document("players", player_id)
            return player_data is not None
        except Exception as e:
            logger.error(f"Failed to check if player {player_id} exists: {e}")
            return False
