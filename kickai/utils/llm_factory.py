#!/usr/bin/env python3
"""
LLM Factory for KICKAI System

This module provides a factory pattern for creating LLM instances
with support for multiple AI providers and robust error handling.
"""

import asyncio
import logging
import os
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# Import the correct AIProvider enum from kickai.core.enums
from kickai.core.enums import AIProvider

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
    api_base: str | None = None
    additional_params: dict | None = None

    def __post_init__(self):
        """Validate temperature range."""
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {self.temperature}")

    @classmethod
    def create_for_agent_type(
        cls, provider: AIProvider, model_name: str, api_key: str, agent_type: str = None
    ) -> "LLMConfig":
        """Create LLM config with agent-specific temperature settings."""
        # Use lower temperature for data-critical agents to prevent hallucination
        if agent_type in [
            "player_coordinator",
            "help_assistant",
            "message_processor",
            "finance_manager",
        ]:
            temperature = 0.1  # Very low temperature for precise, factual responses
        elif agent_type in ["team_manager", "availability_manager"]:
            temperature = 0.3  # Low temperature for administrative tasks
        elif agent_type in ["onboarding_agent"]:
            temperature = 0.2  # Very low temperature for registration guidance
        else:
            temperature = 0.7  # Default temperature for creative tasks

        # Handle case where provider might be None
        if provider is None:
            # Try to get provider from environment as fallback
            import os

            provider_str = os.getenv("AI_PROVIDER", "gemini")
            try:
                provider = AIProvider(provider_str)
            except ValueError:
                provider = AIProvider.GEMINI  # Default fallback

        return cls(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            timeout_seconds=30,
            max_retries=3,
        )


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

                # CrewAI compatibility attributes
                self.supports_functions = False
                self.supports_tools = False
                self.stop = None  # Add missing stop attribute

                logger.info(
                    f"✅ Mock LLM created (model: {model_name}, temperature: {temperature})"
                )

            def supports_stop_words(self) -> bool:
                """CrewAI compatibility method."""
                return False

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

        llm = MockLLM(model_name=config.model_name, temperature=config.temperature)

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

                    # CrewAI compatibility attributes
                    self.supports_functions = False
                    self.supports_tools = False
                    self.stop = None  # Add missing stop attribute

                    # Log initialization
                    logger.info("[LLM INIT] Initializing RobustLiteLLMChatModel")
                    logger.info(f"[LLM INIT] Model: {model_name}")
                    logger.info(f"[LLM INIT] API Key: {api_key[:10]}..." if api_key else "None")
                    logger.info(f"[LLM INIT] Temperature: {temperature}")
                    logger.info(f"[LLM INIT] Timeout: {timeout}s")
                    logger.info(f"[LLM INIT] Max retries: {max_retries}")

                def supports_stop_words(self) -> bool:
                    """CrewAI compatibility method."""
                    return False

                def _clear_vertex_ai_environment(self):
                    """Clear Vertex AI environment variables to avoid conflicts."""
                    vertex_vars = [
                        "GOOGLE_APPLICATION_CREDENTIALS",
                        "GOOGLE_CLOUD_PROJECT",
                        "VERTEX_AI_PROJECT",
                        "VERTEX_AI_LOCATION",
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
                            **kwargs,
                        )

                        duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
                        logger.info(f"[LLM SUCCESS] Request completed in {duration_ms:.2f}ms")

                        # Extract content from response
                        if hasattr(response, "choices") and response.choices:
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
                            **kwargs,
                        )

                        duration_ms = (asyncio.get_event_loop().time() * 1000) - start_time
                        logger.info(f"[LLM SUCCESS] Async request completed in {duration_ms:.2f}ms")

                        # Extract content from response
                        if hasattr(response, "choices") and response.choices:
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
                        if hasattr(message, "content") and hasattr(message, "role"):
                            formatted_messages.append(
                                {"role": message.role, "content": message.content}
                            )
                        elif isinstance(message, dict):
                            formatted_messages.append(message)
                        else:
                            # Fallback: treat as user message
                            formatted_messages.append({"role": "user", "content": str(message)})
                    return formatted_messages

                def _handle_litellm_error(self, error, duration_ms, messages, **kwargs):
                    """Handle LiteLLM errors with detailed logging."""
                    logger.error(f"[LLM ERROR] Request failed after {duration_ms:.2f}ms")
                    logger.error(f"[LLM ERROR] Error type: {type(error).__name__}")
                    logger.error(f"[LLM ERROR] Error message: {error!s}")
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
                    logger.error("[LLM ERROR] Full traceback:")
                    logger.error(traceback.format_exc())

                    # Log diagnostics
                    logger.error(f"[LLM DIAGNOSTICS] - API Key present: {bool(self.api_key)}")
                    logger.error(
                        f"[LLM DIAGNOSTICS] - API Key length: {len(self.api_key) if self.api_key else 0}"
                    )
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

            logger.info(
                f"✅ Google Gemini LLM created successfully using LiteLLM (model: {litellm_model_name})"
            )
            return llm

        except ImportError:
            error_msg = (
                "LiteLLM package not installed. Please install it with 'pip install litellm'."
            )
            logger.error(error_msg)
            raise LLMProviderError(error_msg)
        except Exception as e:
            error_msg = f"Failed to create Google Gemini LLM: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg)

    def _clear_vertex_ai_environment(self):
        """Clear Vertex AI environment variables to avoid conflicts."""
        vertex_vars = [
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_CLOUD_PROJECT",
            "VERTEX_AI_PROJECT",
            "VERTEX_AI_LOCATION",
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
            # Import LiteLLM for Ollama integration
            from litellm import completion

            # LiteLLM expects model in 'ollama/model_name' format for Ollama
            if not config.model_name.startswith("ollama/"):
                litellm_model_name = f"ollama/{config.model_name}"
            else:
                litellm_model_name = config.model_name

            # Get Ollama base URL from config or environment
            ollama_base_url = config.api_base or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

            # Create a robust Ollama LLM wrapper
            class RobustOllamaLLM:
                def __init__(self, model_name, base_url, temperature, timeout, max_retries):
                    self.model_name = model_name
                    self.base_url = base_url
                    self.temperature = temperature
                    self.timeout = timeout
                    self.max_retries = max_retries

                    # CrewAI compatibility attributes
                    self.supports_functions = False
                    self.supports_tools = False
                    self.stop = None

                    logger.info(f"✅ Ollama LLM created (model: {model_name}, base_url: {base_url})")

                def supports_stop_words(self) -> bool:
                    """CrewAI compatibility method."""
                    return False

                def invoke(self, messages, **kwargs):
                    """Synchronous invocation with Ollama."""
                    try:
                        # Convert messages to LiteLLM format
                        formatted_messages = self._format_messages_for_litellm(messages)

                        # Call LiteLLM with Ollama
                        response = completion(
                            model=self.model_name,
                            messages=formatted_messages,
                            temperature=self.temperature,
                            timeout=self.timeout,
                            max_retries=self.max_retries,
                            api_base=self.base_url,
                            **kwargs,
                        )

                        # Extract content from response
                        if hasattr(response, "choices") and response.choices:
                            content = response.choices[0].message.content
                            return content
                        else:
                            return str(response)

                    except Exception as e:
                        logger.error(f"[OLLAMA ERROR] Request failed: {e}")
                        # Fallback to mock response for testing
                        return "Ollama LLM response (fallback): Processing your request..."

                async def ainvoke(self, messages, **kwargs):
                    """Asynchronous invocation."""
                    return self.invoke(messages, **kwargs)

                def __call__(self, messages, **kwargs):
                    """Call interface for compatibility."""
                    return self.invoke(messages, **kwargs)

                def is_available(self) -> bool:
                    """Check if Ollama is available."""
                    try:
                        import requests
                        response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                        return response.status_code == 200
                    except:
                        return False

                def _format_messages_for_litellm(self, messages):
                    """Format messages for LiteLLM compatibility."""
                    formatted_messages = []
                    for message in messages:
                        if hasattr(message, "content") and hasattr(message, "role"):
                            formatted_messages.append(
                                {"role": message.role, "content": message.content}
                            )
                        elif isinstance(message, dict):
                            formatted_messages.append(message)
                        else:
                            # Fallback: treat as user message
                            formatted_messages.append({"role": "user", "content": str(message)})
                    return formatted_messages

            llm = RobustOllamaLLM(
                model_name=litellm_model_name,
                base_url=ollama_base_url,
                temperature=config.temperature,
                timeout=config.timeout_seconds,
                max_retries=config.max_retries,
            )

            logger.info(f"✅ Ollama LLM created successfully (model: {litellm_model_name})")
            return llm

        except ImportError:
            logger.warning("LiteLLM not available, creating mock Ollama LLM for testing")
            # Fallback to mock LLM if LiteLLM is not available
            class MockOllamaLLM:
                def __init__(self, model_name: str, temperature: float = 0.7):
                    self.model_name = model_name
                    self.temperature = temperature

                    # CrewAI compatibility attributes
                    self.supports_functions = False
                    self.supports_tools = False
                    self.stop = None  # Add missing stop attribute

                    logger.info(
                        f"✅ Mock Ollama LLM created (model: {model_name}, temperature: {temperature})"
                    )

                def supports_stop_words(self) -> bool:
                    """CrewAI compatibility method."""
                    return False

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

            llm = MockOllamaLLM(model_name=config.model_name, temperature=config.temperature)
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


class HuggingFaceProvider(LLMProvider):
    """Hugging Face Inference API provider for free tier models."""

    def validate_config(self, config: LLMConfig) -> bool:
        """Validate Hugging Face configuration."""
        if not config.api_key:
            raise LLMProviderError("Hugging Face requires HUGGINGFACE_API_TOKEN")
        if not config.model_name:
            raise LLMProviderError("Hugging Face requires model_name")
        return True

    def create_llm(self, config: LLMConfig):
        """Create Hugging Face LLM instance."""
        self.validate_config(config)

        try:
            # Try to import huggingface_hub
            try:
                from huggingface_hub import InferenceClient
            except ImportError:
                raise LLMProviderError(
                    "huggingface_hub package not installed. Run: pip install huggingface_hub"
                )

            class HuggingFaceLLM:
                def __init__(self, model_name: str, api_key: str, temperature: float = 0.7):
                    self.model_name = model_name
                    self.api_key = api_key
                    self.temperature = temperature

                    # Initialize the client
                    self.client = InferenceClient(model=model_name, token=api_key)

                    # CrewAI compatibility attributes
                    self.supports_functions = False
                    self.supports_tools = False
                    self.stop = None

                    logger.info(
                        f"✅ HuggingFace LLM created (model: {model_name}, temperature: {temperature})"
                    )

                def supports_stop_words(self) -> bool:
                    """CrewAI compatibility method."""
                    return False

                def invoke(self, messages, **kwargs):
                    """Synchronous invocation."""
                    try:
                        # Convert messages to chat format for conversational models
                        formatted_messages = self._format_messages_for_chat(messages)

                        # Try chat completion first (for conversational models)
                        try:
                            response = self.client.chat_completion(
                                messages=formatted_messages,
                                temperature=self.temperature,
                                max_tokens=kwargs.get("max_tokens", 1000),
                            )

                            # Extract content from response
                            if hasattr(response, "choices") and response.choices:
                                content = response.choices[0].message.content
                                logger.info(f"[HF SUCCESS] Chat completion for {self.model_name}")
                                return content
                            else:
                                return str(response)

                        except Exception as chat_error:
                            # Fallback to text generation if chat completion fails
                            logger.warning(
                                f"Chat completion failed, trying text generation: {chat_error}"
                            )

                            prompt = self._format_messages_as_text(messages)
                            response = self.client.text_generation(
                                prompt=prompt,
                                temperature=self.temperature,
                                max_new_tokens=kwargs.get("max_tokens", 1000),
                                do_sample=True if self.temperature > 0 else False,
                                return_full_text=False,
                            )

                            logger.info(f"[HF SUCCESS] Text generation for {self.model_name}")
                            return response

                    except Exception as e:
                        logger.error(f"[HF ERROR] Model {self.model_name} failed: {e}")
                        raise

                async def ainvoke(self, messages, **kwargs):
                    """Async invocation (runs sync for now)."""
                    return self.invoke(messages, **kwargs)

                def __call__(self, messages, **kwargs):
                    """Call interface for compatibility."""
                    return self.invoke(messages, **kwargs)

                def is_available(self) -> bool:
                    """Check if the LLM is available."""
                    return True

                def _format_messages_for_chat(self, messages):
                    """Format messages for chat completion API."""
                    if isinstance(messages, list):
                        formatted = []
                        for msg in messages:
                            if hasattr(msg, "content") and hasattr(msg, "role"):
                                formatted.append({"role": msg.role, "content": msg.content})
                            elif isinstance(msg, dict) and "content" in msg:
                                role = msg.get("role", "user")
                                formatted.append({"role": role, "content": msg["content"]})
                            else:
                                formatted.append({"role": "user", "content": str(msg)})
                        return formatted
                    return [{"role": "user", "content": str(messages)}]

                def _format_messages_as_text(self, messages):
                    """Format messages as text for text generation API."""
                    if isinstance(messages, list):
                        text_parts = []
                        for msg in messages:
                            if hasattr(msg, "content"):
                                text_parts.append(msg.content)
                            elif isinstance(msg, dict) and "content" in msg:
                                text_parts.append(msg["content"])
                            else:
                                text_parts.append(str(msg))
                        return "\n".join(text_parts)
                    return str(messages)

            llm = HuggingFaceLLM(
                model_name=config.model_name, api_key=config.api_key, temperature=config.temperature
            )

            logger.info(f"✅ Hugging Face LLM created successfully (model: {config.model_name})")
            return llm

        except Exception as e:
            error_msg = f"Failed to create Hugging Face LLM: {e}"
            logger.error(error_msg)
            raise LLMProviderError(error_msg)


class LLMFactory:
    """
    Factory for creating LLM instances.
    Supports multiple AI providers with proper factory pattern.
    """

    _providers: dict[AIProvider, type[LLMProvider]] = {
        AIProvider.GEMINI: GoogleGeminiProvider,
        AIProvider.HUGGINGFACE: HuggingFaceProvider,
        AIProvider.OLLAMA: OllamaProvider,
        AIProvider.MOCK: MockLLMProvider,
    }

    @classmethod
    def register_provider(cls, provider: AIProvider, provider_class: type[LLMProvider]):
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
        logger.info(
            f"Creating LLM with provider: {config.provider.value}, model: {config.model_name}"
        )

        provider = cls.get_provider(config.provider)
        return provider.create_llm(config)

    @classmethod
    def create_from_environment(cls, model_name: str | None = None) -> "Any":
        """
        Create an LLM instance from environment variables.

        Args:
            model_name: Optional model name override
        Returns:
            LangChain-compatible LLM instance
        """
        # Get provider from environment
        provider_str = os.getenv("AI_PROVIDER", "gemini")
        logger.debug(f"🔍 [DEBUG] LLMFactory: AI_PROVIDER from env: {provider_str}")

        try:
            provider = AIProvider(provider_str)
            logger.debug(f"🔍 [DEBUG] LLMFactory: Selected provider: {provider.value}")
        except ValueError:
            raise LLMProviderError(f"Invalid AI_PROVIDER: {provider_str}")

        # Get API key from environment (only for real providers)
        api_key = ""
        if provider == AIProvider.GEMINI:
            api_key = os.getenv("GOOGLE_API_KEY", "")
        elif provider == AIProvider.HUGGINGFACE:
            api_key = os.getenv("HUGGINGFACE_API_TOKEN", "")
        elif provider == AIProvider.OLLAMA:
            # Ollama doesn't need API key
            api_key = ""
        elif provider == AIProvider.MOCK:
            api_key = "mock-key"  # Mock doesn't need real API key

        # Use default model if not specified
        if not model_name:
            # Try AI_MODEL_NAME first, then provider-specific fallbacks
            model_name = os.getenv("AI_MODEL_NAME")
            logger.debug(f"🔍 [DEBUG] LLMFactory: AI_MODEL_NAME from env: {model_name}")

        if not model_name:
            if provider == AIProvider.GEMINI:
                model_name = os.getenv("GOOGLE_AI_MODEL_NAME", "gemini-1.5-flash")
                logger.debug(f"🔍 [DEBUG] LLMFactory: GOOGLE_AI_MODEL_NAME from env: {model_name}")
            elif provider == AIProvider.HUGGINGFACE:
                model_name = os.getenv("HUGGINGFACE_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
                logger.debug(f"🔍 [DEBUG] LLMFactory: HUGGINGFACE_MODEL from env: {model_name}")
            elif provider == AIProvider.OLLAMA:
                model_name = os.getenv("OLLAMA_MODEL", "llama2")
                logger.debug(f"🔍 [DEBUG] LLMFactory: OLLAMA_MODEL from env: {model_name}")
            elif provider == AIProvider.MOCK:
                model_name = os.getenv("MOCK_MODEL", "mock-model")
                logger.debug(f"🔍 [DEBUG] LLMFactory: MOCK_MODEL from env: {model_name}")

        logger.debug(f"🔍 [DEBUG] LLMFactory: Final model_name: {model_name}")

        config = LLMConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=float(
                os.getenv("LLM_TEMPERATURE", "0.1")
            ),  # Default to low temperature to prevent hallucination
            timeout_seconds=int(os.getenv("LLM_TIMEOUT", "30")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
        )

        return cls.create_llm(config)

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported AI providers."""
        return [provider.value for provider in cls._providers.keys()]


def create_llm(provider: AIProvider, model_name: str = None, **kwargs):
    """
    Convenience function to create LLM instances.

    Args:
        provider: AI provider enum
        model_name: Optional model name override
        **kwargs: Additional configuration parameters

    Returns:
        LLM instance compatible with CrewAI
    """
    if provider == AIProvider.OLLAMA:
        # Set default Ollama configuration
        ollama_base_url = kwargs.get('api_base') or os.getenv("OLLAMA_BASE_URL", "http://macmini1.local:11434")
        ollama_model = model_name or os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_0")

        config = LLMConfig(
            provider=provider,
            model_name=ollama_model,
            api_key="",  # Ollama doesn't need API key
            temperature=kwargs.get('temperature', 0.3),
            timeout_seconds=kwargs.get('timeout', 30),
            max_retries=kwargs.get('max_retries', 3),
            api_base=ollama_base_url
        )

        return LLMFactory.create_llm(config)

    else:
        # Use environment-based creation for other providers
        return LLMFactory.create_from_environment(model_name)
