#!/usr/bin/env python3
"""
Player Entity

This module defines the Player entity for the player registration domain.
Players represent football players, separate from Team Members who are administrators.
A person can be both a Player and a Team Member, linked by telegram_id.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from kickai.core.enums import PlayerPosition


class OnboardingStatus(Enum):
    """Player onboarding status enumeration."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"


class PlayerRole(Enum):
    """Minimal role enum for tests."""

    PLAYER = "player"
    CAPTAIN = "captain"
    GOALKEEPER = "goalkeeper"


@dataclass
class Player:
    """
    Player entity representing a football player in a team.

    Players are football-specific entities with position, skills, and match-related data.
    This is separate from Team Members who are administrators/managers.
    A person can be both a Player and a Team Member, linked by telegram_id.
    """

    # Core identification fields
    telegram_id: int | None = None  # Telegram user ID (integer) - for linking to Telegram
    player_id: str | None = None  # Player identifier (M001MH format) - unique within team
    team_id: str = ""  # Team identifier (KA format)

    # Personal information
    name: str | None = None
    telegram_username: str | None = None

    # Football-specific information
    position: str | None = None  # e.g., "Midfielder", "Forward"

    # Contact and personal information
    phone_number: str | None = None
    email: str | None = None
    date_of_birth: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    medical_notes: str | None = None

    # Status and approval
    status: str = "pending"  # pending, approved, rejected, active, inactive

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Metadata
    source: str | None = None  # e.g., "telegram_sync", "manual_entry", "registration_form"
    sync_version: str | None = None

    def _post_init_(self):
        """Validate and set defaults after initialization."""
        self._validate()
        self._set_defaults()

    def _validate(self):
        """Validate player data."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")

        # Require either player_id or telegram_id for identification
        if not self.player_id and not self.telegram_id:
            raise ValueError("Either player_id or telegram_id must be provided")

        # Note: player_id format validation removed - 01JD format is valid

        # Validate telegram_id type if provided (allow int or convertible string for database compatibility)
        if self.telegram_id is not None:
            if not isinstance(self.telegram_id, (int, str)):
                raise ValueError(
                    f"telegram_id must be an integer or string, got {type(self.telegram_id)}"
                )
            # If it's a string, it should be convertible to int
            if isinstance(self.telegram_id, str):
                try:
                    int(self.telegram_id)
                except ValueError:
                    raise ValueError(
                        f"telegram_id string '{self.telegram_id}' is not convertible to integer"
                    )

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
        name: str = None,
        telegram_username: str = None,
        phone_number: str = None,
    ) -> "Player":
        """
        Create a Player from Telegram user data.

        Args:
            team_id: The team ID
            telegram_id: The Telegram user ID
            name: Player's display name
            telegram_username: Telegram @username
            phone_number: Phone number if available

        Returns:
            A new Player instance
        """
        # Use provided name or generate default
        display_name = name if name else f"User {telegram_id}"

        return cls(
            team_id=team_id,
            telegram_id=telegram_id,  # Keep as integer
            name=display_name,
            telegram_username=telegram_username,
            phone_number=phone_number,
            source="telegram_sync",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "team_id": self.team_id,
            "telegram_id": self.telegram_id,
            "player_id": self.player_id,
            "name": self.name,
            "telegram_username": self.telegram_username,
            "position": self.position,
            "phone_number": self.phone_number,
            "email": self.email,
            "date_of_birth": self.date_of_birth,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source": self.source,
            "sync_version": self.sync_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Create from dictionary - strict validation for inputs."""
        # Only handle telegram_id - NO OTHER OPTIONS
        telegram_id = data.get("telegram_id")
        if telegram_id is not None:
            try:
                telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id
            except (ValueError, TypeError) as e:
                # For input validation, reject bad data with clear error
                raise ValueError(
                    f"Invalid telegram_id format: {telegram_id}. Must be convertible to integer."
                ) from e

        return cls(
            team_id=data.get("team_id", ""),
            telegram_id=telegram_id,
            player_id=data.get("player_id"),
            name=data.get("name"),
            telegram_username=data.get("telegram_username"),
            position=data.get("position"),
            phone_number=data.get("phone_number"),
            email=data.get("email"),
            date_of_birth=data.get("date_of_birth"),
            emergency_contact_name=data.get("emergency_contact_name"),
            emergency_contact_phone=data.get("emergency_contact_phone"),
            status=data.get("status", "pending"),
            created_at=cls._parse_datetime(data.get("created_at")),
            updated_at=cls._parse_datetime(data.get("updated_at")),
            source=data.get("source"),
            sync_version=data.get("sync_version"),
        )

    @classmethod
    def from_database_dict(cls, data: dict) -> "Player":
        """Create from database dictionary with graceful handling of existing data."""
        import logging

        logger = logging.getLogger(__name__)

        # Create player without triggering validation
        player = object.__new__(cls)

        # Set attributes directly
        player.team_id = data.get("team_id", "")
        # Only handle telegram_id - NO OTHER OPTIONS
        telegram_id = data.get("telegram_id")
        if telegram_id is not None:
            original_value = telegram_id
            original_type = type(telegram_id).__name__
            try:
                telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id
            except (ValueError, TypeError):
                # For database retrieval, log the issue but preserve original value as string
                logger.warning(
                    f"Failed to convert telegram_id '{original_value}' (type: {original_type}) to int, preserving as string. Player: {data.get('name', 'Unknown')}"
                )
                # Keep original value to avoid data loss - downstream code should handle gracefully
                telegram_id = original_value
        player.telegram_id = telegram_id
        player.player_id = data.get("player_id")
        player.name = data.get("name")
        player.telegram_username = data.get("telegram_username")
        player.position = data.get("position")
        player.phone_number = data.get("phone_number")
        player.email = data.get("email")
        player.date_of_birth = data.get("date_of_birth")
        player.emergency_contact_name = data.get("emergency_contact_name")
        player.emergency_contact_phone = data.get("emergency_contact_phone")

        player.medical_notes = data.get("medical_notes")
        player.status = data.get("status", "pending")
        player.source = data.get("source")
        player.sync_version = data.get("sync_version")

        # Parse datetime fields
        if data.get("created_at"):
            try:
                player.created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            except ValueError:
                player.created_at = None
        else:
            player.created_at = None

        if data.get("updated_at"):
            try:
                player.updated_at = datetime.fromisoformat(
                    data["updated_at"].replace("Z", "+00:00")
                )
            except ValueError:
                player.updated_at = None
        else:
            player.updated_at = None

        return player

    @staticmethod
    def _parse_datetime(dt_value) -> datetime | None:
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
        if self.name:
            return self.name
        elif self.telegram_username:
            return f"@{self.telegram_username}"
        elif self.telegram_id:
            return f"User {self.telegram_id}"
        elif self.player_id:
            return f"Player {self.player_id}"
        else:
            return "Unknown Player"

    def get_position_display(self) -> str:
        """Get formatted position display."""
        if self.position:
            return self.position.title()
        return "Not specified"

    def update_football_info(self, position: str = None):
        """Update football-specific information."""
        if position is not None:
            self.position = position

        self.updated_at = datetime.utcnow()

    def update_personal_info(
        self,
        phone_number: str = None,
        email: str = None,
        date_of_birth: str = None,
        emergency_contact_name: str = None,
        emergency_contact_phone: str = None,
        medical_notes: str = None,
    ):
        """Update personal information."""
        if phone_number is not None:
            self.phone_number = phone_number
        if email is not None:
            self.email = email
        if date_of_birth is not None:
            self.date_of_birth = date_of_birth
        if emergency_contact_name is not None:
            self.emergency_contact_name = emergency_contact_name
        if emergency_contact_phone is not None:
            self.emergency_contact_phone = emergency_contact_phone
        if medical_notes is not None:
            self.medical_notes = medical_notes

        self.updated_at = datetime.utcnow()
