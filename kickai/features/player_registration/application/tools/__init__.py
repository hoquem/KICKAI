"""Player Registration Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for player registration features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools
from .player_tools import (
    approve_player,
    list_players_all,
    list_players_active
)
from .player_info_tools import (
    get_player_info,
    get_player_current_info,
    get_player_current_match,
    list_team_combined,
    get_availability_player_history
)
from .player_update_tools import (
    update_player_field,
    update_player_multiple,
    get_player_update_help
)

# Export all tools for agent registration
__all__ = [
    # Player management tools
    "approve_player",
    "list_players_all", 
    "list_players_active",
    # Player info tools
    "get_player_info",
    "get_player_current_info", 
    "get_player_current_match",
    "list_team_combined",
    "get_availability_player_history",
    # Player update tools
    "update_player_field",
    "update_player_multiple",
    "get_player_update_help"
]