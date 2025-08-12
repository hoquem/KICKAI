"""
Simple ID Generator for KICKAI

This module provides a single, consistent ID generation system:
- Team IDs: Simple team codes (e.g., KAI, MCI, LIV)
- Team Member IDs: M + 2-digit number + initials (e.g., M01MH for Mahmudul Hoque)
- Match IDs: M + DDMM + team codes (e.g., M1501KAILIV)
- User linking: Uses telegram_id directly (integer)

Features:
- Single source of truth for all ID generation
- Simple, readable formats
- Collision detection and resolution
- Stable IDs (same input = same ID)
"""

import hashlib
import re
import threading
from datetime import datetime

from loguru import logger


class SimpleIDGenerator:
    """Thread-safe simple ID generator with consistent formats."""

    def __init__(self):
        self.used_team_ids: set[str] = set()
        self.used_member_ids: set[str] = set()
        self.used_match_ids: set[str] = set()
        self.team_mappings: dict[str, str] = {}
        self.member_mappings: dict[str, str] = {}
        self._lock = threading.RLock()  # Reentrant lock for nested calls

    def _normalize_name(self, name: str) -> str:
        """Normalize a name for consistent processing."""
        if not name:
            return ""

        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r"\s+", " ", name.lower().strip())

        # Remove common words that don't add meaning
        common_words = ["the", "fc", "football", "club", "united", "city", "town"]
        words = normalized.split()
        filtered_words = [word for word in words if word not in common_words]

        return " ".join(filtered_words)

    def _generate_simple_team_code(self, team_name: str) -> str:
        """Generate a simple 3-4 letter team code."""
        normalized = self._normalize_name(team_name)

        if not normalized:
            return "UNK"

        words = normalized.split()

        if len(words) >= 2:
            # Use first letter of each word (max 4 characters)
            code = "".join(word[0].upper() for word in words[:4])
            return code[:4]
        else:
            # For single words, use first 3-4 letters
            return normalized[:4].upper()

    def generate_team_id(self, team_name: str) -> str:
        """Generate a simple team ID (thread-safe)."""
        if not team_name or not team_name.strip():
            raise ValueError("Team name cannot be empty")

        with self._lock:
            normalized = self._normalize_name(team_name)

            # Check if we already have a mapping
            if normalized in self.team_mappings:
                return self.team_mappings[normalized]

            # Generate simple team code (3-4 characters)
            team_code = self._generate_simple_team_code(team_name)

            # Resolve collision
            final_id = self._resolve_collision(team_code, self.used_team_ids)

            # Store mapping atomically
            self.team_mappings[normalized] = final_id
            self.used_team_ids.add(final_id)

            logger.info(f"Generated team ID '{final_id}' for '{team_name}'")
            return final_id

    def generate_member_id(self, name: str, existing_ids: set[str] | None = None) -> str:
        """Generate a team member ID with format M + 3-digit number + initials (thread-safe)."""
        if not name or not name.strip():
            raise ValueError("Member name cannot be empty")

        with self._lock:
            # Parse name into first and last components
            name_parts = name.strip().split()
            if len(name_parts) >= 2:
                first_initial = name_parts[0][0].upper()
                last_initial = name_parts[-1][0].upper()
            else:
                # Single name - use first letter twice
                first_initial = name_parts[0][0].upper() if name_parts else "U"
                last_initial = first_initial

            initials = f"{first_initial}{last_initial}"

            # Get existing member numbers
            existing_numbers = set()
            id_set = existing_ids or self.used_member_ids

            for member_id in id_set:
                if member_id.startswith("M") and len(member_id) >= 4:
                    # Extract number from existing member IDs (M001XX format)
                    match = re.match(r"M(\d{3})", member_id)
                    if match:
                        existing_numbers.add(int(match.group(1)))

            # Find next available number (increased limit to 999)
            member_number = 1
            while member_number in existing_numbers:
                member_number += 1
                if member_number > 999:  # Limit to 999 members
                    # Use hash-based fallback for very large teams
                    hash_suffix = hashlib.md5(f"{name}{len(existing_numbers)}".encode()).hexdigest()[:3].upper()
                    base_id = f"M{hash_suffix}{initials}"
                    break
            else:
                # Create member ID: M + 3-digit number + initials
                base_id = f"M{member_number:03d}{initials}"

            # Resolve collision with enhanced strategy
            final_id = self._resolve_collision_robust(base_id, id_set)

            # Store mapping atomically
            member_key = name.lower().strip()
            self.member_mappings[member_key] = final_id
            if existing_ids is not None:
                existing_ids.add(final_id)
            else:
                self.used_member_ids.add(final_id)

            logger.info(f"Generated member ID '{final_id}' for '{name}'")
            return final_id

    def generate_match_id(
        self,
        home_team: str,
        away_team: str,
        match_date: str,
    ) -> str:
        """Generate a simple match ID with format M + DDMM + team codes (thread-safe)."""
        if not home_team or not away_team or not match_date:
            raise ValueError("Home team, away team, and match date are required")

        with self._lock:
            # Get team IDs (these calls are also thread-safe)
            home_id = self.generate_team_id(home_team)
            away_id = self.generate_team_id(away_team)

            # Parse date to get day and month
            try:
                parsed_date = datetime.strptime(match_date, "%Y-%m-%d")
                day = parsed_date.day
                month = parsed_date.month

                # Create match ID: M + DDMM + home_team + away_team
                base_id = f"M{day:02d}{month:02d}{home_id}{away_id}"

                # Resolve collision by adding number suffix if needed
                final_id = self._resolve_collision_robust(base_id, self.used_match_ids)
                self.used_match_ids.add(final_id)

                logger.info(f"Generated match ID '{final_id}' for {home_team} vs {away_team} on {match_date}")
                return final_id

            except Exception as e:
                logger.error(f"Date parsing error: {e}")
                # Fallback to sequential numbering with team info
                match_number = len(self.used_match_ids) + 1
                final_id = f"M{match_number:03d}{home_id}{away_id}"
                final_id = self._resolve_collision_robust(final_id, self.used_match_ids)
                self.used_match_ids.add(final_id)
                logger.info(f"Generated fallback match ID '{final_id}' for {home_team} vs {away_team}")
                return final_id

    def generate_training_id(self, team_id: str, session_type: str, date: str, time: str) -> str:
        """Generate a training session ID (thread-safe)."""
        if not all([team_id, session_type, date, time]):
            raise ValueError("All training parameters are required")

        with self._lock:
            try:
                # Parse date to get day and month
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
                day = parsed_date.day
                month = parsed_date.month

                # Parse time to get hour
                parsed_time = datetime.strptime(time, "%H:%M")
                hour = parsed_time.hour

                # Get session type abbreviation
                type_abbrev = {
                    "technical_skills": "TECH",
                    "tactical_awareness": "TACT",
                    "fitness_conditioning": "FIT",
                    "match_practice": "MATCH",
                    "recovery_session": "REC"
                }.get(session_type.lower(), "TRAIN")

                # Create training ID: T + DDMM + team_id + type + HHMM
                training_id = f"T{day:02d}{month:02d}{team_id}{type_abbrev}{hour:02d}00"

                logger.info(f"Generated training ID '{training_id}' for {team_id} on {date} at {time}")
                return training_id

            except ValueError as e:
                logger.error(f"Error generating training ID: {e}")
                # Fallback to simple format
                fallback_id = f"T{team_id}{session_type[:4].upper()}{date.replace('-', '')}"
                logger.info(f"Generated fallback training ID '{fallback_id}'")
                return fallback_id

    def _resolve_collision(self, base_id: str, existing_ids: set[str]) -> str:
        """Resolve ID collision by adding a number suffix (legacy method)."""
        return self._resolve_collision_robust(base_id, existing_ids)

    def _resolve_collision_robust(self, base_id: str, existing_ids: set[str]) -> str:
        """Enhanced collision resolution with better uniqueness guarantees."""
        if base_id not in existing_ids:
            return base_id

        # Try adding numbers 1-999 (increased range)
        for i in range(1, 1000):
            candidate = f"{base_id}{i}"
            if candidate not in existing_ids:
                return candidate

        # If numeric suffixes exhausted, use timestamp + hash approach
        import time
        timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of millisecond timestamp
        candidate = f"{base_id}T{timestamp}"
        if candidate not in existing_ids:
            return candidate

        # Final fallback: UUID-based suffix
        import uuid
        uuid_suffix = str(uuid.uuid4())[:8].upper().replace('-', '')
        return f"{base_id}U{uuid_suffix}"

    def get_team_mappings(self) -> dict[str, str]:
        """Get all team name to ID mappings (thread-safe)."""
        with self._lock:
            return self.team_mappings.copy()

    def get_member_mappings(self) -> dict[str, str]:
        """Get all member name to ID mappings (thread-safe)."""
        with self._lock:
            return self.member_mappings.copy()

    def get_stats(self) -> dict[str, int]:
        """Get generator statistics (thread-safe)."""
        with self._lock:
            return {
                "team_ids_generated": len(self.used_team_ids),
                "member_ids_generated": len(self.used_member_ids),
                "match_ids_generated": len(self.used_match_ids),
                "team_mappings": len(self.team_mappings),
                "member_mappings": len(self.member_mappings),
            }

    def clear_all(self):
        """Clear all stored IDs (useful for testing) - thread-safe."""
        with self._lock:
            self.used_team_ids.clear()
            self.used_member_ids.clear()
            self.used_match_ids.clear()
            self.team_mappings.clear()
            self.member_mappings.clear()
            logger.info("Cleared all ID generator memory")


# Thread-safe singleton pattern
_instance = None
_instance_lock = threading.Lock()

def get_id_generator() -> SimpleIDGenerator:
    """Get the singleton ID generator instance (thread-safe)."""
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:  # Double-checked locking
                _instance = SimpleIDGenerator()
    return _instance

# Global instance (backward compatibility)
id_generator = get_id_generator()


# Convenience functions (thread-safe)
def generate_team_id(team_name: str) -> str:
    """Generate a simple team ID (thread-safe)."""
    return get_id_generator().generate_team_id(team_name)


def generate_member_id(name: str, existing_ids: set[str] | None = None) -> str:
    """Generate a team member ID (thread-safe)."""
    return get_id_generator().generate_member_id(name, existing_ids)


def generate_match_id(home_team: str, away_team: str, match_date: str) -> str:
    """Generate a simple match ID (thread-safe)."""
    return get_id_generator().generate_match_id(home_team, away_team, match_date)


def generate_training_id(team_id: str, session_type: str, date: str, time: str) -> str:
    """Generate a training session ID (thread-safe)."""
    return get_id_generator().generate_training_id(team_id, session_type, date, time)


# Legacy compatibility functions (thread-safe, will be removed after migration)
def generate_football_team_id(team_name: str, league_info: str = "") -> str:
    """Legacy function - use generate_team_id instead (thread-safe)."""
    logger.warning("Using deprecated function generate_football_team_id, use generate_team_id instead")
    return generate_team_id(team_name)


def generate_football_player_id(name: str, position: str, team_id: str, existing_ids: set[str] | None = None) -> str:
    """Legacy function - use generate_member_id instead (thread-safe)."""
    logger.warning("Using deprecated function generate_football_player_id, use generate_member_id instead")
    return generate_member_id(name, existing_ids)


def generate_football_match_id(home_team: str, away_team: str, match_date: str, competition: str = "FRIENDLY", match_time: str = "") -> str:
    """Legacy function - use generate_match_id instead (thread-safe)."""
    logger.warning("Using deprecated function generate_football_match_id, use generate_match_id instead")
    return generate_match_id(home_team, away_team, match_date)


def generate_football_training_id(team_id: str, session_type: str, date: str, time: str) -> str:
    """Legacy function - use generate_training_id instead (thread-safe)."""
    logger.warning("Using deprecated function generate_football_training_id, use generate_training_id instead")
    return generate_training_id(team_id, session_type, date, time)
