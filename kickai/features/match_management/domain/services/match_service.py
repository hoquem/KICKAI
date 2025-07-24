import logging
from datetime import datetime, timedelta

from kickai.core.exceptions import MatchError, MatchNotFoundError, create_error_context
from kickai.database.firebase_client import get_firebase_client
from kickai.features.match_management.domain.entities.match import Match, MatchStatus
from kickai.features.match_management.domain.interfaces.match_service_interface import IMatchService
from kickai.utils.football_id_generator import generate_football_match_id

logger = logging.getLogger(__name__)

class MatchService(IMatchService):
    """Service for managing matches."""

    def __init__(self, data_store=None):
        if data_store is None:
            self._data_store = get_firebase_client()
        else:
            self._data_store = data_store

    async def create_match(self, team_id: str, opponent: str, date: datetime, location: str | None = None, status: MatchStatus = MatchStatus.SCHEDULED, home_away: str = "home", competition: str | None = None) -> Match:
        """Creates a new match."""
        try:
            # Generate football-friendly match ID
            match_date_str = date.strftime('%Y-%m-%d')
            competition_str = competition or "Friendly"

            # For home matches, team_id is home team, opponent is away team
            # For away matches, opponent is home team, team_id is away team
            if home_away.lower() == "home":
                home_team = team_id
                away_team = opponent
            else:
                home_team = opponent
                away_team = team_id

            match_id = generate_football_match_id(home_team, away_team, match_date_str, competition_str)

            match = Match.create(
                team_id=team_id,
                opponent=opponent,
                date=date,
                location=location,
                status=status,
                home_away=home_away,
                competition=competition
            )
            match.id = match_id
            await self._data_store.create_match(match)
            logger.info(f"Football match created: {match.id}")
            return match
        except Exception as e:
            logger.error(f"Failed to create match: {e}")
            raise MatchError(f"Failed to create match: {e!s}", create_error_context("create_match"))

    async def get_match(self, match_id: str) -> Match | None:
        """Retrieves a match by its ID."""
        try:
            match = await self._data_store.get_match(match_id)
            return match
        except Exception as e:
            logger.error(f"Failed to get match {match_id}: {e}")
            raise MatchError(f"Failed to get match: {e!s}", create_error_context("get_match"))

    async def update_match(self, match_id: str, **updates) -> Match:
        """Updates an existing match."""
        try:
            match = await self.get_match(match_id)
            if not match:
                raise MatchNotFoundError(f"Match not found: {match_id}", create_error_context("update_match"))

            match.update(**updates)
            await self._data_store.update_match(match)
            logger.info(f"Match {match.id} updated.")
            return match
        except MatchNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update match {match_id}: {e}")
            raise MatchError(f"Failed to update match: {e!s}", create_error_context("update_match"))

    async def delete_match(self, match_id: str) -> bool:
        """Deletes a match."""
        try:
            success = await self._data_store.delete_match(match_id)
            if not success:
                raise MatchNotFoundError(f"Match not found: {match_id}", create_error_context("delete_match"))
            logger.info(f"Match {match_id} deleted.")
            return True
        except MatchNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete match {match_id}: {e}")
            raise MatchError(f"Failed to delete match: {e!s}", create_error_context("delete_match"))

    async def list_matches(self, team_id: str, status: MatchStatus | None = None) -> list[Match]:
        """Lists matches for a team, with optional filters."""
        try:
            filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
            if status:
                filters.append({'field': 'status', 'operator': '==', 'value': status.value})

            data_list = await self._data_store.query_documents('matches', filters)
            return [Match.from_dict(data) for data in data_list]
        except Exception as e:
            logger.error(f"Failed to list matches for team {team_id}: {e}")
            raise MatchError(f"Failed to list matches: {e!s}", create_error_context("list_matches"))

    async def generate_fixtures(self, team_id: str, num_matches: int, opponents: list[str]) -> list[Match]:
        """Generates a set of fixtures for the team (placeholder for complex logic)."""
        logger.info(f"Generating {num_matches} fixtures for team {team_id} against {opponents}")
        generated_matches = []
        for i in range(num_matches):
            opponent = opponents[i % len(opponents)]
            match_date = datetime.now() + timedelta(days=(i+1)*7) # One match per week
            match = await self.create_match(team_id, opponent, match_date, location="Generated Venue", status=MatchStatus.SCHEDULED, home_away="home", competition="Friendly")
            generated_matches.append(match)
        return generated_matches
