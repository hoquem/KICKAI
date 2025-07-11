from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from database.models_improved import Payment, PaymentType, PaymentStatus

class IPaymentService(ABC):
    @abstractmethod
    async def record_payment(self, player_id: str, amount: float, type: PaymentType, related_entity_id: Optional[str] = None, description: Optional[str] = None) -> Payment:
        pass

    @abstractmethod
    async def get_player_payments(self, player_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        pass

    @abstractmethod
    async def get_team_payments(self, team_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        pass

    @abstractmethod
    async def create_payment_request(self, player_id: str, amount: float, type: PaymentType, due_date: datetime, description: Optional[str] = None, related_entity_id: Optional[str] = None) -> Payment:
        pass

    @abstractmethod
    async def update_payment_status(self, payment_id: str, new_status: PaymentStatus, paid_date: Optional[datetime] = None) -> Payment:
        pass

    @abstractmethod
    async def list_payments(self, player_id: Optional[str] = None, status: Optional[PaymentStatus] = None, payment_type: Optional[PaymentType] = None) -> List[Payment]:
        pass

# Backward compatibility alias
PaymentServiceInterface = IPaymentService
PaymentRecord = Payment