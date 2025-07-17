"""
Simplified Message Handler - Modular Architecture

This module has been refactored to use a modular architecture with separate
components for validation, processing, and logging.

The monolithic SimplifiedMessageHandler has been split into focused components:
- validation/: Message validation and permission checking
- processing/: Command and NLP processing
- logging/: Message logging and error handling
- handler.py: Main orchestrator class

This refactoring follows the single responsibility principle and improves
maintainability and testability.
"""

# Import from the new modular structure
from .message_handling import (
    SimplifiedMessageHandler,
    get_simplified_message_handler,
    handle_message,
    register_simplified_handler,
    MessageContext
)

from .message_handling.validation import (
    MessageValidator,
    PermissionChecker
)

from .message_handling.processing import (
    CommandProcessor,
    NaturalLanguageProcessor
)

from .message_handling.logging import (
    MessageLogger,
    ErrorHandler
)

# Re-export for backward compatibility
__all__ = [
    'SimplifiedMessageHandler',
    'get_simplified_message_handler',
    'handle_message',
    'register_simplified_handler',
    'MessageContext',
    'MessageValidator',
    'PermissionChecker',
    'CommandProcessor',
    'NaturalLanguageProcessor',
    'MessageLogger',
    'ErrorHandler'
] 