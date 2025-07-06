#!/usr/bin/env python3
"""
Payment Tools for KICKAI Agents

This module provides tools for agents to interact with the payment system.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from src.core.config import get_config
from src.services.payment_service import PaymentService, PaymentType
from src.services.mocks.mock_payment_service import MockPaymentService

logger = logging.getLogger(__name__)


class PaymentTools:
    """Tools for payment operations."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.config = get_config()
        
        # Initialize payment service based on environment
        if self.config.is_testing() or not self.config.payment.collectiv_api_key:
            self.payment_service = MockPaymentService(team_id)
        else:
            self.payment_service = PaymentService(team_id)
        
        logger.info(f"✅ Payment Tools initialized for team {team_id}")
    
    def is_payment_enabled(self) -> bool:
        """Check if payment system is enabled."""
        return self.payment_service.is_enabled()
    
    async def create_match_fee_payment(self, 
                                     player_id: str,
                                     amount: float,
                                     match_id: str,
                                     match_date: datetime,
                                     description: str = "") -> Dict[str, Any]:
        """Create a match fee payment request."""
        try:
            if not self.is_payment_enabled():
                return {
                    "success": False,
                    "error": "Payment system is not enabled",
                    "payment_id": None,
                    "payment_url": None
                }
            
            payment_response = await self.payment_service.create_match_fee_payment(
                player_id=player_id,
                amount=amount,
                match_id=match_id,
                match_date=match_date,
                description=description
            )
            
            return {
                "success": True,
                "payment_id": payment_response.payment_id,
                "payment_url": payment_response.payment_url,
                "amount": payment_response.amount,
                "currency": payment_response.currency,
                "status": payment_response.status.value,
                "reference": payment_response.reference
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create match fee payment: {e}")
            return {
                "success": False,
                "error": str(e),
                "payment_id": None,
                "payment_url": None
            }
    
    async def create_membership_fee_payment(self,
                                          player_id: str,
                                          amount: float,
                                          period: str,
                                          description: str = "") -> Dict[str, Any]:
        """Create a membership fee payment request."""
        try:
            if not self.is_payment_enabled():
                return {
                    "success": False,
                    "error": "Payment system is not enabled",
                    "payment_id": None,
                    "payment_url": None
                }
            
            payment_response = await self.payment_service.create_membership_fee_payment(
                player_id=player_id,
                amount=amount,
                period=period,
                description=description
            )
            
            return {
                "success": True,
                "payment_id": payment_response.payment_id,
                "payment_url": payment_response.payment_url,
                "amount": payment_response.amount,
                "currency": payment_response.currency,
                "status": payment_response.status.value,
                "reference": payment_response.reference
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create membership fee payment: {e}")
            return {
                "success": False,
                "error": str(e),
                "payment_id": None,
                "payment_url": None
            }
    
    async def create_fine_payment(self,
                                player_id: str,
                                amount: float,
                                reason: str,
                                due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Create a fine payment request."""
        try:
            if not self.is_payment_enabled():
                return {
                    "success": False,
                    "error": "Payment system is not enabled",
                    "payment_id": None,
                    "payment_url": None
                }
            
            payment_response = await self.payment_service.create_fine_payment(
                player_id=player_id,
                amount=amount,
                reason=reason,
                due_date=due_date
            )
            
            return {
                "success": True,
                "payment_id": payment_response.payment_id,
                "payment_url": payment_response.payment_url,
                "amount": payment_response.amount,
                "currency": payment_response.currency,
                "status": payment_response.status.value,
                "reference": payment_response.reference
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create fine payment: {e}")
            return {
                "success": False,
                "error": str(e),
                "payment_id": None,
                "payment_url": None
            }
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get the status of a payment."""
        try:
            if not self.is_payment_enabled():
                return {
                    "success": False,
                    "error": "Payment system is not enabled",
                    "status": None
                }
            
            payment_response = await self.payment_service.get_payment_status(payment_id)
            
            return {
                "success": True,
                "payment_id": payment_response.payment_id,
                "status": payment_response.status.value,
                "amount": payment_response.amount,
                "currency": payment_response.currency,
                "created_at": payment_response.created_at.isoformat() if payment_response.created_at else None,
                "updated_at": payment_response.updated_at.isoformat() if payment_response.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment status: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": None
            }
    
    async def get_pending_payments(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """Get all pending payments for a player or team."""
        try:
            if not self.is_payment_enabled():
                return {
                    "success": False,
                    "error": "Payment system is not enabled",
                    "payments": []
                }
            
            pending_payments = await self.payment_service.get_pending_payments(player_id)
            
            payments_data = []
            for payment in pending_payments:
                payments_data.append({
                    "payment_id": payment.payment_id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status.value,
                    "payment_url": payment.payment_url,
                    "reference": payment.reference,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None
                })
            
            return {
                "success": True,
                "payments": payments_data,
                "count": len(payments_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get pending payments: {e}")
            return {
                "success": False,
                "error": str(e),
                "payments": []
            }
    
    async def get_payment_history(self, player_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get payment history for a player or team."""
        try:
            if not self.is_payment_enabled():
                return {
                    "success": False,
                    "error": "Payment system is not enabled",
                    "payments": []
                }
            
            payment_history = await self.payment_service.get_payment_history(player_id, limit)
            
            payments_data = []
            for payment in payment_history:
                payments_data.append({
                    "payment_id": payment.payment_id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status.value,
                    "reference": payment.reference,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None,
                    "updated_at": payment.updated_at.isoformat() if payment.updated_at else None
                })
            
            return {
                "success": True,
                "payments": payments_data,
                "count": len(payments_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment history: {e}")
            return {
                "success": False,
                "error": str(e),
                "payments": []
            }
    
    def get_payment_stats(self) -> Dict[str, Any]:
        """Get payment statistics."""
        try:
            if not self.is_payment_enabled():
                return {
                    "success": False,
                    "error": "Payment system is not enabled",
                    "stats": {}
                }
            
            stats = self.payment_service.get_payment_stats()
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "stats": {}
            }
    
    def format_payment_message(self, payment_data: Dict[str, Any]) -> str:
        """Format payment data into a user-friendly message."""
        if not payment_data.get("success"):
            return f"❌ Payment Error: {payment_data.get('error', 'Unknown error')}"
        
        payment_id = payment_data.get("payment_id", "Unknown")
        amount = payment_data.get("amount", 0)
        currency = payment_data.get("currency", "GBP")
        status = payment_data.get("status", "unknown")
        payment_url = payment_data.get("payment_url")
        
        message = f"💳 Payment Created\n\n"
        message += f"**Payment ID:** `{payment_id}`\n"
        message += f"**Amount:** £{amount:.2f}\n"
        message += f"**Status:** {status.title()}\n"
        
        if payment_url:
            message += f"\n🔗 **Payment Link:** {payment_url}\n"
        
        if status == "pending":
            message += "\n⏰ Please complete the payment using the link above."
        elif status == "completed":
            message += "\n✅ Payment completed successfully!"
        elif status == "failed":
            message += "\n❌ Payment failed. Please try again."
        
        return message
    
    def format_payment_list(self, payments_data: Dict[str, Any]) -> str:
        """Format payment list into a user-friendly message."""
        if not payments_data.get("success"):
            return f"❌ Error: {payments_data.get('error', 'Unknown error')}"
        
        payments = payments_data.get("payments", [])
        count = payments_data.get("count", 0)
        
        if count == 0:
            return "📋 No payments found."
        
        message = f"📋 Payment List ({count} payments)\n\n"
        
        for i, payment in enumerate(payments, 1):
            payment_id = payment.get("payment_id", "Unknown")
            amount = payment.get("amount", 0)
            currency = payment.get("currency", "GBP")
            status = payment.get("status", "unknown")
            created_at = payment.get("created_at")
            
            message += f"{i}. **{payment_id}**\n"
            message += f"   💰 £{amount:.2f} | 📊 {status.title()}\n"
            
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    message += f"   📅 {created_date.strftime('%Y-%m-%d %H:%M')}\n"
                except:
                    pass
            
            message += "\n"
        
        return message 