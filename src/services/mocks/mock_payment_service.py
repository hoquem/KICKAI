from services.interfaces.payment_service_interface import PaymentServiceInterface, PaymentRecord, PaymentStatus, PaymentType
from typing import List, Optional, Dict, Any

class MockPaymentService(PaymentServiceInterface):
    def __init__(self):
        self.payments = []

    def create_payment(self, player_id: str, amount: float, payment_type: PaymentType, metadata: Optional[Dict[str, Any]] = None) -> PaymentRecord:
        record = PaymentRecord(
            id=f"mock_{len(self.payments)+1}",
            player_id=player_id,
            amount=amount,
            payment_type=payment_type,
            status=PaymentStatus.PAID,
            metadata=metadata or {},
        )
        self.payments.append(record)
        return record

    def get_payment_status(self, payment_id: str) -> PaymentStatus:
        for p in self.payments:
            if p.id == payment_id:
                return p.status
        return PaymentStatus.FAILED

    def list_payments(self, player_id: Optional[str] = None, payment_type: Optional[PaymentType] = None) -> List[PaymentRecord]:
        results = self.payments
        if player_id:
            results = [p for p in results if p.player_id == player_id]
        if payment_type:
            results = [p for p in results if p.payment_type == payment_type]
        return results

    def get_payment_statistics(self, team_id: Optional[str] = None) -> Dict[str, Any]:
        return {"total": len(self.payments)} 