"""
Team Administration Commands

This module contains commands for team administration.
"""

# Import the actual command modules that exist
from . import player_admin_commands, team_commands, update_commands

_all_ = ["team_commands", "player_admin_commands", "update_commands"]
