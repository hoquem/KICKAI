"""
Payment Service Interface

This module defines the interface for payment operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core.exceptions import PaymentError


class IPaymentService(ABC):
    """Interface for payment operations."""
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if payment system is enabled."""
        pass
    
    @abstractmethod
    async def create_payment_request(self, 
                                   player_id: str,
                                   amount: float,
                                   payment_type: str,
                                   description: str = "",
                                   due_date: Optional[datetime] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new payment request."""
        pass
    
    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get the status of a payment."""
        pass
    
    @abstractmethod
    async def create_match_fee_payment(self, 
                                     player_id: str,
                                     amount: float,
                                     match_id: str,
                                     match_date: datetime,
                                     description: str = "") -> Dict[str, Any]:
        """Create a match fee payment request."""
        pass
    
    @abstractmethod
    async def create_membership_fee_payment(self,
                                          player_id: str,
                                          amount: float,
                                          period: str,
                                          description: str = "") -> Dict[str, Any]:
        """Create a membership fee payment request."""
        pass
    
    @abstractmethod
    async def create_fine_payment(self,
                                player_id: str,
                                amount: float,
                                reason: str,
                                due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Create a fine payment request."""
        pass
    
    @abstractmethod
    async def get_pending_payments(self, player_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pending payments for a player or team."""
        pass
    
    @abstractmethod
    async def get_payment_history(self, player_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get payment history for a player or team."""
        pass
    
    @abstractmethod
    def get_payment_stats(self) -> Dict[str, Any]:
        """Get payment statistics."""
        pass 