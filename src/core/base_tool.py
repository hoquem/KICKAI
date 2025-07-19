"""
Base tool class for CrewAI compatibility.
This inherits from CrewAI BaseTool and follows CrewAI guidelines exactly.
"""

from abc import abstractmethod
from typing import Any, Dict, Optional
from crewai.tools import BaseTool as CrewAITool
from loguru import logger
import json
import re


class BaseTool(CrewAITool):
    """Base class for all tools used with CrewAI agents."""
    
    def __init__(self, name: str, description: str, **kwargs):
        super().__init__(name=name, description=description, **kwargs)
    
    def _run(self, *args, **kwargs) -> Any:
        """
        Execute the tool with the given parameters.
        This method handles CrewAI's parameter passing format.
        """
        # Debug logging
        logger.info(f"[DEBUG] BaseTool {self.name} _run called with args: {args}, kwargs: {kwargs}")
        
        # Parse parameters from CrewAI's format
        parsed_kwargs = self._parse_crewai_parameters(args, kwargs)
        
        # Call the actual implementation
        return self._execute_tool(parsed_kwargs)
    
    def _parse_crewai_parameters(self, args, kwargs) -> Dict[str, Any]:
        """
        Parse parameters from CrewAI's format.
        CrewAI might pass parameters as:
        1. A single JSON string in args[0]
        2. Individual kwargs
        3. A combination of both
        """
        parsed_kwargs = {}
        
        # First, copy any existing kwargs
        parsed_kwargs.update(kwargs)
        
        # Check if there's a JSON string in args
        if args and len(args) > 0:
            first_arg = args[0]
            if isinstance(first_arg, str):
                try:
                    # Try to parse as JSON
                    json_data = json.loads(first_arg)
                    if isinstance(json_data, dict):
                        parsed_kwargs.update(json_data)
                        logger.info(f"[DEBUG] BaseTool {self.name} parsed JSON: {json_data}")
                except json.JSONDecodeError:
                    # Not JSON, might be a single parameter
                    logger.info(f"[DEBUG] BaseTool {self.name} first arg is not JSON: {first_arg}")
        
        # Extract context from task description if present
        context = self._extract_context_from_task(parsed_kwargs)
        if context:
            parsed_kwargs.update(context)
            logger.info(f"[DEBUG] BaseTool {self.name} extracted context: {context}")
        
        logger.info(f"[DEBUG] BaseTool {self.name} final parsed kwargs: {parsed_kwargs}")
        return parsed_kwargs
    
    def _extract_context_from_task(self, kwargs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract context from task description or kwargs."""
        # Check if context is already in kwargs
        if 'context' in kwargs:
            return kwargs['context']
        
        # Check if context parameters are already in kwargs
        context_params = {}
        if 'team_id' in kwargs:
            context_params['team_id'] = kwargs['team_id']
        if 'user_id' in kwargs:
            context_params['user_id'] = kwargs['user_id']
        if 'is_leadership_chat' in kwargs:
            context_params['is_leadership_chat'] = kwargs['is_leadership_chat']
        
        if context_params:
            return context_params
        
        return None
    
    @abstractmethod
    def _execute_tool(self, kwargs: Dict[str, Any]) -> Any:
        """Execute the tool with the given parameters."""
        pass
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        return self._run(**kwargs)
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>" 