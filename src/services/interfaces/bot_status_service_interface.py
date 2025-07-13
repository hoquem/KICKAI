"""
Bot Status Service Interface

This interface defines the contract for bot status monitoring services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IBotStatusService(ABC):
    """Interface for bot status monitoring services."""
    
    @abstractmethod
    def get_bot_status(self) -> Dict[str, Any]:
        """
        Get the current bot status.
        
        Returns:
            Dictionary containing bot status information
        """
        pass
    
    @abstractmethod
    def is_bot_running(self) -> bool:
        """
        Check if the bot is currently running.
        
        Returns:
            True if bot is running, False otherwise
        """
        pass
    
    @abstractmethod
    def get_uptime(self) -> str:
        """
        Get the bot uptime as a formatted string.
        
        Returns:
            Formatted uptime string
        """
        pass 