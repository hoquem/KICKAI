"""
Multi-Team Manager Service for KICKAI

This service handles operations across multiple teams and manages team mappings.
"""

import logging
from typing import List, Optional, Dict, Any
from database.models_improved import Team, BotMapping
from database.firebase_client import get_firebase_client
from core.exceptions import TeamError
from database.models_improved import TeamStatus

logger = logging.getLogger(__name__)


class MultiTeamManager:
    """Service for managing operations across multiple teams."""
    
    def __init__(self):
        self._data_store = get_firebase_client()
        logger.info("✅ MultiTeamManager initialized")
    
    async def get_all_teams(self) -> List[Team]:
        """Get all teams in the system."""
        try:
            return await self._data_store.get_all_teams()
        except Exception as e:
            logger.error(f"❌ Failed to get all teams: {e}")
            return []
    
    async def get_teams_by_status(self, status: str) -> List[Team]:
        """Get teams filtered by status."""
        try:
            team_status = TeamStatus(status)
            return await self._data_store.get_all_teams(team_status)
        except Exception as e:
            logger.error(f"❌ Failed to get teams by status {status}: {e}")
            return []
    
    async def get_bot_mappings(self) -> List[BotMapping]:
        """Get all bot mappings."""
        try:
            # This would need to be implemented in the data store
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"❌ Failed to get bot mappings: {e}")
            return []
    
    async def get_team_by_bot_username(self, bot_username: str) -> Optional[Team]:
        """Get team by bot username."""
        try:
            mapping = await self._data_store.get_bot_mapping_by_username(bot_username)
            if mapping:
                return await self._data_store.get_team(mapping.team_id)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get team by bot username {bot_username}: {e}")
            return None
    
    async def get_teams_with_members_count(self) -> List[Dict[str, Any]]:
        """Get teams with their member counts."""
        try:
            teams = await self.get_all_teams()
            result = []
            
            for team in teams:
                members = await self._data_store.get_team_members_by_team(team.id)
                result.append({
                    'team': team,
                    'member_count': len(members)
                })
            
            return result
        except Exception as e:
            logger.error(f"❌ Failed to get teams with member counts: {e}")
            return []
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        try:
            teams = await self.get_all_teams()
            total_members = 0
            active_teams = 0
            
            for team in teams:
                if team.status.value == 'active':
                    active_teams += 1
                members = await self._data_store.get_team_members_by_team(team.id)
                total_members += len(members)
            
            return {
                'total_teams': len(teams),
                'active_teams': active_teams,
                'total_members': total_members,
                'average_members_per_team': total_members / len(teams) if teams else 0
            }
        except Exception as e:
            logger.error(f"❌ Failed to get system statistics: {e}")
            return {}
    
    async def validate_team_operations(self, team_id: str, operation: str) -> bool:
        """Validate if a team operation is allowed."""
        try:
            team = await self._data_store.get_team(team_id)
            if not team:
                return False
            
            # Add validation logic here
            if operation == "delete" and team.status.value == "active":
                # Check if team has members
                members = await self._data_store.get_team_members_by_team(team_id)
                if members:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to validate team operation: {e}")
            return False 