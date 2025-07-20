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
from crewai.tools import tool

from src.core.settings import get_settings
from src.core.enums import AgentRole, AIProvider
from src.config.agents import get_agent_config, get_enabled_agent_configs
from src.agents.configurable_agent import ConfigurableAgent, AgentFactory
from src.utils.llm_factory import LLMFactory, LLMConfig, LLMProviderError
from src.agents.tool_registry import get_tool_registry, get_tool_names
from loguru import logger

class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass

class AgentInitializationError(Exception):
    """Raised when agent initialization fails."""
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

class AgentToolsManager:
    """Manages tool loading and configuration for agents using agent-specific tool lists."""
    
    def __init__(self, team_config, telegram_context=None):
        self.team_config = team_config
        self.telegram_context = telegram_context
        self._tool_registry = get_tool_registry()
        self._build_tool_registry()
    
    def _build_tool_registry(self) -> Dict[str, Any]:
        logger.debug(f"AgentToolsManager._build_tool_registry called for team {self.team_config.default_team_id}")
        logger.info(f"[TOOL REGISTRY] Starting tool registry build for team {self.team_config.default_team_id}")
        
        # Ensure tools are discovered
        if not self._tool_registry._discovered:
            self._tool_registry.auto_discover_tools()
        
        # Get all available tools
        available_tools = self._tool_registry.get_tool_names()
        logger.info(f"[TOOL REGISTRY] Loaded tools: {available_tools}")
        
        # Return tool functions mapping for backward compatibility
        return self._tool_registry.get_tool_functions()
    
    @log_errors
    def get_tools_for_agent(self, role: AgentRole) -> List[Any]:
        """Get tools for a specific agent role using agent-specific configuration."""
        try:
            # Get agent configuration
            config = get_agent_config(role)
            if not config:
                logger.warning(f"No configuration found for role {role}")
                return []
            
            # Get tools based on agent-specific configuration
            tools = []
            for tool_name in config.tools:
                tool_func = self._tool_registry.get_tool_function(tool_name)
                if tool_func:
                    tools.append(tool_func)
                    logger.info(f"[AGENT TOOLS] ✅ Found tool '{tool_name}' for {role.value}")
                else:
                    logger.warning(f"[AGENT TOOLS] ❌ Tool '{tool_name}' not found for {role.value}")
            
            logger.info(f"🔧 Loading {len(tools)} tools for {role.value}")
            return tools
            
        except Exception as e:
            logger.error(f"Error getting tools for agent {role}: {e}")
            return []
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return self._tool_registry.get_tool_names()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        tool = self._tool_registry.get_tool(tool_name)
        if tool:
            return {
                'name': tool.name,
                'description': tool.description,
                'type': tool.tool_type.value,
                'category': tool.category.value,
                'feature': tool.feature_module
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
            
            # Create agent factory with the actual tool registry object
            agent_factory = AgentFactory(
                team_id=self.team_id,
                llm=self.llm,
                tool_registry=tools_manager._tool_registry  # Pass the actual ToolRegistry object
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
        
        crew_agents = [agent.crew_agent for agent in self.agents.values()]
        
        # Create crew with LangChain Gemini LLM
        self.crew = Crew(
            agents=crew_agents,
            verbose=False,  # Set to False to reduce verbose output
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
        logger.info(f"🚨 EXECUTE_TASK CALLED: task_description='{task_description}', execution_context={execution_context}")
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
                logger.info(f"🤖 TEAM MANAGEMENT: Creating orchestration pipeline")
                try:
                    from agents.simplified_orchestration import SimplifiedOrchestrationPipeline
                    self._orchestration_pipeline = SimplifiedOrchestrationPipeline(llm=self.llm)
                    logger.info(f"🤖 ORCHESTRATION: Initialized orchestration pipeline")
                except Exception as e:
                    logger.error(f"🤖 TEAM MANAGEMENT: Failed to create orchestration pipeline: {e}", exc_info=True)
                    # Fallback to basic crew
                    logger.info(f"🤖 TEAM MANAGEMENT: Falling back to basic crew execution")
                    return await self._execute_with_basic_crew(task_description, execution_context)
            else:
                logger.info(f"🤖 TEAM MANAGEMENT: Using existing orchestration pipeline")
            
            # Enhanced logging for debugging
            is_help_command = task_description.lower().strip() == "/help"
            is_myinfo_command = task_description.lower().strip() == "/myinfo"
            
            if is_myinfo_command:
                logger.info(f"🔍 MYINFO FLOW STEP 7: About to call orchestration pipeline")
                logger.info(f"🔍 MYINFO FLOW STEP 7a: task_description='{task_description}'")
                logger.info(f"🔍 MYINFO FLOW STEP 7b: execution_context={execution_context}")
            
            # Execute task through orchestration pipeline
            logger.info(f"🤖 TEAM MANAGEMENT: Calling orchestration pipeline.execute_task")
            result = await self._orchestration_pipeline.execute_task(
                task_description=task_description,
                available_agents=self.agents,
                execution_context=execution_context
            )
            
            if is_myinfo_command:
                logger.info(f"🔍 MYINFO FLOW STEP 8: Orchestration pipeline completed")
                logger.info(f"🔍 MYINFO FLOW STEP 8a: result={result}")
            
            logger.info(f"🤖 TEAM MANAGEMENT: Task execution completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"🤖 TEAM MANAGEMENT: Error during task execution: {e}", exc_info=True)
            logger.info(f"🤖 TEAM MANAGEMENT: Falling back to basic crew execution due to error")
            return await self._execute_with_basic_crew(task_description, execution_context)
    
    async def _execute_with_basic_crew(self, task_description: str, execution_context: Dict[str, Any]) -> str:
        """
        Fallback method to execute task using basic CrewAI crew.
        This is used when the orchestration pipeline fails.
        """
        try:
            logger.info(f"🤖 BASIC CREW: Executing task with basic crew")
            logger.info(f"🤖 BASIC CREW: Task description: {task_description}")
            logger.info(f"🤖 BASIC CREW: Execution context: {execution_context}")
            
            # Use the basic crew that was created in _create_crew
            if hasattr(self, 'crew') and self.crew:
                logger.info(f"🤖 BASIC CREW: Using existing crew")
                result = await self.crew.kickoff({"name": task_description})
                logger.info(f"🤖 BASIC CREW: Task completed with result: {result}")
                return result
            else:
                logger.error(f"🤖 BASIC CREW: No crew available for fallback")
                return "❌ Sorry, I'm unable to process your request at the moment."
                
        except Exception as e:
            logger.error(f"🤖 BASIC CREW: Error in fallback execution: {e}", exc_info=True)
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
                    'crew_agent_available': agent.crew_agent is not None
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