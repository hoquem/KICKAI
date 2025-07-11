#!/usr/bin/env python3
"""
LLM Factory for KICKAI System

This module provides a factory pattern for creating LLM instances
with support for multiple AI providers and robust error handling.
"""

import os
import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Type, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers."""
    GOOGLE_GEMINI = "google_gemini"
    OLLAMA = "ollama"


@dataclass
class LLMConfig:
    """Configuration for LLM instances."""
    provider: AIProvider
    model_name: str
    api_key: str
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3
    api_base: Optional[str] = None
    additional_params: Optional[Dict] = None


class LLMProviderError(Exception):
    """Exception raised for LLM provider errors."""
    pass


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def create_llm(self, config: LLMConfig):
        """Create an LLM instance."""
        pass
    
    @abstractmethod
    def validate_config(self, config: LLMConfig) -> bool:
        """Validate the configuration."""
        pass


class GoogleGeminiProvider(LLMProvider):
    """Google Gemini LLM provider using direct API with robust error handling."""
    
    def validate_config(self, config: LLMConfig) -> bool:
        """Validate Gemini configuration."""
        if not config.api_key:
            raise LLMProviderError("Google Gemini requires GOOGLE_API_KEY")
        if not config.model_name:
            raise LLMProviderError("Google Gemini requires model_name")
        return True
    
    def create_llm(self, config: LLMConfig):
        """Create a Google Gemini LLM instance with comprehensive error handling."""
        self.validate_config(config)
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            # Set environment variable for the API key
            os.environ["GOOGLE_API_KEY"] = config.api_key
            
            # Clear any Vertex AI related environment variables
            self._clear_vertex_ai_environment()
            
            # Create the LangChain Gemini LLM
            from litellm import completion
            
            # LiteLLM expects model in 'provider/model_name' format
            litellm_model_name = f"gemini/{config.model_name}"
            
            # Create a robust LLM wrapper with comprehensive error handling
            class RobustLiteLLMChatModel:
                def __init__(self, model_name, api_key, temperature, timeout, max_retries):
                    self.model_name = model_name
                    self.api_key = api_key
                    self.temperature = temperature
                    self.timeout = timeout
                    self.max_retries = max_retries
                    self.client = None
                    
                    # Log initialization
                    logger.info(f"[LLM INIT] Initializing RobustLiteLLMChatModel")
                    logger.info(f"[LLM INIT] Model: {model_name}")
                    logger.info(f"[LLM INIT] API Key: {api_key[:10]}..." if api_key else "None")
                    logger.info(f"[LLM INIT] Temperature: {temperature}")
                    logger.info(f"[LLM INIT] Timeout: {timeout}s")
                    logger.info(f"[LLM INIT] Max Retries: {max_retries}")

                async def agenerate(self, messages, **kwargs):
                    """Generate response with comprehensive error handling."""
                    start_time = asyncio.get_event_loop().time()
                    
                    # Log the request
                    logger.info(f"[LLM REQUEST] Starting LiteLLM completion request")
                    logger.info(f"[LLM REQUEST] Model: {self.model_name}")
                    logger.info(f"[LLM REQUEST] Messages count: {len(messages)}")
                    logger.info(f"[LLM REQUEST] First message preview: {str(messages[0])[:100]}..." if messages else "No messages")
                    
                    try:
                        # Convert LangChain messages to litellm format
                        litellm_messages = []
                        for msg in messages:
                            if hasattr(msg, 'type') and msg.type == 'human':
                                litellm_messages.append({"role": "user", "content": msg.content})
                            elif hasattr(msg, 'type') and msg.type == 'ai':
                                litellm_messages.append({"role": "assistant", "content": msg.content})
                            else:
                                litellm_messages.append({"role": "user", "content": str(msg)})
                        
                        logger.info(f"[LLM REQUEST] Converted to LiteLLM format: {len(litellm_messages)} messages")
                        
                        # Make the LiteLLM API call with comprehensive error handling
                        response = await self._make_litellm_request(litellm_messages, **kwargs)
                        
                        # Convert litellm response back to LangChain format
                        from langchain_core.messages import AIMessage
                        result = AIMessage(content=response.choices[0].message.content)
                        
                        # Log success
                        duration = (asyncio.get_event_loop().time() - start_time) * 1000
                        logger.info(f"[LLM SUCCESS] LiteLLM request completed successfully in {duration:.2f}ms")
                        logger.info(f"[LLM SUCCESS] Response length: {len(result.content)} characters")
                        logger.info(f"[LLM SUCCESS] Response preview: {result.content[:100]}...")
                        
                        return result
                        
                    except Exception as e:
                        # Comprehensive error handling
                        duration = (asyncio.get_event_loop().time() - start_time) * 1000
                        await self._handle_litellm_error(e, duration, messages, **kwargs)
                        raise

                def generate(self, messages, **kwargs):
                    """Synchronous wrapper for agenerate."""
                    return asyncio.run(self.agenerate(messages, **kwargs))
                
                async def _make_litellm_request(self, litellm_messages, **kwargs):
                    """Make the actual LiteLLM API request with retry logic."""
                    from litellm import completion
                    
                    # Prepare request parameters
                    request_params = {
                        "model": self.model_name,
                        "messages": litellm_messages,
                        "api_key": self.api_key,
                        "temperature": self.temperature,
                        "request_timeout": self.timeout,
                        "num_retries": self.max_retries,
                        **kwargs
                    }
                    
                    logger.info(f"[LLM API] Making LiteLLM completion request")
                    logger.info(f"[LLM API] Request params: {list(request_params.keys())}")
                    
                    # Make the request - LiteLLM completion is sync, not async
                    response = completion(**request_params)
                    
                    # Validate response
                    if not response or not hasattr(response, 'choices') or not response.choices:
                        raise LLMProviderError("LiteLLM returned empty or invalid response")
                    
                    if not response.choices[0] or not hasattr(response.choices[0], 'message'):
                        raise LLMProviderError("LiteLLM response missing message content")
                    
                    return response
                
                async def _handle_litellm_error(self, error, duration_ms, messages, **kwargs):
                    """Handle LiteLLM errors with detailed logging and diagnostics."""
                    error_type = type(error).__name__
                    error_msg = str(error)
                    
                    # Create detailed error context
                    error_context = {
                        "error_type": error_type,
                        "error_message": error_msg,
                        "model": self.model_name,
                        "api_key_present": bool(self.api_key),
                        "api_key_preview": self.api_key[:10] + "..." if self.api_key else "None",
                        "temperature": self.temperature,
                        "timeout": self.timeout,
                        "max_retries": self.max_retries,
                        "duration_ms": duration_ms,
                        "messages_count": len(messages),
                        "request_kwargs": list(kwargs.keys())
                    }
                    
                    # Categorize and log errors appropriately
                    if "API key" in error_msg.lower() or "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                        logger.critical(f"[LLM ERROR] 🔑 API KEY ERROR: {error_msg}")
                        logger.critical(f"[LLM ERROR] 🔑 This is likely an invalid or expired GOOGLE_API_KEY")
                        logger.critical(f"[LLM ERROR] 🔑 Please check your .env file and ensure GOOGLE_API_KEY is correct")
                        logger.critical(f"[LLM ERROR] 🔑 Error context: {error_context}")
                        
                    elif "503" in error_msg or "service unavailable" in error_msg.lower():
                        logger.error(f"[LLM ERROR] 🚫 SERVICE UNAVAILABLE (503): {error_msg}")
                        logger.error(f"[LLM ERROR] 🚫 Google Gemini API is temporarily unavailable")
                        logger.error(f"[LLM ERROR] 🚫 This is a Google service issue, not a configuration problem")
                        logger.error(f"[LLM ERROR] 🚫 Error context: {error_context}")
                        
                    elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                        logger.error(f"[LLM ERROR] ⏰ TIMEOUT ERROR: {error_msg}")
                        logger.error(f"[LLM ERROR] ⏰ Request timed out after {duration_ms:.2f}ms")
                        logger.error(f"[LLM ERROR] ⏰ Consider increasing timeout or checking network connectivity")
                        logger.error(f"[LLM ERROR] ⏰ Error context: {error_context}")
                        
                    elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                        logger.error(f"[LLM ERROR] 📊 QUOTA/RATE LIMIT ERROR: {error_msg}")
                        logger.error(f"[LLM ERROR] 📊 Google Gemini API quota exceeded or rate limited")
                        logger.error(f"[LLM ERROR] 📊 Check your Google Cloud Console for quota usage")
                        logger.error(f"[LLM ERROR] 📊 Error context: {error_context}")
                        
                    elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                        logger.error(f"[LLM ERROR] 🤖 MODEL NOT FOUND: {error_msg}")
                        logger.error(f"[LLM ERROR] 🤖 Model '{self.model_name}' may not exist or be accessible")
                        logger.error(f"[LLM ERROR] 🤖 Check your AI_MODEL_NAME environment variable")
                        logger.error(f"[LLM ERROR] 🤖 Error context: {error_context}")
                        
                    elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                        logger.error(f"[LLM ERROR] 🌐 NETWORK ERROR: {error_msg}")
                        logger.error(f"[LLM ERROR] 🌐 Network connectivity issue or DNS problem")
                        logger.error(f"[LLM ERROR] 🌐 Check your internet connection and firewall settings")
                        logger.error(f"[LLM ERROR] 🌐 Error context: {error_context}")
                        
                    else:
                        # Generic error handling
                        logger.error(f"[LLM ERROR] ❌ UNKNOWN ERROR: {error_msg}")
                        logger.error(f"[LLM ERROR] ❌ Error type: {error_type}")
                        logger.error(f"[LLM ERROR] ❌ Full error context: {error_context}")
                        logger.error(f"[LLM ERROR] ❌ Full traceback: {traceback.format_exc()}")
                    
                    # Additional diagnostics
                    logger.info(f"[LLM DIAGNOSTICS] Environment check:")
                    logger.info(f"[LLM DIAGNOSTICS] - GOOGLE_API_KEY present: {bool(os.getenv('GOOGLE_API_KEY'))}")
                    logger.info(f"[LLM DIAGNOSTICS] - AI_PROVIDER: {os.getenv('AI_PROVIDER', 'not set')}")
                    logger.info(f"[LLM DIAGNOSTICS] - AI_MODEL_NAME: {os.getenv('AI_MODEL_NAME', 'not set')}")
                    logger.info(f"[LLM DIAGNOSTICS] - Request duration: {duration_ms:.2f}ms")

            llm = RobustLiteLLMChatModel(
                model_name=litellm_model_name,
                api_key=config.api_key,
                temperature=config.temperature,
                timeout=config.timeout_seconds,
                max_retries=config.max_retries,
            )
            
            logger.info(f"✅ Google Gemini LLM created successfully using LiteLLM (model: {litellm_model_name})")
            return llm
            
        except ImportError:
            error_msg = "langchain-google-genai package not installed. Please install it with 'pip install langchain-google-genai'."
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
        except Exception as e:
            error_msg = f"Failed to create Google Gemini LLM: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
    
    def _clear_vertex_ai_environment(self):
        """Clear any Vertex AI related environment variables."""
        vertex_vars = [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'GOOGLE_CLOUD_PROJECT', 
            'GOOGLE_CLOUD_LOCATION',
            'GOOGLE_GENAI_USE_VERTEXAI'
        ]
        
        for var in vertex_vars:
            if var in os.environ:
                logger.warning(f"⚠️  Found {var} environment variable. Clearing to prevent Vertex AI routing.")
                del os.environ[var]
        
        # Clear any Google Cloud service account related variables
        for key in list(os.environ.keys()):
            if any(term in key.upper() for term in ['VERTEX', 'AIPLATFORM', 'GOOGLE_CLOUD']):
                if key != 'GOOGLE_API_KEY':  # Keep the direct API key
                    logger.info(f"Clearing potential Vertex AI variable: {key}")
                    del os.environ[key]

class OllamaProvider(LLMProvider):
    """Ollama LLM provider for local models."""
    
    def validate_config(self, config: LLMConfig) -> bool:
        """Validate Ollama configuration."""
        if not config.model_name:
            raise LLMProviderError("Ollama requires model_name")
        return True
    
    def create_llm(self, config: LLMConfig):
        """Create an Ollama LLM instance."""
        self.validate_config(config)
        
        try:
            from langchain_ollama import OllamaLLM
            
            # Create the Ollama LLM with CrewAI-compatible configuration
            llm = OllamaLLM(
                model=config.model_name,
                temperature=config.temperature,
                timeout=config.timeout_seconds,
                # Add additional parameters for better CrewAI compatibility
                stop=None,
                repeat_penalty=1.1,
                top_k=10,
                top_p=0.9,
            )
            logger.info(f"✅ Ollama LLM created successfully (model: {config.model_name})")
            return llm
            
        except ImportError:
            error_msg = "langchain-community package not installed. Please install it with 'pip install langchain-community'."
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
        except Exception as e:
            error_msg = f"Failed to create Ollama LLM: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg)

class LLMFactory:
    """
    Factory for creating LLM instances.
    Supports multiple AI providers with proper factory pattern.
    """
    
    _providers: Dict[AIProvider, Type[LLMProvider]] = {
        AIProvider.GOOGLE_GEMINI: GoogleGeminiProvider,
        AIProvider.OLLAMA: OllamaProvider,
    }
    
    @classmethod
    def register_provider(cls, provider: AIProvider, provider_class: Type[LLMProvider]):
        """Register a new LLM provider."""
        cls._providers[provider] = provider_class
        logger.info(f"Registered LLM provider: {provider.value}")
    
    @classmethod
    def get_provider(cls, provider: AIProvider) -> LLMProvider:
        """Get the provider instance for the given AI provider."""
        if provider not in cls._providers:
            raise LLMProviderError(f"Unsupported AI provider: {provider.value}")
        
        provider_class = cls._providers[provider]
        return provider_class()
    
    @classmethod
    def create_llm(cls, config: LLMConfig):
        """
        Create an LLM instance based on the provided configuration.
        
        Args:
            config: LLM configuration object
        Returns:
            LangChain-compatible LLM instance
        Raises:
            LLMProviderError: If LLM creation fails
        """
        logger.info(f"Creating LLM with provider: {config.provider.value}, model: {config.model_name}")
        
        provider = cls.get_provider(config.provider)
        return provider.create_llm(config)
    
    @classmethod
    def create_from_environment(cls, model_name: Optional[str] = None) -> 'Any':
        """
        Create an LLM instance from environment variables.
        
        Args:
            model_name: Optional model name override
        Returns:
            LangChain-compatible LLM instance
        """
        # Get provider from environment
        provider_str = os.getenv('AI_PROVIDER', 'google_gemini')
        logger.info(f"🔍 [DEBUG] LLMFactory: AI_PROVIDER from env: {provider_str}")
        
        try:
            provider = AIProvider(provider_str)
            logger.info(f"🔍 [DEBUG] LLMFactory: Selected provider: {provider.value}")
        except ValueError:
            raise LLMProviderError(f"Invalid AI_PROVIDER: {provider_str}")
        
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY') if provider == AIProvider.GOOGLE_GEMINI else None
        
        # Use default model if not specified
        if not model_name:
            # Try AI_MODEL_NAME first, then provider-specific fallbacks
            model_name = os.getenv('AI_MODEL_NAME')
            logger.info(f"🔍 [DEBUG] LLMFactory: AI_MODEL_NAME from env: {model_name}")
            
        if not model_name:
            if provider == AIProvider.GOOGLE_GEMINI:
                model_name = os.getenv('GOOGLE_AI_MODEL_NAME', 'gemini-1.5-flash')
                logger.info(f"🔍 [DEBUG] LLMFactory: GOOGLE_AI_MODEL_NAME from env: {model_name}")
            else:
                model_name = os.getenv('OLLAMA_MODEL', 'llama2')
                logger.info(f"🔍 [DEBUG] LLMFactory: OLLAMA_MODEL from env: {model_name}")
        
        logger.info(f"🔍 [DEBUG] LLMFactory: Final model_name: {model_name}")
        
        config = LLMConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key or "",
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            timeout_seconds=int(os.getenv('LLM_TIMEOUT', '30')),
            max_retries=int(os.getenv('LLM_MAX_RETRIES', '3')),
        )
        
        return cls.create_llm(config)
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported AI providers."""
        return [provider.value for provider in cls._providers.keys()] 