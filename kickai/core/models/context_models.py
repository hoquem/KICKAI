"""
Pydantic context models for CrewAI native context passing.

This module defines the context models used throughout the system to ensure
proper validation and type safety when passing context to CrewAI tools.
"""

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, validator


class BaseContext(BaseModel):
    """Base context model for all operations."""

    team_id: str = Field(..., description="Team identifier")
    telegram_id: int = Field(..., description="Telegram user identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Context timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("team_id")
    def validate_team_id_required(cls, v):
        """Validate team_id is not empty."""
        if not v or not v.strip():
            raise ValueError("Team ID cannot be empty")
        return v.strip()

    @validator("telegram_id")
    def validate_telegram_id_required(cls, v):
        """Validate telegram_id is positive integer."""
        # First check if it was originally an int (Pydantic may convert strings)
        if isinstance(v, str):
            # Try to convert but validate it's a proper integer string
            try:
                v = int(v)
            except ValueError:
                raise ValueError("Telegram ID must be a valid integer")
        
        if not isinstance(v, int) or v <= 0:
            raise ValueError("Telegram ID must be a positive integer")
        return v

    @validator("team_id")
    def validate_team_id(cls, v):
        """Validate team ID format."""
        if len(v) > 20:
            raise ValueError("Team ID must be 20 characters or less")
        return v



class PlayerContext(BaseContext):
    """Context for player-related operations."""

    player_id: str | None = Field(None, description="Player identifier")
    phone: str | None = Field(None, description="Phone number")
    position: str | None = Field(None, description="Player position")

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

    match_id: str | None = Field(None, description="Match identifier")
    match_date: datetime | None = Field(None, description="Match date")
    venue: str | None = Field(None, description="Match venue")

    @validator("match_id")
    def validate_match_id(cls, v):
        """Validate match ID if provided."""
        if v is not None and len(v) > 20:
            raise ValueError("Match ID must be 20 characters or less")
        return v


class PaymentContext(BaseContext):
    """Context for payment-related operations."""

    amount: float | None = Field(None, description="Payment amount")
    currency: str = Field(default="GBP", description="Currency code")
    payment_type: str | None = Field(None, description="Type of payment")

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

    match_id: str | None = Field(None, description="Match identifier")
    attendance_status: str | None = Field(None, description="Attendance status")

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

    message_type: str | None = Field(None, description="Type of message")
    recipient_group: str | None = Field(None, description="Recipient group")

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


        context_type: Type of context to create
        **kwargs: Context data


    :return: Appropriate context object
    :rtype: str  # TODO: Fix type


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


        context_data: Data to validate
        context_type: Type of context to validate against


    :return: True if valid, False otherwise
    :rtype: str  # TODO: Fix type
    """
    try:
        create_context(context_type, **context_data)
        return True
    except Exception as e:
        logger.warning(f"Context validation failed: {e}")
        return False
