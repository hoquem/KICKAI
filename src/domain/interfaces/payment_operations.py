"""
Domain interface for payment operations.

This interface defines the contract for payment-related operations
without depending on the application layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class IPaymentOperations(ABC):
    """Interface for payment operations."""
    
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