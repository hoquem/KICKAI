"""
Player Registration Commands

This module provides command handlers for player registration functionality.
Commands are registered using @command decorators in individual files.
"""

# Import command modules to ensure decorators are executed
from . import player_commands
from . import check_fa_command

__all__ = [
    "player_commands",
    "check_fa_command"
]
