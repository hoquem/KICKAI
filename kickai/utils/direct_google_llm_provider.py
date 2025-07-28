#!/usr/bin/env python3
"""
Direct Google LLM Provider
Uses google.generativeai directly instead of LiteLLM
"""
import os
from typing import Dict, List

import asyncio
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DirectGoogleLLMConfig:
    """Configuration for Direct Google LLM."""

    api_key: str
    model_name: str = os.getenv("GOOGLE_MODEL_NAME", "gemini-1.5-flash")
    temperature: float = float(os.getenv("GOOGLE_TEMPERATURE", "0.7"))
    timeout_seconds: int = int(os.getenv("GOOGLE_TIMEOUT_SECONDS", "30"))
    max_retries: int = int(os.getenv("GOOGLE_MAX_RETRIES", "3"))


class DirectGoogleLLM:
    """Direct Google LLM using google.generativeai."""

    def __init__(self, config: DirectGoogleLLMConfig):
        self.config = config
        self._model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the Google Generative AI model."""
        try:
            import google.generativeai as genai

            # Configure the API
            genai.configure(api_key=self.config.api_key)

            # Create the model
            self._model = genai.GenerativeModel(self.config.model_name)

            logger.info(f"✅ Direct Google LLM initialized: {self.config.model_name}")

        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Direct Google LLM: {e}")
            raise

    def _format_messages_for_google(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for Google Generative AI."""
        formatted_content = ""

        for message in messages:
            if isinstance(message, dict):
                role = message.get("role", "user")
                content = message.get("content", "")

                if role == "system":
                    formatted_content += f"System: {content}\n\n"
                elif role == "user":
                    formatted_content += f"User: {content}\n\n"
                elif role == "assistant":
                    formatted_content += f"Assistant: {content}\n\n"
            else:
                # Fallback: treat as user message
                formatted_content += f"User: {message!s}\n\n"

        return formatted_content.strip()

    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Synchronous invocation."""
        start_time = asyncio.get_event_loop().time() * 1000

        try:
            # Format messages for Google API
            formatted_content = self._format_messages_for_google(messages)

            # Generate content
            response = self._model.generate_content(
                formatted_content,
                generation_config={"temperature": self.config.temperature, **kwargs},
            )

            duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
            logger.info(f"[DIRECT GOOGLE LLM] Request completed in {duration_ms:.2f}ms")

            return response.text

        except Exception as e:
            duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
            logger.error(f"[DIRECT GOOGLE LLM] Request failed after {duration_ms:.2f}ms")
            logger.error(f"[DIRECT GOOGLE LLM] Error: {e}")
            raise

    async def ainvoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Asynchronous invocation (runs synchronously)."""
        return self.invoke(messages, **kwargs)

    def __call__(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call interface for compatibility."""
        return self.invoke(messages, **kwargs)

    def is_available(self) -> bool:
        """Check if the LLM is available."""
        return self._model is not None


class DirectGoogleLLMProvider:
    """Provider for Direct Google LLM."""

    def create_llm(self, config: DirectGoogleLLMConfig) -> DirectGoogleLLM:
        """Create a Direct Google LLM instance."""
        return DirectGoogleLLM(config)


def create_direct_google_llm(
    api_key: str,
    model_name: str = None,
    temperature: float = None,
    timeout_seconds: int = None,
    max_retries: int = None,
) -> DirectGoogleLLM:
    """Factory function to create a Direct Google LLM instance."""
    config = DirectGoogleLLMConfig(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
    )

    provider = DirectGoogleLLMProvider()
    return provider.create_llm(config)
