"""
Reminder Service for KICKAI

This module handles automated and manual reminders for player onboarding.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Tuple, Any
from dataclasses import dataclass

from database.models_improved import Player, OnboardingStatus, PaymentStatus
from services.player_service import get_player_service
from core.bot_config_manager import get_bot_config_manager
from utils.llm_client import LLMClient
from utils.llm_intent import LLMIntent
from services.interfaces.reminder_service_interface import IReminderService


@dataclass
class ReminderMessage:
    """Represents a reminder message."""
    player_id: str
    message: str
    reminder_type: str  # 'automated' or 'manual'
    sent_at: datetime
    reminder_number: int


class ReminderService(IReminderService):
    """Service for handling onboarding reminders."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_service = get_player_service(team_id=team_id)
        self.bot_config_manager = get_bot_config_manager()
        from services.payment_service import get_payment_service
        self.payment_service = get_payment_service(team_id=team_id)
        
        # Reminder schedule (in hours)
        self.reminder_schedule = {
            "first_reminder": 24,
            "second_reminder": 48,
            "third_reminder": 72,
            "max_reminders": 3
        }
    
    async def check_and_send_reminders(self) -> List[ReminderMessage]:
        """Check for players who need reminders and send them."""
        try:
            players = await self.player_service.get_team_players(self.team_id)
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
    
    async def send_automated_reminder(self, player: Player) -> Optional[ReminderMessage]:
        """Send an automated reminder to a player."""
        try:
            reminder_number = player.reminders_sent + 1
            message = self._generate_reminder_message(player, reminder_number)
            
            # Update player reminder tracking
            player.send_reminder()
            await self.player_service.update_player(
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
    
    async def send_manual_reminder(self, player_id: str, admin_id: str) -> Tuple[bool, str]:
        """Send a manual reminder to a player (admin triggered)."""
        try:
            # Find player by player_id
            players = await self.player_service.get_team_players(self.team_id)
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
            await self.player_service.update_player(
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
            return False, f"❌ Error sending reminder: {str(e)}"
    
    def _generate_reminder_message(self, player: Player, reminder_number: int) -> str:
        """Generate reminder message based on reminder number and player status."""
        progress = player.get_onboarding_progress()

        # Check for outstanding payments
        outstanding_payments = asyncio.run(self.payment_service.list_payments(player_id=player.id, status=PaymentStatus.PENDING))
        if outstanding_payments:
            return self._generate_payment_reminder_message(player, outstanding_payments)

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
Just reply with: "My emergency contact is [Name], [Phone], [Relationship]"

Example: "My emergency contact is John Doe, 07123456789, my husband"

Need help? Reply with "help" or contact admin."""

        else:  # reminder_number == 3
            return f"""⏰ Final Reminder - Complete Onboarding

Hi {player.name}! 👋

This is your final reminder to complete your KICKAI Team onboarding.

📊 Your Progress:
🔄 Step 1: Basic Registration ✅ Completed
🔄 Step 2: Emergency Contact {'✅ Completed' if progress['steps']['emergency_contact']['completed'] else '⏳ Pending'}
🔄 Step 3: Date of Birth {'✅ Completed' if progress['steps']['date_of_birth']['completed'] else '⏳ Pending'}
🔄 Step 4: FA Registration {'✅ Completed' if progress['steps']['fa_registration']['completed'] else '⏳ Pending'}

⚠️ Important: Incomplete onboarding may delay your team approval.

💡 Need Immediate Help?
• Reply with "help" for step-by-step guidance
• Contact admin directly
• Use /status to see your current progress

Let's get you set up today! 🏆"""

    def _generate_payment_reminder_message(self, player: Player, payments: List[Any]) -> str:
        """Generates an AI-driven gentle nudge for outstanding payments."""
        llm_client = LLMClient()

        payment_details = "\n".join([f"- £{p.amount:.2f} for {p.description or p.type.value.replace('_', ' ')} (Due: {p.due_date.strftime('%d/%m/%Y') if p.due_date else 'N/A'})" for p in payments])

        prompt = f"""Generate a gentle and friendly reminder message for a football player named {player.name} about their outstanding payments. The message should encourage them to pay without being overly pushy. Include the following details:

Outstanding Payments:
{payment_details}

Keep it concise and encouraging. End with a positive note about playing with the team.
"""
        try:
            # Use LLM to generate the message
            generated_message = asyncio.run(llm_client.generate_text(prompt))
            return f"""👋 Hi {player.name}!

{generated_message}

To view your full financial dashboard, type /financial_dashboard.

Thanks for your cooperation! ⚽🏆"""
        except Exception as e:
            logging.error(f"Error generating AI payment reminder: {e}")
            # Fallback to a default message if LLM fails
            return f"""👋 Hi {player.name}!

Just a friendly reminder about your outstanding payments:
{payment_details}

Please take a moment to settle these so we can keep everything running smoothly.

To view your full financial dashboard, type /financial_dashboard.

Thanks for your cooperation! ⚽🏆"""

    def _generate_manual_reminder_message(self, player: Player):
        """Generate manual reminder message from admin."""
        progress = player.get_onboarding_progress()
        
        return f"""📢 Message from Admin

Hi {player.name}! 👋

Just checking in on your onboarding progress. We'd love to have you fully set up and ready to play!

📊 Your Progress:
🔄 Step 1: Basic Registration ✅ Completed
🔄 Step 2: Emergency Contact {'✅ Completed' if progress['steps']['emergency_contact']['completed'] else '⏳ Pending'}
🔄 Step 3: Date of Birth {'✅ Completed' if progress['steps']['date_of_birth']['completed'] else '⏳ Pending'}
🔄 Step 4: FA Registration {'✅ Completed' if progress['steps']['fa_registration']['completed'] else '⏳ Pending'}

💡 Quick Help:
Just reply with your emergency contact details to continue!

Example: "My emergency contact is John Doe, 07123456789, my husband"

Let me know if you need any help! 🏆"""
    
    def _get_time_since_last_activity(self, player: Player) -> str:
        """Get human-readable time since last activity."""
        if not player.last_activity:
            return "Unknown"
        
        time_diff = datetime.now() - player.last_activity
        hours = int(time_diff.total_seconds() / 3600)
        
        if hours < 1:
            return "Less than 1 hour"
        elif hours < 24:
            return f"{hours} hours"
        else:
            days = hours // 24
            remaining_hours = hours % 24
            if remaining_hours == 0:
                return f"{days} days"
            else:
                return f"{days} days, {remaining_hours} hours"
    
    async def _send_telegram_message(self, telegram_id: str, message: str) -> None:
        """Send message via Telegram (placeholder for integration)."""
        # This would integrate with the Telegram bot
        # For now, just log the message
        logging.info(f"Sending reminder to Telegram ID {telegram_id}: {message[:100]}...")
    
    async def _notify_admin_reminder_sent(self, player: Player, reminder_number: int) -> None:
        """Notify admin that a reminder was sent."""
        try:
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.leadership_chat_id:
                return
            
            # Send to leadership chat (this would need to be implemented)
            logging.info(f"Admin notification sent for reminder to {player.name}")
            
        except Exception as e:
            logging.error(f"Error notifying admin about reminder: {e}")
    
    async def get_players_needing_reminders(self) -> List[Player]:
        """Get list of players who need reminders."""
        try:
            players = await self.player_service.get_team_players(self.team_id)
            return [p for p in players if p.needs_reminder()]
        except Exception as e:
            logging.error(f"Error getting players needing reminders: {e}")
            return []


def get_reminder_service(team_id: str) -> ReminderService:
    """Get reminder service instance."""
    return ReminderService(team_id) 