"""
Bot Status Service Interface

This module defines the interface for bot status and health monitoring operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class IBotStatusService(ABC):
    """Interface for bot status and health monitoring operations."""
    
    @abstractmethod
    async def get_bot_status(self, team_id: str) -> Dict[str, Any]:
        """
        Get the current status of a bot for a team.
        
        Args:
            team_id: The team ID to get status for
            
        Returns:
            Dictionary containing bot status information
        """
        pass
    
    @abstractmethod
    async def update_bot_status(self, team_id: str, status: Dict[str, Any]) -> bool:
        """
        Update the status of a bot for a team.
        
        Args:
            team_id: The team ID to update status for
            status: Dictionary containing status information
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_bot_health(self, team_id: str) -> Dict[str, Any]:
        """
        Get the health status of a bot for a team.
        
        Args:
            team_id: The team ID to get health for
            
        Returns:
            Dictionary containing health information
        """
        pass
    
    @abstractmethod
    async def record_bot_activity(self, team_id: str, activity_type: str, 
                                details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record bot activity for monitoring.
        
        Args:
            team_id: The team ID
            activity_type: Type of activity
            details: Optional details about the activity
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_bot_activity_log(self, team_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the activity log for a bot.
        
        Args:
            team_id: The team ID
            limit: Maximum number of entries to return
            
        Returns:
            List of activity log entries
        """
        pass 