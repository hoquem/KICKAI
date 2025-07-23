"""
Reminder Service for KICKAI

This module handles automated and manual reminders for player onboarding.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.settings import Settings
from features.communication.domain.interfaces.reminder_service_interface import IReminderService
from features.payment_management.domain.interfaces.payment_operations import IPaymentOperations
from features.player_registration.domain.entities.player import OnboardingStatus, Player
from features.player_registration.domain.interfaces.player_operations import IPlayerOperations


@dataclass
class ReminderMessage:
    """Represents a reminder message."""
    player_id: str
    message: str
    reminder_type: str  # 'automated' or 'manual'
    sent_at: datetime
    reminder_number: int


class ReminderService(IReminderService):
    """Service for managing player reminders and notifications."""

    def __init__(self, team_id: str, player_operations: IPlayerOperations, payment_operations: IPaymentOperations):
        self.team_id = team_id
        self.player_operations = player_operations
        self.payment_operations = payment_operations
        self.settings = Settings()

        # Reminder configuration
        self.reminder_config = {
            "first_reminder": 24,
            "second_reminder": 48,
            "third_reminder": 72,
            "max_reminders": 3
        }

    async def check_and_send_reminders(self) -> list[ReminderMessage]:
        """Check for players who need reminders and send them."""
        try:
            players = await self.player_operations.get_team_players(self.team_id)
            reminders_sent = []

            for player in players:
                if player.needs_reminder():
                    reminder_message = await self.send_automated_reminder(player)
                    if reminder_message:
                        reminders_sent.append(reminder_message)

            return reminders_sent

        except Exception as e:
            logging.error(f"Error checking and sending reminders: {e}")
            return []

    async def send_automated_reminder(self, player: Player) -> ReminderMessage | None:
        """Send an automated reminder to a player."""
        try:
            reminder_number = player.reminders_sent + 1
            message = await self._generate_reminder_message(player, reminder_number)

            # Update player reminder tracking
            player.send_reminder()
            await self.player_operations.update_player(
                player.id,
                reminders_sent=player.reminders_sent,
                last_reminder_sent=player.last_reminder_sent,
                next_reminder_due=player.next_reminder_due
            )

            # Send the message (this would integrate with Telegram bot)
            await self._send_telegram_message(player.telegram_id, message)

            # Notify admin about reminder sent
            await self._notify_admin_reminder_sent(player, reminder_number)

            return ReminderMessage(
                player_id=player.player_id,
                message=message,
                reminder_type="automated",
                sent_at=datetime.now(),
                reminder_number=reminder_number
            )

        except Exception as e:
            logging.error(f"Error sending automated reminder to {player.name}: {e}")
            return None

    async def send_manual_reminder(self, player_id: str, admin_id: str) -> tuple[bool, str]:
        """Send a manual reminder to a player (admin triggered)."""
        try:
            # Find player by player_id
            players = await self.player_operations.get_team_players(self.team_id)
            player = None
            for p in players:
                if p.player_id.upper() == player_id.upper():
                    player = p
                    break

            if not player:
                return False, f"❌ Player {player_id} not found"

            if player.onboarding_status not in [OnboardingStatus.IN_PROGRESS, OnboardingStatus.PENDING]:
                return False, f"❌ Player {player.name} is not in onboarding"

            # Generate manual reminder message
            message = self._generate_manual_reminder_message(player)

            # Update player reminder tracking
            player.send_reminder()
            await self.player_operations.update_player(
                player.id,
                reminders_sent=player.reminders_sent,
                last_reminder_sent=player.last_reminder_sent,
                next_reminder_due=player.next_reminder_due
            )

            # Send the message
            await self._send_telegram_message(player.telegram_id, message)

            # Return success message for admin
            admin_message = f"""📢 Reminder Sent to {player.name} ({player.player_id})

📋 Reminder Details:
• Type: Manual Admin Reminder
• Message: Custom reminder message
• Sent: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 Current Status:
• Onboarding Progress: {player.get_onboarding_progress()['completed_steps']}/4 steps completed
• Time Since Last Activity: {self._get_time_since_last_activity(player)}
• Previous Reminders: {player.reminders_sent - 1} (automated)

✅ Reminder delivered successfully"""

            return True, admin_message

        except Exception as e:
            logging.error(f"Error sending manual reminder: {e}")
            return False, f"❌ Error sending reminder: {e!s}"

    async def _generate_reminder_message(self, player: Player, reminder_number: int) -> str:
        """Generate reminder message based on reminder number and player status."""
        progress = player.get_onboarding_progress()

        # Check for outstanding payments - properly async
        try:
            from features.payment_management.domain.entities.payment_models import PaymentStatus
            outstanding_payments = await self.payment_operations.list_payments(player_id=player.id, status=PaymentStatus.PENDING)
        except Exception as e:
            logging.error(f"Error getting outstanding payments: {e}")
            outstanding_payments = []

        if outstanding_payments:
            return await self._generate_payment_reminder_message(player, outstanding_payments)

        # Existing onboarding reminders
        if reminder_number == 1:
            return f"""⏰ Gentle Reminder - Complete Your Onboarding

Hi {player.name}! 👋

You started your KICKAI Team onboarding yesterday but haven't completed it yet.

📊 Your Progress:
🔄 Step 1: Basic Registration ✅ Completed
🔄 Step 2: Emergency Contact {'✅ Completed' if progress['steps']['emergency_contact']['completed'] else '⏳ Pending'}
🔄 Step 3: Date of Birth {'✅ Completed' if progress['steps']['date_of_birth']['completed'] else '⏳ Pending'}
🔄 Step 4: FA Registration {'✅ Completed' if progress['steps']['fa_registration']['completed'] else '⏳ Pending'}

💡 Need Help?
• Reply with "help" for assistance
• Contact admin if you have questions
• Use /status to check your current progress

Ready to continue? Just reply with your emergency contact details!"""

        elif reminder_number == 2:
            return f"""⏰ Reminder - Onboarding Still Pending

Hi {player.name}! 👋

Your KICKAI Team onboarding is still incomplete. Let's get you set up!

📊 Your Progress:
🔄 Step 1: Basic Registration ✅ Completed
🔄 Step 2: Emergency Contact {'✅ Completed' if progress['steps']['emergency_contact']['completed'] else '⏳ Pending'}
🔄 Step 3: Date of Birth {'✅ Completed' if progress['steps']['date_of_birth']['completed'] else '⏳ Pending'}
🔄 Step 4: FA Registration {'✅ Completed' if progress['steps']['fa_registration']['completed'] else '⏳ Pending'}

💡 Quick Start:
• Emergency Contact: Reply with "emergency: [name] [phone]"
• Date of Birth: Reply with "dob: [YYYY-MM-DD]"
• FA Registration: Reply with "fa: [FA number]"

Need help? Just reply with "help"!"""

        else:  # reminder_number >= 3
            return f"""⏰ Final Reminder - Complete Onboarding

Hi {player.name}! 👋

This is your final reminder to complete your KICKAI Team onboarding.

📊 Your Progress:
🔄 Step 1: Basic Registration ✅ Completed
🔄 Step 2: Emergency Contact {'✅ Completed' if progress['steps']['emergency_contact']['completed'] else '⏳ Pending'}
🔄 Step 3: Date of Birth {'✅ Completed' if progress['steps']['date_of_birth']['completed'] else '⏳ Pending'}
🔄 Step 4: FA Registration {'✅ Completed' if progress['steps']['fa_registration']['completed'] else '⏳ Pending'}

⚠️ Action Required:
Please complete your onboarding within 24 hours to avoid delays.

💡 Quick Commands:
• /status - Check your progress
• /help - Get assistance
• Contact admin for support

Let's get you fully registered!"""

    async def _generate_payment_reminder_message(self, player: Player, payments: list[Any]) -> str:
        """Generate payment reminder message."""
        total_amount = sum(payment.amount for payment in payments)

        return f"""💰 Payment Reminder

Hi {player.name}! 👋

You have outstanding payments that need to be settled:

📊 Outstanding Payments:
{chr(10).join([f"• {payment.description}: £{payment.amount}" for payment in payments])}

💰 Total Outstanding: £{total_amount}

💳 Payment Options:
• Use the payment link provided earlier
• Contact admin for alternative payment methods
• Reply with "payment" for assistance

⏰ Please settle these payments to avoid any delays in your registration.

Need help? Reply with "help" or contact admin!"""

    def _generate_manual_reminder_message(self, player: Player):
        """Generate manual reminder message."""
        progress = player.get_onboarding_progress()

        return f"""📢 Admin Reminder - Complete Your Onboarding

Hi {player.name}! 👋

Your team admin has sent you a reminder to complete your onboarding.

📊 Your Progress:
🔄 Step 1: Basic Registration ✅ Completed
🔄 Step 2: Emergency Contact {'✅ Completed' if progress['steps']['emergency_contact']['completed'] else '⏳ Pending'}
🔄 Step 3: Date of Birth {'✅ Completed' if progress['steps']['date_of_birth']['completed'] else '⏳ Pending'}
🔄 Step 4: FA Registration {'✅ Completed' if progress['steps']['fa_registration']['completed'] else '⏳ Pending'}

💡 Quick Commands:
• /status - Check your progress
• /help - Get assistance
• Contact admin for support

Please complete your onboarding as soon as possible!"""

    def _get_time_since_last_activity(self, player: Player) -> str:
        """Get formatted time since last activity."""
        if not player.last_activity:
            return "Unknown"

        time_diff = datetime.now() - player.last_activity
        if time_diff.days > 0:
            return f"{time_diff.days} days"
        elif time_diff.seconds > 3600:
            return f"{time_diff.seconds // 3600} hours"
        else:
            return f"{time_diff.seconds // 60} minutes"

    async def _send_telegram_message(self, telegram_id: str, message: str) -> None:
        """Send message via Telegram (placeholder for integration)."""
        # This would integrate with the Telegram bot
        logging.info(f"Would send message to {telegram_id}: {message[:100]}...")

    async def _notify_admin_reminder_sent(self, player: Player, reminder_number: int) -> None:
        """Notify admin that a reminder was sent."""
        # This would send a notification to admin
        logging.info(f"Reminder #{reminder_number} sent to {player.name} ({player.player_id})")

    async def get_players_needing_reminders(self) -> list[Player]:
        """Get list of players who need reminders."""
        try:
            players = await self.player_operations.get_team_players(self.team_id)
            return [player for player in players if player.needs_reminder()]
        except Exception as e:
            logging.error(f"Error getting players needing reminders: {e}")
            return []
