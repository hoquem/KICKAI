#!/usr/bin/env python3
"""
Simplified CrewAI Football Team Management System - 8-Agent Architecture

This module implements a simplified team management system using the new
generic ConfigurableAgent class and centralized configuration system.

8-Agent Architecture:
1. Message Processor: Primary user interface and command parsing
2. Team Manager: Strategic coordination and high-level planning
3. Player Coordinator: Operational player management and registration
4. Finance Manager: Financial tracking and payment management
5. Performance Analyst: Performance analysis and tactical insights
6. Learning Agent: Continuous learning and system improvement
7. Onboarding Agent: Specialized player onboarding and registration
8. Command Fallback Agent: Handles unrecognized commands and fallback scenarios

Each agent is created using the generic ConfigurableAgent class with
configuration from the centralized config system.
"""

import logging
import traceback
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from functools import wraps

from crewai import Agent, Crew
from langchain.tools import BaseTool

from core.improved_config_system import get_improved_config, TeamConfig
from core.enums import AgentRole, AIProvider
from config.agents import get_agent_config, get_enabled_agent_configs
from agents.configurable_agent import ConfigurableAgent, AgentFactory
from utils.llm_factory import LLMFactory, LLMConfig, LLMProviderError
from agents.intelligent_system import (
    IntentClassifier, RequestComplexityAssessor, DynamicTaskDecomposer,
    CapabilityBasedRouter, TaskExecutionOrchestrator, UserPreferenceLearner,
    TaskContext, TaskComplexity, Subtask, CapabilityType
)

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass


class AgentInitializationError(Exception):
    """Raised when agent initialization fails."""
    pass


def log_errors(func):
    """Decorator to log errors in agent operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper


class AgentToolsManager:
    """Manages tool loading and configuration for agents."""
    
    def __init__(self, team_config: TeamConfig):
        self.team_config = team_config
        self._tool_registry = self._build_tool_registry()
    
    def _build_tool_registry(self) -> Dict[str, BaseTool]:
        """Build the tool registry with all available tools."""
        tool_registry = {}
        
        try:
            # Import and register only the tools that actually exist
            from domain.tools.communication_tools import (
                SendMessageTool, SendPollTool, SendAnnouncementTool
            )
            
            # Communication tools
            tool_registry['send_message'] = SendMessageTool(team_id=self.team_config.team_id)
            tool_registry['send_poll'] = SendPollTool(team_id=self.team_config.team_id)
            tool_registry['send_announcement'] = SendAnnouncementTool(team_id=self.team_config.team_id)
            
            logger.info(f"✅ Tool registry built with {len(tool_registry)} tools")
            
        except Exception as e:
            logger.error(f"Error building tool registry: {e}", exc_info=True)
            # Don't raise the exception, just return empty registry
            return {}
        
        return tool_registry
    
    @log_errors
    def get_tools_for_agent(self, role: AgentRole) -> List[BaseTool]:
        """Get tools for a specific agent role."""
        try:
            # Get agent configuration
            config = get_agent_config(role)
            if not config:
                logger.warning(f"No configuration found for role {role}")
                return []
            
            # Get tools based on configuration
            tools = []
            for tool_name in config.tools:
                if tool_name in self._tool_registry:
                    tools.append(self._tool_registry[tool_name])
                else:
                    logger.warning(f"Tool {tool_name} not found in registry for role {role}")
            
            logger.info(f"🔧 Loading {len(tools)} tools for {role.value}")
            return tools
            
        except Exception as e:
            logger.error(f"Error getting tools for agent {role}: {e}")
            return []
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tool_registry.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        if tool_name in self._tool_registry:
            tool = self._tool_registry[tool_name]
            return {
                'name': tool.name,
                'description': tool.description,
                'type': type(tool).__name__
            }
        return None


class TeamManagementSystem:
    """
    Simplified Team Management System using generic ConfigurableAgent.
    
    This system uses the new generic ConfigurableAgent class and centralized
    configuration to create and manage all agents.
    """
    
    def __init__(self, team_id: str):
        """
        Initialize the team management system.
        
        Args:
            team_id: The team ID to manage
        """
        logger.info(f"[TEAM INIT] Starting TeamManagementSystem initialization for team {team_id}")
        
        self.team_id = team_id
        self.agents: Dict[AgentRole, ConfigurableAgent] = {}
        self.crew: Optional[Crew] = None
        
        # Initialize configuration
        logger.info(f"[TEAM INIT] Getting improved config")
        self.config_manager = get_improved_config()
        logger.info(f"[TEAM INIT] Getting team config for {team_id}")
        self.team_config = self.config_manager.get_team_config(team_id)
        logger.info(f"[TEAM INIT] Loaded team_config: {self.team_config}")
        
        if not self.team_config:
            raise ConfigurationError(f"No team configuration found for {team_id}")
        
        # Initialize LLM
        logger.info(f"[TEAM INIT] Initializing LLM")
        self._initialize_llm()
        
        # Initialize agents
        logger.info(f"[TEAM INIT] Initializing agents dictionary")
        self._initialize_agents()
        
        # Create crew
        logger.info(f"[TEAM INIT] Creating crew")
        self._create_crew()
        
        logger.info(f"✅ TeamManagementSystem initialized for team {team_id}")
    
    def _initialize_llm(self):
        """Initialize the language model."""
        try:
            import os
            from utils.llm_factory import LLMConfig
            
            # Get AI configuration from team config
            ai_config = self.team_config.ai_config if hasattr(self.team_config, 'ai_config') else None
            
            if ai_config:
                logger.info(f"Initializing LangChain Gemini LLM with model: {ai_config.model_name}")
                config = LLMConfig(
                    provider=AIProvider.GOOGLE_GEMINI,
                    model_name=ai_config.model_name,
                    api_key=ai_config.api_key or os.getenv('GOOGLE_API_KEY'),
                    temperature=ai_config.temperature,
                    timeout_seconds=ai_config.timeout_seconds,
                    max_retries=ai_config.max_retries
                )
                self.llm = LLMFactory.create_llm(config)
            else:
                # Fallback to default configuration
                logger.info("Initializing LangChain Gemini LLM with default model: gemini-1.5-flash")
                config = LLMConfig(
                    provider=AIProvider.GOOGLE_GEMINI,
                    model_name="gemini-1.5-flash",
                    api_key=os.getenv('GOOGLE_API_KEY'),
                    temperature=0.7,
                    timeout_seconds=60,
                    max_retries=3
                )
                self.llm = LLMFactory.create_llm(config)
            
            logger.info(f"✅ LangChain Gemini LLM initialized successfully: {type(self.llm).__name__}")
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}", exc_info=True)
            raise
    
    def _initialize_agents(self) -> None:
        """Initialize all agents using the new generic ConfigurableAgent system."""
        try:
            logger.info(f"[AGENT INIT] Initializing agents...")
            
            # Create tools manager
            tools_manager = AgentToolsManager(self.team_config)
            
            # Create agent factory
            agent_factory = AgentFactory(
                team_id=self.team_id,
                llm=self.llm,
                tool_registry={name: tool for name, tool in tools_manager._tool_registry.items()}
            )
            
            # Create all enabled agents
            self.agents = agent_factory.create_all_agents()
            
            if not self.agents:
                raise AgentInitializationError("No agents were initialized!")
            
            logger.info(f"[AGENT INIT] All enabled agents initialized: {list(self.agents.keys())}")
            
        except Exception as e:
            logger.error(f"[AGENT INIT] Critical error in agent initialization: {e}", exc_info=True)
            raise
    
    def _create_crew(self) -> None:
        """Create the CrewAI crew."""
        if not self.agents:
            raise AgentInitializationError("No agents available to create crew")
        
        crew_agents = [agent.get_crew_agent() for agent in self.agents.values()]
        
        # Create crew with LangChain Gemini LLM
        self.crew = Crew(
            agents=crew_agents,
            verbose=True,
            memory=True,
            llm=self.llm
        )
        
        logger.info(f"✅ Crew created successfully with {len(crew_agents)} agents using LangChain Gemini LLM")
    
    def get_agent(self, role: AgentRole) -> Optional[ConfigurableAgent]:
        """Get a specific agent by role."""
        return self.agents.get(role)
    
    def get_enabled_agents(self) -> List[ConfigurableAgent]:
        """Get all enabled agents."""
        return list(self.agents.values())
    
    def get_orchestration_pipeline_status(self) -> Dict[str, Any]:
        """Get the status of the orchestration pipeline."""
        if hasattr(self, '_orchestration_pipeline'):
            return self._orchestration_pipeline.get_pipeline_status()
        else:
            return {
                'orchestration_pipeline': 'Not initialized',
                'all_components_initialized': False
            }
    
    async def execute_task(self, task_description: str, execution_context: Dict[str, Any]) -> str:
        """
        Execute a task using the orchestration pipeline.
        
        This method delegates task execution to the dedicated OrchestrationPipeline
        which breaks down the process into separate, swappable components.
        """
        try:
            # Initialize orchestration pipeline if not already done
            if not hasattr(self, '_orchestration_pipeline'):
                from agents.orchestration_pipeline import OrchestrationPipeline
                self._orchestration_pipeline = OrchestrationPipeline(llm=self.llm)
                logger.info(f"🤖 ORCHESTRATION: Initialized orchestration pipeline for team {self.team_id}")
            
            # Enhanced logging for debugging
            is_help_command = task_description.lower().strip() == "/help"
            if is_help_command:
                logger.info(f"🤖 ORCHESTRATION: Help command detected")
                
                # Get the Message Processor agent for help commands
                message_processor = self.get_agent(AgentRole.MESSAGE_PROCESSOR)
                if message_processor:
                    result = await message_processor.execute(task_description, execution_context)
                    logger.info(f"🤖 ORCHESTRATION: Help command executed successfully")
                    return result
                else:
                    return "❌ Sorry, the help system is currently unavailable."
            
            # Use the orchestration pipeline for all other tasks
            logger.info(f"🤖 ORCHESTRATION: Using orchestration pipeline for task execution")
            
            # Execute using the orchestration pipeline
            result = await self._orchestration_pipeline.execute_task(
                task_description=task_description,
                available_agents=self.agents,
                execution_context=execution_context
            )
            
            return str(result) if result else "Task completed successfully."
            
        except Exception as e:
            logger.error(f"Error in TeamManagementSystem.execute_task: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error processing your request: {str(e)}"
    
    @contextmanager
    def debug_mode(self):
        """Context manager for debug mode."""
        original_level = logger.level
        logger.setLevel(logging.DEBUG)
        try:
            yield
        finally:
            logger.setLevel(original_level)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the system."""
        try:
            health_status = {
                'system': 'healthy',
                'agents_count': len(self.agents),
                'agents': {},
                'crew_created': self.crew is not None,
                'llm_available': self.llm is not None,
                'team_config_loaded': self.team_config is not None
            }
            
            # Check each agent
            for role, agent in self.agents.items():
                health_status['agents'][role.value] = {
                    'enabled': agent.is_enabled(),
                    'tools_count': len(agent.get_tools()),
                    'crew_agent_available': agent.get_crew_agent() is not None
                }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                'system': 'unhealthy',
                'error': str(e)
            }


# Convenience functions for backward compatibility
def create_team_management_system(team_id: str) -> TeamManagementSystem:
    """Create a team management system for the specified team."""
    return TeamManagementSystem(team_id)


def get_agent(team_id: str, role: AgentRole) -> Optional[ConfigurableAgent]:
    """Get a specific agent for a team."""
    system = TeamManagementSystem(team_id)
    return system.get_agent(role)


def execute_task(team_id: str, task_description: str, execution_context: Dict[str, Any]) -> str:
    """Execute a task for a team."""
    system = TeamManagementSystem(team_id)
    import asyncio
    return asyncio.run(system.execute_task(task_description, execution_context)) 