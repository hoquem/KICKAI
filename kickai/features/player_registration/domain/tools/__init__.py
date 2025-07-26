#!/usr/bin/env python3
"""
Player registration tools module.

This module provides tools for player registration and management.
"""

# Import the function-based tools
from .player_tools import (
    add_player,
    approve_player,
    get_all_players,
    get_match,
    get_my_status,
    get_player_status,
)

# Import the parser tool
from .registration_parser import parse_registration_command
from .registration_tools import (
    register_player,
    register_team_member,
    registration_guidance,
    team_member_registration,
)

__all__ = [
    # Registration tools
    "register_player",
    "team_member_registration",
    "registration_guidance",
    "parse_registration_command",

    # Player management tools (only the ones actually used by agents)
    "add_player",
    "approve_player",
    "get_my_status",
    "get_player_status",
    "get_all_players",
    "get_match",

]

# Note: Removed unused tools: remove_player, get_player_info, list_players
# These tools are not assigned to any agents in the configuration
