"""
Team Administration Feature

This module provides team administration functionality including
team management, member management, and role assignment.
"""

from typing import Any, Dict, List

from loguru import logger

# Import commands for discovery
from . import application  # This will discover all commands


def initialize_team_administration(config: dict[str, Any]) -> None:
    """Initialize the team administration feature."""
    logger.info("Initializing team administration feature")
    # Feature initialization logic would go here
    logger.info("Team administration feature initialized successfully")


def shutdown_team_administration() -> None:
    """Shutdown the team administration feature."""
    logger.info("Shutting down team administration feature")
    # Feature shutdown logic would go here
    logger.info("Team administration feature shutdown complete")


# Export all tools for CrewAI discovery
__all__ = [
    # Tools
    "add_player",
    "add_team_member_simplified", 
    "update_team_member_information",
    "get_team_member_updatable_fields",
    "validate_team_member_update_request",
    "get_pending_team_member_approval_requests",
    # Functions
    "initialize_team_administration",
    "shutdown_team_administration",
]
