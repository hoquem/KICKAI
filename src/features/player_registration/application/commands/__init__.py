"""
Player Registration Commands

This module provides command handlers for player registration functionality.
"""

from core.command_registry import get_command_registry, command
from .player_commands import handle_add_player
from .check_fa_command import CheckFACommand

# Get the command registry
registry = get_command_registry()

# Register commands with the unified registry
registry.register_command(
    name="/add",
    description="Add a new player to the team",
    handler=handle_add_player,
    feature="player_registration",
    aliases=["/addplayer", "/register"],
    examples=[
        "/add John Smith 07123456789 Forward",
        "/add Jane Doe 07987654321 Midfielder true"
    ],
    parameters={
        "player_name": "Full name of the player",
        "phone": "Phone number (format: 07XXXXXXXXX)",
        "position": "Player position (Forward, Midfielder, Defender, Goalkeeper)",
        "fa_eligible": "Whether player is FA eligible (true/false, optional)"
    },
    help_text="Add a new player to the team. The player will be assigned a unique ID and added to the team roster."
)

# Register the CheckFACommand
check_fa_command = CheckFACommand()
registry.register_command(
    name="/checkfa",
    description="Check FA registration status for a player",
    handler=check_fa_command.execute,
    feature="player_registration",
    permission_level="leadership",
    aliases=["/fa", "/facheck"],
    examples=[
        "/checkfa JS001",
        "/checkfa John Smith"
    ],
    parameters={
        "player_id": "Player ID or name to check"
    },
    help_text="Check the FA registration status for a specific player. This will query the FA website for current registration information."
)

__all__ = [
    "handle_add_player",
    "CheckFACommand"
]
