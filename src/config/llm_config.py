#!/usr/bin/env python3
"""
LLM Configuration for KICKAI YAML-based CrewAI system.

This module provides LLM configuration and factory functions for the
YAML-based CrewAI configuration approach.
"""

import os
from typing import Optional, Any
from loguru import logger

from src.utils.llm_factory import LLMFactory, LLMConfig
from src.core.enums import AIProvider
from src.core.settings import get_settings


def get_llm_config() -> Any:
    """
    Get the LLM configuration for the YAML-based crew.
    
    Returns:
        Configured LLM instance for use with CrewAI agents
    """
    try:
        # Get settings
        settings = get_settings()
        
        # Create LLM configuration
        llm_config = LLMConfig(
            provider=settings.ai_provider,
            model_name=settings.ai_model_name,
            api_key=settings.get_ai_api_key(),
            temperature=settings.ai_temperature,
            timeout_seconds=settings.ai_timeout,
            max_retries=settings.ai_max_retries
        )
        
        # Create LLM instance
        llm = LLMFactory.create_llm(llm_config)
        
        logger.info(f"✅ LLM configured successfully: {settings.ai_provider.value} - {settings.ai_model_name}")
        return llm
        
    except Exception as e:
        logger.error(f"❌ Failed to configure LLM: {e}")
        
        # Fallback to mock LLM for development
        logger.info("🔄 Falling back to mock LLM for development")
        mock_config = LLMConfig(
            provider=AIProvider.MOCK,
            model_name="mock-model",
            api_key="mock-key",
            temperature=0.7
        )
        return LLMFactory.create_llm(mock_config)


def get_llm_config_for_agent(agent_role: str) -> Any:
    """
    Get LLM configuration for a specific agent role.
    
    Args:
        agent_role: The role of the agent
        
    Returns:
        Configured LLM instance for the agent
    """
    # For now, all agents use the same LLM configuration
    # In the future, this could be customized per agent role
    return get_llm_config()


def validate_llm_config() -> bool:
    """
    Validate that the LLM configuration is working.
    
    Returns:
        True if LLM is working, False otherwise
    """
    try:
        llm = get_llm_config()
        
        # Test the LLM with a simple prompt
        test_prompt = "Hello, this is a test message."
        response = llm.invoke([{"role": "user", "content": test_prompt}])
        
        logger.info(f"✅ LLM validation successful: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ LLM validation failed: {e}")
        return False


# Global LLM instance for reuse
_global_llm = None

def get_global_llm() -> Any:
    """
    Get a global LLM instance for reuse across the application.
    
    Returns:
        Configured LLM instance
    """
    global _global_llm
    if _global_llm is None:
        _global_llm = get_llm_config()
    return _global_llm 