from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class TeamMember:
    id: str
    user_id: str
    telegram_id: Optional[str]
    team_id: str
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None 