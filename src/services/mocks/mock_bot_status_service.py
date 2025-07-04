"""
Mock Bot Status Service

This module provides a mock implementation of the BotStatusService interface
for testing purposes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..interfaces.bot_status_service_interface import IBotStatusService


class MockBotStatusService(IBotStatusService):
    """Mock implementation of BotStatusService for testing."""
    
    def __init__(self):
        self._bot_status: Dict[str, Dict[str, Any]] = {}
        self._activity_log: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_bot_status(self, team_id: str) -> Dict[str, Any]:
        """Get the current status of a bot for a team."""
        status = self._bot_status.get(team_id, {
            "status": "online",
            "last_activity": datetime.now().isoformat(),
            "uptime": "24h",
            "version": "1.0.0"
        })
        self.logger.info(f"Mock: Retrieved bot status for team {team_id}")
        return status
    
    async def update_bot_status(self, team_id: str, status: Dict[str, Any]) -> bool:
        """Update the status of a bot for a team."""
        self._bot_status[team_id] = status
        self.logger.info(f"Mock: Updated bot status for team {team_id}")
        return True
    
    async def get_bot_health(self, team_id: str) -> Dict[str, Any]:
        """Get the health status of a bot for a team."""
        health = {
            "status": "healthy",
            "memory_usage": "45%",
            "cpu_usage": "12%",
            "response_time": "150ms",
            "last_check": datetime.now().isoformat()
        }
        self.logger.info(f"Mock: Retrieved bot health for team {team_id}")
        return health
    
    async def record_bot_activity(self, team_id: str, activity_type: str, 
                                details: Optional[Dict[str, Any]] = None) -> bool:
        """Record bot activity for monitoring."""
        if team_id not in self._activity_log:
            self._activity_log[team_id] = []
        
        activity = {
            "type": activity_type,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self._activity_log[team_id].append(activity)
        self.logger.info(f"Mock: Recorded activity {activity_type} for team {team_id}")
        return True
    
    async def get_bot_activity_log(self, team_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the activity log for a bot."""
        activities = self._activity_log.get(team_id, [])
        if limit:
            activities = activities[-limit:]
        self.logger.info(f"Mock: Retrieved {len(activities)} activities for team {team_id}")
        return activities
    
    def reset(self):
        """Reset the mock service state."""
        self._bot_status.clear()
        self._activity_log.clear()
        self.logger.info("Mock: Bot status service reset") 