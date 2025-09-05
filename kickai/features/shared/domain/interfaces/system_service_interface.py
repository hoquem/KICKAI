#!/usr/bin/env python3
"""
System Service Interface - Clean Architecture Domain Layer

This module defines the interface for system service operations.
Following Clean Architecture principles, this interface defines the contract
that system service implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any


class ISystemService(ABC):
    """Interface for system service operations."""

    @abstractmethod
    def perform_ping(self) -> Any:
        """
        Perform a system ping test to check connectivity and response time.

        Returns:
            Ping result object with timing and status information
        """
        pass

    @abstractmethod
    def format_ping_response(self, ping_result: Any) -> str:
        """
        Format ping result into a displayable message.

        Args:
            ping_result: The ping result to format

        Returns:
            Formatted ping response string
        """
        pass

    @abstractmethod
    def get_system_info(self) -> Any:
        """
        Get current system information including version and capabilities.

        Returns:
            System information object with version, build, and feature details
        """
        pass

    @abstractmethod
    def format_version_response(self, system_info: Any) -> str:
        """
        Format system information into a displayable message.

        Args:
            system_info: The system information to format

        Returns:
            Formatted version response string
        """
        pass

    @abstractmethod
    def get_system_health(self) -> Any:
        """
        Perform comprehensive system health check.

        Returns:
            Health report object with service availability and system metrics
        """
        pass

    @abstractmethod
    def format_health_report(self, health_report: Any) -> str:
        """
        Format health report into a displayable message.

        Args:
            health_report: The health report to format

        Returns:
            Formatted health report string
        """
        pass

    @abstractmethod
    def get_system_status(self) -> Any:
        """
        Get current system operational status.

        Returns:
            Status information object with uptime and operational details
        """
        pass

    @abstractmethod
    def format_status_response(self, status_info: Any) -> str:
        """
        Format status information into a displayable message.

        Args:
            status_info: The status information to format

        Returns:
            Formatted status response string
        """
        pass
