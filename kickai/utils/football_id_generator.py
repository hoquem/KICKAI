"""
Football-Friendly ID Generator for KICKAI

This module provides football-contextual ID generation that makes sense to football people:
- Team IDs with league context (e.g., PLMCI for Premier League Manchester City)
- Player IDs with jersey numbers and positions (e.g., 01GKJS for Jersey #1 Goalkeeper John Smith)
- Match IDs with competition context (e.g., PL2024-01-15-MCI-LIV)

Features:
- Football-specific conventions (jersey numbers, positions, competitions)
- League and competition context
- Position-based player identification
- Professional football date formats
- Collision detection and resolution
- Stable IDs (same input = same ID)
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from loguru import logger


class PlayerPosition(Enum):
    """Football player positions with codes."""

    GOALKEEPER = "GK"
    DEFENDER = "DF"
    MIDFIELDER = "MF"
    FORWARD = "FW"
    WINGER = "WG"
    STRIKER = "ST"


class Competition(Enum):
    """Football competitions with prefixes."""

    PREMIER_LEAGUE = "PL"
    EFL_CHAMPIONSHIP = "EFL"
    EFL_LEAGUE_ONE = "EFL1"
    EFL_LEAGUE_TWO = "EFL2"
    FA_CUP = "FA"
    EFL_CUP = "EFLC"
    SUNDAY_LEAGUE = "SUN"
    FRIENDLY = "FRI"
    NON_LEAGUE = "NON"


@dataclass
class FootballIDGenerator:
    """Football-friendly ID generator with football conventions."""

    def __post_init__(self):
        self.used_team_ids: set[str] = set()
        self.used_player_ids: set[str] = set()
        self.used_match_ids: set[str] = set()
        self.team_mappings: dict[str, str] = {}
        self.player_mappings: dict[str, str] = {}

    def _normalize_name(self, name: str) -> str:
        """Normalize a name for consistent processing."""
        if not name:
            return ""

        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r"\s+", " ", name.lower().strip())

        # Remove common football words that don't add meaning
        common_words = [
            "the",
            "fc",
            "football",
            "club",
            "united",
            "city",
            "town",
            "athletic",
            "athletics",
            "rovers",
            "rangers",
            "wanderers",
        ]
        words = normalized.split()
        filtered_words = [word for word in words if word not in common_words]

        return " ".join(filtered_words)

    def _get_league_prefix(self, team_name: str, league_info: str = "") -> str:
        """Determine league prefix based on team name and league info."""
        team_lower = team_name.lower()
        league_lower = league_info.lower()

        # Check for Premier League teams (simplified list)
        pl_teams = [
            "arsenal",
            "chelsea",
            "liverpool",
            "manchester city",
            "manchester united",
            "tottenham",
            "newcastle",
            "brighton",
            "west ham",
            "crystal palace",
        ]

        if any(team in team_lower for team in pl_teams) or "premier" in league_lower:
            return Competition.PREMIER_LEAGUE.value

        # Check for EFL teams
        if any(
            word in league_lower for word in ["championship", "league one", "league two", "efl"]
        ):
            if "league one" in league_lower:
                return Competition.EFL_LEAGUE_ONE.value
            elif "league two" in league_lower:
                return Competition.EFL_LEAGUE_TWO.value
            else:
                return Competition.EFL_CHAMPIONSHIP.value

        # Check for Sunday League
        if any(word in league_lower for word in ["sunday", "amateur", "recreational"]):
            return Competition.SUNDAY_LEAGUE.value

        # Default to Non-League
        return Competition.NON_LEAGUE.value

    def _generate_simple_team_code(self, team_name: str) -> str:
        """Generate a simple 3-4 letter team code."""
        normalized = self._normalize_name(team_name)

        if not normalized:
            return "UNK"

        words = normalized.split()

        if len(words) >= 2:
            # Use first letter of each word (max 4 characters)
            code = "".join(word[0].upper() for word in words[:4])
            return code[:4]  # Limit to 4 characters
        else:
            # For single words, use first 3-4 letters
            return normalized[:4].upper()

    def generate_team_id(self, team_name: str, league_info: str = "") -> str:
        """Generate a simple team ID for Sunday league use."""
        normalized = self._normalize_name(team_name)

        # Check if we already have a mapping
        if normalized in self.team_mappings:
            return self.team_mappings[normalized]

        # Generate simple team code (3-4 characters)
        team_code = self._generate_simple_team_code(team_name)

        # Resolve collision
        final_id = self._resolve_collision(team_code, self.used_team_ids)

        # Store mapping
        self.team_mappings[normalized] = final_id
        self.used_team_ids.add(final_id)

        logger.info(f"Generated simple team ID '{final_id}' for '{team_name}'")
        return final_id

    def _get_position_code(self, position: str) -> str:
        """Get position code from position string."""
        position_lower = position.lower()

        if any(word in position_lower for word in ["goalkeeper", "keeper", "gk"]):
            return PlayerPosition.GOALKEEPER.value
        elif any(word in position_lower for word in ["defender", "defence", "defense", "back"]):
            return PlayerPosition.DEFENDER.value
        elif any(word in position_lower for word in ["midfielder", "midfield", "mid"]):
            return PlayerPosition.MIDFIELDER.value
        elif any(word in position_lower for word in ["forward", "striker", "attack"]):
            return PlayerPosition.FORWARD.value
        elif any(word in position_lower for word in ["winger", "wing"]):
            return PlayerPosition.WINGER.value
        else:
            return PlayerPosition.MIDFIELDER.value  # Default

    def _get_jersey_number(self, position: str, existing_numbers: set[int]) -> int:
        """Get appropriate jersey number based on position and availability."""
        position_code = self._get_position_code(position)

        # Traditional position-based number ranges
        position_ranges = {
            PlayerPosition.GOALKEEPER.value: [1, 12, 13, 25, 26],
            PlayerPosition.DEFENDER.value: [
                2,
                3,
                4,
                5,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
            ],
            PlayerPosition.MIDFIELDER.value: [
                6,
                7,
                8,
                10,
                11,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
            ],
            PlayerPosition.FORWARD.value: [
                9,
                10,
                11,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
            ],
            PlayerPosition.WINGER.value: [
                7,
                11,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
            ],
            PlayerPosition.STRIKER.value: [
                9,
                10,
                11,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
            ],
        }

        # Try position-appropriate numbers first
        preferred_numbers = position_ranges.get(position_code, list(range(1, 36)))

        for number in preferred_numbers:
            if number not in existing_numbers:
                return number

        # If all preferred numbers taken, use any available number
        for number in range(1, 100):
            if number not in existing_numbers:
                return number

        # Fallback
        return 99

    def generate_player_id(
        self,
        first_name: str,
        last_name: str,
        position: str,
        team_id: str,
        existing_ids: set[str] | None = None,
    ) -> str:
        """Generate a football-contextual player ID with jersey number and position."""
        if not first_name or not last_name or not position:
            return "99UNK1"

        # Normalize names
        first_norm = first_name.strip()
        last_norm = last_name.strip()

        # Get existing jersey numbers for this team
        existing_numbers = set()
        id_set = existing_ids or self.used_player_ids

        for player_id in id_set:
            if player_id.startswith(team_id):
                # Extract jersey number from existing player IDs
                match = re.match(r"(\d{1,2})", player_id)
                if match:
                    existing_numbers.add(int(match.group(1)))

        # Get position code
        position_code = self._get_position_code(position)

        # Get jersey number
        jersey_number = self._get_jersey_number(position, existing_numbers)

        # Generate initials
        initials = f"{first_norm[0].upper()}{last_norm[0].upper()}"

        # Create base ID: JerseyNumber + PositionCode + Initials
        base_id = f"{jersey_number:02d}{position_code}{initials}"

        # Resolve collision
        final_id = self._resolve_collision(base_id, id_set)

        # Store mapping
        player_key = f"{first_norm.lower()} {last_norm.lower()}"
        self.player_mappings[player_key] = final_id
        if existing_ids is not None:
            existing_ids.add(final_id)
        else:
            self.used_player_ids.add(final_id)

        logger.info(
            f"Generated football player ID '{final_id}' for {first_name} {last_name} ({position})"
        )
        return final_id

    def generate_match_id(
        self,
        home_team: str,
        away_team: str,
        match_date: str,
        competition: str = "FRIENDLY",
        match_time: str = "",
    ) -> str:
        """Generate a simple match ID with date and team information."""
        # Get team IDs
        home_id = self.generate_team_id(home_team)
        away_id = self.generate_team_id(away_team)

        # Parse date to get day and month
        try:
            parsed_date = datetime.strptime(match_date, "%Y-%m-%d")
            day = parsed_date.day
            month = parsed_date.month

            # Create simple match ID: M{DD}{MM}{HOME}{AWAY}
            base_id = f"M{day:02d}{month:02d}{home_id}{away_id}"

            # Resolve collision by adding number suffix if needed
            final_id = self._resolve_collision(base_id, self.used_match_ids)
            self.used_match_ids.add(final_id)

            logger.info(
                f"Generated simple match ID '{final_id}' for {home_team} vs {away_team} on {match_date}"
            )
            return final_id

        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            # Fallback to sequential numbering with team info
            match_number = len(self.used_match_ids) + 1
            final_id = f"M{match_number}{home_id}{away_id}"
            self.used_match_ids.add(final_id)
            logger.info(f"Generated fallback match ID '{final_id}' for {home_team} vs {away_team}")
            return final_id

    def _get_competition_prefix(self, competition: str) -> str:
        """Get competition prefix from competition string."""
        competition_lower = competition.lower()

        if "premier" in competition_lower or "pl" in competition_lower:
            return Competition.PREMIER_LEAGUE.value
        elif "fa cup" in competition_lower or "fa" in competition_lower:
            return Competition.FA_CUP.value
        elif "efl cup" in competition_lower or "carabao" in competition_lower:
            return Competition.EFL_CUP.value
        elif "championship" in competition_lower:
            return Competition.EFL_CHAMPIONSHIP.value
        elif "league one" in competition_lower:
            return Competition.EFL_LEAGUE_ONE.value
        elif "league two" in competition_lower:
            return Competition.EFL_LEAGUE_TWO.value
        elif "sunday" in competition_lower:
            return Competition.SUNDAY_LEAGUE.value
        else:
            return Competition.FRIENDLY.value

    def _parse_date(self, date_str: str) -> str:
        """Parse date into YYYY-MM-DD format."""
        try:
            # Clean the date string
            cleaned_date = re.sub(
                r"\b(Union[against, vs]|Union[v, on]|Union[at, home]|away)\b",
                "",
                date_str,
                flags=re.IGNORECASE,
            ).strip()

            # Try different date formats
            date_formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%d-%m-%Y",
                "%d/%m/%y",
                "%d-%m-%y",
                "%B %d, %Y",
                "%d %B %Y",
                "%B %d %Y",
                "%d %B, %Y",
            ]

            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(cleaned_date, fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            # If no format works, try to extract from text
            year_match = re.search(r"\b(20\d{2})\b", cleaned_date)
            month_match = re.search(
                r"\b(Union[jan, feb]|Union[mar, apr]|Union[may, jun]|Union[jul, aug]|Union[sep, oct]|Union[nov, dec])\b",
                cleaned_date,
                re.IGNORECASE,
            )
            day_match = re.search(r"\b(\d{1,2})\b", cleaned_date)

            if year_match and month_match and day_match:
                year = year_match.group(1)
                month_map = {
                    "jan": "01",
                    "feb": "02",
                    "mar": "03",
                    "apr": "04",
                    "may": "05",
                    "jun": "06",
                    "jul": "07",
                    "aug": "08",
                    "sep": "09",
                    "oct": "10",
                    "nov": "11",
                    "dec": "12",
                }
                month = month_map.get(month_match.group(1).lower(), "01")
                day = day_match.group(1).zfill(2)
                return f"{year}-{month}-{day}"

            return datetime.now().strftime("%Y-%m-%d")  # Default to today

        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            return datetime.now().strftime("%Y-%m-%d")  # Default to today

    def _resolve_collision(self, base_id: str, existing_ids: set[str]) -> str:
        """Resolve ID collision by adding a number suffix."""
        if base_id not in existing_ids:
            return base_id

        # Try adding numbers 1-99
        for i in range(1, 100):
            candidate = f"{base_id}{i}"
            if candidate not in existing_ids:
                return candidate

        # If all numbers are taken, use hash-based suffix
        hash_suffix = hashlib.md5(base_id.encode()).hexdigest()[:2].upper()
        return f"{base_id}{hash_suffix}"

    def get_team_mappings(self) -> dict[str, str]:
        """Get all team name to ID mappings."""
        return self.team_mappings.copy()

    def get_player_mappings(self) -> dict[str, str]:
        """Get all player name to ID mappings."""
        return self.player_mappings.copy()

    def clear_all(self):
        """Clear all stored IDs (useful for testing)."""
        self.used_team_ids.clear()
        self.used_player_ids.clear()
        self.used_match_ids.clear()
        self.team_mappings.clear()
        self.player_mappings.clear()
        logger.info("Cleared all football ID generator memory")


# Global instance
football_id_generator = FootballIDGenerator()


# Convenience functions for backward compatibility
def generate_football_team_id(team_name: str, league_info: str = "") -> str:
    """Generate a football-contextual team ID."""
    return football_id_generator.generate_team_id(team_name, league_info)


def generate_football_player_id(
    first_name: str,
    last_name: str,
    position: str,
    team_id: str,
    existing_ids: set[str] | None = None,
) -> str:
    """Generate a football-contextual player ID."""
    return football_id_generator.generate_player_id(
        first_name, last_name, position, team_id, existing_ids
    )


def generate_football_match_id(
    home_team: str,
    away_team: str,
    match_date: str,
    competition: str = "FRIENDLY",
    match_time: str = "",
) -> str:
    """Generate a football-contextual match ID."""
    return football_id_generator.generate_match_id(
        home_team, away_team, match_date, competition, match_time
    )
