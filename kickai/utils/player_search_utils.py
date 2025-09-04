#!/usr/bin/env python3
"""
Player Search Utilities

This module provides shared utilities for player search functionality across different tools.
It centralizes the logic for finding players by various identifiers (ID, phone, name).
"""

from typing import Any

from loguru import logger

from kickai.features.player_registration.domain.entities.player import Player


class PlayerSearchResult:
    """Represents the result of a player search operation."""

    def __init__(
        self,
        player: Player | None = None,
        search_method: str = "unknown",
        searched_identifier: str = "",
    ):
        self.player = player
        self.search_method = search_method
        self.searched_identifier = searched_identifier
        self.found = player is not None

    def __bool__(self) -> bool:
        """Return True if player was found."""
        return self.found


async def find_player_by_identifier(
    player_service: Any, identifier: str, team_id: str, require_active: bool = False
) -> PlayerSearchResult:
    """
    Find a player using multiple search strategies.

    This function tries to find a player by:
    1. Player ID (exact match)
    2. Phone number (exact match)
    3. Name (partial case-insensitive match)

    Args:
        player_service: The player service instance
        identifier: The search identifier (ID, phone, or name)
        team_id: Team ID to search within
        require_active: If True, only return active players

    Returns:
        PlayerSearchResult containing the player (if found) and search metadata
    """
    if not identifier or not identifier.strip():
        logger.warning("Empty identifier provided to player search")
        return PlayerSearchResult(searched_identifier=identifier)

    identifier = identifier.strip()
    logger.debug(f"🔍 Searching for player '{identifier}' in team {team_id}")

    # Strategy 1: Try by player ID first (most specific)
    try:
        player = await player_service.get_player_by_id(identifier, team_id)
        if player and (not require_active or _is_player_active(player)):
            logger.debug(f"✅ Found player by ID: {player.name}")
            return PlayerSearchResult(player, "player_id", identifier)
    except Exception as e:
        logger.debug(f"Player ID search failed: {e}")
        pass

    # Strategy 2: Try by phone number (exact match)
    try:
        players = await player_service.get_all_players(team_id)
        for player in players:
            if player.phone_number == identifier:
                if not require_active or _is_player_active(player):
                    logger.debug(f"✅ Found player by phone: {player.name}")
                    return PlayerSearchResult(player, "phone", identifier)
    except Exception as e:
        logger.debug(f"Phone search failed: {e}")
        pass

    # Strategy 3: Try by name (partial case-insensitive match)
    try:
        players = await player_service.get_all_players(team_id)
        identifier_lower = identifier.lower()

        # First try exact name match
        for player in players:
            if player.name.lower() == identifier_lower:
                if not require_active or _is_player_active(player):
                    logger.debug(f"✅ Found player by exact name: {player.name}")
                    return PlayerSearchResult(player, "name_exact", identifier)

        # Then try partial name match
        for player in players:
            if identifier_lower in player.name.lower():
                if not require_active or _is_player_active(player):
                    logger.debug(f"✅ Found player by partial name: {player.name}")
                    return PlayerSearchResult(player, "name_partial", identifier)

    except Exception as e:
        logger.debug(f"Name search failed: {e}")
        pass

    logger.debug(f"❌ No player found for identifier '{identifier}'")
    return PlayerSearchResult(searched_identifier=identifier)


def _is_player_active(player: Player) -> bool:
    """Check if a player is active."""
    if not player or not player.status:
        return False

    status_str = player.status.value if hasattr(player.status, "value") else str(player.status)
    return status_str.lower() == "active"


def validate_player_identifier(identifier: str) -> tuple[bool, str]:
    """
    Validate a player identifier.

    Args:
        identifier: The identifier to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not identifier:
        return False, "Player identifier is required"

    if not identifier.strip():
        return False, "Player identifier cannot be empty or whitespace only"

    if len(identifier.strip()) < 2:
        return False, "Player identifier must be at least 2 characters long"

    # Check for potentially dangerous characters (basic validation)
    dangerous_chars = ["<", ">", '"', "'", "&", "\x00", "\n", "\r"]
    if any(char in identifier for char in dangerous_chars):
        return False, "Player identifier contains invalid characters"

    return True, ""


def format_search_suggestions(identifier: str, team_id: str) -> str:
    """
    Format helpful search suggestions for when a player is not found.

    Args:
        identifier: The failed search identifier
        team_id: Team ID that was searched

    Returns:
        Formatted suggestion message
    """
    return f"""❌ Player Not Found

No player found matching: "{identifier}"

💡 Try:
• Player ID: /status MH123
• Phone number: /status +447123456789
• Name (exact): /status John Smith
• Name (partial): /status John
• Check spelling and try again

🔍 Searched in team: {team_id}"""


def get_search_method_display(search_method: str) -> str:
    """
    Convert search method code to user-friendly display text.

    Args:
        search_method: The search method code

    Returns:
        User-friendly display text
    """
    method_map = {
        "player_id": "Player ID",
        "phone": "Phone Number",
        "name_exact": "Exact Name Match",
        "name_partial": "Partial Name Match",
        "unknown": "Unknown Method",
    }
    return method_map.get(search_method, search_method.replace("_", " ").title())
