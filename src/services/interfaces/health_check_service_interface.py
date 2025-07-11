"""
Health Check Service Interface

This module defines the interface for the HealthCheckService.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from services.health_check_types import SystemHealthReport, ComponentType


class IHealthCheckService(ABC):
    """Interface for health check service."""
    
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
        """Export health report to JSON file."""
        pass
    
    @abstractmethod
    def set_check_interval(self, interval_seconds: int) -> None:
        """Set the health check interval."""
        pass
    
    @abstractmethod
    def add_custom_check(self, name: str, component_type: ComponentType, check_func: callable) -> None:
        """Add a custom health check."""
        pass 