#!/usr/bin/env python3
"""
Player registration tools module.

This module provides tools for player registration and management.
"""

# Import the function-based tools
from .registration_tools import (
    register_player,
    team_member_registration,
    registration_guidance
)

from .player_tools import (
    register_player as register_player_tool,
    approve_player,
    get_player_info,
    list_players,
    remove_player,
    get_my_status,
    get_player_status,
    get_all_players,
    get_match,
    get_user_status,
    get_available_commands,
    format_help_message
)

__all__ = [
    # Registration tools
    "register_player",
    "team_member_registration", 
    "registration_guidance",
    
    # Player management tools
    "register_player_tool",
    "approve_player",
    "get_player_info",
    "list_players",
    "remove_player",
    "get_my_status",
    "get_player_status",
    "get_all_players",
    "get_match",
    "get_user_status",
    "get_available_commands",
    "format_help_message"
] 