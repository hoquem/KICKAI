#!/usr/bin/env python3
"""
Player Registration Service

This module provides the business logic for player registration operations.
"""

from datetime import datetime

from src.features.player_registration.domain.entities.player import Player
from src.features.player_registration.domain.repositories.player_repository_interface import (
    PlayerRepositoryInterface,
)
from src.utils.football_id_generator import generate_football_player_id


class PlayerRegistrationService:
    """Service for player registration operations."""

    def __init__(self, player_repository: PlayerRepositoryInterface):
        self.player_repository = player_repository

    async def register_player(self, name: str, phone: str, position: str, team_id: str) -> Player:
        """Register a new player."""
        # Validate input parameters
        self._validate_player_input(name, phone, position, team_id)
        
        # Check if player already exists
        existing_player = await self.player_repository.get_player_by_phone(phone, team_id)
        if existing_player:
            raise ValueError(f"Player with phone {phone} already exists in team {team_id}")

        # Get existing player IDs to avoid collisions
        existing_players = await self.player_repository.get_all_players(team_id)
        existing_ids = {player.player_id for player in existing_players if player.player_id}
        
        # Generate football-friendly player ID
        # Split name into first and last name for football ID generation
        name_parts = name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]
        else:
            first_name = name_parts[0] if name_parts else "Unknown"
            last_name = first_name
        
        player_id = generate_football_player_id(first_name, last_name, position, team_id, existing_ids)
        
        # Create new player
        player = Player(
            user_id=f"user_{team_id}_{phone}",
            player_id=player_id,
            team_id=team_id,
            full_name=name,
            phone_number=phone,
            position=position,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return await self.player_repository.create_player(player)

    def _validate_player_input(self, name: str, phone: str, position: str, team_id: str) -> None:
        """Validate player input parameters."""
        if not name or not name.strip():
            raise ValueError("Player name cannot be empty")
        if not phone or not phone.strip():
            raise ValueError("Player phone cannot be empty")
        if not position or not position.strip():
            raise ValueError("Player position cannot be empty")
        if not team_id or not team_id.strip():
            raise ValueError("Team ID cannot be empty")
        
        # Validate phone number format (basic validation)
        phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
        if not phone_clean.isdigit() or len(phone_clean) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        
        # Validate position (basic validation)
        valid_positions = ['goalkeeper', 'defender', 'midfielder', 'forward', 'utility']
        if position.lower() not in valid_positions:
            raise ValueError(f"Position must be one of: {', '.join(valid_positions)}")
        
        # Validate name length
        if len(name.strip()) < 2:
            raise ValueError("Player name must be at least 2 characters long")
        
        # Validate team_id format (basic validation)
        if len(team_id.strip()) < 2:
            raise ValueError("Team ID must be at least 2 characters long")

    async def approve_player(self, player_id: str, team_id: str) -> Player:
        """Approve a player."""
        player = await self.player_repository.get_player_by_id(player_id, team_id)
        if not player:
            raise ValueError(f"Player {player_id} not found in team {team_id}")

        player.approve()
        return await self.player_repository.update_player(player)

    async def reject_player(self, *, player_id: str, team_id: str) -> Player:
        """Reject a player."""
        player = await self.player_repository.get_player_by_id(player_id, team_id)
        if not player:
            raise ValueError(f"Player {player_id} not found in team {team_id}")

        player.reject()
        return await self.player_repository.update_player(player)

    async def get_player(self, *, player_id: str, team_id: str) -> Player | None:
        """Get a player by ID."""
        return await self.player_repository.get_player_by_id(player_id, team_id)

    async def get_player_by_phone(self, *, phone: str, team_id: str) -> Player | None:
        """Get a player by phone number."""
        return await self.player_repository.get_player_by_phone(phone, team_id)

    async def get_all_players(self, *, team_id: str) -> list[Player]:
        """Get all players in a team."""
        return await self.player_repository.get_all_players(team_id)

    async def get_pending_players(self, *, team_id: str) -> list[Player]:
        """Get all pending players in a team."""
        return await self.player_repository.get_players_by_status(team_id, "pending")

    async def get_approved_players(self, *, team_id: str) -> list[Player]:
        """Get all approved players in a team."""
        return await self.player_repository.get_players_by_status(team_id, "approved")

    async def get_active_players(self, *, team_id: str) -> list[Player]:
        """Get all active players in a team."""
        return await self.player_repository.get_players_by_status(team_id, "active")

    async def get_all_players(self, *, team_id: str) -> list[Player]:
        """Get all players for a team."""
        return await self.player_repository.get_all_players(team_id)

    async def remove_player(self, *, player_id: str, team_id: str) -> bool:
        """Remove a player from the team."""
        return await self.player_repository.delete_player(player_id, team_id)
