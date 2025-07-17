from typing import Dict, Any, Optional
from services.interfaces.payment_gateway_interface import IPaymentGateway
import logging

logger = logging.getLogger(__name__)

class MockPaymentGateway(IPaymentGateway):
    """Mock payment gateway implementation for development and testing.
    
    This will be replaced with Collectiv integration in the future.
    """
    
    def __init__(self):
        self.charges = {}
        self.charge_counter = 0
    
    async def create_charge(self, amount: float, currency: str, source: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Creates a mock charge."""
        self.charge_counter += 1
        charge_id = f"mock_charge_{self.charge_counter}"
        
        charge_data = {
            "id": charge_id,
            "amount": amount,
            "currency": currency,
            "source": source,
            "description": description or "Mock payment",
            "status": "succeeded",
            "created": "2024-01-01T00:00:00Z"
        }
        
        self.charges[charge_id] = charge_data
        logger.info(f"Created mock charge: {charge_id} for {amount} {currency}")
        
        return charge_data
    
    async def create_refund(self, charge_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Creates a mock refund."""
        if charge_id not in self.charges:
            raise ValueError(f"Charge {charge_id} not found")
        
        charge = self.charges[charge_id]
        refund_amount = amount or charge["amount"]
        
        refund_data = {
            "id": f"mock_refund_{charge_id}",
            "charge_id": charge_id,
            "amount": refund_amount,
            "status": "succeeded",
            "created": "2024-01-01T00:00:00Z"
        }
        
        logger.info(f"Created mock refund for charge {charge_id}: {refund_amount}")
        return refund_data
    
    async def get_payment_status(self, charge_id: str) -> str:
        """Retrieves the status of a mock payment."""
        if charge_id not in self.charges:
            raise ValueError(f"Charge {charge_id} not found")
        
        return self.charges[charge_id]["status"] 