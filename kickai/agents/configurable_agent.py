#!/usr/bin/env python3
"""
Configurable Agent for KICKAI System - CrewAI 2025 Best Practices

This module provides a clean, simplified configurable agent that follows CrewAI 2025 
best practices for context passing and tool parameter handling.
"""

import traceback
from typing import Any

from crewai import Agent
from loguru import logger

from kickai.config.agents import get_agent_config
from kickai.config.llm_config import get_llm_config
from kickai.core.config import get_settings
from kickai.core.enums import AgentRole
from kickai.core.exceptions import AgentInitializationError


class ConfigurableAgent:
    """
    A clean, simplified configurable agent for the KICKAI system.

    Features:
    - CrewAI 2025 best practices
    - Clean initialization and execution
    - Proper context handling
    - Error resilience
    - Sequential process execution
    """

    def __init__(self, agent_role: AgentRole, team_id: str):
        """
        Initialize agent with role and team ID.

        Args:
            agent_role: The role this agent should perform
            team_id: The team this agent belongs to
        """
        self.agent_role = agent_role
        self.team_id = team_id

        # Initialize components in clean order
        self._initialize_components()

        logger.info(f"✅ ConfigurableAgent created: {agent_role.value} for team {team_id}")

    def _initialize_components(self):
        """Initialize all required components for the agent."""
        try:
            # 1. Tool registry - get singleton instance (already initialized)
            from kickai.agents.tool_registry import get_tool_registry

            self.tool_registry = get_tool_registry()

            # 2. LLM configuration
            llm_config = get_llm_config()
            # Use per-agent model selection via llm_config
            main_llm, tool_llm = llm_config.get_llm_for_agent(self.agent_role)
            self.llm = main_llm
            self.tool_llm = tool_llm  # Store tool_llm for function calling

            # 3. Agent configuration
            # Use default context for agent initialization
            context = {
                "team_name": "KICKAI",
                "team_id": self.team_id,
                "chat_type": "main",
                "user_role": "public",
                "username": "user",
            }
            self.config = get_agent_config(self.agent_role, context)

            # 4. CrewAI agent
            self.crew_agent = self._create_crew_agent()

        except Exception as e:
            logger.error(f"❌ Failed to initialize ConfigurableAgent: {e}")
            raise AgentInitializationError("ConfigurableAgent", f"Agent initialization failed: {e}")

    def _create_crew_agent(self) -> Agent:
        """Create the underlying CrewAI agent with proper configuration for sequential process."""
        # Get tools for this agent role using direct assignment (CrewAI best practice)
        tools = self._get_tools_for_agent()

        # No delegation tools needed for sequential process - agents work independently

        # Get memory system for this agent
        from kickai.core.memory_manager import get_memory_manager

        memory_manager = get_memory_manager()
        agent_memory = memory_manager.get_memory_for_agent(self.agent_role)

        # Create agent with optimized configuration and memory
        settings = get_settings()
        
        # Manager agent needs delegation enabled for hierarchical process
        # Worker agents should have delegation disabled to focus on their tools
        is_manager = self.agent_role == AgentRole.MANAGER_AGENT
        allow_delegation = is_manager

        # Prepare agent creation parameters
        agent_params = {
            "role": self.config.role,
            "goal": self.config.goal,
            "backstory": self.config.backstory,
            "tools": tools,
            "llm": self.llm,
            "function_calling_llm": self.tool_llm,  # Use tool_llm for function calling
            "verbose": True,
            "max_iter": self.config.max_iterations,
            "memory": agent_memory,  # Enable entity-specific memory
            "allow_delegation": allow_delegation,  # Manager delegates, workers don't
        }
        
        # Add system_template if configured for this agent
        if hasattr(self.config, 'system_template') and self.config.system_template:
            agent_params["system_template"] = self.config.system_template
            logger.debug(f"🎯 Added system_template for {self.agent_role.value}")

        agent = Agent(**agent_params)

        delegation_mode = "manager with delegation" if allow_delegation else "worker without delegation"
        logger.debug(
            f"🔧 Created CrewAI agent for {self.agent_role.value} with {len(tools)} tools ({delegation_mode})"
        )
        return agent

    def _get_tools_for_agent(self) -> list[Any]:
        """
        Get tools for this agent using direct assignment (CrewAI best practice).

        Context is passed via Task.config instead of wrapper injection.
        """
        tools = []

        try:
            # Get tool names from agent config (from YAML)
            tool_names = self.config.tools
            logger.debug(f"🔍 Looking for {len(tool_names)} tools for {self.agent_role.value}")

            # Direct tool lookup from registry (no manager layer)
            for tool_name in tool_names:
                tool_func = self.tool_registry.get_tool_function(tool_name)
                if tool_func:
                    tools.append(tool_func)
                    logger.debug(f"✅ Found tool '{tool_name}' for {self.agent_role.value}")
                else:
                    # Try alternative lookup methods if direct lookup fails
                    all_tools = self.tool_registry.list_all_tools()
                    found_tool = None
                    for tool in all_tools:
                        if tool.name == tool_name:
                            found_tool = tool
                            break

                    if found_tool and found_tool.tool_function:
                        tools.append(found_tool.tool_function)
                        logger.debug(
                            f"✅ Found tool '{tool_name}' via search for {self.agent_role.value}"
                        )
                    else:
                        logger.warning(
                            f"❌ Tool '{tool_name}' not found for {self.agent_role.value}"
                        )

            # For now, skip context injection to avoid callable issues
            # Context will be passed via Task.config instead
            if tools:
                logger.info(
                    f"🔧 Loaded {len(tools)} tools (context via Task.config) for {self.agent_role.value}"
                )
                return tools
            else:
                logger.info(f"🔧 No tools found for {self.agent_role.value}")
                return []

        except Exception as e:
            logger.error(f"❌ Error loading tools for {self.agent_role.value}: {e}")
            return []


    # Delegation methods removed - not needed for sequential process

    def get_tools(self) -> list:
        """Get the tools available for this agent."""
        if hasattr(self.crew_agent, "tools"):
            return self.crew_agent.tools
        else:
            # Fallback: get tools directly from registry
            return self._get_tools_for_agent()

    def is_enabled(self) -> bool:
        """Check if this agent is enabled."""
        return self.config.enabled if hasattr(self, "config") else True

    async def execute(self, task_description: str, context: dict[str, Any]) -> str:
        """
        Execute a task by delegating to the team's persistent crew system.

        This method now acts as a delegation layer to the TeamManagementSystem,
        ensuring all task execution goes through persistent crews with memory
        and proper resource management.

        Args:
            task_description: Description of the task to execute
            context: Execution context with user information

        Returns:
            Result of the task execution

        Raises:
            ValueError: If context is missing or invalid
        """
        if not context:
            raise ValueError("Execution context is required and cannot be empty")

        logger.info(
            f"🚀 Delegating task for {self.agent_role.value} to persistent team system: {task_description[:50]}..."
        )

        try:
            # Validate context to prevent placeholder values
            self._validate_context(context)

            # Get or create the team's persistent management system
            from kickai.core.team_system_manager import get_team_system

            team_system = await get_team_system(self.team_id)

            # Delegate to the persistent crew system
            result = await team_system.execute_task(task_description, context)

            logger.info(f"✅ Task completed for {self.agent_role.value} via persistent crew")
            return result

        except Exception as e:
            logger.error(f"❌ Task delegation failed for {self.agent_role.value}: {e}")
            logger.error(traceback.format_exc())
            return f"❌ Task execution failed: {e!s}"

    def _validate_context(self, context: dict[str, Any]):
        """Validate execution context to ensure it's complete and valid."""
        # CrewAI 2025 native validation - check required keys
        required_keys = [
            "team_id",
            "telegram_id",
            "chat_type",
            "user_role",
            "is_registered",
            "telegram_username",
        ]
        for key in required_keys:
            if key not in context:
                raise ValueError(f"Missing required context key: {key}")
            if context[key] is None:
                raise ValueError(f"Context key '{key}' cannot be None")

        logger.debug(f"🔍 Context validated for {self.agent_role.value}")


class AgentFactory:
    """
    A clean factory for creating configurable agents.

    Simplifies agent creation and management.
    """

    def __init__(self, team_id: str):
        """
        Initialize the factory for a specific team.

        Args:
            team_id: The team ID for all agents created by this factory
        """
        self.team_id = team_id
        logger.debug(f"🏭 AgentFactory initialized for team: {team_id}")

    def create_agent(self, role: AgentRole) -> ConfigurableAgent:
        """
        Create a single configurable agent.

        Args:
            role: The role for the agent to create

        Returns:
            Configured agent ready for execution

        Raises:
            AgentInitializationError: If agent creation fails
        """
        try:
            return ConfigurableAgent(role, self.team_id)
        except Exception as e:
            raise AgentInitializationError(
                role.value, f"Failed to create agent for role {role.value}: {e}"
            )

    def create_all_agents(self) -> dict[AgentRole, ConfigurableAgent]:
        """
        Create all enabled agents for the team with delegation support.

        Returns:
            Dictionary mapping agent roles to configured agents
        """
        agents = {}

        try:
            from kickai.config.agents import get_enabled_agent_configs

            # Use default context for agent creation
            context = {
                "team_name": "KICKAI",
                "team_id": self.team_id,
                "chat_type": "main",
                "user_role": "public",
                "username": "user",
            }
            enabled_configs = get_enabled_agent_configs(context)

            # First pass: create all agents
            for role in enabled_configs.keys():
                try:
                    agents[role] = self.create_agent(role)
                    logger.debug(f"✅ Created agent: {role.value}")
                except Exception as e:
                    logger.error(f"❌ Failed to create agent {role.value}: {e}")
                    # Continue creating other agents even if one fails

            # All agents are independent - no delegation setup needed for sequential process
            logger.info(
                f"🎉 AgentFactory created {len(agents)} independent agents for team {self.team_id}"
            )
            return agents

        except Exception as e:
            logger.error(f"❌ Failed to create agents: {e}")
            return agents  # Return whatever agents were successfully created


# Utility functions for backward compatibility and convenience
def create_agent(role: AgentRole, team_id: str) -> ConfigurableAgent:
    """
    Convenience function to create a single agent.

    Args:
        role: Agent role to create
        team_id: Team ID for the agent

    Returns:
        Configured agent
    """
    factory = AgentFactory(team_id)
    return factory.create_agent(role)


def create_all_agents(team_id: str) -> dict[AgentRole, ConfigurableAgent]:
    """
    Convenience function to create all agents for a team.

    Args:
        team_id: Team ID for all agents

    Returns:
        Dictionary of all created agents
    """
    factory = AgentFactory(team_id)
    return factory.create_all_agents()
