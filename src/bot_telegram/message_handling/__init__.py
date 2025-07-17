"""
Message Handling System

This package provides a modular message handling system that replaces the monolithic
SimplifiedMessageHandler with smaller, focused components following the single responsibility principle.
"""

from .handler import SimplifiedMessageHandler, get_simplified_message_handler, handle_message, register_simplified_handler
from .validation import MessageValidator, PermissionChecker
from .processing import CommandProcessor, NaturalLanguageProcessor
from .logging import MessageLogger, ErrorHandler

__all__ = [
    'SimplifiedMessageHandler',
    'get_simplified_message_handler',
    'handle_message',
    'register_simplified_handler',
    'MessageValidator',
    'PermissionChecker',
    'CommandProcessor',
    'NaturalLanguageProcessor',
    'MessageLogger',
    'ErrorHandler'
] 