from abc import ABC, abstractmethod
from typing import Any


class IPlayerService(ABC):
    @abstractmethod
    async def create_player(self, player_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_player(self, player_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def update_player(self, player_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_player(self, player_id: str) -> bool:
        pass

    @abstractmethod
    async def list_players(self, team_id: str | None = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def find_player_by_phone(self, phone: str) -> dict[str, Any] | None:
        pass
