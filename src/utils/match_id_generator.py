"""
Match ID Generator for KICKAI

This module provides human-readable match ID generation functionality
using the new comprehensive ID system.
"""

import logging
from typing import Dict
from .id_generator import id_manager, generate_match_id, generate_team_id

logger = logging.getLogger(__name__)


class MatchIDGenerator:
    """Legacy wrapper for backward compatibility."""
    
    def __init__(self):
        self.team_abbreviations = {}
        self.generated_ids = set()
        self.team_variations = {}
    
    def get_team_abbreviation(self, team_name: str) -> str:
        """Get team abbreviation using the new system."""
        return generate_team_id(team_name)
    
    def generate_match_id(self, opponent: str, date: str, venue: str = '') -> str:
        """Generate match ID using the new system."""
        home_team = "BP Hatters FC"  # Default home team
        return generate_match_id(home_team, opponent, date)
    
    def get_known_teams(self) -> Dict[str, str]:
        """Get known teams from the new system."""
        return id_manager.get_known_teams()
    
    def clear_memory(self):
        """Clear memory (for testing)."""
        id_manager.clear_all()


# Global instance for backward compatibility
match_id_generator = MatchIDGenerator() 