"""
Configurable Agent for KICKAI System

This module provides a configurable agent that can be used with different
configurations and behavioral mixins.
"""

import logging
import traceback
from dataclasses import dataclass
from typing import Any

from crewai import Agent

from kickai.config.agents import AgentConfig, get_agent_config
from kickai.core.enums import AgentRole
from kickai.core.exceptions import AgentInitializationError, ConfigurationError

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
    config: AgentConfig | None = None
    team_memory: Any | None = None  # Add team memory for context persistence


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
        """Create the underlying CrewAI agent with native memory."""
        try:
            config = self.context.config or get_agent_config(self.context.role)

            # Debug logging to see what we're getting
            logger.info(f"[AGENT DEBUG] Context config type: {type(self.context.config)}")
            logger.info(f"[AGENT DEBUG] Context config: {self.context.config}")
            logger.info(f"[AGENT DEBUG] Context team_memory type: {type(self.context.team_memory)}")
            logger.info(f"[AGENT DEBUG] Context team_memory: {self.context.team_memory}")
            logger.info(f"[AGENT DEBUG] Config type: {type(config)}")
            logger.info(f"[AGENT DEBUG] Config: {config}")

            if not config or not config.enabled:
                raise ConfigurationError(f"Agent configuration not found or disabled for role: {self.context.role}")

            # Get tools for this role
            tools = self._get_tools_for_role(config.tools)

            # Get behavioral mixin if available
            mixin = get_mixin_for_role(self.context.role)

            # Get verbose setting from environment
            from kickai.core.settings import get_settings
            settings = get_settings()
            verbose_mode = settings.verbose_logging or settings.is_development

            # Build agent parameters
            agent_params = {
                "role": config.role.value,
                "goal": config.goal,
                "backstory": config.backstory,
                "tools": tools,
                "llm": self.context.llm,
                "verbose": verbose_mode,  # Use environment-based verbose setting
                "allow_delegation": config.allow_delegation,
                "max_iter": config.max_iterations
            }

            # Add mixin if available
            if mixin:
                agent_params["backstory"] = f"{agent_params['backstory']}\n\n{mixin}"

            logger.info(f"[AGENT FACTORY] Creating agent with {len(tools)} tools")
            agent = LoggingCrewAIAgent(**agent_params)

            return agent

        except Exception as e:
            logger.error(f"[AGENT FACTORY] Error creating agent {self.context.role}: {e}")
            logger.error(f"[AGENT FACTORY] Traceback: {traceback.format_exc()}")
            raise AgentInitializationError(f"Failed to create agent for role {self.context.role}: {e!s}")

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
        """Get the agent's tools."""
        return self._crew_agent.tools

    def is_enabled(self) -> bool:
        """Check if the agent is enabled."""
        return True  # All agents are enabled by default

    async def execute(self, task: str, context: dict[str, Any] = None) -> str:
        """Execute a task using the underlying CrewAI agent with native context passing."""
        try:
            if context is None:
                context = {}

            # Create a task using native CrewAI approach
            from crewai import Task

            # Create task with native context support
            crew_task = Task(
                description=f"""TASK: {task}

EXECUTION CONTEXT:
- User ID: {{user_id}}
- Team ID: {{team_id}}
- Chat ID: {{chat_id}}
- Chat Type: {{chat_type}}
- Username: {{username}}
- Telegram Name: {{telegram_name}}
- Message Text: {{message_text}}
- Is Registered: {{is_registered}}
- Is Player: {{is_player}}
- Is Team Member: {{is_team_member}}

CRITICAL TOOL USAGE INSTRUCTIONS:
When calling tools, you MUST pass the exact values from the execution context above as explicit parameters.

EXAMPLES:
- get_team_overview(team_id="{{team_id}}", user_id="{{user_id}}")
- get_my_status(team_id="{{team_id}}", user_id="{{user_id}}")
- get_all_players(team_id="{{team_id}}")
- send_message(chat_id="{{chat_id}}", text="Your message here", team_id="{{team_id}}")

DO NOT:
- Use placeholder values like "current_user" or "123"
- Call tools without parameters
- Use hardcoded team IDs
- Assume context will be automatically available

ALWAYS:
- Pass team_id="{{team_id}}" explicitly to every tool that needs it
- Pass user_id="{{user_id}}" explicitly to every tool that needs it
- Use the exact values from the execution context above""",
                agent=self._crew_agent,
                expected_output="A clear and helpful response to the user's request"
            )

            # Use native CrewAI context passing - interpolate context into task description
            if context:
                # Convert context to inputs for interpolation
                inputs = {
                    'user_id': context.get('user_id', 'unknown'),
                    'team_id': context.get('team_id', 'unknown'),
                    'chat_id': context.get('chat_id', 'unknown'),
                    'chat_type': context.get('chat_type', 'unknown'),
                    'username': context.get('username', ''),
                    'telegram_name': context.get('telegram_name', ''),
                    'message_text': context.get('message_text', ''),
                    'is_registered': context.get('is_registered', False),
                    'is_player': context.get('is_player', False),
                    'is_team_member': context.get('is_team_member', False)
                }

                # Use native CrewAI interpolation
                crew_task.interpolate_inputs_and_add_conversation_history(inputs)

            # Execute the task using native CrewAI Agent.execute_task() method
            logger.info(f"🚀 [AGENT] Starting execution with agent {self.role}")
            logger.info(f"📋 [AGENT] Task: {task}")
            logger.info(f"🔧 [AGENT] Available tools: {[tool.name for tool in self._crew_agent.tools]}")

            # Enhanced logging for help commands
            is_help_command = task.lower().strip() == "/help" or "help" in task.lower()
            if is_help_command:
                logger.info(f"🔍 [HELP DEBUG] About to execute help command with agent {self.role}")
                logger.info(f"🔍 [HELP DEBUG] Task description: '{task}'")
                logger.info(f"🔍 [HELP DEBUG] Context: {context}")
                logger.info(f"🔍 [HELP DEBUG] Agent tools: {[tool.name for tool in self._crew_agent.tools]}")

            # Use native CrewAI Agent.execute_task() method
            result = self._crew_agent.execute_task(crew_task)

            logger.info(f"✅ [AGENT] Execution completed for {self.role}")

            # Handle result properly
            result_str = str(result)

            # Enhanced logging for help commands
            if is_help_command:
                logger.info("🔍 [HELP DEBUG] Agent execution completed")
                logger.info(f"🔍 [HELP DEBUG] Raw result type: {type(result)}")
                logger.info(f"🔍 [HELP DEBUG] Raw result: {result}")
                logger.info(f"🔍 [HELP DEBUG] Final result string: {result_str}")
                logger.info(f"🔍 [HELP DEBUG] Final result length: {len(result_str)}")
                logger.info(f"🔍 [HELP DEBUG] Final result preview: {result_str[:200]}{'...' if len(result_str) > 200 else ''}")

            logger.debug(f"📄 [AGENT] Result: {result_str[:200]}{'...' if len(result_str) > 200 else ''}")

            return result_str

        except Exception as e:
            logger.error(f"❌ Error executing task with agent {self.role}: {e}")
            return "❌ Sorry, I'm having trouble processing your request right now. Please try again in a moment."


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

    def get_agent(self, role: AgentRole) -> ConfigurableAgent | None:
        """Get an agent by role."""
        try:
            return self.create_agent(role)
        except Exception as e:
            logger.error(f"❌ Failed to get agent for role {role}: {e}")
            return None
