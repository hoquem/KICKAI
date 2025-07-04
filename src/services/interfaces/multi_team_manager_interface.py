"""
Multi Team Manager Interface

This module defines the interface for multi-team management operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class IMultiTeamManager(ABC):
    """Interface for multi-team management operations."""
    
    @abstractmethod
    async def get_all_teams(self) -> List[Dict[str, Any]]:
        """
        Get all teams managed by the system.
        
        Returns:
            List of team information dictionaries
        """
        pass
    
    @abstractmethod
    async def get_team_info(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific team.
        
        Args:
            team_id: The team ID to get info for
            
        Returns:
            Team information dictionary or None if not found
        """
        pass
    
    @abstractmethod
    async def create_team(self, team_data: Dict[str, Any]) -> str:
        """
        Create a new team.
        
        Args:
            team_data: Team data dictionary
            
        Returns:
            Team ID of the created team
        """
        pass
    
    @abstractmethod
    async def update_team(self, team_id: str, team_data: Dict[str, Any]) -> bool:
        """
        Update team information.
        
        Args:
            team_id: The team ID to update
            team_data: Updated team data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_team(self, team_id: str) -> bool:
        """
        Delete a team.
        
        Args:
            team_id: The team ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_team_stats(self, team_id: str) -> Dict[str, Any]:
        """
        Get statistics for a team.
        
        Args:
            team_id: The team ID to get stats for
            
        Returns:
            Dictionary containing team statistics
        """
        pass
    
    @abstractmethod
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system-wide statistics.
        
        Returns:
            Dictionary containing system statistics
        """
        pass 