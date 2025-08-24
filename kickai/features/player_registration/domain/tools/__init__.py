#!/usr/bin/env python3
"""
Player registration tools module.

This module provides tools for player registration and management.
"""

# Clean Architecture: Domain layer contains pure business logic functions only
# NO TOOLS EXPORTED - All CrewAI tools are provided by the Application layer
# 
# These functions are available for internal domain use but are not exposed as tools:
# - approve_player (service function)
# - get_my_status (service function) 
# - get_all_players (service function)
# - get_active_players (service function)
# - get_player_match (service function)
# - list_team_members_and_players (service function)
# - update_player_field (service function)
# - update_player_multiple_fields (service function)
# - get_player_update_help (service function)
# - get_player_current_info (service function)

# Domain layer exports nothing - all tools come from application layer
__all__ = []

# Note: Removed unused tools: remove_player, get_player_info, list_players, get_player_status
