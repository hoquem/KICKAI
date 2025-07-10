"""
Generic ConfigurableAgent for KICKAI

This module provides a single, generic ConfigurableAgent class that can be
instantiated with different configurations for different roles. All agent-specific
configurations are managed through the centralized configuration system.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from crewai import Agent
from langchain.tools import BaseTool

from core.enums import AgentRole
from config.agents import get_agent_config, AgentConfig
from agents.behavioral_mixins import get_mixin_for_role
from agents.team_memory import TeamMemory
from core.error_handling import handle_agent_errors, validate_input


logger = logging.getLogger(__name__)


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
                'tools': self.tools,
                'llm': self.llm,
                'verbose': self.config.verbose,
                'allow_delegation': self.config.allow_delegation,
                'max_iter': self.config.max_iterations
            }
            
            # Add memory if enabled - use boolean value
            if self.config.memory_enabled:
                agent_params['memory'] = True
            else:
                agent_params['memory'] = False
            
            # Create the CrewAI agent
            crew_agent = Agent(**agent_params)
            
            logger.info(f"✅ Created CrewAI agent for role {self.config.role}")
            return crew_agent
            
        except Exception as e:
            logger.error(f"Error creating CrewAI agent for role {self.config.role}: {e}")
            raise
    
    @handle_agent_errors(operation="agent_execution")
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a task using this agent.
        
        Args:
            task: The task to execute
            context: Optional context information
            
        Returns:
            The result of task execution
        """
        # Validate inputs
        validate_input(task, str, "task", required=True)
        if context is not None:
            validate_input(context, dict, "context", required=False)
        
        # Apply behavioral mixin if available
        if self.behavioral_mixin and hasattr(self.behavioral_mixin, 'pre_execute'):
            task = self.behavioral_mixin.pre_execute(task, context)
        
        # Execute the task using the CrewAI agent
        result = self._crew_agent.execute(task)
        
        # Apply behavioral mixin post-processing if available
        if self.behavioral_mixin and hasattr(self.behavioral_mixin, 'post_execute'):
            result = self.behavioral_mixin.post_execute(result, context)
        
        return result
    
    @handle_agent_errors(operation="agent_task_execution")
    async def execute_task(self, subtask: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task using this agent (async version for orchestration pipeline).
        
        Args:
            subtask: The subtask to execute (can be a string or subtask object)
            context: Optional context information
            
        Returns:
            Dictionary containing the result of task execution
        """
        try:
            # Extract task description from subtask
            if hasattr(subtask, 'description'):
                task_description = subtask.description
            elif isinstance(subtask, dict):
                task_description = subtask.get('description', str(subtask))
            else:
                task_description = str(subtask)
            
            # Validate inputs
            validate_input(task_description, str, "task_description", required=True)
            if context is not None:
                validate_input(context, dict, "context", required=False)
            
            logger.info(f"Agent {self.role.value} executing task: {task_description[:100]}...")
            
            # Apply behavioral mixin if available
            if self.behavioral_mixin and hasattr(self.behavioral_mixin, 'pre_execute'):
                task_description = self.behavioral_mixin.pre_execute(task_description, context)
            
            # Execute the task using the CrewAI agent
            result = self._crew_agent.execute(task_description)
            
            # Apply behavioral mixin post-processing if available
            if self.behavioral_mixin and hasattr(self.behavioral_mixin, 'post_execute'):
                result = self.behavioral_mixin.post_execute(result, context)
            
            logger.info(f"Agent {self.role.value} completed task successfully")
            
            return {
                "success": True,
                "result": result,
                "agent_role": self.role.value,
                "task_description": task_description
            }
            
        except Exception as e:
            logger.error(f"Agent {self.role.value} failed to execute task: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_role": self.role.value,
                "task_description": getattr(subtask, 'description', str(subtask)) if hasattr(subtask, 'description') else str(subtask)
            }
    
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
        """
        Create a ConfigurableAgent for the specified role.
        
        Args:
            role: The agent role to create
            
        Returns:
            Configured agent instance or None if role not found/disabled
        """
        try:
            # Get configuration for the role
            config = get_agent_config(role)
            if not config:
                logger.warning(f"No configuration found for role {role}")
                return None
            
            if not config.enabled:
                logger.info(f"Agent role {role} is disabled")
                return None
            
            # Get tools for this role
            tools = self._get_tools_for_role(config.tools)
            
            # Create context
            context = AgentCreationContext(
                team_id=self.team_id,
                llm=self.llm,
                tools=tools,
                config=config,
                team_memory=self.team_memory
            )
            
            # Create and return the agent
            agent = ConfigurableAgent(context)
            logger.info(f"✅ Created agent for role {role}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent for role {role}: {e}")
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
        """
        Get tools for a role based on tool names.
        
        Args:
            tool_names: List of tool names to get
            
        Returns:
            List of tool instances
        """
        tools = []
        
        for tool_name in tool_names:
            if tool_name in self.tool_registry:
                tools.append(self.tool_registry[tool_name])
            else:
                logger.warning(f"Tool {tool_name} not found in registry")
        
        logger.info(f"🔧 Loading {len(tools)} tools for role")
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