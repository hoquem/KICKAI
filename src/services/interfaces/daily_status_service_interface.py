"""
Daily Status Service Interface

This module defines the interface for daily status reporting operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class IDailyStatusService(ABC):
    """Interface for daily status reporting operations."""
    
    @abstractmethod
    async def generate_daily_status(self, team_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive daily status report for a team.
        
        Args:
            team_id: The team ID to generate status for
            
        Returns:
            Dictionary containing daily status information
        """
        pass
    
    @abstractmethod
    async def get_player_status_summary(self, team_id: str) -> Dict[str, Any]:
        """
        Get a summary of player statuses for a team.
        
        Args:
            team_id: The team ID to get status for
            
        Returns:
            Dictionary containing player status summary
        """
        pass
    
    @abstractmethod
    async def get_fa_registration_summary(self, team_id: str) -> Dict[str, Any]:
        """
        Get a summary of FA registration status for a team.
        
        Args:
            team_id: The team ID to get FA status for
            
        Returns:
            Dictionary containing FA registration summary
        """
        pass
    
    @abstractmethod
    async def get_onboarding_summary(self, team_id: str) -> Dict[str, Any]:
        """
        Get a summary of player onboarding status for a team.
        
        Args:
            team_id: The team ID to get onboarding status for
            
        Returns:
            Dictionary containing onboarding summary
        """
        pass 