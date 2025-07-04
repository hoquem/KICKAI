"""
FA Registration Checker Interface

This module defines the interface for FA registration checking operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

from .player_service_interface import IPlayerService


class IFARegistrationChecker(ABC):
    """Interface for FA registration checking operations."""
    
    @abstractmethod
    async def scrape_team_page(self) -> Dict[str, bool]:
        """
        Scrape the FA team page to get registered players.
        
        Returns:
            Dict mapping player names to registration status (True = registered)
        """
        pass
    
    @abstractmethod
    async def check_player_registration(self, team_id: str) -> Dict[str, bool]:
        """
        Check FA registration status for all players in a team.
        
        Args:
            team_id: The team ID to check players for
            
        Returns:
            Dict mapping player IDs to registration status updates
        """
        pass
    
    @abstractmethod
    async def scrape_fixtures(self) -> List[Dict]:
        """
        Scrape fixtures and match results from FA website.
        
        Returns:
            List of fixture/match data
        """
        pass 