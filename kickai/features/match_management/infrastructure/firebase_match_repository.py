import logging
from datetime import datetime

from kickai.features.match_management.domain.entities.match import Match, MatchStatus
from kickai.features.match_management.domain.repositories.match_repository_interface import (
    MatchRepositoryInterface,
)

logger = logging.getLogger(__name__)


class FirebaseMatchRepository(MatchRepositoryInterface):
    """Firebase implementation of match repository."""

    def __init__(self, firebase_client):
        self.firebase_client = firebase_client

    def _get_collection_name(self, team_id: str) -> str:
        """Get the collection name for a team's matches."""
        return f"kickai_{team_id}_matches"

    async def create(self, match: Match) -> Match:
        """Create a new match."""
        try:
            collection_name = self._get_collection_name(match.team_id)
            await self.firebase_client.create_document(
                collection=collection_name, document_id=match.match_id, data=match.to_dict()
            )
            logger.info(f"Created match {match.match_id} in collection {collection_name}")
            return match
        except Exception as e:
            logger.error(f"Failed to create match {match.match_id}: {e}")
            raise

    async def get_by_id(self, match_id: str) -> Match | None:
        """Get match by ID."""
        try:
            # We need to search across all team collections to find the match
            # This is a limitation of the current design - we could optimize this
            # by storing a global matches collection or using a different approach
            teams = await self.firebase_client.query_documents("teams")

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                data = await self.firebase_client.get_document(collection_name, match_id)
                if data:
                    return Match.from_dict(data)

            return None
        except Exception as e:
            logger.error(f"Failed to get match {match_id}: {e}")
            return None

    async def get_by_team(self, team_id: str) -> list[Match]:
        """Get all matches for a team."""
        try:
            collection_name = self._get_collection_name(team_id)
            docs = await self.firebase_client.query_documents(collection_name)
            matches = [Match.from_dict(doc) for doc in docs]

            # Sort by match date (newest first)
            matches.sort(key=lambda m: m.match_date, reverse=True)

            logger.info(f"Retrieved {len(matches)} matches for team {team_id}")
            return matches
        except Exception as e:
            logger.error(f"Failed to get matches for team {team_id}: {e}")
            return []

    async def get_by_team_and_status(self, team_id: str, status: MatchStatus) -> list[Match]:
        """Get matches for a team by status."""
        try:
            collection_name = self._get_collection_name(team_id)
            docs = await self.firebase_client.query_documents(
                collection_name, filters={"status": status.value}
            )
            matches = [Match.from_dict(doc) for doc in docs]

            # Sort by match date (newest first)
            matches.sort(key=lambda m: m.match_date, reverse=True)

            logger.info(f"Retrieved {len(matches)} {status.value} matches for team {team_id}")
            return matches
        except Exception as e:
            logger.error(f"Failed to get {status.value} matches for team {team_id}: {e}")
            return []

    async def get_upcoming_matches(self, team_id: str, limit: int = 10) -> list[Match]:
        """Get upcoming matches for a team."""
        try:
            all_matches = await self.get_by_team(team_id)
            now = datetime.utcnow()

            upcoming_matches = [
                match for match in all_matches if match.match_date > now and match.is_upcoming
            ]

            # Sort by match date (earliest first)
            upcoming_matches.sort(key=lambda m: m.match_date)

            return upcoming_matches[:limit]
        except Exception as e:
            logger.error(f"Failed to get upcoming matches for team {team_id}: {e}")
            return []

    async def get_past_matches(self, team_id: str, limit: int = 10) -> list[Match]:
        """Get past matches for a team."""
        try:
            all_matches = await self.get_by_team(team_id)
            now = datetime.utcnow()

            past_matches = [
                match for match in all_matches if match.match_date <= now or match.is_completed
            ]

            # Sort by match date (newest first)
            past_matches.sort(key=lambda m: m.match_date, reverse=True)

            return past_matches[:limit]
        except Exception as e:
            logger.error(f"Failed to get past matches for team {team_id}: {e}")
            return []

    async def update(self, match: Match) -> Match:
        """Update a match."""
        try:
            collection_name = self._get_collection_name(match.team_id)
            await self.firebase_client.update_document(
                collection=collection_name, document_id=match.match_id, data=match.to_dict()
            )
            logger.info(f"Updated match {match.match_id}")
            return match
        except Exception as e:
            logger.error(f"Failed to update match {match.match_id}: {e}")
            raise

    async def delete(self, match_id: str) -> bool:
        """Delete a match."""
        try:
            # We need to find the match first to get the team_id
            match = await self.get_by_id(match_id)
            if not match:
                logger.warning(f"Match {match_id} not found for deletion")
                return False

            collection_name = self._get_collection_name(match.team_id)
            await self.firebase_client.delete_document(collection_name, match_id)
            logger.info(f"Deleted match {match_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete match {match_id}: {e}")
            return False

    async def get_matches_by_date_range(
        self, team_id: str, start_date: str, end_date: str
    ) -> list[Match]:
        """Get matches within a date range."""
        try:
            all_matches = await self.get_by_team(team_id)
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)

            matches_in_range = [
                match for match in all_matches if start_dt <= match.match_date <= end_dt
            ]

            # Sort by match date (earliest first)
            matches_in_range.sort(key=lambda m: m.match_date)

            logger.info(
                f"Retrieved {len(matches_in_range)} matches in date range for team {team_id}"
            )
            return matches_in_range
        except Exception as e:
            logger.error(f"Failed to get matches in date range for team {team_id}: {e}")
            return []
