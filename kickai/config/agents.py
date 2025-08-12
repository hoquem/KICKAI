"""
YAML-based Agent Configuration Manager

This module loads agent configurations from agents.yaml and provides
template processing and context variable substitution with performance optimizations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from loguru import logger

from kickai.core.enums import AgentRole


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    role: AgentRole
    goal: str
    backstory: str
    tools: list[str] = field(default_factory=list)
    enabled: bool = True
    max_iterations: int = 10
    allow_delegation: bool = True
    verbose: bool = True
    temperature: float = 0.3  # Default from settings.ai_temperature
    max_tokens: int = 800  # Use default from settings.ai_max_tokens
    primary_entity_type: Optional[str] = None
    entity_types: list[str] = field(default_factory=list)


class YAMLAgentConfigurationManager:
    """Manages agent configurations loaded from YAML with template processing and performance optimizations."""

    def __init__(self, yaml_path: str = "kickai/config/agents.yaml"):
        self.yaml_path = Path(yaml_path)
        self._config_data = None
        self._processed_configs = {}
        self._load_yaml_config()
        logger.info(f"✅ YAMLAgentConfigurationManager initialized with {self.yaml_path}")

    def _load_yaml_config(self):
        """Load and parse the YAML configuration file."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Agent configuration file not found: {self.yaml_path}")

        try:
            with open(self.yaml_path, encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f)
            logger.info(f"✅ Loaded agent configuration from {self.yaml_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load agent configuration from {self.yaml_path}: {e}")
            raise

    def _process_templates(self, text: str, context: dict[str, Any]) -> str:
        """Process template variables and shared templates with performance optimizations."""
        if not text:
            return text

        # Add current date if not provided
        if "current_date" not in context:
            context["current_date"] = datetime.now().strftime("%Y-%m-%d")

        # Process template variables
        for var_name, var_value in context.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(var_value))

        # Process shared templates
        shared_templates = self._config_data.get("shared_templates", {})

        # Process shared_backstory template
        if "{{ shared_backstory }}" in text:
            shared_backstory = shared_templates.get("shared_backstory", "")
            shared_backstory = self._process_templates(shared_backstory, context)
            text = text.replace("{{ shared_backstory }}", shared_backstory)

        # Process team_context template
        if "{{ team_context }}" in text:
            team_context = shared_templates.get("team_context", "")
            team_context = self._process_templates(team_context, context)
            text = text.replace("{{ team_context }}", team_context)

        # Process chat_type_rules template
        if "{{ chat_type_rules }}" in text:
            chat_type_rules = shared_templates.get("chat_type_rules", "")
            chat_type_rules = self._process_templates(chat_type_rules, context)
            text = text.replace("{{ chat_type_rules }}", chat_type_rules)

        # Process performance_optimizations template
        if "{{ performance_optimizations }}" in text:
            performance_optimizations = shared_templates.get("performance_optimizations", "")
            performance_optimizations = self._process_templates(performance_optimizations, context)
            text = text.replace("{{ performance_optimizations }}", performance_optimizations)

        return text

    def _get_agent_optimization_rules(self, agent_name: str) -> str:
        """Get agent-specific optimization rules based on agent type."""
        agent_optimizations = self._config_data.get("agent_optimizations", {})

        # Determine agent type based on name
        if agent_name in ["message_processor", "player_coordinator", "help_assistant"]:
            return agent_optimizations.get("data_critical_agents", {}).get("optimization_rules", "")
        elif agent_name in ["team_administration", "availability_manager", "communication_manager"]:
            return agent_optimizations.get("administrative_agents", {}).get("optimization_rules", "")
        elif agent_name in ["squad_selector", "performance_analyst"]:
            return agent_optimizations.get("creative_agents", {}).get("optimization_rules", "")
        else:
            return ""  # Default for other agents

    def _get_agent_temperature(self, agent_name: str) -> float:
        """Get agent-specific temperature setting."""
        from kickai.core.config import get_settings
        settings = get_settings()
        
        agent_optimizations = self._config_data.get("agent_optimizations", {})

        # Determine agent type based on name and use settings values
        if agent_name in ["message_processor", "player_coordinator", "help_assistant"]:
            return agent_optimizations.get("data_critical_agents", {}).get("temperature", settings.ai_temperature_tools)
        elif agent_name in ["team_administration", "availability_manager", "communication_manager"]:
            return agent_optimizations.get("administrative_agents", {}).get("temperature", settings.ai_temperature)
        elif agent_name in ["squad_selector", "performance_analyst"]:
            return agent_optimizations.get("creative_agents", {}).get("temperature", settings.ai_temperature_creative)
        else:
            return settings.ai_temperature  # Default temperature from settings

    def _get_agent_max_tokens(self, agent_name: str) -> int:
        """Get agent-specific max_tokens setting."""
        from kickai.core.config import get_settings
        settings = get_settings()
        
        agent_optimizations = self._config_data.get("agent_optimizations", {})

        # Determine agent type based on name and use settings values
        if agent_name in ["message_processor", "player_coordinator", "help_assistant"]:
            return agent_optimizations.get("data_critical_agents", {}).get("max_tokens", settings.ai_max_tokens_tools)
        elif agent_name in ["team_administration", "availability_manager", "communication_manager"]:
            return agent_optimizations.get("administrative_agents", {}).get("max_tokens", settings.ai_max_tokens)
        elif agent_name in ["squad_selector", "performance_analyst"]:
            return agent_optimizations.get("creative_agents", {}).get("max_tokens", settings.ai_max_tokens_creative)
        else:
            return settings.ai_max_tokens  # Default max_tokens from settings

    def get_agent_config(self, role: AgentRole, context: dict[str, Any]) -> AgentConfig:
        """Get agent configuration with processed templates and performance optimizations."""
        agent_name = role.value

        # Create cache key based on role and context
        context_key = hash(str(context))
        cache_key = f"{agent_name}_{context_key}"

        # Check if config is already cached
        if cache_key in self._processed_configs:
            logger.debug(f"✅ Using cached config for {agent_name}")
            return self._processed_configs[cache_key]

        if not self._config_data or "agents" not in self._config_data:
            raise ValueError("No agents configuration found in YAML file")

        # Find agent data in the list
        agent_data = None
        for agent in self._config_data["agents"]:
            if agent.get("name") == agent_name:
                agent_data = agent
                break
                
        if agent_data is None:
            raise ValueError(f"Agent '{agent_name}' not found in configuration")

        # Process templates with context
        processed_role = self._process_templates(agent_data["role"], context)
        processed_goal = self._process_templates(agent_data["goal"], context)
        processed_backstory = self._process_templates(agent_data["backstory"], context)

        # Get agent-specific settings
        temperature = agent_data.get("temperature", self._get_agent_temperature(agent_name))
        max_tokens = agent_data.get("max_tokens", self._get_agent_max_tokens(agent_name))

        # Add agent-specific optimization rules to backstory if not already present
        optimization_rules = self._get_agent_optimization_rules(agent_name)
        if optimization_rules and "🚨" not in processed_backstory:
            processed_backstory += f"\n\n{optimization_rules}"

        config = AgentConfig(
            role=role,
            goal=processed_goal,
            backstory=processed_backstory,
            tools=agent_data.get("tools", []),
            enabled=agent_data.get("enabled", True),
            max_iterations=agent_data.get("max_iterations", 10),
            allow_delegation=agent_data.get("allow_delegation", True),
            verbose=agent_data.get("verbose", True),
            temperature=temperature,
            max_tokens=max_tokens,
            primary_entity_type=agent_data.get("primary_entity_type"),
            entity_types=agent_data.get("entity_types", [])
        )

        # Cache the processed config
        self._processed_configs[cache_key] = config
        logger.debug(f"✅ Cached config for {agent_name}")

        return config

    def get_all_agent_configs(self, context: dict[str, Any]) -> dict[AgentRole, AgentConfig]:
        """Get all agent configurations with processed templates and performance optimizations."""
        configs = {}
        agents_data = self._config_data.get("agents", [])

        for agent_data in agents_data:
            try:
                agent_name = agent_data.get("name")
                if not agent_name:
                    logger.warning(f"⚠️ Agent data missing name: {agent_data}")
                    continue
                    
                role = AgentRole(agent_name)
                configs[role] = self.get_agent_config(role, context)
            except ValueError:
                # Skip unknown agent roles
                logger.warning(f"⚠️ Unknown agent role: {agent_data}")
                continue

        logger.info(f"✅ Loaded {len(configs)} agent configurations with performance optimizations")
        return configs

    def get_enabled_agent_configs(self, context: dict[str, Any]) -> dict[AgentRole, AgentConfig]:
        """Get only enabled agent configurations with processed templates and performance optimizations."""
        all_configs = self.get_all_agent_configs(context)
        enabled_configs = {
            role: config for role, config in all_configs.items()
            if config.enabled
        }
        logger.info(f"✅ Loaded {len(enabled_configs)} enabled agent configurations with performance optimizations")
        return enabled_configs

    def get_agent_tools(self, role: AgentRole) -> list[str]:
        """Get tools for a specific agent."""
        agent_name = role.value
        agents_data = self._config_data.get("agents", [])
        
        for agent in agents_data:
            if agent.get("name") == agent_name:
                return agent.get("tools", [])
        return []

    def get_agent_goal(self, role: AgentRole, context: dict[str, Any]) -> str:
        """Get processed goal for a specific agent."""
        config = self.get_agent_config(role, context)
        return config.goal

    def get_agent_backstory(self, role: AgentRole, context: dict[str, Any]) -> str:
        """Get processed backstory for a specific agent."""
        config = self.get_agent_config(role, context)
        return config.backstory

    def get_agent_temperature(self, role: AgentRole) -> float:
        """Get temperature setting for a specific agent."""
        config = self.get_agent_config(role, {})
        return config.temperature

    def get_agent_max_tokens(self, role: AgentRole) -> int:
        """Get max_tokens setting for a specific agent."""
        config = self.get_agent_config(role, {})
        return config.max_tokens

    def get_llm_optimizations(self) -> dict[str, Any]:
        """Get LLM performance optimization settings."""
        return self._config_data.get("llm_optimizations", {})

    def get_performance_rules(self) -> dict[str, str]:
        """Get performance rules for LLM optimization."""
        llm_optimizations = self.get_llm_optimizations()
        return llm_optimizations.get("performance_rules", {})

    def get_all_configs(self) -> dict[AgentRole, AgentConfig]:
        """Get all agent configurations without context (for backward compatibility)."""
        # Use default context for backward compatibility
        context = {
            "team_name": "KICKAI",
            "team_id": "KAI",
            "chat_type": "main",
            "user_role": "public",
            "username": "user"
        }
        return self.get_all_agent_configs(context)

    def update_agent_config(self, role: AgentRole, config: AgentConfig) -> None:
        """Update agent configuration in memory (does not persist to YAML)."""
        # Store updated config in processed configs cache
        context = {
            "team_name": "KICKAI",
            "team_id": "KAI",
            "chat_type": "main",
            "user_role": "public",
            "username": "user"
        }
        context_key = hash(str(context))
        cache_key = f"{role.value}_{context_key}"
        self._processed_configs[cache_key] = config
        logger.debug(f"✅ Updated agent config for {role.value}")


# Global instance
_agent_config_manager = None

def get_agent_config_manager() -> YAMLAgentConfigurationManager:
    """Get the global agent configuration manager instance."""
    global _agent_config_manager
    if _agent_config_manager is None:
        _agent_config_manager = YAMLAgentConfigurationManager()
    return _agent_config_manager

def get_agent_config(role: AgentRole, context: dict[str, Any]) -> AgentConfig:
    """Get agent configuration with context and performance optimizations."""
    return get_agent_config_manager().get_agent_config(role, context)

def get_all_agent_configs(context: dict[str, Any]) -> dict[AgentRole, AgentConfig]:
    """Get all agent configurations with context and performance optimizations."""
    return get_agent_config_manager().get_all_agent_configs(context)

def get_enabled_agent_configs(context: dict[str, Any]) -> dict[AgentRole, AgentConfig]:
    """Get enabled agent configurations with context and performance optimizations."""
    return get_agent_config_manager().get_enabled_agent_configs(context)

def get_agent_tools(role: AgentRole) -> list[str]:
    """Get tools for a specific agent."""
    return get_agent_config_manager().get_agent_tools(role)

def get_agent_goal(role: AgentRole, context: dict[str, Any]) -> str:
    """Get processed goal for a specific agent."""
    return get_agent_config_manager().get_agent_goal(role, context)

def get_agent_backstory(role: AgentRole, context: dict[str, Any]) -> str:
    """Get processed backstory for a specific agent."""
    return get_agent_config_manager().get_agent_backstory(role, context)

def get_agent_temperature(role: AgentRole) -> float:
    """Get temperature setting for a specific agent."""
    return get_agent_config_manager().get_agent_temperature(role)

def get_agent_max_tokens(role: AgentRole) -> int:
    """Get max_tokens setting for a specific agent."""
    return get_agent_config_manager().get_agent_max_tokens(role)

def get_llm_optimizations() -> dict[str, Any]:
    """Get LLM performance optimization settings."""
    return get_agent_config_manager().get_llm_optimizations()

def get_performance_rules() -> dict[str, str]:
    """Get performance rules for LLM optimization."""
    return get_agent_config_manager().get_performance_rules()


# Backward compatibility functions
def get_agent_config_manager_legacy():
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_agent_config_manager_legacy() - use get_agent_config_manager() instead")
    return get_agent_config_manager()

def get_agent_config_legacy(role: AgentRole) -> Optional[AgentConfig]:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_agent_config_legacy() - use get_agent_config(role, context) instead")
    # Return a basic config without context for backward compatibility
    try:
        context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
        return get_agent_config(role, context)
    except Exception as e:
        logger.error(f"❌ Failed to get legacy agent config for {role}: {e}")
        return None

def get_all_agent_configs_legacy() -> dict[AgentRole, AgentConfig]:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_all_agent_configs_legacy() - use get_all_agent_configs(context) instead")
    # Return basic configs without context for backward compatibility
    try:
        context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
        return get_all_agent_configs(context)
    except Exception as e:
        logger.error(f"❌ Failed to get legacy agent configs: {e}")
        return {}

def get_enabled_agent_configs_legacy() -> dict[AgentRole, AgentConfig]:
    """Legacy function for backward compatibility."""
    logger.warning("⚠️ Using legacy get_enabled_agent_configs_legacy() - use get_enabled_agent_configs(context) instead")
    # Return basic configs without context for backward compatibility
    try:
        context = {"team_name": "KICKAI", "team_id": "KAI", "chat_type": "main", "user_role": "public", "username": "user"}
        return get_enabled_agent_configs(context)
    except Exception as e:
        logger.error(f"❌ Failed to get legacy enabled agent configs: {e}")
        return {}
