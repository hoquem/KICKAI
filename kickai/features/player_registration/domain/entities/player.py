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

from kickai.utils.user_id_generator import generate_user_id


class PlayerPosition(Enum):
    """Player position enumeration."""

    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    UTILITY = "utility"


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
    telegram_id: str | None = None
    player_id: str | None = None  # Team-specific player identifier (e.g., "KTI_MH_001")

    # Personal information
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    username: str | None = None

    # Football-specific information
    position: str | None = None  # e.g., "Midfielder", "Forward"
    preferred_foot: str | None = None  # "left", "right", "both"
    jersey_number: str | None = None

    # Contact and personal information
    phone_number: str | None = None
    email: str | None = None
    date_of_birth: str | None = None
    emergency_contact: str | None = None
    medical_notes: str | None = None

    # Status and approval
    status: str = "pending"  # pending, approved, rejected, active, inactive

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Metadata
    source: str | None = None  # e.g., "telegram_sync", "manual_entry", "registration_form"
    sync_version: str | None = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        self._validate()
        self._set_defaults()

    def _validate(self):
        """Validate player data."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        if not self.user_id:
            raise ValueError("User ID cannot be empty")

        # Validate status
        valid_statuses = ["pending", "approved", "rejected", "active", "inactive"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        # Validate user_id format
        if not self.user_id.startswith("user_"):
            raise ValueError(f"Invalid user_id format: {self.user_id}. Must start with 'user_'")

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
            telegram_id=str(telegram_id),
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
        return cls(
            user_id=data.get("user_id", ""),
            team_id=data.get("team_id", ""),
            telegram_id=data.get("telegram_id"),
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
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
            source=data.get("source"),
            sync_version=data.get("sync_version"),
        )

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
