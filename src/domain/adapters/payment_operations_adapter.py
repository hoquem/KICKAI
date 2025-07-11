"""
Application layer adapter for payment operations.

This adapter implements the domain interface by wrapping the application layer services.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PaymentOperationsAdapter:
    """Adapter that wraps the payment service to implement domain interface."""
    
    def __init__(self, payment_service):
        self.payment_service = payment_service
        self.logger = logging.getLogger(__name__)

    async def create_match_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PaymentOperationsAdapter] create_match_fee called with amount={amount}, description={description}, team_id={team_id}")
        try:
            result = await self.payment_service.create_match_fee(amount, description, team_id)
            self.logger.info(f"[PaymentOperationsAdapter] create_match_fee result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error creating match fee: {e}", exc_info=True)
            return False, f"Error creating match fee: {str(e)}"

    async def create_membership_fee(self, amount: float, description: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PaymentOperationsAdapter] create_membership_fee called with amount={amount}, description={description}, team_id={team_id}")
        try:
            result = await self.payment_service.create_membership_fee(amount, description, team_id)
            self.logger.info(f"[PaymentOperationsAdapter] create_membership_fee result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error creating membership fee: {e}", exc_info=True)
            return False, f"Error creating membership fee: {str(e)}"

    async def create_fine(self, amount: float, description: str, player_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PaymentOperationsAdapter] create_fine called with amount={amount}, description={description}, player_id={player_id}, team_id={team_id}")
        try:
            result = await self.payment_service.create_fine(amount, description, player_id, team_id)
            self.logger.info(f"[PaymentOperationsAdapter] create_fine result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error creating fine: {e}", exc_info=True)
            return False, f"Error creating fine: {str(e)}"

    async def get_payment_status(self, user_id: str, team_id: str) -> str:
        self.logger.info(f"[PaymentOperationsAdapter] get_payment_status called with user_id={user_id}, team_id={team_id}")
        try:
            result = await self.payment_service.get_payment_status(user_id, team_id)
            self.logger.info(f"[PaymentOperationsAdapter] get_payment_status result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting payment status: {e}", exc_info=True)
            return f"Error getting payment status: {str(e)}"

    async def get_pending_payments(self, team_id: str) -> str:
        self.logger.info(f"[PaymentOperationsAdapter] get_pending_payments called with team_id={team_id}")
        try:
            result = await self.payment_service.get_pending_payments(team_id)
            self.logger.info(f"[PaymentOperationsAdapter] get_pending_payments result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting pending payments: {e}", exc_info=True)
            return f"Error getting pending payments: {str(e)}"

    async def get_payment_history(self, user_id: str, team_id: str) -> str:
        self.logger.info(f"[PaymentOperationsAdapter] get_payment_history called with user_id={user_id}, team_id={team_id}")
        try:
            result = await self.payment_service.get_payment_history(user_id, team_id)
            self.logger.info(f"[PaymentOperationsAdapter] get_payment_history result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting payment history: {e}", exc_info=True)
            return f"Error getting payment history: {str(e)}"

    async def get_payment_stats(self, team_id: str) -> str:
        self.logger.info(f"[PaymentOperationsAdapter] get_payment_stats called with team_id={team_id}")
        try:
            result = await self.payment_service.get_payment_stats(team_id)
            self.logger.info(f"[PaymentOperationsAdapter] get_payment_stats result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting payment stats: {e}", exc_info=True)
            return f"Error getting payment stats: {str(e)}"

    async def get_payment_help(self) -> str:
        self.logger.info(f"[PaymentOperationsAdapter] get_payment_help called")
        try:
            result = await self.payment_service.get_payment_help()
            self.logger.info(f"[PaymentOperationsAdapter] get_payment_help result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting payment help: {e}", exc_info=True)
            return f"Error getting payment help: {str(e)}"

    async def get_financial_dashboard(self, team_id: str) -> str:
        self.logger.info(f"[PaymentOperationsAdapter] get_financial_dashboard called with team_id={team_id}")
        try:
            result = await self.payment_service.get_financial_dashboard(team_id)
            self.logger.info(f"[PaymentOperationsAdapter] get_financial_dashboard result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error getting financial dashboard: {e}", exc_info=True)
            return f"Error getting financial dashboard: {str(e)}"

    async def refund_payment(self, payment_id: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PaymentOperationsAdapter] refund_payment called with payment_id={payment_id}, team_id={team_id}")
        try:
            result = await self.payment_service.refund_payment(payment_id, team_id)
            self.logger.info(f"[PaymentOperationsAdapter] refund_payment result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error refunding payment: {e}", exc_info=True)
            return False, f"Error refunding payment: {str(e)}"

    async def record_expense(self, amount: float, description: str, category: str, team_id: str) -> tuple[bool, str]:
        self.logger.info(f"[PaymentOperationsAdapter] record_expense called with amount={amount}, description={description}, category={category}, team_id={team_id}")
        try:
            result = await self.payment_service.record_expense(amount, description, category, team_id)
            self.logger.info(f"[PaymentOperationsAdapter] record_expense result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error recording expense: {e}", exc_info=True)
            return False, f"Error recording expense: {str(e)}" 