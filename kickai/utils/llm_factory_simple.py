"""
Simple LLM Factory for KICKAI


This module provides a simple, clean LLM factory for creating LangChain-compatible LLM instances.
"""

import logging

from typing import Any, Optional

from kickai.core.config import get_settings
from kickai.core.enums import AIProvider

logger = logging.getLogger(__name__)


class SimpleLLMFactory:
    """Simple LLM factory for creating LangChain-compatible LLM instances."""

    
    @staticmethod
    def create_llm(model_name: Optional[str] = None, temperature: Optional[float] = None) -> Any:
        """
        Create an LLM instance using the current configuration.

        
        Args:
            model_name: Optional model name override
            temperature: Optional temperature override
            
        Returns:
            LangChain-compatible LLM instance

        """
        settings = get_settings()
        
        # Use provided values or defaults from settings
        final_model_name = model_name or settings.ai_model_simple or settings.ai_model_advanced or settings.ai_model_name or "gemini-1.5-flash"
        final_temperature = temperature or settings.ai_temperature
        
        logger.info(f"🔧 Creating LLM with provider: {settings.ai_provider.value}, model: {final_model_name}")
        
        try:
            if settings.ai_provider == AIProvider.GROQ:
                return SimpleLLMFactory._create_groq_llm(settings, final_model_name, final_temperature)
            elif settings.ai_provider == AIProvider.GOOGLE_GEMINI:
                return SimpleLLMFactory._create_gemini_llm(settings, final_model_name, final_temperature)
            elif settings.ai_provider == AIProvider.OPENAI:
                return SimpleLLMFactory._create_openai_llm(settings, final_model_name, final_temperature)
            elif settings.ai_provider == AIProvider.OLLAMA:
                return SimpleLLMFactory._create_ollama_llm(settings, final_model_name, final_temperature)

            else:
                raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create LLM: {e}")
            raise e

    @staticmethod
    def _create_groq_llm(settings, model_name: str, temperature: float) -> Any:
        """Create Groq LLM instance."""
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            raise ImportError("langchain_groq is required for Groq provider")

        return ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=settings.groq_api_key,
            timeout=settings.ai_timeout,
        )

    @staticmethod
    def _create_gemini_llm(settings, model_name: str, temperature: float) -> Any:
        """Create Gemini LLM instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError("langchain_google_genai is required for Gemini provider")

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=settings.gemini_api_key,
            timeout=settings.ai_timeout,
        )

    @staticmethod
    def _create_openai_llm(settings, model_name: str, temperature: float) -> Any:
        """Create OpenAI LLM instance."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain_openai is required for OpenAI provider")

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.openai_api_key,
            timeout=settings.ai_timeout,
        )

    @staticmethod
    def _create_ollama_llm(settings, model_name: str, temperature: float) -> Any:
        """Create Ollama LLM instance."""
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError("langchain_ollama is required for Ollama provider")

        return ChatOllama(
            model=model_name,
            temperature=temperature,
            base_url=settings.ollama_base_url,
            timeout=settings.ai_timeout,
        )


# Backward compatibility
RateLimitedLLMFactory = SimpleLLMFactory

