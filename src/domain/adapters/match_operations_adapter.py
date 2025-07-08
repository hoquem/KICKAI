"""
Application layer adapter for match operations.

This adapter implements the domain interface by wrapping the application layer services.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MatchOperationsAdapter:
    """Adapter that wraps the match service to implement domain interface."""
    
    def __init__(self, match_service):
        self.match_service = match_service
        self.logger = logging.getLogger(__name__)

    async def create_match(self, opponent: str, date: str, time: str, venue: str, competition: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[MatchOperationsAdapter] create_match called with opponent={opponent}, date={date}, time={time}, venue={venue}, competition={competition}, team_id={team_id}")
        try:
            result = await self.match_service.create_match(opponent, date, time, venue, competition, team_id)
            self.logger.info(f"[MatchOperationsAdapter] create_match result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error creating match: {e}", exc_info=True)
            return False, f"Error creating match: {str(e)}"

    async def list_matches(self, team_id: str) -> str:
        self.logger.info(f"[MatchOperationsAdapter] list_matches called with team_id={team_id}")
        try:
            result = await self.match_service.list_matches(team_id)
            self.logger.info(f"[MatchOperationsAdapter] list_matches result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error listing matches: {e}", exc_info=True)
            return f"Error listing matches: {str(e)}"

    async def get_match(self, match_id: str, team_id: str) -> Optional[Any]:
        self.logger.info(f"[MatchOperationsAdapter] get_match called with match_id={match_id}, team_id={team_id}")
        try:
            result = await self.match_service.get_match(match_id, team_id)
            self.logger.info(f"[MatchOperationsAdapter] get_match result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting match: {e}", exc_info=True)
            return None

    async def update_match(self, match_id: str, updates: Dict[str, Any], team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[MatchOperationsAdapter] update_match called with match_id={match_id}, updates={updates}, team_id={team_id}")
        try:
            result = await self.match_service.update_match(match_id, updates, team_id)
            self.logger.info(f"[MatchOperationsAdapter] update_match result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error updating match: {e}", exc_info=True)
            return False, f"Error updating match: {str(e)}"

    async def delete_match(self, match_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[MatchOperationsAdapter] delete_match called with match_id={match_id}, team_id={team_id}")
        try:
            result = await self.match_service.delete_match(match_id, team_id)
            self.logger.info(f"[MatchOperationsAdapter] delete_match result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error deleting match: {e}", exc_info=True)
            return False, f"Error deleting match: {str(e)}"

    async def record_match_result(self, match_id: str, result: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[MatchOperationsAdapter] record_match_result called with match_id={match_id}, result={result}, team_id={team_id}")
        try:
            result = await self.match_service.record_match_result(match_id, result, team_id)
            self.logger.info(f"[MatchOperationsAdapter] record_match_result result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error recording match result: {e}", exc_info=True)
            return False, f"Error recording match result: {str(e)}"

    async def attend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[MatchOperationsAdapter] attend_match called with match_id={match_id}, user_id={user_id}, team_id={team_id}")
        try:
            result = await self.match_service.attend_match(match_id, user_id, team_id)
            self.logger.info(f"[MatchOperationsAdapter] attend_match result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error attending match: {e}", exc_info=True)
            return False, f"Error attending match: {str(e)}"

    async def unattend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[MatchOperationsAdapter] unattend_match called with match_id={match_id}, user_id={user_id}, team_id={team_id}")
        try:
            result = await self.match_service.unattend_match(match_id, user_id, team_id)
            self.logger.info(f"[MatchOperationsAdapter] unattend_match result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error unattending match: {e}", exc_info=True)
            return False, f"Error unattending match: {str(e)}" 