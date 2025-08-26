#!/usr/bin/env python3
"""
CrewAI Context Wrapper for Parameter Injection

This module provides a CrewAI-native solution for automatically injecting
context parameters (telegram_id, team_id, username, chat_type) into tool calls.

Instead of relying on agents to explicitly pass these parameters, we wrap
tools to automatically inject context parameters from the execution context.
"""

import inspect
import functools
from typing import Any, Callable, Dict, Optional
from loguru import logger


class ContextInjectionWrapper:
    """Wrapper that automatically injects context parameters into tool calls."""
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize context wrapper with execution context.
        
        Args:
            context: Execution context containing telegram_id, team_id, username, chat_type
        """
        self.context = context
        
        # Validate required context parameters
        required_params = ['telegram_id', 'team_id', 'username', 'chat_type']
        missing_params = [param for param in required_params if not context.get(param)]
        
        if missing_params:
            raise ValueError(f"Missing required context parameters: {', '.join(missing_params)}")
            
        logger.debug(f"🔧 ContextInjectionWrapper initialized with context: {list(context.keys())}")

    def wrap_tool(self, tool_function: Callable) -> Callable:
        """
        Wrap a tool function to automatically inject context parameters.
        
        Args:
            tool_function: The tool function to wrap
            
        Returns:
            Wrapped function that injects context parameters
        """
        try:
            # Get function signature to understand parameters
            sig = inspect.signature(tool_function)
            param_names = list(sig.parameters.keys())
            
            # Check if this tool expects context parameters
            context_params = ['telegram_id', 'team_id', 'username', 'chat_type']
            expects_context = any(param in param_names for param in context_params)
            
            if not expects_context:
                # Tool doesn't need context injection, return as-is
                logger.debug(f"🔧 Tool {getattr(tool_function, '__name__', 'unknown')} doesn't need context injection")
                return tool_function
            
            @functools.wraps(tool_function)
            async def context_injected_tool(*args, **kwargs):
                """Wrapper that injects context parameters automatically."""
                try:
                    # Inject context parameters if they're not already provided
                    injected_kwargs = kwargs.copy()
                    
                    for param in context_params:
                        if param in param_names and param not in injected_kwargs:
                            if param in self.context:
                                injected_kwargs[param] = self.context[param]
                                logger.debug(f"🔧 Injected {param}={self.context[param]} into tool call")
                    
                    # Call the original function with injected parameters
                    result = await tool_function(*args, **injected_kwargs)
                    
                    logger.debug(f"✅ Context-injected tool call completed successfully")
                    return result
                    
                except Exception as e:
                    logger.error(f"❌ Context-injected tool call failed: {e}")
                    raise
            
            # Preserve tool metadata for CrewAI
            if hasattr(tool_function, 'name'):
                context_injected_tool.name = tool_function.name
            if hasattr(tool_function, 'description'):
                context_injected_tool.description = tool_function.description
            if hasattr(tool_function, 'args_schema'):
                context_injected_tool.args_schema = tool_function.args_schema
                
            logger.debug(f"✅ Wrapped tool {getattr(tool_function, '__name__', 'unknown')} with context injection")
            return context_injected_tool
            
        except Exception as e:
            logger.error(f"❌ Failed to wrap tool with context injection: {e}")
            return tool_function  # Return original if wrapping fails

    def wrap_tool_list(self, tools: list) -> list:
        """
        Wrap a list of tools with context injection.
        
        Args:
            tools: List of tool functions to wrap
            
        Returns:
            List of wrapped tools with context injection
        """
        wrapped_tools = []
        
        for tool in tools:
            try:
                wrapped_tool = self.wrap_tool(tool)
                wrapped_tools.append(wrapped_tool)
                
            except Exception as e:
                logger.error(f"❌ Failed to wrap tool {getattr(tool, '__name__', 'unknown')}: {e}")
                wrapped_tools.append(tool)  # Keep original if wrapping fails
        
        logger.info(f"🔧 Context wrapper processed {len(tools)} tools, wrapped {len(wrapped_tools)}")
        return wrapped_tools


def create_context_wrapper(execution_context: Dict[str, Any]) -> ContextInjectionWrapper:
    """
    Create a context wrapper from execution context.
    
    Args:
        execution_context: Execution context containing required parameters
        
    Returns:
        ContextInjectionWrapper configured with the provided context
    """
    return ContextInjectionWrapper(execution_context)


def apply_context_injection_to_agent_tools(agent_tools: list, execution_context: Dict[str, Any]) -> list:
    """
    Apply context injection to agent tools.
    
    This is the main function to use in the crew system to automatically
    inject context parameters into tool calls.
    
    Args:
        agent_tools: List of tools assigned to an agent
        execution_context: Execution context with required parameters
        
    Returns:
        List of context-wrapped tools
    """
    try:
        wrapper = create_context_wrapper(execution_context)
        wrapped_tools = wrapper.wrap_tool_list(agent_tools)
        
        logger.info(f"🎯 Applied context injection to {len(agent_tools)} agent tools")
        return wrapped_tools
        
    except Exception as e:
        logger.error(f"❌ Failed to apply context injection to agent tools: {e}")
        return agent_tools  # Return original tools if injection fails