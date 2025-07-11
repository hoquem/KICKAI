"""
Constants for KICKAI

This module centralizes all constants used throughout the application.
"""

# Firestore Collection Prefix
FIRESTORE_COLLECTION_PREFIX = "kickai"

# Team ID
DEFAULT_TEAM_ID = "KAI"

# Bot Version
BOT_VERSION = "1.0.0"

# Collection Names (without prefix)
COLLECTION_PLAYERS = "players"
COLLECTION_TEAMS = "teams"
COLLECTION_TEAM_MEMBERS = "team_members"
COLLECTION_MATCHES = "matches"
COLLECTION_BOT_MAPPINGS = "bot_mappings"
COLLECTION_PAYMENTS = "payments"
COLLECTION_DAILY_STATUS = "daily_status"
COLLECTION_FIXTURES = "fixtures"

# Full collection names (with prefix)
def get_collection_name(collection: str) -> str:
    """Get the full collection name with prefix."""
    return f"{FIRESTORE_COLLECTION_PREFIX}_{collection}"

# Predefined full collection names
FIRESTORE_COLLECTIONS = {
    "players": get_collection_name(COLLECTION_PLAYERS),
    "teams": get_collection_name(COLLECTION_TEAMS),
    "team_members": get_collection_name(COLLECTION_TEAM_MEMBERS),
    "matches": get_collection_name(COLLECTION_MATCHES),
    "bot_mappings": get_collection_name(COLLECTION_BOT_MAPPINGS),
    "payments": get_collection_name(COLLECTION_PAYMENTS),
    "daily_status": get_collection_name(COLLECTION_DAILY_STATUS),
    "fixtures": get_collection_name(COLLECTION_FIXTURES),
} 