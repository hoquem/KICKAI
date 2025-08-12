#!/usr/bin/env python3
"""
Team administration tools module.

This module provides tools for team administration and management.
"""

# Import the native CrewAI tools (working version with plain string returns)
from .simplified_team_member_tools_native import add_team_member_simplified

# Import team member tools
from .team_member_tools_native import (
    add_team_member_role,
    get_my_team_member_status,
    get_team_members,
    promote_team_member_to_admin,
    remove_team_member_role,
    team_member_registration,
)

# Import team member update tools
from .update_team_member_tools_native import (
    get_pending_team_member_approval_requests,
    get_team_member_updatable_fields,
    update_team_member_information,
)

__all__ = [
    # Team member registration
    "team_member_registration",
    "get_my_team_member_status",
    # Team member management
    "get_team_members", 
    "add_team_member_role",
    "remove_team_member_role",
    "promote_team_member_to_admin",
    # Simplified team member tools
    "add_team_member_simplified",
    # Team member update tools
    "update_team_member_information",
    "get_team_member_updatable_fields",
    "get_pending_team_member_approval_requests",
    # Note: validate_team_member_update_request is only available in JSON version
    # and is temporarily disabled pending native implementation
]

# Note: JSON versions of these tools are deprecated and should not be used
# All imports now use native CrewAI tools with plain string returns
