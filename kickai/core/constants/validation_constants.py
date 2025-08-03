"""
Validation constants for KICKAI.

This module contains constants related to data validation, including
field lengths, patterns, and validation rules.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern


@dataclass(frozen=True)
class ValidationConstants:
    """Data validation configuration constants."""
    
    # String Length Limits
    MIN_NAME_LENGTH: int = 2
    MAX_NAME_LENGTH: int = 100
    MIN_USERNAME_LENGTH: int = 3
    MAX_USERNAME_LENGTH: int = 50
    MIN_TEAM_NAME_LENGTH: int = 2
    MAX_TEAM_NAME_LENGTH: int = 100
    
    # Phone Number Validation
    MIN_PHONE_LENGTH: int = 10
    MAX_PHONE_LENGTH: int = 15
    UK_PHONE_REGEX: str = r"^(\+44|0)[0-9]{10}$"
    INTERNATIONAL_PHONE_REGEX: str = r"^\+?[1-9]\d{1,14}$"
    
    # Player Position Validation
    VALID_PLAYER_POSITIONS: List[str] = field(default_factory=lambda: [
        "goalkeeper", "defender", "midfielder", "forward", "winger", "striker", "utility", "any"
    ])
    
    # Team Member Role Validation
    VALID_TEAM_MEMBER_ROLES: List[str] = field(default_factory=lambda: [
        "coach", "manager", "assistant", "coordinator", "volunteer", "admin", "member"
    ])
    
    # Message Validation
    MIN_MESSAGE_LENGTH: int = 1
    MAX_MESSAGE_LENGTH: int = 4096
    MAX_COMMAND_LENGTH: int = 100
    
    # ID Validation
    MIN_ID_LENGTH: int = 1
    MAX_ID_LENGTH: int = 50
    ID_REGEX: str = r"^[a-zA-Z0-9_-]+$"
    
    # Team ID Validation
    MIN_TEAM_ID_LENGTH: int = 2
    MAX_TEAM_ID_LENGTH: int = 20
    TEAM_ID_REGEX: str = r"^[a-zA-Z0-9_-]+$"
    
    # User ID Validation (Telegram user IDs are numeric)
    USER_ID_REGEX: str = r"^[0-9]+$"
    MIN_USER_ID_VALUE: int = 1
    MAX_USER_ID_VALUE: int = 2147483647  # 32-bit signed integer max
    
    # Chat ID Validation (can be negative for group chats)
    CHAT_ID_REGEX: str = r"^-?[0-9]+$"
    MIN_CHAT_ID_VALUE: int = -2147483648  # 32-bit signed integer min
    MAX_CHAT_ID_VALUE: int = 2147483647   # 32-bit signed integer max
    
    # File Validation
    ALLOWED_IMAGE_EXTENSIONS: List[str] = field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".gif", ".webp"])
    ALLOWED_DOCUMENT_EXTENSIONS: List[str] = field(default_factory=lambda: [".pdf", ".doc", ".docx", ".txt", ".csv"])
    MAX_FILENAME_LENGTH: int = 255
    
    # Email Validation (optional)
    EMAIL_REGEX: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    MAX_EMAIL_LENGTH: int = 320
    
    # URL Validation
    URL_REGEX: str = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    MAX_URL_LENGTH: int = 2048
    
    # Date/Time Validation
    DATE_REGEX: str = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"  # YYYY-MM-DD
    TIME_REGEX: str = r"^[0-9]{2}:[0-9]{2}$"           # HH:MM
    DATETIME_REGEX: str = r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$"  # YYYY-MM-DD HH:MM
    
    # Numeric Validation
    MIN_AGE: int = 16
    MAX_AGE: int = 99
    MIN_JERSEY_NUMBER: int = 1
    MAX_JERSEY_NUMBER: int = 99
    
    # Match/Event Validation
    MIN_MATCH_DURATION_MINUTES: int = 45
    MAX_MATCH_DURATION_MINUTES: int = 180
    MAX_SCORE_VALUE: int = 99
    
    @classmethod
    def get_compiled_regex(cls, pattern_name: str) -> Pattern[str]:
        """
        Get compiled regex pattern by name.
        
        Args:
            pattern_name: Name of the regex pattern
            
        Returns:
            Compiled regex pattern
        """
        patterns = {
            "uk_phone": cls.UK_PHONE_REGEX,
            "international_phone": cls.INTERNATIONAL_PHONE_REGEX,
            "id": cls.ID_REGEX,
            "team_id": cls.TEAM_ID_REGEX,
            "user_id": cls.USER_ID_REGEX,
            "chat_id": cls.CHAT_ID_REGEX,
            "email": cls.EMAIL_REGEX,
            "url": cls.URL_REGEX,
            "date": cls.DATE_REGEX,
            "time": cls.TIME_REGEX,
            "datetime": cls.DATETIME_REGEX,
        }
        
        pattern = patterns.get(pattern_name)
        if pattern is None:
            raise ValueError(f"Unknown pattern name: {pattern_name}")
        
        return re.compile(pattern)
    
    @classmethod
    def validate_player_position(cls, position: str) -> bool:
        """
        Validate player position.
        
        Args:
            position: Position to validate
            
        Returns:
            True if valid position
        """
        return position.lower() in cls.VALID_PLAYER_POSITIONS
    
    @classmethod
    def validate_team_member_role(cls, role: str) -> bool:
        """
        Validate team member role.
        
        Args:
            role: Role to validate
            
        Returns:
            True if valid role
        """
        return role.lower() in cls.VALID_TEAM_MEMBER_ROLES
    
    @classmethod
    def get_position_suggestions(cls, partial: str) -> List[str]:
        """
        Get position suggestions for partial input.
        
        Args:
            partial: Partial position input
            
        Returns:
            List of matching positions
        """
        partial_lower = partial.lower()
        return [
            pos for pos in cls.VALID_PLAYER_POSITIONS
            if pos.startswith(partial_lower)
        ]
    
    @classmethod
    def get_role_suggestions(cls, partial: str) -> List[str]:
        """
        Get role suggestions for partial input.
        
        Args:
            partial: Partial role input
            
        Returns:
            List of matching roles
        """
        partial_lower = partial.lower()
        return [
            role for role in cls.VALID_TEAM_MEMBER_ROLES
            if role.startswith(partial_lower)
        ]
    
    @classmethod
    def get_validation_error_message(cls, field: str, value: str, error_type: str) -> str:
        """
        Get user-friendly validation error message.
        
        Args:
            field: Field name that failed validation
            value: Value that failed validation
            error_type: Type of validation error
            
        Returns:
            User-friendly error message
        """
        messages = {
            "too_short": f"{field} is too short. Minimum length is {cls._get_min_length(field)} characters.",
            "too_long": f"{field} is too long. Maximum length is {cls._get_max_length(field)} characters.",
            "invalid_format": f"{field} has invalid format. Please check the format and try again.",
            "invalid_position": f"Invalid position. Valid positions are: {', '.join(cls.VALID_PLAYER_POSITIONS)}",
            "invalid_role": f"Invalid role. Valid roles are: {', '.join(cls.VALID_TEAM_MEMBER_ROLES)}",
            "invalid_phone": f"Invalid phone number. Please use UK format: +44XXXXXXXXXX or 0XXXXXXXXXX",
            "required": f"{field} is required and cannot be empty.",
        }
        
        return messages.get(error_type, f"{field} validation failed.")
    
    @classmethod
    def _get_min_length(cls, field: str) -> int:
        """Get minimum length for a field."""
        min_lengths = {
            "name": cls.MIN_NAME_LENGTH,
            "username": cls.MIN_USERNAME_LENGTH,
            "team_name": cls.MIN_TEAM_NAME_LENGTH,
            "phone": cls.MIN_PHONE_LENGTH,
            "message": cls.MIN_MESSAGE_LENGTH,
            "id": cls.MIN_ID_LENGTH,
            "team_id": cls.MIN_TEAM_ID_LENGTH,
        }
        return min_lengths.get(field, 1)
    
    @classmethod
    def _get_max_length(cls, field: str) -> int:
        """Get maximum length for a field."""
        max_lengths = {
            "name": cls.MAX_NAME_LENGTH,
            "username": cls.MAX_USERNAME_LENGTH,
            "team_name": cls.MAX_TEAM_NAME_LENGTH,
            "phone": cls.MAX_PHONE_LENGTH,
            "message": cls.MAX_MESSAGE_LENGTH,
            "id": cls.MAX_ID_LENGTH,
            "team_id": cls.MAX_TEAM_ID_LENGTH,
        }
        return max_lengths.get(field, 255)