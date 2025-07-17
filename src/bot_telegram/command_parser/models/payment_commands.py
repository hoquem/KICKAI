"""
Payment Command Models

This module contains Pydantic models for payment-related commands.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreatePaymentCommand(BaseModel):
    """Model for /create_payment command parameters."""
    amount: float = Field(..., gt=0, description="Payment amount")
    description: str = Field(..., description="Payment description")
    player_id: Optional[str] = Field(None, description="Player ID for player-specific payment")
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class PaymentStatusCommand(BaseModel):
    """Model for /payment_status command parameters."""
    payment_id: Optional[str] = Field(None, description="Payment ID to check")
    player_id: Optional[str] = Field(None, description="Player ID to check payments for")


class PendingPaymentsCommand(BaseModel):
    """Model for /pending_payments command parameters."""
    filter: Optional[str] = Field(None, description="Filter type (overdue, upcoming, etc.)")


class PaymentHistoryCommand(BaseModel):
    """Model for /payment_history command parameters."""
    player_id: Optional[str] = Field(None, description="Player ID to get history for")
    period: Optional[str] = Field(None, description="Time period (week, month, year)")


class FinancialDashboardCommand(BaseModel):
    """Model for /financial_dashboard command parameters."""
    period: Optional[str] = Field("month", description="Time period (week, month, year)") 