from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PaymentGatewayInterface(ABC):
    """Interface for payment gateway operations."""
    
    @abstractmethod
    async def create_payment_link(self, amount: float, currency: str, 
                                description: str, reference: str,
                                expires_in_days: int = 7) -> Dict[str, Any]:
        """Create a payment link."""
        pass
    
    @abstractmethod
    async def get_payment_link_status(self, link_id: str) -> Dict[str, Any]:
        """Get the status of a payment link."""
        pass
    
    @abstractmethod
    async def process_payment(self, link_id: str, payment_method: str = "card") -> Dict[str, Any]:
        """Process a payment using a payment link."""
        pass
    
    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a payment."""
        pass
    
    @abstractmethod
    async def create_charge(self, amount: float, currency: str, source: str, 
                          description: Optional[str] = None) -> Dict[str, Any]:
        """Create a direct charge."""
        pass
    
    @abstractmethod
    async def create_refund(self, charge_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Create a refund for a charge."""
        pass
    
    @abstractmethod
    async def get_payment_status(self, charge_id: str) -> str:
        """Get the status of a payment."""
        pass 