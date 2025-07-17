"""
Improved Database Models for KICKAI

This module defines improved data models using great OOP principles:
- Base classes for common functionality
- Proper validation and error handling
- Consistent patterns across all models
- Better type safety and documentation
- Factory methods and builders
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import re
from uuid import uuid4
from utils.validation_utils import validate_phone, validate_email, validate_name


# ============================================================================
# ENUMS
# ============================================================================

class PlayerPosition(Enum):
    """Player positions in football."""
    ANY = "any"
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    STRIKER = "striker"
    UTILITY = "utility"
    
    @classmethod
    def get_display_name(cls, position: 'PlayerPosition') -> str:
        """Get a human-readable display name for a position."""
        return position.value.title()

    @classmethod
    def from_string(cls, position_str: str) -> 'PlayerPosition':
        """Create PlayerPosition from string with case-insensitive matching."""
        if not position_str:
            return cls.UTILITY
        
        # Normalize the string
        normalized = position_str.lower().strip()
        
        # Try exact match first
        try:
            return cls(normalized)
        except ValueError:
            pass
        
        # Try case-insensitive matching
        for position in cls:
            if position.value.lower() == normalized:
                return position
        
        # Try partial matching for common variations
        if normalized in ['fwd', 'for', 'striker']:
            return cls.FORWARD
        elif normalized in ['gk', 'keeper', 'goalie']:
            return cls.GOALKEEPER
        elif normalized in ['def', 'defence', 'defense']:
            return cls.DEFENDER
        elif normalized in ['mid', 'center']:
            return cls.MIDFIELDER
        elif normalized in ['st', 'attack']:
            return cls.STRIKER
        elif normalized in ['any', 'all', 'flexible']:
            return cls.ANY
        
        # Default to utility if no match found
        return cls.UTILITY


class PlayerRole(Enum):
    """Player roles in the team."""
    PLAYER = "player"
    CAPTAIN = "captain"
    VICE_CAPTAIN = "vice_captain"
    MANAGER = "manager"
    COACH = "coach"
    
    @classmethod
    def is_leadership_role(cls, role: 'PlayerRole') -> bool:
        """Check if a role is a leadership role."""
        leadership_roles = {cls.CAPTAIN, cls.VICE_CAPTAIN, cls.MANAGER, cls.COACH}
        return role in leadership_roles
    
    @classmethod
    def from_string(cls, role_str: str) -> 'PlayerRole':
        """Create PlayerRole from string with legacy value handling."""
        if not role_str:
            return cls.PLAYER
        
        # Normalize the string
        normalized = role_str.lower().strip()
        
        # Handle legacy "admin" value by mapping to "manager"
        if normalized == "admin":
            return cls.MANAGER
        
        # Try exact match first
        try:
            return cls(normalized)
        except ValueError:
            pass
        
        # Try case-insensitive matching
        for role in cls:
            if role.value.lower() == normalized:
                return role
        
        # Default to player if no match found
        return cls.PLAYER


class OnboardingStatus(Enum):
    """Player onboarding status."""
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    
    @classmethod
    def is_completed(cls, status: 'OnboardingStatus') -> bool:
        """Check if onboarding is completed."""
        return status == cls.COMPLETED
    
    @classmethod
    def is_in_progress(cls, status: 'OnboardingStatus') -> bool:
        """Check if onboarding is in progress."""
        return status in [cls.IN_PROGRESS, cls.PENDING_APPROVAL]
    
    @classmethod
    def from_string(cls, status_str: str) -> 'OnboardingStatus':
        """Create OnboardingStatus from string with flexible parsing."""
        if not status_str:
            return cls.PENDING
        
        normalized = status_str.strip().lower()
        
        # Try exact match first
        try:
            return cls(normalized)
        except ValueError:
            pass
        
        # Try case-insensitive matching
        for status in cls:
            if status.value.lower() == normalized:
                return status
        
        # Try common variations
        if normalized in ['approved', 'complete', 'done', 'finished']:
            return cls.COMPLETED
        elif normalized in ['pending', 'waiting', 'new']:
            return cls.PENDING
        elif normalized in ['in_progress', 'progress', 'ongoing', 'active']:
            return cls.IN_PROGRESS
        elif normalized in ['pending_approval', 'approval', 'review']:
            return cls.PENDING_APPROVAL
        elif normalized in ['failed', 'error', 'rejected']:
            return cls.FAILED
        
        # Default to pending if no match found
        return cls.PENDING


class TeamStatus(Enum):
    """Team status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    
    @classmethod
    def is_active(cls, status: 'TeamStatus') -> bool:
        """Check if team is active."""
        return status == cls.ACTIVE


class MatchStatus(Enum):
    """Match status."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    @classmethod
    def is_finished(cls, status: 'MatchStatus') -> bool:
        """Check if match is finished."""
        return status in [cls.COMPLETED, cls.CANCELLED]


class PaymentStatus(Enum):
    """Payment status."""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentType(Enum):
    """Payment type."""
    MATCH_FEE = "match_fee"
    SUBSCRIPTION = "subscription"
    FINE = "fine"
    OTHER = "other"


class ExpenseCategory(Enum):
    """Expense category."""
    PITCH_FEES = "pitch_fees"
    REFEREE_FEES = "referee_fees"
    EQUIPMENT = "equipment"
    TEAM_MEAL = "team_meal"
    FA_FEES = "fa_fees"
    OTHER = "other"


# ============================================================================
# BASE CLASSES
# ============================================================================

@dataclass
class BaseModel(ABC):
    """Base class for all models with common functionality."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Common validation for all models."""
        self._validate_common_fields()
        self._validate_model_specific()
    
    def _validate_common_fields(self):
        """Validate common fields across all models."""
        if not self.id:
            raise ValueError("ID cannot be empty")
        
        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime object")
        
        if not isinstance(self.updated_at, datetime):
            raise ValueError("updated_at must be a datetime object")
    
    @abstractmethod
    def _validate_model_specific(self):
        """Validate model-specific fields. Must be implemented by subclasses."""
        pass
    
    def update(self, **kwargs):
        """Update model fields with validation."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        # Re-validate after update
        self._validate_model_specific()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary. Must be implemented by subclasses."""
        pass
    
    def get_age(self) -> Optional[int]:
        """Get age of the model (time since creation)."""
        if not self.created_at:
            return None
        return (datetime.now() - self.created_at).days


class ValidatorMixin:
    """Mixin providing validation utilities."""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate UK phone number format using centralized validation."""
        return validate_phone(phone, region="GB")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format using centralized validation."""
        return validate_email(email)
    
    @staticmethod
    def validate_name(name: str, min_length: int = 2) -> bool:
        """Validate name format using centralized validation."""
        return validate_name(name, min_length=min_length)
    
    @staticmethod
    def validate_id_format(id_str: str, prefix: str = "") -> bool:
        """Validate ID format."""
        if not id_str:
            return False
        if prefix and not id_str.startswith(prefix):
            return False
        return len(id_str) >= 3


# ============================================================================
# PLAYER MODEL
# ============================================================================

@dataclass
class Player(BaseModel, ValidatorMixin):
    """Player data model with enhanced onboarding support."""
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    position: PlayerPosition = PlayerPosition.UTILITY
    role: PlayerRole = PlayerRole.PLAYER
    fa_registered: bool = False
    fa_eligible: bool = True
    fa_registration_number: Optional[str] = None
    match_eligible: bool = False
    player_id: str = ""
    invite_link: Optional[str] = None
    onboarding_status: OnboardingStatus = OnboardingStatus.PENDING
    onboarding_step: Optional[str] = None
    onboarding_started_at: Optional[datetime] = None
    onboarding_completed_at: Optional[datetime] = None
    emergency_contact: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    date_of_birth: Optional[str] = None
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    external_id: Optional[str] = None # New field for external database integration
    team_id: str = ""
    admin_approved: bool = False
    admin_approved_at: Optional[datetime] = None
    admin_approved_by: Optional[str] = None
    reminders_sent: int = 0
    last_reminder_sent: Optional[datetime] = None
    next_reminder_due: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    is_injured: bool = False
    injury_details: Optional[str] = None
    is_suspended: bool = False
    suspension_details: Optional[str] = None
    return_date: Optional[datetime] = None
    onboarding_progress: Dict[str, Any] = field(default_factory=lambda: {
        "emergency_contact": {"completed": False, "completed_at": None, "data": None},
        "date_of_birth": {"completed": False, "completed_at": None, "data": None},
        "fa_registration": {"completed": False, "completed_at": None, "data": None},
        "completion": {"completed": False, "completed_at": None, "data": None}
    })
    
    def __post_init__(self):
        """Validate player data after initialization and auto-generate player_id if missing."""
        super().__post_init__()
        
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
        
        # Auto-generate player_id if not provided
        if not self.player_id:
            from utils.id_generator import generate_player_id_from_name
            self.player_id = generate_player_id_from_name(self.name, self.team_id)
            self.id = self.player_id
        
        # Set onboarding started time if status is in progress
        if self.onboarding_status == OnboardingStatus.IN_PROGRESS and not self.onboarding_started_at:
            self.onboarding_started_at = datetime.now()
        
        # Set last activity if not set
        if not self.last_activity:
            self.last_activity = datetime.now()
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format using centralized validation."""
        return validate_phone(phone, region="GB")
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format using centralized validation."""
        return validate_email(email)
    
    def get_onboarding_progress(self) -> Dict[str, Any]:
        """Get current onboarding progress."""
        total_steps = 4
        completed_steps = sum(1 for step in self.onboarding_progress.values() if step.get("completed", False))
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": (completed_steps / total_steps) * 100 if total_steps > 0 else 0,
            "current_step": self._get_current_step(),
            "steps": self.onboarding_progress
        }
    
    def _get_current_step(self) -> str:
        """Get the current onboarding step."""
        if self.onboarding_status == OnboardingStatus.PENDING:
            return "basic_registration"
        elif self.onboarding_status == OnboardingStatus.IN_PROGRESS:
            if not self.onboarding_progress["emergency_contact"]["completed"]:
                return "emergency_contact"
            elif not self.onboarding_progress["date_of_birth"]["completed"]:
                return "date_of_birth"
            elif not self.onboarding_progress["fa_registration"]["completed"]:
                return "fa_registration"
            else:
                return "completion"
        else:
            return "completed"
    
    def get_current_onboarding_step(self) -> str:
        """Get the current onboarding step (public method)."""
        return self._get_current_step()
    
    def update_onboarding_step(self, step: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Update onboarding step progress."""
        if step in self.onboarding_progress:
            self.onboarding_progress[step]["completed"] = True
            self.onboarding_progress[step]["completed_at"] = datetime.now()
            if data:
                self.onboarding_progress[step]["data"] = data
            
            # Update last activity
            self.last_activity = datetime.now()
            
            # Check if all steps are complete
            if all(step_data.get("completed", False) for step_data in self.onboarding_progress.values()):
                self.onboarding_status = OnboardingStatus.COMPLETED
                self.onboarding_completed_at = datetime.now()
    
    def needs_reminder(self) -> bool:
        """Check if player needs a reminder."""
        if self.onboarding_status not in [OnboardingStatus.IN_PROGRESS, OnboardingStatus.PENDING]:
            return False
        
        if self.reminders_sent >= 3:  # Maximum 3 reminders
            return False
        
        if not self.last_activity:
            return True
        
        # Check if enough time has passed since last activity
        hours_since_activity = (datetime.now() - self.last_activity).total_seconds() / 3600
        
        if self.reminders_sent == 0 and hours_since_activity >= 24:
            return True
        elif self.reminders_sent == 1 and hours_since_activity >= 48:
            return True
        elif self.reminders_sent == 2 and hours_since_activity >= 72:
            return True
        
        return False
    
    def get_next_reminder_time(self) -> Optional[datetime]:
        """Get when the next reminder should be sent."""
        if self.reminders_sent >= 3:
            return None
        
        if not self.last_activity:
            return datetime.now() + timedelta(hours=24)
        
        if self.reminders_sent == 0:
            return self.last_activity + timedelta(hours=24)
        elif self.reminders_sent == 1:
            return self.last_activity + timedelta(hours=48)
        elif self.reminders_sent == 2:
            return self.last_activity + timedelta(hours=72)
        
        return None
    
    def send_reminder(self) -> None:
        """Mark that a reminder was sent."""
        self.reminders_sent += 1
        self.last_reminder_sent = datetime.now()
        self.next_reminder_due = self.get_next_reminder_time()

    def is_match_eligible(self) -> bool:
        """Check if player is eligible for match selection."""
        # Check if onboarding is complete and admin approved
        if not self.is_onboarding_complete() or not self.admin_approved:
            return False
        if self.is_injured:
            return False
        if self.is_suspended:
            return False
        if self.return_date and self.return_date > datetime.now():
            return False
        return True

    def is_fa_registered(self) -> bool:
        """Check if player is FA registered."""
        return self.fa_registered and self.fa_eligible

    def is_fa_eligible(self) -> bool:
        """Check if player is eligible for FA registration."""
        return self.fa_eligible

    def get_display_status(self) -> str:
        """Get a human-readable display status for the player."""
        if self.onboarding_status == OnboardingStatus.COMPLETED and self.admin_approved:
            if self.is_injured:
                return "Injured"
            elif self.is_suspended:
                return "Suspended"
            elif self.return_date and self.return_date > datetime.now():
                return f"Returning {self.return_date.strftime('%Y-%m-%d')}"
            else:
                return "Active"
        elif self.onboarding_status == OnboardingStatus.IN_PROGRESS:
            return "Onboarding"
        elif self.onboarding_status == OnboardingStatus.PENDING_APPROVAL:
            return "Pending Approval"
        elif self.onboarding_status == OnboardingStatus.PENDING:
            return "Pending"
        else:
            return "Unknown"
    
    def get_detailed_status(self) -> str:
        """Get a detailed status string including FA and match eligibility."""
        base_status = self.get_display_status()
        
        # Add FA status
        if self.fa_registered:
            fa_status = "🏆 FA Registered"
        elif self.fa_eligible:
            fa_status = "⚠️ FA Eligible (Not Registered)"
        else:
            fa_status = "❌ FA Not Eligible"
        
        # Add match eligibility
        if self.is_match_eligible():
            match_status = "✅ Match Eligible"
        else:
            match_status = "❌ Not Match Eligible"
        
        return f"{base_status} | {fa_status} | {match_status}"

    def is_active(self) -> bool:
        """Check if player is active (completed onboarding and approved)."""
        return (self.onboarding_status == OnboardingStatus.COMPLETED and 
                self.admin_approved and 
                not self.is_injured and 
                not self.is_suspended)

    def is_pending_approval(self) -> bool:
        """Check if player is pending approval."""
        return (self.onboarding_status in [OnboardingStatus.PENDING, OnboardingStatus.PENDING_APPROVAL] or
                (self.onboarding_status == OnboardingStatus.COMPLETED and not self.admin_approved))

    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary."""
        data = super().to_dict()
        data['position'] = self.position.value
        data['role'] = self.role.value
        data['onboarding_status'] = self.onboarding_status.value
        data['onboarding_started_at'] = self.onboarding_started_at.isoformat() if self.onboarding_started_at else None
        data['onboarding_completed_at'] = self.onboarding_completed_at.isoformat() if self.onboarding_completed_at else None
        data['admin_approved_at'] = self.admin_approved_at.isoformat() if self.admin_approved_at else None
        data['last_reminder_sent'] = self.last_reminder_sent.isoformat() if self.last_reminder_sent else None
        data['next_reminder_due'] = self.next_reminder_due.isoformat() if self.next_reminder_due else None
        data['last_activity'] = self.last_activity.isoformat() if self.last_activity else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary."""
        # Convert enum values back to enum objects with flexible position parsing
        if 'position' in data and isinstance(data['position'], str):
            data['position'] = PlayerPosition.from_string(data['position'])
        
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = PlayerRole.from_string(data['role'])
        
        if 'onboarding_status' in data and isinstance(data['onboarding_status'], str):
            data['onboarding_status'] = OnboardingStatus.from_string(data['onboarding_status'])
        
        # Convert datetime strings back to datetime objects
        datetime_fields = [
            'onboarding_started_at', 'onboarding_completed_at', 'admin_approved_at',
            'last_reminder_sent', 'next_reminder_due', 'last_activity',
            'created_at', 'updated_at'
        ]
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        try:
            return cls(**data)
        except ValueError as e:
            # Log the error and the data that caused it
            # In a real application, you'd use a proper logger
            print(f"Skipping player due to validation error: {e}. Data: {data}")
            return None
    
    @classmethod
    def create(cls, name: str, phone: str, team_id: str, **kwargs) -> 'Player':
        """Factory method to create a player with validation."""
        # Handle position with flexible parsing
        if 'position' in kwargs and isinstance(kwargs['position'], str):
            kwargs['position'] = PlayerPosition.from_string(kwargs['position'])
        
        return cls(name=name, phone=phone, team_id=team_id, **kwargs)
    
    @classmethod
    def with_generated_id(cls, name: str, phone: str, team_id: str, **kwargs) -> 'Player':
        """Factory method to create a player with a generated ID."""
        from utils.id_generator import generate_player_id_from_name
        
        # Generate player ID
        player_id = generate_player_id_from_name(name, team_id)
        
        # Set the generated ID
        kwargs['player_id'] = player_id
        kwargs['id'] = player_id  # Also set the base id field
        
        # Handle position with flexible parsing
        if 'position' in kwargs and isinstance(kwargs['position'], str):
            kwargs['position'] = PlayerPosition.from_string(kwargs['position'])
        
        return cls(name=name, phone=phone, team_id=team_id, **kwargs)

    def get_display_name(self) -> str:
        """Get a human-readable display name for the player."""
        return f"{self.name} ({self.position.value.title()}) - {self.player_id}"

    def get_position_display(self) -> str:
        """Get a human-readable display name for the player's position."""
        return self.position.value.title()

    def is_onboarding_complete(self) -> bool:
        """Check if onboarding is complete."""
        return self.onboarding_status == OnboardingStatus.COMPLETED

    def _validate_model_specific(self):
        # Minimal implementation for test and basic usage
        pass


# ============================================================================
# TEAM MODEL
# ============================================================================

@dataclass
class Team(BaseModel, ValidatorMixin):
    """Improved Team data model."""
    
    name: str = ""
    status: TeamStatus = TeamStatus.ACTIVE
    description: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    fa_website_url: Optional[str] = None
    fa_team_url: Optional[str] = None
    fa_fixtures_url: Optional[str] = None
    payment_rules: Dict[str, Any] = field(default_factory=dict)
    budget_limits: Dict[str, Any] = field(default_factory=dict)
    current_balance: float = 0.0
    
    def _validate_model_specific(self):
        """Validate team-specific fields."""
        if not self.validate_name(self.name, min_length=3):
            raise ValueError("Team name cannot be empty and must be at least 3 characters")
    
    def is_active(self) -> bool:
        """Check if team is active."""
        return TeamStatus.is_active(self.status)
    
    def get_display_name(self) -> str:
        """Get team's display name."""
        return f"{self.name} ({self.status.value})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary."""
        data = super().to_dict()
        data['status'] = self.status.value
        data['fa_website_url'] = self.fa_website_url
        data['payment_rules'] = self.payment_rules
        data['budget_limits'] = self.budget_limits
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Team':
        """Create team from dictionary."""
        # Remove team_id if present (it's not a field in the Team model)
        if 'team_id' in data:
            del data['team_id']
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TeamStatus(data['status'])
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Handle new fields, providing defaults if not present in data
        data['fa_website_url'] = data.get('fa_website_url')
        data['payment_rules'] = data.get('payment_rules', {})
        data['budget_limits'] = data.get('budget_limits', {})
        
        return cls(**data)
    
    @classmethod
    def create(cls, name: str, description: Optional[str] = None, **kwargs) -> 'Team':
        """Factory method to create a team."""
        return cls(
            name=name,
            description=description,
            **kwargs
        )


# ============================================================================
# TEAM MEMBER MODEL
# ============================================================================

@dataclass
class TeamMember(BaseModel):
    """Improved Team Member data model."""
    
    team_id: str = ""
    user_id: str = ""
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    chat_access: Dict[str, bool] = field(default_factory=lambda: {"main_chat": True, "leadership_chat": False})
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.now)
    
    def _validate_model_specific(self):
        """Validate team member-specific fields."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        
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
    
    def can_access_chat(self, chat_type: str) -> bool:
        """Check if member can access a specific chat type."""
        return self.chat_access.get(chat_type, False)
    
    def get_display_name(self) -> str:
        """Get member's display name."""
        roles_str = ", ".join(self.roles)
        return f"User {self.user_id} ({roles_str})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team member to dictionary."""
        data = super().to_dict()
        data['joined_at'] = self.joined_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamMember':
        """Create team member from dictionary."""
        if 'joined_at' in data and isinstance(data['joined_at'], str):
            data['joined_at'] = datetime.fromisoformat(data['joined_at'])
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    @classmethod
    def create(cls, team_id: str, user_id: str, roles: List[str], **kwargs) -> 'TeamMember':
        """Factory method to create a team member."""
        return cls(
            team_id=team_id,
            user_id=user_id,
            roles=roles,
            **kwargs
        )


# ============================================================================
# MATCH MODEL
# ============================================================================

@dataclass
class Match(BaseModel):
    """Improved Match data model."""
    
    team_id: str = ""
    opponent: str = ""
    date: datetime = field(default_factory=datetime.now)
    location: Optional[str] = None
    status: MatchStatus = MatchStatus.SCHEDULED
    home_away: str = "home"  # home, away, neutral
    competition: Optional[str] = None
    confirmed_players: List[str] = field(default_factory=list) # List of player_ids
    score: Optional[str] = None
    goal_scorers: List[str] = field(default_factory=list)
    assists: List[str] = field(default_factory=list)
    attendees: List[str] = field(default_factory=list) # List of player_ids who confirmed attendance
    
    def _validate_model_specific(self):
        """Validate match-specific fields."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        
        if not self.opponent.strip():
            raise ValueError("Opponent cannot be empty")
        
        if self.home_away not in ["home", "away", "neutral"]:
            raise ValueError("Home/away must be 'home', 'away', or 'neutral'")
    
    def is_finished(self) -> bool:
        """Check if match is finished."""
        return MatchStatus.is_finished(self.status)
    
    def is_home_match(self) -> bool:
        """Check if this is a home match."""
        return self.home_away == "home"
    
    def get_display_name(self) -> str:
        """Get match display name."""
        return f"{self.opponent} ({self.home_away}) - {self.status.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match to dictionary."""
        data = super().to_dict()
        data['status'] = self.status.value
        data['date'] = self.date.isoformat()
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
    
    @classmethod
    def create(cls, team_id: str, opponent: str, date: datetime, **kwargs) -> 'Match':
        """Factory method to create a match."""
        return cls(
            team_id=team_id,
            opponent=opponent,
            date=date,
            **kwargs
        )


# ============================================================================
# PAYMENT MODEL
# ============================================================================

@dataclass
class Payment(BaseModel, ValidatorMixin):
    """Payment data model."""
    
    team_id: str = ""
    player_id: str = ""
    amount: float = 0.0
    type: PaymentType = PaymentType.OTHER
    status: PaymentStatus = PaymentStatus.PENDING
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    related_entity_id: Optional[str] = None  # e.g., match_id, subscription_id
    description: Optional[str] = None
    
    def _validate_model_specific(self):
        """Validate payment-specific fields."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        if not self.player_id:
            raise ValueError("Player ID cannot be empty")
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")
        if not isinstance(self.type, PaymentType):
            raise ValueError("Invalid payment type")
        if not isinstance(self.status, PaymentStatus):
            raise ValueError("Invalid payment status")

    def to_dict(self) -> Dict[str, Any]:
        """Convert payment to dictionary."""
        data = super().to_dict()
        data['type'] = self.type.value
        data['status'] = self.status.value
        data['due_date'] = self.due_date.isoformat() if self.due_date else None
        data['paid_date'] = self.paid_date.isoformat() if self.paid_date else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create payment from dictionary."""
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = PaymentType(data['type'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PaymentStatus(data['status'])
        
        if 'due_date' in data and isinstance(data['due_date'], str):
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        if 'paid_date' in data and isinstance(data['paid_date'], str):
            data['paid_date'] = datetime.fromisoformat(data['paid_date'])
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)

    @classmethod
    def create(cls, team_id: str, player_id: str, amount: float, type: PaymentType, **kwargs) -> 'Payment':
        """Factory method to create a payment."""
        return cls(team_id=team_id, player_id=player_id, amount=amount, type=type, **kwargs)


# ============================================================================
# EXPENSE MODEL
# ============================================================================

@dataclass
class Expense(BaseModel, ValidatorMixin):
    """Expense data model."""

@dataclass
class FixtureData(BaseModel):
    """Model for scraped fixture data."""
    team_id: str = ""
    fixture_text: str = ""
    fixture_date: Optional[datetime] = None
    opponent: Optional[str] = None
    home_away: Optional[str] = None
    competition: Optional[str] = None
    score: Optional[str] = None
    status: Optional[str] = None

    def _validate_model_specific(self):
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        if not self.fixture_text:
            raise ValueError("Fixture text cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['fixture_date'] = self.fixture_date.isoformat() if self.fixture_date else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FixtureData':
        if 'fixture_date' in data and isinstance(data['fixture_date'], str):
            data['fixture_date'] = datetime.fromisoformat(data['fixture_date'])
        return cls(**data)


class Expense(BaseModel, ValidatorMixin):
    """Expense data model."""
    team_id: str = ""
    amount: float = 0.0
    category: ExpenseCategory = ExpenseCategory.OTHER
    description: Optional[str] = None
    date: datetime = field(default_factory=datetime.now)
    receipt_url: Optional[str] = None
    
    def _validate_model_specific(self):
        """Validate expense-specific fields."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        if self.amount <= 0:
            raise ValueError("Expense amount must be positive")
        if not isinstance(self.category, ExpenseCategory):
            raise ValueError("Invalid expense category")

    def to_dict(self) -> Dict[str, Any]:
        """Convert expense to dictionary."""
        data = super().to_dict()
        data['category'] = self.category.value
        data['date'] = self.date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Create expense from dictionary."""
        if 'category' in data and isinstance(data['category'], str):
            data['category'] = ExpenseCategory(data['category'])
        
        if 'date' in data and isinstance(data['date'], str):
            data['date'] = datetime.fromisoformat(data['date'])
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)

    @classmethod
    def create(cls, team_id: str, amount: float, category: ExpenseCategory, **kwargs) -> 'Expense':
        """Factory method to create an expense."""
        return cls(team_id=team_id, amount=amount, category=category, **kwargs)


# ============================================================================
# BOT MAPPING MODEL
# ============================================================================

@dataclass
class BotMapping(BaseModel):
    """Improved Bot Mapping data model."""
    
    team_name: str = ""
    bot_username: str = ""
    chat_id: str = ""
    bot_token: str = ""
    
    def _validate_model_specific(self):
        """Validate bot mapping-specific fields."""
        if not self.team_name.strip():
            raise ValueError("Team name cannot be empty")
        
        if not self.bot_username.strip():
            raise ValueError("Bot username cannot be empty")
        
        if not self.chat_id.strip():
            raise ValueError("Chat ID cannot be empty")
        
        if not self.bot_token.strip():
            raise ValueError("Bot token cannot be empty")
    
    def get_display_name(self) -> str:
        """Get bot mapping display name."""
        return f"{self.team_name} - {self.bot_username}"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BotMapping':
        """Create bot mapping from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    @classmethod
    def create(cls, team_name: str, bot_username: str, chat_id: str, bot_token: str, **kwargs) -> 'BotMapping':
        """Factory method to create a bot mapping."""
        return cls(
            team_name=team_name,
            bot_username=bot_username,
            chat_id=chat_id,
            bot_token=bot_token,
            **kwargs
        )


# ============================================================================
# MODEL FACTORY
# ============================================================================

class ModelFactory:
    """Factory class for creating models with validation."""
    
    @staticmethod
    def create_player(name: str, phone: str, team_id: str, **kwargs) -> Player:
        """Create a player with validation."""
        return Player.create(name, phone, team_id, **kwargs)
    
    @staticmethod
    def create_team(name: str, description: Optional[str] = None, **kwargs) -> Team:
        """Create a team with validation."""
        return Team.create(name, description, **kwargs)
    
    @staticmethod
    def create_team_member(team_id: str, user_id: str, roles: List[str], **kwargs) -> TeamMember:
        """Create a team member with validation."""
        return TeamMember.create(team_id, user_id, roles, **kwargs)
    
    @staticmethod
    def create_match(team_id: str, opponent: str, date: datetime, **kwargs) -> Match:
        """Create a match with validation."""
        return Match.create(team_id, opponent, date, **kwargs)
    
    @staticmethod
    def create_payment(team_id: str, player_id: str, amount: float, type: PaymentType, **kwargs) -> Payment:
        """Create a payment with validation."""
        return Payment.create(team_id, player_id, amount, type, **kwargs)

    @staticmethod
    def create_expense(team_id: str, amount: float, category: ExpenseCategory, **kwargs) -> Expense:
        """Create an expense with validation."""
        return Expense.create(team_id, amount, category, **kwargs)

    @staticmethod
    def create_bot_mapping(team_name: str, bot_username: str, chat_id: str, bot_token: str, **kwargs) -> BotMapping:
        """Create a bot mapping with validation."""
        return BotMapping.create(team_name, bot_username, chat_id, bot_token, **kwargs) 