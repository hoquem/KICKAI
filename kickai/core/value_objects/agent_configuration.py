"""
Agent configuration value objects.

These value objects encapsulate agent configuration with type safety and validation.
"""

from __future__ import annotations

from dataclasses import dataclass

from kickai.core.enums import AgentRole, AIProvider


@dataclass(frozen=True)
class LLMConfiguration:
    """Configuration for LLM settings."""

    provider: AIProvider
    model_name: str
    temperature: float
    timeout_seconds: int
    max_retries: int
    max_tokens: int | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")

        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")

        if not self.model_name.strip():
            raise ValueError("Model name cannot be empty")

    @classmethod
    def for_data_critical_agent(cls, provider: AIProvider = AIProvider.OLLAMA) -> LLMConfiguration:
        """Create configuration optimized for data-critical agents (anti-hallucination)."""
        from kickai.core.config import get_settings

        settings = get_settings()

        model_map = {
            AIProvider.OLLAMA: "llama3.2:1b",
            AIProvider.HUGGINGFACE: "microsoft/DialoGPT-small",
            AIProvider.GEMINI: "gemini-1.5-flash",
            AIProvider.OPENAI: "gpt-3.5-turbo",
        }

        return cls(
            provider=provider,
            model_name=model_map.get(provider, "llama3.2:1b"),
            temperature=0.1,  # Low temperature for consistency
            timeout_seconds=30,
            max_retries=3,
            max_tokens=settings.ai_max_tokens_tools,  # Use settings value
        )

    @classmethod
    def for_administrative_agent(cls, provider: AIProvider = AIProvider.OLLAMA) -> LLMConfiguration:
        """Create configuration for administrative agents (balanced reasoning)."""
        from kickai.core.config import get_settings

        settings = get_settings()

        model_map = {
            AIProvider.OLLAMA: "llama3.2:3b",
            AIProvider.HUGGINGFACE: "microsoft/DialoGPT-medium",
            AIProvider.GEMINI: "gemini-1.5-flash",
            AIProvider.OPENAI: "gpt-3.5-turbo",
        }

        return cls(
            provider=provider,
            model_name=model_map.get(provider, "llama3.2:3b"),
            temperature=0.3,  # Moderate temperature
            timeout_seconds=45,
            max_retries=2,
            max_tokens=settings.ai_max_tokens,  # Use settings value
        )

    @classmethod
    def for_creative_agent(cls, provider: AIProvider = AIProvider.OLLAMA) -> LLMConfiguration:
        """Create configuration for creative agents (analytical and creative tasks)."""
        from kickai.core.config import get_settings

        settings = get_settings()

        model_map = {
            AIProvider.OLLAMA: "llama3.2:3b",
            AIProvider.HUGGINGFACE: "microsoft/DialoGPT-large",
            AIProvider.GEMINI: "gemini-1.5-pro",
            AIProvider.OPENAI: "gpt-4",
        }

        return cls(
            provider=provider,
            model_name=model_map.get(provider, "llama3.2:3b"),
            temperature=0.7,  # Higher temperature for creativity
            timeout_seconds=60,
            max_retries=2,
            max_tokens=settings.ai_max_tokens_creative,  # Use settings value
        )


@dataclass(frozen=True)
class AgentConfiguration:
    """Complete configuration for a CrewAI agent."""

    role: AgentRole
    llm_config: LLMConfiguration
    max_iterations: int = 10
    allow_delegation: bool = True
    verbose: bool = True
    memory_enabled: bool = True
    learning_enabled: bool = True

    def __post_init__(self) -> None:
        if self.max_iterations <= 0:
            raise ValueError("Max iterations must be positive")

    @classmethod
    def for_role(
        cls, role: AgentRole, provider: AIProvider = AIProvider.OLLAMA
    ) -> AgentConfiguration:
        """Create appropriate configuration for a given agent role."""

        # Data-critical agents (require high precision, low hallucination)
        data_critical_roles = {
            AgentRole.PLAYER_COORDINATOR,
            AgentRole.HELP_ASSISTANT,
            AgentRole.MESSAGE_PROCESSOR,
        }

        # Administrative agents (need balanced reasoning)
        administrative_roles = {
            AgentRole.TEAM_ADMINISTRATOR,
            AgentRole.SQUAD_SELECTOR,
        }

        # Creative agents (benefit from higher creativity)
        creative_roles = {
            AgentRole.SQUAD_SELECTOR,
        }

        if role in data_critical_roles:
            llm_config = LLMConfiguration.for_data_critical_agent(provider)
            # Data-critical agents should have limited iterations to prevent elaboration
            max_iterations = 1
            memory_enabled = True  # Enable memory for persistent crew continuity
        elif role in administrative_roles:
            llm_config = LLMConfiguration.for_administrative_agent(provider)
            max_iterations = 3
            memory_enabled = True
        elif role in creative_roles:
            llm_config = LLMConfiguration.for_creative_agent(provider)
            max_iterations = 5
            memory_enabled = True
        else:
            # Default to administrative configuration
            llm_config = LLMConfiguration.for_administrative_agent(provider)
            max_iterations = 3
            memory_enabled = True

        return cls(
            role=role,
            llm_config=llm_config,
            max_iterations=max_iterations,
            allow_delegation=True,
            verbose=True,
            memory_enabled=memory_enabled,
            learning_enabled=True,
        )

    def with_llm_config(self, llm_config: LLMConfiguration) -> AgentConfiguration:
        """Create new configuration with updated LLM config."""
        return AgentConfiguration(
            role=self.role,
            llm_config=llm_config,
            max_iterations=self.max_iterations,
            allow_delegation=self.allow_delegation,
            verbose=self.verbose,
            memory_enabled=self.memory_enabled,
            learning_enabled=self.learning_enabled,
        )

    def with_iterations(self, max_iterations: int) -> AgentConfiguration:
        """Create new configuration with updated max iterations."""
        return AgentConfiguration(
            role=self.role,
            llm_config=self.llm_config,
            max_iterations=max_iterations,
            allow_delegation=self.allow_delegation,
            verbose=self.verbose,
            memory_enabled=self.memory_enabled,
            learning_enabled=self.learning_enabled,
        )


@dataclass(frozen=True)
class SystemConfiguration:
    """System-wide configuration constants."""

    # Default timeouts
    DEFAULT_AGENT_TIMEOUT_SECONDS: int = 30
    DEFAULT_TOOL_TIMEOUT_SECONDS: int = 10
    DEFAULT_DATABASE_TIMEOUT_SECONDS: int = 15

    # Retry settings
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_RETRY_DELAY_SECONDS: float = 1.0

    # Performance settings
    MAX_CONCURRENT_AGENTS: int = 5
    MAX_TOOL_EXECUTION_TIME_SECONDS: int = 60

    # Validation settings
    MIN_PHONE_LENGTH: int = 10
    MAX_PHONE_LENGTH: int = 15
    MAX_NAME_LENGTH: int = 100
    MAX_MESSAGE_LENGTH: int = 4096

    # Security settings
    MAX_LOGIN_ATTEMPTS: int = 5
    SESSION_TIMEOUT_MINUTES: int = 60

    def __post_init__(self) -> None:
        # Validate configuration values
        if self.DEFAULT_AGENT_TIMEOUT_SECONDS <= 0:
            raise ValueError("Agent timeout must be positive")

        if self.DEFAULT_MAX_RETRIES < 0:
            raise ValueError("Max retries cannot be negative")

        if self.MAX_CONCURRENT_AGENTS <= 0:
            raise ValueError("Max concurrent agents must be positive")

    @classmethod
    def default(cls) -> SystemConfiguration:
        """Create default system configuration."""
        return cls()

    @classmethod
    def production(cls) -> SystemConfiguration:
        """Create production-optimized configuration."""
        return cls(
            DEFAULT_AGENT_TIMEOUT_SECONDS=45,
            DEFAULT_TOOL_TIMEOUT_SECONDS=15,
            DEFAULT_DATABASE_TIMEOUT_SECONDS=20,
            MAX_CONCURRENT_AGENTS=10,
        )

    @classmethod
    def development(cls) -> SystemConfiguration:
        """Create development-friendly configuration."""
        return cls(
            DEFAULT_AGENT_TIMEOUT_SECONDS=60,
            DEFAULT_TOOL_TIMEOUT_SECONDS=30,
            DEFAULT_DATABASE_TIMEOUT_SECONDS=30,
            MAX_CONCURRENT_AGENTS=3,
        )
