from typing import List, Optional
"""
Simplified LLM Configuration for KICKAI following CrewAI Best Practices

This module provides a single source of truth for LLM configuration,
following CrewAI's recommended patterns for direct LLM instantiation
with agent-specific optimization and production-ready Ollama client.
"""

import logging

from crewai import LLM
from litellm import completion

from kickai.core.enums import AgentRole, AIProvider
from kickai.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMConfiguration:
    """
    Centralized LLM configuration following CrewAI best practices.

    This class provides direct LLM instantiation as recommended by CrewAI,
    with agent-specific optimization and function calling LLM support.
    It dynamically selects the LLM provider based on settings.
    """

    def __init__(self):
        """Initialize LLM configuration from settings."""
        self.settings = get_settings()
        self.ai_provider = self.settings.ai_provider
        self.default_model = self.settings.ai_model_name
        self.groq_api_key = self.settings.groq_api_key
        self.ollama_base_url = self.settings.ollama_base_url

        logger.info(
            f"🤖 LLM Configuration initialized: provider={self.ai_provider.value}, model={self.default_model}"
        )

    def _create_llm(self, temperature: float, max_tokens: int) -> LLM:
        """
        Helper to create an LLM instance based on the configured AI provider.
        """
        if self.ai_provider == AIProvider.GROQ:
            return LLM(
                model=f"groq/{self.default_model}",
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.groq_api_key,
            )
        elif self.ai_provider == AIProvider.OLLAMA:
            return LLM(
                model=f"ollama/{self.default_model}",
                base_url=self.ollama_base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif self.ai_provider == AIProvider.GOOGLE_GEMINI:
            return LLM(
                model=f"gemini/{self.default_model}",
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.settings.google_gemini_api_key, # Assuming you have this in settings
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

    @property
    def main_llm(self) -> LLM:
        """
        Primary LLM for complex reasoning tasks.

        Returns:
            LLM: Configured for balanced reasoning with moderate temperature
        """
        return self._create_llm(temperature=0.3, max_tokens=800)

    @property
    def tool_llm(self) -> LLM:
        """
        Optimized LLM for tool calling and function execution.

        Uses lower temperature for precise tool calling as recommended by CrewAI.

        Returns:
            LLM: Configured for precise tool calling
        """
        return self._create_llm(temperature=0.1, max_tokens=500)

    @property
    def creative_llm(self) -> LLM:
        """
        Higher temperature LLM for creative and analytical tasks.

        Returns:
            LLM: Configured for creative reasoning
        """
        return self._create_llm(temperature=0.7, max_tokens=1000)

    @property
    def data_critical_llm(self) -> LLM:
        """
        Ultra-precise LLM for data-critical operations.

        Uses very low temperature for anti-hallucination in critical operations.

        Returns:
            LLM: Configured for maximum precision
        """
        return self._create_llm(temperature=0.1, max_tokens=600)

    def get_llm_for_agent(self, agent_role: AgentRole) -> tuple[LLM, LLM]:
        """
        Get optimal LLM configuration for specific agent role.

        Returns tuple of (main_llm, function_calling_llm) as recommended by CrewAI.

        Args:
            agent_role: The agent role to get LLM configuration for

        Returns:
            tuple[LLM, LLM]: (main_llm, function_calling_llm)
        """
        # Data-critical agents use precise models (high accuracy priority)
        if agent_role in [
            AgentRole.PLAYER_COORDINATOR,      # Player data management
            AgentRole.MESSAGE_PROCESSOR,       # Primary interface
            AgentRole.HELP_ASSISTANT,          # User guidance
        ]:
            return self.data_critical_llm, self.tool_llm

        # Administrative agents use balanced models 
        if agent_role in [
            AgentRole.TEAM_ADMINISTRATOR,      # Team management
        ]:
            return self.main_llm, self.tool_llm

        # Creative/analytical agents use higher temperature models
        if agent_role in [
            AgentRole.SQUAD_SELECTOR,          # Squad selection and tactics
        ]:
            return self.creative_llm, self.tool_llm

        # Default: balanced configuration for any other agents
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
        Test connection to the configured LLM provider synchronously.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            messages = [{
                "role": "user",
                "content": "Hello, world!"
            }]
            # Use litellm.completion for a universal connection test
            response = completion(
                model=f"{self.ai_provider.value}/{self.default_model}",
                messages=messages,
                api_key=self.groq_api_key if self.ai_provider == AIProvider.GROQ else \
                        self.settings.google_gemini_api_key if self.ai_provider == AIProvider.GOOGLE_GEMINI else None,
                base_url=self.ollama_base_url if self.ai_provider == AIProvider.OLLAMA else None,
                temperature=0.1,
                max_tokens=10,
                timeout=10, # 10 second timeout for connection test
            )
            if response.choices and response.choices[0].message.content:
                logger.info(f"✅ {self.ai_provider.value} connection test successful")
                return True
            else:
                logger.error(f"❌ {self.ai_provider.value} connection test failed: No content in response")
                return False
        except Exception as e:
            logger.error(f"❌ {self.ai_provider.value} connection test failed: {e}")
            return False

    async def test_connection_async(self) -> bool:
        """
        Test connection to the configured LLM provider asynchronously.

        Returns:
            bool: True if connection successful, False otherwise
        """
        # For simplicity, async test can call sync test or use an async litellm call
        # For now, we'll just call the sync version for immediate fix
        return self.test_connection()

    def get_available_models(self) -> list[str]:
        """
        Get list of available models from the configured LLM provider.

        Note: This is a placeholder. LiteLLM does not have a direct API to list models.
        You would typically query the provider's API directly or maintain a local list.

        Returns:
            List[str]: List of available model names (placeholder)
        """
        logger.warning("Listing available models is not directly supported via LiteLLM for all providers.")
        return [self.default_model] # Return configured model as a placeholder


# Global instance - single source of truth
_llm_config: Optional[LLMConfiguration] = None


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
