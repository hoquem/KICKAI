"""
LLM Client Utility

This module provides LLM client functionality for natural language processing
in the KICKAI system.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from src.utils.llm_intent import extract_intent

logger = logging.getLogger(__name__)


async def extract_intent(message: str, context: str = "") -> Dict[str, Any]:
    """
    Async wrapper for intent extraction.
    
    Args:
        message: The input message to analyze
        context: Additional context about the conversation
    
    Returns:
        Dictionary containing 'intent' and 'entities' keys
    """
    try:
        # Run the sync function in a thread pool to make it async
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: extract_intent(message, context)
        )
        return result
    except Exception as e:
        logger.error(f"Error in async intent extraction: {e}")
        return {
            'intent': 'unknown',
            'entities': {},
            'confidence': 0.0
        }


class LLMClient:
    """LLM client for natural language processing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    async def extract_intent(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Extract intent from a message using the LLM client.
        
        Args:
            message: The input message
            context: Additional context
            
        Returns:
            Dictionary with intent and entities
        """
        return await extract_intent(message, context)
    
    async def process_message(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Process a message and return structured information.
        
        Args:
            message: The input message
            context: Additional context
            
        Returns:
            Dictionary with processing results
        """
        try:
            intent_result = await self.extract_intent(message, context)
            
            return {
                'success': True,
                'intent': intent_result.get('intent', 'unknown'),
                'entities': intent_result.get('entities', {}),
                'confidence': intent_result.get('confidence', 0.0),
                'original_message': message,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': str(e),
                'intent': 'unknown',
                'entities': {},
                'confidence': 0.0,
                'original_message': message,
                'context': context
            }


# Global LLM client instance
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


async def process_message_with_llm(message: str, context: str = "") -> Dict[str, Any]:
    """
    Process a message using the global LLM client.
    
    Args:
        message: The input message
        context: Additional context
        
    Returns:
        Dictionary with processing results
    """
    client = get_llm_client()
    return await client.process_message(message, context) 