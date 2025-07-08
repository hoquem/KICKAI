"""
Concrete implementation of ICommandOperations that uses domain adapters.

This implementation provides a clean abstraction layer between the domain
and infrastructure layers by using adapters that wrap application services.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .interfaces.command_operations import ICommandOperations, PlayerInfo, TeamInfo, MatchInfo
from .adapters import (
    PlayerOperationsAdapter,
    TeamOperationsAdapter,
    MatchOperationsAdapter,
    PaymentOperationsAdapter,
    UtilityOperationsAdapter
)

logger = logging.getLogger(__name__)


class CommandOperationsImpl(ICommandOperations):
    """Concrete implementation of command operations using adapters."""
    
    def __init__(self, player_adapter: PlayerOperationsAdapter,
                 team_adapter: TeamOperationsAdapter,
                 match_adapter: MatchOperationsAdapter,
                 payment_adapter: PaymentOperationsAdapter,
                 utility_adapter: UtilityOperationsAdapter):
        """Initialize with all required adapters."""
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.match_adapter = match_adapter
        self.payment_adapter = payment_adapter
        self.utility_adapter = utility_adapter
    
    # Player operations - delegate to player adapter
    async def get_player_info(self, user_id: str, team_id: str) -> tuple[bool, str]:
        """Get player information by user ID."""
        return await self.player_adapter.get_player_info(user_id, team_id)
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[PlayerInfo]:
        """Get player information by phone number."""
        return await self.player_adapter.get_player_by_phone(phone, team_id)
    
    async def list_players(self, team_id: str, is_leadership_chat: bool = False) -> str:
        """List all players in a team."""
        return await self.player_adapter.list_players(team_id, is_leadership_chat)
    
    async def register_player(self, user_id: str, team_id: str, player_id: Optional[str] = None) -> tuple[bool, str]:
        """Register a new player."""
        return await self.player_adapter.register_player(user_id, team_id, player_id)
    
    async def add_player(self, name: str, phone: str, position: str, team_id: str) -> tuple[bool, str]:
        """Add a new player to the team."""
        return await self.player_adapter.add_player(name, phone, position, team_id)
    
    async def remove_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Remove a player from the team."""
        return await self.player_adapter.remove_player(player_id, team_id)
    
    async def approve_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Approve a player for match squad selection."""
        return await self.player_adapter.approve_player(player_id, team_id)
    
    async def reject_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player for match squad selection."""
        return await self.player_adapter.reject_player(player_id, reason, team_id)
    
    async def get_pending_approvals(self, team_id: str) -> str:
        """Get list of players pending approval."""
        return await self.player_adapter.get_pending_approvals(team_id)
    
    async def injure_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as injured."""
        return await self.player_adapter.injure_player(player_id, team_id)
    
    async def suspend_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as suspended."""
        return await self.player_adapter.suspend_player(player_id, reason, team_id)
    
    async def recover_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as recovered."""
        return await self.player_adapter.recover_player(player_id, team_id)
    
    # Team operations - delegate to team adapter
    async def create_team(self, name: str, description: Optional[str] = None) -> tuple[bool, str]:
        """Create a new team."""
        return await self.team_adapter.create_team(name, description)
    
    async def delete_team(self, team_id: str) -> tuple[bool, str]:
        """Delete a team."""
        return await self.team_adapter.delete_team(team_id)
    
    async def list_teams(self) -> str:
        """List all teams."""
        return await self.team_adapter.list_teams()
    
    async def get_team_stats(self, team_id: str) -> str:
        """Get team statistics."""
        return await self.team_adapter.get_team_stats(team_id)
    
    # Match operations - delegate to match adapter
    async def create_match(self, opponent: str, date: str, time: str, venue: str, competition: str, team_id: str) -> tuple[bool, str]:
        """Create a new match."""
        return await self.match_adapter.create_match(opponent, date, time, venue, competition, team_id)
    
    async def list_matches(self, team_id: str) -> str:
        """List all matches for a team."""
        return await self.match_adapter.list_matches(team_id)
    
    async def get_match(self, match_id: str, team_id: str) -> Optional[MatchInfo]:
        """Get match information."""
        return await self.match_adapter.get_match(match_id, team_id)
    
    async def update_match(self, match_id: str, updates: Dict[str, Any], team_id: str) -> tuple[bool, str]:
        """Update match information."""
        return await self.match_adapter.update_match(match_id, updates, team_id)
    
    async def delete_match(self, match_id: str, team_id: str) -> tuple[bool, str]:
        """Delete a match."""
        return await self.match_adapter.delete_match(match_id, team_id)
    
    async def record_match_result(self, match_id: str, result: str, team_id: str) -> tuple[bool, str]:
        """Record match result."""
        return await self.match_adapter.record_match_result(match_id, result, team_id)
    
    async def attend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Mark player attendance for a match."""
        return await self.match_adapter.attend_match(match_id, user_id, team_id)
    
    async def unattend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Cancel player attendance for a match."""
        return await self.match_adapter.unattend_match(match_id, user_id, team_id)
    
    # Payment operations - delegate to payment adapter
    async def create_match_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        """Create a match fee."""
        return await self.payment_adapter.create_match_fee(amount, description, team_id)
    
    async def create_membership_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        """Create a membership fee."""
        return await self.payment_adapter.create_membership_fee(amount, description, team_id)
    
    async def create_fine(self, amount: float, description: str, player_id: str, team_id: str) -> tuple[bool, str]:
        """Create a fine for a player."""
        return await self.payment_adapter.create_fine(amount, description, player_id, team_id)
    
    async def get_payment_status(self, user_id: str, team_id: str) -> str:
        """Get payment status for a user."""
        return await self.payment_adapter.get_payment_status(user_id, team_id)
    
    async def get_pending_payments(self, team_id: str) -> str:
        """Get pending payments for a team."""
        return await self.payment_adapter.get_pending_payments(team_id)
    
    async def get_payment_history(self, user_id: str, team_id: str) -> str:
        """Get payment history for a user."""
        return await self.payment_adapter.get_payment_history(user_id, team_id)
    
    async def get_payment_stats(self, team_id: str) -> str:
        """Get payment statistics for a team."""
        return await self.payment_adapter.get_payment_stats(team_id)
    
    async def get_payment_help(self) -> str:
        """Get payment help information."""
        return await self.payment_adapter.get_payment_help()
    
    async def get_financial_dashboard(self, team_id: str) -> str:
        """Get financial dashboard for a team."""
        return await self.payment_adapter.get_financial_dashboard(team_id)
    
    async def refund_payment(self, payment_id: str, team_id: str) -> tuple[bool, str]:
        """Refund a payment."""
        return await self.payment_adapter.refund_payment(payment_id, team_id)
    
    async def record_expense(self, amount: float, description: str, category: str, team_id: str) -> tuple[bool, str]:
        """Record an expense."""
        return await self.payment_adapter.record_expense(amount, description, category, team_id)
    
    # Utility operations - delegate to utility adapter
    async def check_fa_registration(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Check FA registration status for a player."""
        return await self.utility_adapter.check_fa_registration(player_id, team_id)
    
    async def get_daily_status(self, team_id: str) -> str:
        """Get daily status report."""
        return await self.utility_adapter.get_daily_status(team_id)
    
    async def run_background_tasks(self, team_id: str) -> str:
        """Run background tasks."""
        return await self.utility_adapter.run_background_tasks(team_id)
    
    async def send_reminder(self, message: str, team_id: str) -> tuple[bool, str]:
        """Send a reminder to team members."""
        return await self.utility_adapter.send_reminder(message, team_id)
    
    async def generate_invitation(self, identifier: str, team_id: str) -> tuple[bool, str]:
        """Generate an invitation for a player."""
        return await self.utility_adapter.generate_invitation(identifier, team_id)
    
    async def broadcast_message(self, message: str, team_id: str) -> tuple[bool, str]:
        """Broadcast a message to team members."""
        return await self.utility_adapter.broadcast_message(message, team_id)
    
    async def announce(self, message: str, team_id: str) -> tuple[bool, str]:
        """Send an announcement."""
        return await self.utility_adapter.announce(message, team_id)
    
    async def get_user_role(self, user_id: str, team_id: str) -> str:
        """Get user role for permission checking."""
        return await self.utility_adapter.get_user_role(user_id, team_id) 