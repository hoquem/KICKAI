#!/usr/bin/env python3
"""
Player registration tools module.

This module provides tools for player registration and management.
"""

# Import the function-based tools
from .player_tools import (
    approve_player,
    get_all_players,
    get_active_players,
    get_my_status,
    get_player_match,
    get_player_status,
    list_team_members_and_players,
)

__all__ = [
    # Player management tools (only the ones actually used by agents)
    "approve_player",
    "get_my_status",
    "get_player_status",
    "get_all_players",
    "get_active_players",
    "get_player_match",
    "list_team_members_and_players",
]

# Note: Removed unused tools: remove_player, get_player_info, list_players
# These tools are not assigned to any agents in the configuration
