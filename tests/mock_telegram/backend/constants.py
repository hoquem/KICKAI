"""
Mock Telegram Backend Constants

This module defines constants for the Mock Telegram testing system,
following fail-fast configuration principles.
"""

import os
from typing import Final

from kickai.core.constants import (
    NetworkConstants,
    TimeoutConstants,
    get_environment_with_default,
    get_mock_telegram_port,
    get_mock_telegram_url
)


class MockTelegramConstants:
    """Constants specific to Mock Telegram system."""
    
    # Default configuration
    DEFAULT_HOST: Final[str] = NetworkConstants.DEFAULT_HOST
    DEFAULT_PORT: Final[int] = NetworkConstants.DEFAULT_MOCK_TELEGRAM_PORT
    
    # API paths
    API_BASE_PATH: Final[str] = "/api"
    WEBSOCKET_PATH: Final[str] = "/ws"
    
    # Mock user IDs (for testing)
    TEST_PLAYER_ID: Final[int] = 1001
    TEST_MEMBER_ID: Final[int] = 1002
    TEST_ADMIN_ID: Final[int] = 1003
    TEST_LEADERSHIP_ID: Final[int] = 1004
    
    # Chat IDs (negative values are valid for group chats)
    MAIN_CHAT_ID: Final[int] = -1001
    LEADERSHIP_CHAT_ID: Final[int] = -1002
    
    # Limits
    MAX_MESSAGE_LENGTH: Final[int] = 4096
    MAX_USERS_PER_RESPONSE: Final[int] = 100
    MAX_CHATS_PER_RESPONSE: Final[int] = 50
    
    # Validation patterns
    INVITE_LINK_PATTERN: Final[str] = r'http://localhost:8001/\?[^\s]+'
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get base URL for Mock Telegram service."""
        return get_mock_telegram_url()
    
    @classmethod
    def get_port(cls) -> int:
        """Get port for Mock Telegram service."""
        return get_mock_telegram_port()
    
    @classmethod
    def get_api_url(cls) -> str:
        """Get API URL for Mock Telegram service."""
        return f"{cls.get_base_url()}{cls.API_BASE_PATH}"
    
    @classmethod
    def get_websocket_url(cls) -> str:
        """Get WebSocket URL for Mock Telegram service."""
        base_url = cls.get_base_url().replace('http://', 'ws://')
        return f"{base_url}{cls.WEBSOCKET_PATH}"


def validate_mock_telegram_config() -> None:
    """
    Validate Mock Telegram configuration (fail-fast).
    
    Raises:
        ValueError: If configuration is invalid.
    """
    port = MockTelegramConstants.get_port()
    if not (1 <= port <= 65535):
        raise ValueError(f"Invalid Mock Telegram port: {port}")
    
    if not MockTelegramConstants.DEFAULT_HOST:
        raise ValueError("Mock Telegram host cannot be empty")
    
    if MockTelegramConstants.MAX_MESSAGE_LENGTH <= 0:
        raise ValueError("MAX_MESSAGE_LENGTH must be positive")


# Validate configuration on import (fail-fast principle)
validate_mock_telegram_config()


# Export commonly used values for convenience
MOCK_TELEGRAM_URL = MockTelegramConstants.get_base_url()
MOCK_TELEGRAM_API_URL = MockTelegramConstants.get_api_url()
MOCK_TELEGRAM_WS_URL = MockTelegramConstants.get_websocket_url()
MOCK_TELEGRAM_PORT = MockTelegramConstants.get_port()