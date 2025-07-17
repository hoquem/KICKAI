from abc import ABC, abstractmethod
from typing import Dict, Any

class IMonitoringService(ABC):
    @abstractmethod
    async def perform_system_health_check(self) -> Dict[str, Any]:
        pass
    @abstractmethod
    async def get_system_metrics(self) -> Dict[str, Any]:
        pass
    @abstractmethod
    def log_system_event(self, event_type: str, message: str, level: str = "info") -> None:
        pass
    @abstractmethod
    async def check_service_dependencies(self) -> Dict[str, bool]:
        pass 