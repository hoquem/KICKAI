#!/usr/bin/env python3
"""
Team Mapping Service Interface for KICKAI

This interface defines the contract for team mapping services that manage
the mapping between Telegram chat IDs and team IDs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any


class ITeamMappingService(ABC):
    """Interface for team mapping services."""
    
    @abstractmethod
    def set_default_team_id(self, team_id: str) -> None:
        """Set the default team ID for fallback scenarios."""
        pass
    
    @abstractmethod
    def get_default_team_id(self) -> Optional[str]:
        """Get the default team ID."""
        pass
    
    @abstractmethod
    def add_chat_mapping(self, chat_id: str, team_id: str) -> None:
        """Add a chat ID to team ID mapping."""
        pass
    
    @abstractmethod
    def get_team_id_for_chat(self, chat_id: str) -> Optional[str]:
        """Get team ID for a chat ID with caching."""
        pass
    
    @abstractmethod
    async def load_mappings_from_firestore(self) -> None:
        """Load team mappings from Firestore and cache them."""
        pass
    
    @abstractmethod
    async def save_mapping_to_firestore(self, chat_id: str, team_id: str) -> bool:
        """Save a team mapping to Firestore."""
        pass
    
    @abstractmethod
    def get_all_mappings(self) -> Dict[str, str]:
        """Get all current chat to team mappings."""
        pass
    
    @abstractmethod
    def clear_mappings(self) -> None:
        """Clear all mappings (useful for testing)."""
        pass
    
    @abstractmethod
    def get_mapping_stats(self) -> Dict[str, Any]:
        """Get statistics about team mappings."""
        pass 