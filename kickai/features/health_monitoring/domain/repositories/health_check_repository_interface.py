from abc import ABC, abstractmethod
from typing import Any, Union


class HealthCheckRepositoryInterface(ABC):
    @abstractmethod
    async def save(self, health_check: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, check_id: str) -> Union[dict[str, Any], None]:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def update(self, check_id: str, updates: dict[str, Any]) -> bool:
        pass
