"""
Configurable Agent for KICKAI System

This module provides a configurable agent that can be used with different
configurations and behavioral mixins.
"""

import logging
import traceback
from typing import Any

from crewai import Agent

from kickai.config.agents import get_agent_config
from kickai.core.enums import AgentRole
from kickai.core.exceptions import AgentInitializationError

# Removed custom tool output capture - using CrewAI native tools_results

logger = logging.getLogger(__name__)


class LoggingCrewAIAgent(Agent):
    """CrewAI Agent with enhanced logging capabilities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"🤖 Created CrewAI Agent: {self.role}")


from kickai.agents.agent_types import AgentContext
from kickai.agents.tools_manager import AgentToolsManager


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

        # Set agent-specific temperature for data-critical agents
        agent_llm = self._get_agent_specific_llm()

        # Use CrewAI's native tool handling - no custom wrapping needed
        crew_agent = LoggingCrewAIAgent(
            role=self.context.config.role,
            goal=self.context.config.goal,
            backstory=self.context.config.backstory,
            tools=tools,
            llm=agent_llm,
            verbose=True,
            # CrewAI best practices for preventing hallucination
            max_iter=1,  # Limit iterations to prevent elaboration
        )

        # Log final agent LLM configuration for verification
        final_temp = getattr(crew_agent.llm, "temperature", "unknown")
        final_model = getattr(crew_agent.llm, "model_name", "unknown")
        logger.info(
            f"🌡️ AGENT CREATED: {self.context.role.value} with LLM temperature: {final_temp}, model: {final_model}"
        )

        return crew_agent

    def _get_tools_for_role(self, tool_names: list[str]) -> list[Any]:
        """Get tools for a specific role. Tools are validated at factory level."""
        return self._tools_manager.get_tools_for_role(self.context.role)

    def _get_agent_specific_llm(self) -> Any:
        """Get agent-specific LLM with appropriate temperature."""
        try:
            from kickai.core.enums import AgentRole

            # Default LLM from context
            base_llm = self.context.llm

            # Set temperature 0.1 for data-critical agents to prevent hallucination
            data_critical_agents = [
                AgentRole.PLAYER_COORDINATOR,
                AgentRole.HELP_ASSISTANT,
                AgentRole.MESSAGE_PROCESSOR,
                AgentRole.FINANCE_MANAGER,
            ]

            # Set temperature 0.2 for onboarding agent
            onboarding_agents = [AgentRole.ONBOARDING_AGENT]

            # Set temperature 0.3 for administrative agents
            administrative_agents = [AgentRole.TEAM_MANAGER, AgentRole.AVAILABILITY_MANAGER]

            if self.context.role in data_critical_agents:
                temperature = 0.1
            elif self.context.role in onboarding_agents:
                temperature = 0.2
            elif self.context.role in administrative_agents:
                temperature = 0.3
            else:
                # Return original LLM for creative agents (0.7 default)
                return base_llm

            # Create a copy of the LLM with appropriate temperature
            if hasattr(base_llm, "temperature"):
                # Check if this is our RobustLiteLLMChatModel
                if hasattr(base_llm, "model_name") and hasattr(base_llm, "api_key"):
                    # For our RobustLiteLLMChatModel
                    agent_llm = type(base_llm)(
                        model_name=base_llm.model_name,
                        api_key=base_llm.api_key,
                        temperature=temperature,
                        timeout=base_llm.timeout,
                        max_retries=base_llm.max_retries,
                    )
                    logger.info(
                        f"🌡️ Set temperature {temperature} for {self.context.role.value} agent"
                    )
                    return agent_llm
                else:
                    # For other LLM types, try to preserve the original model name
                    model_name = getattr(base_llm, "model_name", None)
                    if model_name is None:
                        # If no model_name attribute, try to get it from the class name or other attributes
                        model_name = getattr(base_llm, "__class__.__name__", "unknown-model")

                    # Create new instance with same type but different temperature
                    agent_llm = type(base_llm)(
                        model_name=model_name,
                        temperature=temperature,
                        **{
                            k: v
                            for k, v in base_llm.__dict__.items()
                            if k not in ["temperature", "model_name"]
                        },
                    )
                    logger.info(
                        f"🌡️ Set temperature {temperature} for {self.context.role.value} agent"
                    )
                    return agent_llm
            else:
                logger.warning(f"⚠️ Could not set temperature for LLM type: {type(base_llm)}")

            # Return original LLM for other agents
            return base_llm

        except Exception as e:
            logger.warning(f"⚠️ Failed to create agent-specific LLM: {e}")
            # Return original LLM if creation fails
            return self.context.llm

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
            "team_id": self.context.team_id,
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

    def _enhance_task_with_anti_hallucination_instructions(
        self, task_description: str, context: dict[str, Any] | None = None
    ) -> str:
        """Enhance task description with anti-hallucination instructions for data-critical tasks."""
        try:
            # Check if this is a task that requires strict factual adherence
            requires_anti_hallucination = any(
                [
                    "get_active_players" in task_description.lower(),
                    ("list" in task_description.lower() and "player" in task_description.lower()),
                    "/list" in task_description.lower(),
                    "show players" in task_description.lower(),
                    "team roster" in task_description.lower(),
                    "get_my_status" in task_description.lower(),
                    "myinfo" in task_description.lower(),
                    "/myinfo" in task_description.lower(),
                    "get_player_status" in task_description.lower(),
                ]
            )

            if not requires_anti_hallucination:
                return task_description

            # Create enhanced task description with strict anti-hallucination instructions
            anti_hallucination_instructions = """
🚨 CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:

1. NEVER invent or add data that doesn't exist in the tool output
2. NEVER add players, phone numbers, or IDs that weren't returned by tools
3. NEVER modify, add to, or change any tool output
4. Return tool outputs EXACTLY as received - NO modifications
5. If a tool shows 2 players, don't invent a 3rd player like "Saim"
6. Be 100% factual and accurate - no creative additions

CRITICAL: Your response MUST be EXACTLY what the tools return, nothing more, nothing less.
"""

            enhanced_task = f"{task_description}\n\n{anti_hallucination_instructions}"

            logger.info(
                f"🔧 Enhanced task with anti-hallucination instructions for {self.context.role.value}"
            )
            return enhanced_task

        except Exception as e:
            logger.warning(f"⚠️ Failed to enhance task with anti-hallucination instructions: {e}")
            return task_description

    def _is_data_critical_task(self, task_description: str) -> bool:
        """Check if this is a data-critical task that requires strict factual adherence."""
        data_critical_keywords = [
            "get_active_players",
            "list",
            "show players",
            "team roster",
            "get_my_status",
            "myinfo",
            "get_player_status",
            "status",
        ]

        task_lower = task_description.lower()
        return any(keyword in task_lower for keyword in data_critical_keywords)

    def _get_structured_output_format(self, task_description: str) -> str:
        """Get structured output format for data-critical tasks."""
        if self._is_data_critical_task(task_description):
            return """
CRITICAL: Your response MUST be EXACTLY what the tools return, nothing more, nothing less.
Do not add any additional information, players, or data that wasn't in the tool output.
"""
        return "Provide a clear and helpful response based on the tool results."

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Execute a task with this agent."""
        try:
            logger.info(
                f"🚀 [CONFIGURABLE AGENT] Starting task execution for {self.context.role.value if self.context.role else 'Unknown'}"
            )
            logger.info(f"📝 Task: {task}")
            logger.info(f"🔧 Context: {context}")

            # Skip temperature setting for now to avoid startup issues

            from crewai import Crew, Task

            # Ensure task is a string
            if not isinstance(task, str):
                task = str(task)

            logger.info(
                f"🚀 [CONFIGURABLE AGENT] Executing task for {self.context.role}: {task[:50]}..."
            )

            # No need to clear tool captures - using CrewAI native tools_results

            # Create a CrewAI Task and Crew for proper execution

            # Create a task for this agent with robust context enhancement
            enhanced_task = task
            if context:
                context_info = []
                tool_instructions = []

                for key, value in context.items():
                    # Handle different value types robustly
                    if value is None:
                        context_info.append(f"{key}: null")
                    elif isinstance(value, str):
                        if value.strip():
                            context_info.append(f"{key}: {value}")
                            # Add specific instructions for chat_type
                            if key == "chat_type":
                                tool_instructions.append(
                                    f"ALWAYS pass {key}='{value}' when calling tools that require it (like get_my_status, get_active_players)"
                                )
                        else:
                            context_info.append(f"{key}: empty")
                    else:
                        context_info.append(f"{key}: {value!s}")

                if context_info:
                    enhanced_task = (
                        f"{task}\n\nAvailable context parameters: {', '.join(context_info)}"
                    )

                    if tool_instructions:
                        enhanced_task += "\n\nCRITICAL TOOL INSTRUCTIONS:\n" + "\n".join(
                            tool_instructions
                        )

                    enhanced_task += "\n\nPlease use these context parameters when calling tools that require them."

            # Enhance task with anti-hallucination instructions for data-critical tasks
            enhanced_task = self._enhance_task_with_anti_hallucination_instructions(
                enhanced_task, context
            )

            # CRITICAL: Double-check agent temperature for debugging
            agent_llm = self._crew_agent.llm
            actual_temperature = getattr(agent_llm, "temperature", "unknown")
            logger.info(
                f"🌡️ EXECUTION CHECK: {self.context.role.value} agent using temperature: {actual_temperature}"
            )

            # Check if this is a data-critical task that requires memory disabled
            is_data_critical = self._is_data_critical_task(task)

            # Get structured output format for data-critical tasks
            structured_output = self._get_structured_output_format(task)

            # Create task with enhanced anti-hallucination instructions
            crew_task = Task(
                description=enhanced_task,
                agent=self._crew_agent,
                expected_output=structured_output,
                config=context or {},  # Pass context data through config for reference
                # CrewAI task settings for strict output control
                async_execution=False,  # Synchronous execution for better control
                human_input=False,  # No human input that could influence output
            )

            from crewai import Process

            # Temporarily disable memory to resolve CrewAI + Gemini compatibility issues
            memory_enabled = (
                settings.crewai_memory_enabled  # Use setting-based memory enablement
            )
            memory_config = None

            if memory_enabled and not is_data_critical:
                from kickai.core.settings import get_settings
                settings = get_settings()
                
                # Use settings-based memory configuration
                if settings.crewai_memory_provider == "huggingface":
                    # Use Hugging Face API token for embeddings
                    memory_config = {
                        "provider": "huggingface",
                        "config": {
                            "api_key": settings.huggingface_api_token,
                            "model": settings.crewai_memory_model
                        },
                    }
                else:
                    # Use Google API key for other providers (google, openai)
                    memory_config = {
                        "provider": settings.crewai_memory_provider,
                        "config": {
                            "api_key": settings.google_api_key, 
                            "model": settings.crewai_memory_model
                        },
                    }
                
                # Log memory configuration for debugging
                logger.info(f"🧠 Memory enabled with provider: {settings.crewai_memory_provider}, model: {settings.crewai_memory_model}")

            # Create a crew with properly configured memory using Google Gemini
            crew = Crew(
                agents=[self._crew_agent],
                tasks=[crew_task],
                verbose=True,  # Ensure verbose logging is enabled
                memory=memory_enabled,  # Enable memory with Google Gemini configuration
                memory_config=memory_config,  # Use Google Gemini for embeddings
                # CrewAI anti-hallucination settings
                process=Process.sequential,  # Required: must be sequential or hierarchical
                share_crew=False,  # Don't share crew state that could cause issues
            )

            # Log crew creation for debugging
            logger.info(
                f"🚀 [CONFIGURABLE AGENT] Created crew with {len(crew.agents)} agents, verbose=True"
            )
            logger.info(
                f"🔧 [CONFIGURABLE AGENT] Agent tools: {[tool.name for tool in self._crew_agent.tools]}"
            )

            # Execute using CrewAI's kickoff method
            result = crew.kickoff()

            # Log execution completion with anti-hallucination, memory, and structured output status
            has_anti_hallucination = "🚨 CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:" in enhanced_task
            has_structured_output = "CRITICAL: Your response MUST be EXACTLY" in structured_output
            memory_status = "memory disabled" if is_data_critical else "memory enabled"
            structured_status = "structured output" if has_structured_output else "standard output"
            anti_hallucination_status = (
                "with anti-hallucination instructions"
                if has_anti_hallucination
                else "without special instructions"
            )
            logger.info(
                f"📊 [CONFIGURABLE AGENT] Execution completed successfully {anti_hallucination_status}, {memory_status}, {structured_status}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ [CONFIGURABLE AGENT] Task execution failed: {e}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise


class AgentFactory:
    """Factory for creating configurable agents."""

    def __init__(
        self, team_id: str, llm: Any, tool_registry: Any
    ):  # tool_registry is ToolRegistry object
        self.team_id = team_id
        self.llm = llm
        self.tool_registry = tool_registry

    def _validate_agent_tools(self, role: AgentRole, required_tools: list[str]) -> None:
        """Validate that required tools are available for the agent."""
        available_tools = self.tool_registry.get_tools_for_role(role)
        available_tool_names = [tool.name for tool in available_tools]

        missing_tools = [tool for tool in required_tools if tool not in available_tool_names]
        if missing_tools:
            logger.warning(f"⚠️ Agent {role.value} missing tools: {missing_tools}")

    def create_agent(self, role: AgentRole) -> ConfigurableAgent:
        """Create a configurable agent for the specified role."""
        try:
            # Get agent configuration
            config = get_agent_config(role)

            # Validate required tools
            if config and config.tools:
                self._validate_agent_tools(role, config.tools)

            # Create agent context
            context = AgentContext(
                role=role,
                team_id=self.team_id,
                llm=self.llm,
                tool_registry=self.tool_registry,
                config=config,
            )

            # Create and return the agent
            agent = ConfigurableAgent(context)
            logger.info(f"✅ Created configurable agent for role: {role.value}")
            return agent

        except Exception as e:
            logger.error(f"❌ Failed to create agent for role {role.value}: {e}")
            raise AgentInitializationError(
                f"Failed to create agent for role {role.value}: {e}"
            ) from e

    def create_all_agents(self) -> dict[AgentRole, ConfigurableAgent]:
        """Create all available agents."""
        agents = {}

        for role in AgentRole:
            try:
                agents[role] = self.create_agent(role)
            except Exception as e:
                logger.error(f"❌ Failed to create agent for role {role.value}: {e}")
                # Continue with other agents even if one fails

        logger.info(f"✅ Created {len(agents)} agents")
        return agents

    def get_agent(self, role: AgentRole) -> ConfigurableAgent | None:
        """Get an agent for the specified role."""
        try:
            return self.create_agent(role)
        except Exception as e:
            logger.error(f"❌ Failed to get agent for role {role.value}: {e}")
            return None
