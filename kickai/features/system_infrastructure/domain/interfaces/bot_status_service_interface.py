#!/usr/bin/env python3
"""
Bot Status Service Interface

Defines the contract for bot status monitoring services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class IBotStatusService(ABC):
    """Interface for bot status service operations."""

    @abstractmethod
    async def get_bot_status(self) -> Dict[str, Any]:
        """
        Get current bot status information.
        
        Returns:
            Dictionary containing bot status details
        """
        pass

    @abstractmethod
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health information.
        
        Returns:
            Dictionary containing system health metrics
        """
        pass

    @abstractmethod
    async def record_bot_activity(
        self,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None
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
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
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
    async def check_service_dependencies(self) -> Dict[str, bool]:
        """
        Check status of all service dependencies.
        
        Returns:
            Dictionary mapping service names to their availability status
        """
        pass

    @abstractmethod
    async def get_error_summary(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
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