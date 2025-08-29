from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Set, Dict

from kickai.core.enums import TeamStatus
from .team_member import TeamMember  # re-export compatibility for tests

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

    # Bot configuration - SINGLE SOURCE OF TRUTH
    # These fields are the authoritative source for bot configuration
    # The settings dict should NOT contain duplicate bot config
    bot_id: Optional[str] = None
    bot_token: Optional[str] = None
    main_chat_id: Optional[str] = None
    leadership_chat_id: Optional[str] = None

    def _post_init_(self):
        """Ensure data consistency after initialization."""
        # Bot configuration is now stored in explicit fields only
        pass

    def get_bot_config(self) -> Dict[str, Any]:
        """Get bot configuration as a dictionary."""
        return {
            "bot_id": self.bot_id,
            "bot_token": self.bot_token,
            "main_chat_id": self.main_chat_id,
            "leadership_chat_id": self.leadership_chat_id,
        }

    def set_bot_config(
        self,
        bot_id: str = None,
        bot_token: str = None,
        main_chat_id: str = None,
        leadership_chat_id: str = None,
    ):
        """Set bot configuration."""
        if bot_id is not None:
            self.bot_id = bot_id
        if bot_token is not None:
            self.bot_token = bot_token
        if main_chat_id is not None:
            self.main_chat_id = main_chat_id
        if leadership_chat_id is not None:
            self.leadership_chat_id = leadership_chat_id
