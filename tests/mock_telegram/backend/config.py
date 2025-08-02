"""
Configuration for Mock Telegram Testing System

This module provides centralized configuration management for the mock Telegram
testing system, including environment variable support and validation.
"""

import os
from typing import Optional
from dataclasses import dataclass
from pydantic import Field
from pydantic_settings import BaseSettings


@dataclass
class MockTelegramConfig:
    """Configuration for the mock Telegram testing system"""
    
    # Service configuration
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    
    # Limits and constraints
    max_messages: int = 1000
    max_users: int = 100
    max_message_length: int = 4096
    max_username_length: int = 32
    max_name_length: int = 64
    
    # Bot integration
    enable_bot_integration: bool = True
    bot_timeout_seconds: float = 5.0
    bot_max_retries: int = 3
    
    # WebSocket configuration
    websocket_timeout: float = 30.0
    websocket_max_connections: int = 100
    
    # CORS configuration
    cors_origins: list = None
    cors_allow_credentials: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """Set default values for CORS origins"""
        if self.cors_origins is None:
            self.cors_origins = ["*"]


class MockTelegramSettings(BaseSettings):
    """Pydantic settings for environment variable configuration"""
    
    # Service configuration
    MOCK_TELEGRAM_HOST: str = Field(default="0.0.0.0", env="MOCK_TELEGRAM_HOST")
    MOCK_TELEGRAM_PORT: int = Field(default=8001, env="MOCK_TELEGRAM_PORT")
    MOCK_TELEGRAM_DEBUG: bool = Field(default=False, env="MOCK_TELEGRAM_DEBUG")
    
    # Limits and constraints
    MOCK_TELEGRAM_MAX_MESSAGES: int = Field(default=1000, env="MOCK_TELEGRAM_MAX_MESSAGES")
    MOCK_TELEGRAM_MAX_USERS: int = Field(default=100, env="MOCK_TELEGRAM_MAX_USERS")
    MOCK_TELEGRAM_MAX_MESSAGE_LENGTH: int = Field(default=4096, env="MOCK_TELEGRAM_MAX_MESSAGE_LENGTH")
    MOCK_TELEGRAM_MAX_USERNAME_LENGTH: int = Field(default=32, env="MOCK_TELEGRAM_MAX_USERNAME_LENGTH")
    MOCK_TELEGRAM_MAX_NAME_LENGTH: int = Field(default=64, env="MOCK_TELEGRAM_MAX_NAME_LENGTH")
    
    # Bot integration
    MOCK_TELEGRAM_ENABLE_BOT_INTEGRATION: bool = Field(default=True, env="MOCK_TELEGRAM_ENABLE_BOT_INTEGRATION")
    MOCK_TELEGRAM_BOT_TIMEOUT: float = Field(default=5.0, env="MOCK_TELEGRAM_BOT_TIMEOUT")
    MOCK_TELEGRAM_BOT_MAX_RETRIES: int = Field(default=3, env="MOCK_TELEGRAM_BOT_MAX_RETRIES")
    
    # WebSocket configuration
    MOCK_TELEGRAM_WS_TIMEOUT: float = Field(default=30.0, env="MOCK_TELEGRAM_WS_TIMEOUT")
    MOCK_TELEGRAM_WS_MAX_CONNECTIONS: int = Field(default=100, env="MOCK_TELEGRAM_WS_MAX_CONNECTIONS")
    
    # CORS configuration
    MOCK_TELEGRAM_CORS_ORIGINS: str = Field(default="*", env="MOCK_TELEGRAM_CORS_ORIGINS")
    MOCK_TELEGRAM_CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="MOCK_TELEGRAM_CORS_ALLOW_CREDENTIALS")
    
    # Logging
    MOCK_TELEGRAM_LOG_LEVEL: str = Field(default="INFO", env="MOCK_TELEGRAM_LOG_LEVEL")
    MOCK_TELEGRAM_LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="MOCK_TELEGRAM_LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment
    
    def to_config(self) -> MockTelegramConfig:
        """Convert settings to MockTelegramConfig"""
        return MockTelegramConfig(
            host=self.MOCK_TELEGRAM_HOST,
            port=self.MOCK_TELEGRAM_PORT,
            debug=self.MOCK_TELEGRAM_DEBUG,
            max_messages=self.MOCK_TELEGRAM_MAX_MESSAGES,
            max_users=self.MOCK_TELEGRAM_MAX_USERS,
            max_message_length=self.MOCK_TELEGRAM_MAX_MESSAGE_LENGTH,
            max_username_length=self.MOCK_TELEGRAM_MAX_USERNAME_LENGTH,
            max_name_length=self.MOCK_TELEGRAM_MAX_NAME_LENGTH,
            enable_bot_integration=self.MOCK_TELEGRAM_ENABLE_BOT_INTEGRATION,
            bot_timeout_seconds=self.MOCK_TELEGRAM_BOT_TIMEOUT,
            bot_max_retries=self.MOCK_TELEGRAM_BOT_MAX_RETRIES,
            websocket_timeout=self.MOCK_TELEGRAM_WS_TIMEOUT,
            websocket_max_connections=self.MOCK_TELEGRAM_WS_MAX_CONNECTIONS,
            cors_origins=self.MOCK_TELEGRAM_CORS_ORIGINS.split(",") if self.MOCK_TELEGRAM_CORS_ORIGINS != "*" else ["*"],
            cors_allow_credentials=self.MOCK_TELEGRAM_CORS_ALLOW_CREDENTIALS,
            log_level=self.MOCK_TELEGRAM_LOG_LEVEL,
            log_format=self.MOCK_TELEGRAM_LOG_FORMAT
        )


def get_config() -> MockTelegramConfig:
    """Get configuration from environment variables or defaults"""
    try:
        settings = MockTelegramSettings()
        return settings.to_config()
    except Exception as e:
        # Fallback to default configuration
        print(f"Warning: Could not load configuration from environment: {e}")
        return MockTelegramConfig()


def validate_config(config: MockTelegramConfig) -> bool:
    """Validate configuration values"""
    errors = []
    
    # Validate port
    if not (1024 <= config.port <= 65535):
        errors.append(f"Port must be between 1024 and 65535, got {config.port}")
    
    # Validate limits
    if config.max_messages <= 0:
        errors.append("max_messages must be positive")
    
    if config.max_users <= 0:
        errors.append("max_users must be positive")
    
    if config.max_message_length <= 0:
        errors.append("max_message_length must be positive")
    
    if config.max_username_length <= 0:
        errors.append("max_username_length must be positive")
    
    if config.max_name_length <= 0:
        errors.append("max_name_length must be positive")
    
    # Validate timeouts
    if config.bot_timeout_seconds <= 0:
        errors.append("bot_timeout_seconds must be positive")
    
    if config.websocket_timeout <= 0:
        errors.append("websocket_timeout must be positive")
    
    # Validate WebSocket limits
    if config.websocket_max_connections <= 0:
        errors.append("websocket_max_connections must be positive")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True


# Default configuration instance
DEFAULT_CONFIG = get_config()

# Validate default configuration
try:
    validate_config(DEFAULT_CONFIG)
except ValueError as e:
    print(f"Warning: Default configuration validation failed: {e}")
    # Use safe defaults
    DEFAULT_CONFIG = MockTelegramConfig() 