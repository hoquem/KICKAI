"""
KICKAI - AI-powered Telegram bot for Sunday league football team management

This package provides the core functionality for managing Sunday league football teams
through an intelligent Telegram bot interface.
"""

__version__ = "0.1.0"
__author__ = "KICKAI Team"
__description__ = "AI-powered Telegram bot for Sunday league football team management"

# Export main components for easy access
from .core.dependency_container import get_service, get_singleton
from .core.config import get_settings
from .database.firebase_client import get_firebase_client
from .utils.id_generator import (
    generate_match_id,
    generate_member_id,
    generate_team_id,
)

__all__ = [
    "generate_match_id",
    "generate_member_id",
    "generate_team_id",
    "get_firebase_client",
    "get_service",
    "get_settings",
    "get_singleton",
]
