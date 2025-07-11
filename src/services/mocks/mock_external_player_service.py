from typing import Dict, Any, Optional, List
import asyncio

from services.interfaces.external_player_service_interface import ExternalPlayerServiceInterface

class MockExternalPlayerService(ExternalPlayerServiceInterface):
    """A mock implementation of ExternalPlayerServiceInterface for testing and demonstration."""

    def __init__(self):
        self._mock_db: Dict[str, Dict[str, Any]] = {
            "ext_player_1": {"name": "External John", "email": "john.e@example.com", "age": 25},
            "ext_player_2": {"name": "External Jane", "email": "jane.e@example.com", "age": 30}
        }
        self._next_id = 3

    async def fetch_player_data(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Simulates fetching player data from an external source."""
        await asyncio.sleep(0.1)  # Simulate network delay
        return self._mock_db.get(external_id)

    async def update_player_data(self, external_id: str, data: Dict[str, Any]) -> bool:
        """Simulates updating player data in an external source."""
        await asyncio.sleep(0.1)  # Simulate network delay
        if external_id in self._mock_db:
            self._mock_db[external_id].update(data)
            return True
        return False

    async def search_player_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulates searching for players based on criteria."""
        await asyncio.sleep(0.1)  # Simulate network delay
        results = []
        for ext_id, player_data in self._mock_db.items():
            match = True
            for key, value in criteria.items():
                if player_data.get(key) != value:
                    match = False
                    break
            if match:
                results.append({"external_id": ext_id, **player_data})
        return results

    async def create_external_player(self, data: Dict[str, Any]) -> Optional[str]:
        """Simulates creating a new player record in the external system."""
        await asyncio.sleep(0.1)  # Simulate network delay
        new_id = f"ext_player_{self._next_id}"
        self._mock_db[new_id] = data
        self._next_id += 1
        return new_id
