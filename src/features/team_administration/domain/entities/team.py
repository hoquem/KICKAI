from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class TeamStatus(Enum):
    """Team status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

# TeamMember class moved to separate file: team_member.py

@dataclass
class Team:
    name: str
    status: TeamStatus = TeamStatus.ACTIVE
    description: str = ""
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    fa_team_url: Optional[str] = None
    fa_fixtures_url: Optional[str] = None
    id: Optional[str] = None
    # Explicit bot config fields
    bot_id: Optional[str] = None
    bot_token: Optional[str] = None
    main_chat_id: Optional[str] = None
    leadership_chat_id: Optional[str] = None 