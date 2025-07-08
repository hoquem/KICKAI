#!/usr/bin/env python3
"""
Unified Message Handler for KICKAI Bot

This module provides a single entry point for all message processing,
handling both slash commands and natural language with proper routing
and error handling.
"""

import asyncio
import traceback
from typing import Dict, Any, Optional
import os

# Import Telegram types
from telegram import Update
from telegram.ext import ContextTypes

# Import centralized logging configuration
from core.logging_config import (
    get_logger, LogContext, LogMessages,
    log_user_event, log_performance, log_errors
)

# Import core components
from src.services.team_mapping_service import TeamMappingService
from src.services.command_operations_factory import get_command_operations
from src.telegram.unified_command_system import is_slash_command, extract_command_name, process_command
from src.agents.crew_agents import TeamManagementSystem
from src.core.improved_config_system import get_improved_config
from src.core.exceptions import KICKAIError

logger = get_logger(__name__)


class UnifiedMessageHandler:
    """
    Unified message handler that processes all incoming messages.
    Now fully CrewAI-powered: all intent, routing, and execution is handled by the intelligent system and CrewAI agents.
    """
    def __init__(self, team_id: str):
        self.team_id = team_id
        # Initialize the intelligent TeamManagementSystem
        # All intelligent system components are now integrated into TeamManagementSystem.execute_task
        self.team_system = TeamManagementSystem(team_id)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        try:
            message = update.effective_message
            if not message or not message.text:
                return None
            text = message.text.strip()
            if not text:
                return None
            if not update.effective_user or not update.effective_chat:
                return "❌ Unable to process message: Missing user or chat information"
            user_id = str(update.effective_user.id)
            chat_id = str(update.effective_chat.id)
            username = update.effective_user.username or "unknown"
            log_context = LogContext(
                team_id=self.team_id,
                user_id=user_id,
                chat_id=chat_id,
                operation="message_processing",
                component="unified_handler"
            )
            logger.info(f"Processing message: {text[:50]}... from {username} ({user_id}) in {chat_id}", context=log_context)
            
            # Check for onboarding response first
            onboarding_response = await self._handle_onboarding_response(user_id, text)
            if onboarding_response:
                return onboarding_response
            
            # Prepare context for intelligent system
            execution_context = {
                'user_id': user_id,
                'chat_id': chat_id,
                'username': username,
                'team_id': self.team_id,
                'user_role': await self._get_user_role(user_id),
                'is_leadership_chat': await self._is_leadership_chat(chat_id),
                'user_history': [],  # TODO: Implement user history tracking
                'message_timestamp': message.date.isoformat() if message.date else None
            }
            
            # Use the intelligent TeamManagementSystem.execute_task method
            # This now includes the full intelligent system pipeline:
            # 1. Intent classification
            # 2. Complexity assessment  
            # 3. Task decomposition
            # 4. Capability-based routing
            # 5. Orchestrated execution
            # 6. Result aggregation
            # 7. User preference learning
            # 8. Response personalization
            result = self.team_system.execute_task(text, execution_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in CrewAI-powered unified message handler: {e}",
                        context=LogContext(team_id=self.team_id, component="unified_handler"), exc_info=e)
            return f"❌ Sorry, I encountered an error processing your request: {str(e)}"
    
    async def _handle_onboarding_response(self, user_id: str, text: str) -> Optional[str]:
        """Handle onboarding responses using improved workflow."""
        try:
            # Import improved onboarding workflow
            from .onboarding_handler_improved import get_improved_onboarding_workflow
            
            # Check if user is in onboarding
            improved_workflow = get_improved_onboarding_workflow(self.team_id)
            
            # Try to process as onboarding response
            success, message = await improved_workflow.process_response(user_id, text)
            
            if success:
                logger.info(f"Onboarding response processed for user {user_id}",
                           context=LogContext(team_id=self.team_id, user_id=user_id, operation="onboarding"))
                return message
            else:
                # Not an onboarding response, continue with normal processing
                logger.debug(f"Not an onboarding response for user {user_id}",
                           context=LogContext(team_id=self.team_id, user_id=user_id, operation="onboarding"))
                return None
                
        except Exception as e:
            logger.error(f"Error handling onboarding response: {e}",
                        context=LogContext(team_id=self.team_id, user_id=user_id, operation="onboarding"), exc_info=e)
            return None
    
    async def _get_user_role(self, user_id: str) -> str:
        """Get user role for context."""
        try:
            from src.services.user_management_factory import get_user_management
            user_management = get_user_management()
            return await user_management.get_user_role(user_id, self.team_id)
        except Exception as e:
            logger.error(f"Error getting user role: {e}",
                        context=LogContext(team_id=self.team_id, user_id=user_id, operation="get_user_role"), exc_info=e)
            return 'player'  # Default to player
    
    async def _is_leadership_chat(self, chat_id: str) -> bool:
        """Check if this is a leadership chat."""
        try:
            from src.services.user_management_factory import get_user_management
            user_management = get_user_management()
            return await user_management.is_leadership_chat(chat_id, self.team_id)
        except Exception as e:
            logger.error(f"Error checking leadership chat: {e}",
                        context=LogContext(team_id=self.team_id, chat_id=chat_id, operation="check_leadership_chat"), exc_info=e)
            return False


# ============================================================================
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# ============================================================================

_unified_handler: Optional[UnifiedMessageHandler] = None


async def _get_team_id_from_context(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    """
    Get team ID from context using the team mapping service.
    
    This function uses multiple strategies to determine the correct team ID:
    - Bot token (different bots for different teams)
    - Bot username
    - Chat ID (different chats for different teams)
    - User context (user's team membership)
    - Default team ID (fallback)
    """
    try:
        from src.services.team_mapping_service import get_team_mapping_service
        
        # Get the team mapping service
        team_mapping_service = get_team_mapping_service(team_id=None)  # Use default for fallback
        
        # Extract context information
        bot_token = None
        bot_username = None
        chat_id = None
        user_id = None
        
        # Get bot information
        if hasattr(context, 'bot') and hasattr(context.bot, 'token'):
            bot_token = context.bot.token
            bot_username = context.bot.username
        
        # Get chat information
        if update.effective_chat:
            chat_id = str(update.effective_chat.id)
        
        # Get user information
        if update.effective_user:
            user_id = str(update.effective_user.id)
        
        # Resolve team ID using the mapping service
        team_id = team_mapping_service.resolve_team_id(
            bot_token=bot_token,
            bot_username=bot_username,
            chat_id=chat_id,
            user_id=user_id
        )
        
        logger.debug(f"Resolved team ID: {team_id} (bot: {bot_username}, chat: {chat_id}, user: {user_id})")
        return team_id
        
    except Exception as e:
        logger.error(f"Error getting team ID from context: {e}")
        # Fallback to default team ID
        try:
            from src.services.team_mapping_service import get_team_mapping_service
            team_mapping_service = get_team_mapping_service(team_id=None)  # Use default for fallback
            return team_mapping_service.get_default_team_id() or os.getenv('DEFAULT_TEAM_ID', 'KAI')
        except:
            return os.getenv('DEFAULT_TEAM_ID', 'KAI')  # Final fallback


def get_unified_handler(team_id: str) -> UnifiedMessageHandler:
    """Get the global unified message handler."""
    global _unified_handler
    if _unified_handler is None or _unified_handler.team_id != team_id:
        _unified_handler = UnifiedMessageHandler(team_id)
    return _unified_handler


async def handle_message_unified(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global message handler function for registration with telegram.ext.
    
    This is the single entry point that replaces all the complex routing.
    """
    try:
        # Get team ID from context or config
        team_id = await _get_team_id_from_context(context, update)
        
        # Get the unified handler
        handler = get_unified_handler(team_id)
        
        # Process the message
        result = await handler.handle_message(update, context)
        
        # Send response if we have one
        if result and update.effective_message:
            await update.effective_message.reply_text(
                result,
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"Error in global message handler: {e}")
        try:
            if update.effective_message:
                max_attempts = 3
                for attempt in range(1, max_attempts + 1):
                    try:
                        await update.effective_message.reply_text(
                            "❌ Sorry, I encountered an error processing your request. Please try again.",
                            parse_mode='HTML'
                        )
                        break
                    except Exception as send_error:
                        logger.error(f"Failed to send error message (attempt {attempt}): {send_error}")
                        if attempt < max_attempts:
                            await asyncio.sleep(1)
                        else:
                            logger.error(f"Giving up after {max_attempts} attempts to send error message.")
        except Exception as send_error:
            logger.error(f"Failed to send error message (outer): {send_error}")


# ============================================================================
# REGISTRATION FUNCTIONS
# ============================================================================

def register_unified_handler(app):
    """
    Register the unified message handler with the telegram application.
    
    This replaces all the complex command registration with a single, clean handler.
    Team ID is resolved dynamically for each message using the team mapping service.
    """
    try:
        from telegram.ext import MessageHandler, filters
        
        # Register handler for all text messages (both commands and natural language)
        app.add_handler(MessageHandler(filters.TEXT, handle_message_unified))
        
        logger.info("✅ Unified message handler registered successfully")
        logger.info("   Team ID: Resolved dynamically per message")
        logger.info("   Handles: Slash commands and natural language")
        logger.info("   Architecture: Clean, maintainable, single entry point")
        
    except Exception as e:
        logger.error(f"❌ Failed to register unified message handler: {e}")
        raise


# ============================================================================
# MIGRATION HELPER FUNCTIONS
# ============================================================================

def get_migration_status() -> Dict[str, Any]:
    """
    Get the status of the migration to the unified system.
    
    This helps track what needs to be migrated from the old system.
    """
    return {
        "unified_system_ready": True,
        "old_handlers_to_remove": [
            "src.telegram.command_dispatcher.CommandDispatcher",
            "src.telegram.telegram_command_handler.AgentBasedMessageHandler",
            "src.telegram.telegram_command_handler.llm_command_handler",
            "src.agents.handlers.SimpleAgenticHandler._route_command",
        ],
        "new_architecture": {
            "command_pattern": "Each command is a separate object",
            "strategy_pattern": "Different permission strategies",
            "chain_of_responsibility": "Command routing and validation",
            "factory_pattern": "Command creation",
            "single_entry_point": "UnifiedMessageHandler.handle_message",
        },
        "benefits": [
            "Single responsibility principle",
            "Open/closed principle",
            "Dependency inversion",
            "Easy to test",
            "Easy to extend",
            "No more routing conflicts",
            "Clear permission system",
            "Consistent error handling",
        ]
    }


def print_migration_guide():
    """Print a guide for migrating to the unified system."""
    print("""
🔄 MIGRATION GUIDE: Unified Command System

The new unified command system replaces the complex routing with clean OOP principles:

📋 WHAT TO DO:
1. Replace the old command registration in run_telegram_bot.py:
   OLD: register_langchain_agentic_handler(app)
   NEW: register_unified_handler(app)

2. Remove old routing files:
   - src/telegram/command_dispatcher.py (replaced)
   - Complex routing in telegram_command_handler.py (simplified)

3. Update imports to use the new system:
   from telegram.unified_message_handler import register_unified_handler

🎯 BENEFITS:
- Single entry point for all messages
- Clear permission system
- Easy to add new commands
- No more routing conflicts
- Consistent error handling
- Testable architecture

🏗️ ARCHITECTURE:
- Command Pattern: Each command is a separate object
- Strategy Pattern: Different permission strategies  
- Chain of Responsibility: Command routing and validation
- Factory Pattern: Command creation
- Single Responsibility: Each class has one job

Ready to migrate! 🚀
    """)


if __name__ == "__main__":
    print_migration_guide() 