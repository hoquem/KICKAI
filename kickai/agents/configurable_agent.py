#!/usr/bin/env python3
"""
Configurable Agent for KICKAI System - CrewAI 2025 Best Practices

This module provides a clean, simplified configurable agent that follows CrewAI 2025 
best practices for context passing and tool parameter handling.
"""

import traceback
from typing import Any, Dict, Set, List

from crewai import Agent, Crew, Process, Task
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
    - Inter-agent delegation support
    """

    def __init__(self, agent_role: AgentRole, team_id: str, other_agents: List['ConfigurableAgent'] = None):
        """
        Initialize agent with role and team ID.

        Args:
            agent_role: The role this agent should perform
            team_id: The team this agent belongs to
            other_agents: List of other agents for delegation capabilities
        """
        self.agent_role = agent_role
        self.team_id = team_id
        self.other_agents = other_agents or []

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
                "username": "user"
            }
            self.config = get_agent_config(self.agent_role, context)

            # 4. CrewAI agent
            self.crew_agent = self._create_crew_agent()

        except Exception as e:
            logger.error(f"❌ Failed to initialize ConfigurableAgent: {e}")
            raise AgentInitializationError("ConfigurableAgent", f"Agent initialization failed: {e}")

    def _create_crew_agent(self) -> Agent:
        """Create the underlying CrewAI agent with proper configuration and delegation tools."""
        # Get tools for this agent role using direct assignment (CrewAI best practice)
        tools = self._get_tools_for_agent()

        # Add delegation tools for inter-agent communication
        delegation_tools = self._get_delegation_tools()
        if delegation_tools:
            tools.extend(delegation_tools)
            logger.info(f"🔗 Added {len(delegation_tools)} delegation tools to {self.agent_role.value}")

        # Get memory system for this agent
        from kickai.core.memory_manager import get_memory_manager
        memory_manager = get_memory_manager()
        agent_memory = memory_manager.get_memory_for_agent(self.agent_role)
        
        # Create agent with optimized configuration and memory
        settings = get_settings()

        agent = Agent(
            role=self.config.role,
            goal=self.config.goal,
            backstory=self.config.backstory,
            tools=tools,
            llm=self.llm,
            function_calling_llm=self.tool_llm,  # Use tool_llm for function calling
            verbose=True,
            max_iter=self.config.max_iterations,
            memory=agent_memory,  # Enable entity-specific memory
            allow_delegation=(self.agent_role == AgentRole.MESSAGE_PROCESSOR),  # Only manager agent allows delegation
        )

        logger.debug(
            f"🔧 Created CrewAI agent for {self.agent_role.value} with {len(tools)} tools"
        )
        return agent

    def _get_tools_for_agent(self) -> List[Any]:
        """
        Get tools for this agent using direct assignment (CrewAI best practice).
        
        Now applies context injection using the existing context_wrapper.py
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
                        logger.debug(f"✅ Found tool '{tool_name}' via search for {self.agent_role.value}")
                    else:
                        logger.warning(f"❌ Tool '{tool_name}' not found for {self.agent_role.value}")
            
            # For now, skip context injection to avoid callable issues
            # Context will be passed via Task.config instead
            if tools:
                logger.info(f"🔧 Loaded {len(tools)} tools (context via Task.config) for {self.agent_role.value}")
                return tools
            else:
                logger.info(f"🔧 No tools found for {self.agent_role.value}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Error loading tools for {self.agent_role.value}: {e}")
            return []

    def _apply_context_injection_to_tools(self, tools: List[Any]) -> List[Any]:
        """
        Apply context injection to tools using the existing context_wrapper.py
        """
        try:
            # Create default execution context for this agent
            # This will be updated dynamically when tasks are executed
            default_context = {
                'telegram_id': 0,  # Will be updated per task
                'team_id': self.team_id,
                'username': 'user',  # Will be updated per task
                'chat_type': 'main'  # Will be updated per task
            }
            
            # Apply context injection using existing wrapper
            from kickai.agents.context_wrapper import apply_context_injection_to_agent_tools
            wrapped_tools = apply_context_injection_to_agent_tools(tools, default_context)
            
            logger.info(f"🎯 Applied context injection to {len(tools)} tools for {self.agent_role.value}")
            return wrapped_tools
            
        except Exception as e:
            logger.error(f"❌ Error applying context injection for {self.agent_role.value}: {e}")
            # Return original tools if context injection fails
            return tools

    def _get_delegation_tools(self) -> List[Any]:
        """Get delegation tools for inter-agent communication."""
        if not self.other_agents:
            return []

        try:
            # Convert other agents to CrewAI agents for delegation
            crew_agents = []
            for other_agent in self.other_agents:
                if hasattr(other_agent, 'crew_agent') and other_agent.crew_agent:
                    crew_agents.append(other_agent.crew_agent)

            if crew_agents:
                # Get delegation tools from CrewAI
                delegation_tools = self.crew_agent.get_delegation_tools(crew_agents)
                logger.debug(f"🔗 Created {len(delegation_tools)} delegation tools for {self.agent_role.value}")
                return delegation_tools
            else:
                logger.warning(f"⚠️ No valid CrewAI agents found for delegation in {self.agent_role.value}")
                return []

        except Exception as e:
            logger.error(f"❌ Error creating delegation tools for {self.agent_role.value}: {e}")
            return []

    def set_other_agents(self, other_agents: List['ConfigurableAgent']):
        """Set other agents for delegation capabilities."""
        self.other_agents = other_agents
        # Recreate agent with new delegation tools
        if hasattr(self, 'crew_agent'):
            self.crew_agent = self._create_crew_agent()

    def get_tools(self) -> list:
        """Get the tools available for this agent."""
        if hasattr(self.crew_agent, 'tools'):
            return self.crew_agent.tools
        else:
            # Fallback: get tools directly from registry
            return self._get_tools_for_agent()

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
            from kickai.utils.task_description_enhancer import TaskDescriptionEnhancer
            enhanced_description = TaskDescriptionEnhancer.enhance_task_description(task_description, context)

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



    async def _execute_crewai_task(self, task_description: str, context: Dict[str, Any]) -> str:
        """Execute the actual CrewAI task with proper context handling."""
        logger.debug(f"🔧 Creating task with context: {context}")

        # Create task with simplified description to avoid prompt pollution
        task = Task(
            description=task_description,
            agent=self.crew_agent,
            expected_output="A clear and helpful response based on the user's request.",
            config=context,  # Tools access this via get_task_config()
        )

        # Create and execute crew with minimal configuration
        crew = Crew(
            agents=[self.crew_agent],
            tasks=[task],
            process=Process.sequential,
            memory=False,  # Disable memory for stateless execution
            verbose=False,  # Disable verbose logging to reduce output pollution
        )

        logger.info(f"🚀 Starting CrewAI execution for {self.agent_role.value}")


        # Execute and return result
        result = crew.kickoff()

        logger.info(f"✅ CrewAI execution completed for {self.agent_role.value}")
        
        # Clean up the result to remove any prompt pollution
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        # Use the sanitizer to clean up any prompt pollution
        from kickai.utils.tool_output_sanitizer import sanitize_tool_output, validate_tool_output
        
        # Validate the output first
        validation = validate_tool_output(result_str)
        
        if validation["is_polluted"]:
            logger.warning(f"⚠️ Tool output pollution detected for {self.agent_role.value}")
            logger.debug(f"🔍 Pollution issues: {validation['issues']}")
            
            # Use the sanitizer to clean the output
            clean_result = sanitize_tool_output(result_str)
            
            if clean_result and clean_result.strip():
                logger.info(f"✅ Successfully cleaned polluted output for {self.agent_role.value}")
                return clean_result
            else:
                logger.error(f"❌ Failed to extract clean data from polluted output for {self.agent_role.value}")
                return f"❌ Error: Tool output was corrupted. Please try again."
        
        return result_str


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
                "username": "user"
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

            # Second pass: set up delegation between agents
            for role, agent in agents.items():
                other_agents = [other_agent for other_role, other_agent in agents.items() if other_role != role]
                agent.set_other_agents(other_agents)
                logger.debug(f"🔗 Set up delegation for {role.value} with {len(other_agents)} other agents")

            logger.info(f"🎉 AgentFactory created {len(agents)} agents with delegation support for team {self.team_id}")
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
