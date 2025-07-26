"""
FirebasePaymentRepository for Payment Management.

Implements PaymentRepositoryInterface using Firebase/Firestore as the backend.
"""

from typing import Union
from kickai.features.payment_management.domain.entities.payment import Payment
from kickai.features.payment_management.domain.repositories.payment_repository_interface import (
    PaymentRepositoryInterface,
)


class FirebasePaymentRepository(PaymentRepositoryInterface):
    """Repository for managing payments in Firebase/Firestore."""
    def __init__(self, firebase_client):
        self._client = firebase_client

    async def create(self, payment: Payment) -> Payment:
        # TODO: Implement Firestore logic
        raise NotImplementedError

    async def get_by_id(self, payment_id: str) -> Union[Payment, None]:
        # TODO: Implement Firestore logic
        raise NotImplementedError

    async def get_by_team(self, team_id: str) -> list[Payment]:
        # TODO: Implement Firestore logic
        raise NotImplementedError

    async def update(self, payment: Payment) -> Payment:
        # TODO: Implement Firestore logic
        raise NotImplementedError

    async def delete(self, payment_id: str) -> None:
        # TODO: Implement Firestore logic
        raise NotImplementedError
