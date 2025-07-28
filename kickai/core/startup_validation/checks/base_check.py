"""
Base Check

This module provides the base class for all health checks.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..reporting import CheckCategory, CheckResult

logger = logging.getLogger(__name__)


class BaseCheck(ABC):
    """
    Base class for all health checks.

    All health checks should inherit from this class and implement
    the execute method.
    """

    name: str
    category: CheckCategory
    description: str

    @abstractmethod
    async def execute(self, context: Optional[Dict[str, Any]] = None) -> CheckResult:
        """
        Execute the health check.

        Args:
            context: Optional context data for the check

        Returns:
            CheckResult with the check status and details
        """
        pass

    def __str__(self) -> str:
        return f"{self.name} ({self.category.value})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
