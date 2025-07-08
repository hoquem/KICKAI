#!/usr/bin/env python3
"""
Telegram Handlers Package

This package contains modular handlers for different types of Telegram commands.
Each handler follows the single responsibility principle and inherits from BaseHandler
for common functionality like logging, error handling, and response formatting.
"""

from .base_handler import BaseHandler, HandlerContext, HandlerResult
from .player_registration_handler import PlayerRegistrationHandler, handle_player_registration_command

__all__ = [
    'BaseHandler',
    'HandlerContext', 
    'HandlerResult',
    'PlayerRegistrationHandler',
    'handle_player_registration_command'
] 