from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class TeamMember:
    """Team member entity representing a user's membership in a team."""
    id: Optional[str] = None
    user_id: str = ""
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    team_id: str = ""
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    chat_access: Dict[str, bool] = field(default_factory=dict)
    created_at: Optional[datetime] = None 
    joined_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the team member after initialization."""
        self._validate()
        # Set default timestamps if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.joined_at is None:
            self.joined_at = datetime.utcnow()
        # Set default chat access for players
        if "player" in self.roles and not self.chat_access:
            self.chat_access = {"main_chat": True, "leadership_chat": False}
    
    def _validate(self):
        """Validate team member data."""
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.roles:
            raise ValueError("Team member must have at least one role")
        
        # Validate roles
        valid_roles = ["player", "captain", "vice_captain", "admin", "manager"]
        invalid_roles = [role for role in self.roles if role not in valid_roles]
        if invalid_roles:
            raise ValueError(f"Invalid roles: {invalid_roles}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'telegram_id': self.telegram_id,
            'telegram_username': self.telegram_username,
            'team_id': self.team_id,
            'roles': self.roles,
            'permissions': self.permissions,
            'chat_access': self.chat_access,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TeamMember':
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            telegram_id=data.get('telegram_id'),
            telegram_username=data.get('telegram_username'),
            team_id=data.get('team_id', ''),
            roles=data.get('roles', []),
            permissions=data.get('permissions', []),
            chat_access=data.get('chat_access', {}),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            joined_at=datetime.fromisoformat(data['joined_at']) if data.get('joined_at') else None
        )
    
    def has_role(self, role: str) -> bool:
        """Check if member has a specific role."""
        return role in self.roles
    
    def has_permission(self, permission: str) -> bool:
        """Check if member has a specific permission."""
        return permission in self.permissions
    
    def can_access_chat(self, chat_type: str) -> bool:
        """Check if member can access a specific chat type."""
        return self.chat_access.get(chat_type, False)
    
    @classmethod
    def create(cls, team_id: str, user_id: str, roles: List[str]) -> 'TeamMember':
        """Create a new team member."""
        return cls(
            team_id=team_id,
            user_id=user_id,
            roles=roles,
            created_at=datetime.utcnow(),
            joined_at=datetime.utcnow()
        )
    
    def has_any_leadership_role(self) -> bool:
        """Check if member has any leadership role."""
        leadership_roles = ["captain", "vice_captain", "admin", "manager"]
        return any(role in self.roles for role in leadership_roles)
    
    def is_player(self) -> bool:
        """Check if member is a player."""
        return "player" in self.roles
    
    def is_admin(self) -> bool:
        """Check if member is an admin."""
        return "admin" in self.roles
    
    def is_captain(self) -> bool:
        """Check if member is a captain."""
        return "captain" in self.roles
    
    def get_display_name(self) -> str:
        """Get display name for the member."""
        base_name = ""
        if self.telegram_username:
            base_name = f"@{self.telegram_username}"
        elif self.telegram_id:
            base_name = f"User {self.telegram_id}"
        else:
            base_name = f"User {self.user_id}"
        
        # Add role information
        role_names = []
        if "player" in self.roles:
            role_names.append("player")
        if "captain" in self.roles:
            role_names.append("captain")
        if "admin" in self.roles:
            role_names.append("admin")
        
        if role_names:
            return f"{base_name} ({', '.join(role_names)})"
        else:
            return base_name 