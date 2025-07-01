"""
DEPRECATED: Player Registration logic has moved to the new service layer.

This file is retained for backward compatibility and will be removed in a future release.
Use src/services/player_service.py and src/telegram/player_registration_handler.py instead.
"""

from src.services.player_service import get_player_service
from src.services.team_service import get_team_service
from src.telegram.player_registration_handler import PlayerRegistrationHandler, PlayerCommandHandler
from src.database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus

# Example usage for migration reference:
# player_service = get_player_service()
# team_service = get_team_service()
# handler = PlayerRegistrationHandler(team_id="your_team_id")
# command_handler = PlayerCommandHandler(handler)

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DEPRECATED: All legacy classes have been removed
# Use the new service layer and handlers instead:
# - PlayerService for player operations
# - PlayerRegistrationHandler for registration workflow
# - PlayerCommandHandler for command processing 