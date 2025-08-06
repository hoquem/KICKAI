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
from datetime import datetime

from loguru import logger

from kickai.utils.constants import FALLBACK_ID_PREFIX, ID_NUMBER_FORMAT, LOG_MESSAGES, MAX_ID_NUMBER


class SimpleIDGenerator:
    """Simple ID generator for players and team members."""

    def __init__(self):
        self.used_ids: set[str] = set()

    def generate_player_id(
        self, name: str, team_id: str, existing_ids: set[str] | None = None
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
        self, name: str, team_id: str, existing_ids: set[str] | None = None
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

    def generate_match_id(self, team_id: str, opponent: str, match_date: datetime) -> str:
        """
        Generate a match ID in format MATCH_{Date}_{Team}_{Opponent}.

        Args:
            team_id: Team ID
            opponent: Opponent team name
            match_date: Match date

        Returns:
            Match ID in format MATCH_2024-01-15_KTI_ARSENAL
        """
        date_str = match_date.strftime("%Y-%m-%d")
        opponent_clean = re.sub(r'[^A-Za-z0-9]', '', opponent.upper())
        match_id = f"MATCH_{date_str}_{team_id}_{opponent_clean}"

        logger.info(f"Generated match ID: {match_id}")
        return match_id

    def generate_availability_id(self, match_id: str, player_id: str) -> str:
        """
        Generate an availability ID in format AVAIL_{MatchID}_{PlayerID}.

        Args:
            match_id: Match ID
            player_id: Player ID

        Returns:
            Availability ID in format AVAIL_MATCH_2024-01-15_KTI_ARSENAL_01MH
        """
        availability_id = f"AVAIL_{match_id}_{player_id}"

        logger.info(f"Generated availability ID: {availability_id}")
        return availability_id

    def generate_attendance_id(self, match_id: str, player_id: str) -> str:
        """
        Generate an attendance ID in format ATTEND_{MatchID}_{PlayerID}.

        Args:
            match_id: Match ID
            player_id: Player ID

        Returns:
            Attendance ID in format ATTEND_MATCH_2024-01-15_KTI_ARSENAL_01MH
        """
        attendance_id = f"ATTEND_{match_id}_{player_id}"

        logger.info(f"Generated attendance ID: {attendance_id}")
        return attendance_id

    def _extract_initials(self, name: str) -> str:
        """
        Extract initials from a full name.

        Args:
            name: Full name (e.g., "Mahmudul Hoque", "John Smith")

        Returns:
            Initials in uppercase (e.g., "MH", "JS")
        """
        # Split the name into words and extract first letter of each
        words = name.strip().split()
        if not words:
            return "XX"  # Fallback for empty names

        initials = "".join(word[0].upper() for word in words if word)

        # Ensure we have at least 2 characters
        if len(initials) < 2:
            initials = initials + "X" * (2 - len(initials))
        elif len(initials) > 2:
            initials = initials[:2]  # Take only first 2 initials

        return initials

    def clear_used_ids(self):
        """Clear the set of used IDs."""
        self.used_ids.clear()
        logger.info("Cleared used IDs set")


# Global instance
simple_id_generator = SimpleIDGenerator()


# Convenience functions
def generate_simple_player_id(name: str, team_id: str, existing_ids: set[str] | None = None) -> str:
    """Generate a simple player ID."""
    return simple_id_generator.generate_player_id(name, team_id, existing_ids)


def generate_simple_team_member_id(
    name: str, team_id: str, existing_ids: set[str] | None = None
) -> str:
    """Generate a simple team member ID."""
    return simple_id_generator.generate_team_member_id(name, team_id, existing_ids)


def extract_initials(name: str) -> str:
    """Extract initials from a full name."""
    return simple_id_generator._extract_initials(name)
