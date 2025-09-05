"""Player Registration Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for player registration features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools
from .player_info_tools import (
    get_player_by_identifier,
    get_player_match_by_identifier,
    get_player_match_self,
    get_player_self,
)
from .player_tools import approve_player, list_players_active, list_players_all
from .player_update_tools import (
    get_player_update_help,
    update_player_field,
    update_player_multiple_fields,
)

# Export all tools for agent registration
__all__ = [
    # Player management tools
    "approve_player",
    "list_players_all",
    "list_players_active",
    # Player info tools (CrewAI semantic naming)
    "get_player_self",
    "get_player_by_identifier",
    "get_player_match_self",
    "get_player_match_by_identifier",
    # Player update tools
    "update_player_field",
    "update_player_multiple_fields",
    "get_player_update_help",
]
