from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from kickai.core.enums import TeamStatus

# TeamMember class moved to separate file: team_member.py


@dataclass
class Team:
    name: str
    status: TeamStatus = TeamStatus.ACTIVE
    description: str = ""
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None
    settings: dict[str, Any] = field(default_factory=dict)
    fa_team_url: str | None = None
    fa_fixtures_url: str | None = None
    id: str | None = None

    # Bot configuration - SINGLE SOURCE OF TRUTH
    # These fields are the authoritative source for bot configuration
    # The settings dict should NOT contain duplicate bot config
    bot_id: str | None = None
    bot_token: str | None = None
    main_chat_id: str | None = None
    leadership_chat_id: str | None = None

    def __post_init__(self):
        """Ensure data consistency after initialization."""
        # Bot configuration is now stored in explicit fields only
        pass

    def get_bot_config(self) -> dict[str, Any]:
        """Get bot configuration as a dictionary."""
        return {
            "bot_id": self.bot_id,
            "bot_token": self.bot_token,
            "main_chat_id": self.main_chat_id,
            "leadership_chat_id": self.leadership_chat_id,
        }

    def set_bot_config(
        self,
        bot_id: str | None = None,
        bot_token: str | None = None,
        main_chat_id: str | None = None,
        leadership_chat_id: str | None = None,
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
