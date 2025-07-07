import logging
from typing import List

from src.services.match_service import get_match_service
from src.services.player_service import get_player_service
from src.database.models_improved import MatchStatus

logger = logging.getLogger(__name__)

class MatchCommands:
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.match_service = get_match_service()
        self.player_service = get_player_service()

    async def handle_record_result(self, args: List[str]) -> str:
        """Handles the record result command."""
        if len(args) < 3:
            return "❌ Usage: /record_result <match_id> <our_score>-<opponent_score> [scorers] [assists]"

        match_id = args[0]
        score_str = args[1]
        scorers_str = args[2] if len(args) > 2 else ""
        assists_str = args[3] if len(args) > 3 else ""

        try:
            our_score, opponent_score = map(int, score_str.split('-'))
        except ValueError:
            return "❌ Invalid score format. Use <our_score>-<opponent_score> (e.g., 3-1)"

        scorers = [s.strip() for s in scorers_str.split(',')] if scorers_str else []
        assists = [a.strip() for a in assists_str.split(',')] if assists_str else []

        try:
            match = await self.match_service.update_match(
                match_id,
                score=score_str,
                goal_scorers=scorers,
                assists=assists,
                status=MatchStatus.COMPLETED
            )

            # Update player statistics (placeholder)
            # In a real scenario, you'd iterate through scorers/assists and update player models
            # For example: await self.player_service.update_player_stats(player_id, goals=1)

            return f"✅ Match {match.id} result recorded: {match.score}. Scorers: {match.goal_scorers}. Assists: {match.assists}."
        except Exception as e:
            logger.error(f"Error recording match result: {e}")
            return f"❌ Failed to record match result: {str(e)}"

    async def handle_attend_match(self, match_id: str, player_id: str) -> str:
        """Handles a player attending a match."""
        try:
            match = await self.match_service.get_match(match_id)
            if not match:
                return f"❌ Match {match_id} not found."

            if player_id not in match.attendees:
                match.attendees.append(player_id)
                await self.match_service.update_match(match.id, attendees=match.attendees)
                return f"✅ Player {player_id} is now attending match {match_id}."
            else:
                return f"ℹ️ Player {player_id} is already attending match {match_id}."
        except Exception as e:
            logger.error(f"Error handling attend match: {e}")
            return f"❌ Failed to record attendance: {str(e)}"

    async def handle_unattend_match(self, match_id: str, player_id: str) -> str:
        """Handles a player unattending a match."""
        try:
            match = await self.match_service.get_match(match_id)
            if not match:
                return f"❌ Match {match_id} not found."

            if player_id in match.attendees:
                match.attendees.remove(player_id)
                await self.match_service.update_match(match.id, attendees=match.attendees)
                return f"✅ Player {player_id} is no longer attending match {match_id}."
            else:
                return f"ℹ️ Player {player_id} was not attending match {match_id}."
        except Exception as e:
            logger.error(f"Error handling unattend match: {e}")
            return f"❌ Failed to remove attendance: {str(e)}"
