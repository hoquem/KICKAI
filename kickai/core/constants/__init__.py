"""
System constants for KICKAI.

This package contains all system-wide constants, replacing magic numbers
and string literals with properly named, typed constants.
"""

from .system_constants import SystemConstants
from .agent_constants import AgentConstants
from .validation_constants import ValidationConstants
from .timeout_constants import TimeoutConstants

# Import Firestore constants for backward compatibility
from kickai.core.firestore_constants import (
    get_team_players_collection,
    get_team_matches_collection,
    get_collection_name,
    get_team_specific_collection_name,
    FIRESTORE_COLLECTION_PREFIX,
)

# Note: get_players_collection and get_team_members_collection are available in kickai.core.constants
# Import them directly where needed to avoid circular imports

# Export commonly used constants for backward compatibility
BOT_VERSION = SystemConstants.BOT_VERSION
normalize_chat_type = SystemConstants.normalize_chat_type
get_chat_type_display_name = SystemConstants.get_chat_type_display_name

__all__ = [
    "SystemConstants",
    "AgentConstants", 
    "ValidationConstants",
    "TimeoutConstants",
    "BOT_VERSION",
    "normalize_chat_type",
    "get_chat_type_display_name",
    # "get_players_collection",  # Available in kickai.core.constants
    # "get_team_members_collection",  # Available in kickai.core.constants
    "get_team_players_collection",
    "get_team_matches_collection",
    "get_collection_name",
    "get_team_specific_collection_name",
    "FIRESTORE_COLLECTION_PREFIX",
]