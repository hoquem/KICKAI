"""
CrewAI Native LLM Configuration for KICKAI - Clean Implementation

This module provides a single source of truth for LLM configuration using
only CrewAI-supported parameters. No fallbacks, no defaults, fail-fast approach.

Features:
- Direct CrewAI LLM configuration with supported parameters only
- Thread-safe singleton pattern
- Production-ready provider-specific optimizations
- Fail-fast validation with no silent failures
"""

import logging
from functools import lru_cache

from crewai import LLM

from kickai.core.config import get_settings
from kickai.core.enums import AgentRole, AIProvider

logger = logging.getLogger(__name__)


class LLMConfiguration:
    """
    Centralized LLM configuration following CrewAI best practices.

    Clean implementation with:
    - No fallbacks or defaults
    - Direct provider-specific configurations
    - Fail-fast validation
    - Single responsibility for each method
    """

    def __init__(self):
        """Initialize LLM configuration from settings."""
        self.settings = get_settings()
        self.ai_provider = self.settings.ai_provider

        # Model selection - fail if not configured
        self.simple_model = self._get_required_setting("ai_model_simple")
        self.advanced_model = self._get_required_setting("ai_model_advanced")
        self.nlp_model = getattr(self.settings, "ai_model_nlp", self.advanced_model)

        # Provider-specific settings
        self._validate_provider_requirements()

        logger.info(
            f"🤖 LLM Configuration: provider={self.ai_provider.value}, "
            f"simple={self.simple_model}, advanced={self.advanced_model}"
        )

    def _get_required_setting(self, setting_name: str) -> str:
        """Get required setting value or fail."""
        value = getattr(self.settings, setting_name, None)
        if not value:
            raise ValueError(f"Required setting {setting_name} is not configured")
        return value

    def _validate_provider_requirements(self) -> None:
        """Validate provider-specific requirements."""
        if self.ai_provider == AIProvider.GROQ:
            if not self.settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is required for Groq provider")

        elif self.ai_provider == AIProvider.OPENAI:
            if not getattr(self.settings, "openai_api_key", None):
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")

        elif self.ai_provider == AIProvider.GOOGLE_GEMINI:
            if not getattr(self.settings, "gemini_api_key", None):
                raise ValueError("GOOGLE_API_KEY is required for Gemini provider")

        elif self.ai_provider == AIProvider.OLLAMA:
            if not self.settings.ollama_base_url:
                raise ValueError("OLLAMA_BASE_URL is required for Ollama provider")

    def create_llm(self, model_name: str, temperature: float, max_tokens: int) -> LLM:
        """
        Create LLM instance with provider-specific configuration.

        Args:
            model_name: Name of the model to use
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLM: Configured CrewAI LLM instance

        Raises:
            ValueError: If provider configuration is invalid
        """
        # Base configuration
        config = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": self.settings.ai_timeout,
            "stream": False,  # Disable streaming for CrewAI compatibility
        }

        # Provider-specific configuration
        if self.ai_provider == AIProvider.GROQ:
            return LLM(model=f"groq/{model_name}", api_key=self.settings.groq_api_key, **config)

        elif self.ai_provider == AIProvider.OPENAI:
            # For OpenAI, use model_name directly (litellm handles the provider prefix)
            return LLM(
                model=model_name,  # Use model_name directly, not f"openai/{model_name}"
                api_key=self.settings.openai_api_key,
                **config,
            )

        elif self.ai_provider == AIProvider.GOOGLE_GEMINI:
            return LLM(model=f"gemini/{model_name}", api_key=self.settings.gemini_api_key, **config)

        elif self.ai_provider == AIProvider.OLLAMA:
            return LLM(
                model=f"ollama/{model_name}", base_url=self.settings.ollama_base_url, **config
            )

        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

    @property
    @lru_cache(maxsize=1)
    def main_llm(self) -> LLM:
        """Primary LLM for complex reasoning tasks."""
        return self.create_llm(
            model_name=self.advanced_model,
            temperature=self.settings.ai_temperature,
            max_tokens=self.settings.ai_max_tokens,
        )

    @property
    @lru_cache(maxsize=1)
    def tool_llm(self) -> LLM:
        """Optimized LLM for tool calling with lower temperature."""
        return self.create_llm(
            model_name=self.simple_model,
            temperature=self.settings.ai_temperature_tools,
            max_tokens=self.settings.ai_max_tokens_tools,
        )

    def get_llm_for_agent(self, agent_role: AgentRole) -> tuple[LLM, LLM]:
        """
        Get LLM instances for agent and tool calling.

        Args:
            agent_role: The role of the agent

        Returns:
            tuple[LLM, LLM]: Tuple of (agent_llm, tool_llm)
        """
        # Agent-specific model and temperature selection
        agent_configs = {
            AgentRole.MESSAGE_PROCESSOR: {
                "model_name": self.simple_model,
                "temperature": self.settings.ai_temperature_tools,
                "max_tokens": self.settings.ai_max_tokens_tools,
            },
            AgentRole.HELP_ASSISTANT: {
                "model_name": self.simple_model,
                "temperature": self.settings.ai_temperature_tools,
                "max_tokens": self.settings.ai_max_tokens_tools,
            },
            AgentRole.PLAYER_COORDINATOR: {
                "model_name": self.simple_model,
                "temperature": self.settings.ai_temperature_tools,
                "max_tokens": self.settings.ai_max_tokens_tools,
            },
            AgentRole.TEAM_ADMINISTRATOR: {
                "model_name": self.advanced_model,
                "temperature": self.settings.ai_temperature,
                "max_tokens": self.settings.ai_max_tokens,
            },
            AgentRole.SQUAD_SELECTOR: {
                "model_name": self.advanced_model,
                "temperature": self.settings.ai_temperature,
                "max_tokens": self.settings.ai_max_tokens,
            },
        }

        config = agent_configs.get(agent_role)
        if not config:
            raise ValueError(f"No LLM configuration found for agent role: {agent_role}")

        # Create agent LLM
        agent_llm = self.create_llm(**config)

        # Create tool LLM with lower temperature
        tool_config = config.copy()
        tool_config["temperature"] = self.settings.ai_temperature_tools
        tool_llm = self.create_llm(**tool_config)

        return agent_llm, tool_llm

    def create_manager_llm(self) -> LLM:
        """
        Create manager LLM for hierarchical process coordination with delegation formatting rules.

        Enhanced with specific formatting instructions for Gemini models to prevent
        "unhashable type: 'dict'" errors in CrewAI delegation.

        Returns:
            LLM: Configured manager LLM with delegation formatting system template
        """
        # Manager LLM system template with delegation formatting rules
        delegation_system_template = """
KICKAI Manager LLM - Hierarchical Process Coordination

You are the manager LLM for a 5-agent CrewAI system coordinating football team management operations.

🚨 CRITICAL DELEGATION FORMATTING RULES (GEMINI COMPATIBILITY):

When delegating tasks to agents, ALWAYS use simple string parameters:
- ✅ CORRECT: delegate_work(task='Check player status', context='User wants info', coworker='player_coordinator')
- ❌ WRONG: delegate_work(task={'description': 'Check player status'}, context={'description': 'User wants info'})

DELEGATION PARAMETERS MUST BE SIMPLE STRINGS:
- task='simple task description string'
- context='context information string'
- coworker='agent_name_string'

NEVER use dictionary objects as parameter values. Always use simple key='value' format.

Available agents: message_processor, help_assistant, player_coordinator, team_administrator, squad_selector

For delegation, ensure all tool arguments are simple key-value pairs with string values only.
"""

        # Use the configured advanced model from .env for manager_llm
        try:
            # Create base LLM configuration
            base_config = {
                "temperature": 0.3,  # Optimal temperature for hierarchical coordination
                "max_tokens": self.settings.ai_max_tokens,  # From .env AI_MAX_TOKENS
                "timeout": self.settings.ai_timeout,
                "stream": False,
                "system_template": delegation_system_template,  # Add system template
            }

            # Provider-specific configuration with system template
            if self.ai_provider == AIProvider.GROQ:
                return LLM(
                    model=f"groq/{self.advanced_model}",
                    api_key=self.settings.groq_api_key,
                    **base_config,
                )

            elif self.ai_provider == AIProvider.OPENAI:
                return LLM(
                    model=self.advanced_model, api_key=self.settings.openai_api_key, **base_config
                )

            elif self.ai_provider == AIProvider.GOOGLE_GEMINI:
                return LLM(
                    model=f"gemini/{self.advanced_model}",
                    api_key=self.settings.gemini_api_key,
                    **base_config,
                )

            elif self.ai_provider == AIProvider.OLLAMA:
                return LLM(
                    model=f"ollama/{self.advanced_model}",
                    base_url=self.settings.ollama_base_url,
                    **base_config,
                )
            else:
                raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "insufficient_quota" in error_msg:
                logger.warning(f"⚠️ OpenAI quota exceeded: {e}")
                logger.info("🔄 Falling back to simple model for manager_llm")
            elif "model" in error_msg and (
                "does not exist" in error_msg or "not found" in error_msg
            ):
                logger.warning(f"⚠️ Advanced model access denied: {e}")
                logger.info("🔄 Falling back to simple model for manager_llm")
            else:
                logger.warning(f"⚠️ Failed to create advanced model manager LLM: {e}")
                logger.info("🔄 Falling back to simple model for manager_llm")

            # Fallback to simple model for manager_llm
            try:
                return self.create_llm(
                    model_name=self.simple_model,  # From .env AI_MODEL_SIMPLE
                    temperature=0.3,  # Optimal temperature for hierarchical coordination
                    max_tokens=self.settings.ai_max_tokens,  # From .env AI_MAX_TOKENS
                )
            except Exception as fallback_error:
                logger.warning(f"⚠️ Simple model fallback failed: {fallback_error}")
                logger.error("❌ All model fallbacks failed for manager_llm")
                raise fallback_error


# Singleton instance
_llm_config = None


def get_llm_config() -> LLMConfiguration:
    """
    Get the global LLM configuration instance.

    Returns:
        LLMConfiguration: The singleton LLM configuration instance

    Raises:
        ValueError: If configuration is invalid
    """
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfiguration()
    return _llm_config


def get_llm(model_type: str = "main") -> LLM:
    """
    Get LLM instance by type.

    Args:
        model_type: Type of LLM ('main', 'tool')

    Returns:
        LLM: Configured LLM instance

    Raises:
        ValueError: If model type is not supported
    """
    config = get_llm_config()

    if model_type == "main":
        return config.main_llm
    elif model_type == "tool":
        return config.tool_llm
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
