#!/usr/bin/env python3
"""
Standardized Context Types for KICKAI - Single Source of Truth

This module provides the single source of truth for context objects that ensure consistent
context passing across the entire system to agents and tools.

All context operations should use this module to maintain consistency.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Set, List

from loguru import logger
from kickai.core.enums import ChatType, PermissionLevel


class ContextSource(Enum):
    """Source of the context."""

    TELEGRAM_MESSAGE = "telegram_message"
    COMMAND = "command"
    NATURAL_LANGUAGE = "natural_language"
    SYSTEM = "system"


@dataclass
class UserPermissions:
    """User permissions information."""

    is_player: bool = False
    is_team_member: bool = False
    is_admin: bool = False
    is_leadership: bool = False
    permissions: List[PermissionLevel] = field(default_factory=list)

    def __post_init__(self):
        """Validate permissions consistency."""
        if self.is_admin and not (self.is_player or self.is_team_member):
            raise ValueError("Admin must be either player or team member")
        if self.is_leadership and not (self.is_player or self.is_team_member):
            raise ValueError("Leadership must be either player or team member")


@dataclass
class StandardizedContext:
    """
    Standardized context object for consistent context passing across the system.

    This is the SINGLE SOURCE OF TRUTH for all context operations in the KICKAI system.
    All agents and tools should use this context object to ensure consistency.

    Features:
    - Comprehensive validation
    - Factory methods for common use cases
    - Serialization/deserialization support
    - Permission handling
    - Metadata support
    """

    # Core fields (always present)
    telegram_id: int
    team_id: str
    chat_id: str
    chat_type: str
    message_text: str
    username: str
    telegram_name: str

    # Optional fields (populated when available)
    user_permissions: Optional[UserPermissions] = None
    player_data: Optional[Dict[str, Any]] = None
    team_member_data: Optional[Dict[str, Any]] = None
    is_registered: bool = False
    is_player: bool = False
    is_team_member: bool = False

    # Context metadata
    source: ContextSource = ContextSource.TELEGRAM_MESSAGE
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Ensure chat_type is a string
        if isinstance(self.chat_type, ChatType):
            self.chat_type = self.chat_type.value

        # Set boolean flags based on user_permissions if available
        if self.user_permissions:
            self.is_player = self.user_permissions.is_player
            self.is_team_member = self.user_permissions.is_team_member
            self.is_registered = self.is_player or self.is_team_member

        # Validate core fields
        self._validate_core_fields()

    def _validate_core_fields(self):
        """Validate that all core fields are properly set."""
        if not self.telegram_id:
            raise ValueError("telegram_id is required")
        if not self.team_id or not str(self.team_id).strip():
            raise ValueError("team_id is required and cannot be empty")
        if not self.chat_id or not str(self.chat_id).strip():
            raise ValueError("chat_id is required and cannot be empty")
        if not self.chat_type or not str(self.chat_type).strip():
            raise ValueError("chat_type is required and cannot be empty")
        if not self.message_text:
            self.message_text = ""  # Allow empty message text
        if not self.username:
            self.username = "unknown"
        if not self.telegram_name:
            self.telegram_name = self.username

    @classmethod
    def create_from_telegram_message(
        cls,
        telegram_id: int,
        team_id: str,
        chat_id: str,
        chat_type: str,
        message_text: str,
        username: str,
        telegram_name: str,
        is_player: bool = False,
        is_team_member: bool = False,
        is_admin: bool = False,
        is_leadership: bool = False,
        **kwargs
    ) -> "StandardizedContext":
        """
        Factory method to create context from Telegram message data.
        
        This is the primary method for creating context from Telegram messages.
        """
        # Create user permissions
        user_permissions = UserPermissions(
            is_player=is_player,
            is_team_member=is_team_member,
            is_admin=is_admin,
            is_leadership=is_leadership
        )

        return cls(
            telegram_id=telegram_id,
            team_id=team_id,
            chat_id=chat_id,
            chat_type=chat_type,
            message_text=message_text,
            username=username,
            telegram_name=telegram_name,
            user_permissions=user_permissions,
            source=ContextSource.TELEGRAM_MESSAGE,
            **kwargs
        )

    @classmethod
    def create_from_command(
        cls,
        telegram_id: int,
        team_id: str,
        chat_id: str,
        chat_type: str,
        command: str,
        username: str,
        telegram_name: str,
        is_player: bool = False,
        is_team_member: bool = False,
        is_admin: bool = False,
        is_leadership: bool = False,
        **kwargs
    ) -> "StandardizedContext":
        """
        Factory method to create context from command data.
        """
        user_permissions = UserPermissions(
            is_player=is_player,
            is_team_member=is_team_member,
            is_admin=is_admin,
            is_leadership=is_leadership
        )

        return cls(
            telegram_id=telegram_id,
            team_id=team_id,
            chat_id=chat_id,
            chat_type=chat_type,
            message_text=command,
            username=username,
            telegram_name=telegram_name,
            user_permissions=user_permissions,
            source=ContextSource.COMMAND,
            **kwargs
        )

    @classmethod
    def create_system_context(
        cls,
        team_id: str,
        operation: str,
        **kwargs
    ) -> "StandardizedContext":
        """
        Factory method to create system-level context.
        """
        return cls(
            telegram_id=0,  # System context
            team_id=team_id,
            chat_id="system",
            chat_type="system",
            message_text=operation,
            username="system",
            telegram_name="system",
            source=ContextSource.SYSTEM,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "telegram_id": self.telegram_id,
            "team_id": self.team_id,
            "chat_id": self.chat_id,
            "chat_type": self.chat_type,
            "message_text": self.message_text,
            "username": self.username,
            "telegram_name": self.telegram_name,
            "is_registered": self.is_registered,
            "is_player": self.is_player,
            "is_team_member": self.is_team_member,
            "source": self.source.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "user_permissions": {
                "is_player": self.user_permissions.is_player if self.user_permissions else False,
                "is_team_member": self.user_permissions.is_team_member if self.user_permissions else False,
                "is_admin": self.user_permissions.is_admin if self.user_permissions else False,
                "is_leadership": self.user_permissions.is_leadership if self.user_permissions else False,
            } if self.user_permissions else None,
            "player_data": self.player_data,
            "team_member_data": self.team_member_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StandardizedContext":
        """Create context from dictionary with validation of critical fields."""
        # Validate that critical fields are present
        required_fields = ["telegram_id", "team_id", "chat_id", "chat_type", "message_text", "username"]
        missing_fields = [
            field for field in required_fields if field not in data or not data[field]
        ]

        if missing_fields:
            raise ValueError(f"Missing required fields for StandardizedContext: {missing_fields}")

        # Recreate user permissions if present
        user_permissions = None
        if data.get("user_permissions"):
            user_permissions = UserPermissions(
                is_player=data["user_permissions"].get("is_player", False),
                is_team_member=data["user_permissions"].get("is_team_member", False),
                is_admin=data["user_permissions"].get("is_admin", False),
                is_leadership=data["user_permissions"].get("is_leadership", False),
            )

        # Create context
        return cls(
            telegram_id=data["telegram_id"],
            team_id=data["team_id"],
            chat_id=data["chat_id"],
            chat_type=data["chat_type"],
            message_text=data["message_text"],
            username=data["username"],
            telegram_name=data.get("telegram_name", data["username"]),
            user_permissions=user_permissions,
            player_data=data.get("player_data"),
            team_member_data=data.get("team_member_data"),
            is_registered=data.get("is_registered", False),
            is_player=data.get("is_player", False),
            is_team_member=data.get("is_team_member", False),
            source=ContextSource(data.get("source", "telegram_message")),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )

    def validate_for_tool(self, tool_name: str) -> bool:
        """
        Validate context for tool execution.
        
        Args:
            tool_name: Name of the tool for logging
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self._validate_core_fields()
            logger.debug(f"✅ Context validation passed for {tool_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Context validation failed for {tool_name}: {e}")
            return False

    def get_context_summary(self) -> str:
        """Get a human-readable summary of the context."""
        return (
            f"User: {self.username} (ID: {self.telegram_id}) | "
            f"Team: {self.team_id} | "
            f"Chat: {self.chat_type} ({self.chat_id}) | "
            f"Registered: {self.is_registered} | "
            f"Player: {self.is_player} | "
            f"Team Member: {self.is_team_member}"
        )


# Global context validator for system-wide use
def validate_context_data(context_data: Dict[str, Any], context_type: str = "standardized") -> bool:
    """
    Validate context data without creating an object.
    
    Args:
        context_data: Data to validate
        context_type: Type of context to validate against
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if context_type == "standardized":
            StandardizedContext.from_dict(context_data)
        else:
            logger.warning(f"Unknown context type: {context_type}")
            return False
        return True
    except Exception as e:
        logger.warning(f"Context validation failed: {e}")
        return False


def create_safe_context_fallback(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a safe context fallback when validation fails."""
    return {
        "telegram_id": context_data.get("telegram_id", 0),
        "team_id": context_data.get("team_id", "unknown"),
        "chat_id": context_data.get("chat_id", "unknown"),
        "chat_type": context_data.get("chat_type", "unknown"),
        "message_text": context_data.get("message_text", ""),
        "username": context_data.get("username", "unknown"),
        "telegram_name": context_data.get("telegram_name", "unknown"),
        "is_registered": False,
        "is_player": False,
        "is_team_member": False,
        "source": "system",
        "timestamp": datetime.now().isoformat(),
        "metadata": context_data.get("metadata", {}),
    }


# Backward compatibility functions
def create_context_from_telegram_message(
    telegram_id: int,
    team_id: str,
    chat_id: str,
    chat_type: str,
    message_text: str,
    username: str,
    telegram_name: str = "",
    **kwargs
) -> StandardizedContext:
    """
    Create standardized context from Telegram message data.
    
    This function provides backward compatibility with existing code.
    """
    return StandardizedContext.create_from_telegram_message(
        telegram_id=telegram_id,
        team_id=team_id,
        chat_id=chat_id,
        chat_type=chat_type,
        message_text=message_text,
        username=username,
        telegram_name=telegram_name,
        **kwargs
    )


def create_context_from_command(
    telegram_id: int,
    team_id: str,
    chat_id: str,
    chat_type: str,
    command_text: str,
    username: str,
    telegram_name: str = "",
    **kwargs
) -> StandardizedContext:
    """
    Create standardized context from command data.
    
    This function provides backward compatibility with existing code.
    """
    return StandardizedContext.create_from_command(
        telegram_id=telegram_id,
        team_id=team_id,
        chat_id=chat_id,
        chat_type=chat_type,
        command=command_text,
        username=username,
        telegram_name=telegram_name,
        **kwargs
    )
