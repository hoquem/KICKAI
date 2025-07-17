"""
Base Health Check

This module provides the base class for all health checks.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """Status of a health check."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class CheckCategory(Enum):
    """Categories of health checks."""
    LLM = "LLM"
    AGENT = "AGENT"
    TOOL = "TOOL"
    TASK = "TASK"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    CONFIGURATION = "CONFIGURATION"
    DATABASE = "DATABASE"
    TELEGRAM = "TELEGRAM"


@dataclass
class CheckResult:
    """Result of a health check."""
    name: str
    category: CheckCategory
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error: Optional[Exception] = None


class HealthCheck(ABC):
    """Abstract base class for health checks."""
    
    def __init__(self, name: str, category: CheckCategory, critical: bool = True):
        self.name = name
        self.category = category
        self.critical = critical
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        """Execute the health check."""
        pass
    
    def __str__(self) -> str:
        return f"{self.category.value}:{self.name}"
    
    def _measure_duration(self, func):
        """Decorator to measure execution duration."""
        async def wrapper(*args, **kwargs):
            start_time = asyncio.get_event_loop().time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                if hasattr(result, 'duration_ms'):
                    result.duration_ms = duration_ms
                return result
            except Exception as e:
                duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                logger.error(f"Health check {self.name} failed after {duration_ms:.2f}ms: {e}")
                raise
        return wrapper 