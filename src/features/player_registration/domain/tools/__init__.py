#!/usr/bin/env python3
"""
Player registration tools module.

This module provides tools for player registration and management.
"""

# Import the function-based tools
from .registration_tools import (
    register_player,
    register_team_member,
    team_member_registration,
    registration_guidance
)

# Import the parser tool
from .registration_parser import parse_registration_command

from .player_tools import (
    approve_player,
    get_my_status,
    get_player_status,
    get_all_players,
    get_match
)



__all__ = [
    # Registration tools
    "register_player",
    "team_member_registration", 
    "registration_guidance",
    "parse_registration_command",
    
    # Player management tools (only the ones actually used by agents)
    "approve_player",
    "get_my_status",
    "get_player_status", 
    "get_all_players",
    "get_match",

]

# Note: Removed unused tools: remove_player, get_player_info, list_players
# These tools are not assigned to any agents in the configuration 