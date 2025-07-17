"""
Payment Operations Interface for Payment Management Feature

Defines the contract for payment-related operations in the clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional

class IPaymentOperations(ABC):
    @abstractmethod
    async def create_match_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def create_membership_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def create_fine(self, amount: float, description: str, player_id: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def get_payment_status(self, user_id: str, team_id: str) -> str:
        pass
    @abstractmethod
    async def get_pending_payments(self, team_id: str) -> str:
        pass
    @abstractmethod
    async def get_payment_history(self, user_id: str, team_id: str) -> str:
        pass
    @abstractmethod
    async def get_payment_stats(self, team_id: str) -> str:
        pass
    @abstractmethod
    async def get_payment_help(self) -> str:
        pass
    @abstractmethod
    async def get_financial_dashboard(self, team_id: str) -> str:
        pass
    @abstractmethod
    async def refund_payment(self, payment_id: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def record_expense(self, amount: float, description: str, category: str, team_id: str) -> tuple[bool, str]:
        pass 