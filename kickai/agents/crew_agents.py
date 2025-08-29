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
                goal="Coordinate and delegate tasks to the most appropriate specialist agents based on user intent",
                backstory="""You are an experienced team manager who coordinates work between specialist agents.
                
                CRITICAL INSTRUCTIONS FOR DELEGATION:
                When using the "Delegate work to coworker" tool, you MUST pass parameters as simple strings, NOT as dictionaries.
                
                CORRECT parameter format:
                - task: "Simple string description of what needs to be done"
                - context: "Simple string with all necessary context information"
                - coworker: "help_assistant" (just the role name as a string)
                
                INCORRECT parameter format (DO NOT USE):
                - task: {"description": "...", "type": "str"}
                - context: {"telegram_id": 123, "team_id": "KTI"}
                - coworker: {"role": "help_assistant"}
                
                INTENT-BASED DELEGATION:
                Use your intelligence to understand the user's intent and delegate to the most appropriate specialist:
                
                - help_assistant: For general help, system commands, and queries about available commands
                - player_coordinator: For player information, status, updates, and player-related queries
                - team_administrator: For team member management, adding players/members (leadership only)
                - squad_selector: For availability, match management, and squad-related queries
                
                Analyze the user's request and their intent, then delegate to the agent best suited to handle that type of request.""",
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

            # Create enhanced task description for manager agent
            user = validated_context.get('username', 'user')
            chat_type = validated_context.get('chat_type', 'main')
            telegram_id = validated_context.get('telegram_id', 0)
            team_id = validated_context.get('team_id', self.team_id)

            # Create a simplified task description with context inline to avoid delegation parameter issues
            enhanced_task = f"""
User ({user}) in {chat_type} chat says: "{task_description}"

Context Information:
- User ID: {telegram_id}
- Team ID: {team_id}
- Username: {user}
- Chat Type: {chat_type}

As the team manager, understand what the user wants and delegate to the most appropriate specialist agent.

IMPORTANT: When delegating to a specialist agent, format your parameters as simple strings:
- task: "Help the user with their request: {task_description}"
- context: "User ID: {telegram_id}, Team: {team_id}, Username: {user}, Chat Type: {chat_type}"
- coworker: "help_assistant" (or the appropriate agent role)

Available specialist agents:
- help_assistant: For general help, system commands, and queries about available commands
- player_coordinator: For player information, status, updates, and player-related queries
- team_administrator: For team member management, adding players/members (leadership only)
- squad_selector: For availability, match management, and squad-related queries

Use your intelligence to analyze the user's intent and delegate to the most appropriate specialist agent.
"""

            # Create task for the crew - remove context parameter as it conflicts with delegation
            task = Task(
                description=enhanced_task,
                expected_output="Appropriate response to the user's request"
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
