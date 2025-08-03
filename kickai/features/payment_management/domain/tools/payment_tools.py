#!/usr/bin/env python3
"""
Payment Management Tools

This module provides tools for payment management operations.
"""

from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    format_tool_error,
    sanitize_input,
    validate_required_input,
)


class CreatePaymentInput(BaseModel):
    """Input model for create_payment tool."""

    team_id: str
    user_id: str
    player_id: str
    amount: float
    payment_type: str
    description: str


class GetPaymentHistoryInput(BaseModel):
    """Input model for get_payment_history tool."""

    team_id: str
    user_id: str
    player_id: str | None = None


class MarkPaymentPaidInput(BaseModel):
    """Input model for mark_payment_paid tool."""

    team_id: str
    user_id: str
    payment_id: str


class ExportPaymentDataInput(BaseModel):
    """Input model for export_payment_data tool."""

    team_id: str
    user_id: str
    start_date: str | None = None
    end_date: str | None = None


@tool("create_payment")
def create_payment(
    team_id: str, user_id: str, player_id: str, amount: float, payment_type: str, description: str
) -> str:
    """
    Create a new payment record.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        player_id: Player ID for the payment
        amount: Payment amount
        payment_type: Type of payment (match_fee, membership_fee, fine, etc.)
        description: Payment description

    Returns:
        Success message with payment details or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(player_id, "Player ID")
        if validation_error:
            return validation_error

        if amount <= 0:
            return format_tool_error("Payment amount must be greater than 0")

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        player_id = sanitize_input(player_id, max_length=50)
        payment_type = sanitize_input(payment_type, max_length=50)
        description = sanitize_input(description, max_length=200)

        # Get payment service
        container = get_container()
        payment_service = container.get_service("PaymentService")

        if not payment_service:
            return format_tool_error("Payment service not available")

        # Create payment
        success, message = payment_service.create_payment_sync(
            team_id=team_id,
            player_id=player_id,
            amount=amount,
            payment_type=payment_type,
            description=description,
            created_by=user_id,
        )

        if success:
            return f"""✅ Payment Created Successfully!

💰 Payment Details:
• Player ID: {player_id}
• Amount: £{amount:.2f}
• Type: {payment_type}
• Description: {description}
• Status: Pending

📋 Next Steps:
• Player will be notified of the payment
• Payment can be marked as paid when received
• Use /payments to view payment history"""
        else:
            return format_tool_error(f"Failed to create payment: {message}")

    except Exception as e:
        logger.error(f"Failed to create payment: {e}", exc_info=True)
        return format_tool_error(f"Failed to create payment: {e}")


@tool("get_payment_history")
def get_payment_history(team_id: str, user_id: str, player_id: str | None = None) -> str:
    """
    Get payment history for a team or specific player.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        player_id: Player ID (optional) - if provided, shows only that player's payments

    Returns:
        Payment history summary or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        if player_id:
            player_id = sanitize_input(player_id, max_length=50)

        # Get payment service
        container = get_container()
        payment_service = container.get_service("PaymentService")

        if not payment_service:
            return format_tool_error("Payment service not available")

        # Get payment history
        success, message = payment_service.get_payment_history_sync(
            team_id=team_id, player_id=player_id
        )

        if success:
            return f"""📊 Payment History

{message}

💡 Use /payments [player_id] to view specific player payments"""
        else:
            return format_tool_error(f"Failed to get payment history: {message}")

    except Exception as e:
        logger.error(f"Failed to get payment history: {e}", exc_info=True)
        return format_tool_error(f"Failed to get payment history: {e}")


@tool("mark_payment_paid")
def mark_payment_paid(team_id: str, user_id: str, payment_id: str) -> str:
    """
    Mark a payment as paid.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        payment_id: Payment ID to mark as paid

    Returns:
        Success message or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(payment_id, "Payment ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        payment_id = sanitize_input(payment_id, max_length=50)

        # Get payment service
        container = get_container()
        payment_service = container.get_service("PaymentService")

        if not payment_service:
            return format_tool_error("Payment service not available")

        # Mark payment as paid
        success, message = payment_service.mark_payment_paid_sync(
            team_id=team_id, payment_id=payment_id, marked_by=user_id
        )

        if success:
            return f"""✅ Payment Marked as Paid!

💰 Payment Details:
• Payment ID: {payment_id}
• Status: Paid
• Marked by: {user_id}
• Date: {message}

📋 The player has been notified of the payment confirmation."""
        else:
            return format_tool_error(f"Failed to mark payment as paid: {message}")

    except Exception as e:
        logger.error(f"Failed to mark payment as paid: {e}", exc_info=True)
        return format_tool_error(f"Failed to mark payment as paid: {e}")


@tool("export_payment_data")
def export_payment_data(
    team_id: str, user_id: str, start_date: str | None = None, end_date: str | None = None
) -> str:
    """
    Export payment data for reporting.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        start_date: Start date for export (optional, format: YYYY-MM-DD)
        end_date: End date for export (optional, format: YYYY-MM-DD)

    Returns:
        Export summary or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        if start_date:
            start_date = sanitize_input(start_date, max_length=20)
        if end_date:
            end_date = sanitize_input(end_date, max_length=20)

        # Get payment service
        container = get_container()
        payment_service = container.get_service("PaymentService")

        if not payment_service:
            return format_tool_error("Payment service not available")

        # Export payment data
        success, message = payment_service.export_payment_data_sync(
            team_id=team_id, start_date=start_date, end_date=end_date
        )

        if success:
            return f"""📊 Payment Data Export

{message}

💡 The export has been generated and is available for download."""
        else:
            return format_tool_error(f"Failed to export payment data: {message}")

    except Exception as e:
        logger.error(f"Failed to export payment data: {e}", exc_info=True)
        return format_tool_error(f"Failed to export payment data: {e}") 