
from features.match_management.domain.entities.match import Match
from features.match_management.domain.repositories.match_repository_interface import (
    MatchRepositoryInterface,
)


class FirebaseMatchRepository(MatchRepositoryInterface):
    def __init__(self, firebase_client):
        self.firebase_client = firebase_client

    async def create(self, match: Match) -> Match:
        # Placeholder: Implement actual Firebase logic
        await self.firebase_client.set_document('matches', match.id, match.__dict__)
        return match

    async def get_by_id(self, match_id: str) -> Match | None:
        data = await self.firebase_client.get_document('matches', match_id)
        if data:
            return Match(**data)
        return None

    async def get_by_team(self, team_id: str) -> list[Match]:
        # Placeholder: Implement actual Firebase logic
        docs = await self.firebase_client.query_collection('matches', {'team_id': team_id})
        return [Match(**doc) for doc in docs]

    async def update(self, match: Match) -> Match:
        await self.firebase_client.set_document('matches', match.id, match.__dict__)
        return match

    async def delete(self, match_id: str) -> None:
        await self.firebase_client.delete_document('matches', match_id)
