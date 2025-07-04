"""
Mock Monitoring Service

This module provides a mock implementation of the MonitoringService interface
for testing purposes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..interfaces.monitoring_service_interface import IMonitoringService


class MockMonitoringService(IMonitoringService):
    """Mock implementation of MonitoringService for testing."""
    
    def __init__(self):
        self._metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._events: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    async def record_metric(self, metric_name: str, value: float, 
                          tags: Optional[Dict[str, str]] = None) -> bool:
        """Record a metric value."""
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        
        metric = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or {}
        }
        
        self._metrics[metric_name].append(metric)
        self.logger.info(f"Mock: Recorded metric {metric_name}: {value}")
        return True
    
    async def get_metric(self, metric_name: str, 
                        tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get a metric value."""
        if metric_name not in self._metrics:
            return None
        
        metrics = self._metrics[metric_name]
        if not metrics:
            return None
        
        # Return the latest value
        return metrics[-1]["value"]
    
    async def get_metrics_summary(self, time_range: str = "1h") -> Dict[str, Any]:
        """Get a summary of all metrics for a time range."""
        summary = {
            "time_range": time_range,
            "total_metrics": len(self._metrics),
            "metrics": {}
        }
        
        for metric_name, values in self._metrics.items():
            if values:
                summary["metrics"][metric_name] = {
                    "latest": values[-1]["value"],
                    "count": len(values)
                }
        
        self.logger.info(f"Mock: Retrieved metrics summary for {time_range}")
        return summary
    
    async def record_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Record an event for monitoring."""
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self._events.append(event)
        self.logger.info(f"Mock: Recorded event {event_type}")
        return True
    
    async def get_events(self, event_type: Optional[str] = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Get events for monitoring."""
        events = self._events
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        if limit:
            events = events[-limit:]
        
        self.logger.info(f"Mock: Retrieved {len(events)} events")
        return events
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the system."""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics_count": len(self._metrics),
            "events_count": len(self._events),
            "uptime": "24h"
        }
        self.logger.info("Mock: Performed health check")
        return health
    
    def reset(self):
        """Reset the mock service state."""
        self._metrics.clear()
        self._events.clear()
        self.logger.info("Mock: Monitoring service reset") 