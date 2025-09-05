"""Squad Selection Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for squad selection and availability management.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import squad and availability tools (clean naming convention)
from .squad_availability_tools import (
    get_attendance_player_history_lookup,
    get_attendance_player_history_self,
    get_availability_player_lookup,
    get_availability_player_self,
    get_availability_summary,
    list_matches_upcoming,
    list_players_available,
    select_squad_optimal,
)

# Export all tools for agent registration
__all__ = [
    # Squad selection tools (clean naming convention)
    "select_squad_optimal",
    "list_players_available",
    "get_availability_summary",
    "get_availability_player_self",
    "get_availability_player_lookup",
    "get_attendance_player_history_self",
    "get_attendance_player_history_lookup",
    "list_matches_upcoming",
]
