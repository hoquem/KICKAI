"""
Message Validator

This module provides message validation logic.
"""

import logging
from typing import Tuple
from telegram import Update

logger = logging.getLogger(__name__)


class MessageValidator:
    """Validates incoming messages."""
    
    @staticmethod
    def validate_message(update: Update) -> Tuple[bool, str]:
        """Validate that a message can be processed."""
        if not update.effective_message or not update.effective_message.text:
            return False, "No text message found"
        
        if not update.effective_user or not update.effective_chat:
            return False, "Missing user or chat information"
        
        text = update.effective_message.text.strip()
        if not text:
            return False, "Empty message"
        
        return True, "Valid message"
    
    @staticmethod
    def validate_message_length(text: str, max_length: int = 4096) -> Tuple[bool, str]:
        """Validate message length."""
        if len(text) > max_length:
            return False, f"Message too long (max {max_length} characters)"
        return True, "Valid message length"
    
    @staticmethod
    def validate_command_format(text: str) -> Tuple[bool, str]:
        """Validate command format."""
        if text.startswith('/'):
            # Check for basic command structure
            parts = text.split()
            if len(parts) == 0:
                return False, "Invalid command format"
            
            command = parts[0]
            if len(command) < 2:  # Just "/" is not valid
                return False, "Invalid command format"
            
            return True, "Valid command format"
        
        return True, "Not a command"
    
    @staticmethod
    def sanitize_message(text: str) -> str:
        """Sanitize message text."""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<script>', '</script>', 'javascript:', 'data:']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip() 