from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IPaymentGateway(ABC):
    """Abstract base class for all payment gateway integrations."""

    @abstractmethod
    async def create_charge(self, amount: float, currency: str, source: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Creates a charge using the payment gateway."""
        pass

    @abstractmethod
    async def create_refund(self, charge_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Creates a refund for a given charge."""
        pass

    @abstractmethod
    async def get_payment_status(self, charge_id: str) -> str:
        """Retrieves the status of a payment."""
        pass

# Backward compatibility alias
PaymentGatewayInterface = IPaymentGateway
