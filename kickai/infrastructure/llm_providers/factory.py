"""
LLM Providers Factory

This module provides a factory pattern for managing different LLM providers
with proper configuration, error handling, and integration with the existing
LLM factory system.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from kickai.core.config import get_settings
from kickai.core.enums import AIProvider


# Simple compatibility classes for LLM factory
@dataclass
class LLMConfig:
    """Legacy LLM configuration for compatibility."""

    provider: AIProvider
    model_name: str
    api_key: str | None = None
    temperature: float = 0.7
    timeout: int = 30


class LLMFactory:
    """Legacy LLM factory for compatibility."""

    @staticmethod
    def create_llm(config: LLMConfig) -> Any:
        """Create LLM using the new factory."""
        from kickai.utils.llm_factory_simple import SimpleLLMFactory

        return SimpleLLMFactory.create_llm(config.model_name, config.temperature)


class LLMProviderError(Exception):
    """LLM provider error."""

    pass


logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""

    provider: AIProvider
    model_name: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3
    additional_params: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate configuration."""
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {self.temperature}")

        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")

        if not self.model_name.strip():
            raise ValueError("Model name cannot be empty")


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration."""
        pass

    @abstractmethod
    def create_llm(self) -> Any:
        """Create an LLM instance."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass

    def get_health_status(self) -> dict[str, Any]:
        """Get provider health status."""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model_name,
            "available": self.is_available(),
            "temperature": self.config.temperature,
            "timeout": self.config.timeout_seconds,
        }


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""

    def _validate_config(self) -> None:
        """Validate Ollama configuration."""
        if not self.config.model_name:
            raise ValueError("Ollama requires model_name")

        # Set default base URL if not provided
        if not self.config.base_url:
            self.config.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def create_llm(self) -> Any:
        """Create Ollama LLM instance."""
        try:
            # Convert to LLMConfig format for compatibility
            llm_config = LLMConfig(
                provider=self.config.provider,
                model_name=self.config.model_name,
                api_key="",  # Ollama doesn't need API key
                temperature=self.config.temperature,
                timeout_seconds=self.config.timeout_seconds,
                max_retries=self.config.max_retries,
                api_base=self.config.base_url,
                additional_params=self.config.additional_params,
            )

            return LLMFactory.create_llm(llm_config)

        except Exception as e:
            logger.error(f"Failed to create Ollama LLM: {e}")
            raise LLMProviderError(f"Ollama LLM creation failed: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            import requests

            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider implementation."""

    def _validate_config(self) -> None:
        """Validate Gemini configuration."""
        if not self.config.api_key:
            raise ValueError("Gemini requires API key")

        if not self.config.model_name:
            self.config.model_name = os.getenv("GOOGLE_AI_MODEL_NAME", "gemini-1.5-flash")

    def create_llm(self) -> Any:
        """Create Gemini LLM instance."""
        try:
            # Convert to LLMConfig format for compatibility
            llm_config = LLMConfig(
                provider=self.config.provider,
                model_name=self.config.model_name,
                api_key=self.config.api_key,
                temperature=self.config.temperature,
                timeout_seconds=self.config.timeout_seconds,
                max_retries=self.config.max_retries,
                additional_params=self.config.additional_params,
            )

            return LLMFactory.create_llm(llm_config)

        except Exception as e:
            logger.error(f"Failed to create Gemini LLM: {e}")
            raise LLMProviderError(f"Gemini LLM creation failed: {e}")

    def is_available(self) -> bool:
        """Check if Gemini is available."""
        # For now, assume available if API key is present
        # In a production system, you might want to make a test API call
        return bool(self.config.api_key)


class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face LLM provider implementation."""

    def _validate_config(self) -> None:
        """Validate Hugging Face configuration."""
        if not self.config.api_key:
            raise ValueError("Hugging Face requires API key")

        if not self.config.model_name:
            raise ValueError("Hugging Face requires model_name")

    def create_llm(self) -> Any:
        """Create Hugging Face LLM instance."""
        try:
            # Convert to LLMConfig format for compatibility
            llm_config = LLMConfig(
                provider=self.config.provider,
                model_name=self.config.model_name,
                api_key=self.config.api_key,
                temperature=self.config.temperature,
                timeout_seconds=self.config.timeout_seconds,
                max_retries=self.config.max_retries,
                additional_params=self.config.additional_params,
            )

            return LLMFactory.create_llm(llm_config)

        except Exception as e:
            logger.error(f"Failed to create Hugging Face LLM: {e}")
            raise LLMProviderError(f"Hugging Face LLM creation failed: {e}")

    def is_available(self) -> bool:
        """Check if Hugging Face is available."""
        # For now, assume available if API key is present
        return bool(self.config.api_key)


class MockProvider(BaseLLMProvider):
    """Mock LLM provider for testing."""

    def _validate_config(self) -> None:
        """Validate mock configuration."""
        # Mock provider doesn't require specific validation
        pass

    def create_llm(self) -> Any:
        """Create mock LLM instance."""
        try:
            # Convert to LLMConfig format for compatibility
            llm_config = LLMConfig(
                provider=self.config.provider,
                model_name=self.config.model_name,
                api_key="mock-key",
                temperature=self.config.temperature,
                timeout_seconds=self.config.timeout_seconds,
                max_retries=self.config.max_retries,
                additional_params=self.config.additional_params,
            )

            return LLMFactory.create_llm(llm_config)

        except Exception as e:
            logger.error(f"Failed to create Mock LLM: {e}")
            raise LLMProviderError(f"Mock LLM creation failed: {e}")

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances.

    This factory provides a clean interface for creating and managing
    different LLM providers with proper configuration and error handling.
    """

    _providers: dict[AIProvider, type[BaseLLMProvider]] = {
        AIProvider.OLLAMA: OllamaProvider,
        AIProvider.GOOGLE_GEMINI: GeminiProvider,
        AIProvider.HUGGINGFACE: HuggingFaceProvider,
        AIProvider.MOCK: MockProvider,
    }

    @classmethod
    def register_provider(cls, provider: AIProvider, provider_class: type[BaseLLMProvider]) -> None:
        """Register a new LLM provider."""
        cls._providers[provider] = provider_class
        logger.info(f"Registered LLM provider: {provider.value}")

    @classmethod
    def get_provider_class(cls, provider: AIProvider) -> type[BaseLLMProvider]:
        """Get the provider class for the given AI provider."""
        if provider not in cls._providers:
            raise LLMProviderError(f"Unsupported AI provider: {provider.value}")

        return cls._providers[provider]

    @classmethod
    def create_provider(cls, config: ProviderConfig) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            config: Provider configuration

        Returns:
            Configured LLM provider instance

        Raises:
            LLMProviderError: If provider creation fails
        """
        logger.info(f"Creating LLM provider: {config.provider.value}, model: {config.model_name}")

        provider_class = cls.get_provider_class(config.provider)
        return provider_class(config)

    @classmethod
    def create_from_settings(cls, provider: AIProvider | None = None) -> BaseLLMProvider:
        """
        Create an LLM provider from application settings.

        Args:
            provider: Optional provider override

        Returns:
            Configured LLM provider instance
        """
        settings = get_settings()

        # Use provided provider or get from settings
        selected_provider = provider or settings.ai_provider

        # Get API key based on provider
        api_key = None
        if selected_provider == AIProvider.GOOGLE_GEMINI:
            api_key = settings.gemini_api_key
        elif selected_provider == AIProvider.GROQ:
            api_key = settings.groq_api_key
        elif selected_provider == AIProvider.HUGGINGFACE:
            api_key = settings.huggingface_api_token  # Assuming this is in settings
        elif selected_provider == AIProvider.OPENAI:
            api_key = settings.openai_api_key  # Assuming this is in settings
        elif selected_provider == AIProvider.OLLAMA:
            api_key = None  # Ollama doesn't need API key

        # Create provider configuration
        # Choose model: prefer simple/advanced pair; fallback to legacy name
        model_name = (
            settings.ai_model_simple or settings.ai_model_advanced or settings.ai_model_name or ""
        )

        config = ProviderConfig(
            provider=selected_provider,
            model_name=model_name,
            api_key=api_key,
            base_url=settings.ollama_base_url if selected_provider == AIProvider.OLLAMA else None,
            temperature=settings.ai_temperature,
            timeout_seconds=settings.ai_timeout,
            max_retries=settings.ai_max_retries,
        )

        return cls.create_provider(config)

    @classmethod
    def create_from_environment(cls, provider: AIProvider | None = None) -> BaseLLMProvider:
        """
        Create an LLM provider from environment variables.

        Args:
            provider: Optional provider override

        Returns:
            Configured LLM provider instance
        """
        # Get provider from environment or use default (force Groq as safe default)
        if provider is None:
            provider_str = os.getenv("AI_PROVIDER", "groq")
            try:
                provider = AIProvider(provider_str)
            except ValueError:
                raise LLMProviderError(f"Invalid AI_PROVIDER: {provider_str}")

        # Get model name from environment
        model_name = os.getenv("AI_MODEL_NAME")
        if not model_name:
            if provider == AIProvider.GEMINI:
                model_name = os.getenv("GOOGLE_AI_MODEL_NAME", "gemini-1.5-flash")
            elif provider == AIProvider.HUGGINGFACE:
                model_name = os.getenv("HUGGINGFACE_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
            elif provider == AIProvider.OLLAMA:
                model_name = os.getenv("OLLAMA_MODEL", "llama2")
            elif provider == AIProvider.MOCK:
                model_name = os.getenv("MOCK_MODEL", "mock-model")

        # Get API key based on provider
        api_key = None
        if provider == AIProvider.GEMINI:
            api_key = os.getenv("GOOGLE_API_KEY")
        elif provider == AIProvider.HUGGINGFACE:
            api_key = os.getenv("HUGGINGFACE_API_TOKEN")

        # Get base URL for Ollama
        base_url = None
        if provider == AIProvider.OLLAMA:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # Create provider configuration
        config = ProviderConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT", "30")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
        )

        return cls.create_provider(config)

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported AI providers."""
        return [provider.value for provider in cls._providers.keys()]

    @classmethod
    def get_provider_health_status(cls) -> dict[str, dict[str, Any]]:
        """Get health status for all providers."""
        health_status = {}

        for provider_enum in cls._providers.keys():
            try:
                # Create a minimal config for health check
                config = ProviderConfig(
                    provider=provider_enum,
                    model_name="test-model",
                    api_key="test-key" if provider_enum != AIProvider.OLLAMA else None,
                )

                provider_instance = cls.create_provider(config)
                health_status[provider_enum.value] = provider_instance.get_health_status()

            except Exception as e:
                health_status[provider_enum.value] = {
                    "provider": provider_enum.value,
                    "available": False,
                    "error": str(e),
                }

        return health_status


# Convenience functions for easy access
def create_llm_provider(config: ProviderConfig) -> BaseLLMProvider:
    """Create an LLM provider with the given configuration."""
    return LLMProviderFactory.create_provider(config)


def create_llm_provider_from_settings(provider: AIProvider | None = None) -> BaseLLMProvider:
    """Create an LLM provider from application settings."""
    return LLMProviderFactory.create_from_settings(provider)


def get_provider_health_status() -> dict[str, dict[str, Any]]:
    """Get health status for all available providers."""
    return LLMProviderFactory.get_provider_health_status()
