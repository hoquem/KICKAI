"""
Mock Collectiv Payment Gateway

This module provides a mock implementation of the Collectiv payment system
for development and testing purposes. It simulates all the key functionality
of the Collectiv API without requiring actual API credentials.
"""

import logging
import asyncio
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from features.payment_management.domain.interfaces.payment_gateway_interface import IPaymentGateway

logger = logging.getLogger(__name__)


class PaymentLinkStatus(Enum):
    """Status of payment links."""
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TransactionStatus(Enum):
    """Status of payment transactions."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class MockPaymentLink:
    """Mock payment link data structure."""
    id: str
    amount: float
    currency: str
    description: str
    reference: str
    status: PaymentLinkStatus
    payment_url: str
    expires_at: datetime
    created_at: datetime
    paid_at: Optional[datetime] = None
    transaction_id: Optional[str] = None


@dataclass
class MockTransaction:
    """Mock transaction data structure."""
    id: str
    payment_link_id: str
    amount: float
    currency: str
    payment_method: str
    status: TransactionStatus
    transaction_data: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None


class MockCollectivPaymentGateway(IPaymentGateway):
    """
    Mock Collectiv payment gateway for development and testing.
    
    This class simulates the Collectiv API functionality including:
    - Payment link creation
    - Payment processing
    - Transaction management
    - Webhook simulation
    """
    
    def __init__(self, api_key: str = "mock_collectiv_key", base_url: str = "https://api.collectiv.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.payment_links: Dict[str, MockPaymentLink] = {}
        self.transactions: Dict[str, MockTransaction] = {}
        self.webhook_url: Optional[str] = None
        self.webhook_secret: str = "mock_webhook_secret"
        
        logger.info("✅ MockCollectivPaymentGateway initialized")
    
    async def create_payment_link(self, amount: float, currency: str, 
                                description: str, reference: str,
                                expires_in_days: int = 7) -> Dict[str, Any]:
        """
        Create a mock payment link.
        
        Args:
            amount: Payment amount
            currency: Currency code (e.g., 'GBP')
            description: Payment description
            reference: Reference ID for tracking
            expires_in_days: Days until link expires
            
        Returns:
            Dict containing payment link details
        """
        link_id = f"cl_{uuid.uuid4().hex[:16]}"
        payment_url = f"https://pay.collectiv.com/mock/{link_id}"
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        payment_link = MockPaymentLink(
            id=link_id,
            amount=amount,
            currency=currency,
            description=description,
            reference=reference,
            status=PaymentLinkStatus.PENDING,
            payment_url=payment_url,
            expires_at=expires_at,
            created_at=datetime.now()
        )
        
        self.payment_links[link_id] = payment_link
        
        logger.info(f"✅ Created mock payment link: {link_id} for £{amount}")
        
        return {
            "id": link_id,
            "url": payment_url,
            "amount": amount,
            "currency": currency,
            "description": description,
            "reference": reference,
            "expires_at": expires_at.isoformat(),
            "status": "pending"
        }
    
    async def get_payment_link_status(self, link_id: str) -> Dict[str, Any]:
        """
        Get the status of a payment link.
        
        Args:
            link_id: Payment link ID
            
        Returns:
            Dict containing payment link status
        """
        if link_id not in self.payment_links:
            raise ValueError(f"Payment link {link_id} not found")
        
        link = self.payment_links[link_id]
        
        # Check if link has expired
        if link.status == PaymentLinkStatus.PENDING and datetime.now() > link.expires_at:
            link.status = PaymentLinkStatus.EXPIRED
            logger.info(f"Payment link {link_id} has expired")
        
        return {
            "id": link.id,
            "amount": link.amount,
            "currency": link.currency,
            "status": link.status.value,
            "paid_at": link.paid_at.isoformat() if link.paid_at else None,
            "transaction_id": link.transaction_id,
            "expires_at": link.expires_at.isoformat()
        }
    
    async def process_payment(self, link_id: str, payment_method: str = "card") -> Dict[str, Any]:
        """
        Simulate processing a payment for a payment link.
        
        Args:
            link_id: Payment link ID
            payment_method: Payment method used
            
        Returns:
            Dict containing transaction details
        """
        if link_id not in self.payment_links:
            raise ValueError(f"Payment link {link_id} not found")
        
        link = self.payment_links[link_id]
        
        if link.status != PaymentLinkStatus.PENDING:
            raise ValueError(f"Payment link {link_id} is not in pending status")
        
        if datetime.now() > link.expires_at:
            link.status = PaymentLinkStatus.EXPIRED
            raise ValueError(f"Payment link {link_id} has expired")
        
        # Simulate payment processing delay
        await asyncio.sleep(1)
        
        # Create transaction
        transaction_id = f"tx_{uuid.uuid4().hex[:16]}"
        transaction = MockTransaction(
            id=transaction_id,
            payment_link_id=link_id,
            amount=link.amount,
            currency=link.currency,
            payment_method=payment_method,
            status=TransactionStatus.COMPLETED,
            transaction_data={
                "payment_method": payment_method,
                "card_last4": "1234",
                "card_brand": "visa"
            },
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        self.transactions[transaction_id] = transaction
        
        # Update payment link
        link.status = PaymentLinkStatus.PAID
        link.paid_at = datetime.now()
        link.transaction_id = transaction_id
        
        # Simulate webhook notification
        await self._simulate_webhook(link_id, transaction_id)
        
        logger.info(f"✅ Processed payment for link {link_id}: £{link.amount}")
        
        return {
            "id": transaction_id,
            "amount": link.amount,
            "currency": link.currency,
            "status": "completed",
            "payment_method": payment_method,
            "completed_at": datetime.now().isoformat()
        }
    
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Simulate refunding a payment.
        
        Args:
            transaction_id: Transaction ID to refund
            amount: Amount to refund (if None, refunds full amount)
            
        Returns:
            Dict containing refund details
        """
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        transaction = self.transactions[transaction_id]
        
        if transaction.status != TransactionStatus.COMPLETED:
            raise ValueError(f"Transaction {transaction_id} is not completed")
        
        refund_amount = amount or transaction.amount
        refund_id = f"rf_{uuid.uuid4().hex[:16]}"
        
        # Create refund transaction
        refund_transaction = MockTransaction(
            id=refund_id,
            payment_link_id=transaction.payment_link_id,
            amount=refund_amount,
            currency=transaction.currency,
            payment_method="refund",
            status=TransactionStatus.REFUNDED,
            transaction_data={
                "original_transaction_id": transaction_id,
                "refund_reason": "customer_request"
            },
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        self.transactions[refund_id] = refund_transaction
        
        # Update original transaction
        transaction.status = TransactionStatus.REFUNDED
        
        logger.info(f"✅ Processed refund for transaction {transaction_id}: £{refund_amount}")
        
        return {
            "id": refund_id,
            "amount": refund_amount,
            "currency": transaction.currency,
            "status": "refunded",
            "original_transaction_id": transaction_id,
            "completed_at": datetime.now().isoformat()
        }
    
    async def _simulate_webhook(self, link_id: str, transaction_id: str):
        """Simulate sending a webhook notification."""
        if not self.webhook_url:
            return
        
        webhook_data = {
            "event": "payment.completed",
            "data": {
                "payment_link_id": link_id,
                "transaction_id": transaction_id,
                "amount": self.payment_links[link_id].amount,
                "currency": self.payment_links[link_id].currency,
                "completed_at": datetime.now().isoformat()
            }
        }
        
        # In a real implementation, this would send an HTTP POST to the webhook URL
        logger.info(f"📡 Simulated webhook notification: {json.dumps(webhook_data, indent=2)}")
    
    def set_webhook_url(self, url: str):
        """Set the webhook URL for notifications."""
        self.webhook_url = url
        logger.info(f"✅ Webhook URL set to: {url}")
    
    async def create_charge(self, amount: float, currency: str, source: str, 
                          description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a direct charge (not using payment links).
        
        Args:
            amount: Charge amount
            currency: Currency code
            source: Payment source (e.g., card token)
            description: Charge description
            
        Returns:
            Dict containing charge details
        """
        charge_id = f"ch_{uuid.uuid4().hex[:16]}"
        
        # Simulate processing delay
        await asyncio.sleep(1)
        
        logger.info(f"✅ Created charge: {charge_id} for £{amount}")
        
        return {
            "id": charge_id,
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "description": description,
            "created_at": datetime.now().isoformat()
        }
    
    async def create_refund(self, charge_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Create a refund for a charge."""
        refund_id = f"rf_{uuid.uuid4().hex[:16]}"
        logger.info(f"✅ Created refund: {refund_id} for charge {charge_id}")
        return {"id": refund_id, "status": "succeeded"}
    
    async def get_payment_status(self, charge_id: str) -> str:
        """Get the status of a payment."""
        # Mock implementation - always returns succeeded
        return "succeeded"
    
    def get_payment_link(self, link_id: str) -> Optional[MockPaymentLink]:
        """Get a payment link by ID."""
        return self.payment_links.get(link_id)
    
    def get_transaction(self, transaction_id: str) -> Optional[MockTransaction]:
        """Get a transaction by ID."""
        return self.transactions.get(transaction_id)
    
    def list_payment_links(self, status: Optional[PaymentLinkStatus] = None) -> List[MockPaymentLink]:
        """List payment links with optional status filter."""
        links = list(self.payment_links.values())
        if status:
            links = [link for link in links if link.status == status]
        return links
    
    def list_transactions(self, status: Optional[TransactionStatus] = None) -> List[MockTransaction]:
        """List transactions with optional status filter."""
        transactions = list(self.transactions.values())
        if status:
            transactions = [tx for tx in transactions if tx.status == status]
        return transactions
    
    def clear_mock_data(self):
        """Clear all mock data for testing."""
        self.payment_links.clear()
        self.transactions.clear()
        logger.info("✅ Cleared all mock payment data")
    
    def get_mock_statistics(self) -> Dict[str, Any]:
        """Get statistics about mock data."""
        return {
            "payment_links_count": len(self.payment_links),
            "transactions_count": len(self.transactions),
            "pending_links": len([link for link in self.payment_links.values() if link.status == PaymentLinkStatus.PENDING]),
            "paid_links": len([link for link in self.payment_links.values() if link.status == PaymentLinkStatus.PAID]),
            "completed_transactions": len([tx for tx in self.transactions.values() if tx.status == TransactionStatus.COMPLETED]),
            "refunded_transactions": len([tx for tx in self.transactions.values() if tx.status == TransactionStatus.REFUNDED])
        } 