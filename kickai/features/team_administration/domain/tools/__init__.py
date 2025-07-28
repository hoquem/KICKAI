#!/usr/bin/env python3
"""
Team administration tools module.

This module provides tools for team administration and management.
"""

# Import the simplified team member tools
from .simplified_team_member_tools import add_team_member_simplified

# Import the update team member tools to register them
from . import update_team_member_tools

__all__ = [
    # Simplified team member tools
    "add_team_member_simplified",
]
