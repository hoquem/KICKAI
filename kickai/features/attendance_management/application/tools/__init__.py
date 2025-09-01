"""Attendance Management Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for attendance management features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all attendance management tools
from .attendance_tools import (
    record_attendance,
    get_match_attendance,
    get_player_attendance_history,
    get_attendance_summary,
    update_attendance,
    get_attendance_statistics
)

# Export all tools for agent registration
__all__ = [
    "record_attendance",
    "get_match_attendance", 
    "get_player_attendance_history",
    "get_attendance_summary",
    "update_attendance",
    "get_attendance_statistics"
]