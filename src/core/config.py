"""
Core Configuration Management for KICKAI

All configuration (Firebase, Telegram, AI, etc.) must be loaded through this module.
No other module should load config or secrets directly.

This module provides centralized configuration management with validation,
type safety, and environment-specific settings.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


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
        self._load_env_files()
        self._config: Dict[str, Any] = {}
        self._load_configuration()
        # Remove validation from __init__ - make it lazy
        self._validated = False
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment."""
        # Check for explicit environment variable first (highest priority)
        env = os.getenv("ENVIRONMENT", "").lower()
        if env:
            try:
                detected_env = Environment(env)
                logging.info(f"Environment explicitly set to: {detected_env}")
                return detected_env
            except ValueError:
                logging.warning(f"Unknown environment '{env}', will use other detection methods")
        
        # Check for KICKAI_ENV as fallback
        env = os.getenv("KICKAI_ENV", "").lower()
        if env:
            try:
                detected_env = Environment(env)
                logging.info(f"KICKAI_ENV set to: {detected_env}")
                return detected_env
            except ValueError:
                logging.warning(f"Unknown KICKAI_ENV '{env}', will use other detection methods")
        
        # Check for CI/testing environments
        if os.getenv("CI") or os.getenv("GITHUB_ACTIONS") or os.getenv("PYTEST_CURRENT_TEST"):
            logging.info("CI/testing environment detected")
            return Environment.TESTING
        
        # Check for Railway environment and determine which one
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
            # Check Railway service name to determine environment
            railway_service = os.getenv("RAILWAY_SERVICE_NAME", "").lower()
            
            if "testing" in railway_service or "test" in railway_service:
                logging.info(f"Railway testing environment detected: {railway_service}")
                return Environment.TESTING
            elif "staging" in railway_service or "stage" in railway_service:
                logging.info(f"Railway staging environment detected: {railway_service}")
                return Environment.DEVELOPMENT  # Treat staging as development for config purposes
            elif "production" in railway_service or "prod" in railway_service:
                logging.info(f"Railway production environment detected: {railway_service}")
                return Environment.PRODUCTION
            else:
                # Default Railway environment - check if it's explicitly set to production
                if env == "production":
                    logging.info("Railway environment with explicit production setting")
                    return Environment.PRODUCTION
                else:
                    # Default Railway environment - treat as development/staging
                    logging.info(f"Railway environment detected (defaulting to development): {railway_service}")
                    return Environment.DEVELOPMENT
        
        # Auto-detect production environments (non-Railway)
        if env == "production":
            return Environment.PRODUCTION
        
        # Check for other production indicators (non-Railway)
        if os.getenv("PORT") and not os.getenv("VIRTUAL_ENV"):
            # Common production indicator
            logging.info("Production environment detected (PORT set, no VIRTUAL_ENV)")
            return Environment.PRODUCTION
        
        # Check for testing environment
        if env == "testing":
            return Environment.TESTING
        
        # Default to development
        if not env:
            env = "development"
        
        try:
            return Environment(env)
        except ValueError:
            logging.warning(f"Unknown environment '{env}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_env_files(self):
        """Load environment variables from .env files."""
        if not DOTENV_AVAILABLE:
            logging.warning("python-dotenv not available, skipping .env file loading")
            return
        
        # Load .env files based on environment
        env_files = []
        
        # Always try to load base .env file
        if os.path.exists(".env"):
            env_files.append(".env")
        
        # Load environment-specific .env file
        env_specific = f".env.{self._environment.value}"
        if os.path.exists(env_specific):
            env_files.append(env_specific)
        
        # Load test environment file if in testing
        if self._environment == Environment.TESTING and os.path.exists(".env.test"):
            env_files.append(".env.test")
        
        # Load the files
        for env_file in env_files:
            try:
                load_dotenv(env_file)
                logging.info(f"Loaded environment variables from {env_file}")
            except Exception as e:
                logging.warning(f"Failed to load {env_file}: {e}")
    
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
        # Extract project_id from FIREBASE_CREDENTIALS_JSON if available
        project_id = ""
        firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if firebase_creds_json:
            try:
                import json
                creds_dict = json.loads(firebase_creds_json)
                project_id = creds_dict.get("project_id", "")
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Fallback to environment variable if JSON parsing failed
        if not project_id:
            project_id = os.getenv("FIREBASE_PROJECT_ID", "")
        
        return DatabaseConfig(
            project_id=project_id,
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
        
        # Load API key based on provider
        api_key = ""
        if provider == AIProvider.GOOGLE_GEMINI:
            api_key = os.getenv("GOOGLE_API_KEY", "")
        elif provider == AIProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY", "")
        elif provider == AIProvider.OLLAMA:
            # For Ollama, we don't need an API key, but we need to ensure Ollama is running
            api_key = "ollama_local"  # Placeholder for Ollama
        else:
            # Fallback to generic AI_API_KEY
            api_key = os.getenv("AI_API_KEY", "")
        
        # Set default model name based on provider
        default_model = "gemini-2.0-flash-001"
        if provider == AIProvider.OLLAMA:
            default_model = "llama3.1:8b-instruct-q4_0"
        elif provider == AIProvider.OPENAI:
            default_model = "gpt-4"
        
        return AIConfig(
            provider=provider,
            api_key=api_key,
            model_name=os.getenv("AI_MODEL_NAME", default_model),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "1000")),
            timeout_seconds=int(os.getenv("AI_TIMEOUT", "60"))
        )
    
    def _load_telegram_config(self) -> TelegramConfig:
        """Load Telegram configuration.
        
        In production, bot tokens are loaded from Firestore via the bot configuration manager.
        In development/testing, they can be loaded from environment variables or local config files.
        """
        # Get bot token from environment variable (for development/testing)
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        # In production, we'll get the bot token from the bot configuration manager
        # when needed, rather than storing it here
        if self._environment == Environment.PRODUCTION and not bot_token:
            # In production, we don't require TELEGRAM_BOT_TOKEN in environment
            # as it will be loaded from Firestore when needed
            bot_token = ""
        
        return TelegramConfig(
            bot_token=bot_token,
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
    
    def validate_configuration(self):
        """Validate the loaded configuration (lazy validation)."""
        if self._validated:
            return
        
        # Skip validation in testing environment
        if self._environment == Environment.TESTING:
            logging.info("Testing environment detected, skipping configuration validation")
            self._validated = True
            return
        
        errors = []
        
        # Check for Firebase credentials
        firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        firebase_creds_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
        
        if not firebase_creds_json and not firebase_creds_file:
            errors.append("Either FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE is required")
        elif firebase_creds_json:
            # Validate that the JSON contains required fields
            try:
                import json
                creds_dict = json.loads(firebase_creds_json)
                if not creds_dict.get("project_id"):
                    errors.append("FIREBASE_CREDENTIALS_JSON must contain project_id")
                if not creds_dict.get("private_key"):
                    errors.append("FIREBASE_CREDENTIALS_JSON must contain private_key")
                if not creds_dict.get("client_email"):
                    errors.append("FIREBASE_CREDENTIALS_JSON must contain client_email")
            except json.JSONDecodeError:
                errors.append("FIREBASE_CREDENTIALS_JSON must be valid JSON")
        elif firebase_creds_file:
            # Validate that the file exists
            if not os.path.exists(firebase_creds_file):
                errors.append(f"FIREBASE_CREDENTIALS_FILE does not exist: {firebase_creds_file}")
        
        # For production, AI_API_KEY and TELEGRAM_BOT_TOKEN may be loaded from Firebase
        # Only validate if we're in development or if they're explicitly required
        if self._environment == Environment.DEVELOPMENT:
            # Check for appropriate API key based on provider
            if self._config["ai"].provider == AIProvider.GOOGLE_GEMINI:
                if not self._config["ai"].api_key:
                    errors.append("GOOGLE_API_KEY is required in development environment for Gemini")
            elif self._config["ai"].provider == AIProvider.OPENAI:
                if not self._config["ai"].api_key:
                    errors.append("OPENAI_API_KEY is required in development environment for OpenAI")
            elif self._config["ai"].provider == AIProvider.OLLAMA:
                # For Ollama, check if the service is running
                try:
                    import subprocess
                    result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
                    if result.returncode != 0:
                        errors.append("Ollama is not running. Please start Ollama with 'ollama serve'")
                    elif self._config["ai"].model_name not in result.stdout:
                        errors.append(f"Ollama model '{self._config['ai'].model_name}' not found. Available models: {result.stdout}")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    errors.append("Ollama is not installed or not accessible. Please install Ollama and start it with 'ollama serve'")
            else:
                if not self._config["ai"].api_key:
                    errors.append("AI_API_KEY is required in development environment")
            
            # In development, we can use either environment variables or local config files
            # Don't require TELEGRAM_BOT_TOKEN if using local config files
            if not self._config["telegram"].bot_token:
                # Check if we have a local bot configuration
                try:
                    from .bot_config_manager import get_bot_config_manager
                    manager = get_bot_config_manager()
                    config = manager.load_configuration()
                    if not config.teams:
                        errors.append("TELEGRAM_BOT_TOKEN is required in development environment or configure local bot config")
                except Exception:
                    errors.append("TELEGRAM_BOT_TOKEN is required in development environment")
        
        # Validate ranges
        if not (0.0 <= self._config["ai"].temperature <= 2.0):
            errors.append("AI_TEMPERATURE must be between 0.0 and 2.0")
        
        if self._config["ai"].max_tokens <= 0:
            errors.append("AI_MAX_TOKENS must be positive")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
        
        self._validated = True
    
    def _needs_validation(self) -> bool:
        """Check if validation is needed for the current environment."""
        # Skip validation in testing environment
        if self._environment == Environment.TESTING:
            return False
        
        # Only validate in development and production
        return self._environment in [Environment.DEVELOPMENT, Environment.PRODUCTION]
    
    @property
    def environment(self) -> Environment:
        """Get the current environment."""
        return self._environment
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration."""
        if self._needs_validation():
            self.validate_configuration()
        return self._config["database"]
    
    @property
    def ai(self) -> AIConfig:
        """Get AI configuration."""
        if self._needs_validation():
            self.validate_configuration()
        return self._config["ai"]
    
    @property
    def telegram(self) -> TelegramConfig:
        """Get Telegram configuration."""
        if self._needs_validation():
            self.validate_configuration()
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