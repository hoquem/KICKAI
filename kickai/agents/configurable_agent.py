"""
Configurable Agent for KICKAI System

This module provides a configurable agent that can be used with different
configurations and behavioral mixins.
"""

import logging
import traceback
from dataclasses import dataclass
from typing import Any, Union

from crewai import Agent

from kickai.config.agents import AgentConfig, get_agent_config
from kickai.core.enums import AgentRole
from kickai.core.exceptions import AgentInitializationError, ConfigurationError
# Removed custom tool output capture - using CrewAI native tools_results

from .behavioral_mixins import get_mixin_for_role
from .team_memory import TeamMemory

logger = logging.getLogger(__name__)


class LoggingCrewAIAgent(Agent):
    """CrewAI Agent with enhanced logging capabilities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"🤖 Created CrewAI Agent: {self.role}")


@dataclass
class AgentContext:
    """Context for creating configurable agents."""
    role: AgentRole
    team_id: str
    llm: Any
    tool_registry: Any
    config: Union[AgentConfig, None] = None
    team_memory: Union[Any, None] = None  # Add team memory for context persistence


class AgentToolsManager:
    """Manages tool assignment for agents."""

    def __init__(self, tool_registry: Any):  # ToolRegistry object
        self.tool_registry = tool_registry
        # Fix: Call len() on the result of get_tool_names(), not on the tool_registry object
        tool_names = tool_registry.get_tool_names() if hasattr(tool_registry, 'get_tool_names') else []
        tool_count = len(tool_names)
        logger.info(f"🔧 AgentToolsManager initialized with {tool_count} tools")

    def get_tools_for_role(self, role: AgentRole, entity_type=None) -> list[Any]:
        """Get tools for a specific role."""
        tools = []

        logger.info(f"[AGENT FACTORY] Getting tools for role: {role}")

        # Get agent configuration
        from kickai.config.agents import get_agent_config
        config = get_agent_config(role)
        if not config:
            logger.warning(f"No configuration found for role {role}")
            return []

        # Tool registry should already be initialized via singleton
        if not self.tool_registry._discovered:
            logger.warning("[AGENT FACTORY] Tool registry not discovered - this should not happen with singleton pattern")

        for tool_name in config.tools:
            # Get the actual tool object from the tool registry
            tool_metadata = self.tool_registry.get_tool(tool_name)
            if tool_metadata and tool_metadata.tool_function:
                # The tool_function is the actual CrewAI tool object
                tools.append(tool_metadata.tool_function)
                logger.info(f"[AGENT FACTORY] ✅ Found tool '{tool_name}' for {role.value}")
            else:
                logger.warning(f"[AGENT FACTORY] ❌ Tool '{tool_name}' not found in registry")

        logger.info(f"[AGENT FACTORY] Returning {len(tools)} tools for {role.value}")
        return tools


class ConfigurableAgent:
    """A configurable agent that can be used with different configurations."""

    def __init__(self, context: AgentContext):
        """Initialize the configurable agent."""
        
        self.context = context
        self._tools_manager = AgentToolsManager(context.tool_registry)
        self._crew_agent = self._create_crew_agent()

        logger.info(f"🤖 ConfigurableAgent created for role: {context.role}")

    def _create_crew_agent(self) -> Agent:
        """Create a CrewAI agent with tools."""
        tools = self._get_tools_for_role(self.context.config.tools)
        
        # Use CrewAI's native tool handling - no custom wrapping needed
        return LoggingCrewAIAgent(
            role=self.context.config.role,
            goal=self.context.config.goal,
            backstory=self.context.config.backstory,
            tools=tools,
            llm=self.context.llm,
            verbose=True
        )

    def _get_tools_for_role(self, tool_names: list[str]) -> list[Any]:
        """Get tools for a specific role. Tools are validated at factory level."""
        return self._tools_manager.get_tools_for_role(self.context.role)

    @property
    def crew_agent(self) -> Agent:
        """Get the underlying CrewAI agent."""
        return self._crew_agent

    @property
    def role(self) -> str:
        """Get the agent's role."""
        return self._crew_agent.role

    @property
    def goal(self) -> str:
        """Get the agent's goal."""
        return self._crew_agent.goal

    @property
    def backstory(self) -> str:
        """Get the agent's backstory."""
        return self._crew_agent.backstory

    @property
    def tools(self) -> list[Any]:
        """Get the agent's tools."""
        return self._crew_agent.tools

    def get_config_summary(self) -> dict[str, Any]:
        """Get a summary of the agent's configuration."""
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "tools_count": len(self.tools),
            "tool_names": [tool.name for tool in self.tools],
            "team_id": self.context.team_id
        }

    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        self._crew_agent.tools.append(tool)
        logger.info(f"🔧 Added tool '{tool.name}' to agent {self.role}")

    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from the agent."""
        for i, tool in enumerate(self._crew_agent.tools):
            if tool.name == tool_name:
                removed_tool = self._crew_agent.tools.pop(i)
                logger.info(f"🔧 Removed tool '{removed_tool.name}' from agent {self.role}")
                return True
        logger.warning(f"⚠️ Tool '{tool_name}' not found in agent {self.role}")
        return False

    def get_tools(self) -> list[Any]:
        """Get all tools available to this agent."""
        return self._crew_agent.tools

    def is_enabled(self) -> bool:
        """Check if the agent is enabled."""
        return self.context.config.enabled if self.context.config else False

    async def execute(self, task: str, context: dict[str, Any] = None) -> str:
        """Execute a task using CrewAI's native context passing."""
        try:
            # Ensure task is a string
            if not isinstance(task, str):
                task = str(task)
            
            logger.info(f"🚀 [CONFIGURABLE AGENT] Executing task for {self.context.role}: {task[:50]}...")
            
            # No need to clear tool captures - using CrewAI native tools_results
            
            # Create a CrewAI Task and Crew for proper execution
            from crewai import Task, Crew
            
            # Create a task for this agent with robust context enhancement
            enhanced_task = task
            if context:
                context_info = []
                for key, value in context.items():
                    # Handle different value types robustly
                    if value is None:
                        context_info.append(f"{key}: null")
                    elif isinstance(value, str):
                        if value.strip():
                            context_info.append(f"{key}: {value}")
                        else:
                            context_info.append(f"{key}: empty")
                    else:
                        context_info.append(f"{key}: {str(value)}")
                
                if context_info:
                    enhanced_task = f"{task}\n\nAvailable context parameters: {', '.join(context_info)}\n\nPlease use these context parameters when calling tools that require them."
            
            crew_task = Task(
                description=enhanced_task,
                agent=self._crew_agent,
                expected_output="A clear and helpful response to the user's request",
                config=context or {}  # Pass context data through config for reference
            )
            
            # Create a crew with just this agent and task
            crew = Crew(
                agents=[self._crew_agent],
                tasks=[crew_task],
                verbose=True
            )
            
            # Execute using CrewAI's kickoff method
            result = crew.kickoff()
            
            # Log execution completion - using CrewAI native tools_results
            logger.info(f"📊 [CONFIGURABLE AGENT] Execution completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [CONFIGURABLE AGENT] Task execution failed: {e}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise


class AgentFactory:
    """Factory for creating agents with different configurations."""

    def __init__(self, team_id: str, llm: Any, tool_registry: Any):  # tool_registry is ToolRegistry object
        """Initialize the agent factory."""
        self.team_id = team_id
        self.llm = llm
        self.tool_registry = tool_registry
        self.team_memory = TeamMemory(team_id)

        logger.info(f"🏭 AgentFactory initialized for team: {team_id}")

    def _validate_agent_tools(self, role: AgentRole, required_tools: list[str]) -> None:
        """Validate that all required tools for an agent are available."""
        missing_tools = []

        for tool_name in required_tools:
            tool_metadata = self.tool_registry.get_tool(tool_name)
            if not tool_metadata or not tool_metadata.tool_function:
                missing_tools.append(tool_name)

        if missing_tools:
            available_tools = self.tool_registry.get_tool_names()
            error_msg = (
                f"Agent '{role.value}' is missing required tools: {missing_tools}. "
                f"Available tools: {available_tools}"
            )
            logger.error(f"❌ {error_msg}")
            raise AgentInitializationError(error_msg)

        logger.info(f"✅ All required tools validated for agent '{role.value}': {required_tools}")

    def create_agent(self, role: AgentRole) -> ConfigurableAgent:
        """Create an agent for a specific role with tool validation."""
        try:
            # Get agent configuration
            config = get_agent_config(role)
            if not config:
                raise AgentInitializationError(f"No configuration found for agent role: {role}")

            if not config.enabled:
                raise AgentInitializationError(f"Agent role '{role.value}' is disabled")

            # Validate that all required tools are available
            self._validate_agent_tools(role, config.tools)

            # Create agent context
            context = AgentContext(
                team_id=self.team_id,
                role=role,
                llm=self.llm,
                tool_registry=self.tool_registry,
                team_memory=self.team_memory,
                config=config
            )

            # Create the agent
            agent = ConfigurableAgent(context)
            logger.info(f"✅ Created agent for role: {role.value} with {len(config.tools)} tools")
            return agent

        except AgentInitializationError:
            # Re-raise AgentInitializationError as-is
            raise
        except Exception as e:
            logger.error(f"❌ Failed to create agent for role {role}: {e}")
            raise AgentInitializationError(f"Failed to create agent for role {role}: {e!s}")

    def create_all_agents(self) -> dict[AgentRole, ConfigurableAgent]:
        """Create all enabled agents for the team with validation."""
        agents = {}
        failed_agents = []

        try:
            # Get all agent roles
            for role in AgentRole:
                try:
                    config = get_agent_config(role)
                    if config and config.enabled:
                        agent = self.create_agent(role)
                        agents[role] = agent
                        logger.info(f"✅ Created agent for role: {role.value}")
                    else:
                        logger.info(f"ℹ️ Skipping disabled agent role: {role.value}")
                except AgentInitializationError as e:
                    failed_agents.append((role, str(e)))
                    logger.error(f"❌ Failed to create agent for role: {role.value} - {e}")
                except Exception as e:
                    failed_agents.append((role, str(e)))
                    logger.error(f"❌ Unexpected error creating agent for role: {role.value} - {e}")

            # Report results
            if failed_agents:
                failed_list = [f"{role.value}: {error}" for role, error in failed_agents]
                logger.warning(f"⚠️ Failed to create {len(failed_agents)} agents: {failed_list}")

            logger.info(f"🎉 Created {len(agents)} agents for team {self.team_id}")
            return agents

        except Exception as e:
            logger.error(f"❌ Failed to create agents: {e}")
            raise AgentInitializationError(f"Failed to create agents: {e!s}")

    def get_agent(self, role: AgentRole) -> Union[ConfigurableAgent, None]:
        """Get an agent by role."""
        try:
            return self.create_agent(role)
        except Exception as e:
            logger.error(f"❌ Failed to get agent for role {role}: {e}")
            return None
