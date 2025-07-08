"""
Domain interface for match status.

This interface defines match status constants without depending
on the infrastructure layer.
"""

from enum import Enum


class MatchStatus(Enum):
    """Match status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed" 