"""Training management tools for KICKAI system."""

# Import all training tools to register them with the tool registry
from .training_tools import (
    schedule_training_session,
    list_training_sessions,
    mark_training_attendance,
    get_training_attendance_summary,
    cancel_training_session,
)

__all__ = [
    "schedule_training_session",
    "list_training_sessions", 
    "mark_training_attendance",
    "get_training_attendance_summary",
    "cancel_training_session",
]