from typing import Optional
#!/usr/bin/env python3
"""
Player Repository Interface

This module defines the interface for player data access operations.
"""

from abc import ABC, abstractmethod

from kickai.features.player_registration.domain.entities.player import Player


class PlayerRepositoryInterface(ABC):
    """Interface for player data access operations."""

    @abstractmethod
    async def create_player(self, player: Player) -> Player:
        """Create a new player."""
        pass

    @abstractmethod
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        """Get a player by ID."""
        pass

    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
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

    @abstractmethod
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[Player]:
        """Get a player by Telegram ID."""
        pass

    @abstractmethod
    async def get_active_players(self, team_id: str) -> list[Player]:
        """Get all active players in a team."""
        pass

    @abstractmethod
    async def approve_player(self, player_id: str, team_id: str) -> Player:
        """Approve a player and set status to active."""
        pass

    @abstractmethod
    async def update_player_field(self, telegram_id: int, team_id: str, field: str, value: str) -> bool:
        """Update a single field for a player."""
        pass

    @abstractmethod
    async def update_player_multiple_fields(self, telegram_id: int, team_id: str, updates: dict[str, str]) -> bool:
        """Update multiple fields for a player."""
        pass
