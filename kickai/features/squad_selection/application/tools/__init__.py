"""Squad Selection Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for squad selection and availability management.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import squad and availability tools (clean naming convention)
from .squad_availability_tools import (
    select_squad_optimal,
    list_players_available,
    get_availability_summary,
    get_availability_player,
    get_attendance_player_history,
    list_matches_upcoming
)

# Export all tools for agent registration
__all__ = [
    # Squad selection tools (clean naming convention)
    "select_squad_optimal",
    "list_players_available",
    "get_availability_summary",
    "get_availability_player",
    "get_attendance_player_history",
    "list_matches_upcoming"
]