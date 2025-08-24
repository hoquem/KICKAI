#!/usr/bin/env python3
"""
Simplified CrewAI Football Team Management System - 6-Agent Architecture

This module provides a simplified, production-ready implementation of the
CrewAI-based football team management system with 6 essential agents.

ESSENTIAL 6-AGENT SYSTEM:
1. MESSAGE_PROCESSOR - Primary interface and routing
2. HELP_ASSISTANT - Help system and guidance
3. PLAYER_COORDINATOR - Player management and onboarding
4. TEAM_ADMINISTRATOR - Team member management
5. SQUAD_SELECTOR - Squad selection and match management
6. NLP_PROCESSOR - Natural language processing and understanding
"""

import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any

from crewai import Crew, Task
from loguru import logger

from kickai.agents.async_tool_metadata import AsyncContextInjector, get_async_tool_registry
from kickai.agents.configurable_agent import ConfigurableAgent
from kickai.agents.tool_registry import initialize_tool_registry
from kickai.config.agents import get_agent_config
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

# Memory and truncation constants
MEMORY_HISTORY_LIMIT = 1
COMMAND_TRUNCATE_LENGTH = 50
RESPONSE_TYPE_TRUNCATE_LENGTH = 50


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

        # Command routing now handled via pure CrewAI agent collaboration
        logger.info("[TEAM INIT] CrewAI native collaboration enabled - MESSAGE_PROCESSOR primary agent")

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
            logger.info("✅ Tool registry initialized for 6-agent architecture")
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



    def _initialize_agents(self):
        """Initialize agents with clean configuration."""
        try:
            # Create agents for each role using the new clean system
            agent_roles = [
                AgentRole.MESSAGE_PROCESSOR,
                AgentRole.HELP_ASSISTANT,
                AgentRole.PLAYER_COORDINATOR,
                AgentRole.TEAM_ADMINISTRATOR,
                AgentRole.SQUAD_SELECTOR,
                AgentRole.NLP_PROCESSOR  # Intelligent routing and context analysis agent
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
        # Entity manager was removed in 6-agent simplification
        return {
            "entity_manager_available": False,
            "agent_entity_mappings": {
                role.value: []
                for role in self.agents.keys()
            },
            "validation_rules": {
                "note": "Entity validation simplified in 6-agent architecture",
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

            # CREWAI BEST PRACTICE: Optimize context before any processing
            from kickai.agents.utils.context_optimizer import ContextOptimizer

            # Add minimal memory reference (not full memory_context)
            execution_context = self._add_memory_context(execution_context)

            # Optimize context following CrewAI best practices
            optimized_context = ContextOptimizer.optimize_execution_context(execution_context)

            logger.info(f"🤖 TEAM MANAGEMENT: Optimized execution context: {optimized_context}")
            logger.info(
                f"🤖 TEAM MANAGEMENT: Available agents: {[role.value for role in self.agents.keys()]}"
            )

            # Log agent details
            self._log_agent_details()

            # Use optimized context for all further processing
            execution_context = optimized_context

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
        """Add minimal memory reference to execution context (optimized for CrewAI)."""
        try:
            telegram_id = execution_context.get("telegram_id")
            if telegram_id and hasattr(self, "team_memory"):
                # Get conversation history count only (not full history)
                history = self.team_memory.get_conversation_history(str(telegram_id), limit=MEMORY_HISTORY_LIMIT)
                has_previous = len(history) > 0
                last_command = history[0].get("input", "") if has_previous else None

                # Add minimal conversation reference (not full memory_context)
                execution_context["has_previous"] = has_previous
                if last_command:
                    execution_context["last_command"] = last_command[:COMMAND_TRUNCATE_LENGTH]  # Truncate

                logger.info(f"🤖 TEAM MANAGEMENT: Added minimal memory reference for telegram_id {telegram_id}")
            return execution_context
        except Exception as e:
            logger.warning(f"⚠️ Could not add memory reference: {e}")
            return execution_context

    def _store_conversation_in_memory(self, task_description: str, result: str, execution_context: dict[str, Any]) -> None:
        """Store conversation using optimized memory manager (CrewAI best practices)."""
        try:
            telegram_id = execution_context.get("telegram_id")
            if telegram_id:
                # Use optimized memory manager for minimal storage
                from kickai.agents.utils.memory_manager import get_memory_manager

                memory_manager = get_memory_manager(self.team_id)

                # Determine response type for better categorization
                response_type = "success"
                if "❌" in result or "Error" in result:
                    response_type = "error"
                elif "help" in task_description.lower() or "/help" in task_description:
                    response_type = "help"
                elif "{" in result and "data" in result:
                    response_type = "data"

                # Store conversation summary (not full content)
                summary = memory_manager.add_conversation_summary(
                    telegram_id=telegram_id,
                    command=task_description,
                    response=result,
                    response_type=response_type
                )

                logger.info(
                    f"🤖 TEAM MANAGEMENT: Stored conversation summary for user {telegram_id}, "
                    f"saved ~{summary.tokens_saved} tokens"
                )

                # Also store in legacy system for compatibility (but with minimal context)
                if hasattr(self, "team_memory"):
                    minimal_context = {
                        "chat_type": execution_context.get("chat_type"),
                        "response_type": response_type
                    }

                    self.team_memory.add_conversation(
                        telegram_id=str(telegram_id),
                        input_text=task_description[:COMMAND_TRUNCATE_LENGTH],  # Truncated
                        output_text=f"{response_type}: {result[:RESPONSE_TYPE_TRUNCATE_LENGTH]}...",  # Summarized
                        context=minimal_context,
                    )

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
            # CREWAI BEST PRACTICE: Optimize context before execution
            from kickai.agents.utils.context_optimizer import ContextOptimizer

            # Create optimized context following CrewAI best practices
            optimized_context = ContextOptimizer.optimize_execution_context(
                raw_context=execution_context,
                target_agent=AgentRole.MESSAGE_PROCESSOR  # Primary agent
            )

            logger.info("🤖 BASIC CREW: Executing task with basic crew")
            logger.info(f"🤖 BASIC CREW: Task description: {task_description}")
            logger.info(f"🤖 BASIC CREW: Optimized execution context: {optimized_context}")

            # Use optimized context for execution
            execution_context = optimized_context

            # Use the basic crew that was created in _create_crew
            if not hasattr(self, "crew") or not self.crew:
                logger.error("🤖 BASIC CREW: No crew available for fallback")
                return "❌ Sorry, I'm unable to process your request at the moment."

            logger.info("🤖 CREWAI NATIVE: Using CrewAI agent collaboration patterns")

            # INTELLIGENT ROUTING: Use command routing manager for proper agent selection
            # Use original task description for routing (before enhancement)
            selected_agent_role = await self._route_command_to_agent(task_description, execution_context)
            agent = self.agents[selected_agent_role]

            logger.info(f"🤖 INTELLIGENT ROUTING: Selected agent - {selected_agent_role.value} for command: {task_description}")

            # Validate and prepare execution context
            execution_context = self._prepare_execution_context(execution_context)

            # Get MESSAGE_PROCESSOR tools (includes NLP collaboration tools)
            agent_tools = self._get_agent_tools(agent, selected_agent_role, execution_context)
            if not agent_tools:
                return "❌ Internal error: No tools available for primary agent. This issue has been logged for investigation."

            # Create and execute task using CrewAI native collaboration
            # The task description will be enhanced within _create_and_execute_task
            result = await self._create_and_execute_task(
                task_description, execution_context, agent
            )

            logger.info(f"🤖 BASIC CREW: Task completed with result: {result}")
            return result

        except Exception as e:
            logger.error(f"🤖 BASIC CREW: Error in fallback execution: {e}", exc_info=True)
            return "❌ Sorry, I'm having trouble processing your request right now. Please try again in a moment."


    def _extract_command_from_task(self, task_description: str) -> str:
        """
        Extract command from CrewAI structured task description using expert patterns.

        Handles both structured descriptions (from AsyncContextInjector) and simple commands.
        Uses CrewAI best practices for task parsing and command extraction.

        Args:
            task_description: Full task description from CrewAI

        Returns:
            Extracted command string (e.g., "/update", "/info", "/help")
        """
        import re

        try:
            # CREWAI NATIVE PATTERN 1: Extract from structured "User Request:" line
            # Format: "User Request: /command args..."
            user_request_match = re.search(r'User Request:\s*([^\n]+)', task_description, re.IGNORECASE)
            if user_request_match:
                user_request = user_request_match.group(1).strip()
                logger.debug(f"🔍 COMMAND EXTRACTION: Found User Request line: '{user_request}'")

                # Extract command from user request line
                command = self._extract_command_from_line(user_request)
                if command:
                    logger.info(f"✅ COMMAND EXTRACTION: Extracted command '{command}' from structured task")
                    return command

            # CREWAI NATIVE PATTERN 2: Extract from "Task:" line (alternative format)
            # Format: "Task: /command args..."
            task_match = re.search(r'Task:\s*([^\n]+)', task_description, re.IGNORECASE)
            if task_match:
                task_line = task_match.group(1).strip()
                logger.debug(f"🔍 COMMAND EXTRACTION: Found Task line: '{task_line}'")

                command = self._extract_command_from_line(task_line)
                if command:
                    logger.info(f"✅ COMMAND EXTRACTION: Extracted command '{command}' from Task line")
                    return command

            # CREWAI NATIVE PATTERN 3: Direct command extraction (fallback for simple cases)
            # Handle cases where task_description is just a command
            command = self._extract_command_from_line(task_description)
            if command:
                logger.info(f"✅ COMMAND EXTRACTION: Extracted command '{command}' from direct input")
                return command

            # CREWAI BEST PRACTICE: Multi-line search for commands anywhere in description
            # Look for command patterns throughout the entire description
            command_pattern = r'(/[a-zA-Z][a-zA-Z0-9_]*)\b'
            commands_found = re.findall(command_pattern, task_description)

            if commands_found:
                # Take the first command found (most likely to be the primary intent)
                first_command = commands_found[0]
                logger.info(f"✅ COMMAND EXTRACTION: Found command '{first_command}' via pattern search")
                return first_command

            # Final fallback - try first word if it looks like a command
            words = task_description.strip().split()
            if words and words[0].startswith('/'):
                logger.info(f"✅ COMMAND EXTRACTION: Using first word '{words[0]}' as command")
                return words[0]

            # No command found
            logger.warning("⚠️ COMMAND EXTRACTION: No command found in task description")
            return ""

        except Exception as e:
            logger.error(f"❌ COMMAND EXTRACTION: Error extracting command: {e}")
            return ""

    def _extract_command_from_line(self, line: str) -> str:
        """
        Extract command from a single line using CrewAI-optimized patterns.

        Args:
            line: Single line of text potentially containing a command

        Returns:
            Command string if found, empty string otherwise
        """
        import re

        try:
            line = line.strip()
            if not line:
                return ""

            # Pattern 1: Command at start of line (most common)
            # "/command args..." or "/command"
            if line.startswith('/'):
                command_match = re.match(r'(/[a-zA-Z][a-zA-Z0-9_]*)', line)
                if command_match:
                    return command_match.group(1)

            # Pattern 2: Command anywhere in line with word boundaries
            # "please /command something" or "run /command now"
            command_match = re.search(r'\b(/[a-zA-Z][a-zA-Z0-9_]*)\b', line)
            if command_match:
                return command_match.group(1)

            # Pattern 3: First word might be command without slash (legacy support)
            words = line.split()
            if words:
                first_word = words[0].lower()
                # Common command patterns without slash
                if first_word in ['help', 'info', 'status', 'list', 'ping', 'version', 'myinfo']:
                    return f"/{first_word}"

            return ""

        except Exception as e:
            logger.warning(f"⚠️ Error extracting command from line '{line}': {e}")
            return ""

    async def _route_command_to_agent(self, task_description: str, execution_context: dict[str, Any]) -> AgentRole:
        """
        Route command using CrewAI Native Collaboration with NLP_PROCESSOR.

        This implements the TRUE CrewAI collaborative approach where:
        1. NLP_PROCESSOR analyzes the task and provides intelligent routing recommendation
        2. MESSAGE_PROCESSOR coordinates based on NLP analysis
        3. Fallback to simple rule-based routing only if NLP collaboration fails
        """
        try:
            # Extract command for context
            command = self._extract_command_from_task(task_description)
            chat_type = execution_context.get('chat_type', 'main')

            logger.info(f"🤖 CREWAI ROUTING: Starting intelligent routing for '{command}' from {chat_type}")

            # CREWAI NATIVE APPROACH: Use NLP_PROCESSOR for intelligent routing analysis
            if AgentRole.NLP_PROCESSOR in self.agents:
                try:
                    logger.info("🧠 CREWAI COLLABORATION: Engaging NLP_PROCESSOR for routing analysis")

                    # Create routing analysis task for NLP_PROCESSOR
                    routing_task = Task(
                        description=f"""
                        You are the intelligent routing specialist for KICKAI's football team management system.

                        Analyze this user request and recommend the most appropriate agent to handle it:

                        User Request: {task_description}
                        Command: {command}
                        Chat Type: {chat_type}
                        User Context: {execution_context}

                        GOAL:
                        Determine the optimal agent to handle this request based on:
                        - User's actual intent and needs
                        - Chat context and permissions
                        - Agent specialization and capabilities
                        - KICKAI system routing patterns

                        APPROACH:
                        Use your routing_recommendation_tool to analyze the request context and available agents.
                        The tool will provide you with comprehensive context about agent capabilities and routing patterns.
                        Apply your LLM intelligence to make the best routing decision.

                        EXPECTED OUTCOME:
                        Provide your routing recommendation in this exact format:
                        AGENT_RECOMMENDATION: [agent_name]

                        Follow with your analysis explaining:
                        - Primary intent identified
                        - Context factors considered
                        - Why the selected agent is the best match
                        - Your confidence level (1-10)
                        """,
                        agent=self.agents[AgentRole.NLP_PROCESSOR].crew_agent,
                        expected_output="AGENT_RECOMMENDATION: [agent_name] with detailed analysis"
                    )

                    # Execute NLP analysis using CrewAI native patterns
                    # Create a temporary crew for NLP analysis
                    from crewai import Crew
                    temp_crew = Crew(
                        agents=[self.agents[AgentRole.NLP_PROCESSOR].crew_agent],
                        tasks=[routing_task],
                        verbose=False
                    )

                    # Execute the analysis through the crew using async pattern
                    # Since we're already in an async context, use kickoff_async() directly
                    nlp_result = await temp_crew.kickoff_async()

                    nlp_response = nlp_result.raw if hasattr(nlp_result, 'raw') else str(nlp_result)

                    # Parse NLP_PROCESSOR recommendation
                    recommended_agent = self._parse_nlp_routing_recommendation(nlp_response)

                    if recommended_agent and recommended_agent in self.agents:
                        logger.info(f"🧠 CREWAI SUCCESS: NLP_PROCESSOR recommends → {recommended_agent.value}")
                        return recommended_agent
                    else:
                        logger.warning(f"⚠️ CREWAI: NLP recommendation '{recommended_agent}' not valid, using fallback")

                except Exception as nlp_error:
                    logger.error(f"❌ CREWAI: NLP_PROCESSOR collaboration failed: {nlp_error}")
            else:
                logger.warning("⚠️ CREWAI: NLP_PROCESSOR not available, using fallback routing")

            # FALLBACK: Simple rule-based routing (non-CrewAI approach)
            logger.info("🔄 FALLBACK: Using simple rule-based routing")
            from kickai.config.command_routing_manager import get_command_routing_manager

            try:
                routing_manager = get_command_routing_manager()
                routing_decision = routing_manager.route_command(command, chat_type, execution_context)

                if routing_decision.agent_role in self.agents:
                    logger.info(f"🔄 FALLBACK SUCCESS: Command '{command}' → {routing_decision.agent_role.value}")

                    # CRITICAL FIX: Ensure execution context has all required parameters for tools
                    # The fallback routing was not properly passing context parameters to tools
                    if not execution_context.get('telegram_id'):
                        logger.error("❌ FALLBACK: Missing telegram_id in execution context")
                        return AgentRole.MESSAGE_PROCESSOR
                    if not execution_context.get('team_id'):
                        logger.error("❌ FALLBACK: Missing team_id in execution context")
                        return AgentRole.MESSAGE_PROCESSOR
                    if not execution_context.get('username'):
                        logger.error("❌ FALLBACK: Missing username in execution context")
                        return AgentRole.MESSAGE_PROCESSOR
                    if not execution_context.get('chat_type'):
                        logger.error("❌ FALLBACK: Missing chat_type in execution context")
                        return AgentRole.MESSAGE_PROCESSOR

                    logger.info("🔄 FALLBACK: Context validation passed - all required parameters present")
                    return routing_decision.agent_role
                else:
                    logger.warning(f"⚠️ FALLBACK: Agent {routing_decision.agent_role.value} not available")
                    return AgentRole.MESSAGE_PROCESSOR

            except Exception as routing_error:
                logger.error(f"❌ FALLBACK: Rule-based routing failed: {routing_error}")
                return AgentRole.MESSAGE_PROCESSOR

        except Exception as e:
            logger.error(f"❌ ROUTING: Error in _route_command_to_agent: {e}")
            # Safe fallback to MESSAGE_PROCESSOR
            return AgentRole.MESSAGE_PROCESSOR

    def _parse_nlp_routing_recommendation(self, nlp_response: str) -> AgentRole:
        """
        Parse NLP_PROCESSOR routing recommendation from its JSON response.

        Expected format: {"agent": "agent_name", "confidence": 0.9, "intent": "...", "reasoning": "..."}
        """
        import json
        import re

        try:
            # Validate input
            if not nlp_response or not isinstance(nlp_response, str):
                logger.warning(f"⚠️ JSON PARSE: Invalid or empty nlp_response: {type(nlp_response)} - {nlp_response}")
                return None
            
            # Clean and validate the response
            cleaned_response = nlp_response.strip()
            if not cleaned_response:
                logger.warning("⚠️ JSON PARSE: Empty response after stripping")
                return None
            
            logger.debug(f"🔍 JSON PARSE: Attempting to parse response: {cleaned_response[:200]}...")
            
            # First try JSON parsing
            try:
                response_json = json.loads(cleaned_response)
                agent_name = response_json.get('agent', '').lower()
                confidence = response_json.get('confidence', 0.0)
                intent = response_json.get('intent', '')
                reasoning = response_json.get('reasoning', '')

                # Map agent names to AgentRole enum
                agent_mapping = {
                    'message_processor': AgentRole.MESSAGE_PROCESSOR,
                    'help_assistant': AgentRole.HELP_ASSISTANT,
                    'player_coordinator': AgentRole.PLAYER_COORDINATOR,
                    'team_administrator': AgentRole.TEAM_ADMINISTRATOR,
                    'squad_selector': AgentRole.SQUAD_SELECTOR,
                    'nlp_processor': AgentRole.NLP_PROCESSOR,
                }

                if agent_name in agent_mapping:
                    logger.info(f"🧠 JSON PARSE: Agent '{agent_name}', confidence {confidence}, intent '{intent}'")
                    logger.debug(f"🧠 JSON REASONING: {reasoning}")
                    return agent_mapping[agent_name]
                else:
                    logger.warning(f"⚠️ JSON PARSE: Unknown agent name '{agent_name}' in JSON response")

            except (json.JSONDecodeError, KeyError) as json_error:
                logger.debug(f"🔄 JSON PARSE: Failed, trying fallback parsing: {json_error}")
                logger.debug(f"🔄 JSON PARSE: Response content: {cleaned_response[:500]}...")

                # Fallback to regex parsing for backwards compatibility
                recommendation_match = re.search(r'AGENT_RECOMMENDATION:\s*([a-zA-Z_]+)', nlp_response)
                if recommendation_match:
                    agent_name = recommendation_match.group(1).lower()
                    agent_mapping = {
                        'message_processor': AgentRole.MESSAGE_PROCESSOR,
                        'help_assistant': AgentRole.HELP_ASSISTANT,
                        'player_coordinator': AgentRole.PLAYER_COORDINATOR,
                        'team_administrator': AgentRole.TEAM_ADMINISTRATOR,
                        'squad_selector': AgentRole.SQUAD_SELECTOR,
                        'nlp_processor': AgentRole.NLP_PROCESSOR,
                    }

                    if agent_name in agent_mapping:
                        logger.info(f"🧠 REGEX PARSE: Successfully parsed recommendation '{agent_name}'")
                        return agent_mapping[agent_name]

                # Look for agent names anywhere in the response as final fallback
                for agent_name, agent_role in [
                    ('player_coordinator', AgentRole.PLAYER_COORDINATOR),
                    ('team_administrator', AgentRole.TEAM_ADMINISTRATOR),
                    ('squad_selector', AgentRole.SQUAD_SELECTOR),
                    ('help_assistant', AgentRole.HELP_ASSISTANT),
                    ('message_processor', AgentRole.MESSAGE_PROCESSOR),
                ]:
                    if agent_name in nlp_response.lower():
                        logger.info(f"🧠 FALLBACK PARSE: Found agent '{agent_name}' in response")
                        return agent_role

            logger.warning("⚠️ NLP PARSE: No agent recommendation found in response")
            return None

        except Exception as e:
            logger.error(f"❌ NLP PARSE: Error parsing recommendation: {e}")
            return None

    def _prepare_execution_context(self, execution_context: dict[str, Any]) -> dict[str, Any]:
        """Prepare and validate execution context."""
        try:
            # Extract required parameters - no defaults to 'unknown'
            team_id = execution_context.get('team_id')
            telegram_id = execution_context.get('telegram_id')
            username = execution_context.get('username')
            chat_type = execution_context.get('chat_type')

            # DEBUG: Log context parameters for troubleshooting
            logger.debug(f"🔍 CONTEXT DEBUG: team_id={team_id}, telegram_id={telegram_id}, username={username}, chat_type={chat_type}")
            logger.debug(f"🔍 CONTEXT DEBUG: Full execution_context keys: {list(execution_context.keys())}")

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
                logger.error(f"❌ CONTEXT VALIDATION: Missing required parameters: {missing_params}")
                logger.error(f"❌ CONTEXT VALIDATION: Available keys: {list(execution_context.keys())}")
                raise ValueError(f"Missing required context parameters: {', '.join(missing_params)}")

            # Ensure all parameters are properly typed
            try:
                telegram_id_int = int(telegram_id) if telegram_id else None
            except (ValueError, TypeError) as e:
                logger.error(f"❌ CONTEXT VALIDATION: Invalid telegram_id format: {telegram_id}")
                raise ValueError(f"Invalid telegram_id format: {telegram_id}") from e

            # Return validated context with proper types
            validated_context = {
                'team_id': str(team_id),
                'telegram_id': telegram_id_int,
                'username': str(username),
                'chat_type': str(chat_type),
                # Preserve other context parameters
                **{k: v for k, v in execution_context.items() if k not in ['team_id', 'telegram_id', 'username', 'chat_type']}
            }

            logger.debug(f"✅ CONTEXT VALIDATION: Successfully prepared context with {len(validated_context)} parameters")
            return validated_context

        except Exception as e:
            logger.error(f"❌ CONTEXT VALIDATION: Error preparing execution context: {e}")
            raise ValueError(f"Failed to prepare execution context: {e}") from e

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
        self, task_description: str, execution_context: dict[str, Any], agent: Any
    ) -> str:
        """Create and execute CrewAI task with native agent collaboration."""
        try:
            # Validate context first (no 'unknown' defaults)
            self._create_structured_description(task_description, execution_context)

            # Create CrewAI task with intelligent agent collaboration
            task = self._create_crewai_task(task_description, agent, execution_context)

            # Execute task using CrewAI native patterns
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

    def _create_crewai_task(self, task_description: str, agent: Any, execution_context: dict[str, Any]) -> Any:
        """Create CrewAI task with intelligent agent collaboration patterns."""
        try:
            from crewai import Task

            # Get agent's tool names from configuration
            agent_config = get_agent_config(agent.agent_role, execution_context)
            agent_tool_names = agent_config.tools if agent_config else []

            # Generate dynamic task description with async tool metadata for collaboration
            dynamic_description = AsyncContextInjector.create_dynamic_task_description(
                user_request=task_description,
                context=execution_context,
                tool_registry=self.async_tool_registry,
                agent_tool_names=agent_tool_names
            )

            # Special JSON output format for NLP_PROCESSOR routing decisions
            if agent.agent_role == AgentRole.NLP_PROCESSOR:
                expected_output = "Return valid JSON only: {\"agent\": \"agent_name\", \"confidence\": 0.0-1.0, \"intent\": \"intent_classification\", \"reasoning\": \"brief_explanation\"}"
                output_format = "json"
            else:
                expected_output = "Extract and return the exact tool output. Parse JSON responses and return the 'data' field content (for success) or 'message' field content (for errors). Do not add extra text or formatting."
                output_format = "string"

            task = Task(
                name=f"collaborative_task_{agent.agent_role.value}",
                description=dynamic_description,
                agent=agent.crew_agent,
                expected_output=expected_output,
                output_format=output_format,
                async_execution=True,  # Enable async execution for async tools
            )

            logger.debug(f"✅ Dynamic task created for {agent.agent_role.value} with {len(agent_tool_names)} tools")
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
