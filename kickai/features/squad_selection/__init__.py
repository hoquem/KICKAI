"""Squad Selection Feature - Clean Architecture Implementation

This feature handles squad selection, availability management, and match coordination
for the KICKAI football team management system.
"""

# Import and export all tools for the SQUAD_SELECTOR agent
from .application.tools import *

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
