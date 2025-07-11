#!/usr/bin/env python3
"""
Simplified CrewAI Football Team Management System - 8-Agent Architecture

This module provides a simplified, production-ready implementation of the
CrewAI-based football team management system with 8 specialized agents.
"""

import logging
import asyncio
import os
import sys
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
import traceback
import time



from crewai import Agent, Crew
from langchain_core.tools import BaseTool

from core.settings import get_settings
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
    
    def __init__(self, team_config, telegram_context=None):
        self.team_config = team_config
        self.telegram_context = telegram_context
        self._tool_registry = self._build_tool_registry()
    
    def _build_tool_registry(self) -> Dict[str, BaseTool]:
        """Build the tool registry with all available tools."""
        tool_registry = {}
        
        print(f"🔍 [DEBUG] AgentToolsManager._build_tool_registry called for team {self.team_config.default_team_id}")
        logger.info(f"[TOOL REGISTRY] Starting tool registry build for team {self.team_config.default_team_id}")
        
        try:
            # Import and register all available tools
            from domain.tools.communication_tools import (
                SendMessageTool, SendPollTool, SendAnnouncementTool
            )
            from domain.tools.player_tools import (
                GetAllPlayersTool, GetPlayerByIdTool, GetPendingApprovalsTool,
    GetPlayerStatusTool, GetMyStatusTool, ApprovePlayerTool
            )
            from domain.tools.logging_tools import (
                LogCommandTool, LogEventTool
            )
            
            # Get command operations interface
            from domain.interfaces.command_operations import ICommandOperations
            from services.command_operations_factory import get_command_operations
            
            print(f"🔍 [DEBUG] Getting command operations interface")
            logger.info(f"[TOOL REGISTRY] Getting command operations interface")
            command_operations = get_command_operations()
            print(f"🔍 [DEBUG] Command operations interface: {type(command_operations).__name__}")
            logger.info(f"[TOOL REGISTRY] Command operations interface: {type(command_operations).__name__}")
            
            # Communication tools
            print(f"🔍 [DEBUG] Registering communication tools")
            logger.info(f"[TOOL REGISTRY] Registering communication tools")
            send_message_tool = SendMessageTool(team_id=self.team_config.default_team_id)
            if self.telegram_context:
                send_message_tool.set_telegram_context(self.telegram_context)
            tool_registry['send_message'] = send_message_tool
            tool_registry['send_poll'] = SendPollTool(team_id=self.team_config.default_team_id)
            tool_registry['send_announcement'] = SendAnnouncementTool(team_id=self.team_config.default_team_id)
            print(f"🔍 [DEBUG] Communication tools registered: {list(tool_registry.keys())[-3:]}")
            logger.info(f"[TOOL REGISTRY] ✅ Communication tools registered: {list(tool_registry.keys())[-3:]}")
            
            # Player tools - need command_operations
            print(f"🔍 [DEBUG] Registering player tools with command_operations")
            logger.info(f"[TOOL REGISTRY] Registering player tools with command_operations")
            tool_registry['get_all_players'] = GetAllPlayersTool(team_id=self.team_config.default_team_id, command_operations=command_operations)
            tool_registry['get_player_by_id'] = GetPlayerByIdTool(team_id=self.team_config.default_team_id, command_operations=command_operations)
            tool_registry['get_pending_approvals'] = GetPendingApprovalsTool(team_id=self.team_config.default_team_id, command_operations=command_operations)
            tool_registry['get_player_status'] = GetPlayerStatusTool(team_id=self.team_config.default_team_id, command_operations=command_operations)
            tool_registry['get_my_status'] = GetMyStatusTool(team_id=self.team_config.default_team_id, command_operations=command_operations)
            tool_registry['approve_player'] = ApprovePlayerTool(team_id=self.team_config.default_team_id, command_operations=command_operations)
            print(f"🔍 [DEBUG] Player tools registered: {list(tool_registry.keys())[-6:]}")
            logger.info(f"[TOOL REGISTRY] ✅ Player tools registered: {list(tool_registry.keys())[-6:]}")
            
            # Logging tools
            print(f"🔍 [DEBUG] Registering logging tools")
            logger.info(f"[TOOL REGISTRY] Registering logging tools")
            tool_registry['log_command'] = LogCommandTool(team_id=self.team_config.default_team_id)
            tool_registry['log_event'] = LogEventTool(team_id=self.team_config.default_team_id)
            print(f"🔍 [DEBUG] Logging tools registered: {list(tool_registry.keys())[-2:]}")
            logger.info(f"[TOOL REGISTRY] ✅ Logging tools registered: {list(tool_registry.keys())[-2:]}")
            
            # Debug: print type, module, and MRO for each tool
            print(f"🔍 [DEBUG] Tool registry details:")
            logger.info(f"[TOOL REGISTRY] Tool registry details:")
            for name, tool in tool_registry.items():
                print(f"[TOOL DEBUG] {name}: type={type(tool)}, module={tool.__class__.__module__}, mro={tool.__class__.__mro__}")
                logger.info(f"[TOOL DEBUG] {name}: type={type(tool)}, module={tool.__class__.__module__}, mro={tool.__class__.__mro__}")
                logger.info(f"[TOOL DEBUG] {name}: name='{tool.name}', description='{tool.description}'")
            
            print(f"🔍 [DEBUG] Tool registry built with {len(tool_registry)} tools: {list(tool_registry.keys())}")
            logger.info(f"✅ Tool registry built with {len(tool_registry)} tools: {list(tool_registry.keys())}")
            
        except Exception as e:
            print(f"❌ [DEBUG] Error building tool registry: {e}")
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
        self.config_manager = get_settings()
        logger.info(f"[TEAM INIT] Getting team config for {team_id}")
        self.team_config = self.config_manager
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
        """Initialize the LLM using the factory pattern with robust error handling."""
        try:
            # Use the new factory method that reads from environment
            self.llm = LLMFactory.create_from_environment()
            
            # Wrap the LLM with our robust error handling for CrewAI
            self.llm = self._wrap_llm_with_error_handling(self.llm)
            
            logger.info(f"✅ LLM initialized successfully with robust error handling: {type(self.llm).__name__}")
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}", exc_info=True)
            raise
    
    def _wrap_llm_with_error_handling(self, llm):
        """Wrap the LLM with robust error handling for CrewAI."""
        try:
            # Create a wrapper that adds error handling to the LLM
            class RobustLLMWrapper:
                def __init__(self, original_llm):
                    self.original_llm = original_llm
                    self.model_name = getattr(original_llm, 'model_name', 'unknown')
                    self.client = getattr(original_llm, 'client', None)
                
                def invoke(self, prompt, **kwargs):
                    """Synchronous invoke with error handling."""
                    start_time = time.time()
                    try:
                        logger.info(f"[LLM REQUEST] CrewAI invoke request to {self.model_name}")
                        logger.info(f"[LLM REQUEST] Prompt preview: {str(prompt)[:100]}...")
                        
                        result = self.original_llm.invoke(prompt, **kwargs)
                        
                        duration = (time.time() - start_time) * 1000
                        logger.info(f"[LLM SUCCESS] CrewAI invoke completed in {duration:.2f}ms")
                        logger.info(f"[LLM SUCCESS] Result preview: {str(result)[:100]}...")
                        
                        return result
                        
                    except Exception as e:
                        duration = (time.time() - start_time) * 1000
                        self._handle_crewai_error(e, duration, prompt, **kwargs)
                        raise
                
                async def ainvoke(self, prompt, **kwargs):
                    """Asynchronous invoke with error handling."""
                    start_time = time.time()
                    try:
                        logger.info(f"[LLM REQUEST] CrewAI ainvoke request to {self.model_name}")
                        logger.info(f"[LLM REQUEST] Prompt preview: {str(prompt)[:100]}...")
                        
                        result = await self.original_llm.ainvoke(prompt, **kwargs)
                        
                        duration = (time.time() - start_time) * 1000
                        logger.info(f"[LLM SUCCESS] CrewAI ainvoke completed in {duration:.2f}ms")
                        logger.info(f"[LLM SUCCESS] Result preview: {str(result)[:100]}...")
                        
                        return result
                        
                    except Exception as e:
                        duration = (time.time() - start_time) * 1000
                        self._handle_crewai_error(e, duration, prompt, **kwargs)
                        raise
                
                def _handle_crewai_error(self, error, duration_ms, prompt, **kwargs):
                    """Handle CrewAI LLM errors with detailed logging."""
                    error_type = type(error).__name__
                    error_msg = str(error)
                    
                    # Create detailed error context
                    error_context = {
                        "error_type": error_type,
                        "error_message": error_msg,
                        "model": self.model_name,
                        "duration_ms": duration_ms,
                        "prompt_length": len(str(prompt)),
                        "kwargs": list(kwargs.keys())
                    }
                    
                    # Categorize and log errors appropriately
                    if "503" in error_msg or "service unavailable" in error_msg.lower():
                        logger.error(f"[LLM ERROR] 🚫 SERVICE UNAVAILABLE (503): {error_msg}")
                        logger.error(f"[LLM ERROR] 🚫 Google Gemini API is temporarily unavailable")
                        logger.error(f"[LLM ERROR] 🚫 This is a Google service issue, not a configuration problem")
                        logger.error(f"[LLM ERROR] 🚫 Error context: {error_context}")
                        
                    elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                        logger.error(f"[LLM ERROR] ⏰ TIMEOUT ERROR: {error_msg}")
                        logger.error(f"[LLM ERROR] ⏰ Request timed out after {duration_ms:.2f}ms")
                        logger.error(f"[LLM ERROR] ⏰ Consider increasing timeout or checking network connectivity")
                        logger.error(f"[LLM ERROR] ⏰ Error context: {error_context}")
                        
                    elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                        logger.error(f"[LLM ERROR] 📊 QUOTA/RATE LIMIT ERROR: {error_msg}")
                        logger.error(f"[LLM ERROR] 📊 Google Gemini API quota exceeded or rate limited")
                        logger.error(f"[LLM ERROR] 📊 Check your Google Cloud Console for quota usage")
                        logger.error(f"[LLM ERROR] 📊 Error context: {error_context}")
                        
                    elif "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                        logger.critical(f"[LLM ERROR] 🔑 API KEY ERROR: {error_msg}")
                        logger.critical(f"[LLM ERROR] 🔑 This is likely an invalid or expired GOOGLE_API_KEY")
                        logger.critical(f"[LLM ERROR] 🔑 Please check your .env file and ensure GOOGLE_API_KEY is correct")
                        logger.critical(f"[LLM ERROR] 🔑 Error context: {error_context}")
                        
                    else:
                        # Generic error handling
                        logger.error(f"[LLM ERROR] ❌ UNKNOWN ERROR: {error_msg}")
                        logger.error(f"[LLM ERROR] ❌ Error type: {error_type}")
                        logger.error(f"[LLM ERROR] ❌ Full error context: {error_context}")
                        logger.error(f"[LLM ERROR] ❌ Full traceback: {traceback.format_exc()}")
                    
                    # Additional diagnostics
                    logger.info(f"[LLM DIAGNOSTICS] Environment check:")
                    logger.info(f"[LLM DIAGNOSTICS] - GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")
                    logger.info(f"[LLM DIAGNOSTICS] - AI_PROVIDER: {os.getenv('AI_PROVIDER', 'not set')}")
                    logger.info(f"[LLM DIAGNOSTICS] - AI_MODEL_NAME: {os.getenv('AI_MODEL_NAME', 'not set')}")
                    logger.info(f"[LLM DIAGNOSTICS] - Request duration: {duration_ms:.2f}ms")
                
                # Forward any other attributes to the original LLM
                def __getattr__(self, name):
                    return getattr(self.original_llm, name)
            
            return RobustLLMWrapper(llm)
            
        except Exception as e:
            logger.error(f"Error wrapping LLM with error handling: {e}")
            return llm  # Return original LLM if wrapping fails
    
    def _initialize_agents(self) -> None:
        """Initialize all agents using the new generic ConfigurableAgent system."""
        try:
            logger.info(f"[AGENT INIT] Initializing agents...")
            
            # Create tools manager
            tools_manager = AgentToolsManager(self.team_config, telegram_context=None)
            
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
            logger.info(f"🤖 TEAM MANAGEMENT: Starting task execution for team {self.team_id}")
            logger.info(f"🤖 TEAM MANAGEMENT: Task description: {task_description}")
            logger.info(f"🤖 TEAM MANAGEMENT: Execution context: {execution_context}")
            logger.info(f"🤖 TEAM MANAGEMENT: Available agents: {[role.value for role in self.agents.keys()]}")
            
            # Log agent details
            for role, agent in self.agents.items():
                tools = agent.get_tools()
                logger.info(f"🤖 TEAM MANAGEMENT: Agent '{role.value}' has {len(tools)} tools: {[tool.name for tool in tools]}")
            
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
                    logger.info(f"🤖 ORCHESTRATION: Using Message Processor agent for help command")
                    result = await message_processor.execute(task_description, execution_context)
                    logger.info(f"🤖 ORCHESTRATION: Help command executed successfully")
                    return result
                else:
                    logger.warning(f"🤖 ORCHESTRATION: Message Processor agent not available for help command")
                    return "❌ Sorry, the help system is currently unavailable."
            
            # Use the orchestration pipeline for all other tasks
            logger.info(f"🤖 ORCHESTRATION: Using orchestration pipeline for task execution")
            
            # Execute using the orchestration pipeline
            result = await self._orchestration_pipeline.execute_task(
                task_description=task_description,
                available_agents=self.agents,
                execution_context=execution_context
            )
            
            logger.info(f"🤖 TEAM MANAGEMENT: Task execution completed successfully")
            logger.info(f"🤖 TEAM MANAGEMENT: Result length: {len(str(result))} characters")
            
            return str(result) if result else "Task completed successfully."
            
        except Exception as e:
            print(f"[AGENT ERROR TRACE] {traceback.format_exc()}")
            logger.error(f"[AGENT ERROR TRACE] Error in TeamManagementSystem.execute_task: {e}", exc_info=True)
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