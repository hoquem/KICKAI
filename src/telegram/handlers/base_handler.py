#!/usr/bin/env python3
"""
Base Handler for Telegram Commands

This module provides a base class for all command handlers with common
functionality like logging, error handling, and response formatting.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.core.enhanced_logging import (
    log_command_error, log_error, ErrorCategory, ErrorSeverity,
    create_error_context
)

logger = logging.getLogger(__name__)


@dataclass
class HandlerContext:
    """Context for command handler execution."""
    user_id: str
    chat_id: str
    team_id: str
    username: Optional[str] = None
    raw_update: Optional[Any] = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}


@dataclass
class HandlerResult:
    """Result of command handler execution."""
    success: bool
    message: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, message: str, metadata: Optional[Dict[str, Any]] = None) -> 'HandlerResult':
        """Create a successful result."""
        return cls(success=True, message=message, metadata=metadata)
    
    @classmethod
    def error_result(cls, error: str, metadata: Optional[Dict[str, Any]] = None) -> 'HandlerResult':
        """Create an error result."""
        return cls(success=False, message="", error=error, metadata=metadata)


class BaseHandler(ABC):
    """Base class for all command handlers."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @abstractmethod
    async def handle(self, context: HandlerContext, **kwargs) -> HandlerResult:
        """Handle the command. Must be implemented by subclasses."""
        pass
    
    def log_command_start(self, context: HandlerContext, command_name: str) -> None:
        """Log the start of command execution."""
        self.logger.info(
            f"Starting {command_name} command",
            extra={
                "user_id": context.user_id,
                "chat_id": context.chat_id,
                "team_id": context.team_id,
                "command": command_name
            }
        )
    
    def log_command_success(self, context: HandlerContext, command_name: str, 
                           result: HandlerResult) -> None:
        """Log successful command execution."""
        self.logger.info(
            f"Completed {command_name} command successfully",
            extra={
                "user_id": context.user_id,
                "chat_id": context.chat_id,
                "team_id": context.team_id,
                "command": command_name,
                "result_length": len(result.message) if result.message else 0
            }
        )
    
    def log_command_error(self, context: HandlerContext, command_name: str, 
                         error: Exception, result: HandlerResult) -> None:
        """Log command execution error."""
        error_context = create_error_context(
            user_id=context.user_id,
            chat_id=context.chat_id,
            team_id=context.team_id,
            command=command_name
        )
        
        log_command_error(
            error=error,
            context=error_context,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.COMMAND_EXECUTION
        )
        
        self.logger.error(
            f"Error in {command_name} command: {str(error)}",
            extra={
                "user_id": context.user_id,
                "chat_id": context.chat_id,
                "team_id": context.team_id,
                "command": command_name,
                "error": str(error)
            },
            exc_info=True
        )
    
    async def execute_with_logging(self, context: HandlerContext, 
                                  command_name: str, **kwargs) -> HandlerResult:
        """Execute handler with comprehensive logging."""
        self.log_command_start(context, command_name)
        
        try:
            result = await self.handle(context, **kwargs)
            
            if result.success:
                self.log_command_success(context, command_name, result)
            else:
                self.log_command_error(context, command_name, 
                                     Exception(result.error), result)
            
            return result
            
        except Exception as e:
            result = HandlerResult.error_result(str(e))
            self.log_command_error(context, command_name, e, result)
            return result
    
    def format_success_message(self, title: str, content: str, 
                              additional_info: Optional[Dict[str, Any]] = None) -> str:
        """Format a success message with consistent styling."""
        message_parts = [f"✅ **{title}**\n"]
        message_parts.append(content)
        
        if additional_info:
            message_parts.append("\n**Details:**")
            for key, value in additional_info.items():
                message_parts.append(f"• {key}: {value}")
        
        return "\n".join(message_parts)
    
    def format_error_message(self, title: str, error: str, 
                           suggestions: Optional[list] = None) -> str:
        """Format an error message with consistent styling."""
        message_parts = [f"❌ **{title}**\n"]
        message_parts.append(error)
        
        if suggestions:
            message_parts.append("\n**Suggestions:**")
            for suggestion in suggestions:
                message_parts.append(f"• {suggestion}")
        
        return "\n".join(message_parts)
    
    def validate_required_parameters(self, params: Dict[str, Any], 
                                   required_params: list) -> Tuple[bool, str]:
        """Validate that required parameters are present."""
        missing_params = []
        for param in required_params:
            if param not in params or not params[param]:
                missing_params.append(param)
        
        if missing_params:
            return False, f"Missing required parameters: {', '.join(missing_params)}"
        
        return True, "" 