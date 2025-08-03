"""
EntityContext value object for unified context handling across the system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from kickai.core.enums import ChatType
from .identifiers import UserId, TeamId, ChatId


@dataclass(frozen=True)
class UserRegistration:
    """Represents user registration status and roles."""
    
    is_registered: bool
    is_player: bool
    is_team_member: bool
    is_admin: bool = False
    is_leadership: bool = False
    
    def __post_init__(self) -> None:
        # Business rule validation
        if self.is_player and self.is_team_member:
            # A user can be both player and team member (dual role)
            pass
        elif not self.is_registered and (self.is_player or self.is_team_member):
            raise ValueError("User cannot have roles without being registered")
        
        if self.is_admin and not (self.is_player or self.is_team_member):
            raise ValueError("Admin must be either player or team member")
        
        if self.is_leadership and not (self.is_player or self.is_team_member):
            raise ValueError("Leadership must be either player or team member")
    
    @classmethod
    def unregistered(cls) -> UserRegistration:
        """Create unregistered user context."""
        return cls(
            is_registered=False,
            is_player=False,
            is_team_member=False,
            is_admin=False,
            is_leadership=False
        )
    
    @classmethod
    def player_only(cls, is_admin: bool = False, is_leadership: bool = False) -> UserRegistration:
        """Create player-only user context."""
        return cls(
            is_registered=True,
            is_player=True,
            is_team_member=False,
            is_admin=is_admin,
            is_leadership=is_leadership
        )
    
    @classmethod
    def team_member_only(cls, is_admin: bool = False, is_leadership: bool = False) -> UserRegistration:
        """Create team member-only user context."""
        return cls(
            is_registered=True,
            is_player=False,
            is_team_member=True,
            is_admin=is_admin,
            is_leadership=is_leadership
        )
    
    @classmethod
    def dual_role(cls, is_admin: bool = False, is_leadership: bool = False) -> UserRegistration:
        """Create dual role (player and team member) user context."""
        return cls(
            is_registered=True,
            is_player=True,
            is_team_member=True,
            is_admin=is_admin,
            is_leadership=is_leadership
        )
    
    def has_any_role(self) -> bool:
        """Check if user has any role (player or team member)."""
        return self.is_player or self.is_team_member
    
    def primary_role(self) -> str:
        """Get the primary role for context-aware behavior."""
        if self.is_player and self.is_team_member:
            return "dual_role"
        elif self.is_player:
            return "player"
        elif self.is_team_member:
            return "team_member"
        else:
            return "unregistered"


@dataclass(frozen=True)
class EntityContext:
    """
    Unified context object that contains all necessary information for
    processing user requests in the KICKAI system.
    
    This replaces scattered context parameters throughout the codebase.
    """
    
    user_id: UserId
    team_id: TeamId
    chat_id: ChatId
    chat_type: ChatType
    user_registration: UserRegistration
    username: Optional[str] = None
    
    def __post_init__(self) -> None:
        # Validation rules
        if self.chat_type == ChatType.PRIVATE and self.chat_id.is_group_chat():
            raise ValueError("Private chat cannot have negative chat ID")
        
        if self.chat_type in (ChatType.MAIN, ChatType.LEADERSHIP) and self.chat_id.is_private_chat():
            raise ValueError("Group chat types cannot have positive chat ID")
    
    @classmethod
    def create(
        cls,
        user_id: str,
        team_id: str,
        chat_id: str,
        chat_type: ChatType,
        is_registered: bool = False,
        is_player: bool = False,
        is_team_member: bool = False,
        is_admin: bool = False,
        is_leadership: bool = False,
        username: Optional[str] = None,
    ) -> EntityContext:
        """
        Convenience factory method for creating EntityContext.
        
        This method handles the conversion of string parameters to value objects
        and creation of the UserRegistration object.
        """
        user_registration = UserRegistration(
            is_registered=is_registered,
            is_player=is_player,
            is_team_member=is_team_member,
            is_admin=is_admin,
            is_leadership=is_leadership,
        )
        
        return cls(
            user_id=UserId(user_id),
            team_id=TeamId(team_id),
            chat_id=ChatId(chat_id),
            chat_type=chat_type,
            user_registration=user_registration,
            username=username,
        )
    
    def is_leadership_context(self) -> bool:
        """Check if this is a leadership context (leadership chat or user has leadership role)."""
        return (self.chat_type == ChatType.LEADERSHIP or 
                self.user_registration.is_leadership or 
                self.user_registration.is_admin)
    
    def is_main_chat_context(self) -> bool:
        """Check if this is main chat context."""
        return self.chat_type == ChatType.MAIN
    
    def is_private_context(self) -> bool:
        """Check if this is private chat context."""
        return self.chat_type == ChatType.PRIVATE
    
    def effective_role_for_chat(self) -> str:
        """
        Get the effective role for the current chat context.
        
        In main chat, treat dual-role users as players.
        In leadership chat, treat dual-role users as team members.
        """
        if not self.user_registration.has_any_role():
            return "unregistered"
        
        if self.chat_type == ChatType.MAIN:
            # In main chat, prioritize player role
            return "player" if self.user_registration.is_player else "team_member"
        elif self.chat_type == ChatType.LEADERSHIP:
            # In leadership chat, prioritize team member role
            return "team_member" if self.user_registration.is_team_member else "player"
        else:
            # Private chat - use actual roles
            return self.user_registration.primary_role()
    
    def can_access_leadership_features(self) -> bool:
        """Check if user can access leadership-only features."""
        return (self.user_registration.is_leadership or 
                self.user_registration.is_admin or
                self.chat_type == ChatType.LEADERSHIP)
    
    def can_access_admin_features(self) -> bool:
        """Check if user can access admin-only features."""
        return self.user_registration.is_admin
    
    def with_updated_registration(self, user_registration: UserRegistration) -> EntityContext:
        """Create new EntityContext with updated user registration."""
        return EntityContext(
            user_id=self.user_id,
            team_id=self.team_id,
            chat_id=self.chat_id,
            chat_type=self.chat_type,
            user_registration=user_registration,
            username=self.username,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/logging."""
        return {
            "user_id": str(self.user_id),
            "team_id": str(self.team_id),
            "chat_id": str(self.chat_id),
            "chat_type": self.chat_type.value,
            "is_registered": self.user_registration.is_registered,
            "is_player": self.user_registration.is_player,
            "is_team_member": self.user_registration.is_team_member,
            "is_admin": self.user_registration.is_admin,
            "is_leadership": self.user_registration.is_leadership,
            "username": self.username,
            "effective_role": self.effective_role_for_chat(),
        }