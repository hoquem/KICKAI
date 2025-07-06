"""
Mock Payment Service

This module provides a mock implementation of the PaymentService for testing.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid

from ...core.exceptions import PaymentError
from ..interfaces.payment_service_interface import IPaymentService

logger = logging.getLogger(__name__)

@dataclass
class MockPaymentRequest:
    """Mock payment request for testing."""
    id: str
    team_id: str
    player_id: str
    amount: float
    currency: str = "GBP"
    payment_type: str = "match_fee"
    description: str = ""
    due_date: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MockPaymentResponse:
    """Mock payment response for testing."""
    payment_id: str
    status: str
    amount: float
    currency: str
    payment_url: Optional[str] = None
    reference: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class MockPaymentService(IPaymentService):
    """Mock implementation of PaymentService for testing."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.payment_requests: Dict[str, MockPaymentRequest] = {}
        self.payment_responses: Dict[str, MockPaymentResponse] = {}
        self.mock_enabled = True
        
        logger.info(f"✅ Mock Payment Service initialized for team {team_id}")
    
    def is_enabled(self) -> bool:
        """Check if payment system is enabled."""
        return self.mock_enabled
    
    def set_enabled(self, enabled: bool):
        """Set whether the payment system is enabled."""
        self.mock_enabled = enabled
    
    async def create_payment_request(self, 
                                   player_id: str,
                                   amount: float,
                                   payment_type: str,
                                   description: str = "",
                                   due_date: Optional[datetime] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new payment request."""
        try:
            if not self.is_enabled():
                raise PaymentError("Payment system is not enabled")
            
            # Validate inputs
            if amount <= 0:
                raise PaymentError("Payment amount must be greater than 0")
            
            if not player_id:
                raise PaymentError("Player ID is required")
            
            # Generate payment request ID
            payment_id = f"mock_pay_{self.team_id}_{player_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create payment request
            payment_request = MockPaymentRequest(
                id=payment_id,
                team_id=self.team_id,
                player_id=player_id,
                amount=amount,
                payment_type=payment_type,
                description=description,
                due_date=due_date,
                metadata=metadata or {}
            )
            
            # Store payment request
            self.payment_requests[payment_id] = payment_request
            
            # Create mock payment response
            payment_response = MockPaymentResponse(
                payment_id=str(uuid.uuid4()),
                status="pending",
                amount=amount,
                currency="GBP",
                payment_url=f"https://mock-payment.example.com/pay/{payment_id}",
                reference=payment_id,
                metadata=payment_request.metadata
            )
            
            # Store payment response
            self.payment_responses[payment_id] = payment_response
            
            logger.info(f"✅ Created mock payment request: {payment_id} for {amount} GBP")
            return payment_response.__dict__
            
        except Exception as e:
            logger.error(f"❌ Failed to create mock payment request: {e}")
            raise PaymentError(f"Failed to create payment request: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get the status of a payment."""
        try:
            if not self.is_enabled():
                raise PaymentError("Payment system is not enabled")
            
            # Check if we have a stored response
            if payment_id in self.payment_responses:
                stored_response = self.payment_responses[payment_id]
                
                # Simulate status updates (randomly complete some payments)
                if stored_response.status == "pending" and datetime.now().hour % 2 == 0:
                    stored_response.status = "completed"
                    stored_response.updated_at = datetime.now()
                
                return stored_response.__dict__
            
            # If not found, return a mock response
            return {
                'payment_id': payment_id,
                'status': 'not_found',
                'amount': 0.0,
                'currency': 'GBP',
                'reference': payment_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get mock payment status: {e}")
            raise PaymentError(f"Failed to get payment status: {str(e)}")
    
    async def create_match_fee_payment(self, 
                                     player_id: str,
                                     amount: float,
                                     match_id: str,
                                     match_date: datetime,
                                     description: str = "") -> Dict[str, Any]:
        """Create a match fee payment request."""
        metadata = {
            'match_id': match_id,
            'match_date': match_date.isoformat(),
            'payment_category': 'match_fee'
        }
        
        return await self.create_payment_request(
            player_id=player_id,
            amount=amount,
            payment_type="match_fee",
            description=description or f"Match fee for {match_id}",
            due_date=match_date - timedelta(days=1),
            metadata=metadata
        )
    
    async def create_membership_fee_payment(self,
                                          player_id: str,
                                          amount: float,
                                          period: str,
                                          description: str = "") -> Dict[str, Any]:
        """Create a membership fee payment request."""
        metadata = {
            'period': period,
            'payment_category': 'membership_fee'
        }
        
        return await self.create_payment_request(
            player_id=player_id,
            amount=amount,
            payment_type="membership_fee",
            description=description or f"Membership fee for {period}",
            due_date=datetime.now() + timedelta(days=7),
            metadata=metadata
        )
    
    async def create_fine_payment(self,
                                player_id: str,
                                amount: float,
                                reason: str,
                                due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Create a fine payment request."""
        metadata = {
            'reason': reason,
            'payment_category': 'fine'
        }
        
        return await self.create_payment_request(
            player_id=player_id,
            amount=amount,
            payment_type="fine",
            description=f"Fine: {reason}",
            due_date=due_date or datetime.now() + timedelta(days=14),
            metadata=metadata
        )
    
    async def get_pending_payments(self, player_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pending payments for a player or team."""
        try:
            pending_payments = []
            
            for payment_id, response in self.payment_responses.items():
                if response.status in ["pending", "processing"]:
                    if player_id is None or self.payment_requests[payment_id].player_id == player_id:
                        pending_payments.append(response.__dict__)
            
            return pending_payments
            
        except Exception as e:
            logger.error(f"❌ Failed to get mock pending payments: {e}")
            return []
    
    async def get_payment_history(self, player_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get payment history for a player or team."""
        try:
            all_payments = [response.__dict__ for response in self.payment_responses.values()]
            
            # Filter by player if specified
            if player_id:
                all_payments = [
                    payment for payment in all_payments
                    if self.payment_requests.get(payment['reference'], {}).player_id == player_id
                ]
            
            # Sort by creation date (newest first)
            all_payments.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
            
            return all_payments[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to get mock payment history: {e}")
            return []
    
    def get_payment_stats(self) -> Dict[str, Any]:
        """Get payment statistics."""
        try:
            total_payments = len(self.payment_responses)
            completed_payments = len([p for p in self.payment_responses.values() if p.status == "completed"])
            pending_payments = len([p for p in self.payment_responses.values() if p.status in ["pending", "processing"]])
            failed_payments = len([p for p in self.payment_responses.values() if p.status == "failed"])
            
            total_amount = sum(p.amount for p in self.payment_responses.values() if p.status == "completed")
            
            return {
                'total_payments': total_payments,
                'completed_payments': completed_payments,
                'pending_payments': pending_payments,
                'failed_payments': failed_payments,
                'total_amount': total_amount,
                'success_rate': (completed_payments / total_payments * 100) if total_payments > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get mock payment stats: {e}")
            return {}
    
    def add_mock_payment(self, payment_id: str, status: str = "pending", amount: float = 10.0):
        """Add a mock payment for testing."""
        payment_response = MockPaymentResponse(
            payment_id=payment_id,
            status=status,
            amount=amount,
            currency="GBP",
            payment_url=f"https://mock-payment.example.com/pay/{payment_id}",
            reference=payment_id
        )
        
        self.payment_responses[payment_id] = payment_response
        logger.info(f"✅ Added mock payment: {payment_id} with status {status}")
    
    def clear_mock_data(self):
        """Clear all mock payment data."""
        self.payment_requests.clear()
        self.payment_responses.clear()
        logger.info("✅ Cleared all mock payment data") 