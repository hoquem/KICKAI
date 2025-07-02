"""
Human-Readable ID Generator for KICKAI

This module provides dynamic, stable, and human-readable ID generation for:
- Team IDs (e.g., BPH for BP Hatters, LIV for Liverpool)
- Player IDs (e.g., JS1 for John Smith, MJ2 for Mike Johnson)
- Match IDs (e.g., BPHLIV0107 for BP Hatters vs Liverpool on 01/07)

Features:
- Dynamic generation based on names/descriptions
- Collision detection and resolution
- Stable IDs (same input = same ID)
- Human-readable format
- No predefined lists required
"""

import re
import logging
import hashlib
from datetime import datetime
from typing import Dict, Set, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class IDGenerator:
    """Base ID generator with common functionality."""
    
    def __post_init__(self):
        self.used_ids: Set[str] = set()
        self.name_mappings: Dict[str, str] = {}
    
    def _normalize_name(self, name: str) -> str:
        """Normalize a name for consistent processing."""
        if not name:
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', name.lower().strip())
        
        # Remove common words that don't add meaning
        common_words = ['the', 'fc', 'football', 'club', 'united', 'city', 'town', 'athletic', 'athletics']
        words = normalized.split()
        filtered_words = [word for word in words if word not in common_words]
        
        return ' '.join(filtered_words)
    
    def _generate_base_id(self, name: str, max_length: int = 3) -> str:
        """Generate a base ID from a name."""
        normalized = self._normalize_name(name)
        
        if not normalized:
            return "UNK"
        
        # Split into words
        words = normalized.split()
        
        if len(words) >= 2:
            # Use first letter of each word
            base_id = ''.join(word[0].upper() for word in words[:max_length])
        else:
            # For single words, use first few letters
            base_id = normalized[:max_length].upper()
        
        return base_id
    
    def _resolve_collision(self, base_id: str, existing_ids: Set[str]) -> str:
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


class TeamIDGenerator(IDGenerator):
    """Generates human-readable team IDs."""
    
    def generate_team_id(self, team_name: str) -> str:
        """Generate a human-readable team ID for a team name."""
        normalized = self._normalize_name(team_name)
        
        # Check if we already have a mapping for this team
        if normalized in self.name_mappings:
            return self.name_mappings[normalized]
        
        # Generate base ID (3 characters)
        base_id = self._generate_base_id(team_name, max_length=3)
        
        # Resolve any collisions
        final_id = self._resolve_collision(base_id, self.used_ids)
        
        # Store the mapping and mark as used
        self.name_mappings[normalized] = final_id
        self.used_ids.add(final_id)
        
        logger.info(f"Generated team ID '{final_id}' for '{team_name}' (normalized: '{normalized}')")
        return final_id
    
    def get_known_teams(self) -> Dict[str, str]:
        """Get all known team name to ID mappings."""
        return self.name_mappings.copy()


class PlayerIDGenerator(IDGenerator):
    """Generates human-readable player IDs."""
    
    def generate_player_id(self, first_name: str, last_name: str, existing_ids: Optional[Set[str]] = None) -> str:
        """Generate a human-readable player ID."""
        if not first_name or not last_name:
            return "UNK1"
        
        # Normalize names
        first_norm = first_name.strip().lower()
        last_norm = last_name.strip().lower()
        
        # Create a unique key for this player
        player_key = f"{first_norm} {last_norm}"
        
        # Check if we already have a mapping
        if player_key in self.name_mappings:
            return self.name_mappings[player_key]
        
        # Generate base ID: first letter of first name + first letter of last name
        base_id = f"{first_name[0].upper()}{last_name[0].upper()}"
        
        # Use existing IDs if provided, otherwise use our internal set
        id_set = existing_ids or self.used_ids
        
        # Resolve collision
        final_id = self._resolve_collision(base_id, id_set)
        
        # Store mapping
        self.name_mappings[player_key] = final_id
        if existing_ids is not None:
            existing_ids.add(final_id)
        else:
            self.used_ids.add(final_id)
        
        logger.info(f"Generated player ID '{final_id}' for '{first_name} {last_name}'")
        return final_id


class MatchIDGenerator(IDGenerator):
    """Generates human-readable match IDs."""
    
    def __init__(self, team_id_generator: TeamIDGenerator):
        super().__init__()
        self.team_id_generator = team_id_generator
    
    def generate_match_id(self, home_team: str, away_team: str, match_date: str, 
                         match_time: str = "") -> str:
        """Generate a human-readable match ID."""
        # Get team IDs
        home_id = self.team_id_generator.generate_team_id(home_team)
        away_id = self.team_id_generator.generate_team_id(away_team)
        
        # Parse date and time
        date_code = self._parse_date_time(match_date, match_time)
        
        # Create base match ID
        base_id = f"{home_id}{away_id}{date_code}"
        
        # Resolve collision
        final_id = self._resolve_collision(base_id, self.used_ids)
        self.used_ids.add(final_id)
        
        logger.info(f"Generated match ID '{final_id}' for {home_team} vs {away_team} on {match_date}")
        return final_id
    
    def _parse_date_time(self, date_str: str, time_str: str = "") -> str:
        """Parse date and time into a compact format (DDMM)."""
        try:
            # Clean the date string
            cleaned_date = re.sub(r'\b(against|vs|v|on|at|home|away)\b', '', date_str, flags=re.IGNORECASE).strip()
            
            # Try different date formats
            date_formats = [
                '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
                '%B %d, %Y', '%d %B %Y', '%B %d %Y', '%d %B, %Y',
                '%d/%m/%Y', '%d-%m-%Y'  # Common UK formats
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(cleaned_date, fmt)
                    return parsed_date.strftime('%d%m')  # DDMM format
                except ValueError:
                    continue
            
            # If no format works, try to extract day and month from text
            day_match = re.search(r'\b(\d{1,2})\b', cleaned_date)
            month_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', cleaned_date, re.IGNORECASE)
            
            if day_match and month_match:
                day = day_match.group(1).zfill(2)
                month_map = {
                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                }
                month = month_map.get(month_match.group(1).lower(), '01')
                return f"{day}{month}"
            
            return '0101'  # Default fallback
            
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            return '0101'  # Default fallback


class IDManager:
    """Main ID manager that coordinates all ID generators."""
    
    def __init__(self):
        self.team_generator = TeamIDGenerator()
        self.player_generator = PlayerIDGenerator()
        self.match_generator = MatchIDGenerator(self.team_generator)
        
        # Load existing IDs from storage (to be implemented)
        self._load_existing_ids()
    
    def _load_existing_ids(self):
        """Load existing IDs from storage to avoid collisions."""
        try:
            # This would load from your database/storage
            # For now, we'll start with empty sets
            logger.info("ID Manager initialized with empty ID sets")
        except Exception as e:
            logger.warning(f"Failed to load existing IDs: {e}")
    
    def generate_team_id(self, team_name: str) -> str:
        """Generate a team ID."""
        return self.team_generator.generate_team_id(team_name)
    
    def generate_player_id(self, first_name: str, last_name: str, existing_ids: Optional[Set[str]] = None) -> str:
        """Generate a player ID."""
        return self.player_generator.generate_player_id(first_name, last_name, existing_ids)
    
    def generate_match_id(self, home_team: str, away_team: str, match_date: str, match_time: str = "") -> str:
        """Generate a match ID."""
        return self.match_generator.generate_match_id(home_team, away_team, match_date, match_time)
    
    def get_known_teams(self) -> Dict[str, str]:
        """Get all known team mappings."""
        return self.team_generator.get_known_teams()
    
    def clear_all(self):
        """Clear all stored IDs (useful for testing)."""
        self.team_generator.used_ids.clear()
        self.team_generator.name_mappings.clear()
        self.player_generator.used_ids.clear()
        self.player_generator.name_mappings.clear()
        self.match_generator.used_ids.clear()
        logger.info("Cleared all ID generator memory")


# Global instance
id_manager = IDManager()


# Convenience functions for backward compatibility
def generate_team_id(team_name: str) -> str:
    """Generate a team ID."""
    return id_manager.generate_team_id(team_name)


def generate_player_id(first_name: str, last_name: str, existing_ids: Optional[Set[str]] = None) -> str:
    """Generate a player ID."""
    return id_manager.generate_player_id(first_name, last_name, existing_ids)


def generate_match_id(home_team: str, away_team: str, match_date: str, match_time: str = "") -> str:
    """Generate a match ID."""
    return id_manager.generate_match_id(home_team, away_team, match_date, match_time)


# Example usage and testing
if __name__ == "__main__":
    # Test team ID generation
    print("🧪 Testing ID Generation")
    print("=" * 50)
    
    teams = [
        "BP Hatters FC",
        "Liverpool",
        "Manchester United",
        "Arsenal",
        "Chelsea",
        "Tottenham Hotspur",
        "Manchester City",
        "Everton"
    ]
    
    print("Team IDs:")
    for team in teams:
        team_id = generate_team_id(team)
        print(f"  {team} -> {team_id}")
    
    print("\nPlayer IDs:")
    players = [
        ("John", "Smith"),
        ("Mike", "Johnson"),
        ("David", "Williams"),
        ("James", "Brown"),
        ("Robert", "Jones")
    ]
    
    existing_player_ids = set()
    for first, last in players:
        player_id = generate_player_id(first, last, existing_player_ids)
        print(f"  {first} {last} -> {player_id}")
    
    print("\nMatch IDs:")
    matches = [
        ("BP Hatters FC", "Liverpool", "01/07/2025", "10:30"),
        ("Manchester United", "Arsenal", "15/07/2025", "14:00"),
        ("Chelsea", "Tottenham Hotspur", "22/07/2025", "16:30")
    ]
    
    for home, away, date, time in matches:
        match_id = generate_match_id(home, away, date, time)
        print(f"  {home} vs {away} on {date} @ {time} -> {match_id}")
    
    print(f"\nKnown teams: {id_manager.get_known_teams()}") 