"""Agent-specific model configurations for different providers."""

from kickai.core.enums import AgentRole, AIProvider

# Agent-specific model mappings
AGENT_MODEL_CONFIG = {
    # Data-Critical Agents (Anti-hallucination priority)
    AgentRole.PLAYER_COORDINATOR: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 500,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.1, "max_tokens": 500},
    },
    AgentRole.MESSAGE_PROCESSOR: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 300,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.1, "max_tokens": 300},
    },
    AgentRole.HELP_ASSISTANT: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 800,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.1, "max_tokens": 800},
    },
    AgentRole.FINANCE_MANAGER: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "temperature": 0.1,
            "max_tokens": 400,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.1, "max_tokens": 400},
    },
    # Administrative Agents
    AgentRole.TEAM_MANAGER: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",  # Use 1.5B since 3B not available
            "temperature": 0.3,
            "max_tokens": 600,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.3, "max_tokens": 600},
    },
    AgentRole.AVAILABILITY_MANAGER: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",  # Use 1.5B since 3B not available
            "temperature": 0.3,
            "max_tokens": 500,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.3, "max_tokens": 500},
    },
    # Onboarding Agent
    AgentRole.ONBOARDING_AGENT: {
        AIProvider.HUGGINGFACE: {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",  # Use 1.5B since 3B not available
            "temperature": 0.2,
            "max_tokens": 700,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.2, "max_tokens": 700},
    },
    # Creative/Analytical Agents
    AgentRole.PERFORMANCE_ANALYST: {
        AIProvider.HUGGINGFACE: {
            "model": "google/gemma-2-2b-it",
            "temperature": 0.7,
            "max_tokens": 1000,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.7, "max_tokens": 1000},
    },
    AgentRole.LEARNING_AGENT: {
        AIProvider.HUGGINGFACE: {
            "model": "google/gemma-2-2b-it",
            "temperature": 0.7,
            "max_tokens": 800,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.7, "max_tokens": 800},
    },
    AgentRole.SQUAD_SELECTOR: {
        AIProvider.HUGGINGFACE: {
            "model": "google/gemma-2-2b-it",
            "temperature": 0.7,
            "max_tokens": 600,
        },
        AIProvider.GEMINI: {"model": "gemini-1.5-flash", "temperature": 0.7, "max_tokens": 600},
    },
}


def get_agent_model_config(agent_role: AgentRole, provider: AIProvider) -> dict | None:
    """Get model configuration for specific agent and provider."""
    return AGENT_MODEL_CONFIG.get(agent_role, {}).get(provider)


def get_fallback_config(agent_role: AgentRole) -> dict:
    """Get fallback configuration (Gemini) for any agent."""
    gemini_config = AGENT_MODEL_CONFIG.get(agent_role, {}).get(AIProvider.GEMINI)
    if gemini_config:
        return gemini_config

    # Default fallback
    return {"model": "gemini-1.5-flash", "temperature": 0.3, "max_tokens": 500}


def get_all_agent_configs() -> dict[AgentRole, dict[AIProvider, dict]]:
    """Get all agent configurations for validation."""
    return AGENT_MODEL_CONFIG


def validate_agent_configs() -> dict[str, bool]:
    """Validate that all agents have proper configurations."""
    validation_results = {}

    for agent_role in AgentRole:
        agent_name = agent_role.value

        # Check if agent has HuggingFace config
        hf_config = get_agent_model_config(agent_role, AIProvider.HUGGINGFACE)
        gemini_config = get_agent_model_config(agent_role, AIProvider.GEMINI)

        validation_results[f"{agent_name}_has_hf_config"] = hf_config is not None
        validation_results[f"{agent_name}_has_gemini_config"] = gemini_config is not None

        # Validate config structure if exists
        if hf_config:
            required_fields = ["model", "temperature", "max_tokens"]
            validation_results[f"{agent_name}_hf_config_complete"] = all(
                field in hf_config for field in required_fields
            )

        if gemini_config:
            required_fields = ["model", "temperature", "max_tokens"]
            validation_results[f"{agent_name}_gemini_config_complete"] = all(
                field in gemini_config for field in required_fields
            )

    return validation_results
