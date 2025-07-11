"""
Configuration Adapter for Backward Compatibility

This module provides backward compatibility during the migration from the old
complex configuration system to the new clean Pydantic Settings system.

It allows existing code to continue working while gradually migrating to the new system.
"""

import logging
from typing import Optional, Dict, Any
from warnings import warn

from .settings import get_settings, Settings
from .enums import AIProvider

logger = logging.getLogger(__name__)


class ConfigurationAdapter:
    """
    Adapter class that provides the old configuration interface
    while using the new Pydantic Settings under the hood.
    """
    
    def __init__(self):
        self._settings = get_settings()
        warn(
            "ConfigurationAdapter is deprecated. Use get_settings() from core.settings instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    @property
    def configuration(self):
        """Return a configuration object that mimics the old structure."""
        return ConfigurationObject(self._settings)
    
    @property
    def environment(self):
        """Get the current environment."""
        return self._settings.environment
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self._settings.is_development
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self._settings.is_production
    
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self._settings.is_testing
    
    def get_team_config(self, team_id: str):
        """Get team configuration (simplified for backward compatibility)."""
        # For now, return a simple team config object
        return TeamConfigObject(self._settings, team_id)
    
    def get_default_team_config(self):
        """Get default team configuration."""
        return self.get_team_config(self._settings.default_team_id)
    
    def get_all_team_configs(self):
        """Get all team configurations (simplified)."""
        return {self._settings.default_team_id: self.get_default_team_config()}


class ConfigurationObject:
    """
    Object that mimics the old configuration structure
    while using the new settings under the hood.
    """
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def environment(self):
        """Get environment configuration."""
        return EnvironmentObject(self._settings)
    
    @property
    def database(self):
        """Get database configuration."""
        return DatabaseObject(self._settings)
    
    @property
    def ai(self):
        """Get AI configuration."""
        return AIObject(self._settings)
    
    @property
    def telegram(self):
        """Get Telegram configuration."""
        return TelegramObject(self._settings)
    
    @property
    def teams(self):
        """Get teams configuration."""
        return TeamsObject(self._settings)
    
    @property
    def payment(self):
        """Get payment configuration."""
        return PaymentObject(self._settings)
    
    @property
    def llm(self):
        """Get LLM configuration."""
        return LLMObject(self._settings)
    
    @property
    def advanced_memory(self):
        """Get advanced memory configuration."""
        return AdvancedMemoryObject(self._settings)
    
    @property
    def logging(self):
        """Get logging configuration."""
        return LoggingObject(self._settings)
    
    @property
    def performance(self):
        """Get performance configuration."""
        return PerformanceObject(self._settings)
    
    @property
    def security(self):
        """Get security configuration."""
        return SecurityObject(self._settings)


class EnvironmentObject:
    """Environment configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def mode(self):
        """Get environment mode."""
        return self._settings.environment.value


class DatabaseObject:
    """Database configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def project_id(self):
        """Get Firebase project ID."""
        return self._settings.firebase_project_id
    
    @property
    def credentials_path(self):
        """Get Firebase credentials path."""
        return self._settings.firebase_credentials_path
    
    @property
    def batch_size(self):
        """Get Firebase batch size."""
        return self._settings.firebase_batch_size
    
    @property
    def timeout_seconds(self):
        """Get Firebase timeout."""
        return self._settings.firebase_timeout


class AIObject:
    """AI configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def provider(self):
        """Get AI provider."""
        return self._settings.ai_provider
    
    @property
    def api_key(self):
        """Get AI API key."""
        return self._settings.get_ai_api_key()
    
    @property
    def model_name(self):
        """Get AI model name."""
        return self._settings.ai_model_name
    
    @property
    def temperature(self):
        """Get AI temperature."""
        return self._settings.ai_temperature
    
    @property
    def max_tokens(self):
        """Get AI max tokens."""
        return self._settings.ai_max_tokens
    
    @property
    def timeout_seconds(self):
        """Get AI timeout."""
        return self._settings.ai_timeout
    
    @property
    def max_retries(self):
        """Get AI max retries."""
        return self._settings.ai_max_retries


class TelegramObject:
    """Telegram configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def bot_token(self):
        """Get bot token."""
        return self._settings.telegram_bot_token
    
    @property
    def webhook_url(self):
        """Get webhook URL."""
        return self._settings.telegram_webhook_url
    
    @property
    def parse_mode(self):
        """Get parse mode."""
        return self._settings.telegram_parse_mode
    
    @property
    def message_timeout(self):
        """Get message timeout."""
        return self._settings.telegram_timeout


class TeamsObject:
    """Teams configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def default_team_id(self):
        """Get default team ID."""
        return self._settings.default_team_id
    
    @property
    def teams(self):
        """Get teams dictionary."""
        return {
            self._settings.default_team_id: TeamConfigObject(self._settings, self._settings.default_team_id)
        }


class TeamConfigObject:
    """Team configuration object."""
    
    def __init__(self, settings: Settings, team_id: str):
        self._settings = settings
        self.team_id = team_id
    
    @property
    def team_name(self):
        """Get team name."""
        return self.team_id
    
    @property
    def bot_token(self):
        """Get bot token."""
        return self._settings.telegram_bot_token
    
    @property
    def bot_username(self):
        """Get bot username."""
        return self._settings.telegram_bot_username
    
    @property
    def main_chat_id(self):
        """Get main chat ID."""
        return self._settings.telegram_main_chat_id
    
    @property
    def leadership_chat_id(self):
        """Get leadership chat ID."""
        return self._settings.telegram_leadership_chat_id
    
    @property
    def is_active(self):
        """Check if team is active."""
        return True


class PaymentObject:
    """Payment configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def collectiv_api_key(self):
        """Get Collectiv API key."""
        return self._settings.collectiv_api_key
    
    @property
    def collectiv_base_url(self):
        """Get Collectiv base URL."""
        return self._settings.collectiv_base_url


class LLMObject:
    """LLM configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def provider(self):
        """Get LLM provider."""
        return self._settings.ai_provider
    
    @property
    def model(self):
        """Get LLM model."""
        return self._settings.ai_model_name
    
    @property
    def api_key(self):
        """Get LLM API key."""
        return self._settings.get_ai_api_key()


class AdvancedMemoryObject:
    """Advanced memory configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def enabled(self):
        """Check if advanced memory is enabled."""
        return self._settings.enable_advanced_memory
    
    @property
    def max_short_term_items(self):
        """Get max short-term items."""
        return self._settings.memory_max_short_term
    
    @property
    def max_long_term_items(self):
        """Get max long-term items."""
        return self._settings.memory_max_long_term
    
    @property
    def max_episodic_items(self):
        """Get max episodic items."""
        return self._settings.memory_max_episodic
    
    @property
    def max_semantic_items(self):
        """Get max semantic items."""
        return self._settings.memory_max_semantic
    
    @property
    def pattern_learning_enabled(self):
        """Check if pattern learning is enabled."""
        return self._settings.memory_pattern_learning
    
    @property
    def preference_learning_enabled(self):
        """Check if preference learning is enabled."""
        return self._settings.memory_preference_learning
    
    @property
    def cleanup_interval_hours(self):
        """Get cleanup interval."""
        return self._settings.memory_cleanup_interval


class LoggingObject:
    """Logging configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def level(self):
        """Get log level."""
        return self._settings.log_level
    
    @property
    def format(self):
        """Get log format."""
        return self._settings.log_format
    
    @property
    def file_path(self):
        """Get log file path."""
        return self._settings.log_file_path
    
    @property
    def max_file_size(self):
        """Get max file size."""
        return self._settings.log_max_file_size
    
    @property
    def backup_count(self):
        """Get backup count."""
        return self._settings.log_backup_count


class PerformanceObject:
    """Performance configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def cache_ttl_seconds(self):
        """Get cache TTL."""
        return self._settings.cache_ttl_seconds
    
    @property
    def max_concurrent_requests(self):
        """Get max concurrent requests."""
        return self._settings.max_concurrent_requests
    
    @property
    def request_timeout(self):
        """Get request timeout."""
        return self._settings.request_timeout
    
    @property
    def retry_attempts(self):
        """Get retry attempts."""
        return self._settings.retry_attempts
    
    @property
    def retry_delay(self):
        """Get retry delay."""
        return self._settings.retry_delay


class SecurityObject:
    """Security configuration object."""
    
    def __init__(self, settings: Settings):
        self._settings = settings
    
    @property
    def jwt_secret(self):
        """Get JWT secret."""
        return self._settings.jwt_secret
    
    @property
    def session_timeout(self):
        """Get session timeout."""
        return self._settings.session_timeout
    
    @property
    def max_login_attempts(self):
        """Get max login attempts."""
        return self._settings.max_login_attempts
    
    @property
    def password_min_length(self):
        """Get password min length."""
        return self._settings.password_min_length


# Backward compatibility functions
def get_improved_config():
    """Backward compatibility function for get_improved_config()."""
    warn(
        "get_improved_config() is deprecated. Use get_settings() from core.settings instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return ConfigurationAdapter()


def initialize_improved_config(config_path: Optional[str] = None):
    """Backward compatibility function for initialize_improved_config()."""
    warn(
        "initialize_improved_config() is deprecated. Use initialize_settings() from core.settings instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from .settings import initialize_settings
    return ConfigurationAdapter()


# Bot config manager compatibility
class BotConfigManager:
    """Backward compatibility for BotConfigManager."""
    
    def __init__(self):
        self._settings = get_settings()
        warn(
            "BotConfigManager is deprecated. Use get_settings() from core.settings instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    def get_bot_token(self) -> str:
        """Get bot token."""
        return self._settings.telegram_bot_token
    
    def get_team_id(self) -> str:
        """Get team ID."""
        return self._settings.default_team_id
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "project_id": self._settings.firebase_project_id,
            "credentials_path": self._settings.firebase_credentials_path,
            "batch_size": self._settings.firebase_batch_size,
            "timeout_seconds": self._settings.firebase_timeout
        }
    
    def get_payment_config(self) -> Dict[str, Any]:
        """Get payment configuration."""
        return {
            "collectiv_api_key": self._settings.collectiv_api_key,
            "collectiv_base_url": self._settings.collectiv_base_url
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return {
            "provider": self._settings.ai_provider,
            "model": self._settings.ai_model_name,
            "api_key": self._settings.get_ai_api_key()
        }
    
    def is_development_mode(self) -> bool:
        """Check if in development mode."""
        return self._settings.is_development
    
    def get_log_level(self) -> str:
        """Get log level."""
        return self._settings.log_level


def get_bot_config_manager():
    """Backward compatibility function for get_bot_config_manager()."""
    warn(
        "get_bot_config_manager() is deprecated. Use get_settings() from core.settings instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return BotConfigManager() 