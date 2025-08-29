#!/usr/bin/env python3
"""
Simplified CrewAI Football Team Management System - 5-Agent Architecture

This module provides a simplified, production-ready implementation using
CrewAI's native delegation and hierarchical process.

5-AGENT SYSTEM:
1. MESSAGE_PROCESSOR - Manager agent (no tools, coordinates delegation)
2. HELP_ASSISTANT - Help system and guidance
3. PLAYER_COORDINATOR - Player management and onboarding
4. TEAM_ADMINISTRATOR - Team member management
5. SQUAD_SELECTOR - Squad selection and match management
"""

# Standard library imports
import logging
from typing import Any

# Third-party imports
from crewai import Crew, Task, Process, Agent
from loguru import logger

# Local application imports
from kickai.agents.configurable_agent import ConfigurableAgent
from kickai.config.llm_config import get_llm_config
from kickai.core.config import get_settings
from kickai.core.enums import AgentRole
from kickai.core.exceptions import AgentInitializationError


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass


class TeamManagementSystem:
    """
    Simplified Team Management System using CrewAI native delegation.
    
    This system leverages CrewAI's built-in hierarchical process and delegation
    capabilities, eliminating the need for manual task routing and execution.
    """

    def __init__(self, team_id: str):
        self.team_id = team_id
        self.agents: dict[AgentRole, ConfigurableAgent] = {}
        self.crew: Crew | None = None

        # Initialize configuration
        logger.info(f"[TEAM INIT] Initializing TeamManagementSystem for team {team_id}")
        self.config_manager = get_settings()
        
        if not self.config_manager:
            raise ConfigurationError(f"No configuration found for {team_id}")

        # Initialize tool registry once for all agents
        logger.info("[TEAM INIT] Initializing tool registry")
        from kickai.agents.tool_registry import initialize_tool_registry
        initialize_tool_registry("kickai")

        # Initialize LLM
        logger.info("[TEAM INIT] Initializing LLM")
        self._initialize_llm()

        # Initialize agents
        logger.info("[TEAM INIT] Initializing agents")
        self._initialize_agents()

        # Create hierarchical crew
        logger.info("[TEAM INIT] Creating hierarchical crew")
        self._create_crew()

        logger.info(f"✅ TeamManagementSystem initialized for team {team_id}")

    def _initialize_llm(self):
        """Initialize the LLM for the system."""
        try:
            llm_config = get_llm_config()
            main_llm, _ = llm_config.get_llm_for_agent(AgentRole.MESSAGE_PROCESSOR)
            self.llm = main_llm

            # Initialize manager LLM for delegation
            self.manager_llm = llm_config.create_llm(
                model_name=llm_config.advanced_model,
                temperature=llm_config.settings.ai_temperature,
                max_tokens=llm_config.settings.ai_max_tokens
            )

            logger.info(f"✅ LLM initialized: {type(self.llm).__name__}")
            logger.info(f"✅ Manager LLM initialized: {llm_config.advanced_model}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise ConfigurationError(f"Failed to initialize LLM: {e!s}") from e

    def _initialize_agents(self):
        """Initialize all agents for the team."""
        try:
            agent_roles = [
                AgentRole.MESSAGE_PROCESSOR,
                AgentRole.HELP_ASSISTANT,
                AgentRole.PLAYER_COORDINATOR,
                AgentRole.TEAM_ADMINISTRATOR,
                AgentRole.SQUAD_SELECTOR
            ]

            logger.info(f"[TEAM INIT] Creating {len(agent_roles)} agents")

            for role in agent_roles:
                try:
                    logger.info(f"[TEAM INIT] Creating agent for role: {role.value}")
                    agent = ConfigurableAgent(role, self.team_id)
                    
                    if not hasattr(agent, 'crew_agent'):
                        raise AgentInitializationError(role.value, "Agent missing crew_agent attribute")

                    self.agents[role] = agent
                    logger.info(f"[TEAM INIT] ✅ Created agent for role: {role.value}")

                except Exception as e:
                    logger.error(f"[TEAM INIT] ❌ Failed to create agent for role {role.value}: {e}")
                    raise AgentInitializationError(role.value, f"Failed to create agent: {e}") from e

            logger.info(f"[TEAM INIT] ✅ Created {len(self.agents)} agents successfully")

        except Exception as e:
            logger.error(f"[TEAM INIT] ❌ Failed to initialize agents: {e}")
            raise AgentInitializationError("TeamManagementSystem", f"Failed to initialize agents: {e}") from e

    def _create_crew(self):
        """Create the CrewAI crew with hierarchical process."""
        try:
            # Get all specialist agents (exclude MESSAGE_PROCESSOR as it becomes manager)
            crew_agents = [
                agent.crew_agent 
                for role, agent in self.agents.items() 
                if role != AgentRole.MESSAGE_PROCESSOR and hasattr(agent, 'crew_agent')
            ]

            if not crew_agents:
                raise AgentInitializationError("TeamManagementSystem", "No specialist agents available")

            # Get verbose setting
            settings = get_settings()
            verbose_mode = settings.verbose_logging or settings.debug

            # Create manager agent (MESSAGE_PROCESSOR becomes manager)
            manager_agent = Agent(
                role="Team Manager",
                goal="Coordinate and delegate tasks to the most appropriate specialist agents based on user intent and preserve their complete responses",
                backstory="""You are an experienced team manager who coordinates work between specialist agents.
                
                🚨 ABSOLUTE RESPONSE PRESERVATION MANDATE:
                YOU ARE STRICTLY FORBIDDEN FROM ALTERING SPECIALIST RESPONSES IN ANY WAY.
                Your ONLY role is delegation and COMPLETE response passthrough.
                
                RESPONSE PRESERVATION PROTOCOL (MANDATORY):
                1. Delegate task to appropriate specialist agent
                2. Receive specialist response
                3. Return specialist response VERBATIM - character for character
                4. NO processing, NO summarizing, NO formatting changes whatsoever
                
                PRESERVATION REQUIREMENTS:
                ✅ PRESERVE: Every character, emoji, line break, formatting mark
                ✅ PRESERVE: Complete invite links, URLs, technical details
                ✅ PRESERVE: All instructions, next steps, contact information
                ✅ PRESERVE: Success messages, error details, user guidance
                ❌ FORBIDDEN: Any summarization, condensation, or modification
                ❌ FORBIDDEN: Removing details, shortening responses, paraphrasing
                ❌ FORBIDDEN: Converting detailed responses to brief summaries
                
                CRITICAL RULE: If specialist provides 500 words, you return ALL 500 words unchanged.
                
                DELEGATION STRATEGY:
                - help_assistant: Help, system commands, available commands
                - player_coordinator: Player information, status, updates, approvals
                - team_administrator: Team member management, adding players/members (leadership only)
                - squad_selector: Availability, match management, squad operations
                
                DELEGATION PARAMETERS FORMAT:
                - task: "Simple string description"
                - context: "Simple context string"
                - coworker: "agent_name" (string only)
                
                RESPONSE HANDLING:
                Upon receiving specialist response, return it EXACTLY as received.
                Think of yourself as a passthrough proxy - you change NOTHING.""",
                llm=self.manager_llm,
                allow_delegation=True,
                tools=[],  # Manager has no tools - only delegates
                verbose=verbose_mode
            )

            # Create hierarchical crew
            self.crew = Crew(
                agents=crew_agents,
                manager_agent=manager_agent,
                process=Process.hierarchical,
                verbose=verbose_mode
            )

            logger.info(f"✅ Created hierarchical crew with {len(crew_agents)} specialist agents and manager agent")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create crew: {str(e)}")
            raise AgentInitializationError("TeamManagementSystem", f"Crew creation failed: {str(e)}")

    async def execute_task(self, task_description: str, execution_context: dict[str, Any]) -> str:
        """
        Execute a task using CrewAI's native delegation.
        
        Args:
            task_description: Description of the task to execute
            execution_context: Context information for task execution
            
        Returns:
            Task execution result
        """
        try:
            logger.info(f"🤖 Starting task execution for team {self.team_id}")
            logger.info(f"🤖 Task: {task_description}")

            # Validate execution context
            validated_context = self._prepare_execution_context(execution_context)

            # Create enhanced task description for manager agent with absolute preservation mandate
            user = validated_context.get('username', 'user')
            chat_type = validated_context.get('chat_type', 'main')
            telegram_id = validated_context.get('telegram_id', 0)
            team_id = validated_context.get('team_id', self.team_id)

            # Create task description with absolute response preservation mandate
            enhanced_task = f"""
User ({user}) in {chat_type} chat says: "{task_description}"

Context Information:
- User ID: {telegram_id}
- Team ID: {team_id}
- Username: {user}
- Chat Type: {chat_type}

🎯 YOUR TASK:
1. Analyze user intent and delegate to appropriate specialist
2. PRESERVE specialist response COMPLETELY AND EXACTLY

🚨 RESPONSE PRESERVATION MANDATE:
Whatever response the specialist provides, you MUST return it VERBATIM.
NO summarizing, NO condensing, NO modifications, NO shortening.
If specialist returns 1000 characters, you return ALL 1000 characters unchanged.

DELEGATION TARGETS:
- help_assistant: Help, system commands, available commands
- player_coordinator: Player info, status, updates, approvals
- team_administrator: Team management, adding players/members (leadership only)  
- squad_selector: Availability, matches, squad operations

DELEGATION FORMAT:
- task: "Process user request: {task_description}"
- context: "User: {user}, ID: {telegram_id}, Team: {team_id}, Chat: {chat_type}"
- coworker: "[agent_name]"

⚡ FINAL INSTRUCTION:
Return the specialist's response EXACTLY as received - character for character.
You are a passthrough proxy. Change NOTHING.
"""

            # Create task for the crew with explicit preservation requirements
            task = Task(
                description=enhanced_task,
                expected_output="""SPECIALIST RESPONSE VERBATIM - NO CHANGES ALLOWED
                
You must return the specialist agent's response EXACTLY as provided:
                - Every character preserved
                - All formatting intact (emojis, line breaks, bullets)
                - Complete invite links and URLs
                - Full instructions and next steps
                - All details, no summarization
                
FORBIDDEN ACTIONS:
                - Summarizing or condensing responses
                - Removing details or formatting
                - Converting long responses to brief summaries
                - Any modification or paraphrasing
                
REQUIRED: Character-for-character exact reproduction of specialist response."""
            )

            # Execute with CrewAI's native delegation - pass minimal inputs to avoid parameter conflicts
            self.crew.tasks = [task]
            result = await self.crew.kickoff_async()
            result = result.raw if hasattr(result, 'raw') else str(result)

            logger.info("🤖 Task execution completed successfully")
            return result

        except Exception as e:
            logger.error(f"❌ Error in execute_task: {e}")
            return f"❌ System error: {e!s}"

    def _prepare_execution_context(self, execution_context: dict[str, Any]) -> dict[str, Any]:
        """Prepare and validate execution context."""
        try:
            # Extract required parameters
            team_id = execution_context.get('team_id')
            telegram_id = execution_context.get('telegram_id')
            username = execution_context.get('username')
            chat_type = execution_context.get('chat_type')

            # Validate all required parameters
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
                raise ValueError(f"Missing required context parameters: {', '.join(missing_params)}")

            # Ensure proper types
            try:
                telegram_id_int = int(telegram_id) if telegram_id else None
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid telegram_id format: {telegram_id}") from e

            # Return validated context
            validated_context = {
                'team_id': str(team_id),
                'telegram_id': telegram_id_int,
                'username': str(username),
                'chat_type': str(chat_type),
                **{k: v for k, v in execution_context.items() 
                   if k not in ['team_id', 'telegram_id', 'username', 'chat_type']}
            }

            logger.debug(f"✅ Context validated with {len(validated_context)} parameters")
            return validated_context

        except Exception as e:
            logger.error(f"❌ Error preparing execution context: {e}")
            raise ValueError(f"Failed to prepare execution context: {e}") from e

    def get_agent_summary(self) -> dict[str, Any]:
        """Get a summary of all agents."""
        summary = {}
        for role, agent in self.agents.items():
            summary[role.value] = {
                "role": role.value,
                "tools_count": len(agent.get_tools()) if hasattr(agent, 'get_tools') else 0,
                "crew_agent_available": hasattr(agent, 'crew_agent') and agent.crew_agent is not None,
            }
        return summary

    def get_agent(self, role: AgentRole) -> ConfigurableAgent | None:
        """Get a specific agent by role."""
        return self.agents.get(role)

    def health_check(self) -> dict[str, Any]:
        """Perform a health check on the system."""
        try:
            health_status = {
                "system": "healthy",
                "agents_count": len(self.agents),
                "agents": {},
                "crew_created": self.crew is not None,
                "llm_available": self.llm is not None,
            }

            # Check each agent
            for role, agent in self.agents.items():
                health_status["agents"][role.value] = {
                    "tools_count": len(agent.get_tools()) if hasattr(agent, 'get_tools') else 0,
                    "crew_agent_available": hasattr(agent, 'crew_agent') and agent.crew_agent is not None,
                }

            return health_status

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"system": "unhealthy", "error": str(e)}


# Convenience functions
def create_team_management_system(team_id: str) -> TeamManagementSystem:
    """Create a team management system for the specified team."""
    return TeamManagementSystem(team_id)


def get_agent(team_id: str, role: AgentRole) -> ConfigurableAgent | None:
    """Get a specific agent for a team."""
    system = TeamManagementSystem(team_id)
    return system.get_agent(role)
