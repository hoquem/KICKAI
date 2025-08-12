#!/usr/bin/env python3
"""
Player registration tools module.

This module provides tools for player registration and management.
"""

# Import the native CrewAI tools (working version without missing dependencies)
from .player_tools_native import (
    approve_player,
    get_active_players,
    get_all_players,
    get_my_status,
    list_team_members_and_players,
)

# Note: get_player_match and get_player_status are only in the JSON version
# For now, using native versions which don't include these tools

__all__ = [
    # Player management tools (available in native version)
    "approve_player",
    "get_my_status",
    "get_all_players",
    "get_active_players",
    "list_team_members_and_players",
    # Note: get_player_status and get_player_match are only in JSON version (temporarily unavailable)
]

# Note: Removed unused tools: remove_player, get_player_info, list_players
# These tools are not assigned to any agents in the configuration
