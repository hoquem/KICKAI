"""
Database Models for KICKAI

This module defines the data models used throughout the KICKAI system,
providing proper validation, type safety, and serialization capabilities.
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import re
from uuid import uuid4


class PlayerPosition(Enum):
    """Player positions."""
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    STRIKER = "striker"
    UTILITY = "utility"


class PlayerRole(Enum):
    """Player roles in the team."""
    PLAYER = "player"
    CAPTAIN = "captain"
    VICE_CAPTAIN = "vice_captain"
    MANAGER = "manager"
    COACH = "coach"


class OnboardingStatus(Enum):
    """Player onboarding status."""
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TeamStatus(Enum):
    """Team status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class MatchStatus(Enum):
    """Match status."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Player:
    """Player data model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    position: PlayerPosition = PlayerPosition.UTILITY
    role: PlayerRole = PlayerRole.PLAYER
    fa_registered: bool = False
    fa_eligible: bool = True
    player_id: str = ""  # e.g., JS1 for John Smith
    invite_link: Optional[str] = None
    onboarding_status: OnboardingStatus = OnboardingStatus.PENDING
    onboarding_step: Optional[str] = None
    emergency_contact: Optional[str] = None
    date_of_birth: Optional[str] = None
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    team_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate player data after initialization."""
        if not self.name.strip():
            raise ValueError("Player name cannot be empty")
        
        # Allow empty phone only during onboarding (pending approval or in progress)
        if self.onboarding_status not in [OnboardingStatus.PENDING_APPROVAL, OnboardingStatus.IN_PROGRESS]:
            if not self.phone.strip():
                raise ValueError("Player phone cannot be empty")
        # If phone is provided, validate format
        if self.phone.strip() and not self._validate_phone(self.phone):
            raise ValueError("Invalid phone number format")
        
        if self.email and not self._validate_email(self.email):
            raise ValueError("Invalid email format")
        
        if not self.player_id:
            self.player_id = self._generate_player_id()
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        # Basic UK phone number validation
        phone_pattern = r'^(\+44|0)[1-9]\d{8,9}$'
        return bool(re.match(phone_pattern, phone.replace(' ', '')))
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def _generate_player_id(self) -> str:
        """Generate a unique player ID from name."""
        if not self.name:
            return ""
        
        # Extract initials from name
        name_parts = self.name.strip().split()
        if len(name_parts) >= 2:
            initials = ''.join(part[0].upper() for part in name_parts[:2])
        else:
            initials = self.name[:2].upper()
        
        return f"{initials}1"  # Simple format, could be enhanced with numbering
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary."""
        data = asdict(self)
        data['position'] = self.position.value
        data['role'] = self.role.value
        data['onboarding_status'] = self.onboarding_status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary."""
        # Convert enum values back to enum objects
        if 'position' in data and isinstance(data['position'], str):
            data['position'] = PlayerPosition(data['position'])
        
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = PlayerRole(data['role'])
        
        if 'onboarding_status' in data and isinstance(data['onboarding_status'], str):
            data['onboarding_status'] = OnboardingStatus(data['onboarding_status'])
        
        # Convert datetime strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def update(self, **kwargs):
        """Update player fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()


@dataclass
class Team:
    """Team data model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    status: TeamStatus = TeamStatus.ACTIVE
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    settings: Dict[str, Any] = field(default_factory=dict)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate team data after initialization."""
        if not self.name.strip():
            raise ValueError("Team name cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Team':
        """Create team from dictionary."""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TeamStatus(data['status'])
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def update(self, **kwargs):
        """Update team fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()


@dataclass
class Match:
    """Match data model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    team_id: str = ""
    opponent: str = ""
    date: datetime = field(default_factory=datetime.now)
    location: Optional[str] = None
    status: MatchStatus = MatchStatus.SCHEDULED
    home_away: str = "home"  # home, away, neutral
    competition: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate match data after initialization."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        
        if not self.opponent.strip():
            raise ValueError("Opponent cannot be empty")
        
        if self.home_away not in ["home", "away", "neutral"]:
            raise ValueError("Home/away must be 'home', 'away', or 'neutral'")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['date'] = self.date.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Match':
        """Create match from dictionary."""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = MatchStatus(data['status'])
        
        if 'date' in data and isinstance(data['date'], str):
            data['date'] = datetime.fromisoformat(data['date'])
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def update(self, **kwargs):
        """Update match fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()


@dataclass
class TeamMember:
    """Team member data model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    team_id: str = ""
    user_id: str = ""  # References player.id or external user ID
    roles: List[str] = field(default_factory=list)  # List of roles: player, captain, vice_captain, manager, coach, admin, volunteer
    permissions: List[str] = field(default_factory=list)  # admin, manage_players, manage_fixtures, etc.
    chat_access: Dict[str, bool] = field(default_factory=lambda: {"main_chat": True, "leadership_chat": False})
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate team member data after initialization."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        
        # Validate that roles list is not empty
        if not self.roles:
            raise ValueError("Team member must have at least one role")
        
        # Validate role values
        valid_roles = {'player', 'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer'}
        invalid_roles = set(self.roles) - valid_roles
        if invalid_roles:
            raise ValueError(f"Invalid roles: {invalid_roles}. Valid roles: {valid_roles}")
    
    def has_role(self, role: str) -> bool:
        """Check if team member has a specific role."""
        return role in self.roles
    
    def has_any_leadership_role(self) -> bool:
        """Check if team member has any leadership role."""
        leadership_roles = {'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer'}
        return any(role in leadership_roles for role in self.roles)
    
    def is_player(self) -> bool:
        """Check if team member is a player."""
        return 'player' in self.roles
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team member to dictionary."""
        data = asdict(self)
        data['joined_at'] = self.joined_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamMember':
        """Create team member from dictionary."""
        if 'joined_at' in data and isinstance(data['joined_at'], str):
            data['joined_at'] = datetime.fromisoformat(data['joined_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def update(self, **kwargs):
        """Update team member fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()


@dataclass
class BotMapping:
    """Bot mapping data model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    team_name: str = ""
    bot_username: str = ""
    chat_id: str = ""
    bot_token: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate bot mapping data after initialization."""
        if not self.team_name.strip():
            raise ValueError("Team name cannot be empty")
        
        if not self.bot_username.strip():
            raise ValueError("Bot username cannot be empty")
        
        if not self.chat_id.strip():
            raise ValueError("Chat ID cannot be empty")
        
        if not self.bot_token.strip():
            raise ValueError("Bot token cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bot mapping to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BotMapping':
        """Create bot mapping from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def update(self, **kwargs):
        """Update bot mapping fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now() 