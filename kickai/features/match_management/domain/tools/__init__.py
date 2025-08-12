# Import the native CrewAI tools (working version with plain string returns)
from .attendance_tools_native import (
    bulk_record_attendance,
    get_match_attendance,
    get_player_attendance_history,
    record_attendance,
)
from .availability_tools_native import (
    get_availability,
    get_player_availability_history,
    mark_availability,
    send_availability_reminders,
)
from .match_tools_native import (
    create_match,
    get_match_details,
    list_matches_sync,
    record_match_result,
    select_squad_tool,
)
from .squad_tools_native import (
    get_available_players_for_squad,
    get_squad_for_match,
    select_squad_for_match,
)

__all__ = [
    # Match tools
    "create_match",
    "list_matches_sync",
    "get_match_details",
    "select_squad_tool",
    "record_match_result",
    # Squad tools
    "get_available_players_for_squad",
    "get_squad_for_match",
    "select_squad_for_match",
    # Availability tools
    "mark_availability",
    "get_availability",
    "get_player_availability_history",
    "send_availability_reminders",
    # Attendance tools
    "record_attendance",
    "get_match_attendance",
    "get_player_attendance_history",
    "bulk_record_attendance",
]

# Note: JSON versions of these tools are deprecated and should not be used
# All imports now use native CrewAI tools with plain string returns
