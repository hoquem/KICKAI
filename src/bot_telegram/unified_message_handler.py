#!/usr/bin/env python3
"""
Unified Message Handler for KICKAI Bot

This module provides a single, unified entry point for all Telegram message handling
using the intelligent 8-agent CrewAI system. It replaces the complex routing logic
with a clean, maintainable architecture.
"""

import asyncio
import traceback
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime

# Import Telegram types
from telegram import Update
from telegram.ext import ContextTypes

# Import core components
from core.improved_config_system import get_improved_config
from agents.crew_agents import TeamManagementSystem
from services.team_mapping_service import get_team_mapping_service
from database.models_improved import PlayerRole
# Removed onboarding handler import - onboarding functionality has been simplified
from services.player_service import get_player_service

# Import centralized logging configuration
from core.logging_config import (
    get_logger, LogContext, LogMessages,
    log_user_event, log_performance, log_errors
)

# Import core components
from services.command_operations_factory import get_command_operations
from bot_telegram.unified_command_system import is_slash_command, extract_command_name, process_command
from telegram.ext import MessageHandler, filters

logger = logging.getLogger(__name__)


class UnifiedMessageHandler:
    """
    Unified message handler that processes all incoming messages.
    Now fully CrewAI-powered: all intent, routing, and execution is handled by the intelligent system and CrewAI agents.
    """
    def __init__(self, team_id: str):
        """Initialize the unified message handler for a specific team."""
        self.team_id = team_id
        self.team_config = None
        self.team_system = None
        self.player_service = get_player_service()
        
        # Initialize team configuration
        self._initialize_team_config()
        
        # Initialize the intelligent agent system
        self._initialize_agent_system()
        
        logger.info(f"[UMH INIT] UnifiedMessageHandler initialized for team {team_id}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Handle incoming messages using the intelligent agent system (async)."""
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
            
            # Enhanced debugging for /myinfo command
            is_myinfo_command = text.lower().strip() == "/myinfo"
            if is_myinfo_command:
                logger.info(f"🔍 MYINFO COMMAND DETECTED - Starting end-to-end trace")
                logger.info(f"🔍 MYINFO FLOW STEP 1: Message received from {username} ({user_id}) in {chat_id}")
            
            logger.info(f"Processing message: {text[:20]}... from {username} ({user_id}) in {chat_id}")
            
            # Execute task using the intelligent agent system for non-slash commands
            if is_myinfo_command:
                logger.info(f"🔍 MYINFO FLOW STEP 3: Preparing execution context")
            
            # Prepare execution context
            execution_context = {
                'user_id': user_id,
                'chat_id': chat_id,
                'username': username,
                'team_id': self.team_id,
                'message_text': text,
                'is_leadership_chat': await self._is_leadership_chat(chat_id),
                'user_role': await self._get_user_role(user_id),
                'timestamp': datetime.now().isoformat(),
                'command_text': text  # Always include the original command text
            }
            
            if is_myinfo_command:
                logger.info(f"🔍 MYINFO FLOW STEP 4: Execution context prepared")
                logger.info(f"🔍 MYINFO FLOW STEP 4a: user_role={execution_context['user_role']}, is_leadership_chat={execution_context['is_leadership_chat']}")
            
            # Check if this is a slash command and route to unified command system
            if text.startswith('/'):
                logger.info(f"🔍 SLASH COMMAND DETECTED: {text}")
                try:
                    # Extract command name and route to unified command system
                    from bot_telegram.unified_command_system import process_command, extract_command_name
                    command_name = extract_command_name(text)
                    if command_name:
                        result = await process_command(command_name, user_id, chat_id, self.team_id, text, username, update)
                        logger.info(f"🔍 UNIFIED COMMAND RESULT: {result.message}")
                        return result.message
                    else:
                        logger.warning(f"🔍 COULD NOT EXTRACT COMMAND NAME FROM: {text}")
                except Exception as e:
                    logger.error(f"Error in unified command system: {e}", exc_info=True)
                    # Fallback to intelligent system
                    logger.info(f"🔍 FALLING BACK TO INTELLIGENT SYSTEM")
            
            # Execute task using the intelligent agent system for non-slash commands
            if is_myinfo_command:
                logger.info(f"🔍 MYINFO FLOW STEP 5: Calling TeamManagementSystem.execute_task")
            
            result = await self.team_system.execute_task(text, execution_context)
            
            if is_myinfo_command:
                logger.info(f"🔍 MYINFO FLOW STEP 6: TeamManagementSystem.execute_task completed")
                logger.info(f"🔍 MYINFO FLOW STEP 6a: Result length={len(result) if result else 0}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in UnifiedMessageHandler.handle_message: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error processing your message: {str(e)}"
    
    async def _determine_user_role(self, user_id: str) -> str:
        """Determine user role for the current team."""
        try:
            # Get player by telegram ID
            players = await self.player_service.get_team_players(self.team_id)
            for player in players:
                if player.telegram_id == user_id:
                    if player.role == PlayerRole.ADMIN:
                        return 'admin'
                    elif player.role == PlayerRole.LEADER:
                        return 'leader'
                    else:
                        return 'player'
            return 'player'  # Default to player if not found
        except Exception as e:
            logger.error(f"Error determining user role: {e}")
            return 'player'  # Default to player on error
    
    async def _is_leadership_chat(self, chat_id: str) -> bool:
        """Check if the chat is a leadership chat."""
        try:
            from services.access_control_service import AccessControlService
            access_control = AccessControlService()
            return access_control.is_leadership_chat(chat_id, self.team_id)
        except Exception as e:
            logger.warning(f"Error checking leadership chat for {chat_id}: {e}")
            return False

    async def _get_user_role(self, user_id: str) -> str:
        """Get user role for permission checking."""
        try:
            # Get player by telegram ID
            players = await self.player_service.get_team_players(self.team_id)
            for player in players:
                if player.telegram_id == user_id:
                    if player.role == PlayerRole.ADMIN:
                        return 'admin'
                    elif player.role == PlayerRole.LEADER:
                        return 'leader'
                    else:
                        return 'player'
            return 'player'  # Default to player if not found
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return 'player'  # Default to player on error

    def _initialize_team_config(self):
        """Initialize team configuration."""
        try:
            # Get team mapping service
            team_mapping_service = get_team_mapping_service()
            team_mapping = team_mapping_service.get_team_mapping(self.team_id)
            
            if team_mapping:
                self.team_config = team_mapping
                logger.info(f"Team configuration loaded for {self.team_id}")
            else:
                logger.error(f"No team configuration found for {self.team_id}")
        except Exception as e:
            logger.error(f"Error initializing team config: {e}")

    def _initialize_agent_system(self):
        """Initialize the intelligent agent system."""
        try:
            logger.info(f"[UMH INIT] About to instantiate TeamManagementSystem for team {self.team_id}")
            self.team_system = TeamManagementSystem(self.team_id)
            logger.info(f"[UMH INIT] TeamManagementSystem instance id: {id(self.team_system)} for team {self.team_id}")
        except Exception as e:
            logger.error(f"Error initializing agent system: {e}")
            self.team_system = None


# ============================================================================
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# ============================================================================

_unified_handler: Optional[UnifiedMessageHandler] = None


async def _get_team_id_from_context(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    """
    Get team ID from context using the improved configuration system.
    
    This function uses multiple strategies to determine the correct team ID:
    - Bot token (different bots for different teams)
    - Bot username
    - Chat ID (different chats for different teams)
    - Default team ID (fallback)
    """
    try:
        # Get the improved configuration manager
        config_manager = get_improved_config()
        
        # Extract context information
        bot_token = None
        bot_username = None
        chat_id = None
        
        # Get bot information
        if hasattr(context, 'bot') and hasattr(context.bot, 'token'):
            bot_token = context.bot.token
            bot_username = context.bot.username
        
        # Get chat information
        if update.effective_chat:
            chat_id = str(update.effective_chat.id)
        
        # Resolve team ID using the improved config system
        team_id = config_manager.resolve_team_id(
            bot_token=bot_token,
            bot_username=bot_username,
            chat_id=chat_id
        )
        
        logger.debug(f"Resolved team ID: {team_id} (bot: {bot_username}, chat: {chat_id})")
        return team_id
        
    except Exception as e:
        logger.error(f"Error getting team ID from context: {e}")
        # Fallback to default team ID
        try:
            config_manager = get_improved_config()
            default_team_config = config_manager.get_default_team_config()
            if default_team_config:
                return default_team_config.team_id
            return os.getenv('DEFAULT_TEAM_ID', 'KAI')
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
    Team ID is resolved dynamically for each message using the team mapping service.
    """
    try:
        # Get team ID from context or config
        team_id = await _get_team_id_from_context(context, update)
        
        # Get the unified handler
        handler = get_unified_handler(team_id)
        
        # Process the message
        result = await handler.handle_message(update, context)
        
        # Debug logging for response
        logger.info(f"🔍 TELEGRAM RESPONSE DEBUG: result={result}")
        logger.info(f"🔍 TELEGRAM RESPONSE DEBUG: result type={type(result)}")
        logger.info(f"🔍 TELEGRAM RESPONSE DEBUG: result length={len(result) if result else 0}")
        logger.info(f"🔍 TELEGRAM RESPONSE DEBUG: update.effective_message={update.effective_message is not None}")
        
        # Send response if we have one
        if result and update.effective_message:
            logger.info(f"🔍 TELEGRAM RESPONSE DEBUG: Sending response to Telegram")
            await update.effective_message.reply_text(
                result,
                parse_mode='HTML'
            )
        elif not result:
            logger.warning(f"🔍 TELEGRAM RESPONSE DEBUG: No result to send")
        elif not update.effective_message:
            logger.warning(f"🔍 TELEGRAM RESPONSE DEBUG: No effective message to reply to")
            
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
        from bot_telegram.unified_message_handler import register_unified_handler
        
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