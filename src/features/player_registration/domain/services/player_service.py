#!/usr/bin/env python3
"""
Player Service

This module provides player management functionality.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.player import Player, PlayerStatus
from ..repositories.player_repository_interface import PlayerRepositoryInterface
from features.team_administration.domain.services.team_service import TeamService

logger = logging.getLogger(__name__)


class PlayerService:
    """Service for managing players."""
    
    def __init__(self, player_repository: PlayerRepositoryInterface, team_service: TeamService):
        self.player_repository = player_repository
        self.team_service = team_service
    
    async def create_player(self, name: str, phone: str, position: str, team_id: str,
                          created_by: str) -> Player:
        """Create a new player."""
        player = Player(
            name=name,
            phone=phone,
            position=position,
            team_id=team_id,
            status=PlayerStatus.PENDING,
            created_by=created_by,
            created_at=datetime.now()
        )
        return await self.player_repository.create(player)
    
    async def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        return await self.player_repository.get_by_id(player_id)
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number."""
        return await self.player_repository.get_by_phone(phone, team_id)
    
    async def get_players_by_team(self, team_id: str, status: Optional[PlayerStatus] = None) -> List[Player]:
        """Get players for a team, optionally filtered by status."""
        players = await self.player_repository.get_by_team(team_id)
        
        if status:
            players = [player for player in players if player.status == status]
        
        return players
    
    async def update_player_status(self, player_id: str, status: PlayerStatus) -> Player:
        """Update a player's status."""
        player = await self.player_repository.get_by_id(player_id)
        if not player:
            raise ValueError(f"Player with ID {player_id} not found")
        
        player.status = status
        player.updated_at = datetime.now()
        
        return await self.player_repository.update(player)
    
    async def get_player_with_team_info(self, player_id: str) -> Dict[str, Any]:
        """Get player information including team details."""
        player = await self.get_player_by_id(player_id)
        if not player:
            return {}
        
        # Get team information using team service
        team = await self.team_service.get_team_by_id(player.team_id)
        team_name = team.name if team else "Unknown Team"
        
        return {
            'player': player,
            'team_name': team_name,
            'team_id': player.team_id
        }
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        return await self.player_repository.delete(player_id) 