"""
Command Processor

This module provides command processing logic.
"""

import logging
from typing import Tuple
from telegram import Update
from telegram.ext import ContextTypes

from core.context_manager import UserContext
from bot_telegram.command_dispatcher import get_command_dispatcher

logger = logging.getLogger(__name__)


class CommandProcessor:
    """Handles command processing."""
    
    def __init__(self):
        self.command_dispatcher = get_command_dispatcher()
    
    async def process_slash_command(self, message_text: str, user_context: UserContext, update: Update) -> Tuple[bool, str]:
        """Process a slash command."""
        try:
            # Use the command dispatcher to handle the command
            result = await self.command_dispatcher.dispatch_command(update, None)
            
            if result:
                return True, result
            else:
                return False, "Command not found or not implemented"
                
        except Exception as e:
            logger.error(f"Error processing command '{message_text}': {e}")
            return False, f"Error processing command: {str(e)}"
    
    async def process_natural_language(self, message_text: str, user_context: UserContext) -> str:
        """Process natural language using the NLP processor."""
        try:
            from .nlp_processor import NaturalLanguageProcessor
            
            nlp_processor = NaturalLanguageProcessor(user_context.team_id)
            result = await nlp_processor.process_natural_language(message_text, user_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing natural language '{message_text}': {e}")
            return f"Error processing natural language: {str(e)}"
    
    def is_command(self, message_text: str) -> bool:
        """Check if a message is a command."""
        return message_text.startswith('/')
    
    def extract_command_name(self, message_text: str) -> str:
        """Extract command name from message text."""
        if not self.is_command(message_text):
            return ""
        
        parts = message_text.split()
        return parts[0] if parts else ""
    
    def extract_command_args(self, message_text: str) -> list:
        """Extract command arguments from message text."""
        if not self.is_command(message_text):
            return []
        
        parts = message_text.split()
        return parts[1:] if len(parts) > 1 else [] 