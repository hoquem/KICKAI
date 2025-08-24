#!/usr/bin/env python3
"""
Standardized Context Types for KICKAI

This module provides standardized context objects that ensure consistent
context passing across the entire system to agents and tools.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Set, List

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
    roles: List[str] = field(default_factory=list)
    permissions: List[PermissionLevel] = field(default_factory=list)


@dataclass
class StandardizedContext:
    """
    Standardized context object for consistent context passing across the system.

    This ensures all agents and tools have access to the same context information
    regardless of how they are called.
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

        # For user registration status, require explicit values (no defaults)
        if "is_registered" not in data:
            raise ValueError("is_registered field is required and must be explicitly set")
        if "is_player" not in data:
            raise ValueError("is_player field is required and must be explicitly set")
        if "is_team_member" not in data:
            raise ValueError("is_team_member field is required and must be explicitly set")

        # Only provide defaults for non-critical fields
        defaults = {
            "telegram_name": data.get("telegram_name", ""),
            "source": ContextSource(data.get("source", ContextSource.TELEGRAM_MESSAGE.value)),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "metadata": data.get("metadata", {}),
        }

        # Merge provided data with defaults
        merged_data = {**defaults, **data}

        return cls(**merged_data)

    def get_user_display_name(self) -> str:
        """Get the best available user display name."""
        if self.telegram_name:
            return self.telegram_name
        elif self.username:
            return self.username
        else:
            return f"User {self.telegram_id}"

    def is_leadership_chat(self) -> bool:
        """Check if this is a leadership chat."""
        return self.chat_type.lower() == "leadership_chat"

    def is_main_chat(self) -> bool:
        """Check if this is a main chat."""
        return self.chat_type.lower() == "main_chat"

    def has_permission(self, permission: PermissionLevel) -> bool:
        """Check if user has a specific permission."""
        if not self.user_permissions:
            return False
        return permission in self.user_permissions.permissions

    def get_context_summary(self) -> str:
        """Get a human-readable context summary."""
        return (
            f"User: {self.get_user_display_name()} "
            f"({self.telegram_id}) | "
            f"Team: {self.team_id} | "
            f"Chat: {self.chat_type} | "
            f"Registered: {self.is_registered}"
        )


def create_context_from_telegram_message(
    telegram_id: int,
    team_id: str,
    chat_id: str,
    chat_type: ChatType,
    message_text: str,
    username: str,
    telegram_name: str = "",
    **kwargs,
) -> StandardizedContext:
    """Create standardized context from Telegram message data."""
    return StandardizedContext(
        telegram_id=int(telegram_id),
        team_id=team_id,
        chat_id=chat_id,
        chat_type=chat_type.value if isinstance(chat_type, ChatType) else chat_type,
        message_text=message_text,
        username=username,
        telegram_name=telegram_name,
        source=ContextSource.TELEGRAM_MESSAGE,
        **kwargs,
    )


def create_context_from_command(
    telegram_id: int,
    team_id: str,
    chat_id: str,
    chat_type: ChatType,
    command_text: str,
    username: str,
    telegram_name: str = "",
    **kwargs,
) -> StandardizedContext:
    """Create standardized context from command data."""
    return StandardizedContext(
        telegram_id=int(telegram_id),
        team_id=team_id,
        chat_id=chat_id,
        chat_type=chat_type.value if isinstance(chat_type, ChatType) else chat_type,
        message_text=command_text,
        username=username,
        telegram_name=telegram_name,
        source=ContextSource.COMMAND,
        **kwargs,
    )


def enhance_context_with_user_data(
    context: StandardizedContext,
    user_permissions: Optional[UserPermissions] = None,
    player_data: Optional[Dict[str, Any]] = None,
    team_member_data: Optional[Dict[str, Any]] = None,
) -> StandardizedContext:
    """Enhance context with additional user data."""
    context.user_permissions = user_permissions
    context.player_data = player_data
    context.team_member_data = team_member_data

    # Update boolean flags
    if user_permissions:
        context.is_player = user_permissions.is_player
        context.is_team_member = user_permissions.is_team_member
        context.is_registered = context.is_player or context.is_team_member

    return context
