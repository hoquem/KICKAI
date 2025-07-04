"""
Mock Daily Status Service

This module provides a mock implementation of the DailyStatusService interface
for testing purposes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..interfaces.daily_status_service_interface import IDailyStatusService


class MockDailyStatusService(IDailyStatusService):
    """Mock implementation of DailyStatusService for testing."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_daily_status(self, team_id: str) -> Dict[str, Any]:
        """Generate a comprehensive daily status report for a team."""
        self.logger.info(f"Mock: Generating daily status for team {team_id}")
        
        return {
            "team_id": team_id,
            "date": datetime.now().isoformat(),
            "total_players": 15,
            "active_players": 12,
            "fa_registered": 8,
            "pending_onboarding": 3,
            "completed_onboarding": 10
        }
    
    async def get_player_status_summary(self, team_id: str) -> Dict[str, Any]:
        """Get a summary of player statuses for a team."""
        self.logger.info(f"Mock: Getting player status summary for team {team_id}")
        
        return {
            "team_id": team_id,
            "total_players": 15,
            "active_players": 12,
            "inactive_players": 3,
            "by_position": {
                "goalkeeper": 2,
                "defender": 4,
                "midfielder": 5,
                "forward": 3,
                "utility": 1
            }
        }
    
    async def get_fa_registration_summary(self, team_id: str) -> Dict[str, Any]:
        """Get a summary of FA registration status for a team."""
        self.logger.info(f"Mock: Getting FA registration summary for team {team_id}")
        
        return {
            "team_id": team_id,
            "total_players": 15,
            "fa_registered": 8,
            "not_fa_registered": 7,
            "registration_rate": 53.3
        }
    
    async def get_onboarding_summary(self, team_id: str) -> Dict[str, Any]:
        """Get a summary of player onboarding status for a team."""
        self.logger.info(f"Mock: Getting onboarding summary for team {team_id}")
        
        return {
            "team_id": team_id,
            "total_players": 15,
            "pending": 3,
            "in_progress": 2,
            "completed": 10,
            "completion_rate": 66.7
        }
    
    def reset(self):
        """Reset the mock service state."""
        self.logger.info("Mock: Daily status service reset") 