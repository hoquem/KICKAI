#!/usr/bin/env python3
"""
Agent Registry for KICKAI System

This module provides a centralized registry for all agents used in the system.
It follows the single source of truth principle and clean architecture patterns.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger


class AgentType(Enum):
    """Types of agents supported by the system."""

    HELP_ASSISTANT = "help_assistant"
    MESSAGE_PROCESSOR = "message_processor"
    PLAYER_COORDINATOR = "player_coordinator"
    TEAM_MANAGER = "team_manager"
    FINANCE_MANAGER = "finance_manager"
    PERFORMANCE_ANALYST = "performance_analyst"
    LEARNING_AGENT = "learning_agent"
    ONBOARDING_AGENT = "onboarding_agent"
    COMMAND_FALLBACK = "command_fallback"
    CUSTOM = "custom"


class AgentCategory(Enum):
    """Categories of agents for organization."""

    CORE = "core"
    FEATURE = "feature"
    UTILITY = "utility"
    CUSTOM = "custom"


@dataclass
class AgentMetadata:
    """Metadata for agent registration."""

    agent_id: str
    agent_type: AgentType
    category: AgentCategory
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True
    dependencies: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] | None = None
    factory_function: Callable | None = None
    feature_module: str = "unknown"
    tags: list[str] = field(default_factory=list)


class AgentFactory(ABC):
    """Abstract base class for agent factories."""

    @abstractmethod
    def create_agent(self, **kwargs) -> Any:
        """Create an agent instance."""
        pass

    @abstractmethod
    def get_agent_info(self) -> dict[str, Any]:
        """Get information about the agent this factory creates."""
        pass


class AgentRegistry:
    """
    Centralized agent registry for the KICKAI system.

    This registry provides:
    - Agent registration and discovery
    - Factory pattern for agent creation
    - Dependency management
    - Configuration management
    - Feature-based organization
    """

    def __init__(self):
        self._agents: dict[str, AgentMetadata] = {}
        self._factories: dict[str, AgentFactory] = {}
        self._agent_aliases: dict[str, str] = {}
        self._feature_agents: dict[str, list[str]] = {}
        self._discovered = False

        logger.info("🔧 AgentRegistry initialized")

    def register_agent(
        self,
        agent_id: str,
        agent_type: AgentType,
        category: AgentCategory,
        name: str,
        description: str,
        version: str = "1.0.0",
        enabled: bool = True,
        dependencies: list[str] | None = None,
        tools: list[str] | None = None,
        config_schema: dict[str, Any] | None = None,
        factory_function: Callable | None = None,
        feature_module: str = "unknown",
        tags: list[str] | None = None,
        aliases: list[str] | None = None,
    ) -> None:
        """
        Register an agent with the registry.

        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent
            category: Category of agent
            name: Display name
            description: Agent description
            version: Agent version
            enabled: Whether agent is enabled
            dependencies: List of dependencies
            tools: List of required tools
            config_schema: Configuration schema
            factory_function: Function to create agent instance
            feature_module: Feature module name
            tags: Tags for categorization
            aliases: Alternative names
        """
        if agent_id in self._agents:
            logger.warning(f"Agent '{agent_id}' already registered, overwriting")

        metadata = AgentMetadata(
            agent_id=agent_id,
            agent_type=agent_type,
            category=category,
            name=name,
            description=description,
            version=version,
            enabled=enabled,
            dependencies=dependencies or [],
            tools=tools or [],
            config_schema=config_schema,
            factory_function=factory_function,
            feature_module=feature_module,
            tags=tags or [],
        )

        self._agents[agent_id] = metadata

        # Register aliases
        if aliases:
            for alias in aliases:
                if alias in self._agent_aliases:
                    logger.warning(
                        f"Alias '{alias}' already registered for '{self._agent_aliases[alias]}', overwriting with '{agent_id}'"
                    )
                self._agent_aliases[alias] = agent_id

        # Group by feature
        if feature_module not in self._feature_agents:
            self._feature_agents[feature_module] = []
        self._feature_agents[feature_module].append(agent_id)

        logger.info(f"🤖 Registered agent: {agent_id} ({feature_module})")

    def register_factory(self, agent_id: str, factory: AgentFactory) -> None:
        """Register a factory for agent creation."""
        self._factories[agent_id] = factory
        logger.info(f"🏭 Registered factory for agent: {agent_id}")

    def get_agent(self, agent_id: str) -> AgentMetadata | None:
        """Get agent metadata by ID or alias."""
        # Check direct ID
        if agent_id in self._agents:
            return self._agents[agent_id]

        # Check aliases
        if agent_id in self._agent_aliases:
            alias_target = self._agent_aliases[agent_id]
            return self._agents.get(alias_target)

        return None

    def get_factory(self, agent_id: str) -> AgentFactory | None:
        """Get agent factory by ID."""
        return self._factories.get(agent_id)

    def create_agent(self, agent_id: str, **kwargs) -> Any:
        """Create an agent instance using its factory."""
        agent_metadata = self.get_agent(agent_id)
        if not agent_metadata:
            raise ValueError(f"Agent '{agent_id}' not found in registry")

        if not agent_metadata.enabled:
            raise ValueError(f"Agent '{agent_id}' is disabled")

        # Try factory first
        factory = self.get_factory(agent_id)
        if factory:
            return factory.create_agent(**kwargs)

        # Try factory function
        if agent_metadata.factory_function:
            return agent_metadata.factory_function(**kwargs)

        raise ValueError(f"No factory available for agent '{agent_id}'")

    def get_agents_by_feature(self, feature_module: str) -> list[AgentMetadata]:
        """Get all agents for a specific feature."""
        agent_ids = self._feature_agents.get(feature_module, [])
        return [self._agents[agent_id] for agent_id in agent_ids if agent_id in self._agents]

    def get_agents_by_type(self, agent_type: AgentType) -> list[AgentMetadata]:
        """Get all agents of a specific type."""
        return [agent for agent in self._agents.values() if agent.agent_type == agent_type]

    def get_agents_by_category(self, category: AgentCategory) -> list[AgentMetadata]:
        """Get all agents in a specific category."""
        return [agent for agent in self._agents.values() if agent.category == category]

    def get_enabled_agents(self) -> list[AgentMetadata]:
        """Get all enabled agents."""
        return [agent for agent in self._agents.values() if agent.enabled]

    def get_agents_with_tool(self, tool_name: str) -> list[AgentMetadata]:
        """Get all agents that use a specific tool."""
        return [agent for agent in self._agents.values() if tool_name in agent.tools]

    def auto_discover_agents(self, src_path: str = "src") -> None:
        """
        Automatically discover and register agents from feature modules.

        This method scans the features directory and looks for agent definitions
        in the domain/agents directories.
        """
        if self._discovered:
            logger.info("Agents already discovered, skipping auto-discovery")
            return

        from pathlib import Path

        src_path = Path(src_path)
        features_path = src_path / "features"

        if not features_path.exists():
            logger.warning(f"Features path not found: {features_path}")
            return

        for feature_dir in features_path.iterdir():
            if not feature_dir.is_dir() or feature_dir.name.startswith("_"):
                continue

            feature_name = feature_dir.name
            agents_path = feature_dir / "domain" / "agents"

            if not agents_path.exists():
                continue

            logger.info(f"🔍 Discovering agents for feature: {feature_name}")
            self._discover_agents_from_path(agents_path, feature_name)

        self._discovered = True
        logger.info(f"✅ Auto-discovery complete. Registered {len(self._agents)} agents")

    def _discover_agents_from_path(self, agents_path: Path, feature_name: str) -> None:
        """Discover agents from a specific path."""
        for py_file in agents_path.glob("*.py"):
            if py_file.name.startswith("_") or py_file.name == "__init__.py":
                continue

            try:
                self._discover_agents_from_file(py_file, feature_name)
            except Exception as e:
                logger.error(f"Error discovering agents from {py_file}: {e}")

    def _discover_agents_from_file(self, file_path: Path, feature_name: str) -> None:
        """Discover agents from a specific file."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(feature_name, file_path)
        if not spec or not spec.loader:
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for agent classes and factory functions
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's an agent class
            if hasattr(attr, "__name__") and hasattr(attr, "__doc__"):
                if "agent" in attr_name.lower() and not attr_name.startswith("_"):
                    self._register_discovered_agent(attr, feature_name, file_path)

    def _register_discovered_agent(
        self, agent_class: type, feature_name: str, file_path: Path
    ) -> None:
        """Register a discovered agent."""
        agent_id = f"{feature_name}_{agent_class.__name__.lower()}"

        # Determine agent type based on class name
        agent_type = self._determine_agent_type(agent_class.__name__)
        category = self._determine_agent_category(feature_name)

        self.register_agent(
            agent_id=agent_id,
            agent_type=agent_type,
            category=category,
            name=agent_class.__name__,
            description=agent_class.__doc__ or f"Agent for {feature_name}",
            feature_module=feature_name,
            factory_function=lambda kwargs: agent_class(kwargs),
        )

    def _determine_agent_type(self, class_name: str) -> AgentType:
        """Determine agent type based on class name."""
        class_lower = class_name.lower()

        if "help" in class_lower:
            return AgentType.HELP_ASSISTANT
        elif "message" in class_lower:
            return AgentType.MESSAGE_PROCESSOR
        elif "player" in class_lower:
            return AgentType.PLAYER_COORDINATOR
        elif "team" in class_lower:
            return AgentType.TEAM_MANAGER
        elif "finance" in class_lower:
            return AgentType.FINANCE_MANAGER
        elif "performance" in class_lower:
            return AgentType.PERFORMANCE_ANALYST
        elif "learning" in class_lower:
            return AgentType.LEARNING_AGENT
        elif "onboarding" in class_lower:
            return AgentType.ONBOARDING_AGENT
        elif "fallback" in class_lower:
            return AgentType.COMMAND_FALLBACK
        else:
            return AgentType.CUSTOM

    def _determine_agent_category(self, feature_name: str) -> AgentCategory:
        """Determine agent category based on feature name."""
        if feature_name in ["shared", "system_infrastructure"]:
            return AgentCategory.CORE
        elif feature_name in ["player_registration", "team_administration", "match_management"]:
            return AgentCategory.FEATURE
        else:
            return AgentCategory.UTILITY

    def get_agent_statistics(self) -> dict[str, Any]:
        """Get statistics about registered agents."""
        total_agents = len(self._agents)
        total_enabled = len(self.get_enabled_agents())

        agents_by_type = {}
        for agent_type in AgentType:
            agents_by_type[agent_type.value] = len(self.get_agents_by_type(agent_type))

        agents_by_category = {}
        for category in AgentCategory:
            agents_by_category[category.value] = len(self.get_agents_by_category(category))

        agents_by_feature = {}
        for feature in self._feature_agents:
            agents_by_feature[feature] = len(self.get_agents_by_feature(feature))

        return {
            "total_agents": total_agents,
            "enabled_agents": total_enabled,
            "disabled_agents": total_agents - total_enabled,
            "agents_by_type": agents_by_type,
            "agents_by_category": agents_by_category,
            "agents_by_feature": agents_by_feature,
            "features_with_agents": list(self._feature_agents.keys()),
        }

    def list_all_agents(self) -> list[AgentMetadata]:
        """Get all registered agents."""
        return list(self._agents.values())

    def search_agents(self, query: str) -> list[AgentMetadata]:
        """Search agents by name, description, or tags."""
        query_lower = query.lower()
        results = []

        for agent in self._agents.values():
            if (
                query_lower in agent.name.lower()
                or query_lower in agent.description.lower()
                or any(query_lower in tag.lower() for tag in agent.tags)
            ):
                results.append(agent)

        return results


# Global agent registry instance
_agent_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


def register_agent_decorator(
    agent_id: str,
    agent_type: AgentType,
    category: AgentCategory = AgentCategory.FEATURE,
    name: str | None = None,
    description: str | None = None,
    version: str = "1.0.0",
    enabled: bool = True,
    dependencies: list[str] | None = None,
    tools: list[str] | None = None,
    config_schema: dict[str, Any] | None = None,
    feature_module: str = "unknown",
    tags: list[str] | None = None,
    aliases: list[str] | None = None,
):
    """
    Decorator to register an agent class with the registry.

    Usage:
        @register_agent_decorator(
            agent_id="help_assistant",
            agent_type=AgentType.HELP_ASSISTANT,
            category=AgentCategory.CORE,
            description="Provides help and assistance to users"
        )
        class HelpAssistantAgent:
            pass
    """

    def decorator(cls: type) -> type:
        registry = get_agent_registry()

        # Use class name if name not provided
        agent_name = name or cls.__name__
        agent_description = description or (cls.__doc__ or f"Agent: {cls.__name__}")

        registry.register_agent(
            agent_id=agent_id,
            agent_type=agent_type,
            category=category,
            name=agent_name,
            description=agent_description,
            version=version,
            enabled=enabled,
            dependencies=dependencies,
            tools=tools,
            config_schema=config_schema,
            factory_function=lambda kwargs: cls(kwargs),
            feature_module=feature_module,
            tags=tags,
            aliases=aliases,
        )

        # Mark class as registered
        cls._agent_registered = True
        return cls

    return decorator
