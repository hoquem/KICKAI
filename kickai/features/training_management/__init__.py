"""
Training Management Feature Module

This module provides comprehensive training session management for football teams,
including session scheduling, attendance tracking, progression monitoring, and analytics.
"""

__version__ = "1.0.0"
__feature__ = "training_management"

# Import tools to register them with the tool registry
try:
    from kickai.features.training_management.domain.tools import (
        schedule_training_session,
        list_training_sessions,
        mark_training_attendance,
        get_training_attendance_summary,
        cancel_training_session,
    )
except ImportError as e:
    # Handle import errors gracefully during development
    import logging
    logging.getLogger(__name__).warning(f"Failed to import training tools: {e}") 