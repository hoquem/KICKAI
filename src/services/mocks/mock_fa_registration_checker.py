"""
Mock FA Registration Checker

This module provides a mock implementation of the FARegistrationChecker interface
for testing purposes.
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..interfaces.fa_registration_checker_interface import IFARegistrationChecker
from ..interfaces.player_service_interface import IPlayerService


class MockFARegistrationChecker(IFARegistrationChecker):
    """Mock implementation of FARegistrationChecker for testing."""
    
    def __init__(self, player_service: IPlayerService):
        self.player_service = player_service
        self._registered_players: Dict[str, bool] = {}
        self.logger = logging.getLogger(__name__)
    
    async def scrape_team_page(self) -> Dict[str, bool]:
        """
        Mock scraping of the FA team page.
        
        Returns:
            Dict mapping player names to registration status (True = registered)
        """
        self.logger.info("Mock: Scraping FA team page")
        return self._registered_players.copy()
    
    async def check_player_registration(self, team_id: str) -> Dict[str, bool]:
        """
        Mock checking FA registration status for all players in a team.
        
        Args:
            team_id: The team ID to check players for
            
        Returns:
            Dict mapping player IDs to registration status updates
        """
        self.logger.info(f"Mock: Checking FA registration for team {team_id}")
        
        # Get all players for the team
        players = await self.player_service.get_team_players(team_id)
        
        updates = {}
        for player in players:
            player_name = player.name.lower()
            is_registered = player_name in self._registered_players
            
            if is_registered and not player.fa_registered:
                updates[player.id] = True
                # Update player in database
                await self.player_service.update_player(
                    player.id,
                    fa_registered=True,
                    fa_registration_date=datetime.now()
                )
        
        self.logger.info(f"Mock: Updated {len(updates)} players as FA registered")
        return updates
    
    async def scrape_fixtures(self) -> List[Dict]:
        """
        Mock scraping fixtures and match results from FA website.
        
        Returns:
            List of fixture/match data
        """
        self.logger.info("Mock: Scraping FA fixtures")
        return [
            {
                'text': 'KICKAI vs Thunder FC - 2-1 Win',
                'timestamp': datetime.now().isoformat()
            },
            {
                'text': 'Lightning United vs KICKAI - 1-1 Draw',
                'timestamp': datetime.now().isoformat()
            }
        ]
    
    def set_registered_players(self, players: List[str]):
        """Set which players are registered for testing."""
        self._registered_players = {name.lower(): True for name in players}
        self.logger.info(f"Mock: Set {len(players)} registered players")
    
    def reset(self):
        """Reset the mock service state."""
        self._registered_players.clear()
        self.logger.info("Mock: FA registration checker reset") 