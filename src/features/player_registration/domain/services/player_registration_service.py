#!/usr/bin/env python3
"""
Player Registration Service

This module provides the business logic for player registration operations.
"""

from typing import List, Optional
from datetime import datetime

from src.features.player_registration.domain.repositories.player_repository_interface import (
    PlayerRepositoryInterface,
    Player
)


class PlayerRegistrationService:
    """Service for player registration operations."""
    
    def __init__(self, player_repository: PlayerRepositoryInterface):
        self.player_repository = player_repository
    
    async def register_player(self, name: str, phone: str, position: str, team_id: str) -> Player:
        """Register a new player."""
        # Check if player already exists
        existing_player = await self.player_repository.get_player_by_phone(phone, team_id)
        if existing_player:
            raise ValueError(f"Player with phone {phone} already exists in team {team_id}")
        
        # Create new player
        player = Player(
            id=f"{team_id}_{phone}",
            name=name,
            phone=phone,
            position=position,
            team_id=team_id,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.player_repository.create_player(player)
    
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
    
    async def get_player(self, *, player_id: str, team_id: str) -> Optional[Player]:
        """Get a player by ID."""
        return await self.player_repository.get_player_by_id(player_id, team_id)
    
    async def get_player_by_phone(self, *, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number."""
        return await self.player_repository.get_player_by_phone(phone, team_id)
    
    async def get_all_players(self, *, team_id: str) -> List[Player]:
        """Get all players in a team."""
        return await self.player_repository.get_all_players(team_id)
    
    async def get_pending_players(self, *, team_id: str) -> List[Player]:
        """Get all pending players in a team."""
        return await self.player_repository.get_players_by_status(team_id, "pending")
    
    async def get_approved_players(self, *, team_id: str) -> List[Player]:
        """Get all approved players in a team."""
        return await self.player_repository.get_players_by_status(team_id, "approved")
    
    async def get_active_players(self, *, team_id: str) -> List[Player]:
        """Get all active players in a team."""
        return await self.player_repository.get_players_by_status(team_id, "active")
    
    async def remove_player(self, *, player_id: str, team_id: str) -> bool:
        """Remove a player from the team."""
        return await self.player_repository.delete_player(player_id, team_id) 