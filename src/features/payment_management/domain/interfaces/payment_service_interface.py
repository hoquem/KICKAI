from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from features.payment_management.domain.entities.payment import Payment, PaymentStatus, PaymentType


class IPaymentService(ABC):
    """Interface for payment service operations."""

    @abstractmethod
    async def create_payment_link(self, player_id: str, amount: float, payment_type: PaymentType,
                                description: str, due_date: datetime | None = None,
                                related_entity_id: str | None = None) -> dict[str, Any]:
        """Create a payment link for a player."""
        pass

    @abstractmethod
    async def process_payment(self, link_id: str, payment_method: str = "card") -> dict[str, Any]:
        """Process a payment using a payment link."""
        pass

    @abstractmethod
    async def get_payment_link_status(self, link_id: str) -> dict[str, Any]:
        """Get the status of a payment link."""
        pass

    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: float | None = None) -> dict[str, Any]:
        """Refund a payment."""
        pass

    @abstractmethod
    async def get_payment_analytics(self, team_id: str, start_date: datetime | None = None,
                                  end_date: datetime | None = None) -> dict[str, Any]:
        """Get payment analytics for a team."""
        pass

    @abstractmethod
    async def record_payment(self, player_id: str, amount: float, type: PaymentType,
                           description: str | None = None, related_entity_id: str | None = None) -> Payment:
        """Record a manual payment."""
        pass

    @abstractmethod
    async def get_player_payments(self, player_id: str, status: PaymentStatus | None = None) -> list[Payment]:
        """Get payments for a specific player."""
        pass

    @abstractmethod
    async def get_team_payments(self, team_id: str, status: PaymentStatus | None = None) -> list[Payment]:
        """Get payments for a specific team."""
        pass

    @abstractmethod
    async def create_payment_request(self, player_id: str, amount: float, type: PaymentType,
                                   due_date: datetime, description: str | None = None,
                                   related_entity_id: str | None = None) -> Payment:
        """Create a payment request."""
        pass

    @abstractmethod
    async def update_payment_status(self, payment_id: str, new_status: PaymentStatus,
                                  paid_date: datetime | None = None) -> Payment:
        """Update the status of a payment."""
        pass

    @abstractmethod
    async def list_payments(self, player_id: str | None = None, status: PaymentStatus | None = None,
                           payment_type: PaymentType | None = None) -> list[Payment]:
        """List payments with optional filters."""
        pass
