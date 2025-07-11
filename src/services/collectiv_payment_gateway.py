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

from services.interfaces.payment_gateway_interface import PaymentGatewayInterface

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


class MockCollectivPaymentGateway(PaymentGatewayInterface):
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
                "processor": "mock_collectiv",
                "card_last4": "1234" if payment_method == "card" else None
            },
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        self.transactions[transaction_id] = transaction
        
        # Update payment link
        link.status = PaymentLinkStatus.PAID
        link.paid_at = datetime.now()
        link.transaction_id = transaction_id
        
        logger.info(f"✅ Processed payment for link {link_id}: £{link.amount}")
        
        # Simulate webhook notification
        await self._simulate_webhook(link_id, transaction_id)
        
        return {
            "id": transaction_id,
            "payment_link_id": link_id,
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
            amount: Amount to refund (full amount if not specified)
            
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
                "refund_reason": "user_requested"
            },
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        self.transactions[refund_id] = refund_transaction
        
        # Update original transaction
        transaction.status = TransactionStatus.REFUNDED
        
        logger.info(f"✅ Refunded payment {transaction_id}: £{refund_amount}")
        
        return {
            "id": refund_id,
            "original_transaction_id": transaction_id,
            "amount": refund_amount,
            "currency": transaction.currency,
            "status": "refunded",
            "created_at": datetime.now().isoformat()
        }
    
    async def _simulate_webhook(self, link_id: str, transaction_id: str):
        """Simulate sending a webhook notification."""
        if not self.webhook_url:
            logger.info(f"Webhook URL not configured, skipping webhook for {link_id}")
            return
        
        webhook_data = {
            "event_type": "payment.completed",
            "data": {
                "payment_link_id": link_id,
                "transaction_id": transaction_id,
                "amount": self.payment_links[link_id].amount,
                "currency": self.payment_links[link_id].currency,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"📡 Simulated webhook sent for payment {link_id}")
        # In a real implementation, this would make an HTTP POST to the webhook URL
    
    def set_webhook_url(self, url: str):
        """Set the webhook URL for payment notifications."""
        self.webhook_url = url
        logger.info(f"Webhook URL set to: {url}")
    
    # Implement PaymentGatewayInterface methods for backward compatibility
    
    async def create_charge(self, amount: float, currency: str, source: str, 
                          description: Optional[str] = None) -> Dict[str, Any]:
        """Create a charge (simplified interface for backward compatibility)."""
        link_id = f"cl_{uuid.uuid4().hex[:16]}"
        reference = f"charge_{source}_{int(datetime.now().timestamp())}"
        
        link_data = await self.create_payment_link(
            amount=amount,
            currency=currency,
            description=description or "Payment",
            reference=reference
        )
        
        # Process the payment immediately
        transaction_data = await self.process_payment(link_id)
        
        return {
            "id": transaction_data["id"],
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "payment_link_id": link_id
        }
    
    async def create_refund(self, charge_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Create a refund (simplified interface for backward compatibility)."""
        return await self.refund_payment(charge_id, amount)
    
    async def get_payment_status(self, charge_id: str) -> str:
        """Get payment status (simplified interface for backward compatibility)."""
        if charge_id in self.transactions:
            return self.transactions[charge_id].status.value
        return "unknown"
    
    # Additional utility methods
    
    def get_payment_link(self, link_id: str) -> Optional[MockPaymentLink]:
        """Get a payment link by ID."""
        return self.payment_links.get(link_id)
    
    def get_transaction(self, transaction_id: str) -> Optional[MockTransaction]:
        """Get a transaction by ID."""
        return self.transactions.get(transaction_id)
    
    def list_payment_links(self, status: Optional[PaymentLinkStatus] = None) -> List[MockPaymentLink]:
        """List payment links, optionally filtered by status."""
        links = list(self.payment_links.values())
        if status:
            links = [link for link in links if link.status == status]
        return links
    
    def list_transactions(self, status: Optional[TransactionStatus] = None) -> List[MockTransaction]:
        """List transactions, optionally filtered by status."""
        transactions = list(self.transactions.values())
        if status:
            transactions = [tx for tx in transactions if tx.status == status]
        return transactions
    
    def clear_mock_data(self):
        """Clear all mock data (useful for testing)."""
        self.payment_links.clear()
        self.transactions.clear()
        logger.info("🧹 Cleared all mock payment data")
    
    def get_mock_statistics(self) -> Dict[str, Any]:
        """Get statistics about mock payment data."""
        total_links = len(self.payment_links)
        total_transactions = len(self.transactions)
        
        status_counts = {}
        for link in self.payment_links.values():
            status_counts[link.status.value] = status_counts.get(link.status.value, 0) + 1
        
        transaction_status_counts = {}
        for tx in self.transactions.values():
            transaction_status_counts[tx.status.value] = transaction_status_counts.get(tx.status.value, 0) + 1
        
        total_amount = sum(link.amount for link in self.payment_links.values() if link.status == PaymentLinkStatus.PAID)
        
        return {
            "total_payment_links": total_links,
            "total_transactions": total_transactions,
            "payment_link_status_counts": status_counts,
            "transaction_status_counts": transaction_status_counts,
            "total_amount_paid": total_amount
        } 