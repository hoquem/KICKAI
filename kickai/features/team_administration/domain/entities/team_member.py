from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set

from kickai.utils.user_id_generator import generate_user_id


@dataclass
class TeamMember:
    """
    Team Member entity representing administrative/management roles within a team.

    Team Members are administrators, managers, or other non-playing staff.
    This is separate from Players who represent football players.
    A person can be both a Team Member and a Player, linked by telegram_id.
    """

    # Core identification fields
    telegram_id: Optional[int] = None  # Telegram user ID (integer) - for linking to Telegram
    member_id: Optional[str] = None    # Member identifier (M001MH format) - unique within team
    team_id: str = ""                  # Team identifier (KA format)
    
    # Legacy field - being phased out in favor of explicit IDs above
    user_id: str = ""  # DEPRECATED: Use telegram_id for linking, member_id for identification

    # Personal information
    name: Optional[str] = None
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
        
        # Require either member_id or telegram_id for identification
        if not self.member_id and not self.telegram_id:
            raise ValueError("Either member_id or telegram_id must be provided")
            
        if not self.role:
            raise ValueError("Role cannot be empty")

        # Validate status
        valid_statuses = ["active", "inactive", "suspended"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        # Validate member_id format if provided
        if self.member_id and not self.member_id.startswith("M"):
            raise ValueError(f"Invalid member_id format: {self.member_id}. Must start with 'M'")
            
        # Validate telegram_id type if provided
        if self.telegram_id is not None and not isinstance(self.telegram_id, int):
            raise ValueError(f"telegram_id must be an integer, got {type(self.telegram_id)}")

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
        username: str = None,
        is_admin: bool = False,
    ) -> "TeamMember":
        """
        Create a TeamMember from Telegram user data.

        Args:
            team_id: The team ID
            telegram_id: The Telegram user ID
            name: Member's display name
            username: Telegram username
            is_admin: Whether the user is an admin in Telegram

        Returns:
            A new TeamMember instance
        """
        user_id = generate_user_id(telegram_id)

        # Determine role based on admin status
        role = "Club Administrator" if is_admin else "Team Member"

        # Use provided name or generate default
        display_name = name if name else f"User {telegram_id}"

        return cls(
            user_id=user_id,
            team_id=team_id,
            telegram_id=telegram_id,  # Keep as integer
            name=display_name,
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
            "name": self.name,
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
        # Generate user_id from telegram_id if missing or empty
        user_id = data.get("user_id", "")
        telegram_id = data.get("telegram_id")

        if not user_id and telegram_id:
            # Generate user_id from telegram_id
            # Handle both string and integer telegram_id from database
            telegram_id_int = int(telegram_id) if isinstance(telegram_id, str) else telegram_id
            user_id = generate_user_id(telegram_id_int)

        # Ensure telegram_id is integer if provided
        if telegram_id is not None:
            telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id

        return cls(
            user_id=user_id,
            team_id=data.get("team_id", ""),
            telegram_id=telegram_id,
            name=data.get("name"),
            username=data.get("username"),
            role=data.get("role", "Team Member"),
            is_admin=data.get("is_admin", False),
            status=data.get("status", "active"),
            phone_number=data.get("phone_number"),
            email=data.get("email"),
            emergency_contact=data.get("emergency_contact"),
            created_at=cls._parse_datetime(data.get("created_at")),
            updated_at=cls._parse_datetime(data.get("updated_at")),
            source=data.get("source"),
            sync_version=data.get("sync_version"),
        )

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

    def is_administrative_role(self) -> bool:
        """Check if this is an administrative role."""
        administrative_roles = ["Club Administrator", "Team Manager", "Coach", "Assistant Coach"]
        return self.role in administrative_roles

    def is_leadership_role(self) -> bool:
        """Check if this is a leadership role."""
        return self.is_admin or self.role in ["Club Administrator", "Team Manager"]

    def get_display_name(self) -> str:
        """Get display name for the member."""
        if self.name:
            return self.name
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

    @property
    def is_active(self) -> bool:
        """Check if the team member is active."""
        return self.status == "active"
