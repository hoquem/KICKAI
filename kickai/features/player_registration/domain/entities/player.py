from typing import Optional, Set
#!/usr/bin/env python3
"""
Player Entity

This module defines the Player entity for the player registration domain.
Players represent football players, separate from Team Members who are administrators.
A person can be both a Player and a Team Member, linked by user_id.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from kickai.core.enums import PlayerPosition
from kickai.utils.user_id_generator import generate_user_id


class PreferredFoot(Enum):
    """Player preferred foot enumeration."""

    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class OnboardingStatus(Enum):
    """Player onboarding status enumeration."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class Player:
    """
    Player entity representing a football player in a team.

    Players are football-specific entities with position, skills, and match-related data.
    This is separate from Team Members who are administrators/managers.
    A person can be both a Player and a Team Member, linked by user_id.
    """

    # Core identification fields
    user_id: str = ""  # Generated from telegram_id using generate_user_id()
    team_id: str = ""
    telegram_id: Optional[int] = None  # Native Telegram integer user ID
    player_id: Optional[str] = None  # Team-specific player identifier (e.g., "team_id_MH_001")

    # Personal information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None

    # Football-specific information
    position: Optional[str] = None  # e.g., "Midfielder", "Forward"
    preferred_foot: Optional[str] = None  # "left", "right", "both"
    jersey_number: Optional[str] = None

    # Contact and personal information
    phone_number: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_notes: Optional[str] = None

    # Status and approval
    status: str = "pending"  # pending, approved, rejected, active, inactive

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Metadata
    source: Optional[str] = None  # e.g., "telegram_sync", "manual_entry", "registration_form"
    sync_version: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        self._validate()
        self._set_defaults()

    def _validate(self):
        """Validate player data."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")

        # Only validate user_id if it's provided (allow empty for database retrieval)
        if self.user_id and not self.user_id.startswith("user_"):
            raise ValueError(f"Invalid user_id format: {self.user_id}. Must start with 'user_'")

        # Validate status
        valid_statuses = ["pending", "approved", "rejected", "active", "inactive"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        # Validate position if provided
        if self.position:
            valid_positions = [pos.value for pos in PlayerPosition]
            if self.position.lower() not in valid_positions:
                raise ValueError(
                    f"Invalid position: {self.position}. Must be one of {valid_positions}"
                )

        # Validate preferred foot if provided
        if self.preferred_foot:
            valid_feet = [foot.value for foot in PreferredFoot]
            if self.preferred_foot.lower() not in valid_feet:
                raise ValueError(
                    f"Invalid preferred foot: {self.preferred_foot}. Must be one of {valid_feet}"
                )

    def _set_defaults(self):
        """Set default values if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.source is None:
            self.source = "manual_entry"
        if self.sync_version is None:
            self.sync_version = "1.0"

    @classmethod
    def create_from_telegram(
        cls,
        team_id: str,
        telegram_id: int,
        first_name: str = None,
        last_name: str = None,
        username: str = None,
        phone_number: str = None,
    ) -> "Player":
        """
        Create a Player from Telegram user data.

        Args:
            team_id: The team ID
            telegram_id: The Telegram user ID
            first_name: Telegram first name
            last_name: Telegram last name
            username: Telegram username
            phone_number: Phone number if available

        Returns:
            A new Player instance
        """
        user_id = generate_user_id(telegram_id)

        # Build full name
        full_name = ""
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name
        elif last_name:
            full_name = last_name
        else:
            full_name = f"User {telegram_id}"

        return cls(
            user_id=user_id,
            team_id=team_id,
            telegram_id=telegram_id,  # Keep as integer
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            username=username,
            phone_number=phone_number,
            source="telegram_sync",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "team_id": self.team_id,
            "telegram_id": self.telegram_id,
            "player_id": self.player_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "username": self.username,
            "position": self.position,
            "preferred_foot": self.preferred_foot,
            "jersey_number": self.jersey_number,
            "phone_number": self.phone_number,
            "email": self.email,
            "date_of_birth": self.date_of_birth,
            "emergency_contact": self.emergency_contact,
            "medical_notes": self.medical_notes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source": self.source,
            "sync_version": self.sync_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Create from dictionary."""
        # Ensure telegram_id is integer if provided
        telegram_id = data.get("telegram_id")
        if telegram_id is not None:
            telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id

        return cls(
            user_id=data.get("user_id", ""),
            team_id=data.get("team_id", ""),
            telegram_id=telegram_id,
            player_id=data.get("player_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            full_name=data.get("full_name"),
            username=data.get("username"),
            position=data.get("position"),
            preferred_foot=data.get("preferred_foot"),
            jersey_number=data.get("jersey_number"),
            phone_number=data.get("phone_number"),
            email=data.get("email"),
            date_of_birth=data.get("date_of_birth"),
            emergency_contact=data.get("emergency_contact"),
            medical_notes=data.get("medical_notes"),
            status=data.get("status", "pending"),
            created_at=cls._parse_datetime(data.get("created_at")),
            updated_at=cls._parse_datetime(data.get("updated_at")),
            source=data.get("source"),
            sync_version=data.get("sync_version"),
        )

    @classmethod
    def from_database_dict(cls, data: dict) -> "Player":
        """Create from database dictionary with relaxed validation for retrieval."""
        # Create player without triggering validation
        player = cls.__new__(cls)

        # Set attributes directly
        player.user_id = data.get("user_id", "")
        player.team_id = data.get("team_id", "")
        # Ensure telegram_id is integer if provided
        telegram_id = data.get("telegram_id")
        if telegram_id is not None:
            telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id
        player.telegram_id = telegram_id
        player.player_id = data.get("player_id")
        player.first_name = data.get("first_name")
        player.last_name = data.get("last_name")
        player.full_name = data.get("full_name")
        player.username = data.get("username")
        player.position = data.get("position")
        player.preferred_foot = data.get("preferred_foot")
        player.jersey_number = data.get("jersey_number")
        player.phone_number = data.get("phone_number")
        player.email = data.get("email")
        player.date_of_birth = data.get("date_of_birth")
        player.emergency_contact = data.get("emergency_contact")
        player.medical_notes = data.get("medical_notes")
        player.status = data.get("status", "pending")
        player.source = data.get("source")
        player.sync_version = data.get("sync_version")

        # Parse datetime fields
        if data.get("created_at"):
            try:
                player.created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except ValueError:
                player.created_at = None
        else:
            player.created_at = None

        if data.get("updated_at"):
            try:
                player.updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            except ValueError:
                player.updated_at = None
        else:
            player.updated_at = None

        return player

    @staticmethod
    def _parse_datetime(dt_value) -> Optional[datetime]:
        """Parse datetime value handling both string and datetime objects."""
        if not dt_value:
            return None
        
        # If it's already a datetime object (from Firestore), return it
        if isinstance(dt_value, datetime):
            return dt_value
        
        # If it's a string, parse it
        if isinstance(dt_value, str):
            try:
                return datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
            except ValueError:
                return None
        
        return None

    def approve(self):
        """Approve the player."""
        self.status = "approved"
        self.updated_at = datetime.utcnow()

    def reject(self):
        """Reject the player."""
        self.status = "rejected"
        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate the player."""
        self.status = "active"
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate the player."""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()

    def is_approved(self) -> bool:
        """Check if player is approved."""
        return self.status == "approved"

    def is_active(self) -> bool:
        """Check if player is active."""
        return self.status == "active"

    def is_pending(self) -> bool:
        """Check if player is pending."""
        return self.status == "pending"

    def get_display_name(self) -> str:
        """Get display name for the player."""
        if self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        elif self.telegram_id:
            return f"User {self.telegram_id}"
        else:
            return f"User {self.user_id}"

    def get_position_display(self) -> str:
        """Get formatted position display."""
        if self.position:
            return self.position.title()
        return "Not specified"

    def update_football_info(
        self, position: str = None, preferred_foot: str = None, jersey_number: str = None
    ):
        """Update football-specific information."""
        if position is not None:
            self.position = position
        if preferred_foot is not None:
            self.preferred_foot = preferred_foot
        if jersey_number is not None:
            self.jersey_number = jersey_number

        self.updated_at = datetime.utcnow()

    def update_personal_info(
        self,
        phone_number: str = None,
        email: str = None,
        date_of_birth: str = None,
        emergency_contact: str = None,
        medical_notes: str = None,
    ):
        """Update personal information."""
        if phone_number is not None:
            self.phone_number = phone_number
        if email is not None:
            self.email = email
        if date_of_birth is not None:
            self.date_of_birth = date_of_birth
        if emergency_contact is not None:
            self.emergency_contact = emergency_contact
        if medical_notes is not None:
            self.medical_notes = medical_notes

        self.updated_at = datetime.utcnow()
