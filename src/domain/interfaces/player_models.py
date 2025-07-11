"""
Domain interfaces for player models.

These interfaces define player-related data structures without depending
on the infrastructure layer.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


class PlayerPosition(Enum):
    """Player position enumeration."""
    ANY = "any"
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    UTILITY = "utility"


class PlayerRole(Enum):
    """Player role enumeration."""
    PLAYER = "player"
    CAPTAIN = "captain"
    VICE_CAPTAIN = "vice_captain"
    COACH = "coach"
    MANAGER = "manager"


class OnboardingStatus(Enum):
    """Onboarding status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Player:
    """Player data structure."""
    id: str
    player_id: str
    name: str
    phone: str
    position: PlayerPosition
    role: PlayerRole
    team_id: str
    status: str
    onboarding_status: OnboardingStatus
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    fa_registered: bool = False
    fa_eligible: bool = False
    is_approved: bool = False
    is_injured: bool = False
    is_suspended: bool = False
    emergency_contact: Optional[str] = None
    date_of_birth: Optional[str] = None
    invite_link: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None 