"""
Health Check Types

This module contains the data structures and types used by the health check service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


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
    DATABASE = "database"
    LLM = "llm"
    PAYMENT_GATEWAY = "payment_gateway"
    TELEGRAM = "telegram"
    EXTERNAL_API = "external_api"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component_name: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None
    
    def to_dict(self) -> Dict[str, Any]:
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
    overall_status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheckResult] = field(default_factory=list)
    summary: Dict[ComponentType, Dict[HealthStatus, int]] = field(default_factory=dict)
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    def add_check(self, check: HealthCheckResult) -> None:
        """Add a health check result to the report."""
        self.checks.append(check)
        
        # Update summary
        if check.component_type not in self.summary:
            self.summary[check.component_type] = {status: 0 for status in HealthStatus}
        self.summary[check.component_type][check.status] += 1
        
        # Track critical failures and warnings
        if check.status == HealthStatus.UNHEALTHY:
            self.critical_issues.append(f"{check.component_type.value}: {check.component_name} - {check.message}")
        elif check.status == HealthStatus.DEGRADED:
            self.warnings.append(f"{check.component_type.value}: {check.component_name} - {check.message}")

    def is_healthy(self) -> bool:
        """Check if the system is healthy (no critical failures)."""
        return len(self.critical_issues) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "overall_status": self.overall_status.value,
            "timestamp": self.timestamp.isoformat(),
            "checks": [check.to_dict() for check in self.checks],
            "summary": {
                comp_type.value: {status.value: count for status, count in comp_summary.items()}
                for comp_type, comp_summary in self.summary.items()
            },
            "critical_issues": self.critical_issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "performance_metrics": self.performance_metrics
        } 