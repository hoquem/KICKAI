from abc import ABC, abstractmethod
from typing import Any


class IExternalPlayerService(ABC):
    @abstractmethod
    async def get_external_player(self, external_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def find_external_player_by_phone(self, phone: str) -> dict[str, Any] | None:
        pass
