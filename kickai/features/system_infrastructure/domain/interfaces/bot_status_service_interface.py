#!/usr/bin/env python3
"""
Bot Status Service Interface

Defines the contract for bot status monitoring services.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class IBotStatusService(ABC):
    """Interface for bot status service operations."""

    @abstractmethod
    async def get_bot_status(self) -> dict[str, Any]:
        """
        Get current bot status information.

        Returns:
            Dictionary containing bot status details
        """
        pass

    @abstractmethod
    async def get_system_health(self) -> dict[str, Any]:
        """
        Get comprehensive system health information.

        Returns:
            Dictionary containing system health metrics
        """
        pass

    @abstractmethod
    async def record_bot_activity(
        self, activity_type: str, details: dict[str, Any] | None = None
    ) -> bool:
        """
        Record bot activity for monitoring.

        Args:
            activity_type: Type of activity (message_processed, command_executed, etc.)
            details: Additional activity details

        Returns:
            True if successfully recorded
        """
        pass

    @abstractmethod
    async def get_activity_metrics(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> dict[str, Any]:
        """
        Get bot activity metrics for a time period.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Dictionary containing activity metrics
        """
        pass

    @abstractmethod
    async def check_service_dependencies(self) -> dict[str, bool]:
        """
        Check status of all service dependencies.

        Returns:
            Dictionary mapping service names to their availability status
        """
        pass

    @abstractmethod
    async def get_error_summary(self, hours: int = 24) -> dict[str, Any]:
        """
        Get summary of errors in the specified time period.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary containing error summary information
        """
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Quick health check for the bot.

        Returns:
            True if bot is healthy and operational
        """
        pass
