"""
Mock Multi Team Manager

This module provides a mock implementation of the MultiTeamManager interface
for testing purposes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..interfaces.multi_team_manager_interface import IMultiTeamManager


class MockMultiTeamManager(IMultiTeamManager):
    """Mock implementation of MultiTeamManager for testing."""
    
    def __init__(self):
        self._teams: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
        self.logger = logging.getLogger(__name__)
    
    async def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all teams managed by the system."""
        teams = list(self._teams.values())
        self.logger.info(f"Mock: Retrieved {len(teams)} teams")
        return teams
    
    async def get_team_info(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific team."""
        team_info = self._teams.get(team_id)
        if team_info:
            self.logger.info(f"Mock: Retrieved team info for {team_id}")
        return team_info
    
    async def create_team(self, team_data: Dict[str, Any]) -> str:
        """Create a new team."""
        team_id = f"T{self._next_id:03d}"
        self._next_id += 1
        
        team_info = {
            "id": team_id,
            "name": team_data.get("name", "Unknown Team"),
            "description": team_data.get("description"),
            "status": team_data.get("status", "active"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **team_data
        }
        
        self._teams[team_id] = team_info
        self.logger.info(f"Mock: Created team {team_info['name']} ({team_id})")
        return team_id
    
    async def update_team(self, team_id: str, team_data: Dict[str, Any]) -> bool:
        """Update team information."""
        if team_id not in self._teams:
            return False
        
        self._teams[team_id].update(team_data)
        self._teams[team_id]["updated_at"] = datetime.now().isoformat()
        self.logger.info(f"Mock: Updated team {team_id}")
        return True
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        if team_id not in self._teams:
            return False
        
        team_name = self._teams[team_id]["name"]
        del self._teams[team_id]
        self.logger.info(f"Mock: Deleted team {team_name} ({team_id})")
        return True
    
    async def get_team_stats(self, team_id: str) -> Dict[str, Any]:
        """Get statistics for a team."""
        if team_id not in self._teams:
            return {}
        
        stats = {
            "team_id": team_id,
            "total_players": 15,
            "active_players": 12,
            "matches_played": 8,
            "wins": 5,
            "draws": 2,
            "losses": 1,
            "goals_for": 18,
            "goals_against": 12,
            "points": 17
        }
        self.logger.info(f"Mock: Retrieved stats for team {team_id}")
        return stats
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        total_teams = len(self._teams)
        total_players = total_teams * 15  # Mock calculation
        
        stats = {
            "total_teams": total_teams,
            "total_players": total_players,
            "active_teams": total_teams,
            "system_uptime": "99.9%",
            "last_updated": datetime.now().isoformat()
        }
        self.logger.info(f"Mock: Retrieved system stats")
        return stats
    
    def reset(self):
        """Reset the mock service state."""
        self._teams.clear()
        self._next_id = 1
        self.logger.info("Mock: Multi team manager reset") 