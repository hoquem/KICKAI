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

from core.enums import AgentRole
from core.exceptions import AgentInitializationError, ConfigurationError
from config.agents import get_agent_config, AgentConfig
from agents.behavioral_mixins import get_mixin_for_role
from agents.team_memory import TeamMemory
from core.error_handling import handle_agent_errors, validate_input


logger = logging.getLogger(__name__)


class LoggingCrewAIAgent(Agent):
    """CrewAI Agent with enhanced logging capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"🤖 Created CrewAI Agent: {self.role}")


@dataclass
class AgentContext:
    """Context for agent creation and configuration."""
    
    team_id: str
    role: AgentRole
    llm: Any
    tool_registry: Dict[str, Any]
    team_memory: Optional[TeamMemory] = None
    config: Optional[AgentConfig] = None


class AgentToolsManager:
    """Manages tool assignment for agents."""
    
    def __init__(self, tool_registry: Dict[str, Any]):
        self.tool_registry = tool_registry
        logger.info(f"🔧 AgentToolsManager initialized with {len(tool_registry)} tools")
    
    def get_tools_for_role(self, tool_names: List[str]) -> List[Any]:
        """Get tools for a specific role."""
        tools = []
        
        logger.info(f"[AGENT FACTORY] Getting tools for role: {tool_names}")
        logger.info(f"[AGENT FACTORY] Tool registry keys: {list(self.tool_registry.keys())}")
        
        for tool_name in tool_names:
            if tool_name in self.tool_registry:
                tool = self.tool_registry[tool_name]
                tools.append(tool)
                logger.info(f"[AGENT FACTORY] ✅ Found tool '{tool_name}' for role")
            else:
                logger.warning(f"[AGENT FACTORY] ❌ Tool '{tool_name}' not found in registry")
                logger.warning(f"[AGENT FACTORY] ❌ Available tools: {list(self.tool_registry.keys())}")
        
        logger.info(f"[AGENT FACTORY] Returning {len(tools)} tools for role")
        return tools


class ConfigurableAgent:
    """A configurable agent that can be used with different configurations."""
    
    def __init__(self, context: AgentContext):
        """Initialize the configurable agent."""
        self.context = context
        self._crew_agent = self._create_crew_agent()
        self._tools_manager = AgentToolsManager(context.tool_registry)
        
        logger.info(f"🤖 ConfigurableAgent created for role: {context.role}")
    
    def _create_crew_agent(self) -> Agent:
        """Create the underlying CrewAI agent."""
        try:
            config = self.context.config or get_agent_config(self.context.role)
            
            if not config or not config.enabled:
                raise ConfigurationError(f"Agent configuration not found or disabled for role: {self.context.role}")
            
            # Get tools for this role
            tools = self._get_tools_for_role(config.tools)
            
            # Get behavioral mixin if available
            mixin = get_mixin_for_role(self.context.role)
            
            # Build agent parameters
            agent_params = {
                "role": config.role.value,
                "goal": config.goal,
                "backstory": config.backstory,
                "tools": tools,
                "llm": self.context.llm,
                "verbose": True,
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
            raise AgentInitializationError(f"Failed to create agent for role {self.context.role}: {str(e)}")
    
    def _get_tools_for_role(self, tool_names: List[str]) -> List[Any]:
        """Get tools for a specific role."""
        tools = []
        
        logger.info(f"[AGENT FACTORY] Getting tools for role: {tool_names}")
        logger.info(f"[AGENT FACTORY] Tool registry keys: {list(self.context.tool_registry.keys())}")
        
        for tool_name in tool_names:
            if tool_name in self.context.tool_registry:
                tool = self.context.tool_registry[tool_name]
                tools.append(tool)
                logger.info(f"[AGENT FACTORY] ✅ Found tool '{tool_name}' for role")
            else:
                logger.warning(f"[AGENT FACTORY] ❌ Tool '{tool_name}' not found in registry")
                logger.warning(f"[AGENT FACTORY] ❌ Available tools: {list(self.context.tool_registry.keys())}")
        
        logger.info(f"[AGENT FACTORY] Returning {len(tools)} tools for role")
        return tools
    
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
    def tools(self) -> List[Any]:
        """Get the agent's tools."""
        return self._crew_agent.tools
    
    def get_config_summary(self) -> Dict[str, Any]:
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
    
    def get_tools(self) -> List[Any]:
        """Get the agent's tools."""
        return self._crew_agent.tools
    
    def is_enabled(self) -> bool:
        """Check if the agent is enabled."""
        return True  # All agents are enabled by default
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> str:
        """Execute a task using the underlying CrewAI agent."""
        try:
            if context is None:
                context = {}
            
            # Create a simple task for the CrewAI agent
            from crewai import Task
            
            # Create a task with the description
            crew_task = Task(
                description=task,
                agent=self._crew_agent,
                expected_output="A clear and helpful response to the user's request"
            )
            
            # Execute the task using the agent's tools and LLM
            # Since we can't directly execute a single task, we'll simulate it
            # by creating a simple crew with just this agent and task
            from crewai import Crew
            
            crew = Crew(
                agents=[self._crew_agent],
                tasks=[crew_task],
                verbose=True
            )
            
            # Execute the crew (kickoff is not async)
            result = crew.kickoff()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error executing task with agent {self.role}: {e}")
            return f"❌ Error executing task: {str(e)}"


class AgentFactory:
    """Factory for creating agents with different configurations."""
    
    def __init__(self, team_id: str, llm: Any, tool_registry: Dict[str, Any]):
        """Initialize the agent factory."""
        self.team_id = team_id
        self.llm = llm
        self.tool_registry = tool_registry
        self.team_memory = TeamMemory(team_id)
        
        logger.info(f"🏭 AgentFactory initialized for team: {team_id}")
    
    def create_agent(self, role: AgentRole) -> ConfigurableAgent:
        """Create an agent for a specific role."""
        try:
            context = AgentContext(
                team_id=self.team_id,
                role=role,
                llm=self.llm,
                tool_registry=self.tool_registry,
                team_memory=self.team_memory
            )
            
            agent = ConfigurableAgent(context)
            logger.info(f"✅ Created agent for role: {role}")
            return agent
            
        except Exception as e:
            logger.error(f"❌ Failed to create agent for role {role}: {e}")
            raise AgentInitializationError(f"Failed to create agent for role {role}: {str(e)}")
    
    def create_all_agents(self) -> Dict[AgentRole, ConfigurableAgent]:
        """Create all enabled agents for the team."""
        agents = {}
        
        try:
            # Get all agent roles
            for role in AgentRole:
                try:
                    config = get_agent_config(role)
                    if config and config.enabled:
                        agent = self.create_agent(role)
                        agents[role] = agent
                        logger.info(f"✅ Created agent for role: {role}")
                    else:
                        logger.info(f"ℹ️ Skipping disabled agent role: {role}")
                except Exception as e:
                    logger.warning(f"❌ Failed to create agent for role: {role}")
                    logger.warning(f"❌ Error: {e}")
            
            logger.info(f"🎉 Created {len(agents)} agents for team {self.team_id}")
            return agents
            
        except Exception as e:
            logger.error(f"❌ Failed to create agents: {e}")
            raise AgentInitializationError(f"Failed to create agents: {str(e)}")
    
    def get_agent(self, role: AgentRole) -> Optional[ConfigurableAgent]:
        """Get an agent by role."""
        try:
            return self.create_agent(role)
        except Exception as e:
            logger.error(f"❌ Failed to get agent for role {role}: {e}")
            return None 