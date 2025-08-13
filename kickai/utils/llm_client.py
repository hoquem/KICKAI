"""
LLM Client Utility

This module provides LLM client functionality for natural language processing
in the KICKAI system.
"""

import asyncio
from typing import Any, Dict, Optional

from loguru import logger

from kickai.utils.async_utils import async_retry, async_timeout, safe_async_call
from kickai.utils.llm_factory import LLMFactory
from kickai.utils.llm_intent import LLMIntentRecognizer


async def extract_intent(message: str, context: str = "") -> dict[str, Any]:
    """
    Async wrapper for LLM-based intent extraction.

    Args:
        message: The input message to analyze
        context: Additional context about the conversation

    Returns:
        Dictionary containing 'intent' and 'entities' keys
    """
    try:
        # Use the new LLM-based intent recognizer
        recognizer = LLMIntentRecognizer()
        context_dict = {"context": context} if context else {}
        
        result = await recognizer.extract_intent(message, context_dict)
        
        return {
            "intent": result.intent,
            "entities": result.entities,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }
    except Exception as e:
        logger.error(f"Error in async intent extraction: {e}")
        return {"intent": "unknown", "entities": {}, "confidence": 0.0, "reasoning": f"Error: {str(e)}"}


class LLMClient:
    """LLM client for natural language processing."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._llm_instance = None
        self._intent_recognizer = None
        self._initialize_components()

    def _initialize_components(self):
        """Initialize the LLM instance and intent recognizer."""
        try:
            # Use the new factory method that reads from environment
            self._llm_instance = LLMFactory.create_from_settings()
            logger.info(f"✅ LLM initialized successfully: {type(self._llm_instance).__name__}")

            # Initialize the intent recognizer
            self._intent_recognizer = LLMIntentRecognizer()
            logger.info("✅ LLMIntentRecognizer initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize LLM components: {e}. Using fallback client.")

    async def extract_intent(self, message: str, context: str = "") -> dict[str, Any]:
        """
        Extract intent from a message using the LLM-based intent recognizer.

        Args:
            message: The input message
            context: Additional context

        Returns:
            Dictionary with intent, entities, confidence, and reasoning
        """
        if self._intent_recognizer:
            context_dict = {"context": context} if context else {}
            result = await self._intent_recognizer.extract_intent(message, context_dict)
            
            return {
                "intent": result.intent,
                "entities": result.entities,
                "confidence": result.confidence,
                "reasoning": result.reasoning
            }
        else:
            # Fallback to the async wrapper
            return await extract_intent(message, context)

    async def process_message(self, message: str, context: str = "") -> dict[str, Any]:
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
                "success": True,
                "intent": intent_result.get("intent", "unknown"),
                "entities": intent_result.get("entities", {}),
                "confidence": intent_result.get("confidence", 0.0),
                "reasoning": intent_result.get("reasoning", ""),
                "original_message": message,
                "context": context,
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "original_message": message,
                "context": context,
            }

    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def generate_text(self, prompt: str, context: str = "") -> str:
        """
        Generate text using the LLM client with retry and timeout.

        Args:
            prompt: The input prompt
            context: Additional context

        Returns:
            Generated text response
        """
        try:
            if not self._llm_instance:
                raise RuntimeError("LLM instance not initialized")

            # Add context to prompt if provided
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nPrompt: {prompt}"

            # Generate response using the LLM instance
            response = await safe_async_call(
                self._llm_instance.generate_text,
                full_prompt,
                timeout=30.0
            )

            return response if response else "No response generated"

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    async def analyze_text(self, text: str, analysis_type: str = "intent") -> dict[str, Any]:
        """
        Analyze text using the LLM client.

        Args:
            text: The text to analyze
            analysis_type: Type of analysis (intent, entities, summary, classification)

        Returns:
            Dictionary with analysis results
        """
        try:
            prompt = self._create_analysis_prompt(text, analysis_type)
            result = await self.generate_text(prompt)

            return {
                "success": True,
                "analysis_type": analysis_type,
                "result": result,
                "original_text": text
            }

        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type,
                "original_text": text
            }

    def _create_analysis_prompt(self, text: str, analysis_type: str) -> str:
        """Create analysis prompt based on type."""
        prompts = {
            "intent": f"Extract the intent from this text: {text}",
            "entities": f"Extract named entities from this text: {text}",
            "summary": f"Summarize this text: {text}",
            "classification": f"Classify this text: {text}",
        }
        return prompts.get(analysis_type, f"Analyze this text for {analysis_type}: {text}")


# Global LLM client instance
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


async def get_async_llm_client() -> LLMClient:
    """Get the global LLM client instance (async version)."""
    return get_llm_client()
