"""
Domain interface for utility operations.

This interface defines the contract for utility-related operations
without depending on the application layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class IUtilityOperations(ABC):
    """Interface for utility operations."""
    
    @abstractmethod
    async def check_fa_registration(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Check FA registration status for a player."""
        pass
    
    @abstractmethod
    async def get_daily_status(self, team_id: str) -> str:
        """Get daily status report."""
        pass
    
    @abstractmethod
    async def run_background_tasks(self, team_id: str) -> str:
        """Run background tasks."""
        pass
    
    @abstractmethod
    async def send_reminder(self, message: str, team_id: str) -> tuple[bool, str]:
        """Send a reminder to team members."""
        pass
    
    @abstractmethod
    async def generate_invitation(self, identifier: str, team_id: str) -> tuple[bool, str]:
        """Generate an invitation for a player."""
        pass
    
    @abstractmethod
    async def broadcast_message(self, message: str, team_id: str) -> tuple[bool, str]:
        """Broadcast a message to team members."""
        pass
    
    @abstractmethod
    async def announce(self, message: str, team_id: str) -> tuple[bool, str]:
        """Send an announcement."""
        pass
    
    @abstractmethod
    async def get_user_role(self, user_id: str, team_id: str) -> str:
        """Get user role for permission checking."""
        pass 