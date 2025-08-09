#!/usr/bin/env python3
"""
Configurable Agent for KICKAI System - CrewAI 2025 Best Practices

This module provides a clean, simplified configurable agent that follows CrewAI 2025 
best practices for context passing and tool parameter handling.
"""

import traceback
from typing import Any, Dict, Set

from crewai import Agent, Crew, Process, Task
from loguru import logger

from kickai.agents.tools_manager import AgentToolsManager
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
            # 1. Tool registry and manager
            from kickai.agents.tool_registry import initialize_tool_registry
            self.tool_registry = initialize_tool_registry("kickai")
            self._tools_manager = AgentToolsManager(self.tool_registry)

            # 2. LLM configuration
            llm_config = get_llm_config()
            # Use per-agent model selection via llm_config
            main_llm, tool_llm = llm_config.get_llm_for_agent(self.agent_role)
            self.llm = main_llm

            # 3. Agent configuration
            # Use default context for agent initialization
            context = {
                "team_name": "KICKAI",
                "team_id": self.team_id,
                "chat_type": "main",
                "user_role": "public",
                "username": "user"
            }
            self.config = get_agent_config(self.agent_role, context)

            # 4. CrewAI agent
            self.crew_agent = self._create_crew_agent()

        except Exception as e:
            logger.error(f"❌ Failed to initialize ConfigurableAgent: {e}")
            raise AgentInitializationError("ConfigurableAgent", f"Agent initialization failed: {e}")

    def _create_crew_agent(self) -> Agent:
        """Create the underlying CrewAI agent with proper configuration."""
        # Get tools for this agent role
        tools = self._tools_manager.get_tools_for_role(self.agent_role)

        # Create agent with optimized configuration
        settings = get_settings()
        # Enforce conservative global cap for safety
        agent_max_rpm = 5
        agent = Agent(
            role=self.config.role,
            goal=self.config.goal,
            backstory=self.config.backstory,
            tools=tools,
            llm=self.llm,
            verbose=True,
            max_iter=self.config.max_iterations,
            max_rpm=agent_max_rpm,
        )

        logger.debug(
            f"🔧 Created CrewAI agent for {self.agent_role.value} with {len(tools)} tools, max_rpm={agent_max_rpm} (global cap)"
        )
        return agent

    def get_tools(self) -> list:
        """Get the tools available for this agent."""
        if hasattr(self.crew_agent, 'tools'):
            return self.crew_agent.tools
        else:
            # Fallback: get tools from tools manager
            return self._tools_manager.get_tools_for_role(self.agent_role)

    def is_enabled(self) -> bool:
        """Check if this agent is enabled."""
        return self.config.enabled if hasattr(self, 'config') else True

    async def execute(self, task_description: str, context: Dict[str, Any]) -> str:
        """
        Execute a task using CrewAI best practices.

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

        logger.info(f"🚀 Executing task for {self.agent_role.value}: {task_description[:50]}...")

        try:
            # Validate context to prevent placeholder values
            self._validate_context(context)

            # Create enhanced task description with context
            enhanced_description = self._enhance_task_description(task_description, context)

            # Create and execute CrewAI task
            result = await self._execute_crewai_task(enhanced_description, context)

            logger.info(f"✅ Task completed for {self.agent_role.value}")
            return result

        except Exception as e:
            logger.error(f"❌ Task execution failed for {self.agent_role.value}: {e}")
            logger.error(traceback.format_exc())
            return f"❌ Task execution failed: {e!s}"

    def _validate_context(self, context: Dict[str, Any]):
        """Validate execution context to ensure it's complete and valid."""
        # CrewAI 2025 native validation - check required keys
        required_keys = ['team_id', 'telegram_id', 'username', 'chat_type', 'user_role', 'is_registered']
        for key in required_keys:
            if key not in context:
                raise ValueError(f"Missing required context key: {key}")
            if context[key] is None:
                raise ValueError(f"Context key '{key}' cannot be None")
        
        logger.debug(f"🔍 Context validated for {self.agent_role.value}")

    def _enhance_task_description(self, task_description: str, context: Dict[str, Any]) -> str:
        """
        Enhance task description with execution context for better LLM understanding.

        This follows CrewAI 2025 best practices by making context visible to the LLM.
        """
        context_info = f"""

EXECUTION CONTEXT FOR TOOL CALLS:
- team_id: "{context['team_id']}"
- telegram_id: {context['telegram_id']}
- username: "{context['username']}"
- chat_type: "{context['chat_type']}"
- user_role: "{context['user_role']}"
- is_registered: {context['is_registered']}

CRITICAL: When calling tools that need context (like get_player_status_by_telegram_id), use these EXACT values as parameters:
- team_id="{context['team_id']}"
- telegram_id={context['telegram_id']}
- chat_type="{context['chat_type']}"
- user_role="{context['user_role']}"
- is_registered={context['is_registered']}"""

        return task_description + context_info

    async def _execute_crewai_task(self, task_description: str, context: Dict[str, Any]) -> str:
        """Execute the actual CrewAI task with proper context handling."""
        logger.debug(f"🔧 Creating task with context: {context}")

        # Create task with context in config (CrewAI 2025 best practice)
        task = Task(
            description=task_description,
            agent=self.crew_agent,
            expected_output="A clear and helpful response based on the user's request.",
            config=context,  # Tools access this via get_task_config()
        )

        # Verify task was created with config
        logger.debug(f"🔍 Task created - has config: {hasattr(task, 'config') and task.config is not None}")
        if hasattr(task, 'config') and task.config:
            logger.debug(f"🔍 Task config keys: {list(task.config.keys())}")

        # CrewAI 2025 native execution - context is passed via task.config
        logger.debug("✅ Context embedded in task for CrewAI native parameter passing")

        # Create and execute crew
        crew = Crew(
            agents=[self.crew_agent],
            tasks=[task],
            process=Process.sequential,
            memory=False,  # Disable memory for stateless execution
            verbose=True,  # Enable verbose logging
        )

        logger.info(f"🚀 Starting CrewAI execution for {self.agent_role.value}")

        # Execute and return result
        result = crew.kickoff()

        logger.info(f"✅ CrewAI execution completed for {self.agent_role.value}")
        return result.raw if hasattr(result, 'raw') else str(result)


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
            raise AgentInitializationError(role.value, f"Failed to create agent for role {role.value}: {e}")

    def create_all_agents(self) -> Dict[AgentRole, ConfigurableAgent]:
        """
        Create all enabled agents for the team.

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
                "username": "user"
            }
            enabled_configs = get_enabled_agent_configs(context)

            for role in enabled_configs.keys():
                try:
                    agents[role] = self.create_agent(role)
                    logger.debug(f"✅ Created agent: {role.value}")
                except Exception as e:
                    logger.error(f"❌ Failed to create agent {role.value}: {e}")
                    # Continue creating other agents even if one fails

            logger.info(f"🎉 AgentFactory created {len(agents)} agents for team {self.team_id}")
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


def create_all_agents(team_id: str) -> Dict[AgentRole, ConfigurableAgent]:
    """
    Convenience function to create all agents for a team.

    Args:
        team_id: Team ID for all agents

    Returns:
        Dictionary of all created agents
    """
    factory = AgentFactory(team_id)
    return factory.create_all_agents()
