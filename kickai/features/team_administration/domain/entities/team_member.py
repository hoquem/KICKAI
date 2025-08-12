from dataclasses import dataclass
from datetime import datetime


@dataclass
class TeamMember:
    """
    Team Member entity representing administrative/management roles within a team.

    Team Members are administrators, managers, or other non-playing staff.
    This is separate from Players who represent football players.
    A person can be both a Team Member and a Player, linked by telegram_id.
    """

    # Core identification fields
    telegram_id: int | None = None  # Telegram user ID (integer) - native Telegram format for linking
    member_id: str | None = None    # Member identifier (M001MH format) - unique within team
    team_id: str = ""                  # Team identifier (KA format)

    # Personal information
    name: str | None = None
    username: str | None = None

    # Administrative role information
    roles: set[str] = None  # Multiple roles support (e.g., {"player", "admin", "coach", "team_member"})
    is_admin: bool = False
    status: str = "active"  # active, inactive, suspended

    # Contact information
    phone_number: str | None = None
    email: str | None = None
    emergency_contact: str | None = None

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Metadata
    source: str | None = None  # e.g., "telegram_sync", "manual_entry"
    sync_version: str | None = None

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

        if not self.roles:
            raise ValueError("Roles cannot be empty")

        # Validate status
        valid_statuses = ["active", "inactive", "suspended"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        # Member_id can be any format - no specific prefix required

        # Validate telegram_id type if provided
        if self.telegram_id is not None and not isinstance(self.telegram_id, int):
            raise ValueError(f"telegram_id must be an integer, got {type(self.telegram_id)}")
        
        # Validate telegram_id value if provided
        if self.telegram_id is not None and self.telegram_id <= 0:
            raise ValueError(f"telegram_id must be positive, got {self.telegram_id}")

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

        # Initialize roles set if not provided
        if self.roles is None:
            self.roles = {"team_member"}

    @classmethod
    def create_from_telegram(
        cls,
        team_id: str,
        telegram_id: int,
        name: str | None = None,
        username: str | None = None,
        is_admin: bool = False,
    ) -> "TeamMember":
        """
        Create a TeamMember from Telegram user data.


            team_id: The team ID
            telegram_id: The Telegram user ID (integer)
            name: Member's display name
            username: Telegram username
            is_admin: Whether the user is an admin in Telegram


    :return: A new TeamMember instance
    :rtype: str  # TODO: Fix type
        """
        # Convert telegram_id to string for storage
        telegram_id_str = str(telegram_id)

        # Determine role based on admin status
        role = "Club Administrator" if is_admin else "Team Member"

        # Use provided name or generate default
        display_name = name if name else f"User {telegram_id}"

        # Determine roles based on admin status and role
        roles = {"team_member"}
        if is_admin:
            roles.add("admin")
        if role in ["Club Administrator", "Team Manager", "Coach", "Assistant Coach"]:
            roles.add(role.lower().replace(" ", "_"))

        return cls(
            team_id=team_id,
            telegram_id=telegram_id_str,  # Store as string for cross-entity linking
            name=display_name,
            username=username,
            roles=roles,
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
            "roles": list(self.roles) if self.roles else [],
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
        # Ensure telegram_id is string if provided
        telegram_id = data.get("telegram_id")
        if telegram_id is not None:
            telegram_id = str(telegram_id) if not isinstance(telegram_id, str) else telegram_id

        is_admin = data.get("is_admin", False)

        # Initialize roles from data
        roles_data = data.get("roles")
        if roles_data:
            # Convert list to set if it's a list
            if isinstance(roles_data, list):
                roles = set(roles_data)
            elif isinstance(roles_data, set):
                roles = roles_data
            else:
                roles = {"team_member"}
        else:
            # Default to team_member role
            roles = {"team_member"}
            if is_admin:
                roles.add("admin")

        return cls(
            team_id=data.get("team_id", ""),
            telegram_id=telegram_id,
            member_id=data.get("member_id"),
            name=data.get("name"),
            username=data.get("username"),
            roles=roles,
            is_admin=is_admin,
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

    def is_administrative_role(self) -> bool:
        """Check if this is an administrative role."""
        administrative_roles = {"club_administrator", "team_manager", "coach", "assistant_coach"}
        return bool(self.roles and administrative_roles.intersection(self.roles))

    def is_leadership_role(self) -> bool:
        """Check if this is a leadership role."""
        leadership_roles = {"club_administrator", "team_manager", "admin"}
        return bool(self.roles and leadership_roles.intersection(self.roles))

    def get_display_name(self) -> str:
        """Get display name for the member."""
        if self.name:
            return self.name
        elif self.username:
            return f"@{self.username}"
        elif self.telegram_id:
            return f"User {self.telegram_id}"
        else:
            return f"Member {self.member_id}" if self.member_id else "Unknown Member"

    def get_primary_role_display(self) -> str:
        """Get formatted primary role display."""
        if not self.roles:
            return "No role"

        # Priority order for role display
        role_priority = [
            "club_administrator",
            "team_manager",
            "coach",
            "assistant_coach",
            "admin",
            "team_member"
        ]

        for role in role_priority:
            if role in self.roles:
                return role.replace("_", " ").title()

    def update_contact_info(
        self, phone_number: str | None = None, email: str | None = None, emergency_contact: str | None = None
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

    def has_role(self, role: str) -> bool:
        """Check if the team member has a specific role."""
        return role in self.roles if self.roles else False

    def add_role(self, role: str) -> None:
        """Add a role to the team member."""
        if self.roles is None:
            self.roles = set()
        self.roles.add(role)
        self.updated_at = datetime.utcnow()

    def remove_role(self, role: str) -> None:
        """Remove a role from the team member."""
        if self.roles and role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.utcnow()

    def get_roles_display(self) -> str:
        """Get a formatted string of all roles."""
        if not self.roles:
            return "No role"
        return ", ".join(sorted(self.roles))
