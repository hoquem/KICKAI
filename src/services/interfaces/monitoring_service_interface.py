"""
Monitoring Service Interface

This module defines the interface for system monitoring and metrics operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class IMonitoringService(ABC):
    """Interface for system monitoring and metrics operations."""
    
    @abstractmethod
    async def record_metric(self, metric_name: str, value: float, 
                          tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for the metric
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_metric(self, metric_name: str, 
                        tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """
        Get a metric value.
        
        Args:
            metric_name: Name of the metric
            tags: Optional tags to filter by
            
        Returns:
            Metric value or None if not found
        """
        pass
    
    @abstractmethod
    async def get_metrics_summary(self, time_range: str = "1h") -> Dict[str, Any]:
        """
        Get a summary of all metrics for a time range.
        
        Args:
            time_range: Time range to get metrics for (e.g., "1h", "24h", "7d")
            
        Returns:
            Dictionary containing metrics summary
        """
        pass
    
    @abstractmethod
    async def record_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Record an event for monitoring.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_events(self, event_type: Optional[str] = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get events for monitoring.
        
        Args:
            event_type: Optional event type to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the system.
        
        Returns:
            Dictionary containing health check results
        """
        pass 