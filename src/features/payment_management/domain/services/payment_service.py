import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.firebase_client import get_firebase_client
from features.payment_management.domain.entities.payment import Payment, PaymentType, PaymentStatus
from features.payment_management.domain.entities.expense import Expense, ExpenseCategory
from features.player_registration.domain.interfaces.player_lookup_interface import IPlayerLookup
from src.core.exceptions import PaymentError, PaymentNotFoundError, create_error_context
from features.payment_management.domain.interfaces.payment_service_interface import IPaymentService
from features.payment_management.domain.interfaces.payment_gateway_interface import IPaymentGateway
from features.payment_management.infrastructure.collectiv_payment_gateway import MockCollectivPaymentGateway
from src.utils.validation_utils import validate_payment_details

class PaymentService(IPaymentService):
    """Service for managing payments with Collectiv integration."""
    def __init__(self, data_store, payment_gateway: Optional[IPaymentGateway] = None, player_lookup: Optional[IPlayerLookup] = None, team_id: Optional[str] = None):
        self._data_store = data_store
        self.team_id = team_id
        self._payment_gateway = payment_gateway or self._get_default_payment_gateway(team_id)
        self._player_lookup = player_lookup

    def _get_default_payment_gateway(self, team_id: Optional[str]) -> IPaymentGateway:
        """Returns the default payment gateway based on configuration."""
        # Use MockCollectivPaymentGateway for development/testing
        # In production, this would check configuration and use real Collectiv API
        return MockCollectivPaymentGateway(
            api_key="mock_collectiv_key",
            base_url="https://api.collectiv.com"
        )

    async def _get_team_id_for_player(self, *, player_id: str) -> str:
        """Get team ID for a player."""
        try:
            team_id = await self._player_lookup.get_player_team_id(player_id)
            return team_id if team_id else self.team_id
        except Exception:
            return self.team_id

    async def _validate_team_id(self, *, team_id: str):
        """Validate that team_id is set."""
        if not team_id:
            raise PaymentError("Team ID is required", create_error_context("_validate_team_id"))

    async def create_payment_link(self, player_id: str, amount: float, payment_type: PaymentType, 
                                description: str, due_date: Optional[datetime] = None,
                                related_entity_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a payment link for a player using Collectiv.
        
        Args:
            player_id: Player ID
            amount: Payment amount
            payment_type: Type of payment
            description: Payment description
            due_date: Due date for payment
            related_entity_id: Related entity ID (e.g., match ID)
            
        Returns:
            Dict containing payment link details
        """
        try:
            team_id = await self._get_team_id_for_player(player_id=player_id)
            await self._validate_team_id(team_id=team_id)
            
            # Create payment link using Collectiv
            reference = f"{team_id}_{player_id}_{int(datetime.now().timestamp())}"
            link_data = await self._payment_gateway.create_payment_link(
                amount=amount,
                currency="GBP",
                description=description,
                reference=reference
            )
            
            # Store payment link in Firestore
            payment_link_doc = {
                "link_id": link_data["id"],
                "player_id": player_id,
                "team_id": team_id,
                "amount": amount,
                "currency": "GBP",
                "payment_type": payment_type.value,
                "description": description,
                "status": "pending",
                "payment_url": link_data["url"],
                "reference": reference,
                "due_date": due_date.isoformat() if due_date else None,
                "related_entity_id": related_entity_id,
                "created_at": datetime.now().isoformat(),
                "expires_at": link_data["expires_at"]
            }
            
            await self._data_store.create_document('payment_links', payment_link_doc, link_data["id"])
            
            # Create payment record
            payment = Payment.create(
                team_id=team_id,
                player_id=player_id,
                amount=amount,
                type=payment_type,
                status=PaymentStatus.PENDING,
                due_date=due_date,
                related_entity_id=related_entity_id,
                description=description
            )
            
            payment_id = await self._data_store.create_document('payments', payment.to_dict(), payment.id)
            payment.id = payment_id
            
            logging.info(f"✅ Created payment link for player {player_id}: £{amount}")
            
            return {
                "payment_id": payment_id,
                "link_id": link_data["id"],
                "payment_url": link_data["url"],
                "amount": amount,
                "description": description,
                "status": "pending",
                "expires_at": link_data["expires_at"]
            }
            
        except Exception as e:
            logging.error(f"Failed to create payment link: {e}")
            raise PaymentError(f"Failed to create payment link: {str(e)}", create_error_context("create_payment_link"))

    async def process_payment(self, link_id: str, payment_method: str = "card") -> Dict[str, Any]:
        """
        Process a payment using a payment link.
        
        Args:
            link_id: Payment link ID
            payment_method: Payment method used
            
        Returns:
            Dict containing transaction details
        """
        try:
            # Get payment link from Firestore
            link_doc = await self._data_store.get_document('payment_links', link_id)
            if not link_doc:
                raise PaymentNotFoundError(f"Payment link {link_id} not found")
            
            # Process payment through Collectiv
            transaction_data = await self._payment_gateway.process_payment(link_id, payment_method)
            
            # Update payment link status
            link_doc["status"] = "paid"
            link_doc["paid_at"] = datetime.now().isoformat()
            link_doc["transaction_id"] = transaction_data["id"]
            link_doc["payment_method"] = payment_method
            
            await self._data_store.update_document('payment_links', link_id, link_doc)
            
            # Store transaction in Firestore
            transaction_doc = {
                "transaction_id": transaction_data["id"],
                "link_id": link_id,
                "player_id": link_doc["player_id"],
                "team_id": link_doc["team_id"],
                "amount": transaction_data["amount"],
                "currency": transaction_data["currency"],
                "payment_method": payment_method,
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "transaction_data": transaction_data
            }
            
            await self._data_store.create_document('transactions', transaction_doc, transaction_data["id"])
            
            # Update payment record
            payment_id = link_doc.get("payment_id")
            if payment_id:
                payment_doc = await self._data_store.get_document('payments', payment_id)
                if payment_doc:
                    payment_doc["status"] = PaymentStatus.PAID.value
                    payment_doc["paid_date"] = datetime.now().isoformat()
                    payment_doc["transaction_id"] = transaction_data["id"]
                    await self._data_store.update_document('payments', payment_id, payment_doc)
            
            # If this is a match fee payment, update the match's confirmed players
            if link_doc.get("payment_type") == PaymentType.MATCH_FEE.value and link_doc.get("related_entity_id"):
                try:
                    # match_service = get_match_service() # This line is removed
                    # match = await match_service.get_match(link_doc["related_entity_id"]) # This line is removed
                    # if match and link_doc["player_id"] not in match.confirmed_players: # This line is removed
                    #     match.confirmed_players.append(link_doc["player_id"]) # This line is removed
                    #     await match_service.update_match(match.id, confirmed_players=match.confirmed_players) # This line is removed
                    #     logging.info(f"Player {link_doc['player_id']} confirmed for match {match.id} due to payment.") # This line is removed
                    pass # Placeholder for match service usage
                except Exception as match_e:
                    logging.error(f"Failed to update match confirmed players for payment {link_id}: {match_e}")
            
            logging.info(f"✅ Processed payment for link {link_id}: £{transaction_data['amount']}")
            
            return transaction_data
            
        except Exception as e:
            logging.error(f"Failed to process payment: {e}")
            raise PaymentError(f"Failed to process payment: {str(e)}", create_error_context("process_payment"))

    async def get_payment_link_status(self, link_id: str) -> Dict[str, Any]:
        """
        Get the status of a payment link.
        
        Args:
            link_id: Payment link ID
            
        Returns:
            Dict containing payment link status
        """
        try:
            link_doc = await self._data_store.get_document('payment_links', link_id)
            if not link_doc:
                raise PaymentNotFoundError(f"Payment link {link_id} not found")
            
            return {
                "link_id": link_id,
                "status": link_doc["status"],
                "amount": link_doc["amount"],
                "description": link_doc["description"],
                "payment_url": link_doc["payment_url"],
                "expires_at": link_doc.get("expires_at"),
                "paid_at": link_doc.get("paid_at"),
                "transaction_id": link_doc.get("transaction_id")
            }
            
        except Exception as e:
            logging.error(f"Failed to get payment link status: {e}")
            raise PaymentError(f"Failed to get payment link status: {str(e)}", create_error_context("get_payment_link_status"))

    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Refund a payment.
        
        Args:
            transaction_id: Transaction ID to refund
            amount: Amount to refund (if None, refunds full amount)
            
        Returns:
            Dict containing refund details
        """
        try:
            # Get transaction from Firestore
            transaction_doc = await self._data_store.get_document('transactions', transaction_id)
            if not transaction_doc:
                raise PaymentNotFoundError(f"Transaction {transaction_id} not found")
            
            # Process refund through Collectiv
            refund_amount = amount or transaction_doc["amount"]
            refund_data = await self._payment_gateway.refund_payment(transaction_id, refund_amount)
            
            # Store refund in Firestore
            refund_doc = {
                "refund_id": refund_data["id"],
                "transaction_id": transaction_id,
                "amount": refund_amount,
                "currency": refund_data["currency"],
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "refund_data": refund_data
            }
            
            await self._data_store.create_document('refunds', refund_doc, refund_data["id"])
            
            logging.info(f"✅ Processed refund for transaction {transaction_id}: £{refund_amount}")
            
            return refund_data
            
        except Exception as e:
            logging.error(f"Failed to refund payment: {e}")
            raise PaymentError(f"Failed to refund payment: {str(e)}", create_error_context("refund_payment"))

    async def get_payment_analytics(self, team_id: str, start_date: Optional[datetime] = None, 
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get payment analytics for a team.
        
        Args:
            team_id: Team ID
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dict containing payment analytics
        """
        try:
            # Get payments for the team
            payments = await self.get_team_payments(team_id)
            
            # Filter by date range if provided
            if start_date:
                payments = [p for p in payments if p.created_date >= start_date]
            if end_date:
                payments = [p for p in payments if p.created_date <= end_date]
            
            # Calculate analytics
            total_payments = len(payments)
            total_amount = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
            pending_amount = sum(p.amount for p in payments if p.status == PaymentStatus.PENDING)
            overdue_amount = sum(p.amount for p in payments if p.status == PaymentStatus.OVERDUE)
            
            # Group by payment type
            payment_types = {}
            for payment in payments:
                payment_type = payment.type.value
                if payment_type not in payment_types:
                    payment_types[payment_type] = {"count": 0, "amount": 0}
                payment_types[payment_type]["count"] += 1
                if payment.status == PaymentStatus.PAID:
                    payment_types[payment_type]["amount"] += payment.amount
            
            return {
                "team_id": team_id,
                "total_payments": total_payments,
                "total_amount": total_amount,
                "pending_amount": pending_amount,
                "overdue_amount": overdue_amount,
                "payment_types": payment_types,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to get payment analytics: {e}")
            raise PaymentError(f"Failed to get payment analytics: {str(e)}", create_error_context("get_payment_analytics"))

    async def record_payment(self, player_id: str, amount: float, type: PaymentType, related_entity_id: Optional[str] = None, description: Optional[str] = None) -> Payment:
        """
        Record a manual payment (e.g., cash payment).
        
        Args:
            player_id: Player ID
            amount: Payment amount
            type: Payment type
            related_entity_id: Related entity ID
            description: Payment description
            
        Returns:
            Payment object
        """
        try:
            team_id = await self._get_team_id_for_player(player_id=player_id)
            await self._validate_team_id(team_id=team_id)
            
            payment = Payment.create(
                team_id=team_id,
                player_id=player_id,
                amount=amount,
                type=type,
                status=PaymentStatus.PAID,
                related_entity_id=related_entity_id,
                description=description or f"Manual {type.value} payment"
            )
            
            payment_id = await self._data_store.create_document('payments', payment.to_dict(), payment.id)
            payment.id = payment_id
            
            logging.info(f"✅ Recorded manual payment for player {player_id}: £{amount}")
            
            return payment
            
        except Exception as e:
            logging.error(f"Failed to record payment: {e}")
            raise PaymentError(f"Failed to record payment: {str(e)}", create_error_context("record_payment"))

    async def get_player_payments(self, player_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        """
        Get payments for a specific player.
        
        Args:
            player_id: Player ID
            status: Optional payment status filter
            
        Returns:
            List of Payment objects
        """
        try:
            filters = [("player_id", "==", player_id)]
            if status:
                filters.append(("status", "==", status.value))
            
            payment_docs = await self._data_store.query_documents('payments', filters)
            return [Payment.from_dict(doc) for doc in payment_docs]
            
        except Exception as e:
            logging.error(f"Failed to get player payments: {e}")
            raise PaymentError(f"Failed to get player payments: {str(e)}", create_error_context("get_player_payments"))

    async def get_team_payments(self, team_id: str, status: Optional[PaymentStatus] = None) -> List[Payment]:
        """
        Get payments for a specific team.
        
        Args:
            team_id: Team ID
            status: Optional payment status filter
            
        Returns:
            List of Payment objects
        """
        try:
            filters = [("team_id", "==", team_id)]
            if status:
                filters.append(("status", "==", status.value))
            
            payment_docs = await self._data_store.query_documents('payments', filters)
            return [Payment.from_dict(doc) for doc in payment_docs]
            
        except Exception as e:
            logging.error(f"Failed to get team payments: {e}")
            raise PaymentError(f"Failed to get team payments: {str(e)}", create_error_context("get_team_payments"))

    async def create_payment_request(self, player_id: str, amount: float, type: PaymentType, due_date: datetime, description: Optional[str] = None, related_entity_id: Optional[str] = None) -> Payment:
        """
        Create a payment request (manual payment tracking).
        
        Args:
            player_id: Player ID
            amount: Payment amount
            type: Payment type
            due_date: Due date
            description: Payment description
            related_entity_id: Related entity ID
            
        Returns:
            Payment object
        """
        try:
            team_id = await self._get_team_id_for_player(player_id=player_id)
            await self._validate_team_id(team_id=team_id)
            
            payment = Payment.create(
                team_id=team_id,
                player_id=player_id,
                amount=amount,
                type=type,
                status=PaymentStatus.PENDING,
                due_date=due_date,
                related_entity_id=related_entity_id,
                description=description or f"{type.value} payment request"
            )
            
            payment_id = await self._data_store.create_document('payments', payment.to_dict(), payment.id)
            payment.id = payment_id
            
            logging.info(f"✅ Created payment request for player {player_id}: £{amount}")
            
            return payment
            
        except Exception as e:
            logging.error(f"Failed to create payment request: {e}")
            raise PaymentError(f"Failed to create payment request: {str(e)}", create_error_context("create_payment_request"))

    async def update_payment_status(self, payment_id: str, new_status: PaymentStatus, paid_date: Optional[datetime] = None) -> Payment:
        """
        Update the status of a payment.
        
        Args:
            payment_id: Payment ID
            new_status: New payment status
            paid_date: Date when payment was made (for PAID status)
            
        Returns:
            Updated Payment object
        """
        try:
            payment_doc = await self._data_store.get_document('payments', payment_id)
            if not payment_doc:
                raise PaymentNotFoundError(f"Payment {payment_id} not found")
            
            payment_doc["status"] = new_status.value
            if new_status == PaymentStatus.PAID and paid_date:
                payment_doc["paid_date"] = paid_date.isoformat()
            
            await self._data_store.update_document('payments', payment_id, payment_doc)
            
            payment = Payment.from_dict(payment_doc)
            payment.id = payment_id
            
            logging.info(f"✅ Updated payment {payment_id} status to {new_status.value}")
            
            return payment
            
        except Exception as e:
            logging.error(f"Failed to update payment status: {e}")
            raise PaymentError(f"Failed to update payment status: {str(e)}", create_error_context("update_payment_status"))

    async def list_payments(self, player_id: Optional[str] = None, status: Optional[PaymentStatus] = None, payment_type: Optional[PaymentType] = None) -> List[Payment]:
        """
        List payments with optional filters.
        
        Args:
            player_id: Optional player ID filter
            status: Optional status filter
            payment_type: Optional payment type filter
            
        Returns:
            List of Payment objects
        """
        try:
            filters = []
            if player_id:
                filters.append(("player_id", "==", player_id))
            if status:
                filters.append(("status", "==", status.value))
            if payment_type:
                filters.append(("type", "==", payment_type.value))
            
            payment_docs = await self._data_store.query_documents('payments', filters)
            return [Payment.from_dict(doc) for doc in payment_docs]
            
        except Exception as e:
            logging.error(f"Failed to list payments: {e}")
            raise PaymentError(f"Failed to list payments: {str(e)}", create_error_context("list_payments")) 