from abc import ABC, abstractmethod

from kickai.features.health_monitoring.domain.entities.health_check_types import SystemHealthReport


class IHealthCheckService(ABC):
    """Interface for health check service operations."""

    @abstractmethod
    async def perform_comprehensive_health_check(self) -> SystemHealthReport:
        """Perform a comprehensive health check of all system components."""
        pass

    @abstractmethod
    async def get_current_health_status(self) -> SystemHealthReport:
        """Get the current health status."""
        pass

    @abstractmethod
    async def get_health_history(self, hours: int = 24) -> List[SystemHealthReport]:
        """Get health history for the specified number of hours."""
        pass

    @abstractmethod
    async def export_health_report(self, file_path: Optional[str] = None) -> str:
        """Export health report to file."""
        pass
