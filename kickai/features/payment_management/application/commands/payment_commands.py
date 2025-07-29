#!/usr/bin/env python3
"""
Payment Management Commands

This module registers all payment management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# PAYMENT COMMANDS
# ============================================================================


@command(
    name="/budget",
    description="View budget information (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="payment_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/budget", "/budget 2024"],
    parameters={"year": "Year to view budget for (optional)"},
    help_text="""
💰 Budget Information (Leadership Only)

View team budget and financial information.

Usage:
• /budget - Show current budget status
• /budget [year] - Show budget for specific year

Example:
/budget 2024

What you'll see:
• Total budget allocated
• Expenses incurred
• Remaining budget
• Payment status summary
• Financial trends

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_budget_command(update, context, **kwargs):
    """Handle /budget command."""
    # This will be handled by the agent system
    return None


@command(
    name="/createpayment",
    description="Create a new payment record (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="payment_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/createpayment John Smith 50.00 Match fee"],
    parameters={
        "player_name": "Player name",
        "amount": "Payment amount",
        "description": "Payment description",
    },
    help_text="""
💳 Create Payment (Leadership Only)

Create a new payment record for a player.

Usage:
/createpayment [player_name] [amount] [description]

Example:
/createpayment John Smith 50.00 Match fee

What happens:
1. Payment record is created
2. Player is notified of the payment
3. Payment status is set to "pending"
4. Payment is tracked in budget

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_createpayment_command(update, context, **kwargs):
    """Handle /createpayment command."""
    # This will be handled by the agent system
    return None


@command(
    name="/payments",
    description="View payment history (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="payment_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/payments", "/payments John Smith"],
    parameters={"player_name": "Player name to filter by (optional)"},
    help_text="""
📋 Payment History (Leadership Only)

View payment history and records.

Usage:
• /payments - Show all payment records
• /payments [player_name] - Show payments for specific player

Example:
/payments John Smith

What you'll see:
• List of all payments
• Payment amounts and dates
• Payment status (pending, paid, cancelled)
• Player information
• Payment descriptions

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_payments_command(update, context, **kwargs):
    """Handle /payments command."""
    # This will be handled by the agent system
    return None


@command(
    name="/markpaid",
    description="Mark payment as paid (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="payment_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/markpaid PAY123", "/markpaid PAY123 2024-01-15"],
    parameters={
        "payment_id": "Payment ID to mark as paid",
        "date": "Payment date (optional, defaults to today)",
    },
    help_text="""
✅ Mark Payment as Paid (Leadership Only)

Mark a payment record as paid.

Usage:
/markpaid [payment_id] [date]

Example:
/markpaid PAY123 2024-01-15

What happens:
1. Payment status is updated to "paid"
2. Payment date is recorded
3. Budget is updated accordingly
4. Player is notified of payment confirmation

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_markpaid_command(update, context, **kwargs):
    """Handle /markpaid command."""
    # This will be handled by the agent system
    return None


# Note: /paymentexport command has been removed as it's not needed for now
# Export functionality can be added later if required
