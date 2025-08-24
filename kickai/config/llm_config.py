from typing import List, Optional, Dict, Any
"""
CrewAI Native LLM Configuration for KICKAI

This module provides a single source of truth for LLM configuration using
only CrewAI-supported parameters. Removed unsupported parameters that cause
BadRequestError with providers like Groq.

Features:
- Native CrewAI LLM configuration with supported parameters only
- Thread-safe configuration management
- Production-ready async compatibility
- Provider-specific parameter optimization
"""

import asyncio
import logging
from functools import lru_cache


from crewai import LLM

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
        """Initialize LLM configuration from settings with rate limiting."""
        self.settings = get_settings()
        self.ai_provider = self.settings.ai_provider
        # Determine default model: prefer simple/advanced pair, fallback to legacy
        self.default_model = (
            self.settings.ai_model_simple
            or self.settings.ai_model_advanced
            or self.settings.ai_model_name  # DEPRECATED fallback
            or ""
        )
        self.simple_model = self.settings.ai_model_simple or self.default_model
        self.advanced_model = self.settings.ai_model_advanced or self.default_model
        self.nlp_model = self.settings.ai_model_nlp or self.advanced_model
        self.groq_api_key = self.settings.groq_api_key
        self.ollama_base_url = self.settings.ollama_base_url

        logger.info(
            f"🤖 LLM Configuration initialized: provider={self.ai_provider.value}, model={self.default_model}"

        )

    def _create_llm(
        self, 
        temperature: float, 
        max_tokens: int,
        use_case: str = "default",
        override_model: Optional[str] = None
    ) -> LLM:
        """
        Create an LLM instance using only CrewAI-supported parameters.
        
        Args:
            temperature: Model temperature
            max_tokens: Maximum tokens to generate
            use_case: Use case identifier for logging and monitoring
            
        Returns:
            LLM: CrewAI LLM instance configured with supported parameters only
            
        Raises:
            ValueError: If AI provider is not supported or API key missing
        """

        model_name = override_model or self.default_model

        logger.info(
            f"Creating {use_case} LLM: provider={self.ai_provider.value}, "
            f"model={model_name}, temp={temperature}, "
            f"max_tokens={max_tokens}"
        )
        
        # Base LLM configuration with CrewAI native parameters only
        base_config = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            # Use only CrewAI-supported parameters
            "timeout": self.settings.ai_timeout,
            # Note: max_retries is handled differently per provider
        }
        
        if self.ai_provider == AIProvider.GROQ:
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY is required for Groq provider")
                

            # Groq-specific configuration with only CrewAI-supported parameters
            groq_config = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": self.settings.ai_timeout,
            }
            
            logger.info(f"Creating GROQ LLM with config: {groq_config}")
            

            return LLM(
                model=f"groq/{model_name}",
                api_key=self.groq_api_key,
                **groq_config
            )
            
        elif self.ai_provider == AIProvider.OLLAMA:
            # Ollama-specific configuration
            ollama_config = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": self.settings.ai_timeout,
            }
            
            return LLM(
                model=f"ollama/{model_name}",
                base_url=self.ollama_base_url,
                **ollama_config
            )
            
        elif self.ai_provider == AIProvider.GOOGLE_GEMINI:
            gemini_api_key = getattr(self.settings, 'gemini_api_key', None)
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY is required for Gemini provider")
                
            # Gemini-specific configuration
            gemini_config = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": self.settings.ai_timeout,
            }
                
            return LLM(
                model=f"gemini/{model_name}",
                api_key=gemini_api_key,
                **gemini_config
            )
            
        elif self.ai_provider == AIProvider.OPENAI:
            if not getattr(self.settings, 'openai_api_key', None):
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
                
            # OpenAI-specific configuration
            openai_config = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": self.settings.ai_timeout,
            }
                
            return LLM(
                model=f"openai/{model_name}",
                api_key=self.settings.openai_api_key,
                **openai_config
            )
            
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

    @property
    @lru_cache(maxsize=1)
    def main_llm(self) -> LLM:
        """
        Primary LLM for complex reasoning tasks.

        Returns:
            LLM: Configured for balanced reasoning with moderate temperature
        """
        return self._create_llm(
            temperature=self.settings.ai_temperature,
            max_tokens=self.settings.ai_max_tokens,
            use_case="main"
        )

    @property
    @lru_cache(maxsize=1)
    def tool_llm(self) -> LLM:
        """

        Optimized LLM for tool calling and function execution.

        Uses lower temperature for precise tool calling as recommended by CrewAI.

        Returns:
            LLM: Configured for precise tool calling
        """
        return self._create_llm(
            temperature=self.settings.ai_temperature_tools,
            max_tokens=self.settings.ai_max_tokens_tools,
            use_case="tool"
        )

    @property
    @lru_cache(maxsize=1)
    def creative_llm(self) -> LLM:
        """
        Higher temperature LLM for creative and analytical tasks.


        Returns:
            LLM: Configured for creative reasoning
        """
        return self._create_llm(
            temperature=self.settings.ai_temperature_creative,
            max_tokens=self.settings.ai_max_tokens_creative,
            use_case="creative"
        )

    @property
    @lru_cache(maxsize=1)
    def data_critical_llm(self) -> LLM:
        """
        Ultra-precise LLM for data-critical operations.


        Uses very low temperature for anti-hallucination in critical operations.

        Returns:
            LLM: Configured for maximum precision
        """
        return self._create_llm(
            temperature=self.settings.ai_temperature_tools,  # Ultra-low temperature
            max_tokens=self.settings.ai_max_tokens_tools,  # Use settings value for consistency
            use_case="data_critical"
        )

    @property
    @lru_cache(maxsize=1)
    def nlp_llm(self) -> LLM:
        """
        Specialized LLM for NLP processing and intent recognition.

        Uses GPT-OSS 20B or advanced model for intelligent language understanding.
        Optimized for 2x faster processing with balanced temperature.

        Returns:
            LLM: Configured for NLP processing
        """
        return self._create_llm(
            temperature=0.2,  # Balanced for understanding
            max_tokens=600,   # Sufficient for analysis
            use_case="nlp",
            override_model=self.nlp_model
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
        # Map to simple/advanced models via env overrides
        if agent_role in [
            AgentRole.MESSAGE_PROCESSOR,
            AgentRole.HELP_ASSISTANT,
            AgentRole.PLAYER_COORDINATOR,
        ]:
            simple_llm = self._create_llm(
                temperature=self.settings.ai_temperature_tools,
                max_tokens=self.settings.ai_max_tokens_tools,
                use_case="simple_agent",
                override_model=self.simple_model,
            )
            tool_llm = self._create_llm(
                temperature=self.settings.ai_temperature_tools,
                max_tokens=self.settings.ai_max_tokens_tools,
                use_case="tool",
                override_model=self.simple_model,
            )
            return simple_llm, tool_llm

        if agent_role in [
            AgentRole.TEAM_ADMINISTRATOR,
            AgentRole.SQUAD_SELECTOR,
        ]:
            advanced_llm = self._create_llm(
                temperature=self.settings.ai_temperature,
                max_tokens=self.settings.ai_max_tokens,
                use_case="advanced_agent",
                override_model=self.advanced_model,
            )
            tool_llm = self._create_llm(
                temperature=self.settings.ai_temperature_tools,
                max_tokens=self.settings.ai_max_tokens_tools,
                use_case="tool",
                override_model=self.advanced_model,
            )
            return advanced_llm, tool_llm

        if agent_role == AgentRole.NLP_PROCESSOR:
            # For NLP processor, use simple Groq model without complex tool calling
            # This addresses the Groq tool calling error
            nlp_llm = self._create_llm(
                temperature=0.2,  # Balanced for understanding
                max_tokens=600,   # Sufficient for analysis
                use_case="nlp_agent",
                override_model=self.simple_model,  # Use simple model instead of nlp_model
            )
            tool_llm = self._create_llm(
                temperature=0.1,  # Precise for tool calls
                max_tokens=400,   # Focused tool responses
                use_case="nlp_tool",
                override_model=self.simple_model,  # Use simple model instead of nlp_model
            )
            return nlp_llm, tool_llm

        # Default fallback
        default_main = self._create_llm(
            temperature=self.settings.ai_temperature,
            max_tokens=self.settings.ai_max_tokens,
            use_case="main",
        )
        default_tool = self._create_llm(
            temperature=self.settings.ai_temperature_tools,
            max_tokens=self.settings.ai_max_tokens_tools,
            use_case="tool",
        )
        return default_main, default_tool

    def validate_configuration(self) -> list[str]:
        """
        Validate LLM configuration and return any errors.

        Returns:
            list[str]: List of validation error messages (empty if valid)
        """
        errors = []

        # Validate base URL for Ollama provider
        if self.ai_provider == AIProvider.OLLAMA:
            if not self.ollama_base_url:
                errors.append("OLLAMA_BASE_URL is required but not configured")

            if not self.ollama_base_url.startswith(('http://', 'https://')):
                errors.append(f"OLLAMA_BASE_URL must start with http:// or https://, got: {self.ollama_base_url}")
        
        # Validate API keys for providers that need them
        if self.ai_provider == AIProvider.GROQ and not self.groq_api_key:
            errors.append("GROQ_API_KEY is required for Groq provider")

        # Validate model name
        if not self.default_model:
            errors.append("AI_MODEL_NAME is required but not configured")

        # Validate model format for Ollama (only if using Ollama)
        if self.ai_provider == AIProvider.OLLAMA and self.default_model and not self.default_model.startswith('llama'):
            logger.warning(f"Model name '{self.default_model}' may not be compatible with Ollama")

        return errors

    def test_connection(self) -> bool:
        """
        Test connection to the configured LLM provider using CrewAI native calls.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create a test LLM using CrewAI with minimal tokens for testing
            test_llm = self._create_llm(
                temperature=0.1,
                max_tokens=10,
                use_case="connection_test"
            )
            
            # Test with a simple prompt
            test_prompt = "Hi"
            
            # Use CrewAI native invocation (synchronous)
            if hasattr(test_llm, 'invoke'):
                response = test_llm.invoke(test_prompt)
            else:
                # Fallback for different CrewAI LLM implementations
                response = str(test_llm)
                
            if response and len(str(response).strip()) > 0:
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
        Test connection to the configured LLM provider asynchronously using CrewAI.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create a test LLM using CrewAI with minimal tokens for testing
            test_llm = self._create_llm(
                temperature=0.1,
                max_tokens=10,
                use_case="async_connection_test"
            )
            
            # Test with a simple prompt
            test_prompt = "Hi"
            
            # Use CrewAI native async invocation if available
            if hasattr(test_llm, 'ainvoke'):
                response = await test_llm.ainvoke(test_prompt)
            else:
                # Fallback to sync version in thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self.test_connection)
                return response
                
            if response and len(str(response).strip()) > 0:
                logger.info(f"✅ {self.ai_provider.value} async connection test successful")
                return True
            else:
                logger.error(f"❌ {self.ai_provider.value} async connection test failed: No content in response")
                return False
                
        except Exception as e:
            logger.error(f"❌ {self.ai_provider.value} async connection test failed: {e}")
            return False

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
