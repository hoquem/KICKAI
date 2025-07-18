#!/usr/bin/env python3
"""
Player ID Service

This module provides services for generating and managing player IDs.
"""

from typing import Optional
from utils.id_generator import PlayerIDGenerator


class PlayerIDService:
    """Service for player ID generation and management."""
    
    def __init__(self, id_generator: PlayerIDGenerator):
        self.id_generator = id_generator
    
    def generate_player_id(self, name: str, team_id: str) -> str:
        """Generate a unique player ID."""
        return self.id_generator.generate_player_id(name, team_id)
    
    def validate_player_id(self, player_id: str) -> bool:
        """Validate a player ID format."""
        return self.id_generator.validate_player_id(player_id)
    
    def get_team_from_player_id(self, player_id: str) -> Optional[str]:
        """Extract team ID from player ID."""
        try:
            return self.id_generator.get_team_from_player_id(player_id)
        except ValueError:
            return None
    
    def get_name_from_player_id(self, player_id: str) -> Optional[str]:
        """Extract name from player ID."""
        try:
            return self.id_generator.get_name_from_player_id(player_id)
        except ValueError:
            return None 