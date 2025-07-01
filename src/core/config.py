"""
Core Configuration Management for KICKAI

This module provides centralized configuration management with validation,
type safety, and environment-specific settings.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AIProvider(Enum):
    """AI provider types."""
    GOOGLE_GEMINI = "google_gemini"
    OPENAI = "openai"
    OLLAMA = "ollama"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    project_id: str
    credentials_path: Optional[str] = None
    collection_prefix: str = "kickai"
    batch_size: int = 500
    timeout_seconds: int = 30


@dataclass
class AIConfig:
    """AI configuration."""
    provider: AIProvider
    api_key: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout_seconds: int = 60


@dataclass
class TelegramConfig:
    """Telegram configuration."""
    bot_token: str
    webhook_url: Optional[str] = None
    parse_mode: str = "MarkdownV2"
    message_timeout: int = 30


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    cache_ttl_seconds: int = 300  # 5 minutes
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: str
    session_timeout: int = 3600  # 1 hour
    max_login_attempts: int = 5
    password_min_length: int = 8


class ConfigurationManager:
    """Centralized configuration management with validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = config_path
        self._environment = self._detect_environment()
        self._config: Dict[str, Any] = {}
        self._load_configuration()
        self._validate_configuration()
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment."""
        env = os.getenv("KICKAI_ENV", "development").lower()
        try:
            return Environment(env)
        except ValueError:
            logging.warning(f"Unknown environment '{env}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_configuration(self):
        """Load configuration from environment variables and files."""
        self._config = {
            "environment": self._environment,
            "database": self._load_database_config(),
            "ai": self._load_ai_config(),
            "telegram": self._load_telegram_config(),
            "logging": self._load_logging_config(),
            "performance": self._load_performance_config(),
            "security": self._load_security_config(),
        }
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration."""
        return DatabaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
            credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH"),
            collection_prefix=os.getenv("FIREBASE_COLLECTION_PREFIX", "kickai"),
            batch_size=int(os.getenv("FIREBASE_BATCH_SIZE", "500")),
            timeout_seconds=int(os.getenv("FIREBASE_TIMEOUT", "30"))
        )
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration."""
        provider_str = os.getenv("AI_PROVIDER", "google_gemini").lower()
        try:
            provider = AIProvider(provider_str)
        except ValueError:
            logging.warning(f"Unknown AI provider '{provider_str}', defaulting to google_gemini")
            provider = AIProvider.GOOGLE_GEMINI
        
        return AIConfig(
            provider=provider,
            api_key=os.getenv("AI_API_KEY", ""),
            model_name=os.getenv("AI_MODEL_NAME", "gemini-pro"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "1000")),
            timeout_seconds=int(os.getenv("AI_TIMEOUT", "60"))
        )
    
    def _load_telegram_config(self) -> TelegramConfig:
        """Load Telegram configuration."""
        return TelegramConfig(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            webhook_url=os.getenv("TELEGRAM_WEBHOOK_URL"),
            parse_mode=os.getenv("TELEGRAM_PARSE_MODE", "MarkdownV2"),
            message_timeout=int(os.getenv("TELEGRAM_TIMEOUT", "30"))
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration."""
        return LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=os.getenv("LOG_FILE_PATH"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration."""
        return PerformanceConfig(
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "1.0"))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration."""
        return SecurityConfig(
            jwt_secret=os.getenv("JWT_SECRET", "default-secret-change-in-production"),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600")),
            max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        )
    
    def _validate_configuration(self):
        """Validate the loaded configuration."""
        errors = []
        
        # Validate required fields
        if not self._config["database"].project_id:
            errors.append("FIREBASE_PROJECT_ID is required")
        
        if not self._config["ai"].api_key:
            errors.append("AI_API_KEY is required")
        
        if not self._config["telegram"].bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        # Validate ranges
        if not (0.0 <= self._config["ai"].temperature <= 2.0):
            errors.append("AI_TEMPERATURE must be between 0.0 and 2.0")
        
        if self._config["ai"].max_tokens <= 0:
            errors.append("AI_MAX_TOKENS must be positive")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    @property
    def environment(self) -> Environment:
        """Get the current environment."""
        return self._environment
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration."""
        return self._config["database"]
    
    @property
    def ai(self) -> AIConfig:
        """Get AI configuration."""
        return self._config["ai"]
    
    @property
    def telegram(self) -> TelegramConfig:
        """Get Telegram configuration."""
        return self._config["telegram"]
    
    @property
    def logging(self) -> LoggingConfig:
        """Get logging configuration."""
        return self._config["logging"]
    
    @property
    def performance(self) -> PerformanceConfig:
        """Get performance configuration."""
        return self._config["performance"]
    
    @property
    def security(self) -> SecurityConfig:
        """Get security configuration."""
        return self._config["security"]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key, default)
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self._environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self._environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self._environment == Environment.TESTING


class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_config() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def initialize_config(config_path: Optional[str] = None) -> ConfigurationManager:
    """Initialize the global configuration manager."""
    global _config_manager
    _config_manager = ConfigurationManager(config_path)
    return _config_manager 