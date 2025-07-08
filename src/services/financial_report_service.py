import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from services.payment_service import PaymentService
from services.expense_service import ExpenseService
from services.team_service import TeamService
from core.bot_config_manager import get_bot_config_manager
# from tools.telegram_tools import format_message_for_telegram  # File doesn't exist
from database.models_improved import ExpenseCategory
import requests

logger = logging.getLogger(__name__)

class FinancialReportService:
    """Service to generate and send financial reports."""

    def __init__(self, team_id: str, bot_token: str):
        self.team_id = team_id
        self.bot_token = bot_token
        self.payment_service = PaymentService(team_id=team_id)
        self.expense_service = ExpenseService()
        self.team_service = TeamService()
        self.bot_config_manager = get_bot_config_manager()

    async def generate_financial_summary(self) -> str:
        """Generates a comprehensive financial summary for the team."""
        try:
            team = await self.team_service.get_team(self.team_id)
            if not team:
                return "❌ Team not found for financial summary."

            total_income = await self.payment_service.get_total_income(self.team_id)
            total_expenses = await self.expense_service.get_total_expenses(self.team_id)
            current_balance = total_income - total_expenses

            message = f"""📊 Financial Summary for {team.name}

💰 Total Income: £{total_income:.2f}
💸 Total Expenses: £{total_expenses:.2f}

Current Balance: £{current_balance:.2f}

Expense Breakdown:"""

            expense_by_category = {}
            for category in ExpenseCategory:
                total_cat_expense = await self.expense_service.get_total_expenses_by_category(self.team_id, category)
                if total_cat_expense > 0:
                    expense_by_category[category.value] = total_cat_expense

            if expense_by_category:
                for category, amount in expense_by_category.items():
                    message += f"\n• {category.replace('_', ' ').title()}: £{amount:.2f}"
            else:
                message += "\n• No expenses recorded yet."

            if team.budget_limits:
                message += "\n\nBudget Limits:"
                for category_str, limit in team.budget_limits.items():
                    category = ExpenseCategory[category_str]
                    current_spent = await self.expense_service.get_total_expenses_by_category(self.team_id, category)
                    remaining = limit - current_spent
                    message += f"\n• {category.value.replace('_', ' ').title()}: £{current_spent:.2f} / £{limit:.2f} (Remaining: £{remaining:.2f})"

            message += "\n\n---\nGenerated automatically by KICKAI Team Management System"
            return message
        except Exception as e:
            logger.error(f"Error generating financial summary for team {self.team_id}: {e}")
            return f"❌ Error generating financial summary: {str(e)}"

    async def send_financial_report(self) -> bool:
        """Generates and sends the financial report to the leadership chat."""
        try:
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.leadership_chat_id:
                logger.error(f"❌ No leadership chat configured for team {self.team_id}")
                return False

            summary_message = await self.generate_financial_summary()
            formatted_message = summary_message  # Use message as-is since telegram_tools doesn't exist

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": bot_config.leadership_chat_id,
                "text": formatted_message,
                "parse_mode": "HTML"
            }

            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Financial report sent to leadership chat {bot_config.leadership_chat_id}")
                return True
            else:
                logger.error(f"❌ Failed to send financial report: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending financial report: {e}")
            return False

    async def schedule_financial_report_task(self) -> None:
        """Schedules the financial report to run based on configuration."""
        while True:
            try:
                now = datetime.now()
                financial_report_config = self.bot_config_manager.get_financial_report_config(self.team_id)

                if not financial_report_config or not financial_report_config.get("enabled", False):
                    logger.info(f"Financial reports disabled for team {self.team_id}. Sleeping for 24 hours.")
                    await asyncio.sleep(24 * 60 * 60)
                    continue

                frequency = financial_report_config.get("frequency", "monthly")
                report_time_str = financial_report_config.get("time", "09:00")
                report_hour, report_minute = map(int, report_time_str.split(":"))

                next_run = None
                if frequency == "daily":
                    next_run = now.replace(hour=report_hour, minute=report_minute, second=0, microsecond=0)
                    if next_run <= now:
                        next_run += timedelta(days=1)
                elif frequency == "weekly":
                    day_of_week_str = financial_report_config.get("day_of_week", "monday").lower()
                    days_of_week = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
                    target_day_of_week = days_of_week.get(day_of_week_str, 0) # Default to Monday

                    days_until_target = (target_day_of_week - now.weekday() + 7) % 7
                    if days_until_target == 0 and now.time() > datetime.strptime(report_time_str, "%H:%M").time():
                        days_until_target = 7
                    next_run = now + timedelta(days=days_until_target)
                    next_run = next_run.replace(hour=report_hour, minute=report_minute, second=0, microsecond=0)

                elif frequency == "monthly":
                    day_of_month = financial_report_config.get("day_of_month", 1)
                    # Ensure day_of_month is valid for the current month
                    try:
                        next_run = now.replace(day=day_of_month, hour=report_hour, minute=report_minute, second=0, microsecond=0)
                    except ValueError: # Day of month might be invalid for current month (e.g., Feb 30)
                        next_run = now.replace(day=1, hour=report_hour, minute=report_minute, second=0, microsecond=0) + timedelta(days=32) # Move to next month
                        next_run = next_run.replace(day=day_of_month)

                    if next_run <= now:
                        # Move to next month
                        if now.month == 12:
                            next_run = next_run.replace(year=now.year + 1, month=1)
                        else:
                            next_run = next_run.replace(month=now.month + 1)
                        # Re-adjust day in case it was invalid for the new month
                        try:
                            next_run = next_run.replace(day=day_of_month)
                        except ValueError:
                            next_run = next_run.replace(day=1) + timedelta(days=32) # Move to next month
                            next_run = next_run.replace(day=day_of_month)

                if next_run is None:
                    logger.error(f"Invalid financial report frequency: {frequency}. Sleeping for 24 hours.")
                    await asyncio.sleep(24 * 60 * 60)
                    continue

                sleep_seconds = (next_run - now).total_seconds()
                if sleep_seconds < 0: # Should not happen with correct logic, but as a safeguard
                    sleep_seconds = 60 # Wait a minute and re-evaluate

                logger.info(f"⏰ Financial report scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')}. Sleeping for {sleep_seconds/3600:.1f} hours.")
                await asyncio.sleep(sleep_seconds)

                await self.send_financial_report()

            except Exception as e:
                logger.error(f"❌ Error in financial report task for team {self.team_id}: {e}")
                await asyncio.sleep(3600) # Wait 1 hour before retrying


async def start_financial_report_service(team_id: str, bot_token: str) -> None:
    """Starts the financial report service for a specific team."""
    service = FinancialReportService(team_id, bot_token)
    await service.schedule_financial_report_task()
