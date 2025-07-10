#!/usr/bin/env python3
"""
LLM Factory for KICKAI System

This module provides a robust, type-safe factory for creating LLM instances.
Now uses the official LangChain Gemini integration.
"""

import logging
from dataclasses import dataclass
from core.enums import AIProvider

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM instances."""
    provider: AIProvider
    model_name: str
    api_key: str
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3

class LLMProviderError(Exception):
    """Exception raised when LLM provider operations fail."""
    pass

class LLMFactory:
    """
    Factory for creating LLM instances using the official LangChain Gemini integration.
    """
    @staticmethod
    def create_llm(config: LLMConfig):
        """
        Create a LangChain-compatible LLM instance based on the provided configuration.
        Args:
            config: LLM configuration object
        Returns:
            LangChain-compatible LLM instance
        Raises:
            LLMProviderError: If LLM creation fails
        """
        logger.info(f"Creating LLM with provider: {config.provider.value}, model: {config.model_name}")
        if config.provider != AIProvider.GOOGLE_GEMINI:
            raise LLMProviderError(f"Unsupported AI provider: {config.provider}. Only GOOGLE_GEMINI is supported.")
        try:
            import os
            from langchain_google_genai import ChatGoogleGenerativeAI
            # Set API key in environment for LangChain
            os.environ["GOOGLE_API_KEY"] = config.api_key
            # Create the LangChain Gemini LLM
            llm = ChatGoogleGenerativeAI(
                model=config.model_name,
                temperature=config.temperature,
                max_retries=config.max_retries,
                timeout=config.timeout_seconds,
            )
            logger.info("✅ LangChain Gemini LLM created successfully")
            return llm
        except ImportError:
            error_msg = "langchain-google-genai package not installed. Please install it with 'pip install langchain-google-genai'."
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
        except Exception as e:
            error_msg = f"Failed to create LangChain Gemini LLM: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg) 