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
from kickai.config.command_routing_manager import get_command_routing_manager

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

    def _initialize_routing_manager(self):
        """Initialize command routing manager - REQUIRED, no fallbacks."""
        try:
            self.routing_manager = get_command_routing_manager()
            logger.info("✅ Command routing manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize command routing manager: {e}")
            # FAIL FAST - No silent fallbacks, configuration must be valid
            raise ConfigurationError(f"Command routing configuration is required and must be valid: {e}")

    def _route_command_to_agent(self, command: str, chat_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> AgentRole:
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
            telegram_id = execution_context.get("telegram_id")
            if telegram_id and hasattr(self, "team_memory"):
                # Get telegram-specific memory context
                memory_context = self.team_memory.get_telegram_memory_context(telegram_id)
                execution_context["memory_context"] = memory_context
                logger.info(f"🤖 TEAM MANAGEMENT: Added memory context for telegram_id {telegram_id}")

            # Use basic crew execution directly
            logger.info("🤖 TEAM MANAGEMENT: Using basic crew execution")
            result = await self._execute_with_basic_crew(task_description, execution_context)

            # Store conversation in memory for context persistence
            if telegram_id and hasattr(self, "team_memory"):
                self.team_memory.add_conversation(
                    telegram_id=str(telegram_id),  # Use correct parameter name
                    input_text=task_description,
                    output_text=result,
                    context=execution_context,
                )
                logger.info(f"🤖 TEAM MANAGEMENT: Stored conversation in memory for user {telegram_id}")

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

                # Use dynamic routing manager for agent selection
                selected_agent_role = self._route_command_to_agent(
                    command=command_name,
                    chat_type=execution_context.get('chat_type'),
                    context=execution_context
                )

                if selected_agent_role and selected_agent_role in self.agents:
                    agent = self.agents[selected_agent_role]

                    # Create task description with embedded context (CrewAI native approach)
                    # Use defensive programming to prevent None values
                    team_id = execution_context.get('team_id') or 'unknown'
                    telegram_id = execution_context.get('telegram_id') or 'unknown' 
                    username = execution_context.get('username') or 'unknown'
                    chat_type = execution_context.get('chat_type') or 'unknown'
                    
                    # Validate critical parameters
                    if team_id == 'unknown' or telegram_id == 'unknown':
                        logger.warning(
                            f"⚠️ Missing critical context: team_id={team_id}, telegram_id={telegram_id}"
                        )
                    
                    # Format task description with context parameters for tool calling
                    structured_description = f"""
                    User Request: {task_description}
                    
                    Context Information:
                    - User Telegram ID: {telegram_id}
                    - Team ID: {team_id} 
                    - Username: {username}
                    - Chat Type: {chat_type}
                    
                    Instructions: Use the provided context information to call tools with the appropriate parameters.
                    Pass telegram_id, team_id, username, and chat_type as direct parameters to tools in STANDARDIZED ORDER.
                    
                    🔧 MANDATORY TOOL SELECTION RULES:
                    - /addplayer: MUST use add_player tool with parameters (telegram_id, team_id, username, chat_type, player_name, phone_number)
                    - /list: MUST use list_team_members_and_players(team_id) for leadership chat or get_active_players(team_id, telegram_id) for main chat
                    - /info, /myinfo, /status: MUST use get_my_status(telegram_id, team_id, chat_type)
                    - /help: MUST use FINAL_HELP_RESPONSE tool
                    - NEVER use send_message for commands that have specific tools
                    
                    IMPORTANT: For get_my_status tool, ALWAYS pass chat_type parameter to determine whether to look up player status (main chat) or team member status (leadership chat).
                    
                    🚨 CRITICAL ANTI-HALLUCINATION RULE 🚨: 
                    Return tool outputs EXACTLY as provided - NEVER add, modify, or invent data.
                    - Tool output is final - DO NOT add extra players, team members, or any data
                    - DO NOT reformat, summarize, or remove emojis, symbols, or formatting
                    - If tool returns 2 players, your response must have EXACTLY 2 players
                    - NEVER add fictional players like "Saim", "Ahmed", etc.
                    
                    MANDATORY TOOL USAGE: You MUST call the appropriate tool for data requests:
                    - NEVER provide made-up or fabricated data - if no tool is called, return "Error: No tool was used to retrieve data"

                    **IMPORTANT: YOUR FINAL ANSWER MUST BE THE EXACT, UNMODIFIED OUTPUT FROM THE TOOL. DO NOT ADD ANY EXTRA TEXT, FORMATTING, OR EXPLANATIONS.**
                    """
                    
                    # Use the agent's configured tools (do NOT override with specific tools)
                    # This ensures agents get their tools from agents.yaml configuration
                    try:
                        agent_tools = agent.get_tools()
                    except Exception as tool_retrieval_error:
                        logger.error(
                            f"❌ Failed to retrieve tools for {selected_agent_role.value}: {tool_retrieval_error}",
                            exc_info=True
                        )
                        return f"❌ Tool retrieval failed: {tool_retrieval_error}"
                    
                    # Validate that the agent has tools with detailed diagnostics
                    if not agent_tools:
                        logger.error(
                            f"❌ No tools configured for {selected_agent_role.value}. "
                            f"Agent config: {getattr(agent, 'config', 'Unknown')}"
                        )
                        # Attempt to get expected tools from configuration for debugging
                        try:
                            from kickai.config.agents import get_agent_config
                            context = {'team_id': team_id, 'telegram_id': telegram_id, 'chat_type': chat_type}
                            expected_config = get_agent_config(selected_agent_role, context)
                            logger.error(
                                f"❌ Expected tools from config: {getattr(expected_config, 'tools', 'Unknown')}"
                            )
                        except Exception as config_error:
                            logger.error(f"❌ Could not retrieve agent config for debugging: {config_error}")
                        
                        return "❌ Internal error: No tools available for agent. This issue has been logged for investigation."
                    
                    # Enhanced tool logging with type safety
                    tool_names = []
                    for tool in agent_tools:
                        if hasattr(tool, 'name') and tool.name:
                            tool_names.append(tool.name)
                        elif hasattr(tool, '__name__'):
                            tool_names.append(tool.__name__)
                        else:
                            tool_names.append(f"<{type(tool).__name__}>")
                    
                    logger.info(
                        f"🔧 Using {len(agent_tools)} configured tools for {selected_agent_role.value}: {tool_names}"
                    )
           
                    # Create a task using CrewAI native approach with agent's configured tools
                    task = Task(
                        description=structured_description,
                        agent=agent.crew_agent,
                        expected_output="The final answer MUST be the exact, raw, and unmodified output from the tool. For example, if the tool returns 'HELLO WORLD', your final answer must also be 'HELLO WORLD'.",
                        output_format="string",  # Ensure output format is specified
                        # NOTE: Do NOT override tools here - let agent use its configured tools

                    )
                    
                    logger.debug(f"✅ Task created with structured description including context")
                    logger.debug(f"🚀 About to kickoff crew")

                    # Add task to crew and execute with enhanced error handling
                    # Clear any previous tasks to prevent memory leaks
                    if hasattr(self.crew, 'tasks'):
                        self.crew.tasks.clear()
                    
                    self.crew.tasks = [task]
                    
                    try:
                        logger.debug(f"🚀 CREW KICKOFF: Starting crew execution")
                        logger.debug(f"🚀 CREW KICKOFF: Task description length: {len(structured_description)} chars")
                        logger.debug(f"🚀 CREW KICKOFF: Agent: {agent.crew_agent.role if hasattr(agent.crew_agent, 'role') else 'unknown'}")
                        
                        # Log the exact prompt being sent to the LLM
                        # Only log full description in debug mode to avoid log pollution
                        if logger.isEnabledFor(logging.DEBUG):
                            # Truncate very long descriptions to prevent log overflow
                            description_preview = (
                                structured_description[:500] + "...[truncated]"
                                if len(structured_description) > 500
                                else structured_description
                            )
                            logger.debug(f"🔍 LLM INPUT: {description_preview}")
                        
                        crew_result = self.crew.kickoff()
                        logger.debug(f"✅ Crew kickoff completed, result type: {type(crew_result)}")
                        
                        # Comprehensive logging of crew result
                        logger.debug(f"🔍 RAW CREW RESULT: {crew_result}")
                        logger.debug(f"🔍 CREW RESULT ATTRIBUTES: {dir(crew_result)}")
                        
                        # Log task execution details to see what tools were called
                        if hasattr(crew_result, "tasks") and crew_result.tasks:
                            for i, task_result in enumerate(crew_result.tasks):
                                logger.debug(f"🔍 TASK {i} RESULT: {task_result}")
                                if hasattr(task_result, "tools_results") and task_result.tools_results:
                                    logger.debug(f"🔍 TASK {i} TOOLS RESULTS: {task_result.tools_results}")
                                if hasattr(task_result, "output"):
                                    logger.debug(f"🔍 TASK {i} OUTPUT: {task_result.output}")
                        
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
                        
                        # Check if there are any tool execution logs we can access
                        if hasattr(crew_result, "tasks_output") and crew_result.tasks_output:
                            for i, output in enumerate(crew_result.tasks_output):
                                logger.debug(f"🔍 TASK OUTPUT {i}: {output}")
                        
                        # Log agent details to verify tool usage
                        if hasattr(agent.crew_agent, "tools") and agent.crew_agent.tools:
                            tool_names = [getattr(tool, 'name', str(tool)) for tool in agent.crew_agent.tools]
                            logger.debug(f"🔍 AGENT TOOLS AVAILABLE: {tool_names}")
                        
                        # Log what the agent was supposed to do
                        logger.debug(f"🔍 EXPECTED TOOL FOR {command_name}: {'add_player' if command_name.lower() == '/addplayer' else 'other'}")

                        # Enhanced CrewAI result extraction with multiple fallbacks
                        result = None
                        
                        # Try different ways to extract the result from CrewAI output
                        extraction_methods = [
                            ("raw.output", lambda cr: hasattr(cr, "raw") and hasattr(cr.raw, "output") and cr.raw.output),
                            ("output", lambda cr: hasattr(cr, "output") and cr.output),
                            ("result", lambda cr: hasattr(cr, "result") and cr.result),
                            ("tasks[0].output", lambda cr: hasattr(cr, "tasks") and len(cr.tasks) > 0 and hasattr(cr.tasks[0], "output") and cr.tasks[0].output),
                            ("tasks_output", lambda cr: hasattr(cr, "tasks_output") and len(cr.tasks_output) > 0 and cr.tasks_output[0]),
                            ("raw", lambda cr: hasattr(cr, "raw") and cr.raw),
                            ("str_conversion", lambda cr: cr)
                        ]
                        
                        for method_name, extractor in extraction_methods:
                            try:
                                extracted = extractor(crew_result)
                                if extracted:
                                    result = str(extracted).strip()
                                    if result:  # Only use non-empty results
                                        logger.debug(f"✅ EXTRACTED FROM {method_name}: '{result[:100]}{'...' if len(result) > 100 else ''}'")
                                        break
                            except Exception as extract_error:
                                logger.debug(f"❌ Failed to extract via {method_name}: {extract_error}")
                                continue
                        
                        # Log the final extracted result
                        logger.debug(f"🔍 FINAL EXTRACTED RESULT: '{result[:100] if result else None}{'...' if result and len(result) > 100 else ''}' (length: {len(result) if result else 0})")
                        
                        # Enhanced validation with better error messaging
                        if not result or result.strip() == "":
                            logger.warning("⚠️ Empty result from crew execution after all extraction methods!")
                            logger.warning(f"⚠️ Crew result type: {type(crew_result)}")
                            logger.warning(f"⚠️ Crew result attributes: {[attr for attr in dir(crew_result) if not attr.startswith('_')]}")
                            logger.warning(f"⚠️ Raw crew_result: {repr(crew_result)}")
                            
                            # Try one more fallback - check for pydantic model data
                            if hasattr(crew_result, "__dict__"):
                                result_dict = crew_result.__dict__
                                logger.debug(f"🔍 Crew result dict: {result_dict}")
                                for key in ["output", "result", "content", "response"]:
                                    if key in result_dict and result_dict[key]:
                                        result = str(result_dict[key]).strip()
                                        logger.debug(f"✅ Extracted from __dict__.{key}: '{result}'")
                                        break
                            
                            if not result:
                                result = "⚠️ Task completed but system could not extract output. This has been logged for investigation."
                            
                    except Exception as crew_error:
                        error_message = str(crew_error)
                        error_type = type(crew_error).__name__
                        
                        logger.error(
                            f"❌ Crew execution failed: {error_message}",
                            exc_info=True,
                            extra={
                                'error_type': error_type,
                                'agent_role': selected_agent_role.value,
                                'team_id': team_id,
                                'task_description_length': len(task_description)
                            }
                        )

                        
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
            
            # Get appropriate LLM based on role using the correct method
            main_llm, function_calling_llm = llm_config.get_llm_for_agent(role)
            llm = main_llm  # Use the main LLM for this agent
            
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
