"""
Mock Player Service

This module provides a mock implementation of the PlayerService interface
for testing purposes.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..interfaces.player_service_interface import IPlayerService
from ...database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus


class MockPlayerService(IPlayerService):
    """Mock implementation of PlayerService for testing."""
    
    def __init__(self):
        self._players: Dict[str, Player] = {}
        self._next_id = 1
        self.logger = logging.getLogger(__name__)
    
    async def create_player(self, name: str, phone: str, team_id: str, 
                          email: Optional[str] = None, position: PlayerPosition = PlayerPosition.UTILITY,
                          role: PlayerRole = PlayerRole.PLAYER, fa_registered: bool = False) -> Player:
        """Create a new player with validation."""
        player_id = f"P{self._next_id:03d}"
        self._next_id += 1
        
        player = Player(
            id=player_id,
            name=name.strip(),
            phone=phone.strip(),
            email=email.strip() if email else None,
            position=position,
            role=role,
            fa_registered=fa_registered,
            fa_eligible=True,
            team_id=team_id,
            onboarding_status=OnboardingStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._players[player_id] = player
        self.logger.info(f"Mock: Player created: {player.name} ({player_id})")
        return player
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        player = self._players.get(player_id)
        if player:
            self.logger.info(f"Mock: Player retrieved: {player.name}")
        return player
    
    async def update_player(self, player_id: str, **updates) -> Player:
        """Update a player with validation."""
        player = self._players.get(player_id)
        if not player:
            raise ValueError(f"Player not found: {player_id}")
        
        # Update the player
        for key, value in updates.items():
            if hasattr(player, key):
                setattr(player, key, value)
        
        player.updated_at = datetime.now()
        self.logger.info(f"Mock: Player updated: {player.name}")
        return player
    
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        if player_id not in self._players:
            raise ValueError(f"Player not found: {player_id}")
        
        player = self._players[player_id]
        del self._players[player_id]
        self.logger.info(f"Mock: Player deleted: {player.name}")
        return True
    
    async def get_team_players(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        players = [p for p in self._players.values() if p.team_id == team_id]
        self.logger.info(f"Mock: Retrieved {len(players)} players for team {team_id}")
        return players
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number."""
        for player in self._players.values():
            if player.phone == phone and player.team_id == team_id:
                return player
        return None
    
    async def update_onboarding_status(self, player_id: str, status: OnboardingStatus) -> Player:
        """Update player onboarding status."""
        player = self._players.get(player_id)
        if not player:
            raise ValueError(f"Player not found: {player_id}")
        
        player.onboarding_status = status
        player.updated_at = datetime.now()
        self.logger.info(f"Mock: Player onboarding status updated: {player.name} -> {status}")
        return player
    
    async def generate_invite_link(self, player_id: str, invite_link: str) -> Player:
        """Generate and store invite link for a player."""
        player = self._players.get(player_id)
        if not player:
            raise ValueError(f"Player not found: {player_id}")
        
        player.invite_link = invite_link
        player.updated_at = datetime.now()
        self.logger.info(f"Mock: Invite link generated for: {player.name}")
        return player
    
    async def generate_player_id(self, name: str) -> str:
        """Generate a human-readable player ID from name."""
        # Simple mock implementation
        initials = ''.join(word[0].upper() for word in name.split() if word)
        return f"{initials}{self._next_id:02d}"
    
    def reset(self):
        """Reset the mock service state."""
        self._players.clear()
        self._next_id = 1
        self.logger.info("Mock: Player service reset") 