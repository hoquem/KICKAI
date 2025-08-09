from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IMatchService(ABC):
    @abstractmethod
    async def create_match(self, match_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_match(self, match_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_match(self, match_id: str) -> bool:
        pass

    @abstractmethod
    async def list_matches(self, team_id: str, status: Optional[str] = None) -> list[dict[str, Any]]:
        pass
