"""
Player Service Interface

This module defines the interface for player management operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus


class IPlayerService(ABC):
    """Interface for player management operations."""
    
    @abstractmethod
    async def create_player(self, name: str, phone: str, team_id: str, 
                          email: Optional[str] = None, position: PlayerPosition = PlayerPosition.UTILITY,
                          role: PlayerRole = PlayerRole.PLAYER, fa_registered: bool = False) -> Player:
        """Create a new player with validation."""
        pass
    
    @abstractmethod
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        pass
    
    @abstractmethod
    async def update_player(self, player_id: str, **updates) -> Player:
        """Update a player with validation."""
        pass
    
    @abstractmethod
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        pass
    
    @abstractmethod
    async def get_team_players(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        pass
    
    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Get a player by phone number."""
        pass
    
    @abstractmethod
    async def update_onboarding_status(self, player_id: str, status: OnboardingStatus) -> Player:
        """Update player onboarding status."""
        pass
    
    @abstractmethod
    async def generate_invite_link(self, player_id: str, invite_link: str) -> Player:
        """Generate and store invite link for a player."""
        pass
    
    @abstractmethod
    async def generate_player_id(self, name: str) -> str:
        """Generate a human-readable player ID from name."""
        pass 