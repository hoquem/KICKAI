from abc import ABC, abstractmethod

from kickai.features.match_management.domain.entities.match import Match, MatchStatus


class MatchRepositoryInterface(ABC):
    """Interface for match repository."""

    @abstractmethod
    async def create(self, match: Match) -> Match:
        """Create a new match."""
        pass

    @abstractmethod
    async def get_by_id(self, match_id: str) -> Match | None:
        """Get match by ID."""
        pass

    @abstractmethod
    async def get_by_team(self, team_id: str) -> list[Match]:
        """Get all matches for a team."""
        pass

    @abstractmethod
    async def get_by_team_and_status(self, team_id: str, status: MatchStatus) -> list[Match]:
        """Get matches for a team by status."""
        pass

    @abstractmethod
    async def get_upcoming_matches(self, team_id: str, limit: int = 10) -> list[Match]:
        """Get upcoming matches for a team."""
        pass

    @abstractmethod
    async def get_past_matches(self, team_id: str, limit: int = 10) -> list[Match]:
        """Get past matches for a team."""
        pass

    @abstractmethod
    async def update(self, match: Match) -> Match:
        """Update a match."""
        pass

    @abstractmethod
    async def delete(self, match_id: str) -> bool:
        """Delete a match."""
        pass

    @abstractmethod
    async def get_matches_by_date_range(
        self, team_id: str, start_date: str, end_date: str
    ) -> list[Match]:
        """Get matches within a date range."""
        pass
