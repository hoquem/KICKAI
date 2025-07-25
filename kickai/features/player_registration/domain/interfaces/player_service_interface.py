from abc import ABC, abstractmethod
from typing import Any, Union, Union


class IPlayerService(ABC):
    @abstractmethod
    async def create_player(self, player_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_player(self, player_id: str, team_id: str) -> Union[dict[str, Any], None]:
        pass

    @abstractmethod
    async def update_player(self, player_id: str, updates: dict[str, Any], team_id: str) -> bool:
        pass

    @abstractmethod
    async def delete_player(self, player_id: str, team_id: str) -> bool:
        pass

    @abstractmethod
    async def list_players(self, team_id: Union[str, None] = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def find_player_by_phone(self, phone: str) -> Union[dict[str, Any], None]:
        pass
