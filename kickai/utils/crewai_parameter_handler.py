#!/usr/bin/env python3
"""
CrewAI Parameter Handler - Unified Parameter Extraction for KICKAI Tools

This module provides robust, standardized parameter handling for CrewAI tools,
addressing the framework's flexible parameter passing patterns while maintaining
clean, maintainable code.

Key Features:
- Handles both dictionary and individual parameter passing
- Type validation and conversion
- Required parameter checking
- CrewAI best practice compliance
- Performance optimized
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from loguru import logger

from kickai.utils.tool_helpers import create_json_response
from kickai.core.enums import ResponseStatus


class CrewAIParameterExtractor:
    """
    Unified parameter extraction utility for CrewAI tools.
    
    Handles the complexities of CrewAI's flexible parameter passing while
    providing a clean, standardized interface for tools.
    """
    
    # Standard KICKAI context parameters
    STANDARD_CONTEXT_PARAMS = ['telegram_id', 'team_id', 'username', 'chat_type']
    
    @classmethod
    def extract_parameters(
        cls, 
        *args, 
        required_params: Optional[List[str]] = None,
        optional_params: Optional[List[str]] = None,
        **kwargs
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Extract and validate parameters from CrewAI tool calls.
        
        Args:
            *args: Positional arguments from CrewAI
            required_params: List of required parameter names
            optional_params: List of optional parameter names
            **kwargs: Keyword arguments from CrewAI
            
        Returns:
            Tuple of (extracted_params_dict, error_message)
            If error_message is not None, extraction failed
        """
        try:
            # Default to standard context parameters if not specified
            if required_params is None:
                required_params = cls.STANDARD_CONTEXT_PARAMS.copy()
            if optional_params is None:
                optional_params = []
            
            all_params = required_params + optional_params
            extracted = {}
            
            # Case 1: Dictionary passed as first positional argument (common in CrewAI)
            if args and isinstance(args[0], dict):
                param_dict = args[0]
                logger.debug(f"🔧 Extracting from dictionary parameter: {list(param_dict.keys())}")
                logger.debug(f"🔧 Looking for parameters: {all_params}")
                
                # Extract each parameter
                for param in all_params:
                    if param in param_dict:
                        extracted[param] = param_dict[param]
                        logger.debug(f"🔧 Found parameter {param}: {param_dict[param]}")
                    else:
                        logger.debug(f"🔧 Missing parameter {param} in dictionary")
                
                # Handle additional positional args if present
                if len(args) > 1:
                    logger.debug(f"🔧 Additional positional args found: {len(args) - 1}")
                    
            # Case 2: Individual parameters via kwargs
            elif kwargs:
                logger.debug(f"🔧 Extracting from keyword arguments: {list(kwargs.keys())}")
                for param in all_params:
                    if param in kwargs:
                        extracted[param] = kwargs[param]
                        
            # Case 3: Individual parameters via positional args (legacy)
            elif args and len(args) >= len(required_params):
                logger.debug(f"🔧 Extracting from positional arguments: {len(args)} args")
                for i, param in enumerate(required_params):
                    if i < len(args):
                        extracted[param] = args[i]
                        
            # Handle special case: intent_data as dictionary
            if 'intent_data' in extracted and isinstance(extracted['intent_data'], dict):
                intent_dict = extracted['intent_data']
                logger.debug(f"🔧 Found intent_data as dictionary: {intent_dict}")
                if 'message' in intent_dict:
                    extracted['intent_data'] = intent_dict['message']
                    logger.debug(f"🔧 Extracted message from intent_data dictionary: {intent_dict['message']}")
                else:
                    extracted['intent_data'] = str(intent_dict)
                    logger.debug(f"🔧 Converted intent_data dictionary to string: {str(intent_dict)}")
            
            # Type conversion and validation
            validation_error = cls._validate_and_convert_parameters(extracted, required_params)
            if validation_error:
                return {}, validation_error
                
            # Check for missing required parameters
            missing_params = [param for param in required_params if param not in extracted or extracted[param] is None]
            logger.debug(f"🔧 Extracted parameters: {list(extracted.keys())}")
            logger.debug(f"🔧 Required parameters: {required_params}")
            logger.debug(f"🔧 Missing parameters: {missing_params}")
            if missing_params:
                error_msg = f"Missing required parameters: {', '.join(missing_params)}"
                logger.warning(f"⚠️ Parameter validation failed: {error_msg}")
                return {}, create_json_response(ResponseStatus.ERROR, message=error_msg)
            
            logger.debug(f"✅ Parameter extraction successful: {list(extracted.keys())}")
            return extracted, None
            
        except Exception as e:
            error_msg = f"Parameter extraction failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {}, create_json_response(ResponseStatus.ERROR, message=error_msg)
    
    @classmethod
    def _validate_and_convert_parameters(
        cls, 
        params: Dict[str, Any], 
        required_params: List[str]
    ) -> Optional[str]:
        """
        Validate and convert parameters to expected types.
        
        Args:
            params: Extracted parameters dictionary
            required_params: List of required parameter names
            
        Returns:
            Error message if validation fails, None if successful
        """
        try:
            # Type conversion for telegram_id (must be int)
            if 'telegram_id' in params and params['telegram_id'] is not None:
                if isinstance(params['telegram_id'], str):
                    try:
                        params['telegram_id'] = int(params['telegram_id'])
                    except (ValueError, TypeError):
                        return create_json_response(
                            ResponseStatus.ERROR,
                            message="telegram_id must be a valid integer"
                        )
                elif not isinstance(params['telegram_id'], int):
                    return create_json_response(
                        ResponseStatus.ERROR,
                        message="telegram_id must be an integer"
                    )
                    
                # Validate telegram_id is positive
                if params['telegram_id'] <= 0:
                    return create_json_response(
                        ResponseStatus.ERROR,
                        message="telegram_id must be a positive integer"
                    )
            
            # Validate string parameters
            string_params = ['team_id', 'username', 'chat_type']
            for param in string_params:
                if param in params and params[param] is not None:
                    if not isinstance(params[param], str):
                        params[param] = str(params[param])
                    if not params[param].strip():
                        return create_json_response(
                            ResponseStatus.ERROR,
                            message=f"{param} cannot be empty"
                        )
            
            # Ensure intent_data is a string if present
            if 'intent_data' in params and params['intent_data'] is not None:
                if not isinstance(params['intent_data'], str):
                    params['intent_data'] = str(params['intent_data'])
            
            return None
            
        except Exception as e:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Parameter validation error: {str(e)}"
            )


def extract_crewai_parameters(
    *args, 
    required: Optional[List[str]] = None,
    optional: Optional[List[str]] = None,
    **kwargs
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Convenience function for parameter extraction.
    
    Args:
        *args: Positional arguments from CrewAI
        required: List of required parameter names
        optional: List of optional parameter names  
        **kwargs: Keyword arguments from CrewAI
        
    Returns:
        Tuple of (extracted_params_dict, error_message)
    """
    return CrewAIParameterExtractor.extract_parameters(
        *args, 
        required_params=required,
        optional_params=optional,
        **kwargs
    )


def validate_required_context(
    params: Dict[str, Any], 
    required_keys: List[str]
) -> Optional[str]:
    """
    Validate that all required context parameters are present and valid.
    
    Args:
        params: Parameter dictionary to validate
        required_keys: List of required parameter names
        
    Returns:
        Error message if validation fails, None if successful
    """
    try:
        missing_keys = []
        invalid_keys = []
        
        for key in required_keys:
            if key not in params:
                missing_keys.append(key)
            elif params[key] is None:
                invalid_keys.append(f"{key} is None")
            elif isinstance(params[key], str) and not params[key].strip():
                invalid_keys.append(f"{key} is empty")
        
        if missing_keys:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Missing required parameters: {', '.join(missing_keys)}"
            )
            
        if invalid_keys:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"Invalid parameters: {', '.join(invalid_keys)}"
            )
        
        return None
        
    except Exception as e:
        return create_json_response(
            ResponseStatus.ERROR,
            message=f"Context validation error: {str(e)}"
        )


# Decorator for automatic parameter extraction
def crewai_tool_params(required: Optional[List[str]] = None, optional: Optional[List[str]] = None):
    """
    Decorator to automatically extract and validate CrewAI tool parameters.
    
    Args:
        required: List of required parameter names
        optional: List of optional parameter names
        
    Usage:
        @tool("my_tool")
        @crewai_tool_params(required=['telegram_id', 'team_id'])
        async def my_tool(*args, **kwargs):
            params = kwargs.get('_extracted_params')
            # Use params dictionary with validated parameters
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract parameters
            params, error = extract_crewai_parameters(*args, required=required, optional=optional, **kwargs)
            
            if error:
                return error
                
            # Inject extracted parameters into kwargs
            kwargs['_extracted_params'] = params
            
            # Call original function
            return await func(*args, **kwargs)
            
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__annotations__ = func.__annotations__
        
        return wrapper
    return decorator