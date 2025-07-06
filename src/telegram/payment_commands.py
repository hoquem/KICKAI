#!/usr/bin/env python3
"""
Payment Commands for KICKAI Telegram Bot

This module provides payment-related commands for the Telegram bot.
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from src.core.config import get_config
from src.tools.payment_tools import PaymentTools
from src.services.player_service import PlayerService
from src.services.team_service import TeamService
from src.core.exceptions import PaymentError, ValidationError

logger = logging.getLogger(__name__)


class PaymentCommands:
    """Payment commands for the Telegram bot."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.config = get_config()
        self.payment_tools = PaymentTools(team_id)
        self.player_service = PlayerService(team_id)
        self.team_service = TeamService(team_id)
        
        logger.info(f"✅ Payment Commands initialized for team {team_id}")
    
    async def handle_payment_command(self, command: str, args: List[str], user_id: str) -> str:
        """Handle payment-related commands."""
        try:
            if command == "create_match_fee":
                return await self._create_match_fee_payment(args, user_id)
            elif command == "create_membership_fee":
                return await self._create_membership_fee_payment(args, user_id)
            elif command == "create_fine":
                return await self._create_fine_payment(args, user_id)
            elif command == "payment_status":
                return await self._get_payment_status(args, user_id)
            elif command == "pending_payments":
                return await self._get_pending_payments(args, user_id)
            elif command == "payment_history":
                return await self._get_payment_history(args, user_id)
            elif command == "payment_stats":
                return await self._get_payment_stats(user_id)
            else:
                return "❌ Unknown payment command. Available commands: create_match_fee, create_membership_fee, create_fine, payment_status, pending_payments, payment_history, payment_stats"
                
        except Exception as e:
            logger.error(f"❌ Payment command error: {e}")
            return f"❌ Payment Error: {str(e)}"
    
    async def _create_match_fee_payment(self, args: List[str], user_id: str) -> str:
        """Create a match fee payment."""
        try:
            if len(args) < 3:
                return "❌ Usage: /create_match_fee <player_id> <amount> <match_id> [description]"
            
            player_id = args[0]
            amount = float(args[1])
            match_id = args[2]
            description = " ".join(args[3:]) if len(args) > 3 else ""
            
            # Validate player exists
            player = await self.player_service.get_player(player_id)
            if not player:
                return f"❌ Player {player_id} not found"
            
            # Set match date to tomorrow (placeholder)
            match_date = datetime.now() + timedelta(days=1)
            
            # Create payment
            payment_data = await self.payment_tools.create_match_fee_payment(
                player_id=player_id,
                amount=amount,
                match_id=match_id,
                match_date=match_date,
                description=description
            )
            
            return self.payment_tools.format_payment_message(payment_data)
            
        except ValueError:
            return "❌ Invalid amount. Please provide a valid number."
        except Exception as e:
            logger.error(f"❌ Failed to create match fee payment: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _create_membership_fee_payment(self, args: List[str], user_id: str) -> str:
        """Create a membership fee payment."""
        try:
            if len(args) < 3:
                return "❌ Usage: /create_membership_fee <player_id> <amount> <period> [description]"
            
            player_id = args[0]
            amount = float(args[1])
            period = args[2]
            description = " ".join(args[3:]) if len(args) > 3 else ""
            
            # Validate player exists
            player = await self.player_service.get_player(player_id)
            if not player:
                return f"❌ Player {player_id} not found"
            
            # Create payment
            payment_data = await self.payment_tools.create_membership_fee_payment(
                player_id=player_id,
                amount=amount,
                period=period,
                description=description
            )
            
            return self.payment_tools.format_payment_message(payment_data)
            
        except ValueError:
            return "❌ Invalid amount. Please provide a valid number."
        except Exception as e:
            logger.error(f"❌ Failed to create membership fee payment: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _create_fine_payment(self, args: List[str], user_id: str) -> str:
        """Create a fine payment."""
        try:
            if len(args) < 3:
                return "❌ Usage: /create_fine <player_id> <amount> <reason> [due_days]"
            
            player_id = args[0]
            amount = float(args[1])
            reason = args[2]
            due_days = int(args[3]) if len(args) > 3 else 14
            
            # Validate player exists
            player = await self.player_service.get_player(player_id)
            if not player:
                return f"❌ Player {player_id} not found"
            
            # Calculate due date
            due_date = datetime.now() + timedelta(days=due_days)
            
            # Create payment
            payment_data = await self.payment_tools.create_fine_payment(
                player_id=player_id,
                amount=amount,
                reason=reason,
                due_date=due_date
            )
            
            return self.payment_tools.format_payment_message(payment_data)
            
        except ValueError:
            return "❌ Invalid amount or due days. Please provide valid numbers."
        except Exception as e:
            logger.error(f"❌ Failed to create fine payment: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _get_payment_status(self, args: List[str], user_id: str) -> str:
        """Get payment status."""
        try:
            if len(args) < 1:
                return "❌ Usage: /payment_status <payment_id>"
            
            payment_id = args[0]
            
            # Get payment status
            status_data = await self.payment_tools.get_payment_status(payment_id)
            
            if not status_data.get("success"):
                return f"❌ Error: {status_data.get('error', 'Unknown error')}"
            
            payment_id = status_data.get("payment_id", "Unknown")
            status = status_data.get("status", "unknown")
            amount = status_data.get("amount", 0)
            currency = status_data.get("currency", "GBP")
            created_at = status_data.get("created_at")
            updated_at = status_data.get("updated_at")
            
            message = f"💳 Payment Status\n\n"
            message += f"**Payment ID:** `{payment_id}`\n"
            message += f"**Amount:** £{amount:.2f}\n"
            message += f"**Status:** {status.title()}\n"
            
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    message += f"**Created:** {created_date.strftime('%Y-%m-%d %H:%M')}\n"
                except:
                    pass
            
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    message += f"**Updated:** {updated_date.strftime('%Y-%m-%d %H:%M')}\n"
                except:
                    pass
            
            if status == "completed":
                message += "\n✅ Payment completed successfully!"
            elif status == "pending":
                message += "\n⏰ Payment is pending."
            elif status == "failed":
                message += "\n❌ Payment failed."
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment status: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _get_pending_payments(self, args: List[str], user_id: str) -> str:
        """Get pending payments."""
        try:
            player_id = args[0] if args else None
            
            # Get pending payments
            payments_data = await self.payment_tools.get_pending_payments(player_id)
            
            return self.payment_tools.format_payment_list(payments_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to get pending payments: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _get_payment_history(self, args: List[str], user_id: str) -> str:
        """Get payment history."""
        try:
            player_id = args[0] if args else None
            limit = int(args[1]) if len(args) > 1 else 10
            
            # Get payment history
            payments_data = await self.payment_tools.get_payment_history(player_id, limit)
            
            return self.payment_tools.format_payment_list(payments_data)
            
        except ValueError:
            return "❌ Invalid limit. Please provide a valid number."
        except Exception as e:
            logger.error(f"❌ Failed to get payment history: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _get_payment_stats(self, user_id: str) -> str:
        """Get payment statistics."""
        try:
            # Get payment stats
            stats_data = self.payment_tools.get_payment_stats()
            
            if not stats_data.get("success"):
                return f"❌ Error: {stats_data.get('error', 'Unknown error')}"
            
            stats = stats_data.get("stats", {})
            
            total_payments = stats.get("total_payments", 0)
            completed_payments = stats.get("completed_payments", 0)
            pending_payments = stats.get("pending_payments", 0)
            failed_payments = stats.get("failed_payments", 0)
            total_amount = stats.get("total_amount", 0)
            success_rate = stats.get("success_rate", 0)
            
            message = f"📊 Payment Statistics\n\n"
            message += f"**Total Payments:** {total_payments}\n"
            message += f"**Completed:** {completed_payments}\n"
            message += f"**Pending:** {pending_payments}\n"
            message += f"**Failed:** {failed_payments}\n"
            message += f"**Total Amount:** £{total_amount:.2f}\n"
            message += f"**Success Rate:** {success_rate:.1f}%\n"
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment stats: {e}")
            return f"❌ Error: {str(e)}"
    
    def get_help_message(self) -> str:
        """Get help message for payment commands."""
        message = "💳 Payment Commands\n\n"
        message += "**Match Fees:**\n"
        message += "`/create_match_fee <player_id> <amount> <match_id> [description]`\n\n"
        
        message += "**Membership Fees:**\n"
        message += "`/create_membership_fee <player_id> <amount> <period> [description]`\n\n"
        
        message += "**Fines:**\n"
        message += "`/create_fine <player_id> <amount> <reason> [due_days]`\n\n"
        
        message += "**Payment Status:**\n"
        message += "`/payment_status <payment_id>`\n\n"
        
        message += "**Pending Payments:**\n"
        message += "`/pending_payments [player_id]`\n\n"
        
        message += "**Payment History:**\n"
        message += "`/payment_history [player_id] [limit]`\n\n"
        
        message += "**Payment Statistics:**\n"
        message += "`/payment_stats`\n\n"
        
        message += "**Examples:**\n"
        message += "• `/create_match_fee player123 15.00 match_001`\n"
        message += "• `/create_membership_fee player123 50.00 monthly`\n"
        message += "• `/create_fine player123 10.00 late_attendance 7`\n"
        message += "• `/payment_status pay_123456`\n"
        message += "• `/pending_payments player123`\n"
        message += "• `/payment_history player123 20`\n"
        
        return message 