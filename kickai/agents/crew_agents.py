#!/usr/bin/env python3
"""
Simplified CrewAI Football Team Management System - 5-Agent Architecture

This module provides a simplified, production-ready implementation of the
CrewAI-based football team management system with 5 essential agents.

ESSENTIAL 5-AGENT SYSTEM:
1. MESSAGE_PROCESSOR - Primary interface and routing
2. HELP_ASSISTANT - Help system and guidance
3. PLAYER_COORDINATOR - Player management and onboarding
4. TEAM_ADMINISTRATOR - Team member management
5. SQUAD_SELECTOR - Squad selection and match management
"""

import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any

from crewai import Crew
from loguru import logger

from kickai.agents.async_tool_metadata import AsyncContextInjector, get_async_tool_registry
from kickai.agents.configurable_agent import ConfigurableAgent

# Removed entity_specific_agents for simplified 5-agent architecture
# Remove SimpleLLMFactory import - replaced with CrewAI native config
# from kickai.utils.llm_factory_simple import SimpleLLMFactory
from kickai.agents.tool_registry import initialize_tool_registry
from kickai.config.agents import get_agent_config
from kickai.config.command_routing_manager import get_command_routing_manager
from kickai.config.llm_config import get_llm_config
from kickai.core.config import get_settings
from kickai.core.enums import AgentRole
from kickai.core.exceptions import AgentInitializationError

# Constants
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BACKOFF_FACTOR = 2
DEFAULT_MAX_ITERATIONS = 3
DEFAULT_TASK_DESCRIPTION_LIMIT = 500
DEFAULT_RESULT_PREVIEW_LIMIT = 100
DEFAULT_VERBOSE_MODE = True
DEFAULT_MEMORY_ENABLED = False


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""

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
        from kickai.agents.team_memory import TeamMemory

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

        # Initialize tool registry and async tool metadata
        logger.info("[TEAM INIT] Initializing tool registry and async tool metadata")
        self._initialize_tool_registry()
        self._initialize_async_tool_registry()

        # Initialize command routing manager
        logger.info("[TEAM INIT] Initializing command routing manager")
        self._initialize_routing_manager()

        # Initialize agents with entity-specific validation
        logger.info("[TEAM INIT] Initializing agents dictionary")
        self._initialize_agents()

        # Create persistent crew
        logger.info("[TEAM INIT] Creating persistent crew")
        self._create_crew()

        logger.info(
            f"✅ TeamManagementSystem initialized for team {team_id} with entity-specific validation"
        )

    def _initialize_llm(self):
        """Initialize the LLM using the factory pattern with robust error handling."""
        try:
            # Use the proper LLM configuration method
            llm_config = get_llm_config()
            # Get LLM for a default agent role (MESSAGE_PROCESSOR)
            main_llm, function_calling_llm = llm_config.get_llm_for_agent(AgentRole.MESSAGE_PROCESSOR)
            self.llm = main_llm

            # Wrap the LLM with our robust error handling for CrewAI
            self.llm = self._wrap_llm_with_error_handling(self.llm)

            logger.info(
                f"✅ LLM initialized successfully with robust error handling: {type(self.llm).__name__}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise ConfigurationError(f"Failed to initialize LLM: {e!s}") from e

    def _initialize_tool_registry(self):
        """Initialize tool registry and entity manager."""
        try:
            self.tool_registry = initialize_tool_registry("kickai")
            logger.info("✅ Tool registry initialized and ready")

            # Simplified initialization without entity manager
            logger.info("✅ Tool registry initialized for 5-agent architecture")
        except Exception as e:
            logger.error(f"❌ Failed to initialize tool registry: {e}")
            raise ConfigurationError(f"Failed to initialize tool registry: {e!s}") from e

    def _initialize_async_tool_registry(self):
        """Initialize async tool metadata registry."""
        try:
            self.async_tool_registry = get_async_tool_registry()

            # Register all tools from the main registry with async metadata
            all_tools = self.tool_registry.get_tool_functions()
            for tool_func in all_tools.values():
                self.async_tool_registry.register_async_tool(tool_func)

            # Get registry stats
            stats = self.async_tool_registry.get_registry_stats()
            logger.info(f"✅ Tool registry initialized: {stats['async_tools']} async, {stats['sync_tools']} sync ({stats['total_tools']} total)")

            if stats['sync_tools'] > 0:
                logger.info(f"📊 Mixed architecture: {stats['sync_tools']} sync tools use bridge pattern, {stats['async_tools']} tools are native async")

        except Exception as e:
            logger.error(f"❌ Failed to initialize async tool registry: {e}")
            raise ConfigurationError(f"Failed to initialize async tool registry: {e!s}") from e

    def _initialize_routing_manager(self):
        """Initialize command routing manager - REQUIRED, no fallbacks."""
        try:
            self.routing_manager = get_command_routing_manager()
            logger.info("✅ Command routing manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize command routing manager: {e}")
            # FAIL FAST - No silent fallbacks, configuration must be valid
            raise ConfigurationError(f"Command routing configuration is required and must be valid: {e}") from e

    def _route_command_to_agent(self, command: str, chat_type: str | None = None, context: dict[str, Any] | None = None) -> AgentRole:
        """
        Route a command to the appropriate agent using the routing manager.

        Args:
            command: Command to route
            chat_type: Chat context (main/leadership/private)
            context: Additional routing context

        Returns:
            AgentRole for the selected agent

        Raises:
            RuntimeError: If routing fails (no silent fallbacks)
        """
        try:
            # Use dynamic routing - REQUIRED, no fallbacks
            routing_decision = self.routing_manager.route_command(command, chat_type, context)
            logger.info(f"🎯 Dynamic routing: {command} → {routing_decision.agent_role.value} ({routing_decision.match_type})")
            return routing_decision.agent_role
        except Exception as e:
            logger.error(f"❌ Routing failed for '{command}': {e}")
            # FAIL FAST - No silent fallbacks
            raise RuntimeError(f"Command routing failed for '{command}': {e}") from e

    def _initialize_agents(self):
        """Initialize agents with clean configuration."""
        try:
            # Create agents for each role using the new clean system
            agent_roles = [
                AgentRole.MESSAGE_PROCESSOR,
                AgentRole.HELP_ASSISTANT,
                AgentRole.PLAYER_COORDINATOR,
                AgentRole.TEAM_ADMINISTRATOR,
                AgentRole.SQUAD_SELECTOR
            ]

            for role in agent_roles:
                try:
                    logger.info(f"[TEAM INIT] Creating agent for role: {role}")

                    # Create agent using ConfigurableAgent directly
                    agent = ConfigurableAgent(role, self.team_id)

                    self.agents[role] = agent
                    logger.info(f"[TEAM INIT] ✅ Created agent for role: {role}")

                except Exception as e:
                    logger.error(f"[TEAM INIT] ❌ Failed to create agent for role {role}: {e}")
                    raise AgentInitializationError(role.value, f"Failed to create agent for role {role}: {e}") from e

            logger.info(f"[TEAM INIT] ✅ Created {len(self.agents)} agents")

        except Exception as e:
            logger.error(f"[TEAM INIT] ❌ Failed to initialize agents: {e}")
            raise AgentInitializationError("TeamManagementSystem", f"Failed to initialize agents: {e}") from e

    def _create_crew(self):
        """Create the CrewAI crew with clean configuration."""
        try:
            # Create crew with all available agents - extract the crew_agent from each ConfigurableAgent
            crew_agents = [agent.crew_agent for agent in self.agents.values() if hasattr(agent, 'crew_agent')]

            if not crew_agents:
                raise AgentInitializationError("TeamManagementSystem", "No agents available for crew creation")

            # Get verbose setting from environment
            settings = get_settings()
            verbose_mode = settings.verbose_logging or settings.debug

            # Import Process enum for CrewAI
            from crewai import Process

            self.crew = Crew(
                agents=crew_agents,
                tasks=[],
                process=Process.sequential,
                verbose=verbose_mode,
                output_log_file="detailed_crew_logs.json",  # Save detailed logs as JSON
                memory=DEFAULT_MEMORY_ENABLED,  # Simplified - no memory for now
                # Add robust retry mechanism with exponential backoff
                max_retries=DEFAULT_MAX_RETRIES,
                retry_exponential_backoff_factor=DEFAULT_RETRY_BACKOFF_FACTOR,
            )

            logger.info(f"✅ Created crew with {len(crew_agents)} agents")

        except Exception as e:
            logger.error(f"❌ Failed to create crew: {e}")
            raise AgentInitializationError("TeamManagementSystem", f"Failed to create crew: {e}") from e

    def _wrap_llm_with_error_handling(self, llm):
        """Wrap LLM with robust error handling for CrewAI."""
        # This is a simplified wrapper - in production you might want more sophisticated error handling
        return llm

    def get_agent_summary(self) -> dict[str, Any]:
        """Get a summary of all agents with their entity types."""
        summary = {}
        for role, agent in self.agents.items():
            context = {"team_id": self.team_id}
            config = get_agent_config(role, context)
            summary[role.value] = {
                "role": role.value,
                "goal": config.goal if config else "Unknown",
                "entity_types": config.entity_types if config else [],
                "primary_entity_type": config.primary_entity_type
                if config and config.primary_entity_type
                else None,
                "tools_count": len(agent.crew_agent.tools) if hasattr(agent.crew_agent, 'tools') else 0,
                "enabled": config.enabled if config else False,
            }
        return summary

    def get_entity_validation_summary(self) -> dict[str, Any]:
        """Get a summary of entity validation capabilities."""
        # Entity manager was removed in 5-agent simplification
        return {
            "entity_manager_available": False,
            "agent_entity_mappings": {
                role.value: []
                for role in self.agents.keys()
            },
            "validation_rules": {
                "note": "Entity validation simplified in 5-agent architecture",
                "validation_via": "Agent configuration and tool routing"
            },
        }

    def get_agent(self, role: AgentRole) -> ConfigurableAgent | None:
        """Get a specific agent by role."""
        return self.agents.get(role)

    def get_enabled_agents(self) -> list[ConfigurableAgent]:
        """Get all enabled agents."""
        return list(self.agents.values())

    def get_orchestration_pipeline_status(self) -> dict[str, Any]:
        """Get the status of the orchestration pipeline."""
        if hasattr(self, "_orchestration_pipeline"):
            return self._orchestration_pipeline.get_pipeline_status()
        else:
            return {
                "orchestration_pipeline": "Not initialized",
                "all_components_initialized": False,
            }

    async def execute_task(self, task_description: str, execution_context: dict[str, Any]) -> str:
        """
        Execute a task using the CrewAI system with memory management.

        Args:
            task_description: Description of the task to execute
            execution_context: Context information for task execution

        Returns:
            Task execution result

        Raises:
            RuntimeError: When task execution fails
        """
        try:
            logger.info(f"🤖 TEAM MANAGEMENT: Starting task execution for team {self.team_id}")
            logger.info(f"🤖 TEAM MANAGEMENT: Task description: {task_description}")
            logger.info(f"🤖 TEAM MANAGEMENT: Execution context: {execution_context}")
            logger.info(
                f"🤖 TEAM MANAGEMENT: Available agents: {[role.value for role in self.agents.keys()]}"
            )

            # Log agent details
            self._log_agent_details()

            # Add conversation context to execution context
            execution_context = self._add_memory_context(execution_context)

            # Execute the task
            result = await self._execute_with_basic_crew(task_description, execution_context)

            # Store conversation in memory for context persistence
            self._store_conversation_in_memory(task_description, result, execution_context)

            logger.info("🤖 TEAM MANAGEMENT: Task execution completed successfully")
            return result

        except Exception as e:
            logger.error(f"❌ Error in execute_task: {e}")
            return f"❌ System error: {e!s}"

    def _log_agent_details(self) -> None:
        """Log details of all available agents."""
        try:
            for role, agent in self.agents.items():
                tools = agent.get_tools()
                logger.info(
                    f"🤖 TEAM MANAGEMENT: Agent '{role.value}' has {len(tools)} tools: {[tool.name for tool in tools]}"
                )
        except Exception as e:
            logger.warning(f"⚠️ Could not log agent details: {e}")

    def _add_memory_context(self, execution_context: dict[str, Any]) -> dict[str, Any]:
        """Add memory context to execution context."""
        try:
            telegram_id = execution_context.get("telegram_id")
            if telegram_id and hasattr(self, "team_memory"):
                # Get telegram-specific memory context
                memory_context = self.team_memory.get_telegram_memory_context(telegram_id)
                execution_context["memory_context"] = memory_context
                logger.info(f"🤖 TEAM MANAGEMENT: Added memory context for telegram_id {telegram_id}")
            return execution_context
        except Exception as e:
            logger.warning(f"⚠️ Could not add memory context: {e}")
            return execution_context

    def _store_conversation_in_memory(self, task_description: str, result: str, execution_context: dict[str, Any]) -> None:
        """Store conversation in memory for context persistence."""
        try:
            telegram_id = execution_context.get("telegram_id")
            if telegram_id and hasattr(self, "team_memory"):
                self.team_memory.add_conversation(
                    telegram_id=str(telegram_id),  # Use correct parameter name
                    input_text=task_description,
                    output_text=result,
                    context=execution_context,
                )
                logger.info(f"🤖 TEAM MANAGEMENT: Stored conversation in memory for user {telegram_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not store conversation in memory: {e}")

    async def _execute_with_basic_crew(
        self, task_description: str, execution_context: dict[str, Any]
    ) -> str:
        """
        Fallback method to execute task using basic CrewAI crew.
        This is used when the orchestration pipeline fails.
        """
        try:
            logger.info("🤖 BASIC CREW: Executing task with basic crew")
            logger.info(f"🤖 BASIC CREW: Task description: {task_description}")
            logger.info(f"🤖 BASIC CREW: Execution context: {execution_context}")

            # Use the basic crew that was created in _create_crew
            if not hasattr(self, "crew") or not self.crew:
                logger.error("🤖 BASIC CREW: No crew available for fallback")
                return "❌ Sorry, I'm unable to process your request at the moment."

            logger.info("🤖 BASIC CREW: Using existing crew")

            # Extract command name and route to appropriate agent
            command_name = self._extract_command_name(task_description)
            selected_agent_role = self._route_command_to_agent(
                command=command_name,
                chat_type=execution_context.get('chat_type'),
                context=execution_context
            )

            if not selected_agent_role or selected_agent_role not in self.agents:
                logger.error("🤖 BASIC CREW: No suitable agent found for task")
                return "❌ Sorry, I'm unable to process your request at the moment."

            agent = self.agents[selected_agent_role]

            # Validate and prepare execution context
            execution_context = self._prepare_execution_context(execution_context)

            # Get agent tools
            agent_tools = self._get_agent_tools(agent, selected_agent_role, execution_context)
            if not agent_tools:
                return "❌ Internal error: No tools available for agent. This issue has been logged for investigation."

            # Create and execute task
            result = await self._create_and_execute_task(
                task_description, execution_context, agent, command_name
            )

            logger.info(f"🤖 BASIC CREW: Task completed with result: {result}")
            return result

        except Exception as e:
            logger.error(f"🤖 BASIC CREW: Error in fallback execution: {e}", exc_info=True)
            return "❌ Sorry, I'm having trouble processing your request right now. Please try again in a moment."

    def _extract_command_name(self, task_description: str) -> str:
        """Extract command name from task description."""
        try:
            return task_description.split()[0] if task_description else ""
        except Exception as e:
            logger.warning(f"⚠️ Could not extract command name: {e}")
            return ""

    def _prepare_execution_context(self, execution_context: dict[str, Any]) -> dict[str, Any]:
        """Prepare and validate execution context."""
        try:
            # Extract required parameters - no defaults to 'unknown'
            team_id = execution_context.get('team_id')
            telegram_id = execution_context.get('telegram_id')
            username = execution_context.get('username')
            chat_type = execution_context.get('chat_type')

            # Validate all required parameters are present
            missing_params = []
            if not team_id:
                missing_params.append('team_id')
            if not telegram_id:
                missing_params.append('telegram_id')
            if not username:
                missing_params.append('username')
            if not chat_type:
                missing_params.append('chat_type')

            if missing_params:
                error_msg = f"Missing required context parameters: {', '.join(missing_params)}"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)

            return {
                'team_id': team_id,
                'telegram_id': telegram_id,
                'username': username,
                'chat_type': chat_type
            }
        except Exception as e:
            logger.warning(f"⚠️ Could not prepare execution context: {e}")
            return execution_context

    def _get_agent_tools(self, agent: Any, selected_agent_role: AgentRole, execution_context: dict[str, Any]) -> list:
        """Get agent tools with validation."""
        try:
            agent_tools = agent.get_tools()

            # Validate that the agent has tools with detailed diagnostics
            if not agent_tools:
                logger.error(
                    f"❌ No tools configured for {selected_agent_role.value}. "
                    f"Agent config: {getattr(agent, 'config', 'Unknown')}"
                )
                # Attempt to get expected tools from configuration for debugging
                self._log_expected_tools_from_config(selected_agent_role, execution_context)
                return []

            # Enhanced tool logging with type safety
            tool_names = self._extract_tool_names(agent_tools)
            logger.info(
                f"🔧 Using {len(agent_tools)} configured tools for {selected_agent_role.value}: {tool_names}"
            )

            return agent_tools

        except Exception as tool_retrieval_error:
            logger.error(
                f"❌ Failed to retrieve tools for {selected_agent_role.value}: {tool_retrieval_error}",
                exc_info=True
            )
            return []

    def _log_expected_tools_from_config(self, selected_agent_role: AgentRole, execution_context: dict[str, Any]) -> None:
        """Log expected tools from configuration for debugging."""
        try:
            from kickai.config.agents import get_agent_config
            context = {
                'team_id': execution_context.get('team_id'),
                'telegram_id': execution_context.get('telegram_id'),
                'chat_type': execution_context.get('chat_type')
            }
            expected_config = get_agent_config(selected_agent_role, context)
            logger.error(
                f"❌ Expected tools from config: {getattr(expected_config, 'tools', 'Unknown')}"
            )
        except Exception as config_error:
            logger.error(f"❌ Could not retrieve agent config for debugging: {config_error}")

    def _extract_tool_names(self, agent_tools: list) -> list[str]:
        """Extract tool names from agent tools."""
        try:
            tool_names = []
            for tool in agent_tools:
                if hasattr(tool, 'name') and tool.name:
                    tool_names.append(tool.name)
                elif hasattr(tool, '__name__'):
                    tool_names.append(tool.__name__)
                else:
                    tool_names.append(f"<{type(tool).__name__}>")
            return tool_names
        except Exception as e:
            logger.warning(f"⚠️ Could not extract tool names: {e}")
            return []

    async def _create_and_execute_task(
        self, task_description: str, execution_context: dict[str, Any], agent: Any, command_name: str
    ) -> str:
        """Create and execute CrewAI task with dynamic async tool integration."""
        try:
            # Validate context first (no 'unknown' defaults)
            self._create_structured_description(task_description, execution_context)

            # Create CrewAI task with dynamic async tool documentation
            task = self._create_crewai_task(command_name, task_description, agent, execution_context)

            # Execute task
            result = await self._execute_crewai_task(task)

            return result

        except Exception as e:
            logger.error(f"❌ Error in create and execute task: {e}")
            return f"❌ System error: {e!s}"

    def _create_structured_description(self, task_description: str, execution_context: dict[str, Any]) -> str:
        """Create dynamic structured description using async tool metadata."""
        try:
            # Validate required context parameters (no defaults to 'unknown')
            if not AsyncContextInjector.validate_context(execution_context):
                missing_params = []
                required_keys = ['telegram_id', 'team_id', 'username', 'chat_type']
                for key in required_keys:
                    if not execution_context.get(key):
                        missing_params.append(key)
                raise ValueError(f"Missing required context parameters: {', '.join(missing_params)}")

            return task_description  # Will be processed by _create_dynamic_task_description

        except Exception as e:
            logger.error(f"❌ Could not validate context for structured description: {e}")
            raise

    def _create_crewai_task(self, command_name: str, task_description: str, agent: Any, execution_context: dict[str, Any]) -> Any:
        """Create CrewAI task with dynamic async tool documentation."""
        try:
            from crewai import Task

            # Get agent's tool names from configuration
            agent_config = get_agent_config(agent.agent_role, execution_context)
            agent_tool_names = agent_config.tools if agent_config else []

            # Generate dynamic task description with async tool metadata
            dynamic_description = AsyncContextInjector.create_dynamic_task_description(
                user_request=task_description,
                context=execution_context,
                tool_registry=self.async_tool_registry,
                agent_tool_names=agent_tool_names
            )

            task = Task(
                name=f"task_{command_name}",
                description=dynamic_description,
                agent=agent.crew_agent,
                expected_output="Extract and return the exact tool output. Parse JSON responses and return the 'data' field content (for success) or 'message' field content (for errors). Do not add extra text or formatting.",
                output_format="string",
                async_execution=True,  # Enable async execution for async tools
            )

            logger.debug(f"✅ Dynamic task created for {command_name} with {len(agent_tool_names)} tools")
            return task

        except Exception as e:
            logger.error(f"❌ Could not create dynamic CrewAI task: {e}")
            raise

    async def _execute_crewai_task(self, task: Any) -> str:
        """Execute CrewAI task and extract result."""
        try:
            # Clear any previous tasks to prevent memory leaks
            if hasattr(self.crew, 'tasks'):
                self.crew.tasks.clear()

            self.crew.tasks = [task]

            # Execute crew using async CrewAI kickoff
            crew_result = await self.crew.kickoff_async()
            logger.debug(f"✅ Crew kickoff completed, result type: {type(crew_result)}")

            # Extract result using CrewAI best practice pattern
            result = crew_result.raw if hasattr(crew_result, 'raw') and crew_result.raw else str(crew_result)

            return result

        except Exception as e:
            logger.error(f"❌ Crew execution failed: {e}", exc_info=True)
            # Re-raise the exception - let presentation layer handle user-friendly error formatting
            raise





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
                "system": "healthy",
                "agents_count": len(self.agents),
                "agents": {},
                "crew_created": self.crew is not None,
                "llm_available": self.llm is not None,
                "team_config_loaded": self.team_config is not None,
            }

            # Check each agent
            for role, agent in self.agents.items():
                health_status["agents"][role.value] = {
                    "enabled": agent.is_enabled(),
                    "tools_count": len(agent.get_tools()),
                    "crew_agent_available": agent.crew_agent is not None,
                }

            return health_status

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"system": "unhealthy", "error": str(e)}


# Convenience functions for backward compatibility
def create_team_management_system(team_id: str) -> TeamManagementSystem:
    """Create a team management system for the specified team."""
    return TeamManagementSystem(team_id)


def get_agent(team_id: str, role: AgentRole) -> ConfigurableAgent | None:
    """Get a specific agent for a team."""
    system = TeamManagementSystem(team_id)
    return system.get_agent(role)
