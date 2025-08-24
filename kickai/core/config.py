"""
Clean Configuration System for KICKAI

This module provides a simple, type-safe configuration system that consolidates
all configuration into one place using industry-standard pydantic-settings.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


from kickai.core.enums import AIProvider


class Settings(BaseSettings):
    """Main application settings - single source of truth for all configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ============================================================================
    # ENVIRONMENT CONFIGURATION
    # ============================================================================
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    
    # ============================================================================
    # FIREBASE CONFIGURATION
    # ============================================================================
    firebase_project_id: str = Field(
        description="Firebase project ID (REQUIRED)"
    )
    firebase_credentials_file: Optional[str] = Field(
        default=None,
        alias="FIREBASE_CREDENTIALS_FILE",
        description="Path to Firebase credentials file"
    )
    firebase_credentials_json: Optional[str] = Field(
        default=None,
        alias="FIREBASE_CREDENTIALS_JSON",
        description="Firebase credentials as JSON string"
    )
    firebase_batch_size: int = Field(default=500, description="Firebase batch size")
    firebase_timeout: int = Field(default=30, description="Firebase timeout in seconds")
    
    # ============================================================================
    # AI/LLM CONFIGURATION
    # ============================================================================
    ai_provider: AIProvider = Field(
        default=AIProvider.GROQ,
        alias="AI_PROVIDER",
        description="AI provider to use"
    )
    
    # API Keys
    groq_api_key: str = Field(
        default="",
        alias="GROQ_API_KEY",
        description="Groq API key (REQUIRED for Groq)"
    )
    gemini_api_key: str = Field(
        default="",
        alias="GOOGLE_API_KEY",
        description="Google API key (REQUIRED for Gemini)"
    )
    openai_api_key: str = Field(
        default="",
        alias="OPENAI_API_KEY",
        description="OpenAI API key (REQUIRED for OpenAI)"
    )
    
    # Model Configuration
    ai_model_name: Optional[str] = Field(
        default=None,
        alias="AI_MODEL_NAME",
        description="DEPRECATED: Use ai_model_simple/advanced instead"
    )
    ai_model_nlp: Optional[str] = Field(
        default=None,
        alias="AI_MODEL_NLP", 
        description="Specialized NLP model for intelligent processing (e.g., gpt-oss-20b)"
    )
    ai_model_simple: Optional[str] = Field(
        default=None,
        alias="AI_MODEL_SIMPLE",
        description="Simple/default AI model name for lightweight agents"
    )
    ai_model_advanced: Optional[str] = Field(
        default=None,
        alias="AI_MODEL_ADVANCED",
        description="Advanced AI model name for complex agents"
    )
    
    # Temperature Settings
    ai_temperature: float = Field(default=0.3, description="Default AI temperature")
    ai_temperature_tools: float = Field(default=0.1, description="AI temperature for tools")
    ai_temperature_creative: float = Field(default=0.7, description="AI temperature for creative tasks")
    
    # Token and Timeout Settings
    ai_max_tokens: int = Field(default=800, description="Default AI max tokens")
    ai_max_tokens_tools: int = Field(default=500, description="AI max tokens for tools")
    ai_max_tokens_creative: int = Field(default=1000, description="AI max tokens for creative tasks")
    ai_timeout: int = Field(default=120, description="AI timeout in seconds")
    ai_max_retries: int = Field(default=5, description="AI max retries")
    

    # Ollama Configuration (if using Ollama)
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
        description="Ollama base URL (only needed if using Ollama provider)"
    )
    
    # ============================================================================
    # TELEGRAM CONFIGURATION
    # ============================================================================
    telegram_webhook_url: Optional[str] = Field(
        default=None,
        alias="TELEGRAM_WEBHOOK_URL",
        description="Telegram webhook URL"
    )
    telegram_parse_mode: str = Field(default="HTML", description="Telegram parse mode")
    telegram_timeout: int = Field(default=30, description="Telegram timeout in seconds")
    
    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================
    log_level: str = Field(default="INFO", alias="LOG_LEVEL", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    log_file_path: Optional[str] = Field(
        default="logs/kickai.log",
        alias="LOG_FILE_PATH",
        description="Log file path"
    )
    log_max_file_size: int = Field(default=10485760, description="Max log file size (10MB)")
    log_backup_count: int = Field(default=5, description="Number of log backup files")
    
    # ============================================================================
    # SYSTEM CONFIGURATION
    # ============================================================================
    debug: bool = Field(default=False, description="Debug mode")
    verbose_logging: bool = Field(default=False, description="Verbose logging")
    test_mode: bool = Field(default=False, description="Test mode")
    
    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================
    
    @field_validator("environment", mode="before")
    @classmethod
    def detect_environment(cls, v):
        """Auto-detect environment if not specified."""
        if v is not None:
            return v
            
        # Check for test environment
        if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("E2E_TESTING"):
            return Environment.TESTING
            
        # Check for production environment
        if os.getenv("RAILWAY_ENVIRONMENT"):
            return Environment.PRODUCTION
            
        return Environment.DEVELOPMENT
    
    @field_validator("ai_provider", mode="before")
    @classmethod
    def validate_ai_provider(cls, v):
        """Validate AI provider."""
        if isinstance(v, str):
            try:
                return AIProvider(v.lower())
            except ValueError:
                raise ValueError(f"Invalid AI_PROVIDER: {v}. Supported: {[p.value for p in AIProvider]}")
        return v
    
    @field_validator("firebase_credentials_file", "firebase_credentials_json")
    @classmethod
    def validate_firebase_credentials(cls, v, info):
        """Validate that at least one Firebase credential method is provided."""
        # Get the other field value
        other_field = "firebase_credentials_json" if info.field_name == "firebase_credentials_file" else "firebase_credentials_file"
        other_value = info.data.get(other_field) if info.data else None
        
        if not v and not other_value:
            raise ValueError(
                "Either FIREBASE_CREDENTIALS_FILE or FIREBASE_CREDENTIALS_JSON must be provided"
            )
        return v
    
    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_api_key(cls, v, info):
        """Validate Groq API key when using Groq provider."""
        if info.data and info.data.get("ai_provider") == AIProvider.GROQ and not v:
            raise ValueError("GROQ_API_KEY is required when using Groq provider")
        return v

    @model_validator(mode="after")
    def validate_model_specification(self):
        """Ensure at least one model is configured via AI_MODEL_SIMPLE/ADVANCED or legacy AI_MODEL_NAME."""
        # Check if any model is configured
        if self.ai_model_name or self.ai_model_simple or self.ai_model_advanced:
            return self
        
        # No models configured at all - raise error
        raise ValueError(
            "Model configuration missing: set AI_MODEL_SIMPLE and AI_MODEL_ADVANCED, or provide legacy AI_MODEL_NAME"
        )
    
    @field_validator("gemini_api_key")
    @classmethod
    def validate_gemini_api_key(cls, v, info):
        """Validate Gemini API key when using Gemini provider."""
        if info.data and info.data.get("ai_provider") == AIProvider.GOOGLE_GEMINI and not v:
            raise ValueError("GOOGLE_API_KEY is required when using Gemini provider")
        return v
    
    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_api_key(cls, v, info):
        """Validate OpenAI API key when using OpenAI provider."""
        if info.data and info.data.get("ai_provider") == AIProvider.OPENAI and not v:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return v
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def get_ai_api_key(self) -> str:
        """Get the appropriate API key for the configured AI provider."""
        if self.ai_provider == AIProvider.GROQ:
            return self.groq_api_key
        elif self.ai_provider == AIProvider.GOOGLE_GEMINI:
            return self.gemini_api_key
        elif self.ai_provider == AIProvider.OPENAI:
            return self.openai_api_key
        else:
            return ""  # Ollama doesn't need an API key
    
    def get_model_name_for_provider(self, model_type: str = "default") -> str:
        """
        Get the model name formatted for the current provider.
        
        NOTE: This method is kept for backward compatibility but may not be actively used.
        The LLMConfig class handles model selection directly via ai_model_simple/advanced.
        
        Args:
            model_type: "simple", "advanced", or "default" (uses first available)
            
        Returns:
            str: Formatted model name for the provider
        """
        # Select the appropriate model based on type
        if model_type == "simple":
            model_name = self.ai_model_simple or self.ai_model_advanced or self.ai_model_name
        elif model_type == "advanced":
            model_name = self.ai_model_advanced or self.ai_model_simple or self.ai_model_name
        else:  # default - use first available
            model_name = self.ai_model_name or self.ai_model_simple or self.ai_model_advanced
        
        if not model_name:
            model_name = ""  # Return empty string if no model configured
            
        # Format for provider
        if self.ai_provider == AIProvider.GROQ:
            return f"groq/{model_name}" if model_name else ""
        else:  # Gemini, OpenAI, Ollama use model name as-is
            return model_name


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings():
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None
