#!/usr/bin/env python3
"""
Unified Message Handler for KICKAI Bot

This module provides a single, clean entry point for all message processing
using the unified command system. It replaces all the complex routing logic
with a simple, maintainable architecture.

Design Patterns Used:
- Facade Pattern: Single interface for all message handling
- Strategy Pattern: Different handling strategies for different message types
- Chain of Responsibility: Message processing pipeline
"""

import logging
from typing import Optional, Any, Dict
from telegram import Update
from telegram.ext import ContextTypes

from .unified_command_system import (
    process_command, is_slash_command, extract_command_name,
    CommandResult
)

logger = logging.getLogger(__name__)


class UnifiedMessageHandler:
    """
    Unified message handler that processes all incoming messages.
    
    This replaces the complex routing system with a single, clean interface.
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up message handlers."""
        # Import here to avoid circular imports
        try:
            from src.agents.handlers import SimpleAgenticHandler
            self.agentic_handler = SimpleAgenticHandler(self.team_id)
            logger.info("✅ Agentic handler initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agentic handler: {e}")
            self.agentic_handler = None
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """
        Main entry point for all message handling.
        
        This method determines the message type and routes it to the appropriate handler.
        """
        try:
            # Extract message information
            message = update.effective_message
            if not message or not message.text:
                return None
            
            text = message.text.strip()
            if not text:
                return None
            
            # Check for required user and chat information
            if not update.effective_user or not update.effective_chat:
                return "❌ Unable to process message: Missing user or chat information"
            
            user_id = str(update.effective_user.id)
            chat_id = str(update.effective_chat.id)
            username = update.effective_user.username or "unknown"
            
            logger.info(f"Processing message: {text[:50]}... from {username} ({user_id}) in {chat_id}")
            
            # Determine message type and route accordingly
            if is_slash_command(text):
                return await self._handle_slash_command(text, user_id, chat_id, username, update)
            else:
                return await self._handle_natural_language(text, user_id, chat_id, username, update)
                
        except Exception as e:
            logger.error(f"Error in unified message handler: {e}")
            return f"❌ Sorry, I encountered an error processing your request: {str(e)}"
    
    async def _handle_slash_command(self, text: str, user_id: str, chat_id: str, 
                                  username: str, update: Update) -> str:
        """Handle slash commands using the unified command system."""
        try:
            # Extract command name
            command_name = extract_command_name(text)
            if not command_name:
                return "❌ Invalid command format. Commands should start with '/'"
            
            logger.info(f"Processing slash command: {command_name}")
            
            # Process command using unified system
            result = await process_command(
                command_name=command_name,
                user_id=user_id,
                chat_id=chat_id,
                team_id=self.team_id,
                message_text=text,
                username=username,
                raw_update=update
            )
            
            if result.success:
                logger.info(f"✅ Command {command_name} executed successfully")
                return result.message
            else:
                logger.warning(f"❌ Command {command_name} failed: {result.error}")
                return result.message
                
        except Exception as e:
            logger.error(f"Error handling slash command: {e}")
            return f"❌ Error processing command: {str(e)}"
    
    async def _handle_natural_language(self, text: str, user_id: str, chat_id: str, 
                                     username: str, update: Update) -> str:
        """Handle natural language messages using the agentic system."""
        try:
            if not self.agentic_handler:
                return "❌ Natural language processing is currently unavailable. Please use slash commands."
            
            logger.info(f"Processing natural language: {text[:50]}...")
            
            # Get user role for context
            user_role = await self._get_user_role(user_id)
            
            # Determine if this is a leadership chat
            is_leadership = await self._is_leadership_chat(chat_id)
            
            # Process with agentic handler
            result = await self.agentic_handler.process_message(
                message=text,
                user_id=user_id,
                chat_id=chat_id,
                user_role=user_role,
                is_leadership_chat=is_leadership
            )
            
            logger.info(f"✅ Natural language processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error handling natural language: {e}")
            return f"❌ Error processing your request: {str(e)}"
    
    async def _get_user_role(self, user_id: str) -> str:
        """Get user role for context."""
        try:
            from src.services.team_member_service import TeamMemberService
            from src.database.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
            team_service = TeamMemberService(firebase_client)
            member = await team_service.get_team_member_by_telegram_id(user_id, self.team_id)
            if member and member.roles:
                return member.roles[0]  # Return first role
            return 'player'
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return 'player'  # Default to player
    
    async def _is_leadership_chat(self, chat_id: str) -> bool:
        """Check if this is a leadership chat."""
        try:
            from src.services.access_control_service import AccessControlService
            access_control = AccessControlService()
            return access_control.is_leadership_chat(chat_id, self.team_id)
        except Exception as e:
            logger.error(f"Error checking leadership chat: {e}")
            return False


# ============================================================================
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# ============================================================================

_unified_handler: Optional[UnifiedMessageHandler] = None


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
        team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # Default team ID
        
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
                await update.effective_message.reply_text(
                    "❌ Sorry, I encountered an error processing your request. Please try again.",
                    parse_mode='HTML'
                )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")


# ============================================================================
# REGISTRATION FUNCTIONS
# ============================================================================

def register_unified_handler(app, team_id: str = "0854829d-445c-4138-9fd3-4db562ea46ee"):
    """
    Register the unified message handler with the telegram application.
    
    This replaces all the complex command registration with a single, clean handler.
    """
    try:
        from telegram.ext import MessageHandler, filters
        
        # Register handler for all text messages (both commands and natural language)
        app.add_handler(MessageHandler(filters.TEXT, handle_message_unified))
        
        logger.info("✅ Unified message handler registered successfully")
        logger.info(f"   Team ID: {team_id}")
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
   from src.telegram.unified_message_handler import register_unified_handler

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