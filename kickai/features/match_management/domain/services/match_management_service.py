from typing import List, Optional

from kickai.features.match_management.domain.entities.match import Match
from kickai.features.match_management.domain.repositories.match_repository_interface import (
    MatchRepositoryInterface,
)


class MatchManagementService:
    def __init__(self, match_repository: MatchRepositoryInterface):
        self.match_repository = match_repository

    async def create_match(self, match: Match) -> Match:
        return await self.match_repository.create(match)

    async def get_match_by_id(self, match_id: str) -> Optional[Match]:
        return await self.match_repository.get_by_id(match_id)

    async def get_matches_by_team(self, team_id: str) -> List[Match]:
        return await self.match_repository.get_by_team(team_id)

    async def update_match(self, match: Match) -> Match:
        return await self.match_repository.update(match)

    async def delete_match(self, match_id: str) -> None:
        await self.match_repository.delete(match_id)
