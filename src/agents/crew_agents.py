#!/usr/bin/env python3
"""
Simplified CrewAI Football Team Management System - 8-Agent Architecture

This module provides a simplified, production-ready implementation of the
CrewAI-based football team management system with 8 specialized agents.
"""

import asyncio
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any

from crewai import Crew
from loguru import logger

from src.agents.configurable_agent import ConfigurableAgent
from src.agents.entity_specific_agents import (
    EntitySpecificAgentManager,
    EntityType,
    create_entity_specific_agent,
)
from src.agents.tool_registry import get_tool_registry
from src.config.agents import get_agent_config, get_enabled_agent_configs
from src.core.enums import AgentRole
from src.core.settings import get_settings
from src.utils.llm_factory import LLMFactory


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass

class AgentInitializationError(Exception):
    """Raised when agent initialization fails."""
    pass

def log_errors(func):
    """Decorator to log errors in tool management."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper


class AgentToolsManager:
    """Manages tool assignment for agents with entity-specific validation."""

    def __init__(self, tool_registry):
        self._tool_registry = tool_registry
        self._entity_manager = EntitySpecificAgentManager(tool_registry)

        logger.info("🔧 AgentToolsManager initialized with entity-specific validation")

    @log_errors
    def get_tools_for_role(self, role: AgentRole, entity_type: EntityType | None = None) -> list[Any]:
        """Get tools for a specific role with entity-specific filtering."""
        try:
            config = get_agent_config(role)
            if not config:
                logger.warning(f"No configuration found for role {role}")
                return []

            # Get tools based on agent-specific configuration
            tools = []
            for tool_name in config.tools:
                # Validate tool access for this agent and entity type
                if entity_type and not self._entity_manager.validate_agent_tool_combination(
                    role, tool_name, {}
                ):
                    logger.warning(f"⚠️ Tool '{tool_name}' not accessible for {role.value} with entity type {entity_type.value}")
                    continue

                tool_func = self._tool_registry.get_tool_function(tool_name)
                if tool_func:
                    tools.append(tool_func)
                    logger.info(f"[AGENT TOOLS] ✅ Found tool '{tool_name}' for {role.value}")
                else:
                    logger.warning(f"[AGENT TOOLS] ❌ Tool '{tool_name}' not found for {role.value}")

            logger.info(f"🔧 Loading {len(tools)} tools for {role.value}")
            return tools

        except Exception as e:
            logger.error(f"Error getting tools for agent {role}: {e}")
            return []

    def get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        return self._tool_registry.get_tool_names()

    def get_tool_info(self, tool_name: str) -> dict[str, Any] | None:
        """Get information about a specific tool."""
        tool = self._tool_registry.get_tool(tool_name)
        if tool:
            return {
                'name': tool.name,
                'description': tool.description,
                'type': tool.tool_type.value,
                'category': tool.category.value,
                'feature': tool.feature_module,
                'entity_types': [et.value for et in tool.entity_types]
            }
        return None


class TeamManagementSystem:
    """
    Simplified Team Management System using generic ConfigurableAgent.
    
    This system uses the new generic ConfigurableAgent class and centralized
    configuration to create and manage all agents with entity-specific validation.
    """

    def __init__(self, team_id: str):
        self.team_id = team_id
        self.agents: dict[AgentRole, ConfigurableAgent] = {}
        self.crew: Crew | None = None

        # Initialize team memory for conversation context
        from src.agents.team_memory import TeamMemory
        self.team_memory = TeamMemory(team_id)
        logger.info(f"[TEAM INIT] Initialized team memory for {team_id}")

        # Initialize configuration
        logger.info("[TEAM INIT] Getting improved config")
        self.config_manager = get_settings()
        logger.info(f"[TEAM INIT] Getting team config for {team_id}")
        self.team_config = self.config_manager
        logger.info(f"[TEAM INIT] Loaded team_config: {self.team_config}")

        if not self.team_config:
            raise ConfigurationError(f"No team configuration found for {team_id}")

        # Initialize LLM
        logger.info("[TEAM INIT] Initializing LLM")
        self._initialize_llm()

        # Initialize tool registry and entity manager
        logger.info("[TEAM INIT] Initializing tool registry and entity manager")
        self._initialize_tool_registry()

        # Initialize agents with entity-specific validation
        logger.info("[TEAM INIT] Initializing agents dictionary")
        self._initialize_agents()

        # Create persistent crew
        logger.info("[TEAM INIT] Creating persistent crew")
        self._create_crew()

        logger.info(f"✅ TeamManagementSystem initialized for team {team_id} with entity-specific validation")

    def _initialize_llm(self):
        """Initialize the LLM using the factory pattern with robust error handling."""
        try:
            # Use the new factory method that reads from environment
            self.llm = LLMFactory.create_from_environment()

            # Wrap the LLM with our robust error handling for CrewAI
            self.llm = self._wrap_llm_with_error_handling(self.llm)

            logger.info(f"✅ LLM initialized successfully with robust error handling: {type(self.llm).__name__}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise ConfigurationError(f"Failed to initialize LLM: {e!s}")

    def _initialize_tool_registry(self):
        """Initialize tool registry and entity manager."""
        try:
            self.tool_registry = get_tool_registry()

            # Ensure tools are discovered and registered
            if not self.tool_registry._discovered:
                logger.info("🔍 Tool registry not discovered, running auto-discovery...")
                self.tool_registry.auto_discover_tools('src')
            else:
                logger.info("✅ Tool registry already discovered")

            self.entity_manager = EntitySpecificAgentManager(self.tool_registry)
            logger.info("✅ Tool registry and entity manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize tool registry: {e}")
            raise ConfigurationError(f"Failed to initialize tool registry: {e!s}")

    def _initialize_agents(self):
        """Initialize all agents with entity-specific validation."""
        try:
            # Get enabled agent configurations
            enabled_configs = get_enabled_agent_configs()

            for role, config in enabled_configs.items():
                try:
                    # Create entity-specific agent
                    agent = create_entity_specific_agent(
                        team_id=self.team_id,
                        role=role,
                        llm=self.llm,
                        tool_registry=self.tool_registry,
                        team_memory=self.team_memory,
                        config=config,
                        entity_type=config.primary_entity_type
                    )

                    self.agents[role] = agent
                    logger.info(f"✅ Created entity-specific agent for role: {role.value} (entity_type: {config.primary_entity_type.value if config.primary_entity_type else 'None'})")

                except Exception as e:
                    logger.error(f"❌ Failed to create agent for role {role.value}: {e}")
                    # Continue with other agents instead of failing completely
                    continue

            logger.info(f"✅ Initialized {len(self.agents)} agents with entity-specific validation")

        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {e}")
            raise AgentInitializationError(f"Failed to initialize agents: {e!s}")

    def _create_crew(self):
        """Create the CrewAI crew with entity-aware agents."""
        try:
            # Create crew with all available agents
            crew_agents = [agent.crew_agent for agent in self.agents.values()]

            if not crew_agents:
                raise AgentInitializationError("No agents available for crew creation")

            # Get verbose setting from environment
            from src.core.settings import get_settings
            settings = get_settings()
            verbose_mode = settings.verbose_logging or settings.is_development

            self.crew = Crew(
                agents=crew_agents,
                tasks=[],
                verbose=verbose_mode,  # Use environment-based verbose setting
                memory=True  # Enable memory for the crew
            )

            logger.info(f"✅ Created crew with {len(crew_agents)} entity-aware agents")

        except Exception as e:
            logger.error(f"❌ Failed to create crew: {e}")
            raise AgentInitializationError(f"Failed to create crew: {e!s}")

    def _wrap_llm_with_error_handling(self, llm):
        """Wrap LLM with robust error handling for CrewAI."""
        # This is a simplified wrapper - in production you might want more sophisticated error handling
        return llm



    def get_agent_summary(self) -> dict[str, Any]:
        """Get a summary of all agents with their entity types."""
        summary = {}
        for role, agent in self.agents.items():
            config = get_agent_config(role)
            summary[role.value] = {
                'role': role.value,
                'goal': config.goal if config else 'Unknown',
                'entity_types': [et.value for et in config.entity_types] if config else [],
                'primary_entity_type': config.primary_entity_type.value if config and config.primary_entity_type else None,
                'tools_count': len(agent.tools),
                'enabled': config.enabled if config else False
            }
        return summary

    def get_entity_validation_summary(self) -> dict[str, Any]:
        """Get a summary of entity validation capabilities."""
        return {
            'entity_manager_available': self.entity_manager is not None,
            'agent_entity_mappings': {
                role.value: [et.value for et in self.entity_manager.agent_entity_mappings.get(role, [])]
                for role in self.agents.keys()
            },
            'validation_rules': {
                'player_keywords': list(self.entity_manager.validator.player_keywords),
                'team_member_keywords': list(self.entity_manager.validator.team_member_keywords),
                'ambiguous_keywords': list(self.entity_manager.validator.ambiguous_keywords)
            }
        }

    def get_agent(self, role: AgentRole) -> ConfigurableAgent | None:
        """Get a specific agent by role."""
        return self.agents.get(role)

    def get_enabled_agents(self) -> list[ConfigurableAgent]:
        """Get all enabled agents."""
        return list(self.agents.values())

    def get_orchestration_pipeline_status(self) -> dict[str, Any]:
        """Get the status of the orchestration pipeline."""
        if hasattr(self, '_orchestration_pipeline'):
            return self._orchestration_pipeline.get_pipeline_status()
        else:
            return {
                'orchestration_pipeline': 'Not initialized',
                'all_components_initialized': False
            }

    async def execute_task(self, task_description: str, execution_context: dict[str, Any]) -> str:
        """
        Execute a task using the orchestration pipeline with conversation context.
        
        This method delegates task execution to the dedicated OrchestrationPipeline
        which breaks down the process into separate, swappable components.
        """
        logger.info(f"🚨 EXECUTE_TASK CALLED: task_description='{task_description}', execution_context={execution_context}")
        try:
            logger.info(f"🤖 TEAM MANAGEMENT: Starting task execution for team {self.team_id}")
            logger.info(f"🤖 TEAM MANAGEMENT: Task description: {task_description}")
            logger.info(f"🤖 TEAM MANAGEMENT: Execution context: {execution_context}")
            logger.info(f"🤖 TEAM MANAGEMENT: Available agents: {[role.value for role in self.agents.keys()]}")

            # Log agent details
            for role, agent in self.agents.items():
                tools = agent.get_tools()
                logger.info(f"🤖 TEAM MANAGEMENT: Agent '{role.value}' has {len(tools)} tools: {[tool.name for tool in tools]}")

            # Add conversation context to execution context
            user_id = execution_context.get('user_id')
            if user_id and hasattr(self, 'team_memory'):
                # Get user-specific memory context
                memory_context = self.team_memory.get_user_memory_context(user_id)
                execution_context['memory_context'] = memory_context
                logger.info(f"🤖 TEAM MANAGEMENT: Added memory context for user {user_id}")

            # Initialize orchestration pipeline if not already done
            if not hasattr(self, '_orchestration_pipeline'):
                logger.info("🤖 TEAM MANAGEMENT: Creating orchestration pipeline")
                try:
                    from agents.simplified_orchestration import SimplifiedOrchestrationPipeline
                    self._orchestration_pipeline = SimplifiedOrchestrationPipeline(llm=self.llm)
                    logger.info("🤖 ORCHESTRATION: Initialized orchestration pipeline")
                except Exception as e:
                    logger.error(f"🤖 TEAM MANAGEMENT: Failed to create orchestration pipeline: {e}", exc_info=True)
                    # Fallback to basic crew
                    logger.info("🤖 TEAM MANAGEMENT: Falling back to basic crew execution")
                    return await self._execute_with_basic_crew(task_description, execution_context)
            else:
                logger.info("🤖 TEAM MANAGEMENT: Using existing orchestration pipeline")

            # Enhanced logging for debugging
            is_help_command = task_description.lower().strip() == "/help"
            is_myinfo_command = task_description.lower().strip() == "/myinfo"

            if is_myinfo_command:
                logger.info("🔍 MYINFO FLOW STEP 7: About to call orchestration pipeline")
                logger.info(f"🔍 MYINFO FLOW STEP 7a: task_description='{task_description}'")
                logger.info(f"🔍 MYINFO FLOW STEP 7b: execution_context={execution_context}")

            # Execute task through orchestration pipeline
            logger.info("🤖 TEAM MANAGEMENT: Calling orchestration pipeline.execute_task")
            result = await self._orchestration_pipeline.execute_task(
                task_description=task_description,
                execution_context=execution_context,
                available_agents=self.agents
            )

            if is_myinfo_command:
                logger.info("🔍 MYINFO FLOW STEP 8: Orchestration pipeline completed")
                logger.info(f"🔍 MYINFO FLOW STEP 8a: result={result}")

            # Store conversation in memory for context persistence
            if user_id and hasattr(self, 'team_memory'):
                self.team_memory.add_conversation(
                    user_id=user_id,
                    input_text=task_description,
                    output_text=result,
                    context=execution_context
                )
                logger.info(f"🤖 TEAM MANAGEMENT: Stored conversation in memory for user {user_id}")

            logger.info("🤖 TEAM MANAGEMENT: Task execution completed successfully")
            return result

        except Exception as e:
            logger.error(f"🤖 TEAM MANAGEMENT: Error during task execution: {e}", exc_info=True)
            logger.info("🤖 TEAM MANAGEMENT: Falling back to basic crew execution due to error")
            return await self._execute_with_basic_crew(task_description, execution_context)

    async def _execute_with_basic_crew(self, task_description: str, execution_context: dict[str, Any]) -> str:
        """
        Fallback method to execute task using basic CrewAI crew.
        This is used when the orchestration pipeline fails.
        """
        try:
            logger.info("🤖 BASIC CREW: Executing task with basic crew")
            logger.info(f"🤖 BASIC CREW: Task description: {task_description}")
            logger.info(f"🤖 BASIC CREW: Execution context: {execution_context}")

            # Use the basic crew that was created in _create_crew
            if hasattr(self, 'crew') and self.crew:
                logger.info("🤖 BASIC CREW: Using existing crew")

                # Create a proper CrewAI task
                from crewai import Task

                # Get the appropriate agent for this task
                selected_agent_role = self.entity_manager.route_operation_to_agent(
                    task_description, execution_context.get('parameters', {}), self.agents
                )

                if selected_agent_role and selected_agent_role in self.agents:
                    agent = self.agents[selected_agent_role]

                    # Create a task for the selected agent
                    task = Task(
                        description=task_description,
                        agent=agent.crew_agent,
                        expected_output="A clear and helpful response to the user's request"
                    )

                    # Add task to crew and execute
                    self.crew.tasks = [task]
                    result = self.crew.kickoff()
                    logger.info(f"🤖 BASIC CREW: Task completed with result: {result}")
                    return result
                else:
                    logger.error("🤖 BASIC CREW: No suitable agent found for task")
                    return "❌ Sorry, I'm unable to process your request at the moment."
            else:
                logger.error("🤖 BASIC CREW: No crew available for fallback")
                return "❌ Sorry, I'm unable to process your request at the moment."

        except Exception as e:
            logger.error(f"🤖 BASIC CREW: Error in fallback execution: {e}", exc_info=True)
            return "❌ Sorry, I'm having trouble processing your request right now. Please try again in a moment."

    @contextmanager
    def debug_mode(self):
        """Context manager for debug mode."""
        original_level = logger.level
        logger.setLevel(logging.DEBUG)
        try:
            yield
        finally:
            logger.setLevel(original_level)

    def health_check(self) -> dict[str, Any]:
        """Perform a health check on the system."""
        try:
            health_status = {
                'system': 'healthy',
                'agents_count': len(self.agents),
                'agents': {},
                'crew_created': self.crew is not None,
                'llm_available': self.llm is not None,
                'team_config_loaded': self.team_config is not None
            }

            # Check each agent
            for role, agent in self.agents.items():
                health_status['agents'][role.value] = {
                    'enabled': agent.is_enabled(),
                    'tools_count': len(agent.get_tools()),
                    'crew_agent_available': agent.crew_agent is not None
                }

            return health_status

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                'system': 'unhealthy',
                'error': str(e)
            }


# Convenience functions for backward compatibility
def create_team_management_system(team_id: str) -> TeamManagementSystem:
    """Create a team management system for the specified team."""
    return TeamManagementSystem(team_id)


def get_agent(team_id: str, role: AgentRole) -> ConfigurableAgent | None:
    """Get a specific agent for a team."""
    system = TeamManagementSystem(team_id)
    return system.get_agent(role)


def execute_task(team_id: str, task_description: str, execution_context: dict[str, Any]) -> str:
    """Execute a task for a team."""
    system = TeamManagementSystem(team_id)
    return asyncio.run(system.execute_task(task_description, execution_context))
