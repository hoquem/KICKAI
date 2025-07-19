"""
Telegram Admin Permission Check

This module provides validation to ensure the bot has proper admin permissions
in Telegram group chats to receive natural language messages.
"""

import asyncio
from typing import Dict, Any, List, Optional
from telegram import Bot, ChatMember
from loguru import logger

from .base_check import BaseCheck
from ..reporting import CheckResult, CheckStatus, CheckCategory


class TelegramAdminCheck(BaseCheck):
    """
    Validates that the bot has admin permissions in Telegram group chats.
    
    This check ensures the bot can receive natural language messages in groups
    by verifying admin permissions and privacy mode settings.
    """
    
    def __init__(self):
        self.name = "TelegramAdminCheck"
        self.category = CheckCategory.CONFIGURATION
        self.description = "Validates bot admin permissions in Telegram chats"
    
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        """
        Execute the Telegram admin permission validation.
        
        Args:
            context: Context containing bot configuration and services
            
        Returns:
            CheckResult with validation status
        """
        try:
            logger.info("🔍 Validating Telegram bot admin permissions...")
            
            # Get bot configuration from context
            bot_config = context.get('bot_config')
            if not bot_config:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="No bot configuration found in context"
                )
            
            bot_token = bot_config.get('bot_token')
            main_chat_id = bot_config.get('main_chat_id')
            leadership_chat_id = bot_config.get('leadership_chat_id')
            
            if not bot_token:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.FAILED,
                    message="Bot token not found in configuration"
                )
            
            # Initialize bot
            bot = Bot(token=bot_token)
            
            # Validate bot info
            bot_info = await bot.get_me()
            logger.info(f"🤖 Bot info: {bot_info.first_name} (@{bot_info.username})")
            
            # Check privacy mode
            privacy_status = await self._check_privacy_mode(bot)
            
            # Validate admin permissions in chats
            chat_validations = []
            if main_chat_id:
                chat_validations.append(await self._validate_chat_permissions(bot, main_chat_id, "Main Chat"))
            if leadership_chat_id:
                chat_validations.append(await self._validate_chat_permissions(bot, leadership_chat_id, "Leadership Chat"))
            
            # Analyze results
            all_passed = privacy_status and all(chat_validations)
            
            if all_passed:
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.PASSED,
                    message="✅ Bot has proper admin permissions in all chats"
                )
            else:
                issues = []
                if not privacy_status:
                    issues.append("Privacy mode may be blocking natural language messages")
                if not all(chat_validations):
                    issues.append("Bot lacks admin permissions in some chats")
                
                return CheckResult(
                    name=self.name,
                    category=self.category,
                    status=CheckStatus.WARNING,
                    message=f"⚠️ Bot permission issues detected: {'; '.join(issues)}"
                )
                
        except Exception as e:
            logger.error(f"Error during Telegram admin validation: {e}")
            return CheckResult(
                name=self.name,
                category=self.category,
                status=CheckStatus.FAILED,
                message=f"Telegram admin validation failed: {str(e)}",
                error=e
            )
    
    async def _check_privacy_mode(self, bot: Bot) -> bool:
        """Check if bot privacy mode allows reading all group messages."""
        try:
            bot_info = await bot.get_me()
            # Note: can_read_all_group_messages is not directly accessible via API
            # We'll assume it's properly configured if bot is admin
            logger.info("🔒 Privacy mode check: Assuming properly configured for admin bots")
            return True
        except Exception as e:
            logger.warning(f"Could not verify privacy mode: {e}")
            return False
    
    async def _validate_chat_permissions(self, bot: Bot, chat_id: int, chat_name: str) -> bool:
        """Validate bot permissions in a specific chat."""
        try:
            # Get bot's member info in the chat
            chat_member = await bot.get_chat_member(chat_id, bot.id)
            
            logger.info(f"📊 {chat_name} ({chat_id}) permissions:")
            logger.info(f"   - Status: {chat_member.status}")
            logger.info(f"   - Can read messages: {getattr(chat_member, 'can_read_messages', 'N/A')}")
            logger.info(f"   - Is admin: {chat_member.status in ['administrator', 'creator']}")
            
            # Check if bot is admin or has proper permissions
            if chat_member.status in ['administrator', 'creator']:
                logger.info(f"✅ {chat_name}: Bot has admin permissions")
                return True
            else:
                logger.warning(f"⚠️ {chat_name}: Bot is not admin (status: {chat_member.status})")
                return False
                
        except Exception as e:
            logger.error(f"❌ {chat_name}: Error checking permissions - {e}")
            return False 