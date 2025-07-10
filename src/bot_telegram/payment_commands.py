"""
Payment Commands for KICKAI Telegram Bot

This module provides payment-related commands for the Telegram bot,
integrating with the mock Collectiv payment system.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from services.payment_service import get_payment_service
from services.player_service import get_player_service
from database.models_improved import PaymentType, PaymentStatus
from core.exceptions import PaymentError, PlayerNotFoundError
from core.improved_config_system import get_improved_config

logger = logging.getLogger(__name__)


class PaymentCommands:
    """Payment commands for the Telegram bot."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.payment_service = get_payment_service(team_id=team_id)
        self.player_service = get_player_service(team_id=team_id)
        self.config = get_improved_config()

    async def create_match_fee_payment(self, chat_id: str, match_id: str, amount: float, 
                                     player_ids: list[str], description: str) -> str:
        """
        Create match fee payments for multiple players.
        
        Args:
            chat_id: Telegram chat ID
            match_id: Match ID
            amount: Payment amount per player
            player_ids: List of player IDs
            description: Payment description
            
        Returns:
            Status message
        """
        try:
            created_links = []
            failed_players = []
            
            for player_id in player_ids:
                try:
                    # Verify player exists
                    player = await self.player_service.get_player(player_id)
                    if not player:
                        failed_players.append(f"{player_id} (not found)")
                        continue
                    
                    # Create payment link
                    payment_data = await self.payment_service.create_payment_link(
                        player_id=player_id,
                        amount=amount,
                        payment_type=PaymentType.MATCH_FEE,
                        description=description,
                        due_date=datetime.now() + timedelta(days=7),
                        related_entity_id=match_id
                    )
                    
                    created_links.append({
                        "player_id": player_id,
                        "player_name": player.name,
                        "payment_url": payment_data["payment_url"],
                        "link_id": payment_data["link_id"]
                    })
                    
                    # Send private payment link to player (in a real system)
                    logger.info(f"Created payment link for {player.name}: {payment_data['payment_url']}")
                    
                except Exception as e:
                    logger.error(f"Failed to create payment for player {player_id}: {e}")
                    failed_players.append(f"{player_id} (error: {str(e)})")
            
            # Build response message
            message = f"💰 **Match Fee Payments Created**\n\n"
            message += f"**Match**: {description}\n"
            message += f"**Amount**: £{amount:.2f} per player\n"
            message += f"**Due Date**: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}\n\n"
            
            if created_links:
                message += f"✅ **Successfully created {len(created_links)} payment links:**\n"
                for link in created_links:
                    message += f"• {link['player_name']} ({link['player_id']})\n"
                    message += f"  Payment URL: {link['payment_url']}\n\n"
            
            if failed_players:
                message += f"❌ **Failed to create payments for {len(failed_players)} players:**\n"
                for failed in failed_players:
                    message += f"• {failed}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create match fee payments: {e}")
            return f"❌ Error creating match fee payments: {str(e)}"

    async def create_membership_fee_payment(self, chat_id: str, player_id: str, amount: float, 
                                          description: str) -> str:
        """
        Create a membership fee payment for a player.
        
        Args:
            chat_id: Telegram chat ID
            player_id: Player ID
            amount: Payment amount
            description: Payment description
            
        Returns:
            Status message
        """
        try:
            # Verify player exists
            player = await self.player_service.get_player(player_id)
            if not player:
                return f"❌ Player {player_id} not found"
            
            # Create payment link
            payment_data = await self.payment_service.create_payment_link(
                player_id=player_id,
                amount=amount,
                payment_type=PaymentType.MEMBERSHIP,
                description=description,
                due_date=datetime.now() + timedelta(days=30)
            )
            
            message = f"💰 **Membership Fee Payment Created**\n\n"
            message += f"**Player**: {player.name} ({player_id})\n"
            message += f"**Amount**: £{amount:.2f}\n"
            message += f"**Description**: {description}\n"
            message += f"**Due Date**: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}\n\n"
            message += f"**Payment URL**: {payment_data['payment_url']}\n\n"
            message += f"Payment Link ID: `{payment_data['link_id']}`"
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create membership fee payment: {e}")
            return f"❌ Error creating membership fee payment: {str(e)}"

    async def create_fine_payment(self, chat_id: str, player_id: str, amount: float, 
                                description: str) -> str:
        """
        Create a fine payment for a player.
        
        Args:
            chat_id: Telegram chat ID
            player_id: Player ID
            amount: Fine amount
            description: Fine description
            
        Returns:
            Status message
        """
        try:
            # Verify player exists
            player = await self.player_service.get_player(player_id)
            if not player:
                return f"❌ Player {player_id} not found"
            
            # Create payment link
            payment_data = await self.payment_service.create_payment_link(
                player_id=player_id,
                amount=amount,
                payment_type=PaymentType.FINE,
                description=description,
                due_date=datetime.now() + timedelta(days=14)
            )
            
            message = f"⚠️ **Fine Payment Created**\n\n"
            message += f"**Player**: {player.name} ({player_id})\n"
            message += f"**Amount**: £{amount:.2f}\n"
            message += f"**Reason**: {description}\n"
            message += f"**Due Date**: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}\n\n"
            message += f"**Payment URL**: {payment_data['payment_url']}\n\n"
            message += f"Payment Link ID: `{payment_data['link_id']}`"
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create fine payment: {e}")
            return f"❌ Error creating fine payment: {str(e)}"

    async def process_payment(self, link_id: str, payment_method: str = "card") -> str:
        """
        Process a payment using a payment link.
        
        Args:
            link_id: Payment link ID
            payment_method: Payment method used
            
        Returns:
            Status message
        """
        try:
            # Process the payment
            transaction_data = await self.payment_service.process_payment(link_id, payment_method)
            
            message = f"✅ **Payment Processed Successfully**\n\n"
            message += f"**Transaction ID**: {transaction_data['id']}\n"
            message += f"**Amount**: £{transaction_data['amount']:.2f}\n"
            message += f"**Payment Method**: {payment_method.title()}\n"
            message += f"**Status**: {transaction_data['status']}\n"
            message += f"**Completed**: {transaction_data['completed_at']}\n\n"
            message += "Payment has been recorded and player is confirmed for any related matches."
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            return f"❌ Error processing payment: {str(e)}"

    async def get_payment_status(self, link_id: str) -> str:
        """
        Get the status of a payment link.
        
        Args:
            link_id: Payment link ID
            
        Returns:
            Status message
        """
        try:
            status_data = await self.payment_service.get_payment_link_status(link_id)
            
            message = f"💰 **Payment Status**\n\n"
            message += f"**Link ID**: {link_id}\n"
            message += f"**Amount**: £{status_data['amount']:.2f}\n"
            message += f"**Status**: {status_data['status'].title()}\n"
            message += f"**Currency**: {status_data['currency']}\n"
            
            if status_data.get('paid_at'):
                message += f"**Paid At**: {status_data['paid_at']}\n"
            
            if status_data.get('transaction_id'):
                message += f"**Transaction ID**: {status_data['transaction_id']}\n"
            
            message += f"**Expires At**: {status_data['expires_at']}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to get payment status: {e}")
            return f"❌ Error getting payment status: {str(e)}"

    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> str:
        """
        Refund a payment.
        
        Args:
            transaction_id: Transaction ID to refund
            amount: Amount to refund (full amount if not specified)
            
        Returns:
            Status message
        """
        try:
            refund_data = await self.payment_service.refund_payment(transaction_id, amount)
            
            message = f"🔄 **Payment Refunded**\n\n"
            message += f"**Refund ID**: {refund_data['id']}\n"
            message += f"**Original Transaction**: {transaction_id}\n"
            message += f"**Refund Amount**: £{refund_data['amount']:.2f}\n"
            message += f"**Status**: {refund_data['status']}\n"
            message += f"**Created**: {refund_data['created_at']}\n\n"
            message += "Refund has been processed and recorded."
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to refund payment: {e}")
            return f"❌ Error refunding payment: {str(e)}"

    async def get_payment_analytics(self, team_id: str, days: int = 30) -> str:
        """
        Get payment analytics for a team.
        
        Args:
            team_id: Team ID
            days: Number of days to analyze
            
        Returns:
            Analytics message
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            analytics = await self.payment_service.get_payment_analytics(
                team_id=team_id,
                start_date=start_date,
                end_date=end_date
            )
            
            message = f"📊 **Payment Analytics**\n\n"
            message += f"**Period**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n"
            message += f"**Total Payments**: {analytics['total_payments']}\n"
            message += f"**Total Amount**: £{analytics['total_amount']:.2f}\n"
            message += f"**Pending Amount**: £{analytics['pending_amount']:.2f}\n"
            message += f"**Collection Rate**: {analytics['collection_rate']:.1f}%\n\n"
            
            if analytics['payment_types']:
                message += "**By Payment Type**:\n"
                for payment_type, data in analytics['payment_types'].items():
                    message += f"• {payment_type.title()}: {data['count']} payments, £{data['amount']:.2f}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to get payment analytics: {e}")
            return f"❌ Error getting payment analytics: {str(e)}"

    async def list_player_payments(self, player_id: str) -> str:
        """
        List all payments for a player.
        
        Args:
            player_id: Player ID
            
        Returns:
            Payment list message
        """
        try:
            # Verify player exists
            player = await self.player_service.get_player(player_id)
            if not player:
                return f"❌ Player {player_id} not found"
            
            payments = await self.payment_service.get_player_payments(player_id)
            
            if not payments:
                return f"📋 No payments found for {player.name} ({player_id})"
            
            message = f"📋 **Payment History for {player.name}**\n\n"
            
            for payment in payments:
                status_emoji = "✅" if payment.status == PaymentStatus.PAID else "⏳" if payment.status == PaymentStatus.PENDING else "❌"
                message += f"{status_emoji} **{payment.type.value.replace('_', ' ').title()}**\n"
                message += f"   Amount: £{payment.amount:.2f}\n"
                message += f"   Status: {payment.status.value.title()}\n"
                if payment.description:
                    message += f"   Description: {payment.description}\n"
                if payment.paid_date:
                    message += f"   Paid: {payment.paid_date.strftime('%Y-%m-%d')}\n"
                message += "\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to list player payments: {e}")
            return f"❌ Error listing player payments: {str(e)}"

    async def send_payment_reminder(self, chat_id: str, link_id: str) -> str:
        """
        Send a payment reminder for a pending payment.
        
        Args:
            chat_id: Telegram chat ID
            link_id: Payment link ID
            
        Returns:
            Reminder message
        """
        try:
            status_data = await self.payment_service.get_payment_link_status(link_id)
            
            if status_data['status'] != 'pending':
                return f"ℹ️ Payment {link_id} is not pending (status: {status_data['status']})"
            
            # Get player info from Firestore data
            firestore_data = status_data.get('firestore_data', {})
            player_id = firestore_data.get('player_id')
            
            if player_id:
                player = await self.player_service.get_player(player_id)
                player_name = player.name if player else player_id
            else:
                player_name = "Unknown Player"
            
            message = f"⏰ **Payment Reminder**\n\n"
            message += f"**Player**: {player_name}\n"
            message += f"**Amount**: £{status_data['amount']:.2f}\n"
            message += f"**Due Date**: {status_data['expires_at'][:10]}\n\n"
            message += f"**Payment URL**: {firestore_data.get('payment_url', 'N/A')}\n\n"
            message += "Please complete your payment to avoid any late fees."
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to send payment reminder: {e}")
            return f"❌ Error sending payment reminder: {str(e)}"


# Global payment commands instance
_payment_commands_instances: dict[str, PaymentCommands] = {}

def get_payment_commands(team_id: str) -> PaymentCommands:
    """Get the payment commands instance for the specified team."""
    global _payment_commands_instances
    
    if team_id not in _payment_commands_instances:
        _payment_commands_instances[team_id] = PaymentCommands(team_id=team_id)
        logger.info(f"Created new PaymentCommands instance for team: {team_id}")
    
    return _payment_commands_instances[team_id] 