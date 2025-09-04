from dataclasses import dataclass
from datetime import datetime

from kickai.core.enums import MemberStatus


@dataclass
class TeamMember:
    """
    Team Member entity representing administrative/management roles within a team.

    Team Members are administrators, managers, or other non-playing staff.
    This is separate from Players who represent football players.
    A person can be both a Team Member and a Player, linked by telegram_id.
    """

    # Core identification fields
    telegram_id: int | None = None  # Telegram user ID (integer) - for linking to Telegram
    member_id: str | None = None  # Member identifier (M001MH format) - unique within team
    team_id: str = ""  # Team identifier (KA format)

    # Personal information
    name: str | None = None
    username: str | None = None

    # Administrative role information
    role: str = "Team Member"  # e.g., "Club Administrator", "Team Manager", "Coach"
    is_admin: bool = False
    status: MemberStatus = MemberStatus.ACTIVE  # Use enum for type safety

    # Contact information
    phone_number: str | None = None
    email: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Metadata
    source: str | None = None  # e.g., "telegram_sync", "manual_entry"
    sync_version: str | None = None

    def _post_init_(self):
        """Validate and set defaults after initialization."""
        # Parse status first to ensure it's an enum before validation
        self.status = self._parse_status(self.status)
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

        # Validate status - now uses enum for type safety
        if not isinstance(self.status, MemberStatus):
            raise ValueError(f"Invalid status type: {type(self.status)}. Must be MemberStatus enum")

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
        # Determine role based on admin status
        role = "Club Administrator" if is_admin else "Team Member"

        # Use provided name or generate default
        display_name = name if name else f"User {telegram_id}"

        return cls(
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
            "team_id": self.team_id,
            "telegram_id": self.telegram_id,
            "member_id": self.member_id,
            "name": self.name,
            "username": self.username,
            "role": self.role,
            "is_admin": self.is_admin,
            "status": self.status.value if isinstance(self.status, MemberStatus) else self.status,
            "phone_number": self.phone_number,
            "email": self.email,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source": self.source,
            "sync_version": self.sync_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamMember":
        """Create from dictionary."""
        telegram_id = data.get("telegram_id")

        # Ensure telegram_id is integer if provided
        if telegram_id is not None:
            telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id

        # Create constructor arguments dict with only expected fields
        # This prevents unexpected keyword argument errors from legacy fields
        constructor_args = {
            "team_id": data.get("team_id", ""),
            "telegram_id": telegram_id,
            "member_id": data.get("member_id"),
            "name": data.get("name"),
            "username": data.get("username"),
            "role": data.get("role", "Team Member"),
            "is_admin": data.get("is_admin", False),
            "status": cls._parse_status(data.get("status", MemberStatus.ACTIVE.value)),
            "phone_number": data.get("phone_number"),
            "email": data.get("email"),
            "emergency_contact_name": data.get("emergency_contact_name"),
            "emergency_contact_phone": data.get("emergency_contact_phone"),
            "created_at": cls._parse_datetime(data.get("created_at")),
            "updated_at": cls._parse_datetime(data.get("updated_at")),
            "source": data.get("source"),
            "sync_version": data.get("sync_version"),
        }

        return cls(**constructor_args)

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

    @staticmethod
    def _parse_status(status_value) -> MemberStatus:
        """Parse status value handling both string and enum objects."""
        if status_value is None:
            return MemberStatus.ACTIVE

        # If it's already a MemberStatus enum, return it
        if isinstance(status_value, MemberStatus):
            return status_value

        # If it's a string, convert to enum
        if isinstance(status_value, str):
            try:
                # Try to create enum from string value
                return MemberStatus(status_value)
            except ValueError:
                # If invalid status string, default to active
                return MemberStatus.ACTIVE

        # For any other type, default to active
        return MemberStatus.ACTIVE

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
        elif self.member_id:
            return f"Member {self.member_id}"
        else:
            return "Unknown Member"

    def get_role_display(self) -> str:
        """Get formatted role display."""
        if self.is_admin:
            return f"{self.role} (Admin)"
        return self.role

    def update_contact_info(
        self,
        phone_number: str = None,
        email: str = None,
        emergency_contact_name: str = None,
        emergency_contact_phone: str = None,
    ):
        """Update contact information."""
        if phone_number is not None:
            self.phone_number = phone_number
        if email is not None:
            self.email = email
        if emergency_contact_name is not None:
            self.emergency_contact_name = emergency_contact_name
        if emergency_contact_phone is not None:
            self.emergency_contact_phone = emergency_contact_phone

        self.updated_at = datetime.utcnow()

    def set_pending(self):
        """Set the team member to pending status."""
        self.status = MemberStatus.PENDING
        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate the team member."""
        self.status = MemberStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate the team member."""
        self.status = MemberStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def suspend(self):
        """Suspend the team member."""
        self.status = MemberStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """Check if the team member is active."""
        return self.status == MemberStatus.ACTIVE
