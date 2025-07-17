"""
Configurable Agent for KICKAI System

This module provides a configurable agent that can be used with different
configurations and behavioral mixins.
"""

import logging
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
import traceback

from crewai import Agent
from langchain_core.tools import BaseTool

from core.enums import AgentRole
from config.agents import get_agent_config, AgentConfig
from agents.behavioral_mixins import get_mixin_for_role
from agents.team_memory import TeamMemory
from core.error_handling import handle_agent_errors, validate_input


logger = logging.getLogger(__name__)


class LoggingCrewAIAgent(Agent):
    """CrewAI Agent wrapper with comprehensive logging for tool selection and execution."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use module-level logger instead of instance attribute to avoid Pydantic conflicts
        logger.info(f"[CREWAI AGENT] LoggingCrewAIAgent initialized with role: {self.role}")
        logger.info(f"[CREWAI AGENT] Available tools: {[tool.name for tool in self.tools] if hasattr(self, 'tools') and self.tools else 'None'}")
    
    def execute_task(self, task, *args, **kwargs):
        """Execute a task with comprehensive logging."""
        logger.debug("LoggingCrewAIAgent.execute_task called")
        logger.info(f"[CREWAI AGENT] Starting task execution")
        logger.info(f"[CREWAI AGENT] Task description: {task.description if hasattr(task, 'description') else str(task)}")
        logger.info(f"[CREWAI AGENT] Agent role: {self.role}")
        logger.info(f"[CREWAI AGENT] Agent tools: {[tool.name for tool in self.tools] if hasattr(self, 'tools') and self.tools else 'None'}")
        
        # Log detailed tool information
        if hasattr(self, 'tools') and self.tools:
            for i, tool in enumerate(self.tools):
                logger.info(f"[CREWAI AGENT] Tool {i+1}: {tool.name} - {getattr(tool, 'description', 'No description')}")
        
        try:
            logger.debug("LoggingCrewAIAgent calling super().execute_task")
            logger.info(f"[CREWAI AGENT] Calling parent execute_task method...")
            
            # Log LLM information
            if hasattr(self, 'llm'):
                logger.info(f"[CREWAI AGENT] LLM type: {type(self.llm).__name__}")
                logger.info(f"[CREWAI AGENT] LLM model: {getattr(self.llm, 'model', 'Unknown')}")
            
            # Call the parent execute_task method (this is sync in CrewAI)
            result = super().execute_task(task, *args, **kwargs)
            
            logger.debug("LoggingCrewAIAgent super().execute_task completed")
            logger.info(f"[CREWAI AGENT] Task execution completed successfully")
            logger.info(f"[CREWAI AGENT] Result: {result[:200]}..." if len(str(result)) > 200 else f"[CREWAI AGENT] Result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"[AGENT ERROR TRACE] {traceback.format_exc()}")
            logger.error(f"[AGENT ERROR TRACE] [CREWAI AGENT] Error during task execution: {e}", exc_info=True)
            raise


@dataclass
class AgentCreationContext:
    """Context for agent creation."""
    team_id: str
    llm: Any
    tools: List[BaseTool]
    config: AgentConfig
    team_memory: Optional[TeamMemory] = None


class ConfigurableAgent:
    """
    Generic agent class that can be configured for any role.
    
    This class replaces all role-specific agent classes and uses centralized
    configuration to determine behavior, tools, and capabilities.
    """
    
    def __init__(self, context: AgentCreationContext):
        """
        Initialize a configurable agent.
        
        Args:
            context: AgentCreationContext containing all necessary information
        """
        self.team_id = context.team_id
        self.role = context.config.role
        self.config = context.config
        self.team_memory = context.team_memory
        self.llm = context.llm
        self.tools = context.tools
        
        # Initialize behavioral mixin if specified
        self.behavioral_mixin = None
        if context.config.behavioral_mixin:
            self.behavioral_mixin = get_mixin_for_role(context.config.behavioral_mixin)
            logger.info(f"Initialized behavioral mixin: {context.config.behavioral_mixin}")
        
        # Initialize team memory if enabled
        if context.config.memory_enabled and context.team_memory is None:
            self.team_memory = TeamMemory(context.team_id)
            logger.info(f"Initialized team memory for {context.team_id}")
        
        # Create the underlying CrewAI Agent
        self._crew_agent = self._create_crew_agent()
        
        logger.info(f"Created ConfigurableAgent for role {context.config.role}")
    
    def _create_crew_agent(self) -> Agent:
        """Create the underlying CrewAI Agent with the current configuration."""
        try:
            # Build agent parameters from configuration
            agent_params = {
                'role': self.config.role.value,
                'goal': self.config.goal,
                'backstory': self.config.backstory,
                'llm': self.llm,
                'verbose': self.config.verbose,
                'allow_delegation': self.config.allow_delegation,
                'max_iter': self.config.max_iterations,
                'tools': self.tools  # Pass tools to the agent
            }
            
            # Add memory if enabled - use boolean value
            if self.config.memory_enabled:
                agent_params['memory'] = self.team_memory.get_memory() # Use the actual memory object
            
            # Use our logging wrapper instead of the base Agent
            agent = LoggingCrewAIAgent(**agent_params)
            return agent
        except Exception as e:
            logging.exception(f"Failed to create CrewAI Agent: {e}")
            raise
    
    @handle_agent_errors(operation="agent_execution")
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a task with the agent.
        
        Args:
            task: The task description
            context: Optional execution context containing team_id, user_id, etc.
            
        Returns:
            The task result as a string
        """
        logger.debug(f"[DEBUG][ConfigurableAgent] Starting execution with task: {task}")
        logger.info(f"[AGENT EXECUTE] Starting execution for agent {self.role}")
        logger.info(f"[AGENT EXECUTE] Task: {task}")
        logger.info(f"[AGENT EXECUTE] Context: {context}")
        
        try:
            # Validate inputs
            validate_input(task, str, "task", required=True)
            if context is not None:
                validate_input(context, dict, "context", required=False)
                logger.debug(f"[DEBUG][ConfigurableAgent] Input validated.")
                logger.info(f"[DEBUG][ConfigurableAgent] Input validated.")
            
            # CRITICAL: Configure tools with execution context before execution
            if context:
                self._configure_tools_with_context(context)
            
            # Apply behavioral mixin if available
            if self.behavioral_mixin and hasattr(self.behavioral_mixin, 'pre_execute'):
                logger.debug(f"[DEBUG][ConfigurableAgent] Applying pre_execute behavioral mixin")
                logger.info(f"[AGENT EXECUTE] Applying pre_execute mixin")
                task = self.behavioral_mixin.pre_execute(task, context)
                logger.info(f"[AGENT EXECUTE] Modified task after pre_execute: {task}")
            
            # Create a CrewAI Task object
            from crewai import Task
            
            crew_task = Task(
                description=task,
                agent=self._crew_agent,
                expected_output="Task result as a string"
            )
            logger.debug(f"[DEBUG][ConfigurableAgent] Building CrewAI task...")
            logger.info(f"[DEBUG][ConfigurableAgent] Building CrewAI task...")
            logger.debug(f"🔍 [DEBUG] ConfigurableAgent executing CrewAI task: {task}")
            logger.info(f"[AGENT EXECUTE] Created CrewAI task, executing...")
            logger.info(f"[AGENT EXECUTE] CrewAI task description: {crew_task.description}")
            logger.info(f"[AGENT EXECUTE] CrewAI agent role: {self._crew_agent.role}")
            logger.info(f"[AGENT EXECUTE] CrewAI agent tools count: {len(self._crew_agent.tools) if hasattr(self._crew_agent, 'tools') else 'unknown'}")
            
            # Log CrewAI agent tool details
            if hasattr(self._crew_agent, 'tools') and self._crew_agent.tools:
                for i, tool in enumerate(self._crew_agent.tools):
                    logger.info(f"[AGENT EXECUTE] CrewAI Tool {i+1}: {tool.name} - {getattr(tool, 'description', 'No description')}")
            
            # Execute the task using the CrewAI agent (async)
            logger.info(f"[AGENT EXECUTE] Starting CrewAI agent execution...")
            
            # Use run_in_executor to handle CrewAI's sync execute_task method
            import asyncio
            loop = asyncio.get_event_loop()
            
            logger.debug(f"🔍 [DEBUG] ConfigurableAgent about to execute CrewAI task with timeout")
            logger.info(f"[AGENT EXECUTE] Starting CrewAI execution with timeout...")
            
            try:
                # Add timeout to prevent hanging
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, 
                        lambda: self._crew_agent.execute_task(crew_task)
                    ),
                    timeout=60.0  # 60 second timeout
                )
                logger.debug(f"🔍 [DEBUG] ConfigurableAgent CrewAI execution completed within timeout")
                logger.info(f"[AGENT EXECUTE] CrewAI execution completed within timeout")
            except asyncio.TimeoutError:
                logger.error(f"[AGENT ERROR TRACE] CrewAI execution timed out after 60 seconds")
                raise Exception("CrewAI agent execution timed out")
            except Exception as e:
                logger.error(f"[AGENT ERROR TRACE] CrewAI execution failed: {traceback.format_exc()}")
                raise
            
            logger.debug(f"🔍 [DEBUG] ConfigurableAgent CrewAI result: {result}")
            logger.info(f"[AGENT EXECUTE] CrewAI execution successful")
            logger.info(f"[AGENT EXECUTE] Result: {result[:200]}..." if len(str(result)) > 200 else f"[AGENT EXECUTE] Result: {result}")
            
            # Apply behavioral mixin if available
            if self.behavioral_mixin and hasattr(self.behavioral_mixin, 'post_execute'):
                logger.debug(f"🔍 [DEBUG] ConfigurableAgent applying post_execute behavioral mixin")
                logger.info(f"[AGENT EXECUTE] Applying post_execute mixin")
                result = self.behavioral_mixin.post_execute(result, context)
                logger.info(f"[AGENT EXECUTE] Modified result after post_execute: {result[:200]}..." if len(str(result)) > 200 else f"[AGENT EXECUTE] Modified result: {result}")
            
            logger.debug(f"🔍 [DEBUG] ConfigurableAgent.execute returning: {result}")
            logger.info(f"[AGENT EXECUTE] Execution completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[AGENT ERROR TRACE] {traceback.format_exc()}")
            logger.error(f"[AGENT EXECUTE] Error during execution: {e}", exc_info=True)
            raise
    
    def _configure_tools_with_context(self, context: Dict[str, Any]) -> None:
        """
        Configure all tools with the execution context.
        
        This ensures that tools have access to team_id, user_id, and other
        context information needed for proper execution.
        
        Args:
            context: Execution context containing team_id, user_id, etc.
        """
        try:
            team_id = context.get('team_id')
            user_id = context.get('user_id')
            chat_id = context.get('chat_id')
            
            logger.info(f"[TOOL CONFIG] Configuring tools with context: team_id={team_id}, user_id={user_id}, chat_id={chat_id}")
            
            # Configure each tool with the context
            for tool in self.tools:
                self._configure_single_tool(tool, context)
                
            # Also configure CrewAI agent tools if they exist
            if hasattr(self._crew_agent, 'tools') and self._crew_agent.tools:
                for tool in self._crew_agent.tools:
                    self._configure_single_tool(tool, context)
                    
            logger.info(f"[TOOL CONFIG] Successfully configured {len(self.tools)} tools with execution context")
            
        except Exception as e:
            logger.error(f"[TOOL CONFIG] Error configuring tools with context: {e}", exc_info=True)
            # Don't raise - this is not critical for execution
    
    def _configure_single_tool(self, tool: Any, context: Dict[str, Any]) -> None:
        """
        Configure a single tool with execution context.
        
        Args:
            tool: The tool to configure
            context: Execution context
        """
        try:
            # Set team_id on tools that support it
            if hasattr(tool, 'team_id'):
                tool.team_id = context.get('team_id')
                logger.debug(f"[TOOL CONFIG] Set team_id={context.get('team_id')} on tool {getattr(tool, 'name', 'unknown')}")
            
            # Set user_id on tools that support it
            if hasattr(tool, 'user_id'):
                tool.user_id = context.get('user_id')
                logger.debug(f"[TOOL CONFIG] Set user_id={context.get('user_id')} on tool {getattr(tool, 'name', 'unknown')}")
            
            # Set chat_id on tools that support it
            if hasattr(tool, 'chat_id'):
                tool.chat_id = context.get('chat_id')
                logger.debug(f"[TOOL CONFIG] Set chat_id={context.get('chat_id')} on tool {getattr(tool, 'name', 'unknown')}")
            
            # Call custom configuration method if available
            if hasattr(tool, 'configure_with_context'):
                tool.configure_with_context(context)
                logger.debug(f"[TOOL CONFIG] Called configure_with_context on tool {getattr(tool, 'name', 'unknown')}")
                
        except Exception as e:
            logger.warning(f"[TOOL CONFIG] Error configuring tool {getattr(tool, 'name', 'unknown')}: {e}")
            # Don't raise - continue with other tools
    
    def get_role(self) -> AgentRole:
        """Get the agent's role."""
        return self.role
    
    def get_goal(self) -> str:
        """Get the agent's goal."""
        return self.config.goal
    
    def get_backstory(self) -> str:
        """Get the agent's backstory."""
        return self.config.backstory
    
    def get_tools(self) -> List[BaseTool]:
        """Get the agent's tools."""
        return self.tools
    
    def is_enabled(self) -> bool:
        """Check if the agent is enabled."""
        return self.config.enabled
    
    def get_crew_agent(self) -> Agent:
        """Get the underlying CrewAI agent."""
        return self._crew_agent
    
    def update_config(self, new_config: AgentConfig) -> None:
        """
        Update the agent's configuration.
        
        Note: This will require recreating the CrewAI agent.
        """
        self.config = new_config
        self._crew_agent = self._create_crew_agent()
        logger.info(f"Updated configuration for agent {self.role}")
    
    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)
        # Recreate the CrewAI agent with new tools
        self._crew_agent = self._create_crew_agent()
        logger.info(f"Added tool to agent {self.role}")
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent."""
        self.tools = [tool for tool in self.tools if tool.name != tool_name]
        # Recreate the CrewAI agent with updated tools
        self._crew_agent = self._create_crew_agent()
        logger.info(f"Removed tool {tool_name} from agent {self.role}")
    
    def get_memory(self) -> Optional[Any]:
        """Get the agent's memory if enabled."""
        if self.config.memory_enabled and self.team_memory:
            return self.team_memory.get_memory()
        return None
    
    def clear_memory(self) -> None:
        """Clear the agent's memory."""
        if self.team_memory:
            self.team_memory.clear()
            logger.info(f"Cleared memory for agent {self.role}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's configuration."""
        return {
            'role': self.role.value,
            'goal': self.config.goal,
            'enabled': self.config.enabled,
            'tools_count': len(self.tools),
            'tool_names': [tool.name for tool in self.tools],
            'behavioral_mixin': self.config.behavioral_mixin,
            'memory_enabled': self.config.memory_enabled,
            'learning_enabled': self.config.learning_enabled,
            'max_iterations': self.config.max_iterations,
            'allow_delegation': self.config.allow_delegation,
            'verbose': self.config.verbose
        }


class AgentFactory:
    """
    Factory for creating ConfigurableAgent instances.
    
    This factory reads configuration from the centralized config system
    and creates appropriately configured agents.
    """
    
    def __init__(self, team_id: str, llm: Any, tool_registry: Dict[str, BaseTool]):
        """
        Initialize the agent factory.
        
        Args:
            team_id: The team ID for the agents
            llm: The language model to use
            tool_registry: Registry of available tools
        """
        self.team_id = team_id
        self.llm = llm
        self.tool_registry = tool_registry
        self.team_memory = TeamMemory(team_id)
        
        logger.info(f"Initialized AgentFactory for team {team_id}")
    
    def create_agent(self, role: AgentRole) -> Optional[ConfigurableAgent]:
        """Create an agent for the specified role."""
        try:
            logger.info(f"[AGENT FACTORY] Creating agent for role: {role.value}")
            
            # Get agent configuration
            config = get_agent_config(role)
            if not config:
                logger.warning(f"[AGENT FACTORY] No configuration found for role {role}")
                return None
            
            if not config.enabled:
                logger.info(f"[AGENT FACTORY] Agent {role.value} is disabled, skipping creation")
                return None
            
            logger.info(f"[AGENT FACTORY] Agent configuration: enabled={config.enabled}, tools={config.tools}")
            
            # Get tools for this agent
            tools = self._get_tools_for_role(config.tools)
            logger.info(f"[AGENT FACTORY] Found {len(tools)} tools for agent {role.value}: {[tool.name for tool in tools]}")
            
            # Create team memory if needed
            team_memory = None
            if config.memory_enabled:
                from agents.team_memory import TeamMemory
                team_memory = TeamMemory(self.team_id)
                logger.info(f"[AGENT FACTORY] Created team memory for agent {role.value}")
            
            # Create agent context
            context = AgentCreationContext(
                team_id=self.team_id,
                llm=self.llm,
                tools=tools,
                config=config,
                team_memory=team_memory
            )
            
            logger.info(f"[AGENT FACTORY] Created agent context for {role.value}")
            
            # Create the agent
            agent = ConfigurableAgent(context)
            
            logger.info(f"[AGENT FACTORY] ✅ Successfully created agent {role.value}")
            logger.info(f"[AGENT FACTORY] Agent {role.value} tools: {[tool.name for tool in agent.get_tools()]}")
            
            return agent
            
        except Exception as e:
            logger.error(f"[AGENT FACTORY] Error creating agent {role.value}: {e}", exc_info=True)
            return None
    
    def create_all_agents(self) -> Dict[AgentRole, ConfigurableAgent]:
        """
        Create all enabled agents.
        
        Returns:
            Dictionary mapping roles to agent instances
        """
        agents = {}
        
        for role in AgentRole:
            agent = self.create_agent(role)
            if agent:
                agents[role] = agent
        
        logger.info(f"Created {len(agents)} agents for team {self.team_id}")
        return agents
    
    def _get_tools_for_role(self, tool_names: List[str]) -> List[BaseTool]:
        """Get tools for a specific role."""
        tools = []
        
        logger.info(f"[AGENT FACTORY] Getting tools for role: {tool_names}")
        logger.info(f"[AGENT FACTORY] Available tools in registry: {list(self.tool_registry.keys())}")
        
        for tool_name in tool_names:
            if tool_name in self.tool_registry:
                tool = self.tool_registry[tool_name]
                tools.append(tool)
                logger.info(f"[AGENT FACTORY] ✅ Found tool '{tool_name}' for role")
            else:
                logger.warning(f"[AGENT FACTORY] ❌ Tool '{tool_name}' not found in registry")
        
        logger.info(f"[AGENT FACTORY] Returning {len(tools)} tools for role")
        return tools
    
    def update_tool_registry(self, new_tool_registry: Dict[str, BaseTool]) -> None:
        """Update the tool registry."""
        self.tool_registry = new_tool_registry
        logger.info("Updated tool registry in AgentFactory")
    
    def get_available_roles(self) -> List[AgentRole]:
        """Get list of available agent roles."""
        return list(AgentRole)
    
    def get_enabled_roles(self) -> List[AgentRole]:
        """Get list of enabled agent roles."""
        enabled_roles = []
        for role in AgentRole:
            config = get_agent_config(role)
            if config and config.enabled:
                enabled_roles.append(role)
        return enabled_roles


# Convenience functions for backward compatibility
def create_agent(role: AgentRole, team_id: str, llm: Any, tools: List[BaseTool]) -> Optional[ConfigurableAgent]:
    """Create a single agent (convenience function)."""
    tool_registry = {tool.name: tool for tool in tools}
    factory = AgentFactory(team_id, llm, tool_registry)
    return factory.create_agent(role)


def create_all_agents(team_id: str, llm: Any, tool_registry: Dict[str, BaseTool]) -> Dict[AgentRole, ConfigurableAgent]:
    """Create all agents (convenience function)."""
    factory = AgentFactory(team_id, llm, tool_registry)
    return factory.create_all_agents() 