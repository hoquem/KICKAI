"""
Simplified LLM Configuration for KICKAI following CrewAI Best Practices

This module provides a single source of truth for LLM configuration,
following CrewAI's recommended patterns for direct LLM instantiation
with agent-specific optimization and production-ready Ollama client.
"""

import logging
from typing import Any, List

from crewai import LLM

from kickai.core.enums import AgentRole
from kickai.core.settings import get_settings
from kickai.infrastructure.ollama_factory import get_ollama_client
from kickai.infrastructure.ollama_client import (
    OllamaConnectionError, 
    OllamaTimeoutError, 
    OllamaCircuitBreakerError,
    OllamaClientError
)

logger = logging.getLogger(__name__)


class LLMConfiguration:
    """
    Centralized LLM configuration following CrewAI best practices.
    
    This class provides direct LLM instantiation as recommended by CrewAI,
    with agent-specific optimization and function calling LLM support.
    """

    def __init__(self):
        """Initialize LLM configuration from settings."""
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url
        self.default_model = self.settings.ai_model_name
        self._ollama_client = None  # Lazy initialization
        
        logger.info(f"🤖 LLM Configuration initialized: model={self.default_model}, base_url={self.base_url}")
    
    @property
    def ollama_client(self):
        """Get or create Ollama client instance (lazy initialization)."""
        if self._ollama_client is None:
            self._ollama_client = get_ollama_client(self.settings)
        return self._ollama_client

    @property
    def main_llm(self) -> LLM:
        """
        Primary LLM for complex reasoning tasks.
        
        Returns:
            LLM: Configured for balanced reasoning with moderate temperature
        """
        return LLM(
            model=f"ollama/{self.default_model}",
            base_url=self.base_url,
            temperature=0.3,
            max_tokens=800
        )

    @property
    def tool_llm(self) -> LLM:
        """
        Optimized LLM for tool calling and function execution.
        
        Uses lower temperature for precise tool calling as recommended by CrewAI.
        
        Returns:
            LLM: Configured for precise tool calling
        """
        return LLM(
            model=f"ollama/{self.default_model}",
            base_url=self.base_url,
            temperature=0.1,  # Lower temp for tool precision
            max_tokens=500
        )

    @property
    def creative_llm(self) -> LLM:
        """
        Higher temperature LLM for creative and analytical tasks.
        
        Returns:
            LLM: Configured for creative reasoning
        """
        return LLM(
            model=f"ollama/{self.default_model}",
            base_url=self.base_url,
            temperature=0.7,  # Higher temp for creativity
            max_tokens=1000
        )

    @property
    def data_critical_llm(self) -> LLM:
        """
        Ultra-precise LLM for data-critical operations.
        
        Uses very low temperature for anti-hallucination in critical operations.
        
        Returns:
            LLM: Configured for maximum precision
        """
        return LLM(
            model=f"ollama/{self.default_model}",
            base_url=self.base_url,
            temperature=0.1,  # Very low for data accuracy
            max_tokens=600
        )

    def get_llm_for_agent(self, agent_role: AgentRole) -> tuple[LLM, LLM]:
        """
        Get optimal LLM configuration for specific agent role.
        
        Returns tuple of (main_llm, function_calling_llm) as recommended by CrewAI.
        
        Args:
            agent_role: The agent role to get LLM configuration for
            
        Returns:
            tuple[LLM, LLM]: (main_llm, function_calling_llm)
        """
        # Data-critical agents use precise models
        if agent_role in [
            AgentRole.PLAYER_COORDINATOR,
            AgentRole.MESSAGE_PROCESSOR,
            AgentRole.FINANCE_MANAGER,
            AgentRole.COMMUNICATION_MANAGER,
        ]:
            return self.data_critical_llm, self.tool_llm

        # Creative/analytical agents use higher temperature models
        if agent_role in [
            AgentRole.PERFORMANCE_ANALYST,
            AgentRole.LEARNING_AGENT,
            AgentRole.SQUAD_SELECTOR,
        ]:
            return self.creative_llm, self.tool_llm

        # Default: balanced configuration for other agents
        return self.main_llm, self.tool_llm

    def validate_configuration(self) -> list[str]:
        """
        Validate LLM configuration and return any errors.
        
        Returns:
            list[str]: List of validation error messages (empty if valid)
        """
        errors = []

        # Validate base URL
        if not self.base_url:
            errors.append("OLLAMA_BASE_URL is required but not configured")

        if not self.base_url.startswith(('http://', 'https://')):
            errors.append(f"OLLAMA_BASE_URL must start with http:// or https://, got: {self.base_url}")

        # Validate model name
        if not self.default_model:
            errors.append("AI_MODEL_NAME is required but not configured")

        # Validate model format for Ollama
        if not self.default_model.startswith('llama'):
            logger.warning(f"Model name '{self.default_model}' may not be compatible with Ollama")

        return errors

    def test_connection(self) -> bool:
        """
        Test connection to Ollama server synchronously.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Use a simple HTTP request instead of the async client for this check
            import httpx
            
            url = f"{self.base_url}/api/tags"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                logger.info("✅ Ollama sync connection test successful")
                return True
        except Exception as e:
            logger.error(f"❌ Ollama sync connection test failed: {e}")
            return False

    async def test_connection_async(self) -> bool:
        """
        Test connection to Ollama server asynchronously using robust client.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            result = await self.ollama_client.health_check()
            if result:
                logger.info("✅ Ollama async connection test successful")
            else:
                logger.error("❌ Ollama async connection test failed")
            return result
        except OllamaCircuitBreakerError:
            logger.error("❌ Ollama connection test blocked by circuit breaker")
            return False
        except (OllamaConnectionError, OllamaTimeoutError) as e:
            logger.error(f"❌ Ollama async connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ollama async connection test failed with unexpected error: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """
        Get list of available models from Ollama server using robust client.
        
        Returns:
            List[str]: List of available model names
        """
        try:
            # Use a simple HTTP request instead of the async client for this check
            import httpx
            import json
            
            url = f"{self.base_url}/api/tags"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                logger.info(f"📋 Available models: {models}")
                return models
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def _get_available_models_async(self) -> List[str]:
        """Get available models asynchronously."""
        try:
            models = await self.ollama_client.get_models()
            logger.info(f"📋 Available models: {models}")
            return models
        except OllamaCircuitBreakerError:
            logger.error("❌ Get models blocked by circuit breaker")
            return []
        except (OllamaConnectionError, OllamaTimeoutError) as e:
            logger.error(f"❌ Failed to get available models: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to get available models with unexpected error: {e}")
            return []


# Global instance - single source of truth
_llm_config: LLMConfiguration | None = None


def get_llm_config() -> LLMConfiguration:
    """
    Get the global LLM configuration instance.
    
    Returns:
        LLMConfiguration: The singleton LLM configuration instance
    """
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfiguration()
    return _llm_config


def initialize_llm_config() -> LLMConfiguration:
    """
    Initialize and validate LLM configuration.
    
    Returns:
        LLMConfiguration: Initialized and validated configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    global _llm_config
    _llm_config = LLMConfiguration()
    
    # Validate configuration
    errors = _llm_config.validate_configuration()
    if errors:
        error_msg = "LLM Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("✅ LLM Configuration initialized and validated successfully")
    return _llm_config