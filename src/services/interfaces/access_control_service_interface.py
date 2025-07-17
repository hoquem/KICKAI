from abc import ABC, abstractmethod
from typing import List
from database.models_improved import TeamMember

class IAccessControlService(ABC):
    """Abstract base class for access control service."""
    
    @abstractmethod
    def has_permission(self, member: TeamMember, permission: str) -> bool:
        """Check if a team member has a specific permission."""
        pass
    
    @abstractmethod
    def require_permission(self, member: TeamMember, permission: str) -> None:
        """Require a specific permission, raise AccessDeniedError if not granted."""
        pass
    
    @abstractmethod
    def get_accessible_chats(self, member: TeamMember) -> List[str]:
        """Get list of chat types the member has access to."""
        pass
    
    @abstractmethod
    def is_leadership_member(self, member: TeamMember) -> bool:
        """Check if a member has any leadership role."""
        pass
    
    @abstractmethod
    def can_manage_team(self, member: TeamMember) -> bool:
        """Check if a member can manage team settings."""
        pass
    
    @abstractmethod
    def can_manage_players(self, member: TeamMember) -> bool:
        """Check if a member can manage players."""
        pass
    
    @abstractmethod
    def can_view_sensitive_data(self, member: TeamMember) -> bool:
        """Check if a member can view sensitive team data."""
        pass
    
    @abstractmethod
    def validate_role_assignment(self, current_member: TeamMember, target_role: str) -> bool:
        """Validate if a member can assign a specific role."""
        pass
    
    @abstractmethod
    def is_leadership_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if a chat ID corresponds to the leadership chat for a team."""
        pass
    
    @abstractmethod
    def is_main_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if a chat ID corresponds to the main chat for a team."""
        pass

# Backward compatibility alias
AccessControlServiceInterface = IAccessControlService 