#!/usr/bin/env python3
"""
UserPermissions Domain Entity

This module defines the UserPermissions entity for the system infrastructure domain.
UserPermissions represents a user's permissions and roles within a team.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class UserPermissions:
    """
    User Permissions entity representing a user's permissions and roles within a team.
    
    This domain entity encapsulates all user permission data and business logic,
    providing a clean interface for permission operations.
    """

    # Core identification
    telegram_id: int
    team_id: str
    
    # Role information
    roles: List[str]
    chat_access: Dict[str, bool]
    
    # Permission flags
    is_admin: bool = False
    is_player: bool = False
    is_team_member: bool = False
    is_first_user: bool = False
    
    def __post_init__(self):
        """Validate and set defaults after initialization."""
        self._validate()
        self._normalize_data()
    
    def _validate(self):
        """Validate user permissions data."""
        if not isinstance(self.telegram_id, int):
            raise ValueError(f"telegram_id must be an integer, got {type(self.telegram_id)}")
        if not self.team_id:
            raise ValueError("team_id cannot be empty")
        if not isinstance(self.roles, list):
            raise ValueError(f"roles must be a list, got {type(self.roles)}")
        if not isinstance(self.chat_access, dict):
            raise ValueError(f"chat_access must be a dict, got {type(self.chat_access)}")
    
    def _normalize_data(self):
        """Normalize and ensure data consistency."""
        # Ensure roles is a list
        if self.roles is None:
            self.roles = []
        
        # Ensure chat_access is a dict
        if self.chat_access is None:
            self.chat_access = {}
        
        # Derive permission flags from roles if not explicitly set
        if self.roles:
            if not self.is_admin and "admin" in self.roles:
                self.is_admin = True
            if not self.is_player and "player" in self.roles:
                self.is_player = True
            if not self.is_team_member and "team_member" in self.roles:
                self.is_team_member = True
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def has_chat_access(self, chat_type: str) -> bool:
        """Check if user has access to a specific chat type."""
        return self.chat_access.get(chat_type, False)
    
    def add_role(self, role: str) -> None:
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
            # Update permission flags
            if role == "admin":
                self.is_admin = True
            elif role == "player":
                self.is_player = True
            elif role == "team_member":
                self.is_team_member = True
    
    def remove_role(self, role: str) -> None:
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            # Update permission flags
            if role == "admin":
                self.is_admin = "admin" in self.roles
            elif role == "player":
                self.is_player = "player" in self.roles
            elif role == "team_member":
                self.is_team_member = "team_member" in self.roles
    
    def grant_chat_access(self, chat_type: str) -> None:
        """Grant access to a specific chat type."""
        self.chat_access[chat_type] = True
    
    def revoke_chat_access(self, chat_type: str) -> None:
        """Revoke access to a specific chat type."""
        self.chat_access[chat_type] = False
    
    def is_authorized_for_action(self, action: str) -> bool:
        """Check if user is authorized for a specific action."""
        # Admin users can perform any action
        if self.is_admin:
            return True
        
        # Define role-based permissions
        role_permissions = {
            "view_team_info": ["team_member", "player", "admin"],
            "manage_team_members": ["admin"],
            "manage_players": ["admin", "team_member"],
            "view_match_info": ["team_member", "player", "admin"],
            "manage_matches": ["admin", "team_member"],
            "access_leadership_chat": ["admin", "team_member"],
            "access_main_chat": ["admin", "team_member", "player"],
        }
        
        allowed_roles = role_permissions.get(action, [])
        return any(self.has_role(role) for role in allowed_roles)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "telegram_id": self.telegram_id,
            "team_id": self.team_id,
            "roles": self.roles,
            "chat_access": self.chat_access,
            "is_admin": self.is_admin,
            "is_player": self.is_player,
            "is_team_member": self.is_team_member,
            "is_first_user": self.is_first_user,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserPermissions":
        """Create from dictionary."""
        return cls(
            telegram_id=data.get("telegram_id", 0),
            team_id=data.get("team_id", ""),
            roles=data.get("roles", []),
            chat_access=data.get("chat_access", {}),
            is_admin=data.get("is_admin", False),
            is_player=data.get("is_player", False),
            is_team_member=data.get("is_team_member", False),
            is_first_user=data.get("is_first_user", False),
        )
    
    @classmethod
    def create_default(cls, telegram_id: int, team_id: str) -> "UserPermissions":
        """Create default permissions for a new user."""
        return cls(
            telegram_id=telegram_id,
            team_id=team_id,
            roles=[],
            chat_access={},
            is_admin=False,
            is_player=False,
            is_team_member=False,
            is_first_user=False,
        )
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"UserPermissions(telegram_id={self.telegram_id}, team_id={self.team_id}, roles={self.roles})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (f"UserPermissions(telegram_id={self.telegram_id}, team_id='{self.team_id}', "
                f"roles={self.roles}, is_admin={self.is_admin})")