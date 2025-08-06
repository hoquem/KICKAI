"""
Agent-specific constants for KICKAI.

This module contains constants related to AI agents, LLM configuration,
and agent system behavior.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConstants:
    """Agent system configuration constants."""

    # LLM Temperature Settings
    DATA_CRITICAL_TEMPERATURE: float = 0.1
    ADMINISTRATIVE_TEMPERATURE: float = 0.3
    CREATIVE_TEMPERATURE: float = 0.7
    FALLBACK_TEMPERATURE: float = 0.5

    # Token Limits
    DATA_CRITICAL_MAX_TOKENS: int = 800
    ADMINISTRATIVE_MAX_TOKENS: int = 1200
    CREATIVE_MAX_TOKENS: int = 2000
    FALLBACK_MAX_TOKENS: int = 1000

    # Agent Execution Limits
    MAX_AGENT_ITERATIONS: int = 10
    DATA_CRITICAL_MAX_ITERATIONS: int = 1
    ADMINISTRATIVE_MAX_ITERATIONS: int = 3
    CREATIVE_MAX_ITERATIONS: int = 5

    # Timeouts (in seconds)
    AGENT_EXECUTION_TIMEOUT: int = 60
    DATA_CRITICAL_TIMEOUT: int = 30
    ADMINISTRATIVE_TIMEOUT: int = 45
    CREATIVE_TIMEOUT: int = 60

    # Tool Execution
    MAX_TOOL_EXECUTION_TIME: int = 30
    MAX_TOOLS_PER_AGENT: int = 20
    MAX_TOOL_RETRIES: int = 2

    # Agent System
    MAX_CONCURRENT_AGENTS: int = 5
    AGENT_POOL_SIZE: int = 10
    AGENT_CLEANUP_INTERVAL: int = 300  # 5 minutes

    # Memory Settings
    ENABLE_AGENT_MEMORY: bool = True
    MEMORY_CONTEXT_WINDOW: int = 10
    MEMORY_RETENTION_HOURS: int = 24

    # CrewAI Settings
    CREW_VERBOSE_MODE: bool = True
    CREW_MAX_EXECUTION_TIME: int = 120
    CREW_ALLOW_DELEGATION: bool = True

    # Model Names by Provider
    OLLAMA_DATA_CRITICAL_MODEL: str = "llama3.2:1b"
    OLLAMA_ADMINISTRATIVE_MODEL: str = "llama3.2:3b"
    OLLAMA_CREATIVE_MODEL: str = "llama3.2:3b"

    HUGGINGFACE_DATA_CRITICAL_MODEL: str = "microsoft/DialoGPT-small"
    HUGGINGFACE_ADMINISTRATIVE_MODEL: str = "microsoft/DialoGPT-medium"
    HUGGINGFACE_CREATIVE_MODEL: str = "microsoft/DialoGPT-large"

    GEMINI_DATA_CRITICAL_MODEL: str = "gemini-1.5-flash"
    GEMINI_ADMINISTRATIVE_MODEL: str = "gemini-1.5-flash"
    GEMINI_CREATIVE_MODEL: str = "gemini-1.5-pro"

    OPENAI_DATA_CRITICAL_MODEL: str = "gpt-3.5-turbo"
    OPENAI_ADMINISTRATIVE_MODEL: str = "gpt-3.5-turbo"
    OPENAI_CREATIVE_MODEL: str = "gpt-4"

    @classmethod
    def get_data_critical_agent_roles(cls) -> list[str]:
        """Get list of agent roles that require data-critical configuration."""
        return [
            "player_coordinator",
            "help_assistant",
            "message_processor",
            "finance_manager",
        ]

    @classmethod
    def get_administrative_agent_roles(cls) -> list[str]:
        """Get list of agent roles that use administrative configuration."""
        return [
            "team_manager",
            "availability_manager",
            "squad_selector",
            "training_coordinator",
        ]

    @classmethod
    def get_creative_agent_roles(cls) -> list[str]:
        """Get list of agent roles that use creative configuration."""
        return [
            "performance_analyst",
            "learning_agent",
            "communication_manager",
            "command_fallback_agent",
        ]

    @classmethod
    def get_model_for_provider_and_type(cls, provider: str, agent_type: str) -> str:
        """
        Get model name for specific provider and agent type.

        Args:
            provider: AI provider (ollama, huggingface, gemini, openai)
            agent_type: Agent type (data_critical, administrative, creative)

        Returns:
            Model name for the provider and type
        """
        model_map = {
            "ollama": {
                "data_critical": cls.OLLAMA_DATA_CRITICAL_MODEL,
                "administrative": cls.OLLAMA_ADMINISTRATIVE_MODEL,
                "creative": cls.OLLAMA_CREATIVE_MODEL,
            },
            "huggingface": {
                "data_critical": cls.HUGGINGFACE_DATA_CRITICAL_MODEL,
                "administrative": cls.HUGGINGFACE_ADMINISTRATIVE_MODEL,
                "creative": cls.HUGGINGFACE_CREATIVE_MODEL,
            },
            "gemini": {
                "data_critical": cls.GEMINI_DATA_CRITICAL_MODEL,
                "administrative": cls.GEMINI_ADMINISTRATIVE_MODEL,
                "creative": cls.GEMINI_CREATIVE_MODEL,
            },
            "openai": {
                "data_critical": cls.OPENAI_DATA_CRITICAL_MODEL,
                "administrative": cls.OPENAI_ADMINISTRATIVE_MODEL,
                "creative": cls.OPENAI_CREATIVE_MODEL,
            },
        }

        provider_models = model_map.get(provider.lower(), {})
        return provider_models.get(agent_type, cls.OLLAMA_ADMINISTRATIVE_MODEL)

    @classmethod
    def get_agent_configuration(cls, agent_role: str) -> dict[str, any]:
        """
        Get complete configuration for an agent role.

        Args:
            agent_role: The agent role name

        Returns:
            Configuration dictionary
        """
        if agent_role in cls.get_data_critical_agent_roles():
            return {
                "temperature": cls.DATA_CRITICAL_TEMPERATURE,
                "max_tokens": cls.DATA_CRITICAL_MAX_TOKENS,
                "max_iterations": cls.DATA_CRITICAL_MAX_ITERATIONS,
                "timeout": cls.DATA_CRITICAL_TIMEOUT,
                "memory_enabled": False,  # Disable for anti-hallucination
            }
        elif agent_role in cls.get_administrative_agent_roles():
            return {
                "temperature": cls.ADMINISTRATIVE_TEMPERATURE,
                "max_tokens": cls.ADMINISTRATIVE_MAX_TOKENS,
                "max_iterations": cls.ADMINISTRATIVE_MAX_ITERATIONS,
                "timeout": cls.ADMINISTRATIVE_TIMEOUT,
                "memory_enabled": True,
            }
        elif agent_role in cls.get_creative_agent_roles():
            return {
                "temperature": cls.CREATIVE_TEMPERATURE,
                "max_tokens": cls.CREATIVE_MAX_TOKENS,
                "max_iterations": cls.CREATIVE_MAX_ITERATIONS,
                "timeout": cls.CREATIVE_TIMEOUT,
                "memory_enabled": True,
            }
        else:
            # Fallback configuration
            return {
                "temperature": cls.FALLBACK_TEMPERATURE,
                "max_tokens": cls.FALLBACK_MAX_TOKENS,
                "max_iterations": cls.ADMINISTRATIVE_MAX_ITERATIONS,
                "timeout": cls.ADMINISTRATIVE_TIMEOUT,
                "memory_enabled": True,
            }
