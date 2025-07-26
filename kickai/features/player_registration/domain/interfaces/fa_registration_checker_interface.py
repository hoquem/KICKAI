from abc import ABC, abstractmethod


class IFARegistrationChecker(ABC):
    """Interface for FA registration checker operations."""

    @abstractmethod
    async def check_player_registration(self, team_id: str) -> dict[str, bool]:
        """Check FA registration status for all players in a team."""
        pass

    @abstractmethod
    async def scrape_fixtures(self) -> list[dict]:
        """Scrape fixtures and match results from FA website."""
        pass
