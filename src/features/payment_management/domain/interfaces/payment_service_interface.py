from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.database.models_improved import Payment, PaymentType, PaymentStatus

class IPaymentService(ABC):
    """Interface for payment service operations."""
    
    @abstractmethod
    async def create_payment_link(self, player_id: str, amount: float, payment_type: PaymentType, 
                                description: str, due_date: Optional[datetime] = None,
                                related_entity_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a payment link for a player."""
        pass
    
    @abstractmethod
    async def process_payment(self, link_id: str, payment_method: str = "card") -> Dict[str, Any]:
        """Process a payment using a payment link."""
        pass
    
    @abstractmethod
    async def get_payment_link_status(self, link_id: str) -> Dict[str, Any]:
        """Get the status of a payment link."""
        pass
    
    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a payment."""
        pass
    
    @abstractmethod
    async def get_payment_analytics(self, team_id: str, start_date: Optional[datetime] = None, 
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get payment analytics for a team."""
        pass
    
    @abstractmethod
    async def record_payment(self, player_id: str, amount: float, type: PaymentType, 
                           related_entity_id: Optional[str] = None, description: Optional[str] = None) -> Payment:
        """Record a manual payment."""
        pass
    
    @abstractmethod
    async def get_player_payments(self, player_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        """Get payments for a specific player."""
        pass
    
    @abstractmethod
    async def get_team_payments(self, team_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        """Get payments for a specific team."""
        pass
    
    @abstractmethod
    async def create_payment_request(self, player_id: str, amount: float, type: PaymentType, 
                                   due_date: datetime, description: Optional[str] = None, 
                                   related_entity_id: Optional[str] = None) -> Payment:
        """Create a payment request."""
        pass
    
    @abstractmethod
    async def update_payment_status(self, payment_id: str, new_status: PaymentStatus, 
                                  paid_date: Optional[datetime] = None) -> Payment:
        """Update the status of a payment."""
        pass
    
    @abstractmethod
    async def list_payments(self, player_id: Optional[str] = None, status: Optional[PaymentStatus] = None, 
                           payment_type: Optional[PaymentType] = None) -> List[Payment]:
        """List payments with optional filters."""
        pass 