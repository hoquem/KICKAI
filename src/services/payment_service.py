#!/usr/bin/env python3
"""
Payment Service for KICKAI

This service handles all payment operations using Collectiv integration.
Designed to be flexible and extensible for future UX improvements.
"""

import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

from src.core.config import get_config
from src.core.exceptions import PaymentError, ValidationError
from .interfaces.payment_service_interface import IPaymentService

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentType(Enum):
    """Payment type enumeration."""
    MATCH_FEE = "match_fee"
    MEMBERSHIP_FEE = "membership_fee"
    FINE = "fine"
    MISC = "miscellaneous"

@dataclass
class PaymentRequest:
    """Payment request data model."""
    id: str
    team_id: str
    player_id: str
    amount: float
    currency: str = "GBP"
    payment_type: PaymentType = PaymentType.MATCH_FEE
    description: str = ""
    due_date: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        data = asdict(self)
        data['payment_type'] = self.payment_type.value
        if self.due_date:
            data['due_date'] = self.due_date.isoformat()
        return data

@dataclass
class PaymentResponse:
    """Payment response data model."""
    payment_id: str
    status: PaymentStatus
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

class CollectivPaymentProvider:
    """Collectiv payment provider implementation."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.collectiv.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def create_payment_link(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """Create a payment link using Collectiv API."""
        try:
            url = f"{self.base_url}/v1/payment-links"
            
            payload = {
                'amount': int(payment_request.amount * 100),  # Convert to pence
                'currency': payment_request.currency,
                'reference': payment_request.id,
                'description': payment_request.description or f"{payment_request.payment_type.value.title()} - {payment_request.team_id}",
                'metadata': {
                    'team_id': payment_request.team_id,
                    'player_id': payment_request.player_id,
                    'payment_type': payment_request.payment_type.value,
                    **payment_request.metadata
                }
            }
            
            if payment_request.due_date:
                payload['expires_at'] = payment_request.due_date.isoformat()
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return {
                'payment_id': data.get('id'),
                'payment_url': data.get('url'),
                'reference': data.get('reference'),
                'status': PaymentStatus.PENDING
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Collectiv API error: {e}")
            raise PaymentError(f"Failed to create payment link: {str(e)}")
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status from Collectiv API."""
        try:
            url = f"{self.base_url}/v1/payments/{payment_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return {
                'payment_id': data.get('id'),
                'status': PaymentStatus(data.get('status', 'pending')),
                'amount': data.get('amount', 0) / 100,  # Convert from pence
                'currency': data.get('currency', 'GBP'),
                'reference': data.get('reference'),
                'created_at': datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
                'updated_at': datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Collectiv API error: {e}")
            raise PaymentError(f"Failed to get payment status: {str(e)}")

class PaymentService(IPaymentService):
    """Main payment service implementation."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.config = get_config()
        
        # Initialize Collectiv provider
        collectiv_api_key = self.config.payment.collectiv_api_key
        collectiv_base_url = self.config.payment.collectiv_base_url
        
        if not collectiv_api_key:
            logger.warning("Collectiv API key not configured - payment features will be disabled")
            self.provider = None
        else:
            self.provider = CollectivPaymentProvider(collectiv_api_key, collectiv_base_url)
        
        # Payment tracking
        self.payment_requests: Dict[str, PaymentRequest] = {}
        self.payment_responses: Dict[str, PaymentResponse] = {}
        
        logger.info(f"✅ Payment Service initialized for team {team_id}")
    
    def is_enabled(self) -> bool:
        """Check if payment system is enabled."""
        return self.provider is not None
    
    async def create_payment_request(self, 
                                   player_id: str,
                                   amount: float,
                                   payment_type: PaymentType,
                                   description: str = "",
                                   due_date: Optional[datetime] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> PaymentResponse:
        """Create a new payment request."""
        try:
            if not self.is_enabled():
                raise PaymentError("Payment system is not enabled")
            
            # Validate inputs
            if amount <= 0:
                raise ValidationError("Payment amount must be greater than 0")
            
            if not player_id:
                raise ValidationError("Player ID is required")
            
            # Generate payment request ID
            payment_id = f"pay_{self.team_id}_{player_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create payment request
            payment_request = PaymentRequest(
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
            
            # Create payment link via Collectiv
            payment_data = self.provider.create_payment_link(payment_request)
            
            # Create payment response
            payment_response = PaymentResponse(
                payment_id=payment_data['payment_id'],
                status=payment_data['status'],
                amount=amount,
                currency=payment_request.currency,
                payment_url=payment_data['payment_url'],
                reference=payment_data['reference'],
                metadata=payment_request.metadata
            )
            
            # Store payment response
            self.payment_responses[payment_id] = payment_response
            
            logger.info(f"✅ Created payment request: {payment_id} for {amount} {payment_request.currency}")
            return payment_response
            
        except Exception as e:
            logger.error(f"❌ Failed to create payment request: {e}")
            raise PaymentError(f"Failed to create payment request: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentResponse:
        """Get the status of a payment."""
        try:
            if not self.is_enabled():
                raise PaymentError("Payment system is not enabled")
            
            # Check if we have a stored response
            if payment_id in self.payment_responses:
                stored_response = self.payment_responses[payment_id]
                
                # Update status from Collectiv if needed
                if stored_response.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
                    try:
                        updated_data = self.provider.get_payment_status(stored_response.payment_id)
                        stored_response.status = updated_data['status']
                        stored_response.updated_at = datetime.now()
                    except Exception as e:
                        logger.warning(f"Failed to update payment status: {e}")
                
                return stored_response
            
            # If not found locally, try to get from Collectiv
            payment_data = self.provider.get_payment_status(payment_id)
            
            payment_response = PaymentResponse(
                payment_id=payment_data['payment_id'],
                status=payment_data['status'],
                amount=payment_data['amount'],
                currency=payment_data['currency'],
                reference=payment_data['reference'],
                created_at=payment_data['created_at'],
                updated_at=payment_data['updated_at']
            )
            
            return payment_response
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment status: {e}")
            raise PaymentError(f"Failed to get payment status: {str(e)}")
    
    async def create_match_fee_payment(self, 
                                     player_id: str,
                                     amount: float,
                                     match_id: str,
                                     match_date: datetime,
                                     description: str = "") -> PaymentResponse:
        """Create a match fee payment request."""
        metadata = {
            'match_id': match_id,
            'match_date': match_date.isoformat(),
            'payment_category': 'match_fee'
        }
        
        return await self.create_payment_request(
            player_id=player_id,
            amount=amount,
            payment_type=PaymentType.MATCH_FEE,
            description=description or f"Match fee for {match_id}",
            due_date=match_date - timedelta(days=1),  # Due 1 day before match
            metadata=metadata
        )
    
    async def create_membership_fee_payment(self,
                                          player_id: str,
                                          amount: float,
                                          period: str,
                                          description: str = "") -> PaymentResponse:
        """Create a membership fee payment request."""
        metadata = {
            'period': period,
            'payment_category': 'membership_fee'
        }
        
        return await self.create_payment_request(
            player_id=player_id,
            amount=amount,
            payment_type=PaymentType.MEMBERSHIP_FEE,
            description=description or f"Membership fee for {period}",
            due_date=datetime.now() + timedelta(days=7),  # Due in 7 days
            metadata=metadata
        )
    
    async def create_fine_payment(self,
                                player_id: str,
                                amount: float,
                                reason: str,
                                due_date: Optional[datetime] = None) -> PaymentResponse:
        """Create a fine payment request."""
        metadata = {
            'reason': reason,
            'payment_category': 'fine'
        }
        
        return await self.create_payment_request(
            player_id=player_id,
            amount=amount,
            payment_type=PaymentType.FINE,
            description=f"Fine: {reason}",
            due_date=due_date or datetime.now() + timedelta(days=14),  # Due in 14 days
            metadata=metadata
        )
    
    async def get_pending_payments(self, player_id: Optional[str] = None) -> List[PaymentResponse]:
        """Get all pending payments for a player or team."""
        try:
            pending_payments = []
            
            for payment_id, response in self.payment_responses.items():
                if response.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
                    if player_id is None or self.payment_requests[payment_id].player_id == player_id:
                        pending_payments.append(response)
            
            return pending_payments
            
        except Exception as e:
            logger.error(f"❌ Failed to get pending payments: {e}")
            return []
    
    async def get_payment_history(self, player_id: Optional[str] = None, limit: int = 50) -> List[PaymentResponse]:
        """Get payment history for a player or team."""
        try:
            all_payments = list(self.payment_responses.values())
            
            # Filter by player if specified
            if player_id:
                all_payments = [
                    payment for payment in all_payments
                    if self.payment_requests.get(payment.payment_id, {}).get('player_id') == player_id
                ]
            
            # Sort by creation date (newest first)
            all_payments.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
            
            return all_payments[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment history: {e}")
            return []
    
    def get_payment_stats(self) -> Dict[str, Any]:
        """Get payment statistics."""
        try:
            total_payments = len(self.payment_responses)
            completed_payments = len([p for p in self.payment_responses.values() if p.status == PaymentStatus.COMPLETED])
            pending_payments = len([p for p in self.payment_responses.values() if p.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]])
            failed_payments = len([p for p in self.payment_responses.values() if p.status == PaymentStatus.FAILED])
            
            total_amount = sum(p.amount for p in self.payment_responses.values() if p.status == PaymentStatus.COMPLETED)
            
            return {
                'total_payments': total_payments,
                'completed_payments': completed_payments,
                'pending_payments': pending_payments,
                'failed_payments': failed_payments,
                'total_amount': total_amount,
                'success_rate': (completed_payments / total_payments * 100) if total_payments > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment stats: {e}")
            return {} 