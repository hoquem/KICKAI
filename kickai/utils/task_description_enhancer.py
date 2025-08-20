#!/usr/bin/env python3
"""
Task Description Enhancer

This module provides a centralized utility for enhancing task descriptions
with consistent context parameter passing across the KICKAI system.
"""

from typing import Dict, Any
from loguru import logger


class TaskDescriptionEnhancer:
    """
    Centralized utility for enhancing task descriptions with consistent context parameters.
    
    This ensures all tools receive the same standard context parameters:
    - telegram_id
    - team_id
    - username
    - chat_type
    """

    @staticmethod
    def enhance_task_description(task_description: str, execution_context: Dict[str, Any]) -> str:
        """
        Enhance task description with standard context parameters.
        
        Args:
            task_description: Original task description
            execution_context: Execution context with user information
            
        Returns:
            Enhanced task description with context information
        """
        try:
            # Extract standard context parameters
            telegram_id = execution_context.get('telegram_id')
            team_id = execution_context.get('team_id')
            username = execution_context.get('username')
            chat_type = execution_context.get('chat_type')
            
            # Validate required parameters
            if not all([telegram_id, team_id, username, chat_type]):
                missing_params = []
                if not telegram_id:
                    missing_params.append('telegram_id')
                if not team_id:
                    missing_params.append('team_id')
                if not username:
                    missing_params.append('username')
                if not chat_type:
                    missing_params.append('chat_type')
                
                logger.warning(f"⚠️ Missing context parameters: {missing_params}")
                return task_description
            
            # Create standardized context information
            context_info = f"""
Context Information:
- User ID: {telegram_id}
- Team ID: {team_id}
- Username: {username}
- Chat Type: {chat_type}

Task: {task_description}

IMPORTANT: All tools should receive these context parameters automatically:
- telegram_id: {telegram_id}
- team_id: {team_id}
- username: {username}
- chat_type: {chat_type}

Instructions:
1. Use the context parameters above when calling any tools
2. All tools expect these standard parameters in the specified order
3. Pass the context parameters as the first arguments to tools
4. Ensure consistent parameter passing across all tool calls
"""
            
            return context_info.strip()
            
        except Exception as e:
            logger.error(f"❌ Error enhancing task description: {e}")
            return task_description

    @staticmethod
    def create_simple_context_info(execution_context: Dict[str, Any]) -> str:
        """
        Create simple context information string for basic task descriptions.
        
        Args:
            execution_context: Execution context with user information
            
        Returns:
            Simple context information string
        """
        try:
            telegram_id = execution_context.get('telegram_id')
            team_id = execution_context.get('team_id')
            username = execution_context.get('username')
            chat_type = execution_context.get('chat_type')
            
            return f"Context: team_id='{team_id}', telegram_id={telegram_id}, chat_type='{chat_type}', username='{username}'"
            
        except Exception as e:
            logger.error(f"❌ Error creating simple context info: {e}")
            return "Context: unavailable"

    @staticmethod
    def validate_context_parameters(execution_context: Dict[str, Any]) -> bool:
        """
        Validate that execution context contains all required parameters.
        
        Args:
            execution_context: Execution context to validate
            
        Returns:
            True if all required parameters are present, False otherwise
        """
        required_params = ['telegram_id', 'team_id', 'username', 'chat_type']
        
        for param in required_params:
            if not execution_context.get(param):
                logger.warning(f"⚠️ Missing required context parameter: {param}")
                return False
        
        return True
