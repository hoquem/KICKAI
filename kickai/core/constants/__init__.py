"""
System constants for KICKAI.

This package contains all system-wide constants, replacing magic numbers
and string literals with properly named, typed constants.
"""

# Import Firestore constants for backward compatibility
from kickai.core.firestore_constants import (
    FIRESTORE_COLLECTION_PREFIX,
    get_collection_name,
    get_team_matches_collection,
    get_team_players_collection,
    get_team_specific_collection_name,
)

from .agent_constants import AgentConstants
from .system_constants import SystemConstants
from .timeout_constants import TimeoutConstants
from .validation_constants import ValidationConstants

# Export commonly used constants for backward compatibility
BOT_VERSION = SystemConstants.BOT_VERSION
normalize_chat_type = SystemConstants.normalize_chat_type
get_chat_type_display_name = SystemConstants.get_chat_type_display_name

# Create aliases for backward compatibility
LimitConstants = ValidationConstants  # Use ValidationConstants as LimitConstants
get_players_collection = get_team_players_collection  # Alias for backward compatibility
get_team_members_collection = get_team_players_collection  # Alias for backward compatibility

# Note: get_command_by_name is available in kickai.core.constants.py
# Import it directly where needed to avoid circular imports

__all__ = [
    "SystemConstants",
    "AgentConstants",
    "ValidationConstants",
    "TimeoutConstants",
    "LimitConstants",
    "BOT_VERSION",
    "normalize_chat_type",
    "get_chat_type_display_name",
    "get_players_collection",
    "get_team_members_collection",
    "get_team_players_collection",
    "get_team_matches_collection",
    "get_collection_name",
    "get_team_specific_collection_name",
    "FIRESTORE_COLLECTION_PREFIX",
]
