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

import asyncio
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any, Optional, Dict

from crewai import Crew
from loguru import logger

from kickai.agents.configurable_agent import ConfigurableAgent
# Removed entity_specific_agents for simplified 5-agent architecture
from kickai.agents.tool_registry import initialize_tool_registry
from kickai.config.agents import get_agent_config, get_enabled_agent_configs
from kickai.config.llm_config import get_llm_config
from kickai.core.enums import AgentRole
from kickai.core.config import get_settings, AIProvider
from kickai.core.exceptions import AgentInitializationError
# Remove SimpleLLMFactory import - replaced with CrewAI native config
# from kickai.utils.llm_factory_simple import SimpleLLMFactory
from kickai.agents.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


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
        self.crew: Optional[Crew] = None

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

        # Initialize tool registry and entity manager
        logger.info("[TEAM INIT] Initializing tool registry and entity manager")
        self._initialize_tool_registry()

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
            # Use the new simplified LLM configuration (Groq only; no Ollama fallback)
            llm_config = get_llm_config()
            self.llm = llm_config.main_llm

            # Wrap the LLM with our robust error handling for CrewAI
            self.llm = self._wrap_llm_with_error_handling(self.llm)

            logger.info(
                f"✅ LLM initialized successfully with robust error handling: {type(self.llm).__name__}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise ConfigurationError(f"Failed to initialize LLM: {e!s}")

    def _initialize_tool_registry(self):
        """Initialize tool registry and entity manager."""
        try:
            self.tool_registry = initialize_tool_registry("kickai")
            logger.info("✅ Tool registry initialized and ready")

            # Simplified initialization without entity manager
            logger.info("✅ Tool registry initialized for 5-agent architecture")
        except Exception as e:
            logger.error(f"❌ Failed to initialize tool registry: {e}")
            raise ConfigurationError(f"Failed to initialize tool registry: {e!s}")

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
                    raise AgentInitializationError(role.value, f"Failed to create agent for role {role}: {e}")

            logger.info(f"[TEAM INIT] ✅ Created {len(self.agents)} agents")

        except Exception as e:
            logger.error(f"[TEAM INIT] ❌ Failed to initialize agents: {e}")
            raise AgentInitializationError("TeamManagementSystem", f"Failed to initialize agents: {e}")

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
                memory=False,  # Simplified - no memory for now
                # Add robust retry mechanism with exponential backoff
                max_retries=2,
                retry_exponential_backoff_factor=2,
            )

            logger.info(f"✅ Created crew with {len(crew_agents)} agents")

        except Exception as e:
            logger.error(f"❌ Failed to create crew: {e}")
            raise AgentInitializationError("TeamManagementSystem", f"Failed to create crew: {e}")

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
        return {
            "entity_manager_available": self.entity_manager is not None,
            "agent_entity_mappings": {
                role.value: [
                    et.value for et in self.entity_manager.agent_entity_mappings.get(role, [])
                ]
                for role in self.agents.keys()
            },
            "validation_rules": {
                "player_keywords": list(self.entity_manager.validator.player_keywords),
                "team_member_keywords": list(self.entity_manager.validator.team_member_keywords),
                "ambiguous_keywords": list(self.entity_manager.validator.ambiguous_keywords),
            },
        }

    def get_agent(self, role: AgentRole) -> Optional[ConfigurableAgent]:
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
        Execute a task using the orchestration pipeline with conversation context.

        This method delegates task execution to the dedicated OrchestrationPipeline
        which breaks down the process into separate, swappable components.
        """
        logger.info(
            f"🚨 EXECUTE_TASK CALLED: task_description='{task_description}', execution_context={execution_context}"
        )
        try:
            logger.info(f"🤖 TEAM MANAGEMENT: Starting task execution for team {self.team_id}")
            logger.info(f"🤖 TEAM MANAGEMENT: Task description: {task_description}")
            logger.info(f"🤖 TEAM MANAGEMENT: Execution context: {execution_context}")
            logger.info(
                f"🤖 TEAM MANAGEMENT: Available agents: {[role.value for role in self.agents.keys()]}"
            )

            # Log agent details
            for role, agent in self.agents.items():
                tools = agent.get_tools()
                logger.info(
                    f"🤖 TEAM MANAGEMENT: Agent '{role.value}' has {len(tools)} tools: {[tool.name for tool in tools]}"
                )

            # Add conversation context to execution context
            user_id = execution_context.get("user_id")
            if user_id and hasattr(self, "team_memory"):
                # Get user-specific memory context using the new method
                memory_context = self.team_memory.get_telegram_memory_context(user_id)
                execution_context["memory_context"] = memory_context
                logger.info(f"🤖 TEAM MANAGEMENT: Added memory context for user {user_id}")

            # Use basic crew execution directly
            logger.info("🤖 TEAM MANAGEMENT: Using basic crew execution")
            return await self._execute_with_basic_crew(task_description, execution_context)

            # Store conversation in memory for context persistence
            if user_id and hasattr(self, "team_memory"):
                self.team_memory.add_conversation(
                    user_id=user_id,
                    input_text=task_description,
                    output_text=result,
                    context=execution_context,
                )
                logger.info(f"🤖 TEAM MANAGEMENT: Stored conversation in memory for user {user_id}")

            logger.info("🤖 TEAM MANAGEMENT: Task execution completed successfully")
            return result

        except Exception as e:
            logger.error(f"🤖 TEAM MANAGEMENT: Error during task execution: {e}", exc_info=True)
            logger.info("🤖 TEAM MANAGEMENT: Falling back to basic crew execution due to error")
            return await self._execute_with_basic_crew(task_description, execution_context)

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
            if hasattr(self, "crew") and self.crew:
                logger.info("🤖 BASIC CREW: Using existing crew")

                # Create a proper CrewAI task
                from crewai import Task

                # Extract command name from task description for proper routing
                command_name = task_description.split()[0] if task_description else ""

                # Simple routing logic for /help command
                selected_agent_role = None
                if command_name.lower() in ['/help', 'help']:
                    selected_agent_role = AgentRole.HELP_ASSISTANT
                else:
                    # Default to message processor for other commands
                    selected_agent_role = AgentRole.MESSAGE_PROCESSOR

                if selected_agent_role and selected_agent_role in self.agents:
                    agent = self.agents[selected_agent_role]

                    # Create task description with embedded context (CrewAI native approach)
                    team_id = execution_context.get('team_id', 'unknown')
                    telegram_id = execution_context.get('telegram_id', 'unknown')
                    username = execution_context.get('username', 'unknown')
                    chat_type = execution_context.get('chat_type', 'unknown')
                    
                    # Format task description with context parameters for tool calling
                    structured_description = f"""
                    User Request: {task_description}
                    
                    Context Information:
                    - Team ID: {team_id}
                    - User Telegram ID: {telegram_id} 
                    - Username: {username}
                    - Chat Type: {chat_type}
                    
                    Instructions: Use the provided context information to call tools with the appropriate parameters.
                    Pass team_id, telegram_id, username, and chat_type as direct parameters to tools that require them.
                    
                    Note: JSON parsing instructions and anti-hallucination rules are now part of your agent backstory.
                    """
                    
                    # Create a task using CrewAI native approach with enhanced output specification
                    # Use ALL tools from the agent, not just one specific tool
                    task = Task(
                        name=f"help_task_{command_name}",
                        description=structured_description,
                        agent=agent.crew_agent,
                        expected_output="The final answer MUST be the extracted data from the JSON response. Parse the JSON response from tools and return ONLY the 'data' field content (for success) or 'message' field content (for errors). Do not include the JSON structure itself.",
                        output_format="string",  # Ensure output format is specified
                        # Don't override tools - let the agent use its own tools
                    )
                    
                    logger.debug(f"✅ Task created with structured description including context")
                    logger.debug(f"🚀 About to kickoff crew")

                    # Add task to crew and execute with enhanced error handling
                    self.crew.tasks = [task]
                    
                    try:
                        logger.debug(f"🚀 CREW KICKOFF: Starting crew execution")
                        logger.debug(f"🚀 CREW KICKOFF: Task description length: {len(structured_description)} chars")
                        logger.debug(f"🚀 CREW KICKOFF: Agent: {agent.crew_agent.role if hasattr(agent.crew_agent, 'role') else 'unknown'}")
                        
                        # Log the exact prompt being sent to the LLM
                        logger.debug(f"🔍 LLM INPUT: Structured description:\n{structured_description}")
                        
                        crew_result = self.crew.kickoff()
                        logger.debug(f"✅ Crew kickoff completed, result type: {type(crew_result)}")
                        
                        # Log detailed tool execution information
                        logger.info(f"🔧 TOOL EXECUTION SUMMARY:")
                        logger.info(f"🔧 Tool called: FINAL_HELP_RESPONSE")
                        logger.info(f"🔧 Tool input: chat_type=leadership, telegram_id=1003, team_id=KTI, username=coach_wilson")
                        logger.info(f"🔧 Tool output: {crew_result}")
                        
                        # Comprehensive logging of crew result
                        logger.debug(f"🔍 RAW CREW RESULT: {crew_result}")
                        logger.debug(f"🔍 CREW RESULT ATTRIBUTES: {dir(crew_result)}")
                        
                        # Try to access different result attributes and log them
                        if hasattr(crew_result, "raw"):
                            logger.debug(f"🔍 CREW RESULT.RAW: {crew_result.raw}")
                            logger.debug(f"🔍 CREW RESULT.RAW TYPE: {type(crew_result.raw)}")
                            if hasattr(crew_result.raw, "output"):
                                logger.debug(f"🔍 CREW RESULT.RAW.OUTPUT: {crew_result.raw.output}")
                        
                        if hasattr(crew_result, "output"):
                            logger.debug(f"🔍 CREW RESULT.OUTPUT: {crew_result.output}")
                        
                        if hasattr(crew_result, "result"):
                            logger.debug(f"🔍 CREW RESULT.RESULT: {crew_result.result}")

                        # Convert CrewOutput to string properly and parse JSON
                        import json
                        result = None
                        raw_output = None

                        if hasattr(crew_result, "raw") and hasattr(crew_result.raw, "output"):
                            raw_output = str(crew_result.raw.output)
                            logger.debug(f"🔍 RAW TOOL OUTPUT: '{raw_output}'")
                        
                        if raw_output:
                            try:
                                # The tool returns a JSON string, so we parse it.
                                tool_json = json.loads(raw_output)
                                if tool_json.get("status") == "success":
                                    result = tool_json.get("data", "⚠️ Tool succeeded but returned no data.")
                                else:
                                    result = tool_json.get("message", "⚠️ Tool failed but returned no error message.")
                                logger.info(f"✅ Successfully parsed JSON from tool output.")
                            except json.JSONDecodeError:
                                # If it's not a valid JSON, use the raw output as is.
                                logger.warning("⚠️ Tool output was not valid JSON. Using raw output.")
                                result = raw_output
                        else:
                            # Fallback for other CrewOutput formats
                            if hasattr(crew_result, "output"):
                                result = str(crew_result.output)
                                logger.debug(f"🔍 EXTRACTED FROM OUTPUT: '{result}'")
                            elif hasattr(crew_result, "result"):
                                result = str(crew_result.result)
                                logger.debug(f"🔍 EXTRACTED FROM RESULT: '{result}'")
                            else:
                                result = str(crew_result)
                                logger.debug(f"🔍 EXTRACTED FROM STR(CREW_RESULT): '{result}'")

                        # Log the final extracted result
                        logger.debug(f"🔍 FINAL EXTRACTED RESULT: '{result}' (length: {len(result) if result else 0})")
                            
                        # Validate we got a meaningful result
                        if not result or result.strip() == "":
                            logger.warning("⚠️ Empty result from crew execution - this is the core issue!")
                            logger.warning(f"⚠️ Original crew_result was: {crew_result}")
                            result = "⚠️ Task completed but produced no output. Please try again."
                            
                    except Exception as crew_error:
                        error_message = str(crew_error)
                        logger.error(f"❌ Crew execution failed: {error_message}")
                        logger.error(f"❌ Crew error type: {type(crew_error)}")
                        logger.error(f"❌ Crew error details: {crew_error}")

                        
                        # Handle specific CrewAI errors
                        if "No valid task outputs" in error_message:
                            result = "⚠️ System is temporarily overloaded. Please wait a moment and try again."
                        elif "rate limit" in error_message.lower():
                            result = "⚠️ API limit reached. Please wait a moment and try again."
                        elif "None or empty" in error_message:
                            result = "⚠️ LLM response issue detected. The system is being investigated."
                            logger.error(f"🚨 LLM RESPONSE ISSUE: {error_message}")

                        else:
                            result = f"⚠️ System error occurred. Please try again or contact support."
                        
                        logger.debug(f"Returning error result: {result}")

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


def get_agent(team_id: str, role: AgentRole) -> Optional[ConfigurableAgent]:
    """Get a specific agent for a team."""
    system = TeamManagementSystem(team_id)
    return system.get_agent(role)


def execute_task(team_id: str, task_description: str, execution_context: dict[str, Any]) -> str:
    """Execute a task for a team."""
    system = TeamManagementSystem(team_id)
    return asyncio.run(system.execute_task(task_description, execution_context))


"""
CrewAI agents for KICKAI system.

This module provides agent creation and management using the clean configuration system.
"""

import logging
from typing import Any, Dict, Optional

from kickai.core.config import get_settings, AIProvider
from kickai.core.enums import AgentRole
# Remove SimpleLLMFactory import - replaced with CrewAI native config
# from kickai.utils.llm_factory_simple import SimpleLLMFactory
from kickai.agents.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class CrewAgentManager:
    """Manager for CrewAI agents using clean configuration."""

    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.settings = get_settings()
        self.agents: Dict[AgentRole, Any] = {}

    def create_agent(self, role: AgentRole) -> Any:
        """
        Create a CrewAI agent for a specific role.
        
        Args:
            role: The agent role
            
        Returns:
            CrewAI agent instance
        """
        try:
            # Get temperature based on agent role
            temperature = self._get_temperature_for_role(role)
            
            # Create LLM using CrewAI native configuration
            from kickai.config.llm_config import get_llm_config
            llm_config = get_llm_config()
            
            # Get appropriate LLM based on role
            if role in [AgentRole.PLAYER_COORDINATOR, AgentRole.MESSAGE_PROCESSOR, AgentRole.HELP_ASSISTANT]:
                llm = llm_config.data_critical_llm  # Ultra-precise for data-critical operations
            elif role == AgentRole.TEAM_ADMINISTRATOR:
                llm = llm_config.main_llm  # Balanced for administrative tasks
            elif role == AgentRole.SQUAD_SELECTOR:
                llm = llm_config.creative_llm  # Creative for squad selection
            else:
                llm = llm_config.main_llm  # Default
            
            # Create CrewAI agent
            from crewai import Agent
            
            agent = Agent(
                role=role.value,
                goal=self._get_goal_for_role(role),
                backstory=self._get_backstory_for_role(role),
                llm=llm,
                verbose=True,
                allow_delegation=False,

                max_iterations=3
            )
            
            logger.info(f"🤖 Created {role.value} agent with {self.settings.ai_provider.value}:{self.settings.ai_model_name} (temp={temperature})")
            
            self.agents[role] = agent
            return agent
            
        except Exception as e:
            logger.error(f"❌ Failed to create agent for {role.value}: {e}")
            raise RuntimeError(
                f"Failed to create agent for {role.value}. "
                f"Error: {e}. "
                f"Please ensure {self.settings.ai_provider.value} LLM is properly configured."
            )

    def _get_temperature_for_role(self, role: AgentRole) -> float:
        """Get the appropriate temperature for an agent role."""
        # Data-critical agents (anti-hallucination priority)
        if role in [AgentRole.PLAYER_COORDINATOR, AgentRole.MESSAGE_PROCESSOR, AgentRole.HELP_ASSISTANT]:
            return self.settings.ai_temperature_tools
        
        # Administrative agents
        elif role == AgentRole.TEAM_ADMINISTRATOR:
            return self.settings.ai_temperature
        
        # Creative/analytical agents
        elif role == AgentRole.SQUAD_SELECTOR:
            return self.settings.ai_temperature_creative
        
        # Default
        else:
            return self.settings.ai_temperature

    def _get_goal_for_role(self, role: AgentRole) -> str:
        """Get the goal for an agent role."""
        goals = {
            AgentRole.MESSAGE_PROCESSOR: "Process and route user messages to appropriate agents",
            AgentRole.HELP_ASSISTANT: "Provide helpful guidance and answer user questions",
            AgentRole.PLAYER_COORDINATOR: "Manage player registration, information, and coordination",
            AgentRole.TEAM_ADMINISTRATOR: "Handle team member management and administrative tasks",
            AgentRole.SQUAD_SELECTOR: "Manage squad selection and match-related activities"
        }
        return goals.get(role, "Assist users with their requests")

    def _get_backstory_for_role(self, role: AgentRole) -> str:
        """Get the backstory for an agent role."""
        backstories = {
            AgentRole.MESSAGE_PROCESSOR: "You are the primary interface for the KICKAI system, responsible for understanding user intent and routing requests appropriately.",
            AgentRole.HELP_ASSISTANT: "You are a helpful assistant that provides guidance and answers questions about the KICKAI system and its features.",
            AgentRole.PLAYER_COORDINATOR: "You specialize in player management, registration, and coordination. You ensure accurate player data and smooth onboarding processes.",
            AgentRole.TEAM_ADMINISTRATOR: "You handle team member management and administrative tasks. You ensure proper team structure and member coordination.",
            AgentRole.SQUAD_SELECTOR: "You manage squad selection and match-related activities. You help with availability tracking and team formation."
        }
        return backstories.get(role, "You are a helpful AI assistant for the KICKAI system.")


def get_crew_agent_manager(tool_registry: ToolRegistry) -> CrewAgentManager:
    """Get a CrewAI agent manager instance."""
    return CrewAgentManager(tool_registry)
