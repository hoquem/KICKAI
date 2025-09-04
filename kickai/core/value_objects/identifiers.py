"""
Core identifier value objects for KICKAI.

These value objects provide type safety for entity identifiers and prevent
mixing different types of IDs accidentally.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """Represents a user identifier with validation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("UserId cannot be empty")
        if not self.value.strip():
            raise ValueError("UserId cannot be only whitespace")
        if len(self.value) > 100:
            raise ValueError("UserId cannot exceed 100 characters")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"UserId('{self.value}')"


@dataclass(frozen=True)
class TeamId:
    """Represents a team identifier with validation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("TeamId cannot be empty")
        if not self.value.strip():
            raise ValueError("TeamId cannot be only whitespace")
        if len(self.value) > 50:
            raise ValueError("TeamId cannot exceed 50 characters")
        # Team IDs should be alphanumeric with underscores/hyphens
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.value):
            raise ValueError(
                "TeamId must contain only alphanumeric characters, underscores, and hyphens"
            )

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"TeamId('{self.value}')"


@dataclass(frozen=True)
class ChatId:
    """Represents a chat identifier with validation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("ChatId cannot be empty")
        if not self.value.strip():
            raise ValueError("ChatId cannot be only whitespace")
        # Chat IDs can be negative for group chats
        try:
            int(self.value)
        except ValueError:
            raise ValueError("ChatId must be a valid integer") from None

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"ChatId('{self.value}')"

    @property
    def as_int(self) -> int:
        """Return the chat ID as an integer."""
        return int(self.value)

    def is_group_chat(self) -> bool:
        """Check if this is a group chat (negative ID)."""
        return self.as_int < 0

    def is_private_chat(self) -> bool:
        """Check if this is a private chat (positive ID)."""
        return self.as_int > 0


@dataclass(frozen=True)
class PlayerId:
    """Represents a player identifier with validation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("PlayerId cannot be empty")
        if not self.value.strip():
            raise ValueError("PlayerId cannot be only whitespace")
        if len(self.value) > 50:
            raise ValueError("PlayerId cannot exceed 50 characters")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"PlayerId('{self.value}')"


@dataclass(frozen=True)
class MessageId:
    """Represents a message identifier with validation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("MessageId cannot be empty")
        if not self.value.strip():
            raise ValueError("MessageId cannot be only whitespace")
        # Message IDs should be numeric for Telegram
        try:
            int(self.value)
        except ValueError:
            raise ValueError("MessageId must be a valid integer") from None

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"MessageId('{self.value}')"

    @property
    def as_int(self) -> int:
        """Return the message ID as an integer."""
        return int(self.value)
