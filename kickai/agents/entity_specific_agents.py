#!/usr/bin/env python3
"""
Entity-Specific Agent Architecture for KICKAI System

This module provides entity-specific agent hierarchies and clear boundaries
between player and team member operations. It implements entity validation
at the orchestration level and ensures proper tool access control.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger

from kickai.core.entity_types import EntityType
from kickai.core.enums import AgentRole, ChatType

from .agent_types import AgentContext
from .tool_registry import ToolRegistry


class EntityAgentType(Enum):
    """Types of entity-specific agents."""

    PLAYER_SPECIALIST = "player_specialist"
    TEAM_MEMBER_SPECIALIST = "team_member_specialist"
    HYBRID_AGENT = "hybrid_agent"  # Can handle both entities
    GENERAL_AGENT = "general_agent"  # Doesn't handle specific entities


@dataclass
class EntityValidationResult:
    """Result of entity validation."""

    is_valid: bool
    entity_type: EntityType | None = None
    error_message: str | None = None
    suggested_agent: AgentRole | None = None


@dataclass
class EntityOperationContext:
    """Context for entity-specific operations."""

    operation_type: str
    entity_type: EntityType
    agent_role: AgentRole
    tool_id: str
    parameters: dict[str, Any]
    validation_result: EntityValidationResult


class EntityValidator(ABC):
    """Abstract base class for entity validation."""

    @abstractmethod
    def validate_operation(
        self, operation: str, parameters: dict[str, Any]
    ) -> EntityValidationResult:
        """Validate if an operation is appropriate for the given parameters."""
        pass

    @abstractmethod
    def get_entity_type_from_parameters(self, parameters: dict[str, Any]) -> EntityType | None:
        """Extract entity type from operation parameters."""
        pass


class PlayerTeamMemberValidator(EntityValidator):
    """Validator for player and team member operations."""

    def __init__(self):
        self.player_keywords = {
            "position",
            "jersey_number",
            "preferred_foot",
            "medical_notes",
            "player_id",
            "onboarding_status",
            "match_eligible",
        }
        self.team_member_keywords = {
            "role",
            "is_admin",
            "permissions",
            "chat_access",
            "administrative",
        }
        self.ambiguous_keywords = {"name", "phone", "email", "telegram_id", "user_id", "status"}

    def validate_operation(
        self, operation: str, parameters: dict[str, Any]
    ) -> EntityValidationResult:
        """Validate if an operation is appropriate for the given parameters."""
        # Check if this is a general command that doesn't require entity validation
        general_commands = {"/help", "/ping", "/version", "/info"}
        operation_lower = operation.lower().strip()

        if operation_lower in general_commands:
            return EntityValidationResult(
                is_valid=True,
                entity_type=EntityType.NEITHER,
                suggested_agent=AgentRole.MESSAGE_PROCESSOR,
            )

        # Extract user context from parameters for simplified routing
        user_context = {}
        if "chat_type" in parameters:
            user_context["chat_type"] = parameters["chat_type"]
        if "is_team_member" in parameters:
            user_context["is_team_member"] = parameters["is_team_member"]
        if "is_player" in parameters:
            user_context["is_player"] = parameters["is_player"]

        # Check operation-based entity type first with user context
        entity_type = self.get_entity_type_from_operation(operation, user_context)

        # If operation doesn't indicate entity type, check parameters
        if entity_type is None:
            entity_type = self.get_entity_type_from_parameters(parameters)

        if entity_type is None:
            return EntityValidationResult(
                is_valid=False,
                error_message="Cannot determine entity type from parameters",
                suggested_agent=AgentRole.MESSAGE_PROCESSOR,
            )

        # Validate operation matches entity type
        operation_lower = operation.lower()

        if entity_type == EntityType.PLAYER:
            if any(
                keyword in operation_lower for keyword in ["team_member", "admin", "management"]
            ):
                return EntityValidationResult(
                    is_valid=False,
                    entity_type=entity_type,
                    error_message="Player operation attempted on team member data",
                    suggested_agent=AgentRole.TEAM_MANAGER,
                )
        elif entity_type == EntityType.TEAM_MEMBER:
            # Allow team members to perform player operations in leadership chat
            # This is the correct behavior for the simplified logic
            pass

        return EntityValidationResult(is_valid=True, entity_type=entity_type)

    def get_entity_type_from_parameters(self, parameters: dict[str, Any]) -> EntityType | None:
        """Extract entity type from operation parameters."""
        param_keys = set(parameters.keys())

        # Check for player-specific parameters
        player_indicators = param_keys.intersection(self.player_keywords)
        if player_indicators:
            return EntityType.PLAYER

        # Check for team member-specific parameters
        team_member_indicators = param_keys.intersection(self.team_member_keywords)
        if team_member_indicators:
            return EntityType.TEAM_MEMBER

        # Check for ambiguous parameters that could be either
        ambiguous_indicators = param_keys.intersection(self.ambiguous_keywords)
        if ambiguous_indicators:
            # Try to infer from context
            return self._infer_entity_type_from_context(parameters)

        return None

    def _infer_entity_type_from_context(self, parameters: dict[str, Any]) -> EntityType | None:
        """Infer entity type from context when parameters are ambiguous."""
        # Check for specific values that indicate entity type
        if "role" in parameters:
            role = str(parameters["role"]).lower()
            if role in ["player", "forward", "midfielder", "defender", "goalkeeper"]:
                return EntityType.PLAYER
            elif role in ["admin", "manager", "coach", "assistant"]:
                return EntityType.TEAM_MEMBER

        if "status" in parameters:
            status = str(parameters["status"]).lower()
            if status in ["pending", "approved", "rejected", "active", "inactive"]:
                # Could be either, need more context
                return None

        return None

    def get_entity_type_from_operation(
        self, operation: str, user_context: dict = None
    ) -> EntityType | None:
        """Extract entity type from operation name with simplified chat-based logic."""
        operation_lower = operation.lower().strip()

        # Extract just the command name (before any parameters)
        command_name = operation_lower.split()[0] if operation_lower else ""

        # SIMPLIFIED LOGIC: Chat type determines entity type
        if user_context:
            chat_type = user_context.get("chat_type", "").lower()

            # Log context for debugging
            logger.debug(
                f"Entity classification: operation={operation}, chat_type={chat_type}, user_context={user_context}"
            )

            # In leadership chat, treat as team member
            if chat_type == ChatType.LEADERSHIP.value:
                if command_name in ["/myinfo", "/status", "/info", "/list", "/team"]:
                    return EntityType.TEAM_MEMBER
                elif command_name in [
                    "/addmember",
                    "/add_member",
                    "/addteammember",
                    "/add_team_member",
                    "/member",
                    "/members",
                    "/admin",
                    "/management",
                ]:
                    return EntityType.TEAM_MEMBER
                else:
                    return EntityType.TEAM_MEMBER  # Default to team member in leadership chat

            # In main chat, treat as player
            elif chat_type == ChatType.MAIN.value:
                if command_name in ["/myinfo", "/status", "/info", "/list"]:
                    return EntityType.PLAYER
                elif command_name in [
                    "/addplayer",
                    "/add_player",
                    "/approve",
                    "/reject",
                    "/player",
                    "/players",
                ]:
                    return EntityType.PLAYER
                else:
                    return EntityType.PLAYER  # Default to player in main chat
            else:
                logger.warning(f"Unknown chat_type: {chat_type} for operation: {operation}")
        else:
            logger.debug(
                f"No user_context provided for operation: {operation} - using fallback classification"
            )

        # Fallback to operation-based classification if no context
        player_operations = {
            "/addplayer",
            "/add_player",
            "/approve",
            "/reject",
            "/player",
            "/players",
        }

        team_member_operations = {
            "/addmember",
            "/add_member",
            "/addteammember",
            "/add_team_member",
            "/member",
            "/members",
            "/admin",
            "/management",
        }

        if command_name in player_operations:
            return EntityType.PLAYER
        elif command_name in team_member_operations:
            return EntityType.TEAM_MEMBER

        return None


class EntitySpecificAgentManager:
    """Manages entity-specific agent operations and routing."""

    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.validator = PlayerTeamMemberValidator()
        self.agent_entity_mappings = self._initialize_agent_entity_mappings()

        logger.info("🔧 EntitySpecificAgentManager initialized")

    def _initialize_agent_entity_mappings(self) -> dict[AgentRole, list[EntityType]]:
        """Initialize mappings between agents and entity types they can handle."""
        return {
            AgentRole.PLAYER_COORDINATOR: [EntityType.PLAYER],
            AgentRole.ONBOARDING_AGENT: [EntityType.PLAYER],
            AgentRole.TEAM_MANAGER: [EntityType.TEAM_MEMBER, EntityType.BOTH],
            AgentRole.MESSAGE_PROCESSOR: [EntityType.BOTH, EntityType.NEITHER],
            AgentRole.FINANCE_MANAGER: [EntityType.BOTH, EntityType.NEITHER],
            AgentRole.PERFORMANCE_ANALYST: [EntityType.PLAYER, EntityType.NEITHER],
            AgentRole.LEARNING_AGENT: [EntityType.NEITHER],
            AgentRole.COMMAND_FALLBACK_AGENT: [EntityType.NEITHER],
            AgentRole.AVAILABILITY_MANAGER: [EntityType.PLAYER],
            AgentRole.SQUAD_SELECTOR: [EntityType.PLAYER],
            AgentRole.COMMUNICATION_MANAGER: [EntityType.NEITHER],
            AgentRole.HELP_ASSISTANT: [EntityType.NEITHER],
        }

    def validate_agent_entity_access(self, agent_role: AgentRole, entity_type: EntityType) -> bool:
        """Validate if an agent can handle a specific entity type."""
        allowed_entities = self.agent_entity_mappings.get(agent_role, [])
        return entity_type in allowed_entities

    def get_appropriate_agent_for_entity(
        self, entity_type: EntityType, operation: str
    ) -> AgentRole | None:
        """Get the most appropriate agent for a given entity type and operation."""
        # Extract just the command name (before any parameters) for proper routing
        operation_lower = operation.lower().strip()
        command_name = operation_lower.split()[0] if operation_lower else ""

        if entity_type == EntityType.PLAYER:
            if any(keyword in command_name for keyword in ["/onboard", "/approve"]):
                return AgentRole.ONBOARDING_AGENT
            elif any(keyword in command_name for keyword in ["/addplayer", "/add_player"]):
                return AgentRole.PLAYER_COORDINATOR
            elif any(
                keyword in command_name for keyword in ["/status", "/info", "/list", "/myinfo"]
            ):
                return AgentRole.PLAYER_COORDINATOR
            elif any(keyword in command_name for keyword in ["/availability", "/squad"]):
                return AgentRole.AVAILABILITY_MANAGER
            else:
                return AgentRole.PLAYER_COORDINATOR

        elif entity_type == EntityType.TEAM_MEMBER:
            if any(keyword in command_name for keyword in ["/admin", "/manage", "/control"]):
                return AgentRole.TEAM_MANAGER
            elif any(
                keyword in command_name
                for keyword in ["/myinfo", "/status", "/info", "/list", "/team"]
            ):
                return (
                    AgentRole.MESSAGE_PROCESSOR
                )  # Has get_my_team_member_status and list_team_members_and_players tools
            else:
                return AgentRole.TEAM_MANAGER

        elif entity_type == EntityType.BOTH:
            return AgentRole.MESSAGE_PROCESSOR

        elif entity_type == EntityType.NEITHER:
            if any(keyword in command_name for keyword in ["/help", "/command"]):
                return AgentRole.HELP_ASSISTANT
            elif any(keyword in command_name for keyword in ["/communication", "/announce"]):
                return AgentRole.COMMUNICATION_MANAGER
            else:
                return AgentRole.MESSAGE_PROCESSOR

        return None

    def validate_tool_access_for_agent(
        self, tool_id: str, agent_role: AgentRole, entity_type: EntityType
    ) -> bool:
        """Validate if an agent can access a specific tool for a given entity type."""
        # First check if agent can handle this entity type
        if not self.validate_agent_entity_access(agent_role, entity_type):
            return False

        # Then check tool registry access control
        return self.tool_registry.validate_tool_access(tool_id, agent_role.value, entity_type)

    def create_entity_operation_context(
        self, operation: str, agent_role: AgentRole, tool_id: str, parameters: dict[str, Any]
    ) -> EntityOperationContext:
        """Create a context for entity-specific operations."""
        validation_result = self.validator.validate_operation(operation, parameters)
        entity_type = validation_result.entity_type or EntityType.NEITHER

        return EntityOperationContext(
            operation_type=operation,
            entity_type=entity_type,
            agent_role=agent_role,
            tool_id=tool_id,
            parameters=parameters,
            validation_result=validation_result,
        )

    def get_entity_specific_tools(
        self, agent_role: AgentRole, entity_type: EntityType
    ) -> list[str]:
        """Get tools that are appropriate for a specific agent and entity type."""
        if not self.validate_agent_entity_access(agent_role, entity_type):
            return []

        tools = self.tool_registry.get_tools_for_agent(agent_role.value, entity_type)
        return [tool.tool_id for tool in tools]

    def route_operation_to_agent(
        self,
        operation: str,
        parameters: dict[str, Any],
        available_agents: dict[AgentRole, "ConfigurableAgent"],
    ) -> AgentRole | None:
        """Route an operation to the most appropriate agent using simplified chat-based logic."""
        # Extract user context from parameters for simplified routing
        user_context = {}
        if "chat_type" in parameters:
            user_context["chat_type"] = parameters["chat_type"]
        if "is_team_member" in parameters:
            user_context["is_team_member"] = parameters["is_team_member"]
        if "is_player" in parameters:
            user_context["is_player"] = parameters["is_player"]

        # Determine entity type from operation with user context
        entity_type = self.validator.get_entity_type_from_operation(operation, user_context)
        if entity_type is None:
            entity_type = EntityType.NEITHER

        # Get appropriate agent
        suggested_agent = self.get_appropriate_agent_for_entity(entity_type, operation)

        if suggested_agent and suggested_agent in available_agents:
            return suggested_agent

        # Fallback to message processor if suggested agent not available
        if AgentRole.MESSAGE_PROCESSOR in available_agents:
            return AgentRole.MESSAGE_PROCESSOR

        return None

    def validate_agent_tool_combination(
        self, agent_role: AgentRole, tool_id: str, parameters: dict[str, Any]
    ) -> bool:
        """Validate if an agent can use a specific tool with given parameters."""
        entity_type = self.validator.get_entity_type_from_parameters(parameters)
        if entity_type is None:
            entity_type = EntityType.NEITHER

        return self.validate_tool_access_for_agent(tool_id, agent_role, entity_type)


class EntityAwareAgentContext(AgentContext):
    """Enhanced agent context with entity awareness."""

    def __init__(
        self,
        team_id: str,
        role: AgentRole,
        llm: Any,
        tool_registry: ToolRegistry,
        team_memory: Any,
        config: Any = None,
        entity_type: EntityType | None = None,
    ):
        super().__init__(role, team_id, llm, tool_registry, config, team_memory)
        self.entity_type = entity_type
        self.entity_manager = EntitySpecificAgentManager(tool_registry)

    def validate_entity_operation(
        self, operation: str, parameters: dict[str, Any]
    ) -> EntityValidationResult:
        """Validate if this agent can perform the given operation."""
        return self.entity_manager.validator.validate_operation(operation, parameters)

    def get_entity_specific_tools(self) -> list[str]:
        """Get tools appropriate for this agent's entity type."""
        if self.entity_type is None:
            return []

        return self.entity_manager.get_entity_specific_tools(self.role, self.entity_type)


def create_entity_specific_agent(
    team_id: str,
    role: AgentRole,
    llm: Any,
    tool_registry: ToolRegistry,
    team_memory: Any,
    config: Any = None,
    entity_type: EntityType | None = None,
) -> "ConfigurableAgent":
    """Create an entity-specific agent with proper validation and temperature override."""

    # Apply agent-specific temperature override for data-critical agents
    agent_specific_llm = _get_agent_specific_llm_with_temperature(llm, role)

    context = EntityAwareAgentContext(
        team_id=team_id,
        role=role,
        llm=agent_specific_llm,  # Use temperature-adjusted LLM
        tool_registry=tool_registry,
        team_memory=team_memory,
        config=config,
        entity_type=entity_type,
    )

    from .configurable_agent import ConfigurableAgent

    return ConfigurableAgent(context)


def _get_agent_specific_llm_with_temperature(base_llm: Any, role: AgentRole) -> Any:
    """Apply agent-specific model and temperature settings using configuration system."""
    try:
        from kickai.config.agent_models import get_agent_model_config, get_fallback_config
        from kickai.core.settings import get_settings

        settings = get_settings()

        # Get agent-specific model config
        model_config = get_agent_model_config(role, settings.ai_provider)

        if not model_config:
            logger.warning(
                f"No model config for {role.value} with {settings.ai_provider.value}, using fallback"
            )
            model_config = get_fallback_config(role)

        # Create agent-specific LLM with proper model and temperature
        from kickai.utils.llm_factory import LLMConfig, LLMFactory

        agent_config = LLMConfig(
            provider=settings.ai_provider,
            model_name=model_config["model"],
            api_key=settings.get_ai_api_key(),
            temperature=model_config["temperature"],
            timeout_seconds=settings.ai_timeout,
            max_retries=settings.ai_max_retries,
        )

        agent_llm = LLMFactory.create_llm(agent_config)

        logger.info(
            f"🤖 Created {role.value} agent with {settings.ai_provider.value}:{model_config['model']} (temp={model_config['temperature']})"
        )

        return agent_llm

    except Exception as e:
        logger.error(f"Failed to create agent-specific LLM for {role.value}: {e}")
        logger.info(f"Falling back to base LLM for {role.value}")
        return base_llm


def get_entity_specific_agent_manager(tool_registry: ToolRegistry) -> EntitySpecificAgentManager:
    """Get an entity-specific agent manager instance."""
    return EntitySpecificAgentManager(tool_registry)
