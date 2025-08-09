"""
Pydantic context models for CrewAI native context passing.

This module defines the context models used throughout the system to ensure
proper validation and type safety when passing context to CrewAI tools.
"""

from datetime import datetime
from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel, Field, validator


class BaseContext(BaseModel):
    """Base context model for all operations."""

    team_id: str = Field(..., description="Team identifier")
    user_id: str = Field(..., description="User identifier (telegram ID)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Context timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("team_id", "user_id")
    def validate_required_fields(cls, v):
        """Validate that required fields are not empty."""
        if not v or not str(v).strip():
            raise ValueError("Field cannot be empty")
        return str(v).strip()

    @validator("team_id")
    def validate_team_id(cls, v):
        """Validate team ID format."""
        if len(v) > 20:
            raise ValueError("Team ID must be 20 characters or less")
        return v

    @validator("user_id")
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if len(v) > 20:
            raise ValueError("User ID must be 20 characters or less")
        return v


class PlayerContext(BaseContext):
    """Context for player-related operations."""

    player_id: Optional[str] = Field(None, description="Player identifier")
    phone: Optional[str] = Field(None, description="Phone number")
    position: Optional[str] = Field(None, description="Player position")

    @validator("player_id")
    def validate_player_id(cls, v):
        """Validate player ID if provided."""
        if v is not None and len(v) > 20:
            raise ValueError("Player ID must be 20 characters or less")
        return v

    @validator("phone")
    def validate_phone(cls, v):
        """Validate phone number if provided using phonenumbers library."""
        if v is not None:
            # Use phonenumbers library for proper validation
            from kickai.utils.phone_utils import is_valid_phone

            if not is_valid_phone(v.strip()):
                raise ValueError("Invalid phone number format")
        return v


class MatchContext(BaseContext):
    """Context for match-related operations."""

    match_id: Optional[str] = Field(None, description="Match identifier")
    match_date: Optional[datetime] = Field(None, description="Match date")
    venue: Optional[str] = Field(None, description="Match venue")

    @validator("match_id")
    def validate_match_id(cls, v):
        """Validate match ID if provided."""
        if v is not None and len(v) > 20:
            raise ValueError("Match ID must be 20 characters or less")
        return v


class PaymentContext(BaseContext):
    """Context for payment-related operations."""

    amount: Optional[float] = Field(None, description="Payment amount")
    currency: str = Field(default="GBP", description="Currency code")
    payment_type: Optional[str] = Field(None, description="Type of payment")

    @validator("amount")
    def validate_amount(cls, v):
        """Validate payment amount if provided."""
        if v is not None and v <= 0:
            raise ValueError("Payment amount must be positive")
        return v

    @validator("currency")
    def validate_currency(cls, v):
        """Validate currency code."""
        if len(v) != 3:
            raise ValueError("Currency code must be 3 characters")
        return v.upper()


class AttendanceContext(BaseContext):
    """Context for attendance-related operations."""

    match_id: Optional[str] = Field(None, description="Match identifier")
    attendance_status: Optional[str] = Field(None, description="Attendance status")

    @validator("attendance_status")
    def validate_attendance_status(cls, v):
        """Validate attendance status if provided."""
        if v is not None:
            valid_statuses = ["present", "absent", "late", "pending"]
            if v.lower() not in valid_statuses:
                raise ValueError(f"Invalid attendance status. Must be one of: {valid_statuses}")
        return v


class CommunicationContext(BaseContext):
    """Context for communication-related operations."""

    message_type: Optional[str] = Field(None, description="Type of message")
    recipient_group: Optional[str] = Field(None, description="Recipient group")

    @validator("message_type")
    def validate_message_type(cls, v):
        """Validate message type if provided."""
        if v is not None:
            valid_types = ["announcement", "reminder", "notification", "alert"]
            if v.lower() not in valid_types:
                raise ValueError(f"Invalid message type. Must be one of: {valid_types}")
        return v


# Context factory for creating appropriate context types
def create_context(context_type: str, **kwargs) -> BaseContext:
    """
    Factory function to create appropriate context objects.

    Args:
        context_type: Type of context to create
        **kwargs: Context data

    Returns:
        Appropriate context object

    Raises:
        ValueError: If context_type is not supported
    """
    context_map = {
        "player": PlayerContext,
        "match": MatchContext,
        "payment": PaymentContext,
        "attendance": AttendanceContext,
        "communication": CommunicationContext,
        "base": BaseContext,
    }

    if context_type not in context_map:
        raise ValueError(f"Unsupported context type: {context_type}")

    context_class = context_map[context_type]
    return context_class(**kwargs)


def validate_context_data(context_data: dict[str, Any], context_type: str = "base") -> bool:
    """
    Validate context data without creating an object.

    Args:
        context_data: Data to validate
        context_type: Type of context to validate against

    Returns:
        True if valid, False otherwise
    """
    try:
        create_context(context_type, **context_data)
        return True
    except Exception as e:
        logger.warning(f"Context validation failed: {e}")
        return False
