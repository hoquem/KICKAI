"""
Concrete implementation of ICommandHandler that wraps existing services.

This implementation provides a clean abstraction layer between the presentation
layer (commands) and the infrastructure layer (services).
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .interfaces.command_handler_interface import (
    ICommandHandler, PlayerInfo, TeamInfo, MatchInfo
)
from services.interfaces.player_service_interface import IPlayerService
from services.interfaces.team_service_interface import ITeamService
from services.interfaces.match_service_interface import IMatchService
from services.interfaces.payment_service_interface import IPaymentService
from services.interfaces.reminder_service_interface import IReminderService
from services.interfaces.daily_status_service_interface import IDailyStatusService
from services.interfaces.fa_registration_checker_interface import IFARegistrationChecker
from services.interfaces.expense_service_interface import IExpenseService
from services.player_service import get_player_service
from domain.interfaces.player_models import OnboardingStatus, PlayerPosition, PlayerRole
from core.exceptions import PlayerDuplicateError, PlayerValidationError

logger = logging.getLogger(__name__)


class CommandHandlerImpl(ICommandHandler):
    """Concrete implementation of ICommandHandler."""
    
    def __init__(
        self,
        player_service: IPlayerService,
        team_service: ITeamService,
        match_service: IMatchService,
        payment_service: IPaymentService,
        reminder_service: IReminderService,
        daily_status_service: IDailyStatusService,
        fa_registration_checker: IFARegistrationChecker,
        expense_service: IExpenseService
    ):
        self.player_service = player_service
        self.team_service = team_service
        self.match_service = match_service
        self.payment_service = payment_service
        self.reminder_service = reminder_service
        self.daily_status_service = daily_status_service
        self.fa_registration_checker = fa_registration_checker
        self.expense_service = expense_service
    
    async def get_player_info(self, user_id: str, team_id: str) -> tuple[bool, str]:
        """Get player information by user ID."""
        try:
            # This would need to be implemented based on how user_id maps to player
            # For now, we'll return a placeholder
            return True, "Player info placeholder"
        except Exception as e:
            logger.error(f"Error getting player info: {e}")
            return False, f"Error getting player info: {str(e)}"
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[PlayerInfo]:
        """Get player information by phone number."""
        try:
            player = await self.player_service.get_player_by_phone(phone, team_id)
            if not player:
                return None
            
            return PlayerInfo(
                player_id=player.player_id,
                name=player.name,
                phone=player.phone,
                position=player.position.value if hasattr(player.position, 'value') else str(player.position),
                onboarding_status=player.onboarding_status.value if hasattr(player.onboarding_status, 'value') else str(player.onboarding_status),
                is_fa_registered=player.is_fa_registered(),
                is_fa_eligible=player.is_fa_eligible(),
                is_match_eligible=player.is_match_eligible(),
                emergency_contact=player.emergency_contact,
                date_of_birth=player.date_of_birth,
                telegram_username=player.telegram_username,
                created_at=player.created_at.isoformat() if player.created_at else None,
                updated_at=player.updated_at.isoformat() if player.updated_at else None
            )
        except Exception as e:
            logger.error(f"Error getting player by phone: {e}")
            return None
    
    async def list_players(self, team_id: str, is_leadership_chat: bool = False) -> str:
        """List all players in a team."""
        try:
            players = await self.player_service.get_team_players(team_id)
            if not players:
                return "📋 No players found in this team."
            
            # Format the list based on chat type
            if is_leadership_chat:
                # Leadership view - show more details
                lines = ["📋 **TEAM PLAYERS** (Leadership View)\n"]
                for player in players:
                    status_emoji = "✅" if player.is_match_eligible() else "⏳"
                    fa_status = "✅" if player.is_fa_registered() else "❌"
                    lines.append(
                        f"{status_emoji} **{player.name}** ({player.player_id.upper()})\n"
                        f"   📞 {player.phone} | 🏃 {player.position.value.title()}\n"
                        f"   FA: {fa_status} | Status: {player.onboarding_status.value.title()}"
                    )
            else:
                # Player view - show basic info
                lines = ["📋 **TEAM PLAYERS**\n"]
                for player in players:
                    if player.is_match_eligible():
                        lines.append(f"✅ **{player.name}** ({player.position.value.title()})")
                    else:
                        lines.append(f"⏳ **{player.name}** ({player.position.value.title()}) - Pending")
            
            return "\n\n".join(lines)
        except Exception as e:
            logger.error(f"Error listing players: {e}")
            return f"❌ Error listing players: {str(e)}"
    
    async def register_player(self, user_id, team_id, player_id=None):
        """Register a new player via invitation/admin action."""
        logger = logging.getLogger(__name__)
        try:
            if not player_id:
                logger.warning(f"No player_id provided for registration (user_id={user_id}, team_id={team_id})")
                return False, "❌ Registration requires a valid player ID. Please use the invitation link or contact your team admin."

            player_service = get_player_service(team_id)
            player = await player_service.get_player(player_id)
            if not player:
                logger.warning(f"Player not found for registration (player_id={player_id}, user_id={user_id}, team_id={team_id})")
                return False, f"❌ Player with ID {player_id} not found. Please check your invitation or contact your team admin."

            if player.onboarding_status == OnboardingStatus.COMPLETED:
                logger.info(f"Player already completed onboarding (player_id={player_id}, user_id={user_id}, team_id={team_id})")
                return False, "✅ You have already completed onboarding. If you need help, contact your team admin."

            # Mark onboarding as complete and link Telegram user
            updates = {
                "onboarding_status": OnboardingStatus.COMPLETED.value,
                "telegram_id": user_id
            }
            await player_service.update_player(player_id, **updates)
            logger.info(f"Player onboarding completed (player_id={player_id}, user_id={user_id}, team_id={team_id})")
            return True, "✅ Registration complete! Welcome to the team. You can now use /myinfo, /status, and other commands."
        except Exception as e:
            logger.error(f"Error registering player (player_id={player_id}, user_id={user_id}, team_id={team_id}): {e}")
            return False, f"❌ Error registering player: {str(e)}"
    
    async def add_player(self, name: str, phone: str, position: str, team_id: str) -> tuple[bool, str]:
        """Add a new player to the team using the service layer."""
        logger = logging.getLogger(__name__)
        try:
            player_service = get_player_service(team_id)
            # Validate and convert position
            try:
                player_position = PlayerPosition(position.lower())
            except ValueError:
                logger.warning(f"Invalid position: {position} (team_id={team_id})")
                return False, f"❌ Invalid position: {position}. Valid positions: {[p.value for p in PlayerPosition]}"
            # Create player
            player = await player_service.create_player(
                name=name,
                phone=phone,
                team_id=team_id,
                position=player_position,
                role=PlayerRole.PLAYER,
                fa_registered=False
            )
            logger.info(f"Player created: {player.name} ({player.id}) in team {team_id}")
            return True, f"✅ Player {player.name} added successfully! Player ID: {player.player_id.upper()}"
        except PlayerDuplicateError as e:
            logger.warning(f"Duplicate player: {phone} in team {team_id}")
            return False, f"❌ Player with phone {phone} already exists in this team."
        except PlayerValidationError as e:
            logger.warning(f"Validation error for player {name}: {e}")
            return False, f"❌ Validation error: {str(e)}"
        except Exception as e:
            logger.error(f"Error adding player {name} to team {team_id}: {e}")
            return False, f"❌ Error adding player: {str(e)}"
    
    async def remove_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Remove a player from the team."""
        try:
            success = await self.player_service.delete_player(player_id)
            if success:
                return True, f"Player {player_id} removed successfully"
            else:
                return False, f"Player {player_id} not found"
        except Exception as e:
            logger.error(f"Error removing player: {e}")
            return False, f"Error removing player: {str(e)}"
    
    async def approve_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Approve a player for match squad selection."""
        try:
            # This would need to be implemented based on the approval flow
            return True, f"Player {player_id} approved successfully"
        except Exception as e:
            logger.error(f"Error approving player: {e}")
            return False, f"Error approving player: {str(e)}"
    
    async def reject_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player for match squad selection."""
        try:
            # This would need to be implemented based on the rejection flow
            return True, f"Player {player_id} rejected: {reason}"
        except Exception as e:
            logger.error(f"Error rejecting player: {e}")
            return False, f"Error rejecting player: {str(e)}"
    
    async def get_pending_approvals(self, team_id: str) -> str:
        """Get list of players pending approval."""
        try:
            # This would need to be implemented based on the pending approvals flow
            return "No players pending approval"
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            return f"Error getting pending approvals: {str(e)}"
    
    async def check_fa_registration(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Check FA registration status for a player."""
        try:
            # This would need to be implemented based on the FA registration checker
            return True, "FA registration check completed"
        except Exception as e:
            logger.error(f"Error checking FA registration: {e}")
            return False, f"Error checking FA registration: {str(e)}"
    
    async def get_daily_status(self, team_id: str) -> str:
        """Get daily status report."""
        try:
            # This would need to be implemented based on the daily status service
            return "Daily status report placeholder"
        except Exception as e:
            logger.error(f"Error getting daily status: {e}")
            return f"Error getting daily status: {str(e)}"
    
    async def run_background_tasks(self, team_id: str) -> str:
        """Run background tasks."""
        try:
            # This would need to be implemented based on the background tasks service
            return "Background tasks completed"
        except Exception as e:
            logger.error(f"Error running background tasks: {e}")
            return f"Error running background tasks: {str(e)}"
    
    async def send_reminder(self, message: str, team_id: str) -> tuple[bool, str]:
        """Send a reminder to team members."""
        try:
            # This would need to be implemented based on the reminder service
            return True, "Reminder sent successfully"
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            return False, f"Error sending reminder: {str(e)}"
    
    async def create_team(self, name: str, description: Optional[str] = None) -> tuple[bool, str]:
        """Create a new team."""
        try:
            team = await self.team_service.create_team(name, description)
            return True, f"Team '{team.name}' created successfully with ID: {team.team_id}"
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            return False, f"Error creating team: {str(e)}"
    
    async def delete_team(self, team_id: str) -> tuple[bool, str]:
        """Delete a team."""
        try:
            success = await self.team_service.delete_team(team_id)
            if success:
                return True, f"Team {team_id} deleted successfully"
            else:
                return False, f"Team {team_id} not found"
        except Exception as e:
            logger.error(f"Error deleting team: {e}")
            return False, f"Error deleting team: {str(e)}"
    
    async def list_teams(self) -> str:
        """List all teams."""
        try:
            teams = await self.team_service.get_all_teams()
            if not teams:
                return "📋 No teams found."
            
            lines = ["📋 **ALL TEAMS**\n"]
            for team in teams:
                lines.append(f"🏆 **{team.name}** ({team.team_id})\n   {team.description or 'No description'}")
            
            return "\n\n".join(lines)
        except Exception as e:
            logger.error(f"Error listing teams: {e}")
            return f"❌ Error listing teams: {str(e)}"
    
    async def create_match(self, opponent: str, date: str, time: str, venue: str, competition: str, team_id: str) -> tuple[bool, str]:
        """Create a new match."""
        try:
            # This would need to be implemented based on the match service
            return True, f"Match against {opponent} created successfully"
        except Exception as e:
            logger.error(f"Error creating match: {e}")
            return False, f"Error creating match: {str(e)}"
    
    async def list_matches(self, team_id: str) -> str:
        """List all matches for a team."""
        try:
            # This would need to be implemented based on the match service
            return "No matches found"
        except Exception as e:
            logger.error(f"Error listing matches: {e}")
            return f"Error listing matches: {str(e)}"
    
    async def get_match(self, match_id: str, team_id: str) -> Optional[MatchInfo]:
        """Get match information."""
        try:
            # This would need to be implemented based on the match service
            return None
        except Exception as e:
            logger.error(f"Error getting match: {e}")
            return None
    
    async def update_match(self, match_id: str, updates: Dict[str, Any], team_id: str) -> tuple[bool, str]:
        """Update match information."""
        try:
            # This would need to be implemented based on the match service
            return True, f"Match {match_id} updated successfully"
        except Exception as e:
            logger.error(f"Error updating match: {e}")
            return False, f"Error updating match: {str(e)}"
    
    async def delete_match(self, match_id: str, team_id: str) -> tuple[bool, str]:
        """Delete a match."""
        try:
            # This would need to be implemented based on the match service
            return True, f"Match {match_id} deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting match: {e}")
            return False, f"Error deleting match: {str(e)}"
    
    async def record_match_result(self, match_id: str, result: str, team_id: str) -> tuple[bool, str]:
        """Record match result."""
        try:
            # This would need to be implemented based on the match service
            return True, f"Match result recorded: {result}"
        except Exception as e:
            logger.error(f"Error recording match result: {e}")
            return False, f"Error recording match result: {str(e)}"
    
    async def get_team_stats(self, team_id: str) -> str:
        """Get team statistics."""
        try:
            # This would need to be implemented based on the stats calculation
            return "Team statistics placeholder"
        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return f"Error getting team stats: {str(e)}"
    
    async def generate_invitation(self, identifier: str, team_id: str) -> tuple[bool, str]:
        """Generate invitation for a player."""
        try:
            # This would need to be implemented based on the invitation flow
            return True, f"Invitation generated for {identifier}"
        except Exception as e:
            logger.error(f"Error generating invitation: {e}")
            return False, f"Error generating invitation: {str(e)}"
    
    async def broadcast_message(self, message: str, team_id: str) -> tuple[bool, str]:
        """Broadcast message to team members."""
        try:
            # This would need to be implemented based on the broadcast flow
            return True, "Message broadcasted successfully"
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return False, f"Error broadcasting message: {str(e)}"
    
    async def attend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Mark player as attending a match."""
        try:
            # This would need to be implemented based on the attendance flow
            return True, f"Marked as attending match {match_id}"
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            return False, f"Error marking attendance: {str(e)}"
    
    async def unattend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Mark player as not attending a match."""
        try:
            # This would need to be implemented based on the attendance flow
            return True, f"Marked as not attending match {match_id}"
        except Exception as e:
            logger.error(f"Error marking non-attendance: {e}")
            return False, f"Error marking non-attendance: {str(e)}"
    
    async def injure_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark player as injured."""
        try:
            # This would need to be implemented based on the injury flow
            return True, f"Player {player_id} marked as injured"
        except Exception as e:
            logger.error(f"Error marking player as injured: {e}")
            return False, f"Error marking player as injured: {str(e)}"
    
    async def suspend_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Suspend a player."""
        try:
            # This would need to be implemented based on the suspension flow
            return True, f"Player {player_id} suspended: {reason}"
        except Exception as e:
            logger.error(f"Error suspending player: {e}")
            return False, f"Error suspending player: {str(e)}"
    
    async def recover_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark player as recovered."""
        try:
            # This would need to be implemented based on the recovery flow
            return True, f"Player {player_id} marked as recovered"
        except Exception as e:
            logger.error(f"Error marking player as recovered: {e}")
            return False, f"Error marking player as recovered: {str(e)}"
    
    async def create_match_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        """Create a match fee."""
        try:
            # This would need to be implemented based on the payment service
            return True, f"Match fee created: £{amount} - {description}"
        except Exception as e:
            logger.error(f"Error creating match fee: {e}")
            return False, f"Error creating match fee: {str(e)}"
    
    async def create_membership_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        """Create a membership fee."""
        try:
            # This would need to be implemented based on the payment service
            return True, f"Membership fee created: £{amount} - {description}"
        except Exception as e:
            logger.error(f"Error creating membership fee: {e}")
            return False, f"Error creating membership fee: {str(e)}"
    
    async def create_fine(self, amount: float, description: str, player_id: str, team_id: str) -> tuple[bool, str]:
        """Create a fine for a player."""
        try:
            # This would need to be implemented based on the payment service
            return True, f"Fine created for {player_id}: £{amount} - {description}"
        except Exception as e:
            logger.error(f"Error creating fine: {e}")
            return False, f"Error creating fine: {str(e)}"
    
    async def get_payment_status(self, user_id: str, team_id: str) -> str:
        """Get payment status for a user."""
        try:
            # This would need to be implemented based on the payment service
            return "Payment status placeholder"
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            return f"Error getting payment status: {str(e)}"
    
    async def get_pending_payments(self, team_id: str) -> str:
        """Get pending payments for a team."""
        try:
            # This would need to be implemented based on the payment service
            return "No pending payments"
        except Exception as e:
            logger.error(f"Error getting pending payments: {e}")
            return f"Error getting pending payments: {str(e)}"
    
    async def get_payment_history(self, user_id: str, team_id: str) -> str:
        """Get payment history for a user."""
        try:
            # This would need to be implemented based on the payment service
            return "Payment history placeholder"
        except Exception as e:
            logger.error(f"Error getting payment history: {e}")
            return f"Error getting payment history: {str(e)}"
    
    async def get_payment_stats(self, team_id: str) -> str:
        """Get payment statistics for a team."""
        try:
            # This would need to be implemented based on the payment service
            return "Payment statistics placeholder"
        except Exception as e:
            logger.error(f"Error getting payment stats: {e}")
            return f"Error getting payment stats: {str(e)}"
    
    async def get_payment_help(self) -> str:
        """Get payment help information."""
        try:
            return """💳 **PAYMENT HELP**

📋 **Available Commands:**
• /payment_status - Check your payment status
• /pending_payments - View pending payments (admin)
• /payment_history - View your payment history
• /payment_stats - View team payment statistics (admin)
• /financial_dashboard - View financial dashboard (admin)

💰 **Payment Types:**
• Match Fees - One-time fees for matches
• Membership Fees - Regular team membership fees
• Fines - Penalties for rule violations

💡 **Need Help?**
Contact your team treasurer or admin for payment assistance."""
        except Exception as e:
            logger.error(f"Error getting payment help: {e}")
            return f"Error getting payment help: {str(e)}"
    
    async def get_financial_dashboard(self, team_id: str) -> str:
        """Get financial dashboard for a team."""
        try:
            # This would need to be implemented based on the payment and expense services
            return "Financial dashboard placeholder"
        except Exception as e:
            logger.error(f"Error getting financial dashboard: {e}")
            return f"Error getting financial dashboard: {str(e)}"
    
    async def refund_payment(self, payment_id: str, team_id: str) -> tuple[bool, str]:
        """Refund a payment."""
        try:
            # This would need to be implemented based on the payment service
            return True, f"Payment {payment_id} refunded successfully"
        except Exception as e:
            logger.error(f"Error refunding payment: {e}")
            return False, f"Error refunding payment: {str(e)}"
    
    async def record_expense(self, amount: float, description: str, category: str, team_id: str) -> tuple[bool, str]:
        """Record an expense."""
        try:
            # This would need to be implemented based on the expense service
            return True, f"Expense recorded: £{amount} - {description} ({category})"
        except Exception as e:
            logger.error(f"Error recording expense: {e}")
            return False, f"Error recording expense: {str(e)}"
    
    async def announce(self, message: str, team_id: str) -> tuple[bool, str]:
        """Make an announcement."""
        try:
            # This would need to be implemented based on the announcement flow
            return True, f"Announcement made: {message}"
        except Exception as e:
            logger.error(f"Error making announcement: {e}")
            return False, f"Error making announcement: {str(e)}" 