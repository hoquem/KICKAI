"""
LLM Client Utility

This module provides LLM client functionality for natural language processing
in the KICKAI system.
"""

import asyncio
from typing import Any

from loguru import logger

from kickai.utils.async_utils import async_retry, async_timeout, safe_async_call
from kickai.utils.llm_factory import LLMFactory
from kickai.utils.llm_intent import extract_intent


async def extract_intent(message: str, context: str = "") -> dict[str, Any]:
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

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._llm_instance = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the LLM instance using the factory pattern."""
        try:
            # Use the new factory method that reads from environment
            self._llm_instance = LLMFactory.create_from_environment()
            logger.info(f"✅ LLM initialized successfully: {type(self._llm_instance).__name__}")

        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}. Using fallback client.")

    def _get_api_key_from_env(self) -> str | None:
        """Get API key from environment variables."""
        import os
        return os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

    async def extract_intent(self, message: str, context: str = "") -> dict[str, Any]:
        """
        Extract intent from a message using the LLM client.

        Args:
            message: The input message
            context: Additional context

        Returns:
            Dictionary with intent and entities
        """
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
            if self._llm_instance:
                # Use the actual LLM instance
                response = await safe_async_call(
                    self._llm_instance.ainvoke,
                    prompt,
                    default_value=None
                )
                if response:
                    return response.content if hasattr(response, 'content') else str(response)

            # Fallback to simple response if LLM is not available
            return f"Generated response for: {prompt[:50]}..."

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Sorry, I couldn't generate a response: {e!s}"

    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """
        Generate a response using the LLM client (alias for generate_text).

        Args:
            prompt: The input prompt
            context: Additional context

        Returns:
            Generated response
        """
        return await self.generate_text(prompt, context)

    @async_retry(max_attempts=3, delay=1.0)
    @async_timeout(30.0)
    async def analyze_text(self, text: str, analysis_type: str) -> dict[str, Any]:
        """
        Analyze text for specific purposes.

        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform

        Returns:
            Analysis results
        """
        try:
            if self._llm_instance:
                # Create analysis prompt based on type
                analysis_prompt = self._create_analysis_prompt(text, analysis_type)
                response = await safe_async_call(
                    self._llm_instance.ainvoke,
                    analysis_prompt,
                    default_value=None
                )
                if response:
                    return {
                        'analysis_type': analysis_type,
                        'result': response.content if hasattr(response, 'content') else str(response),
                        'success': True
                    }

            # Fallback analysis
            return {
                'analysis_type': analysis_type,
                'result': f"Basic analysis of: {text[:50]}...",
                'success': True
            }

        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                'analysis_type': analysis_type,
                'result': f"Analysis failed: {e!s}",
                'success': False,
                'error': str(e)
            }

    def _create_analysis_prompt(self, text: str, analysis_type: str) -> str:
        """Create a prompt for text analysis."""
        prompts = {
            'sentiment': f"Analyze the sentiment of this text: {text}",
            'intent': f"Extract the intent from this text: {text}",
            'entities': f"Extract named entities from this text: {text}",
            'summary': f"Summarize this text: {text}",
            'classification': f"Classify this text: {text}"
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


async def process_message_with_llm(message: str, context: str = "") -> dict[str, Any]:
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
