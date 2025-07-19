"""
Clean Configuration System for KICKAI using Pydantic Settings

This module provides a simple, type-safe configuration system that replaces
the complex improved_config_system.py and all scattered configuration access.
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

from core.enums import AIProvider


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """Main application settings using Pydantic Settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    
    # Database Configuration
    firebase_project_id: str = Field(
        default="",
        description="Firebase project ID"
    )
    firebase_credentials_path: Optional[str] = Field(
        default=None,
        description="Path to Firebase credentials file"
    )
    firebase_credentials_json: Optional[str] = Field(
        default=None,
        description="Firebase credentials as JSON string"
    )
    firebase_batch_size: int = Field(
        default=500,
        description="Firebase batch size for operations"
    )
    firebase_timeout: int = Field(
        default=30,
        description="Firebase timeout in seconds"
    )
    
    # AI Configuration
    ai_provider: AIProvider = Field(
        default=AIProvider.GEMINI,
        description="AI provider to use"
    )
    google_api_key: str = Field(
        default="",
        description="Google API key for Gemini"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    ai_model_name: str = Field(
        default="gemini-1.5-flash",
        description="AI model name"
    )
    ai_temperature: float = Field(
        default=0.7,
        description="AI temperature setting"
    )
    ai_max_tokens: int = Field(
        default=1000,
        description="AI max tokens"
    )
    ai_timeout: int = Field(
        default=120,
        description="AI timeout in seconds"
    )
    ai_max_retries: int = Field(
        default=5,
        description="AI max retries"
    )
    
    # Telegram Configuration
    telegram_bot_token: str = Field(
        default="",
        description="Telegram bot token"
    )
    telegram_bot_username: Optional[str] = Field(
        default=None,
        description="Telegram bot username"
    )
    telegram_main_chat_id: str = Field(
        default="",
        description="Main chat ID"
    )
    telegram_leadership_chat_id: str = Field(
        default="",
        description="Leadership chat ID"
    )
    telegram_webhook_url: Optional[str] = Field(
        default=None,
        description="Telegram webhook URL"
    )
    telegram_parse_mode: str = Field(
        default="MarkdownV2",
        description="Telegram parse mode"
    )
    telegram_timeout: int = Field(
        default=30,
        description="Telegram timeout in seconds"
    )
    
    # Team Configuration
    default_team_id: str = Field(
        default="KAI",
        description="Default team ID"
    )
    
    # Payment Configuration
    collectiv_api_key: str = Field(
        default="",
        description="Collectiv API key"
    )
    collectiv_base_url: str = Field(
        default="https://api.collectiv.com",
        description="Collectiv base URL"
    )
    payment_enabled: bool = Field(
        default=False,
        description="Enable payment system"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    log_file_path: Optional[str] = Field(
        default=None,
        description="Log file path"
    )
    log_max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Max log file size"
    )
    log_backup_count: int = Field(
        default=5,
        description="Number of log backups"
    )
    
    # Performance Configuration
    cache_ttl_seconds: int = Field(
        default=300,
        description="Cache TTL in seconds"
    )
    max_concurrent_requests: int = Field(
        default=10,
        description="Max concurrent requests"
    )
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts"
    )
    retry_delay: float = Field(
        default=1.0,
        description="Retry delay in seconds"
    )
    
    # Security Configuration
    jwt_secret: str = Field(
        default="default-secret-change-in-production",
        description="JWT secret key"
    )
    session_timeout: int = Field(
        default=3600,
        description="Session timeout in seconds"
    )
    max_login_attempts: int = Field(
        default=5,
        description="Max login attempts"
    )
    password_min_length: int = Field(
        default=8,
        description="Minimum password length"
    )
    
    # Advanced Memory Configuration
    enable_advanced_memory: bool = Field(
        default=True,
        description="Enable advanced memory system"
    )
    memory_max_short_term: int = Field(
        default=100,
        description="Max short-term memory items"
    )
    memory_max_long_term: int = Field(
        default=1000,
        description="Max long-term memory items"
    )
    memory_max_episodic: int = Field(
        default=500,
        description="Max episodic memory items"
    )
    memory_max_semantic: int = Field(
        default=200,
        description="Max semantic memory items"
    )
    memory_pattern_learning: bool = Field(
        default=True,
        description="Enable pattern learning"
    )
    memory_preference_learning: bool = Field(
        default=True,
        description="Enable preference learning"
    )
    memory_cleanup_interval: int = Field(
        default=24,
        description="Memory cleanup interval in hours"
    )
    
    # Development Configuration
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    verbose_logging: bool = Field(
        default=False,
        description="Enable verbose logging"
    )
    
    # Test Configuration
    test_mode: bool = Field(
        default=False,
        description="Enable test mode"
    )
    admin_session_string: Optional[str] = Field(
        default=None,
        description="Admin session string for testing"
    )
    player_session_string: Optional[str] = Field(
        default=None,
        description="Player session string for testing"
    )
    
    @validator("environment", pre=True)
    def detect_environment(cls, v):
        """Auto-detect environment if not specified."""
        if v is not None:
            return v
        
        # Check for test environment
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("E2E_TESTING"):
            return Environment.TESTING
        
        # Check for production environment
        if os.getenv("RAILWAY_ENVIRONMENT"):
            railway_service = os.getenv("RAILWAY_SERVICE_NAME", "").lower()
            if "production" in railway_service or "prod" in railway_service:
                return Environment.PRODUCTION
            elif "testing" in railway_service or "test" in railway_service:
                return Environment.TESTING
        
        return Environment.DEVELOPMENT
    
    @validator("ai_provider", pre=True)
    def validate_ai_provider(cls, v):
        """Validate AI provider."""
        if isinstance(v, str):
            try:
                return AIProvider(v.lower())
            except ValueError:
                return AIProvider.GEMINI
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING
    
    @property
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug or self.is_development
    
    def get_ai_api_key(self) -> str:
        """Get the appropriate API key for the AI provider."""
        if self.ai_provider == AIProvider.GEMINI:
            return self.google_api_key
        elif self.ai_provider == AIProvider.OLLAMA:
            # Ollama doesn't use API keys
            return ""
        return ""
    
    def validate_required_fields(self) -> List[str]:
        """Validate required fields and return list of errors."""
        errors = []
        
        # Required for all environments
        if not self.firebase_project_id:
            errors.append("FIREBASE_PROJECT_ID is required")
        
        # AI provider specific requirements
        if self.ai_provider == AIProvider.GEMINI and not self.google_api_key:
            errors.append("GOOGLE_API_KEY is required for Gemini")
        elif self.ai_provider == AIProvider.OLLAMA:
            # Ollama doesn't require an API key
            pass
        
        # Production requirements
        if self.is_production:
            if self.jwt_secret == "default-secret-change-in-production":
                errors.append("JWT_SECRET must be changed in production")
        
        return errors


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def initialize_settings(env_file: Optional[str] = None) -> Settings:
    """Initialize settings with optional custom env file."""
    global _settings
    
    if env_file and Path(env_file).exists():
        # Load custom env file
        _settings = Settings(_env_file=env_file)
    else:
        # Use default settings
        _settings = Settings()
    
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings


# Convenience functions for backward compatibility
def get_config() -> Settings:
    """Alias for get_settings() for backward compatibility."""
    return get_settings()


def get_bot_config() -> Settings:
    """Alias for get_settings() for backward compatibility."""
    return get_settings() 