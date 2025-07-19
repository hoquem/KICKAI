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

# Import the correct AIProvider enum from core.enums
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


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing and development."""
    
    def validate_config(self, config: LLMConfig) -> bool:
        """Validate mock configuration."""
        # Mock provider doesn't require any specific configuration
        return True
    
    def create_llm(self, config: LLMConfig):
        """Create a mock LLM instance."""
        self.validate_config(config)
        
        class MockLLM:
            """Mock LLM for testing and development."""
            
            def __init__(self, model_name: str, temperature: float = 0.7):
                self.model_name = model_name
                self.temperature = temperature
                logger.info(f"✅ Mock LLM created (model: {model_name}, temperature: {temperature})")
            
            def invoke(self, messages, **kwargs):
                """Mock synchronous invocation."""
                logger.info(f"[MOCK LLM] Invoke called with {len(messages)} messages")
                return "Mock LLM response: This is a test response from the mock LLM."
            
            async def ainvoke(self, messages, **kwargs):
                """Mock asynchronous invocation."""
                logger.info(f"[MOCK LLM] Async invoke called with {len(messages)} messages")
                return "Mock LLM response: This is a test response from the mock LLM."
            
            def __call__(self, messages, **kwargs):
                """Call interface for compatibility."""
                return self.invoke(messages, **kwargs)
            
            def is_available(self) -> bool:
                """Check if the LLM is available (always True for mock)."""
                return True
        
        llm = MockLLM(
            model_name=config.model_name,
            temperature=config.temperature
        )
        
        logger.info(f"✅ Mock LLM created successfully (model: {config.model_name})")
        return llm


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
            # Set environment variable for the API key
            os.environ["GOOGLE_API_KEY"] = config.api_key
            
            # Clear any Vertex AI related environment variables
            self._clear_vertex_ai_environment()
            
            # Import LiteLLM for CrewAI compatibility
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
                
                def _clear_vertex_ai_environment(self):
                    """Clear Vertex AI environment variables to avoid conflicts."""
                    vertex_vars = [
                        'GOOGLE_APPLICATION_CREDENTIALS',
                        'GOOGLE_CLOUD_PROJECT',
                        'VERTEX_AI_PROJECT',
                        'VERTEX_AI_LOCATION'
                    ]
                    for var in vertex_vars:
                        if var in os.environ:
                            del os.environ[var]
                            logger.info(f"[LLM INIT] Cleared {var} environment variable")
                
                def invoke(self, messages, **kwargs):
                    """Synchronous invocation with comprehensive error handling."""
                    start_time = asyncio.get_event_loop().time() * 1000
                    
                    try:
                        # Convert messages to LiteLLM format
                        formatted_messages = self._format_messages_for_litellm(messages)
                        
                        # Call LiteLLM with explicit API key
                        response = completion(
                            model=self.model_name,
                            messages=formatted_messages,
                            temperature=self.temperature,
                            timeout=self.timeout,
                            max_retries=self.max_retries,
                            api_key=self.api_key,
                            **kwargs
                        )
                        
                        duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
                        logger.info(f"[LLM SUCCESS] Request completed in {duration_ms:.2f}ms")
                        
                        # Extract content from response
                        if hasattr(response, 'choices') and response.choices:
                            content = response.choices[0].message.content
                            return content
                        else:
                            return str(response)
                            
                    except Exception as e:
                        duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
                        self._handle_litellm_error(e, duration_ms, messages, **kwargs)
                
                async def ainvoke(self, messages, **kwargs):
                    """Asynchronous invocation with comprehensive error handling."""
                    start_time = asyncio.get_event_loop().time() * 1000
                    
                    try:
                        # Convert messages to LiteLLM format
                        formatted_messages = self._format_messages_for_litellm(messages)
                        
                        # Call LiteLLM synchronously (LiteLLM completion is not async)
                        response = completion(
                            model=self.model_name,
                            messages=formatted_messages,
                            temperature=self.temperature,
                            timeout=self.timeout,
                            max_retries=self.max_retries,
                            api_key=self.api_key,
                            **kwargs
                        )
                        
                        duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
                        logger.info(f"[LLM SUCCESS] Async request completed in {duration_ms:.2f}ms")
                        
                        # Extract content from response
                        if hasattr(response, 'choices') and response.choices:
                            content = response.choices[0].message.content
                            return content
                        else:
                            return str(response)
                            
                    except Exception as e:
                        duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
                        self._handle_litellm_error(e, duration_ms, messages, **kwargs)
                
                def __call__(self, messages, **kwargs):
                    """Call interface for compatibility."""
                    return self.invoke(messages, **kwargs)
                
                def is_available(self) -> bool:
                    """Check if the LLM is available."""
                    return True
                
                def _format_messages_for_litellm(self, messages):
                    """Format messages for LiteLLM compatibility."""
                    formatted_messages = []
                    for message in messages:
                        if hasattr(message, 'content') and hasattr(message, 'role'):
                            formatted_messages.append({
                                'role': message.role,
                                'content': message.content
                            })
                        elif isinstance(message, dict):
                            formatted_messages.append(message)
                        else:
                            # Fallback: treat as user message
                            formatted_messages.append({
                                'role': 'user',
                                'content': str(message)
                            })
                    return formatted_messages
                
                def _handle_litellm_error(self, error, duration_ms, messages, **kwargs):
                    """Handle LiteLLM errors with detailed logging."""
                    logger.error(f"[LLM ERROR] Request failed after {duration_ms:.2f}ms")
                    logger.error(f"[LLM ERROR] Error type: {type(error).__name__}")
                    logger.error(f"[LLM ERROR] Error message: {str(error)}")
                    logger.error(f"[LLM ERROR] Model: {self.model_name}")
                    logger.error(f"[LLM ERROR] Temperature: {self.temperature}")
                    logger.error(f"[LLM ERROR] Timeout: {self.timeout}s")
                    logger.error(f"[LLM ERROR] Max retries: {self.max_retries}")
                    logger.error(f"[LLM ERROR] Messages count: {len(messages)}")
                    
                    # Log first message for debugging
                    if messages:
                        first_msg = messages[0]
                        logger.error(f"[LLM ERROR] First message: {str(first_msg)[:200]}...")
                    
                    # Log additional parameters
                    if kwargs:
                        logger.error(f"[LLM ERROR] Additional parameters: {kwargs}")
                    
                    # Log full traceback for debugging
                    logger.error(f"[LLM ERROR] Full traceback:")
                    logger.error(traceback.format_exc())
                    
                    # Log diagnostics
                    logger.error(f"[LLM DIAGNOSTICS] - API Key present: {bool(self.api_key)}")
                    logger.error(f"[LLM DIAGNOSTICS] - API Key length: {len(self.api_key) if self.api_key else 0}")
                    logger.error(f"[LLM DIAGNOSTICS] - Request duration: {duration_ms:.2f}ms")
                    
                    # Re-raise the error
                    raise error

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
            error_msg = "LiteLLM package not installed. Please install it with 'pip install litellm'."
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
        except Exception as e:
            error_msg = f"Failed to create Google Gemini LLM: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
    
    def _clear_vertex_ai_environment(self):
        """Clear Vertex AI environment variables to avoid conflicts."""
        vertex_vars = [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'GOOGLE_CLOUD_PROJECT',
            'VERTEX_AI_PROJECT',
            'VERTEX_AI_LOCATION'
        ]
        for var in vertex_vars:
            if var in os.environ:
                del os.environ[var]
                logger.info(f"[LLM INIT] Cleared {var} environment variable")


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
            # For now, return a mock LLM for Ollama since we're focusing on CrewAI
            # This can be expanded later when we need Ollama support
            class MockOllamaLLM:
                def __init__(self, model_name: str, temperature: float = 0.7):
                    self.model_name = model_name
                    self.temperature = temperature
                    logger.info(f"✅ Mock Ollama LLM created (model: {model_name}, temperature: {temperature})")
                
                def invoke(self, messages, **kwargs):
                    """Mock synchronous invocation."""
                    logger.info(f"[MOCK OLLAMA] Invoke called with {len(messages)} messages")
                    return "Mock Ollama response: This is a test response from the mock Ollama LLM."
                
                async def ainvoke(self, messages, **kwargs):
                    """Mock asynchronous invocation."""
                    logger.info(f"[MOCK OLLAMA] Async invoke called with {len(messages)} messages")
                    return "Mock Ollama response: This is a test response from the mock Ollama LLM."
                
                def __call__(self, messages, **kwargs):
                    """Call interface for compatibility."""
                    return self.invoke(messages, **kwargs)
                
                def is_available(self) -> bool:
                    """Check if the LLM is available (always True for mock)."""
                    return True
            
            llm = MockOllamaLLM(
                model_name=config.model_name,
                temperature=config.temperature
            )
            logger.info(f"✅ Mock Ollama LLM created successfully (model: {config.model_name})")
            return llm
            
        except ImportError:
            error_msg = "Ollama package not installed. Please install it with 'pip install ollama'."
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
        AIProvider.GEMINI: GoogleGeminiProvider,
        AIProvider.OLLAMA: OllamaProvider,
        AIProvider.MOCK: MockLLMProvider,
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
        provider_str = os.getenv('AI_PROVIDER', 'gemini')
        logger.debug(f"🔍 [DEBUG] LLMFactory: AI_PROVIDER from env: {provider_str}")
        
        try:
            provider = AIProvider(provider_str)
            logger.debug(f"🔍 [DEBUG] LLMFactory: Selected provider: {provider.value}")
        except ValueError:
            raise LLMProviderError(f"Invalid AI_PROVIDER: {provider_str}")
        
        # Get API key from environment (only for real providers)
        api_key = ""
        if provider == AIProvider.GEMINI:
            api_key = os.getenv('GOOGLE_API_KEY', '')
        elif provider == AIProvider.MOCK:
            api_key = "mock-key"  # Mock doesn't need real API key
        
        # Use default model if not specified
        if not model_name:
            # Try AI_MODEL_NAME first, then provider-specific fallbacks
            model_name = os.getenv('AI_MODEL_NAME')
            logger.debug(f"🔍 [DEBUG] LLMFactory: AI_MODEL_NAME from env: {model_name}")
            
        if not model_name:
            if provider == AIProvider.GEMINI:
                model_name = os.getenv('GOOGLE_AI_MODEL_NAME', 'gemini-1.5-flash')
                logger.debug(f"🔍 [DEBUG] LLMFactory: GOOGLE_AI_MODEL_NAME from env: {model_name}")
            elif provider == AIProvider.OLLAMA:
                model_name = os.getenv('OLLAMA_MODEL', 'llama2')
                logger.debug(f"🔍 [DEBUG] LLMFactory: OLLAMA_MODEL from env: {model_name}")
            elif provider == AIProvider.MOCK:
                model_name = os.getenv('MOCK_MODEL', 'mock-model')
                logger.debug(f"🔍 [DEBUG] LLMFactory: MOCK_MODEL from env: {model_name}")
        
        logger.debug(f"🔍 [DEBUG] LLMFactory: Final model_name: {model_name}")
        
        config = LLMConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            timeout_seconds=int(os.getenv('LLM_TIMEOUT', '30')),
            max_retries=int(os.getenv('LLM_MAX_RETRIES', '3')),
        )
        
        return cls.create_llm(config)
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported AI providers."""
        return [provider.value for provider in cls._providers.keys()] 