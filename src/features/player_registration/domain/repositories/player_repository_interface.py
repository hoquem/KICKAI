#!/usr/bin/env python3
"""
Player Repository Interface

This module defines the interface for player data access operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Player:
    """Player entity."""
    id: str
    name: str
    phone: str
    position: str
    team_id: str
    status: str = "pending"
    created_at: str | None = None
    updated_at: str | None = None


class PlayerRepositoryInterface(ABC):
    """Interface for player data access operations."""

    @abstractmethod
    async def create_player(self, player: Player) -> Player:
        """Create a new player."""
        pass

    @abstractmethod
    async def get_player_by_id(self, player_id: str, team_id: str) -> Player | None:
        """Get a player by ID."""
        pass

    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: str) -> Player | None:
        """Get a player by phone number."""
        pass

    @abstractmethod
    async def get_all_players(self, team_id: str) -> list[Player]:
        """Get all players in a team."""
        pass

    @abstractmethod
    async def update_player(self, player: Player) -> Player:
        """Update a player."""
        pass

    @abstractmethod
    async def delete_player(self, player_id: str, team_id: str) -> bool:
        """Delete a player."""
        pass

    @abstractmethod
    async def get_players_by_status(self, team_id: str, status: str) -> list[Player]:
        """Get players by status."""
        pass
