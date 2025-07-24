from abc import ABC, abstractmethod

from kickai.features.match_management.domain.entities.match import Match


class MatchRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, match: Match) -> Match:
        pass

    @abstractmethod
    async def get_by_id(self, match_id: str) -> Match | None:
        pass

    @abstractmethod
    async def get_by_team(self, team_id: str) -> list[Match]:
        pass

    @abstractmethod
    async def update(self, match: Match) -> Match:
        pass

    @abstractmethod
    async def delete(self, match_id: str) -> None:
        pass
