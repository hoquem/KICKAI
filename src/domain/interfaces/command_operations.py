"""
Domain interface for command operations.

This interface defines the contract for all command operations
without depending on the application layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from .player_operations import PlayerInfo
from .team_operations import TeamInfo
from .match_operations import MatchInfo


class ICommandOperations(ABC):
    """Interface for all command operations."""
    
    # Player operations
    @abstractmethod
    async def get_player_info(self, user_id: str, team_id: str) -> tuple[bool, str]:
        """Get player information by user ID."""
        pass
    
    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[PlayerInfo]:
        """Get player information by phone number."""
        pass
    
    @abstractmethod
    async def list_players(self, team_id: str, is_leadership_chat: bool = False) -> str:
        """List all players in a team."""
        pass
    
    @abstractmethod
    async def register_player(self, user_id: str, team_id: str, player_id: Optional[str] = None) -> tuple[bool, str]:
        """Register a new player."""
        pass
    
    @abstractmethod
    async def add_player(self, name: str, phone: str, position: str, team_id: str) -> tuple[bool, str]:
        """Add a new player to the team."""
        pass
    
    @abstractmethod
    async def remove_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Remove a player from the team."""
        pass
    
    @abstractmethod
    async def approve_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Approve a player for match squad selection."""
        pass
    
    @abstractmethod
    async def reject_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player for match squad selection."""
        pass
    
    @abstractmethod
    async def reject_player_by_identifier(self, identifier: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player by player ID or phone number."""
        pass

    @abstractmethod
    async def update_player_info(self, user_id: str, field: str, value: str, team_id: str) -> tuple[bool, str]:
        """Update a player's information."""
        pass
    
    @abstractmethod
    async def get_pending_approvals(self, team_id: str) -> str:
        """Get list of players pending approval."""
        pass
    
    @abstractmethod
    async def injure_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as injured."""
        pass
    
    @abstractmethod
    async def suspend_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as suspended."""
        pass
    
    @abstractmethod
    async def recover_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as recovered."""
        pass
    
    # Team operations
    @abstractmethod
    async def create_team(self, name: str, description: Optional[str] = None) -> tuple[bool, str]:
        """Create a new team."""
        pass
    
    @abstractmethod
    async def delete_team(self, team_id: str) -> tuple[bool, str]:
        """Delete a team."""
        pass
    
    @abstractmethod
    async def list_teams(self) -> str:
        """List all teams."""
        pass
    
    @abstractmethod
    async def get_team_stats(self, team_id: str) -> str:
        """Get team statistics."""
        pass
    
    # Match operations
    @abstractmethod
    async def create_match(self, opponent: str, date: str, time: str, venue: str, competition: str, team_id: str) -> tuple[bool, str]:
        """Create a new match."""
        pass
    
    @abstractmethod
    async def list_matches(self, team_id: str) -> str:
        """List all matches for a team."""
        pass
    
    @abstractmethod
    async def get_match(self, match_id: str, team_id: str) -> Optional[MatchInfo]:
        """Get match information."""
        pass
    
    @abstractmethod
    async def update_match(self, match_id: str, updates: Dict[str, Any], team_id: str) -> tuple[bool, str]:
        """Update match information."""
        pass
    
    @abstractmethod
    async def delete_match(self, match_id: str, team_id: str) -> tuple[bool, str]:
        """Delete a match."""
        pass
    
    @abstractmethod
    async def record_match_result(self, match_id: str, result: str, team_id: str) -> tuple[bool, str]:
        """Record match result."""
        pass
    
    @abstractmethod
    async def attend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Mark player attendance for a match."""
        pass
    
    @abstractmethod
    async def unattend_match(self, match_id: str, user_id: str, team_id: str) -> tuple[bool, str]:
        """Cancel player attendance for a match."""
        pass
    
    # Payment operations
    @abstractmethod
    async def create_match_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        """Create a match fee."""
        pass
    
    @abstractmethod
    async def create_membership_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        """Create a membership fee."""
        pass
    
    @abstractmethod
    async def create_fine(self, amount: float, description: str, player_id: str, team_id: str) -> tuple[bool, str]:
        """Create a fine for a player."""
        pass
    
    @abstractmethod
    async def get_payment_status(self, user_id: str, team_id: str) -> str:
        """Get payment status for a user."""
        pass
    
    @abstractmethod
    async def get_pending_payments(self, team_id: str) -> str:
        """Get pending payments for a team."""
        pass
    
    @abstractmethod
    async def get_payment_history(self, user_id: str, team_id: str) -> str:
        """Get payment history for a user."""
        pass
    
    @abstractmethod
    async def get_payment_stats(self, team_id: str) -> str:
        """Get payment statistics for a team."""
        pass
    
    @abstractmethod
    async def get_payment_help(self) -> str:
        """Get payment help information."""
        pass
    
    @abstractmethod
    async def get_financial_dashboard(self, team_id: str) -> str:
        """Get financial dashboard for a team."""
        pass
    
    @abstractmethod
    async def refund_payment(self, payment_id: str, team_id: str) -> tuple[bool, str]:
        """Refund a payment."""
        pass
    
    @abstractmethod
    async def record_expense(self, amount: float, description: str, category: str, team_id: str) -> tuple[bool, str]:
        """Record an expense."""
        pass
    
    # Utility operations
    @abstractmethod
    async def check_fa_registration(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Check FA registration status for a player."""
        pass
    
    @abstractmethod
    async def get_daily_status(self, team_id: str) -> str:
        """Get daily status report."""
        pass
    
    @abstractmethod
    async def run_background_tasks(self, team_id: str) -> str:
        """Run background tasks."""
        pass
    
    @abstractmethod
    async def send_reminder(self, message: str, team_id: str) -> tuple[bool, str]:
        """Send a reminder to team members."""
        pass
    
    @abstractmethod
    async def generate_invitation(self, identifier: str, team_id: str) -> tuple[bool, str]:
        """Generate an invitation for a player."""
        pass
    
    @abstractmethod
    async def broadcast_message(self, message: str, team_id: str) -> tuple[bool, str]:
        """Broadcast a message to team members."""
        pass
    
    @abstractmethod
    async def announce(self, message: str, team_id: str) -> tuple[bool, str]:
        """Send an announcement."""
        pass
    
    @abstractmethod
    async def get_user_role(self, user_id: str, team_id: str) -> str:
        """Get user role for permission checking."""
        pass 