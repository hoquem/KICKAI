from abc import ABC, abstractmethod
from typing import Any


class IMonitoringService(ABC):
    @abstractmethod
    async def perform_system_health_check(self) -> dict[str, Any]:
        pass
    @abstractmethod
    async def get_system_metrics(self) -> dict[str, Any]:
        pass
    @abstractmethod
    def log_system_event(self, event_type: str, message: str, level: str = "info") -> None:
        pass
    @abstractmethod
    async def check_service_dependencies(self) -> dict[str, bool]:
        pass
