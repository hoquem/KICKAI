#!/usr/bin/env python3
"""
Availability Service Interface

Defines the contract for availability management services.
"""

from abc import ABC, abstractmethod
from typing import Any

from kickai.features.match_management.domain.entities.availability import Availability


class IAvailabilityService(ABC):
    """Interface for availability service operations."""

    @abstractmethod
    async def record_availability(
        self, player_id: str, match_id: str, availability_status: str, comments: str | None = None
    ) -> Availability:
        """
        Record a player's availability for a match.

        Args:
            player_id: Player identifier
            match_id: Match identifier
            availability_status: Available/unavailable/maybe
            comments: Optional comments from player

        Returns:
            Created availability record
        """
        pass

    @abstractmethod
    async def update_availability(
        self, availability_id: str, availability_status: str, comments: str | None = None
    ) -> Availability | None:
        """
        Update an existing availability record.

        Args:
            availability_id: Availability record identifier
            availability_status: New availability status
            comments: Updated comments

        Returns:
            Updated availability record if found
        """
        pass

    @abstractmethod
    async def get_player_availability(self, player_id: str, match_id: str) -> Availability | None:
        """
        Get a player's availability for a specific match.

        Args:
            player_id: Player identifier
            match_id: Match identifier

        Returns:
            Availability record if found
        """
        pass

    @abstractmethod
    async def get_match_availability(self, match_id: str) -> list[Availability]:
        """
        Get all availability records for a match.

        Args:
            match_id: Match identifier

        Returns:
            List of availability records
        """
        pass

    @abstractmethod
    async def get_player_availability_history(
        self, player_id: str, limit: int = 50
    ) -> list[Availability]:
        """
        Get availability history for a player.

        Args:
            player_id: Player identifier
            limit: Maximum records to return

        Returns:
            List of availability records
        """
        pass

    @abstractmethod
    async def get_availability_summary(self, match_id: str) -> dict[str, Any]:
        """
        Get availability summary for a match.

        Args:
            match_id: Match identifier

        Returns:
            Summary with counts by status
        """
        pass

    @abstractmethod
    async def remind_missing_availability(self, match_id: str, team_id: str) -> list[str]:
        """
        Get list of players who haven't submitted availability.

        Args:
            match_id: Match identifier
            team_id: Team identifier

        Returns:
            List of player IDs missing availability
        """
        pass
