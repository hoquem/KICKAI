#!/usr/bin/env python3
"""
Simple ID Generator for KICKAI

This module provides a simplified ID generation system that creates human-readable IDs
in the format {Number}{Initials} for players and team members.

Examples:
- Mahmudul Hoque → 01MH
- Second Mahmudul Hoque → 02MH
- John Smith → 01JS
- Second John Smith → 02JS
"""

import re
from typing import Optional

from loguru import logger

from kickai.utils.constants import FALLBACK_ID_PREFIX, ID_NUMBER_FORMAT, LOG_MESSAGES, MAX_ID_NUMBER


class SimpleIDGenerator:
    """Simple ID generator for players and team members."""

    def __init__(self):
        self.used_ids: set[str] = set()

    def generate_player_id(
        self, name: str, team_id: str, existing_ids: Optional[set[str]] = None
    ) -> str:
        """
        Generate a simple player ID in format {Number}{Initials}.

        Args:
            name: Player's full name
            team_id: Team ID for context
            existing_ids: Set of existing IDs to avoid collisions

        Returns:
            Player ID in format 01MH, 02MH, etc.
        """
        # Get initials from name
        initials = self._extract_initials(name)

        # Get existing IDs for collision detection
        all_existing_ids = self.used_ids.copy()
        if existing_ids:
            all_existing_ids.update(existing_ids)

        # Find the next available number for these initials
        number = 1
        while True:
            candidate_id = ID_NUMBER_FORMAT.format(number) + initials
            if candidate_id not in all_existing_ids:
                # Add to our tracking set
                self.used_ids.add(candidate_id)
                logger.info(
                    LOG_MESSAGES["ID_GENERATED"].format(id=candidate_id, name=name, team_id=team_id)
                )
                return candidate_id
            number += 1

            # Safety check to prevent infinite loops
            if number > MAX_ID_NUMBER:
                logger.warning(
                    LOG_MESSAGES["TOO_MANY_PLAYERS"].format(initials=initials, team_id=team_id)
                )
                # Use a hash-based fallback
                import hashlib

                hash_suffix = hashlib.md5(f"{name}{team_id}".encode()).hexdigest()[:2].upper()
                fallback_id = f"{FALLBACK_ID_PREFIX}{initials}{hash_suffix}"
                self.used_ids.add(fallback_id)
                return fallback_id

    def generate_team_member_id(
        self, name: str, team_id: str, existing_ids: Optional[set[str]] = None
    ) -> str:
        """
        Generate a simple team member ID in format user_{Number}{Initials}.

        Args:
            name: Team member's full name
            team_id: Team ID for context
            existing_ids: Set of existing IDs to avoid collisions

        Returns:
            Team member ID in format user_01MH, user_02MH, etc.
        """
        # Generate the base ID using the same logic as player IDs
        base_id = self.generate_player_id(name, team_id, existing_ids)
        # Return with user_ prefix for team members
        return f"user_{base_id}"

    def _extract_initials(self, name: str) -> str:
        """
        Extract initials from a full name.

        Args:
            name: Full name (e.g., "Mahmudul Hoque", "John Smith")

        Returns:
            Uppercase initials (e.g., "MH", "JS")
        """
        if not name or not name.strip():
            return "UN"

        # Clean and split the name
        name_parts = re.sub(r"\s+", " ", name.strip()).split()

        if len(name_parts) == 0:
            return "UN"
        elif len(name_parts) == 1:
            # Single name - use first two letters
            return name_parts[0][:2].upper()
        else:
            # Multiple names - use first letter of first and last name
            first_initial = name_parts[0][0].upper()
            last_initial = name_parts[-1][0].upper()
            return f"{first_initial}{last_initial}"

    def clear_used_ids(self):
        """Clear the used IDs set (useful for testing)."""
        self.used_ids.clear()
        logger.info(LOG_MESSAGES["USED_IDS_CLEARED"])


# Global instance
simple_id_generator = SimpleIDGenerator()


# Convenience functions
def generate_simple_player_id(name: str, team_id: str, existing_ids: Optional[set[str]] = None) -> str:
    """Generate a simple player ID."""
    return simple_id_generator.generate_player_id(name, team_id, existing_ids)


def generate_simple_team_member_id(
    name: str, team_id: str, existing_ids: Optional[set[str]] = None
) -> str:
    """Generate a simple team member ID."""
    return simple_id_generator.generate_team_member_id(name, team_id, existing_ids)


def extract_initials(name: str) -> str:
    """Extract initials from a name."""
    return simple_id_generator._extract_initials(name)
