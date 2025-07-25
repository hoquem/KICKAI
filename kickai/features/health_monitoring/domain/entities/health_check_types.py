"""
Health Check Types

This module contains the data structures and types used by the health check service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Union


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Component type enumeration."""
    AGENT = "agent"
    TOOL = "tool"
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"
    EXTERNAL = "external"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component_name: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)
    error: Union[Exception, None] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component_name": self.component_name,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "message": self.message,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "error": str(self.error) if self.error else None
        }


@dataclass
class SystemHealthReport:
    """Complete system health report."""
    timestamp: datetime
    team_id: str
    overall_status: HealthStatus
    components: dict[str, dict[str, Any]] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    execution_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "team_id": self.team_id,
            "overall_status": self.overall_status.value,
            "components": self.components,
            "recommendations": self.recommendations,
            "execution_time": self.execution_time
        }
