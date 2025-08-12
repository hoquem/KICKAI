import logging

from kickai.features.match_management.domain.entities.availability import (
    Availability,
    AvailabilityStatus,
)
from kickai.features.match_management.domain.repositories.availability_repository_interface import (
    AvailabilityRepositoryInterface,
)

logger = logging.getLogger(__name__)


class FirebaseAvailabilityRepository(AvailabilityRepositoryInterface):
    """Firebase implementation of availability repository."""

    def __init__(self, firebase_client):
        self.firebase_client = firebase_client

    def _get_collection_name(self, team_id: str) -> str:
        """Get the collection name for a team's availability."""
        return f"kickai_{team_id}_match_availability"

    async def create(self, availability: Availability) -> Availability:
        """Create a new availability record."""
        try:
            # We need to get the team_id from the match
            # For now, we'll use a simple approach - this could be optimized
            collection_name = self._get_collection_name("KTI")  # Default team
            await self.firebase_client.create_document(
                collection=collection_name,
                document_id=availability.availability_id,
                data=availability.to_dict()
            )
            logger.info(f"Created availability {availability.availability_id}")
            return availability
        except Exception as e:
            logger.error(f"Failed to create availability {availability.availability_id}: {e}")
            raise

    async def get_by_id(self, availability_id: str) -> Availability | None:
        """Get availability by ID."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                data = await self.firebase_client.get_document(collection_name, availability_id)
                if data:
                    return Availability.from_dict(data)

            return None
        except Exception as e:
            logger.error(f"Failed to get availability {availability_id}: {e}")
            return None

    async def get_by_match_and_player(self, match_id: str, player_id: str) -> Availability | None:
        """Get availability for a specific match and player."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                docs = await self.firebase_client.query_documents(
                    collection_name,
                    filters={"match_id": match_id, "player_id": player_id}
                )
                if docs:
                    return Availability.from_dict(docs[0])

            return None
        except Exception as e:
            logger.error(f"Failed to get availability for match {match_id} and player {player_id}: {e}")
            return None

    async def get_by_match(self, match_id: str) -> list[Availability]:
        """Get all availability records for a match."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")
            all_availabilities = []

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                docs = await self.firebase_client.query_documents(
                    collection_name,
                    filters={"match_id": match_id}
                )
                availabilities = [Availability.from_dict(doc) for doc in docs]
                all_availabilities.extend(availabilities)

            logger.info(f"Retrieved {len(all_availabilities)} availability records for match {match_id}")
            return all_availabilities
        except Exception as e:
            logger.error(f"Failed to get availability for match {match_id}: {e}")
            return []

    async def get_by_player(self, player_id: str, limit: int = 10) -> list[Availability]:
        """Get availability history for a player."""
        try:
            # Search across all team collections
            teams = await self.firebase_client.query_documents("teams")
            all_availabilities = []

            for team in teams:
                team_id = team.get("team_id")
                if not team_id:
                    continue

                collection_name = self._get_collection_name(team_id)
                docs = await self.firebase_client.query_documents(
                    collection_name,
                    filters={"player_id": player_id}
                )
                availabilities = [Availability.from_dict(doc) for doc in docs]
                all_availabilities.extend(availabilities)

            # Sort by created_at (newest first) and limit
            all_availabilities.sort(key=lambda a: a.created_at, reverse=True)

            logger.info(f"Retrieved {len(all_availabilities[:limit])} availability records for player {player_id}")
            return all_availabilities[:limit]
        except Exception as e:
            logger.error(f"Failed to get availability for player {player_id}: {e}")
            return []

    async def get_by_status(self, match_id: str, status: AvailabilityStatus) -> list[Availability]:
        """Get availability records by status for a match."""
        try:
            match_availabilities = await self.get_by_match(match_id)
            filtered_availabilities = [
                availability for availability in match_availabilities
                if availability.status == status
            ]

            logger.info(f"Retrieved {len(filtered_availabilities)} {status.value} availability records for match {match_id}")
            return filtered_availabilities
        except Exception as e:
            logger.error(f"Failed to get {status.value} availability for match {match_id}: {e}")
            return []

    async def update(self, availability: Availability) -> Availability:
        """Update an availability record."""
        try:
            # We need to find the team_id - for now using default
            collection_name = self._get_collection_name("KTI")  # Default team
            await self.firebase_client.update_document(
                collection=collection_name,
                document_id=availability.availability_id,
                data=availability.to_dict()
            )
            logger.info(f"Updated availability {availability.availability_id}")
            return availability
        except Exception as e:
            logger.error(f"Failed to update availability {availability.availability_id}: {e}")
            raise

    async def delete(self, availability_id: str) -> bool:
        """Delete an availability record."""
        try:
            # We need to find the availability first to get the team_id
            availability = await self.get_by_id(availability_id)
            if not availability:
                logger.warning(f"Availability {availability_id} not found for deletion")
                return False

            collection_name = self._get_collection_name("KTI")  # Default team
            await self.firebase_client.delete_document(collection_name, availability_id)
            logger.info(f"Deleted availability {availability_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete availability {availability_id}: {e}")
            return False

    async def get_pending_availability(self, match_id: str) -> list[Availability]:
        """Get all pending availability records for a match."""
        return await self.get_by_status(match_id, AvailabilityStatus.PENDING)
