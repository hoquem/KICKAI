"""
Background Tasks Service Interface

This interface defines the contract for background task management services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IBackgroundTasksService(ABC):
    """Interface for background task management services."""
    
    @abstractmethod
    async def start_all_background_tasks(self, team_id: str) -> None:
        """
        Start all background tasks for a team.
        
        Args:
            team_id: The team ID to start tasks for
        """
        pass
    
    @abstractmethod
    async def stop_all_tasks(self) -> None:
        """Stop all background tasks."""
        pass
    
    @abstractmethod
    async def get_task_status(self) -> Dict[str, Any]:
        """
        Get status of all background tasks.
        
        Returns:
            Dictionary containing task status information
        """
        pass 