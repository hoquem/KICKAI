from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IExternalPlayerService(ABC):
    """Abstract base class for external player data services."""

    @abstractmethod
    async def fetch_player_data(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Fetches player data from an external source using their external ID."""
        pass

    @abstractmethod
    async def update_player_data(self, external_id: str, data: Dict[str, Any]) -> bool:
        """Updates player data in an external source using their external ID."""
        pass

    @abstractmethod
    async def search_player_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Searches for players in the external system based on various criteria.
        Criteria could include name, email, phone, etc.
        """
        pass

    @abstractmethod
    async def create_external_player(self, data: Dict[str, Any]) -> Optional[str]:
        """Creates a new player record in the external system and returns their external ID.
        """
        pass

# Backward compatibility alias
ExternalPlayerServiceInterface = IExternalPlayerService
