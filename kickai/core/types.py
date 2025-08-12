#!/usr/bin/env python3
"""
Centralized type definitions for the KICKAI system.

This module provides standardized data classes used across the entire system
to ensure consistency and prevent type mismatches.
"""

from dataclasses import dataclass, field
from typing import Any

from kickai.core.enums import ChatType


@dataclass
class AgentResponse:
    """
    Standardized agent response used across the entire system.

    This is the single source of truth for agent responses to ensure
    consistency between all components.
    """
    success: bool
    message: str
    error: str | None = None
    agent_type: str | None = None
    confidence: float = 1.0
    metadata: dict[str, Any] | None = None
    needs_contact_button: bool = False


@dataclass
class TelegramMessage:
    """
    Standardized Telegram message representation.

    Used consistently across all message handling components
    to ensure type safety and proper message routing.

    Note: telegram_id uses Telegram's native integer type for user IDs
    which is consistent with Telegram's API specification.
    """
    telegram_id: int  # Native Telegram integer user ID
    text: str
    chat_id: str
    chat_type: ChatType
    team_id: str | None = None
    username: str | None = None
    name: str | None = None
    raw_update: Any | None = None
    contact_phone: str | None = None
    contact_user_id: int | None = None  # Also integer for consistency


@dataclass
class UserFlowDecision:
    """
    User flow decision for routing messages.

    Determines whether a user is registered or unregistered
    and guides the appropriate handling flow.
    """
    flow_type: str  # "REGISTERED_USER" or "UNREGISTERED_USER"
    confidence: float
    metadata: dict[str, Any] | None = None


@dataclass
class IntentResult:
    """
    Intent classification result for message processing.

    Used by the agentic message router to determine
    how to handle incoming messages.
    """
    intent: str
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)


# Constants for user flow types
class UserFlowType:
    """Constants for user flow types."""
    REGISTERED_USER = "REGISTERED_USER"
    UNREGISTERED_USER = "UNREGISTERED_USER"


# Constants for registration types
class RegistrationType:
    """Constants for registration types."""
    PLAYER = "player"
    TEAM_MEMBER = "team_member"
    AMBIGUOUS = "ambiguous"
    ERROR = "error"
