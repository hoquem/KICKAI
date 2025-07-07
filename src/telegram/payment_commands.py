from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.services.payment_service import PaymentService
from src.tools.payment_tools import payment_type_to_str, payment_status_to_str
from src.database.models_improved import ExpenseCategory, PaymentStatus
from src.core.bot_config_manager import get_bot_config_manager
from src.services.expense_service import get_expense_service
from src.services.team_service import get_team_service
import httpx
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)

class PaymentCommands:
    def __init__(self, team_id: str):
        self.payment_service = PaymentService(team_id=team_id)
        self.team_id = team_id
        self.bot_config_manager = get_bot_config_manager()

    async def send_payment_request(self, chat_id: str, payment_id: str, amount: float, payment_type: str, description: str) -> bool:
        """Sends a payment request message with an inline 'Pay Now' button."""
        try:
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.token:
                logger.error(f"Bot token not found for team {self.team_id}")
                return False

            keyboard = [[InlineKeyboardButton("💰 Pay Now", callback_data=f"pay_now_{payment_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message_text = f"""💸 Payment Request

Description: {description}
Amount: £{amount:.2f}
Type: {payment_type.replace('_', ' ').title()}
Payment ID: {payment_id}

To pay, click the button below:
"""

            url = f"https://api.telegram.org/bot{bot_config.token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message_text,
                "reply_markup": reply_markup.to_json(),
                "parse_mode": "HTML"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Payment request sent for {payment_id} to chat {chat_id}")
                    return True
                else:
                    logger.error(f"Failed to send payment request: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending payment request: {e}")
            return False

    async def pay(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Example: /pay <amount> <type> [description]
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /pay <amount> <type> [description]")
            return
        amount = float(args[0])
        payment_type = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else f"{payment_type.replace('_', ' ').title()} payment"
        player_id = str(update.effective_user.id)

        # Create payment record
        record = await self.payment_service.create_payment(player_id, amount, payment_type, description=description)

        # Send payment request with inline button
        success = await self.send_payment_request(update.effective_chat.id, record.id, amount, payment_type, description)
        if success:
            await update.message.reply_text(f"Payment request sent for {record.id} ({amount} {payment_type}).")
        else:
            await update.message.reply_text(f"Payment created: {record.id} ({amount} {payment_type}), but failed to send request.")

    async def payments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        player_id = str(update.effective_user.id)
        payments = self.payment_service.list_payments(player_id=player_id)
        if not payments:
            await update.message.reply_text("No payments found.")
            return
        msg = "Your payments:\n" + "\n".join(f"{p.id}: {p.amount} {payment_type_to_str(p.payment_type)} [{payment_status_to_str(p.status)}]" for p in payments)
        await update.message.reply_text(msg)

    async def payment_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /payment_status <payment_id>")
            return
        payment_id = args[0]
        status = self.payment_service.get_payment_status(payment_id)
        await update.message.reply_text(f"Payment {payment_id} status: {payment_status_to_str(status)}")

    async def get_financial_dashboard(self, telegram_user_id: str) -> str:
        """Generates a personalized financial dashboard for a player."""
        try:
            player = await self.payment_service.player_service.get_player_by_telegram_id(telegram_user_id)
            if not player:
                return "❌ Player not found. Please ensure your profile is complete."

            all_payments = await self.payment_service.list_payments(player_id=player.id)

            owing = []
            paid = []
            upcoming = []

            for p in all_payments:
                if p.status == PaymentStatus.PENDING or p.status == PaymentStatus.OVERDUE:
                    owing.append(p)
                elif p.status == PaymentStatus.PAID:
                    paid.append(p)
                # Assuming 'upcoming' payments are those with a future due date and not yet paid
                if p.due_date and p.due_date > datetime.now() and p.status != PaymentStatus.PAID:
                    upcoming.append(p)

            message = f"""📊 Your Financial Dashboard

👤 Player: {player.name.upper()} ({player.player_id.upper()})

💰 What You Owe:"""
            if owing:
                for p in owing:
                    message += f"\n• £{p.amount:.2f} for {payment_type_to_str(p.type)} (ID: {p.id}) - Due: {p.due_date.strftime('%d/%m') if p.due_date else 'N/A'}"
            else:
                message += "\n• Nothing outstanding! 🎉"

            message += f"\n\n✅ What You've Paid:"""
            if paid:
                for p in paid:
                    message += f"\n• £{p.amount:.2f} for {payment_type_to_str(p.type)} (ID: {p.id}) - Paid: {p.paid_date.strftime('%d/%m') if p.paid_date else 'N/A'}"
            else:
                message += "\n• No payments recorded yet."

            message += f"\n\n📅 Upcoming Payments:"""
            if upcoming:
                for p in upcoming:
                    message += f"\n• £{p.amount:.2f} for {payment_type_to_str(p.type)} (ID: {p.id}) - Due: {p.due_date.strftime('%d/%m') if p.due_date else 'N/A'}"
            else:
                message += "\n• No upcoming payments."

            message += "\n\n💡 Use /payment_history for full details."

            return message
        except Exception as e:
            logger.error(f"Error generating financial dashboard for {telegram_user_id}: {e}")
            return f"❌ Error retrieving financial dashboard: {str(e)}"

    async def handle_refund_payment(self, args: List[str]) -> str:
        """Handles the refund payment command."""
        if not args:
            return "❌ Usage: /refund_payment <payment_id>"
        payment_id = args[0]
        try:
            payment = await self.payment_service.refund_payment(payment_id)
            return f"✅ Payment {payment.id} has been refunded (status: {payment.status.value})."
        except PaymentNotFoundError:
            return f"❌ Payment {payment_id} not found."
        except Exception as e:
            logger.error(f"Error refunding payment {payment_id}: {e}")
            return f"❌ Failed to refund payment {payment_id}: {str(e)}"

    async def handle_record_expense(self, args: List[str]) -> str:
        """Handles the record expense command."""
        if len(args) < 2:
            return "❌ Usage: /record_expense <amount> <category> [description]"
        
        try:
            amount = float(args[0])
            category_str = args[1].upper()
            description = " ".join(args[2:]) if len(args) > 2 else None

            try:
                category = ExpenseCategory[category_str]
            except KeyError:
                return f"❌ Invalid category: {category_str}. Valid categories are: {', '.join([e.name.lower() for e in ExpenseCategory])}"

            expense = await self.payment_service.record_expense(self.team_id, amount, category, description)
            return f"✅ Expense of £{expense.amount:.2f} for {expense.category.value} recorded successfully (ID: {expense.id})."
        except ValueError:
            return "❌ Invalid amount. Please provide a number."
        except Exception as e:
            logger.error(f"Error recording expense: {e}")
            return f"❌ Failed to record expense: {str(e)}"

    async def get_financial_overview(self) -> str:
        """Generates a financial overview for the team."""
        try:
            # Get all payments for the team
            all_payments = await self.payment_service.get_team_payments(self.team_id)
            total_income = sum(p.amount for p in all_payments if p.status == PaymentStatus.PAID)

            # Get all expenses for the team
            expense_service = get_expense_service()
            all_expenses = await expense_service.list_expenses(self.team_id)
            total_expenses = sum(e.amount for e in all_expenses)

            current_balance = total_income - total_expenses

            # Expense breakdown by category
            expense_by_category = {}
            for expense in all_expenses:
                expense_by_category[expense.category.value] = expense_by_category.get(expense.category.value, 0.0) + expense.amount

            message = f"""📊 Team Financial Overview

💰 Total Income: £{total_income:.2f}
💸 Total Expenses: £{total_expenses:.2f}

Current Balance: £{current_balance:.2f}

Expense Breakdown:"""
            if expense_by_category:
                for category, amount in expense_by_category.items():
                    message += f"\n• {category.replace('_', ' ').title()}: £{amount:.2f}"
            else:
                message += "\n• No expenses recorded yet."

            # Add budget limits if available
            team_service = get_team_service()
            team = await team_service.get_team(self.team_id)
            if team and team.budget_limits:
                message += "\n\nBudget Limits:"
                for category, limit in team.budget_limits.items():
                    current_spent = await expense_service.get_total_expenses_by_category(self.team_id, ExpenseCategory[category])
                    remaining = limit - current_spent
                    message += f"\n• {category.replace('_', ' ').title()}: £{current_spent:.2f} / £{limit:.2f} (Remaining: £{remaining:.2f})"

            message += "\n\n💡 Use /record_expense to add new expenses."

            return message
        except Exception as e:
            logger.error(f"Error generating financial overview for team {self.team_id}: {e}")
            return f"❌ Error retrieving financial overview: {str(e)}" 