from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class HealthCheckRepositoryInterface(ABC):
    @abstractmethod
    async def save(self, health_check: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, check_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update(self, check_id: str, updates: Dict[str, Any]) -> bool:
        pass
