"""
Match ID Generator for KICKAI

This module provides human-readable match ID generation functionality
to avoid circular import issues.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Set

logger = logging.getLogger(__name__)


class MatchIDGenerator:
    """Generates human-readable match IDs with dynamic, stable team abbreviations."""
    
    def __init__(self):
        # Dynamic abbreviation memory for this session - starts empty
        self.team_abbreviations: Dict[str, str] = {}
        self.generated_ids: Set[str] = set()
        # Common team name variations mapping
        self.team_variations: Dict[str, str] = {}
    
    def get_team_abbreviation(self, team_name: str) -> str:
        """Get or generate a stable abbreviation for a team name."""
        if not team_name:
            return 'UNK'
        
        normalized = team_name.lower().strip()
        if normalized in ['unknown team', 'unknown', 'tbd', 'tba']:
            return 'UNK'
        
        # Check if already known
        if normalized in self.team_abbreviations:
            return self.team_abbreviations[normalized]
        
        # Generate abbreviation
        abbr = self._generate_abbreviation(normalized)
        
        # Store the abbreviation for future use
        self.team_abbreviations[normalized] = abbr
        
        # Also store common variations of this team name
        self._store_team_variations(normalized, abbr)
        
        logger.info(f"Generated abbreviation '{abbr}' for team '{team_name}' (normalized: '{normalized}')")
        return abbr
    
    def _generate_abbreviation(self, normalized: str) -> str:
        """Generate a 3-character abbreviation for a team name."""
        # Remove common suffixes and prefixes
        cleaned = self._clean_team_name(normalized)
        
        # Use initials if multiple words
        words = cleaned.split()
        if len(words) >= 2:
            # Take first letter of each word
            abbr = ''.join(word[0].upper() for word in words if word)
            if len(abbr) >= 2:
                return abbr[:3]  # Limit to 3 characters
        
        # For single words, take first 3 letters
        return cleaned[:3].upper()
    
    def _clean_team_name(self, team_name: str) -> str:
        """Clean team name by removing common suffixes and prefixes."""
        # Remove common football suffixes
        suffixes_to_remove = [
            r'\s+fc\b', r'\s+football\s+club\b', r'\s+united\b', r'\s+city\b',
            r'\s+town\b', r'\s+athletic\b', r'\s+athletics\b', r'\s+rovers\b',
            r'\s+wanderers\b', r'\s+hotspur\b', r'\s+albion\b', r'\s+county\b'
        ]
        
        cleaned = team_name
        for suffix in suffixes_to_remove:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        # Remove common prefixes
        prefixes_to_remove = [
            r'^the\s+', r'^fc\s+', r'^football\s+club\s+'
        ]
        
        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _store_team_variations(self, normalized: str, abbr: str):
        """Store common variations of team names to map to the same abbreviation."""
        # Generate common variations
        variations = []
        
        # Add with/without "FC"
        if not normalized.endswith(' fc'):
            variations.append(f"{normalized} fc")
        else:
            variations.append(normalized.replace(' fc', ''))
        
        # Add with/without "Football Club"
        if 'football club' not in normalized:
            variations.append(f"{normalized} football club")
        else:
            variations.append(normalized.replace(' football club', ''))
        
        # Add with/without "The"
        if not normalized.startswith('the '):
            variations.append(f"the {normalized}")
        else:
            variations.append(normalized.replace('the ', ''))
        
        # Store variations
        for variation in variations:
            if variation != normalized:
                self.team_variations[variation] = normalized
        
        logger.debug(f"Stored variations for '{normalized}': {variations}")
    
    def get_known_teams(self) -> Dict[str, str]:
        """Get all known team abbreviations for debugging/monitoring."""
        return self.team_abbreviations.copy()
    
    def clear_memory(self):
        """Clear all stored abbreviations (useful for testing)."""
        self.team_abbreviations.clear()
        self.team_variations.clear()
        self.generated_ids.clear()
        logger.info("Cleared MatchIDGenerator memory")
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string and return DDMM format."""
        try:
            # Remove common words
            cleaned = re.sub(r'\b(against|vs|v|on|at|home|away)\b', '', date_str, flags=re.IGNORECASE).strip()
            
            # Try different date formats
            date_formats = [
                '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
                '%B %d, %Y', '%d %B %Y', '%B %d %Y', '%d %B, %Y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(cleaned, fmt)
                    return parsed_date.strftime('%d%m')
                except ValueError:
                    continue
            
            # If no format works, try to extract day and month from text
            day_match = re.search(r'\b(\d{1,2})\b', cleaned)
            month_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', cleaned, re.IGNORECASE)
            
            if day_match and month_match:
                day = day_match.group(1).zfill(2)
                month_map = {
                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                }
                month = month_map[month_match.group(1).lower()]
                return f"{day}{month}"
            
            return '0101'  # Default fallback
            
        except Exception as e:
            logger.error("Date parsing error", error=e)
            return '0101'  # Default fallback
    
    def generate_match_id(self, opponent: str, date: str, venue: str = '') -> str:
        """Generate a human-readable match ID."""
        home_abbr = 'BPH'
        away_abbr = self.get_team_abbreviation(opponent)
        date_code = self.parse_date_readable(date)
        base_id = f"{home_abbr}{away_abbr}-{date_code}"
        final_id = self._resolve_conflicts(base_id)
        self.generated_ids.add(final_id)
        return final_id
    
    def parse_date_readable(self, date_str: str) -> str:
        """Parse date string and return DDMMM format (e.g., 01JUL)."""
        try:
            # Remove common words
            cleaned = re.sub(r'\b(against|vs|v|on|at|home|away)\b', '', date_str, flags=re.IGNORECASE).strip()
            
            # Try different date formats
            date_formats = [
                '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
                '%B %d, %Y', '%d %B %Y', '%B %d %Y', '%d %B, %Y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(cleaned, fmt)
                    return parsed_date.strftime('%d%b').upper()
                except ValueError:
                    continue
            
            # If no format works, try to extract day and month from text
            day_match = re.search(r'\b(\d{1,2})\b', cleaned)
            month_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', cleaned, re.IGNORECASE)
            
            if day_match and month_match:
                day = day_match.group(1).zfill(2)
                month = month_match.group(1).upper()[:3]
                return f"{day}{month}"
            
            return '01JAN'  # Default fallback
            
        except Exception as e:
            logger.error("Date parsing error", error=e)
            return '01JAN'  # Default fallback
    
    def _resolve_conflicts(self, base_id: str) -> str:
        """Resolve ID conflicts by adding numbers."""
        if base_id not in self.generated_ids:
            return base_id
        for i in range(1, 10):
            candidate = f"{base_id}{i}"
            if candidate not in self.generated_ids:
                return candidate
        return base_id


# Global instance
match_id_generator = MatchIDGenerator() 