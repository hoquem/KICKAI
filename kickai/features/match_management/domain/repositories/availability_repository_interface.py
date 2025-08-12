from typing import Optional
from abc import ABC, abstractmethod

from kickai.features.match_management.domain.entities.availability import (
    Availability,
    AvailabilityStatus,
)


class AvailabilityRepositoryInterface(ABC):
    """Interface for availability repository."""

    @abstractmethod
    async def create(self, availability: Availability) -> Availability:
        """Create a new availability record."""
        pass

    @abstractmethod
    async def get_by_id(self, availability_id: str) -> Optional[Availability]:
        """Get availability by ID."""
        pass

    @abstractmethod
    async def get_by_match_and_player(self, match_id: str, player_id: str) -> Optional[Availability]:
        """Get availability for a specific match and player."""
        pass

    @abstractmethod
    async def get_by_match(self, match_id: str) -> list[Availability]:
        """Get all availability records for a match."""
        pass

    @abstractmethod
    async def get_by_player(self, player_id: str, limit: int = 10) -> list[Availability]:
        """Get availability history for a player."""
        pass

    @abstractmethod
    async def get_by_status(self, match_id: str, status: AvailabilityStatus) -> list[Availability]:
        """Get availability records by status for a match."""
        pass

    @abstractmethod
    async def update(self, availability: Availability) -> Availability:
        """Update an availability record."""
        pass

    @abstractmethod
    async def delete(self, availability_id: str) -> bool:
        """Delete an availability record."""
        pass

    @abstractmethod
    async def get_pending_availability(self, match_id: str) -> list[Availability]:
        """Get all pending availability records for a match."""
        pass
