#!/usr/bin/env python3
"""
Team administration tools module.

This module provides tools for team administration and management.
"""

# Import the simplified team member tools
from .simplified_team_member_tools import add_team_member_simplified

# Import team member update tools
from .update_team_member_tools import (
    get_pending_team_member_approval_requests,
    get_team_member_updatable_fields,
    update_team_member_information,
    validate_team_member_update_request,
)

# Import new team member update tools (Phase 5)
from .team_member_update_tools import (
    update_team_member_field,
    update_team_member_multiple_fields,
    get_team_member_update_help,
    get_team_member_current_info,
    update_other_team_member,
)

# Import player management tools
from .player_management_tools import add_player

__all__ = [
    # Simplified team member tools
    "add_team_member_simplified",
    # Team member update tools
    "update_team_member_information",
    "get_team_member_updatable_fields",
    "validate_team_member_update_request",
    "get_pending_team_member_approval_requests",
    # New team member update tools (Phase 5)
    "update_team_member_field",
    "update_team_member_multiple_fields",
    "get_team_member_update_help",
    "get_team_member_current_info",
    "update_other_team_member",
    # Player management tools
    "add_player",
]
