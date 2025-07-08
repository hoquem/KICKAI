import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.firebase_client import get_firebase_client
from database.models_improved import Payment, PaymentType, PaymentStatus, Expense, ExpenseCategory
from services.match_service import get_match_service
from services.player_service import get_player_service
from core.exceptions import PaymentError, PaymentNotFoundError, create_error_context
from services.interfaces.payment_service_interface import IPaymentService
from services.interfaces.payment_gateway_interface import PaymentGatewayInterface
from .stripe_payment_gateway import StripePaymentGateway # Assuming Stripe as an example

class PaymentService(IPaymentService):
    """Service for managing payments."""

    def __init__(self, data_store=None, team_id: Optional[str] = None, payment_gateway: Optional[PaymentGatewayInterface] = None):
        if data_store is None:
            self._data_store = get_firebase_client()
        else:
            self._data_store = data_store
        self.team_id = team_id
        self._payment_gateway = payment_gateway or self._get_default_payment_gateway(team_id)
        self._player_service = get_player_service()

    def _get_default_payment_gateway(self, team_id: Optional[str]) -> PaymentGatewayInterface:
        """Returns the default payment gateway based on configuration."""
        # For now, always return Stripe as a placeholder
        # In a real scenario, this would read from bot_config_manager
        # to determine which gateway to use and its API key.
        # Example: config = get_bot_config_manager().get_payment_config(team_id)
        # if config.get("provider") == "stripe":
        #     return StripePaymentGateway(config.get("api_key"))
        return StripePaymentGateway(api_key="sk_test_mock_stripe_key") # Mock API key

    async def _get_team_id_for_player(self, player_id: str) -> str:
        """Get team_id for a player, with fallback to service team_id."""
        try:
            player = await self._player_service.get_player(player_id)
            if player and player.team_id:
                return player.team_id
        except Exception as e:
            logging.warning(f"Failed to get team_id for player {player_id}: {e}")
        
        if self.team_id:
            return self.team_id
        
        raise PaymentError(f"Team ID not available for player {player_id} and no service team_id configured", 
                          create_error_context("_get_team_id_for_player"))

    async def _validate_team_id(self, team_id: str) -> None:
        """Validate that team_id is provided and not empty."""
        if not team_id or not team_id.strip():
            raise PaymentError("Team ID is required for payment operations", 
                              create_error_context("_validate_team_id"))

    async def record_payment(self, player_id: str, amount: float, type: PaymentType, related_entity_id: Optional[str] = None, description: Optional[str] = None) -> Payment:
        """Records a new payment."""
        try:
            # Get team_id for the player
            team_id = await self._get_team_id_for_player(player_id)
            await self._validate_team_id(team_id)
            
            payment = Payment.create(
                team_id=team_id,
                player_id=player_id,
                amount=amount,
                type=type,
                status=PaymentStatus.PAID,
                paid_date=datetime.now(),
                related_entity_id=related_entity_id,
                description=description
            )

            payment_id = await self._data_store.create_document('payments', payment.to_dict(), payment.id)
            payment.id = payment_id
            logging.info(f"Payment recorded: {payment.id} for team {team_id}")

            # If this is a match fee payment, update the match's confirmed players
            if payment.type == PaymentType.MATCH_FEE and payment.related_entity_id:
                try:
                    match_service = get_match_service()
                    match = await match_service.get_match(payment.related_entity_id)
                    if match:
                        if player_id not in match.confirmed_players:
                            match.confirmed_players.append(player_id)
                            await match_service.update_match(match.id, confirmed_players=match.confirmed_players)
                            logging.info(f"Player {player_id} confirmed for match {match.id} due to payment.")
                except Exception as match_e:
                    logging.error(f"Failed to update match confirmed players for payment {payment.id}: {match_e}")

            # Create charge in payment gateway
            try:
                charge_result = await self._payment_gateway.create_charge(amount, "GBP", player_id, description)
                payment.additional_info['gateway_charge_id'] = charge_result.get('id')
                payment.additional_info['gateway_status'] = charge_result.get('status')
                await self._data_store.update_document('payments', payment.id, payment.to_dict())
                logging.info(f"Charge created in payment gateway for payment {payment.id}: {charge_result.get('id')}")
            except Exception as pg_e:
                logging.error(f"Failed to create charge in payment gateway for payment {payment.id}: {pg_e}")
                # Decide how to handle this failure: mark payment as failed, retry, etc.
                # For now, we'll just log and proceed.

            return payment
        except Exception as e:
            logging.error(f"Failed to record payment: {e}")
            raise PaymentError(f"Failed to record payment: {str(e)}", create_error_context("record_payment"))

    async def get_player_payments(self, player_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        """Retrieves payments for a specific player."""
        try:
            # Get team_id for the player to ensure we're querying the right team's payments
            team_id = await self._get_team_id_for_player(player_id)
            await self._validate_team_id(team_id)
            
            filters = [
                {'field': 'player_id', 'operator': '==', 'value': player_id},
                {'field': 'team_id', 'operator': '==', 'value': team_id}
            ]
            if status:
                filters.append({'field': 'status', 'operator': '==', 'value': status.value})
            
            data_list = await self._data_store.query_documents('payments', filters)
            return [Payment.from_dict(data) for data in data_list]
        except Exception as e:
            logging.error(f"Failed to get player payments: {e}")
            raise PaymentError(f"Failed to get player payments: {str(e)}", create_error_context("get_player_payments"))

    async def get_team_payments(self, team_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        """Retrieves payments for a specific team."""
        try:
            await self._validate_team_id(team_id)
            
            filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
            if status:
                filters.append({'field': 'status', 'operator': '==', 'value': status.value})
            
            data_list = await self._data_store.query_documents('payments', filters)
            return [Payment.from_dict(data) for data in data_list]
        except Exception as e:
            logging.error(f"Failed to get team payments: {e}")
            raise PaymentError(f"Failed to get team payments: {str(e)}", create_error_context("get_team_payments"))

    async def create_payment_request(self, player_id: str, amount: float, type: PaymentType, due_date: datetime, description: Optional[str] = None, related_entity_id: Optional[str] = None) -> Payment:
        """Creates a payment request (sets status to PENDING)."""
        try:
            # Get team_id for the player
            team_id = await self._get_team_id_for_player(player_id)
            await self._validate_team_id(team_id)
            
            payment = Payment.create(
                team_id=team_id,
                player_id=player_id,
                amount=amount,
                type=type,
                status=PaymentStatus.PENDING,
                due_date=due_date,
                related_entity_id=related_entity_id,
                description=description
            )

            payment_id = await self._data_store.create_document('payments', payment.to_dict(), payment.id)
            payment.id = payment_id
            logging.info(f"Payment request created: {payment.id} for team {team_id}")
            return payment
        except Exception as e:
            logging.error(f"Failed to create payment request: {e}")
            raise PaymentError(f"Failed to create payment request: {str(e)}", create_error_context("create_payment_request"))

    async def update_payment_status(self, payment_id: str, new_status: PaymentStatus, paid_date: Optional[datetime] = None) -> Payment:
        """Updates the status of a payment."""
        try:
            payment_data = await self._data_store.get_document('payments', payment_id)
            if not payment_data:
                raise PaymentNotFoundError(f"Payment not found: {payment_id}", create_error_context("update_payment_status"))
            
            payment = Payment.from_dict(payment_data)
            
            # Validate that the payment belongs to the correct team if team_id is set
            if self.team_id and payment.team_id != self.team_id:
                raise PaymentError(f"Payment {payment_id} does not belong to team {self.team_id}", 
                                  create_error_context("update_payment_status"))
            
            payment.status = new_status
            if new_status == PaymentStatus.PAID and paid_date is None:
                payment.paid_date = datetime.now()
            elif paid_date is not None:
                payment.paid_date = paid_date

            # If payment is being marked as PAID, interact with payment gateway
            if new_status == PaymentStatus.PAID and payment.additional_info.get('gateway_charge_id'):
                try:
                    # In a real scenario, you might confirm the charge status with the gateway
                    # For now, we assume the payment was successful if we're marking it as PAID
                    logging.info(f"Confirming payment {payment.id} with gateway: {payment.additional_info['gateway_charge_id']}")
                    # Example: status = await self._payment_gateway.get_payment_status(payment.additional_info['gateway_charge_id'])
                    # if status != "succeeded":
                    #     raise PaymentError("Gateway payment not succeeded")
                except Exception as pg_e:
                    logging.error(f"Failed to confirm payment {payment.id} with gateway: {pg_e}")
                    # Decide how to handle this failure

            await self._data_store.update_document('payments', payment.id, payment.to_dict())
            logging.info(f"Payment {payment.id} status updated to {new_status.value}")
            return payment
        except PaymentNotFoundError:
            raise
        except Exception as e:
            logging.error(f"Failed to update payment status: {e}")
            raise PaymentError(f"Failed to update payment status: {str(e)}", create_error_context("update_payment_status"))

    async def refund_payment(self, payment_id: str) -> Payment:
        """Refunds a payment by setting its status to CANCELLED."""
        try:
            payment_data = await self._data_store.get_document('payments', payment_id)
            if not payment_data:
                raise PaymentNotFoundError(f"Payment not found: {payment_id}", create_error_context("refund_payment"))

            payment = Payment.from_dict(payment_data)
            
            # Validate that the payment belongs to the correct team if team_id is set
            if self.team_id and payment.team_id != self.team_id:
                raise PaymentError(f"Payment {payment_id} does not belong to team {self.team_id}", 
                                  create_error_context("refund_payment"))
            
            if payment.status == PaymentStatus.CANCELLED:
                return payment # Already cancelled

            payment.status = PaymentStatus.CANCELLED
            payment.paid_date = None # A refund means it's no longer considered 'paid'

            # Initiate refund in payment gateway if a charge ID exists
            if payment.additional_info.get('gateway_charge_id'):
                try:
                    refund_result = await self._payment_gateway.create_refund(payment.additional_info['gateway_charge_id'], payment.amount)
                    payment.additional_info['gateway_refund_id'] = refund_result.get('id')
                    payment.additional_info['gateway_refund_status'] = refund_result.get('status')
                    logging.info(f"Refund initiated in payment gateway for payment {payment.id}: {refund_result.get('id')}")
                except Exception as pg_e:
                    logging.error(f"Failed to initiate refund in payment gateway for payment {payment.id}: {pg_e}")
                    # Decide how to handle this failure

            await self._data_store.update_document('payments', payment.id, payment.to_dict())
            logging.info(f"Payment {payment.id} refunded (status set to CANCELLED).")
            return payment
        except PaymentNotFoundError:
            raise
        except Exception as e:
            logging.error(f"Failed to refund payment: {e}")
            raise PaymentError(f"Failed to refund payment: {str(e)}", create_error_context("refund_payment"))

    async def record_expense(self, team_id: str, amount: float, category: ExpenseCategory, description: Optional[str] = None, receipt_url: Optional[str] = None) -> Expense:
        """Records a new expense for a team."""
        try:
            await self._validate_team_id(team_id)
            
            from services.expense_service import get_expense_service
            expense_service = get_expense_service()
            expense = await expense_service.record_expense(team_id, amount, category, description, receipt_url)
            return expense
        except Exception as e:
            logging.error(f"Failed to record expense: {e}")
            raise PaymentError(f"Failed to record expense: {str(e)}", create_error_context("record_expense"))


# Global payment service instances - now team-specific
_payment_service_instances: dict[str, PaymentService] = {}

def get_payment_service(team_id: Optional[str] = None) -> PaymentService:
    """Get the payment service instance for the specified team."""
    global _payment_service_instances
    
    # Use default team ID if not provided
    if not team_id:
        import os
        team_id = os.getenv('DEFAULT_TEAM_ID', 'KAI')
    
    # Return existing instance if available for this team
    if team_id in _payment_service_instances:
        return _payment_service_instances[team_id]
    
    # Create new instance for this team
    payment_service = PaymentService(team_id=team_id)
    _payment_service_instances[team_id] = payment_service
    
    logging.info(f"Created new PaymentService instance for team: {team_id}")
    return payment_service

def initialize_payment_service(team_id: Optional[str] = None) -> PaymentService:
    global _payment_service
    _payment_service = PaymentService(team_id=team_id)
    return _payment_service