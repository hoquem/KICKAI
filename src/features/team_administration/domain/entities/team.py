from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum

class TeamStatus(Enum):
    """Team status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

@dataclass
class TeamMember:
    """Team member entity."""
    team_id: str
    user_id: str
    telegram_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    chat_access: Dict[str, bool] = field(default_factory=dict)
    joined_at: Optional[str] = None

@dataclass
class Team:
    id: str
    name: str
    description: Optional[str] = None
    status: str = "active"
    settings: Dict[str, Any] = field(default_factory=dict)
    fa_team_url: Optional[str] = None
    fa_fixtures_url: Optional[str] = None 