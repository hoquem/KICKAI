"""
Monitoring Service Interface

This interface defines the contract for system monitoring services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IMonitoringService(ABC):
    """Interface for system monitoring services."""
    
    @abstractmethod
    async def perform_system_health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive system health check.
        
        Returns:
            Dictionary containing health check results
        """
        pass
    
    @abstractmethod
    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system metrics and statistics.
        
        Returns:
            Dictionary containing system metrics
        """
        pass
    
    @abstractmethod
    def log_system_event(self, event_type: str, message: str, level: str = "info") -> None:
        """
        Log a system event.
        
        Args:
            event_type: Type of event
            message: Event message
            level: Log level (info, warning, error)
        """
        pass
    
    @abstractmethod
    async def check_service_dependencies(self) -> Dict[str, bool]:
        """
        Check if all service dependencies are available.
        
        Returns:
            Dictionary mapping service names to availability status
        """
        pass 