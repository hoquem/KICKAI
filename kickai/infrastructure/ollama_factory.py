"""
Ollama Client Factory

This module provides a factory function to create Ollama client instances
with proper configuration and error handling.
"""

import logging
from typing import Optional
import asyncio

from kickai.core.settings import Settings
from kickai.infrastructure.ollama_client import OllamaClient, OllamaConfig

logger = logging.getLogger(__name__)

# Global client instance for singleton pattern
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client(settings: Settings) -> OllamaClient:
    """
    Get or create an Ollama client instance.
    
    This function implements a singleton pattern to ensure only one
    Ollama client instance is created and reused.
    
    Args:
        settings: Application settings containing Ollama configuration
        
    Returns:
        OllamaClient: Configured Ollama client instance
        
    Raises:
        ValueError: If Ollama configuration is invalid
    """
    global _ollama_client
    
    if _ollama_client is None:
        try:
            # Create Ollama configuration from settings
            config = OllamaConfig(
                base_url=settings.ollama_base_url,
                connection_timeout=30.0,
                request_timeout=120.0,
                retry_attempts=3,
                retry_min_wait=1.0,
                retry_max_wait=10.0,
                circuit_breaker_failure_threshold=5,
                circuit_breaker_recovery_timeout=60.0,
                circuit_breaker_half_open_max_calls=3
            )
            
            # Create the client
            _ollama_client = OllamaClient(config)
            
            logger.info(f"✅ Ollama client created successfully: base_url={settings.ollama_base_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create Ollama client: {e}")
            raise ValueError(f"Invalid Ollama configuration: {e}")
    
    return _ollama_client


def reset_ollama_client():
    """
    Reset the global Ollama client instance.
    
    This is useful for testing or when you need to recreate the client
    with different configuration.
    """
    global _ollama_client
    
    if _ollama_client is not None:
        try:
            # Close the existing client if it's still open
            asyncio.create_task(_ollama_client.close())
        except Exception as e:
            logger.warning(f"Warning: Failed to close existing Ollama client: {e}")
    
    _ollama_client = None
    logger.info("🔄 Ollama client reset")


def is_ollama_client_initialized() -> bool:
    """
    Check if the Ollama client has been initialized.
    
    Returns:
        bool: True if client is initialized, False otherwise
    """
    return _ollama_client is not None 