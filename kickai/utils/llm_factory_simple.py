"""
Simple LLM Factory for KICKAI

This module provides a simple, clean LLM factory that uses the new configuration system.
"""

import asyncio
import logging
import time
from typing import Any, Optional

from kickai.core.config import get_settings, AIProvider

logger = logging.getLogger(__name__)


class RateLimitedLLMFactory:
    """Rate-limited LLM factory with retry logic for rate limit errors."""
    
    @staticmethod
    def create_llm(model_name: Optional[str] = None, temperature: Optional[float] = None) -> Any:
        """
        Create a rate-limited LLM instance using the current configuration.
        
        Args:
            model_name: Optional model name override
            temperature: Optional temperature override
            
        Returns:
            LangChain-compatible LLM instance with rate limiting
        """
        settings = get_settings()
        
        # Use provided values or defaults from settings
        final_model_name = model_name or settings.ai_model_name
        final_temperature = temperature or settings.ai_temperature
        
        logger.info(f"🔧 Creating rate-limited LLM with provider: {settings.ai_provider.value}, model: {final_model_name}")
        
        try:
            if settings.ai_provider == AIProvider.GROQ:
                return RateLimitedLLMFactory._create_groq_llm(settings, final_model_name, final_temperature)
            elif settings.ai_provider == AIProvider.GEMINI:
                return RateLimitedLLMFactory._create_gemini_llm(settings, final_model_name, final_temperature)
            elif settings.ai_provider == AIProvider.OPENAI:
                return RateLimitedLLMFactory._create_openai_llm(settings, final_model_name, final_temperature)
            elif settings.ai_provider == AIProvider.OLLAMA:
                return RateLimitedLLMFactory._create_ollama_llm(settings, final_model_name, final_temperature)
            else:
                raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create rate-limited LLM: {e}")
            raise RuntimeError(f"Failed to create rate-limited LLM with provider {settings.ai_provider}: {e}")
    
    @staticmethod
    def _create_groq_llm(settings, model_name: str, temperature: float) -> Any:
        """Create a rate-limited Groq LLM instance."""
        from litellm import completion
        
        # Format model name for Groq
        formatted_model = f"groq/{model_name}"
        
        logger.info(f"🤖 Creating rate-limited Groq LLM: {formatted_model}")
        
        def groq_llm_with_retry(messages, **kwargs):
            max_retries = settings.ai_rate_limit_max_retries
            base_delay = settings.ai_rate_limit_retry_delay
            backoff_multiplier = settings.ai_rate_limit_backoff_multiplier
            
            for attempt in range(max_retries + 1):
                try:
                    response = completion(
                        model=formatted_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=settings.ai_max_tokens,
                        timeout=settings.ai_timeout,
                        api_key=settings.groq_api_key,
                        **kwargs
                    )
                    
                    if hasattr(response, "choices") and response.choices:
                        return response.choices[0].message.content
                    else:
                        return str(response)
                        
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Check if it's a rate limit error
                    if "rate limit" in error_str or "rate_limit" in error_str or "tpm" in error_str:
                        if attempt < max_retries:
                            delay = base_delay * (backoff_multiplier ** attempt)
                            logger.warning(f"⚠️ Groq rate limit hit (attempt {attempt + 1}/{max_retries + 1}). Waiting {delay:.1f}s...")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"❌ Groq rate limit exceeded after {max_retries + 1} attempts")
                            raise RuntimeError(f"Groq rate limit exceeded after {max_retries + 1} attempts: {e}")
                    else:
                        # Non-rate-limit error, don't retry
                        logger.error(f"❌ Groq LLM request failed (non-rate-limit): {e}")
                        raise RuntimeError(f"Groq LLM request failed: {e}")
        
        # Create a simple callable object
        class RateLimitedGroqLLM:
            def invoke(self, messages, **kwargs):
                return groq_llm_with_retry(messages, **kwargs)
            
            def ainvoke(self, messages, **kwargs):
                return groq_llm_with_retry(messages, **kwargs)
            
            def __call__(self, messages, **kwargs):
                return groq_llm_with_retry(messages, **kwargs)
        
        return RateLimitedGroqLLM()
        
        return llm
    
    @staticmethod
    def _create_gemini_llm(settings, model_name: str, temperature: float) -> Any:
        """Create a Gemini LLM instance."""
        from litellm import completion
        
        logger.info(f"🤖 Creating Gemini LLM: {model_name}")
        
        def gemini_llm(messages, **kwargs):
            try:
                response = completion(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=settings.ai_max_tokens,
                    timeout=settings.ai_timeout,
                    api_key=settings.gemini_api_key,
                    **kwargs
                )
                
                if hasattr(response, "choices") and response.choices:
                    return response.choices[0].message.content
                else:
                    return str(response)
                    
            except Exception as e:
                logger.error(f"❌ Gemini LLM request failed: {e}")
                raise RuntimeError(f"Gemini LLM request failed: {e}")
        
        # Create a simple callable object
        llm = type('GeminiLLM', (), {
            'invoke': gemini_llm,
            'ainvoke': lambda messages, **kwargs: gemini_llm(messages, **kwargs),
            '__call__': gemini_llm
        })()
        
        return llm
    
    @staticmethod
    def _create_openai_llm(settings, model_name: str, temperature: float) -> Any:
        """Create an OpenAI LLM instance."""
        from litellm import completion
        
        logger.info(f"🤖 Creating OpenAI LLM: {model_name}")
        
        def openai_llm(messages, **kwargs):
            try:
                response = completion(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=settings.ai_max_tokens,
                    timeout=settings.ai_timeout,
                    api_key=settings.openai_api_key,
                    **kwargs
                )
                
                if hasattr(response, "choices") and response.choices:
                    return response.choices[0].message.content
                else:
                    return str(response)
                    
            except Exception as e:
                logger.error(f"❌ OpenAI LLM request failed: {e}")
                raise RuntimeError(f"OpenAI LLM request failed: {e}")
        
        # Create a simple callable object
        llm = type('OpenAILLM', (), {
            'invoke': openai_llm,
            'ainvoke': lambda messages, **kwargs: openai_llm(messages, **kwargs),
            '__call__': openai_llm
        })()
        
        return llm
    
    @staticmethod
    def _create_ollama_llm(settings, model_name: str, temperature: float) -> Any:
        """Create an Ollama LLM instance."""
        from litellm import completion
        
        logger.info(f"🤖 Creating Ollama LLM: {model_name}")
        
        def ollama_llm(messages, **kwargs):
            try:
                response = completion(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=settings.ai_max_tokens,
                    timeout=settings.ai_timeout,
                    api_base=settings.ollama_base_url,
                    **kwargs
                )
                
                if hasattr(response, "choices") and response.choices:
                    return response.choices[0].message.content
                else:
                    return str(response)
                    
            except Exception as e:
                logger.error(f"❌ Ollama LLM request failed: {e}")
                raise RuntimeError(f"Ollama LLM request failed: {e}")
        
        # Create a simple callable object
        llm = type('OllamaLLM', (), {
            'invoke': ollama_llm,
            'ainvoke': lambda messages, **kwargs: ollama_llm(messages, **kwargs),
            '__call__': ollama_llm
        })()
        
        return llm


# Backward compatibility - SimpleLLMFactory now uses rate limiting
SimpleLLMFactory = RateLimitedLLMFactory
