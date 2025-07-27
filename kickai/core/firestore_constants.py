#!/usr/bin/env python3
"""
KICKAI Firestore Constants

This module contains Firestore-specific constants and collection naming utilities.
"""

# Firestore Collection Prefix
FIRESTORE_COLLECTION_PREFIX = "kickai"

# Team ID - Should be read from Firestore, not hardcoded
# DEFAULT_TEAM_ID = "KTI"  # REMOVED: Team ID should come from context

# Bot Version
BOT_VERSION = "1.0.0"

# Collection Names (without prefix)
COLLECTION_PLAYERS = "players"
COLLECTION_TEAMS = "teams"
COLLECTION_TEAM_MEMBERS = "team_members"
COLLECTION_MATCHES = "matches"
COLLECTION_PAYMENTS = "payments"
COLLECTION_DAILY_STATUS = "daily_status"
COLLECTION_MESSAGES = "messages"
COLLECTION_HEALTH_CHECKS = "health_checks"
COLLECTION_ATTENDANCE = "attendance"


# Full collection names (with prefix)
def get_collection_name(collection: str) -> str:
    """Get the full collection name with prefix."""
    return f"{FIRESTORE_COLLECTION_PREFIX}_{collection}"


# Team-specific collection naming (SINGLE SOURCE OF TRUTH)
def get_team_specific_collection_name(team_id: str, collection_type: str) -> str:
    """
    Get team-specific collection name.

    Args:
        team_id: The team ID (e.g., 'KTI', 'KAI')
        collection_type: The collection type (e.g., 'team_members', 'players')

    Returns:
        Full collection name with prefix and team ID
    """
    return f"{FIRESTORE_COLLECTION_PREFIX}_{team_id}_{collection_type}"


# Specific team collection helpers
def get_team_members_collection(team_id: str) -> str:
    """Get team members collection name for a specific team."""
    # Team members are stored in team-specific collections
    return get_team_specific_collection_name(team_id, COLLECTION_TEAM_MEMBERS)


def get_team_players_collection(team_id: str) -> str:
    """Get players collection name for a specific team."""
    # Players are stored in team-specific collections
    return get_team_specific_collection_name(team_id, COLLECTION_PLAYERS)


def get_team_matches_collection(team_id: str) -> str:
    """Get matches collection name for a specific team."""
    # Matches are stored in team-specific collections
    return get_team_specific_collection_name(team_id, COLLECTION_MATCHES)


# Predefined full collection names (for non-team-specific collections)
FIRESTORE_COLLECTIONS = {
    "players": get_collection_name(COLLECTION_PLAYERS),
    "teams": get_collection_name(COLLECTION_TEAMS),
    "team_members": get_collection_name(COLLECTION_TEAM_MEMBERS),
    "matches": get_collection_name(COLLECTION_MATCHES),
    "payments": get_collection_name(COLLECTION_PAYMENTS),
    "daily_status": get_collection_name(COLLECTION_DAILY_STATUS),
}
