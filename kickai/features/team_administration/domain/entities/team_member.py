from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from kickai.utils.user_id_generator import generate_user_id


@dataclass
class TeamMember:
    """
    Team Member entity representing administrative/management roles within a team.

    Team Members are administrators, managers, or other non-playing staff.
    This is separate from Players who represent football players.
    A person can be both a Team Member and a Player, linked by user_id.
    """

    # Core identification fields
    user_id: str = ""  # Generated from telegram_id using generate_user_id()
    team_id: str = ""
    telegram_id: Optional[str] = None

    # Personal information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None

    # Administrative role information
    role: str = "Team Member"  # e.g., "Club Administrator", "Team Manager", "Coach"
    is_admin: bool = False
    status: str = "active"  # active, inactive, suspended

    # Contact information
    phone_number: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Metadata
    source: Optional[str] = None  # e.g., "telegram_sync", "manual_entry"
    sync_version: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        self._validate()
        self._set_defaults()

    def _validate(self):
        """Validate team member data."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.role:
            raise ValueError("Role cannot be empty")

        # Validate status
        valid_statuses = ["active", "inactive", "suspended"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        # Validate user_id format
        if not self.user_id.startswith("user_"):
            raise ValueError(f"Invalid user_id format: {self.user_id}. Must start with 'user_'")

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
        is_admin: bool = False,
    ) -> "TeamMember":
        """
        Create a TeamMember from Telegram user data.

        Args:
            team_id: The team ID
            telegram_id: The Telegram user ID
            first_name: Telegram first name
            last_name: Telegram last name
            username: Telegram username
            is_admin: Whether the user is an admin in Telegram

        Returns:
            A new TeamMember instance
        """
        user_id = generate_user_id(telegram_id)

        # Determine role based on admin status
        role = "Club Administrator" if is_admin else "Team Member"

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
            role=role,
            is_admin=is_admin,
            source="telegram_sync",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "team_id": self.team_id,
            "telegram_id": self.telegram_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "username": self.username,
            "role": self.role,
            "is_admin": self.is_admin,
            "status": self.status,
            "phone_number": self.phone_number,
            "email": self.email,
            "emergency_contact": self.emergency_contact,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source": self.source,
            "sync_version": self.sync_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamMember":
        """Create from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            team_id=data.get("team_id", ""),
            telegram_id=data.get("telegram_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            full_name=data.get("full_name"),
            username=data.get("username"),
            role=data.get("role", "Team Member"),
            is_admin=data.get("is_admin", False),
            status=data.get("status", "active"),
            phone_number=data.get("phone_number"),
            email=data.get("email"),
            emergency_contact=data.get("emergency_contact"),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
            source=data.get("source"),
            sync_version=data.get("sync_version"),
        )

    def is_administrative_role(self) -> bool:
        """Check if this is an administrative role."""
        administrative_roles = ["Club Administrator", "Team Manager", "Coach", "Assistant Coach"]
        return self.role in administrative_roles

    def is_leadership_role(self) -> bool:
        """Check if this is a leadership role."""
        return self.is_admin or self.role in ["Club Administrator", "Team Manager"]

    def get_display_name(self) -> str:
        """Get display name for the member."""
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

    def get_role_display(self) -> str:
        """Get formatted role display."""
        if self.is_admin:
            return f"{self.role} (Admin)"
        return self.role

    def update_contact_info(
        self, phone_number: str = None, email: str = None, emergency_contact: str = None
    ):
        """Update contact information."""
        if phone_number is not None:
            self.phone_number = phone_number
        if email is not None:
            self.email = email
        if emergency_contact is not None:
            self.emergency_contact = emergency_contact

        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate the team member."""
        self.status = "active"
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate the team member."""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()

    def suspend(self):
        """Suspend the team member."""
        self.status = "suspended"
        self.updated_at = datetime.utcnow()
