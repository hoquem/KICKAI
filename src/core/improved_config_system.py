#!/usr/bin/env python3
"""
Improved Configuration System for KICKAI

This module implements a clean, maintainable configuration architecture using:
- Strategy Pattern: Different configuration sources (env, file, database)
- Factory Pattern: Configuration object creation
- Builder Pattern: Complex configuration building
- Observer Pattern: Configuration change notifications
- Chain of Responsibility: Configuration validation
- Singleton Pattern: Global configuration instance

This replaces the monolithic ConfigurationManager with a modular, extensible system.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Set

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AIProvider(Enum):
    """AI provider types."""
    GOOGLE_GEMINI = "google_gemini"
    OLLAMA = "ollama"
    OPENAI = "openai"


class ConfigSource(Enum):
    """Configuration source types."""
    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    DEFAULT = "default"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    project_id: str
    credentials_path: Optional[str] = None
    batch_size: int = 500
    timeout_seconds: int = 30
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class AIConfig:
    """AI configuration."""
    provider: AIProvider
    api_key: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout_seconds: int = 60
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class TelegramConfig:
    """Telegram configuration."""
    bot_token: str
    webhook_url: Optional[str] = None
    parse_mode: str = "MarkdownV2"
    message_timeout: int = 30
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class TeamConfig:
    """Team configuration."""
    default_team_id: str = ""
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class PaymentConfig:
    """Payment configuration."""
    collectiv_api_key: str = ""
    collectiv_base_url: str = "https://api.collectiv.com"
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: AIProvider
    model: str
    api_key: str
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class AdvancedMemoryConfig:
    """Advanced memory configuration."""
    enabled: bool = True
    max_short_term_items: int = 100
    max_long_term_items: int = 1000
    max_episodic_items: int = 500
    max_semantic_items: int = 200
    pattern_learning_enabled: bool = True
    preference_learning_enabled: bool = True
    cleanup_interval_hours: int = 24
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    cache_ttl_seconds: int = 300  # 5 minutes
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: str
    session_timeout: int = 3600
    max_login_attempts: int = 5
    password_min_length: int = 8
    source: ConfigSource = ConfigSource.DEFAULT


@dataclass
class Configuration:
    """Complete configuration object."""
    environment: Environment
    database: DatabaseConfig
    ai: AIConfig
    telegram: TelegramConfig
    team: TeamConfig
    payment: PaymentConfig
    llm: LLMConfig
    advanced_memory: AdvancedMemoryConfig
    logging: LoggingConfig
    performance: PerformanceConfig
    security: SecurityConfig
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# STRATEGY PATTERN: CONFIGURATION SOURCES
# ============================================================================

class ConfigurationSource(ABC):
    """Abstract base class for configuration sources (Strategy Pattern)."""
    
    @abstractmethod
    def load_configuration(self, environment: Environment) -> Dict[str, Any]:
        """Load configuration from this source."""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Get priority of this source (higher = more important)."""
        pass
    
    @abstractmethod
    def is_available(self, environment: Environment) -> bool:
        """Check if this source is available for the given environment."""
        pass


class EnvironmentConfigurationSource(ConfigurationSource):
    """Load configuration from environment variables."""
    
    def load_configuration(self, environment: Environment) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        print("🔍 DEBUG: EnvironmentConfigurationSource.load_configuration called")
        logger.info("🔍 EnvironmentConfigurationSource.load_configuration called")
        
        # Ensure environment variables are loaded
        if DOTENV_AVAILABLE:
            load_dotenv()
        
        config = {}
        
        # Database config
        config["database"] = {
            "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
            "credentials_path": os.getenv("FIREBASE_CREDENTIALS_PATH"),
            "batch_size": int(os.getenv("FIREBASE_BATCH_SIZE", "500")),
            "timeout_seconds": int(os.getenv("FIREBASE_TIMEOUT", "30")),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # AI config
        provider_str = os.getenv("AI_PROVIDER", "google_gemini").lower()
        print(f"🔍 DEBUG: AI_PROVIDER from env: {repr(provider_str)}")
        try:
            provider = AIProvider(provider_str)
            print(f"🔍 DEBUG: Provider enum: {provider}")
        except ValueError:
            provider = AIProvider.GOOGLE_GEMINI
            print(f"🔍 DEBUG: Using default provider: {provider}")
        
        api_key = ""
        if provider == AIProvider.GOOGLE_GEMINI:
            raw_key = os.getenv("GOOGLE_API_KEY", "")
            print(f"🔍 DEBUG: Raw GOOGLE_API_KEY from os.getenv: {repr(raw_key)}")
            api_key = raw_key
            print(f"🔍 DEBUG: GOOGLE_API_KEY loaded: {api_key[:10] if api_key else 'NOT_FOUND'}...")
            logger.info(f"🔍 Loading GOOGLE_API_KEY: {api_key[:10] if api_key else 'NOT_FOUND'}...")
        elif provider == AIProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY", "")
        elif provider == AIProvider.OLLAMA:
            api_key = "ollama_local"
        else:
            api_key = os.getenv("AI_API_KEY", "")
        
        default_model = "gemini-2.0-flash-001"
        if provider == AIProvider.OLLAMA:
            default_model = "llama3.1:8b-instruct-q4_0"
        elif provider == AIProvider.OPENAI:
            default_model = "gpt-4"
        
        config["ai"] = {
            "provider": provider,
            "api_key": api_key,
            "model_name": os.getenv("AI_MODEL_NAME", default_model),
            "temperature": float(os.getenv("AI_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("AI_MAX_TOKENS", "1000")),
            "timeout_seconds": int(os.getenv("AI_TIMEOUT", "60")),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # Telegram config
        config["telegram"] = {
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "webhook_url": os.getenv("TELEGRAM_WEBHOOK_URL"),
            "parse_mode": os.getenv("TELEGRAM_PARSE_MODE", "MarkdownV2"),
            "message_timeout": int(os.getenv("TELEGRAM_TIMEOUT", "30")),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # Logging config
        config["logging"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            "file_path": os.getenv("LOG_FILE_PATH"),
            "max_file_size": int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5")),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # Team config
        config["team"] = {
            "default_team_id": os.getenv("DEFAULT_TEAM_ID", ""),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # Payment config
        config["payment"] = {
            "collectiv_api_key": os.getenv("COLLECTIV_API_KEY", ""),
            "collectiv_base_url": os.getenv("COLLECTIV_BASE_URL", "https://api.collectiv.com"),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # LLM config
        config["llm"] = {
            "provider": os.getenv("LLM_PROVIDER", "google_gemini"),
            "model": os.getenv("LLM_MODEL", "gemini-2.0-flash-001"),
            "api_key": os.getenv("LLM_API_KEY", ""),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # Advanced memory config
        config["advanced_memory"] = {
            "enabled": os.getenv("ENABLE_ADVANCED_MEMORY", "true").lower() == "true",
            "max_short_term_items": int(os.getenv("MEMORY_MAX_SHORT_TERM", "100")),
            "max_long_term_items": int(os.getenv("MEMORY_MAX_LONG_TERM", "1000")),
            "max_episodic_items": int(os.getenv("MEMORY_MAX_EPISODIC", "500")),
            "max_semantic_items": int(os.getenv("MEMORY_MAX_SEMANTIC", "200")),
            "pattern_learning_enabled": os.getenv("MEMORY_PATTERN_LEARNING", "true").lower() == "true",
            "preference_learning_enabled": os.getenv("MEMORY_PREFERENCE_LEARNING", "true").lower() == "true",
            "cleanup_interval_hours": int(os.getenv("MEMORY_CLEANUP_INTERVAL", "24")),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # Performance config
        config["performance"] = {
            "cache_ttl_seconds": int(os.getenv("CACHE_TTL_SECONDS", "300")),
            "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
            "request_timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
            "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
            "retry_delay": float(os.getenv("RETRY_DELAY", "1.0")),
            "source": ConfigSource.ENVIRONMENT
        }
        
        # Security config
        config["security"] = {
            "jwt_secret": os.getenv("JWT_SECRET", "default-secret-change-in-production"),
            "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),
            "max_login_attempts": int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
            "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            "source": ConfigSource.ENVIRONMENT
        }
        
        return config
    
    def get_priority(self) -> int:
        """Environment variables have highest priority."""
        return 100
    
    def is_available(self, environment: Environment) -> bool:
        """Environment variables are always available."""
        return True


class FileConfigurationSource(ConfigurationSource):
    """Load configuration from files."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config"
    
    def load_configuration(self, environment: Environment) -> Dict[str, Any]:
        """Load configuration from files."""
        config = {}
        
        # Try to load from config files
        config_files = [
            f"{self.config_path}/config.json",
            f"{self.config_path}/config.{environment.value}.json",
            "config.json",
            f"config.{environment.value}.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        config.update(file_config)
                        logger.info(f"Loaded configuration from {config_file}")
                except Exception as e:
                    logger.warning(f"Failed to load {config_file}: {e}")
        
        return config
    
    def get_priority(self) -> int:
        """File configuration has medium priority."""
        return 50
    
    def is_available(self, environment: Environment) -> bool:
        """Check if any config files exist."""
        config_files = [
            f"{self.config_path}/config.json",
            f"{self.config_path}/config.{environment.value}.json",
            "config.json",
            f"config.{environment.value}.json"
        ]
        return any(os.path.exists(f) for f in config_files)


class DatabaseConfigurationSource(ConfigurationSource):
    """Load configuration from database (for production)."""
    
    def load_configuration(self, environment: Environment) -> Dict[str, Any]:
        """Load configuration from database."""
        # This would integrate with the bot configuration manager
        # For now, return empty config
        return {}
    
    def get_priority(self) -> int:
        """Database configuration has low priority (fallback)."""
        return 25
    
    def is_available(self, environment: Environment) -> bool:
        """Database config is available in production."""
        return environment == Environment.PRODUCTION


class DefaultConfigurationSource(ConfigurationSource):
    """Load default configuration values."""
    
    def load_configuration(self, environment: Environment) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "database": {
                "project_id": "",
                "credentials_path": None,
                "batch_size": 500,
                "timeout_seconds": 30,
                "source": ConfigSource.DEFAULT
            },
            "ai": {
                "provider": AIProvider.GOOGLE_GEMINI,
                "api_key": "",
                "model_name": "gemini-2.0-flash-001",
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout_seconds": 60,
                "source": ConfigSource.DEFAULT
            },
            "telegram": {
                "bot_token": "",
                "webhook_url": None,
                "parse_mode": "MarkdownV2",
                "message_timeout": 30,
                "source": ConfigSource.DEFAULT
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_path": None,
                "max_file_size": 10 * 1024 * 1024,
                "backup_count": 5,
                "source": ConfigSource.DEFAULT
            },
            "performance": {
                "cache_ttl_seconds": 300,
                "max_concurrent_requests": 10,
                "request_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 1.0,
                "source": ConfigSource.DEFAULT
            },
            "security": {
                "jwt_secret": "default-secret-change-in-production",
                "session_timeout": 3600,
                "max_login_attempts": 5,
                "password_min_length": 8,
                "source": ConfigSource.DEFAULT
            }
        }
    
    def get_priority(self) -> int:
        """Default configuration has lowest priority."""
        return 0
    
    def is_available(self, environment: Environment) -> bool:
        """Default config is always available."""
        return True


# ============================================================================
# BUILDER PATTERN: CONFIGURATION BUILDER
# ============================================================================

class ConfigurationBuilder:
    """Builder for creating Configuration objects."""
    
    def __init__(self):
        self._environment: Optional[Environment] = None
        self._database: Optional[DatabaseConfig] = None
        self._ai: Optional[AIConfig] = None
        self._telegram: Optional[TelegramConfig] = None
        self._team: Optional[TeamConfig] = None
        self._payment: Optional[PaymentConfig] = None
        self._llm: Optional[LLMConfig] = None
        self._advanced_memory: Optional[AdvancedMemoryConfig] = None
        self._logging: Optional[LoggingConfig] = None
        self._performance: Optional[PerformanceConfig] = None
        self._security: Optional[SecurityConfig] = None
        self._metadata: Dict[str, Any] = {}
    
    def environment(self, env: Environment) -> 'ConfigurationBuilder':
        """Set environment."""
        self._environment = env
        return self
    
    def database(self, config: DatabaseConfig) -> 'ConfigurationBuilder':
        """Set database configuration."""
        self._database = config
        return self
    
    def ai(self, config: AIConfig) -> 'ConfigurationBuilder':
        """Set AI configuration."""
        self._ai = config
        return self
    
    def telegram(self, config: TelegramConfig) -> 'ConfigurationBuilder':
        """Set Telegram configuration."""
        self._telegram = config
        return self
    
    def team(self, config: TeamConfig) -> 'ConfigurationBuilder':
        """Set team configuration."""
        self._team = config
        return self
    
    def payment(self, config: PaymentConfig) -> 'ConfigurationBuilder':
        """Set payment configuration."""
        self._payment = config
        return self
    
    def llm(self, config: LLMConfig) -> 'ConfigurationBuilder':
        """Set LLM configuration."""
        self._llm = config
        return self
    
    def advanced_memory(self, config: AdvancedMemoryConfig) -> 'ConfigurationBuilder':
        """Set advanced memory configuration."""
        self._advanced_memory = config
        return self
    
    def logging(self, config: LoggingConfig) -> 'ConfigurationBuilder':
        """Set logging configuration."""
        self._logging = config
        return self
    
    def performance(self, config: PerformanceConfig) -> 'ConfigurationBuilder':
        """Set performance configuration."""
        self._performance = config
        return self
    
    def security(self, config: SecurityConfig) -> 'ConfigurationBuilder':
        """Set security configuration."""
        self._security = config
        return self
    
    def metadata(self, key: str, value: Any) -> 'ConfigurationBuilder':
        """Add metadata."""
        self._metadata[key] = value
        return self
    
    def build(self) -> Configuration:
        """Build the Configuration object."""
        if not self._environment:
            raise ValueError("Environment must be set")
        
        return Configuration(
            environment=self._environment,
            database=self._database or DatabaseConfig(project_id=""),
            ai=self._ai or AIConfig(provider=AIProvider.GOOGLE_GEMINI, api_key="", model_name=""),
            telegram=self._telegram or TelegramConfig(bot_token=""),
            team=self._team or TeamConfig(),
            payment=self._payment or PaymentConfig(),
            llm=self._llm or LLMConfig(provider=AIProvider.GOOGLE_GEMINI, model="", api_key=""),
            advanced_memory=self._advanced_memory or AdvancedMemoryConfig(),
            logging=self._logging or LoggingConfig(),
            performance=self._performance or PerformanceConfig(),
            security=self._security or SecurityConfig(jwt_secret=""),
            metadata=self._metadata
        )


# ============================================================================
# FACTORY PATTERN: CONFIGURATION FACTORY
# ============================================================================

class ConfigurationFactory:
    """Factory for creating configuration objects."""
    
    @staticmethod
    def create_database_config(data: Dict[str, Any]) -> DatabaseConfig:
        """Create DatabaseConfig from dictionary."""
        return DatabaseConfig(
            project_id=data.get("project_id", ""),
            credentials_path=data.get("credentials_path"),
            batch_size=data.get("batch_size", 500),
            timeout_seconds=data.get("timeout_seconds", 30),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_ai_config(data: Dict[str, Any]) -> AIConfig:
        """Create AIConfig from dictionary."""
        provider = data.get("provider", AIProvider.GOOGLE_GEMINI)
        if isinstance(provider, str):
            try:
                provider = AIProvider(provider)
            except ValueError:
                provider = AIProvider.GOOGLE_GEMINI
        
        return AIConfig(
            provider=provider,
            api_key=data.get("api_key", ""),
            model_name=data.get("model_name", "gemini-2.0-flash-001"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 1000),
            timeout_seconds=data.get("timeout_seconds", 60),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_telegram_config(data: Dict[str, Any]) -> TelegramConfig:
        """Create TelegramConfig from dictionary."""
        return TelegramConfig(
            bot_token=data.get("bot_token", ""),
            webhook_url=data.get("webhook_url"),
            parse_mode=data.get("parse_mode", "MarkdownV2"),
            message_timeout=data.get("message_timeout", 30),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_logging_config(data: Dict[str, Any]) -> LoggingConfig:
        """Create LoggingConfig from dictionary."""
        return LoggingConfig(
            level=data.get("level", "INFO"),
            format=data.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=data.get("file_path"),
            max_file_size=data.get("max_file_size", 10 * 1024 * 1024),
            backup_count=data.get("backup_count", 5),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_performance_config(data: Dict[str, Any]) -> PerformanceConfig:
        """Create PerformanceConfig from dictionary."""
        return PerformanceConfig(
            cache_ttl_seconds=data.get("cache_ttl_seconds", 300),
            max_concurrent_requests=data.get("max_concurrent_requests", 10),
            request_timeout=data.get("request_timeout", 30),
            retry_attempts=data.get("retry_attempts", 3),
            retry_delay=data.get("retry_delay", 1.0),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_security_config(data: Dict[str, Any]) -> SecurityConfig:
        """Create SecurityConfig from dictionary."""
        return SecurityConfig(
            jwt_secret=data.get("jwt_secret", "default-secret-change-in-production"),
            session_timeout=data.get("session_timeout", 3600),
            max_login_attempts=data.get("max_login_attempts", 5),
            password_min_length=data.get("password_min_length", 8),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_team_config(data: Dict[str, Any]) -> TeamConfig:
        """Create TeamConfig from dictionary."""
        return TeamConfig(
            default_team_id=data.get("default_team_id", ""),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_payment_config(data: Dict[str, Any]) -> PaymentConfig:
        """Create PaymentConfig from dictionary."""
        return PaymentConfig(
            collectiv_api_key=data.get("collectiv_api_key", ""),
            collectiv_base_url=data.get("collectiv_base_url", "https://api.collectiv.com"),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_llm_config(data: Dict[str, Any]) -> LLMConfig:
        """Create LLMConfig from dictionary."""
        provider = data.get("provider", AIProvider.GOOGLE_GEMINI)
        if isinstance(provider, str):
            try:
                provider = AIProvider(provider)
            except ValueError:
                provider = AIProvider.GOOGLE_GEMINI
        
        return LLMConfig(
            provider=provider,
            model=data.get("model", "gemini-2.0-flash-001"),
            api_key=data.get("api_key", ""),
            source=data.get("source", ConfigSource.DEFAULT)
        )
    
    @staticmethod
    def create_advanced_memory_config(data: Dict[str, Any]) -> AdvancedMemoryConfig:
        """Create AdvancedMemoryConfig from dictionary."""
        return AdvancedMemoryConfig(
            enabled=data.get("enabled", True),
            max_short_term_items=data.get("max_short_term_items", 100),
            max_long_term_items=data.get("max_long_term_items", 1000),
            max_episodic_items=data.get("max_episodic_items", 500),
            max_semantic_items=data.get("max_semantic_items", 200),
            pattern_learning_enabled=data.get("pattern_learning_enabled", True),
            preference_learning_enabled=data.get("preference_learning_enabled", True),
            cleanup_interval_hours=data.get("cleanup_interval_hours", 24),
            source=data.get("source", ConfigSource.DEFAULT)
        )


# ============================================================================
# CHAIN OF RESPONSIBILITY: CONFIGURATION VALIDATION
# ============================================================================

class ConfigurationValidator(ABC):
    """Abstract base class for configuration validators (Chain of Responsibility)."""
    
    def __init__(self, next_validator: Optional['ConfigurationValidator'] = None):
        self._next_validator = next_validator
    
    @abstractmethod
    def validate(self, config: Configuration) -> List[str]:
        """Validate configuration and return list of errors."""
        pass
    
    def _validate_next(self, config: Configuration, errors: List[str]) -> List[str]:
        """Pass validation to next validator in chain."""
        if self._next_validator:
            errors.extend(self._next_validator.validate(config))
        return errors


class EnvironmentValidator(ConfigurationValidator):
    """Validate environment-specific configuration."""
    
    def validate(self, config: Configuration) -> List[str]:
        """Validate environment-specific configuration."""
        errors = []
        
        # Skip validation in testing
        if config.environment == Environment.TESTING:
            return errors
        
        # Validate based on environment
        if config.environment == Environment.PRODUCTION:
            if not config.database.project_id:
                errors.append("Database project_id is required in production")
        
        return self._validate_next(config, errors)


class DatabaseValidator(ConfigurationValidator):
    """Validate database configuration."""
    
    def validate(self, config: Configuration) -> List[str]:
        """Validate database configuration."""
        errors = []
        
        # Check Firebase credentials
        firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        firebase_creds_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
        
        if not firebase_creds_json and not firebase_creds_file:
            errors.append("Either FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE is required")
        
        return self._validate_next(config, errors)


class AIValidator(ConfigurationValidator):
    """Validate AI configuration."""
    
    def validate(self, config: Configuration) -> List[str]:
        """Validate AI configuration."""
        errors = []
        
        if config.environment == Environment.DEVELOPMENT:
            if config.ai.provider == AIProvider.GOOGLE_GEMINI and not config.ai.api_key:
                errors.append("GOOGLE_API_KEY is required in development environment for Gemini")
            elif config.ai.provider == AIProvider.OPENAI and not config.ai.api_key:
                errors.append("OPENAI_API_KEY is required in development environment for OpenAI")
            elif config.ai.provider == AIProvider.OLLAMA:
                # OLLAMA doesn't require an API key
                pass
        
        return self._validate_next(config, errors)


# ============================================================================
# OBSERVER PATTERN: CONFIGURATION CHANGE NOTIFICATIONS
# ============================================================================

class ConfigurationObserver(ABC):
    """Abstract base class for configuration observers."""
    
    @abstractmethod
    def on_configuration_changed(self, config: Configuration):
        """Called when configuration changes."""
        pass


class ConfigurationChangeNotifier:
    """Notifies observers of configuration changes."""
    
    def __init__(self):
        self._observers: Set[ConfigurationObserver] = set()
    
    def add_observer(self, observer: ConfigurationObserver):
        """Add an observer."""
        self._observers.add(observer)
    
    def remove_observer(self, observer: ConfigurationObserver):
        """Remove an observer."""
        self._observers.discard(observer)
    
    def notify_observers(self, config: Configuration):
        """Notify all observers of configuration change."""
        for observer in self._observers:
            try:
                observer.on_configuration_changed(config)
            except Exception as e:
                logger.error(f"Error notifying observer {observer}: {e}")


# ============================================================================
# SINGLETON PATTERN: IMPROVED CONFIGURATION MANAGER
# ============================================================================

class ImprovedConfigurationManager:
    """Improved configuration manager using design patterns."""
    
    _instance: Optional['ImprovedConfigurationManager'] = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager."""
        if self._initialized:
            return
        
        self._config_path = config_path
        self._environment = self._detect_environment()
        self._load_env_files()
        self._configuration: Optional[Configuration] = None
        self._change_notifier = ConfigurationChangeNotifier()
        self._validators = self._setup_validators()
        self._sources = self._setup_sources()
        
        self._initialized = True
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment."""
        # Simplified environment detection (same as original)
        env = os.getenv("ENVIRONMENT", "").lower()
        if env:
            try:
                return Environment(env)
            except ValueError:
                pass
        
        if os.getenv("CI") or os.getenv("GITHUB_ACTIONS") or os.getenv("PYTEST_CURRENT_TEST"):
            return Environment.TESTING
        
        if os.getenv("RAILWAY_ENVIRONMENT"):
            railway_service = os.getenv("RAILWAY_SERVICE_NAME", "").lower()
            if "testing" in railway_service or "test" in railway_service:
                return Environment.TESTING
            elif "production" in railway_service or "prod" in railway_service:
                return Environment.PRODUCTION
            else:
                return Environment.DEVELOPMENT
        
        return Environment.DEVELOPMENT
    
    def _load_env_files(self):
        """Load environment variables from .env files."""
        if not DOTENV_AVAILABLE:
            return
        
        env_files = []
        
        # Check for E2E testing environment
        if os.getenv('E2E_TESTING') or os.getenv('PYTEST_CURRENT_TEST'):
            if os.path.exists(".env.test"):
                env_files.append(".env.test")
                logger.info("E2E testing detected, loading .env.test")
        
        # Load .env if not in E2E testing mode
        if not env_files and os.path.exists(".env"):
            env_files.append(".env")
        
        # Load environment-specific file
        env_specific = f".env.{self._environment.value}"
        if os.path.exists(env_specific):
            env_files.append(env_specific)
        
        for env_file in env_files:
            try:
                load_dotenv(env_file)
                logger.info(f"Loaded environment variables from {env_file}")
            except Exception as e:
                logger.warning(f"Failed to load {env_file}: {e}")
    
    def _setup_sources(self) -> List[ConfigurationSource]:
        """Set up configuration sources in priority order."""
        sources = [
            EnvironmentConfigurationSource(),
            FileConfigurationSource(self._config_path),
            DatabaseConfigurationSource(),
            DefaultConfigurationSource()
        ]
        
        # Filter available sources and sort by priority
        available_sources = [s for s in sources if s.is_available(self._environment)]
        available_sources.sort(key=lambda s: s.get_priority(), reverse=True)
        
        return available_sources
    
    def _setup_validators(self) -> ConfigurationValidator:
        """Set up validation chain."""
        # Chain validators in order
        return EnvironmentValidator(
            DatabaseValidator(
                AIValidator(None)
            )
        )
    
    def load_configuration(self) -> Configuration:
        """Load configuration from all sources."""
        if self._configuration is not None:
            return self._configuration
        
        # Load from all sources in priority order
        merged_config = {}
        for source in self._sources:
            try:
                source_config = source.load_configuration(self._environment)
                # Only add values that haven't been set by higher priority sources
                for key, value in source_config.items():
                    if key not in merged_config:
                        merged_config[key] = value
                    elif isinstance(merged_config[key], dict) and isinstance(value, dict):
                        # For nested dictionaries, only add keys that haven't been set
                        for subkey, subvalue in value.items():
                            if subkey not in merged_config[key]:
                                merged_config[key][subkey] = subvalue
                logger.info(f"Loaded configuration from {source.__class__.__name__}")
            except Exception as e:
                logger.warning(f"Failed to load from {source.__class__.__name__}: {e}")
        
        # Debug: Log the merged configuration
        logger.info(f"🔍 Merged configuration AI section: {merged_config.get('ai', {})}")
        
        # Build configuration object
        builder = ConfigurationBuilder().environment(self._environment)
        
        if "database" in merged_config:
            builder.database(ConfigurationFactory.create_database_config(merged_config["database"]))
        if "ai" in merged_config:
            builder.ai(ConfigurationFactory.create_ai_config(merged_config["ai"]))
        if "telegram" in merged_config:
            builder.telegram(ConfigurationFactory.create_telegram_config(merged_config["telegram"]))
        if "team" in merged_config:
            builder.team(ConfigurationFactory.create_team_config(merged_config["team"]))
        if "payment" in merged_config:
            builder.payment(ConfigurationFactory.create_payment_config(merged_config["payment"]))
        if "llm" in merged_config:
            builder.llm(ConfigurationFactory.create_llm_config(merged_config["llm"]))
        if "advanced_memory" in merged_config:
            builder.advanced_memory(ConfigurationFactory.create_advanced_memory_config(merged_config["advanced_memory"]))
        if "logging" in merged_config:
            builder.logging(ConfigurationFactory.create_logging_config(merged_config["logging"]))
        if "performance" in merged_config:
            builder.performance(ConfigurationFactory.create_performance_config(merged_config["performance"]))
        if "security" in merged_config:
            builder.security(ConfigurationFactory.create_security_config(merged_config["security"]))
        
        self._configuration = builder.build()
        
        # Validate configuration
        self._validate_configuration()
        
        return self._configuration
    
    def _validate_configuration(self):
        """Validate the configuration."""
        if not self._configuration:
            return
        
        errors = self._validators.validate(self._configuration)
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def add_observer(self, observer: ConfigurationObserver):
        """Add a configuration change observer."""
        self._change_notifier.add_observer(observer)
    
    def remove_observer(self, observer: ConfigurationObserver):
        """Remove a configuration change observer."""
        self._change_notifier.remove_observer(observer)
    
    def reload_configuration(self) -> Configuration:
        """Reload configuration and notify observers."""
        self._configuration = None
        config = self.load_configuration()
        self._change_notifier.notify_observers(config)
        return config
    
    @property
    def configuration(self) -> Configuration:
        """Get the current configuration."""
        if self._configuration is None:
            return self.load_configuration()
        return self._configuration
    
    @property
    def environment(self) -> Environment:
        """Get the current environment."""
        return self._environment
    
    def is_development(self) -> bool:
        """Check if in development environment."""
        return self._environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if in production environment."""
        return self._environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if in testing environment."""
        return self._environment == Environment.TESTING


# ============================================================================
# EXCEPTIONS
# ============================================================================

class ConfigurationError(Exception):
    """Configuration-related error."""
    pass


# ============================================================================
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# ============================================================================

_improved_config_manager: Optional[ImprovedConfigurationManager] = None


def get_improved_config() -> ImprovedConfigurationManager:
    """Get the global improved configuration manager."""
    global _improved_config_manager
    if _improved_config_manager is None:
        _improved_config_manager = ImprovedConfigurationManager()
    return _improved_config_manager


def initialize_improved_config(config_path: Optional[str] = None) -> ImprovedConfigurationManager:
    """Initialize the improved configuration system."""
    global _improved_config_manager
    _improved_config_manager = ImprovedConfigurationManager(config_path)
    return _improved_config_manager


# ============================================================================
# MIGRATION HELPER
# ============================================================================

def migrate_from_old_config() -> Configuration:
    """Migrate from the old configuration system to the new one."""
    logger.info("Migrating from old configuration system to improved system")
    
    # Initialize new system
    manager = get_improved_config()
    
    # Load configuration
    config = manager.load_configuration()
    
    logger.info("Migration completed successfully")
    return config
