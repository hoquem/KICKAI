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
    
    # Bot configuration - SINGLE SOURCE OF TRUTH
    # These fields are the authoritative source for bot configuration
    # The settings dict should NOT contain duplicate bot config
    bot_id: Optional[str] = None
    bot_token: Optional[str] = None
    main_chat_id: Optional[str] = None
    leadership_chat_id: Optional[str] = None
    
    def __post_init__(self):
        """Ensure data consistency after initialization."""
        self._ensure_bot_config_consistency()
    
    def _ensure_bot_config_consistency(self):
        """Ensure bot configuration is only in explicit fields, not in settings."""
        # Remove any bot config from settings to avoid duplication
        bot_config_keys = ['bot_id', 'bot_token', 'main_chat_id', 'leadership_chat_id']
        for key in bot_config_keys:
            if key in self.settings:
                # If explicit field is None, populate from settings
                if getattr(self, key) is None:
                    setattr(self, key, self.settings[key])
                # Remove from settings to avoid duplication
                del self.settings[key]
    
    def get_bot_config(self) -> Dict[str, Any]:
        """Get bot configuration as a dictionary."""
        return {
            'bot_id': self.bot_id,
            'bot_token': self.bot_token,
            'main_chat_id': self.main_chat_id,
            'leadership_chat_id': self.leadership_chat_id
        }
    
    def set_bot_config(self, bot_id: str = None, bot_token: str = None, 
                      main_chat_id: str = None, leadership_chat_id: str = None):
        """Set bot configuration, ensuring consistency."""
        if bot_id is not None:
            self.bot_id = bot_id
        if bot_token is not None:
            self.bot_token = bot_token
        if main_chat_id is not None:
            self.main_chat_id = main_chat_id
        if leadership_chat_id is not None:
            self.leadership_chat_id = leadership_chat_id
        
        # Ensure settings doesn't contain duplicate bot config
        self._ensure_bot_config_consistency() 