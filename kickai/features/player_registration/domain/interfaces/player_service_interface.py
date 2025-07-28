from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IPlayerService(ABC):
    @abstractmethod
    async def create_player(self, player_data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_player(self, player_id: str, team_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_player(self, player_id: str, updates: Dict[str, Any], team_id: str) -> bool:
        pass

    @abstractmethod
    async def delete_player(self, player_id: str, team_id: str) -> bool:
        pass

    @abstractmethod
    async def list_players(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def find_player_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        pass
