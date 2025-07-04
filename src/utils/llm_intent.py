"""
LLM Intent Extraction Module

This module provides intent extraction using the new LLM client abstraction layer.
It maintains backward compatibility while leveraging the new architecture.
"""

import asyncio
import logging
from typing import Dict, Any
from .llm_client import extract_intent as extract_intent_async, IntentResult

logger = logging.getLogger(__name__)


def extract_intent(message: str, context: str = "") -> Dict[str, Any]:
    """
    Use an LLM to extract intent and entities from a player's message.
    Returns a dict with 'intent' and 'entities'.
    
    This function maintains backward compatibility while using the new LLM abstraction.
    """
    try:
        # Try to run the async version
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, create a task but return immediately
            # This is not ideal but maintains backward compatibility
            asyncio.create_task(_extract_intent_async(message, context))
            return {"intent": "unknown", "entities": {}, "error": "Async context detected"}
        else:
            # Run the async version synchronously
            result = loop.run_until_complete(extract_intent_async(message, context))
            return {
                "intent": result.intent,
                "entities": result.entities,
                "error": result.error
            }
    except Exception as e:
        logger.error(f"Intent extraction failed: {e}")
        return {"intent": "unknown", "entities": {}, "error": str(e)}


async def _extract_intent_async(message: str, context: str = "") -> IntentResult:
    """
    Internal async function for intent extraction.
    """
    return await extract_intent_async(message, context)


# For backward compatibility - keep the old function name
extract_intent_sync = extract_intent 