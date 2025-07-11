"""
Application layer adapter for team operations.

This adapter implements the domain interface by wrapping the application layer services.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TeamOperationsAdapter:
    """Adapter that wraps the team service to implement domain interface."""
    
    def __init__(self, team_service):
        self.team_service = team_service
        self.logger = logging.getLogger(__name__)

    async def create_team(self, name: str, description: Optional[str] = None) -> tuple[bool, str]:
        self.logger.info(f"[TeamOperationsAdapter] create_team called with name={name}, description={description}")
        try:
            result = await self.team_service.create_team(name, description)
            self.logger.info(f"[TeamOperationsAdapter] create_team result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error creating team: {e}", exc_info=True)
            return False, f"Error creating team: {str(e)}"

    async def delete_team(self, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[TeamOperationsAdapter] delete_team called with team_id={team_id}")
        try:
            result = await self.team_service.delete_team(team_id)
            self.logger.info(f"[TeamOperationsAdapter] delete_team result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error deleting team: {e}", exc_info=True)
            return False, f"Error deleting team: {str(e)}"

    async def list_teams(self) -> str:
        self.logger.info(f"[TeamOperationsAdapter] list_teams called")
        try:
            result = await self.team_service.list_teams()
            self.logger.info(f"[TeamOperationsAdapter] list_teams result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error listing teams: {e}", exc_info=True)
            return f"Error listing teams: {str(e)}"

    async def get_team_stats(self, team_id: str) -> str:
        self.logger.info(f"[TeamOperationsAdapter] get_team_stats called with team_id={team_id}")
        try:
            result = await self.team_service.get_team_stats(team_id)
            self.logger.info(f"[TeamOperationsAdapter] get_team_stats result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting team stats: {e}", exc_info=True)
            return f"Error getting team stats: {str(e)}" 