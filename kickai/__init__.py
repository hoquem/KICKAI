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
from .core.settings import get_settings, initialize_settings
from .database.firebase_client import get_firebase_client
from .utils.football_id_generator import (
    generate_football_match_id,
    generate_football_player_id,
    generate_football_team_id,
)

__all__ = [
    "get_settings",
    "initialize_settings",
    "get_service",
    "get_singleton",
    "get_firebase_client",
    "generate_football_team_id",
    "generate_football_player_id",
    "generate_football_match_id"
]
