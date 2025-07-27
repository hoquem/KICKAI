#!/usr/bin/env python3
"""
Payment Management Commands

This module registers all payment management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# PAYMENT MANAGEMENT COMMANDS
# ============================================================================


@command(
    name="/createpayment",
    description="Create a new payment record (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="payment_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/createpayment", "/createpayment Match Fee 25.00"],
    parameters={"description": "Payment description", "amount": "Payment amount"},
    help_text="""
💰 Create Payment (Leadership Only)

Create a new payment record for team expenses or fees.

Usage:
• /createpayment - Start payment creation process
• /createpayment [description] [amount] - Create payment with details

Example:
/createpayment Match Fee 25.00

What happens:
1. Payment record is created
2. Payment is added to team budget
3. Payment tracking is enabled
4. Team members are notified

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_createpayment_command(update, context, **kwargs):
    """Handle /createpayment command."""
    # This will be handled by the agent system
    return None


@command(
    name="/payments",
    description="View payment records",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="payment_management",
    examples=["/payments", "/payments pending", "/payments completed"],
    parameters={"status": "Optional filter (pending, completed, all)"},
    help_text="""
📊 View Payments

View payment records and status.

Usage:
• /payments - Show all payments
• /payments pending - Show pending payments only
• /payments completed - Show completed payments only

What you'll see:
• Payment descriptions and amounts
• Payment status (pending, completed, overdue)
• Due dates and payment dates
• Payment categories

💡 Tip: Use filters to focus on relevant payments.
    """,
)
async def handle_payments_command(update, context, **kwargs):
    """Handle /payments command."""
    # This will be handled by the agent system
    return None


@command(
    name="/budget",
    description="View team budget and financial status",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="payment_management",
    examples=["/budget", "/budget 2024"],
    parameters={"year": "Optional year to filter (e.g., 2024)"},
    help_text="""
💳 Team Budget

View team budget, expenses, and financial status.

Usage:
• /budget - Show current budget status
• /budget 2024 - Show budget for specific year

What you'll see:
• Total budget allocated
• Total expenses incurred
• Remaining budget
• Payment categories breakdown
• Financial trends

💡 Tip: Track budget to ensure financial sustainability.
    """,
)
async def handle_budget_command(update, context, **kwargs):
    """Handle /budget command."""
    # This will be handled by the agent system
    return None


@command(
    name="/markpaid",
    description="Mark payment as completed (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="payment_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/markpaid PAYMENT123", "/markpaid PAYMENT123 2024-01-15"],
    parameters={
        "payment_id": "Payment ID to mark as paid",
        "date": "Optional payment date (YYYY-MM-DD)",
    },
    help_text="""
✅ Mark Payment Paid (Leadership Only)

Mark a payment as completed and record payment date.

Usage:
• /markpaid PAYMENT123 - Mark payment as paid today
• /markpaid PAYMENT123 2024-01-15 - Mark payment as paid on specific date

What happens:
1. Payment status is updated to 'completed'
2. Payment date is recorded
3. Budget is updated
4. Payment history is updated

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_markpaid_command(update, context, **kwargs):
    """Handle /markpaid command."""
    # This will be handled by the agent system
    return None


@command(
    name="/paymentexport",
    description="Export payment data (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="payment_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/paymentexport", "/paymentexport 2024"],
    parameters={"year": "Optional year to filter (e.g., 2024)"},
    help_text="""
📋 Export Payment Data (Leadership Only)

Export payment data for accounting and reporting.

Usage:
• /paymentexport - Export all payment data
• /paymentexport 2024 - Export data for specific year

What you'll get:
• CSV file with payment records
• Payment details and amounts
• Payment dates and status
• Budget summaries
• Financial reports

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_paymentexport_command(update, context, **kwargs):
    """Handle /paymentexport command."""
    # This will be handled by the agent system
    return None
