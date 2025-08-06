#!/usr/bin/env python3
"""
Example Usage of LLM Provider Factory

This script demonstrates how to use the new LLM provider factory
to create and manage different LLM providers.
"""

import asyncio
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from kickai.core.enums import AIProvider
from kickai.infrastructure.llm_providers.factory import (
    BaseLLMProvider,
    LLMProviderFactory,
    ProviderConfig,
    create_llm_provider,
    create_llm_provider_from_environment,
    create_llm_provider_from_settings,
    get_provider_health_status,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example of basic provider creation."""
    logger.info("🔧 Example 1: Basic Provider Creation")

    # Create an Ollama provider
    ollama_config = ProviderConfig(
        provider=AIProvider.OLLAMA,
        model_name="llama2",
        base_url="http://localhost:11434",
        temperature=0.7,
    )

    ollama_provider = create_llm_provider(ollama_config)
    logger.info(f"✅ Created Ollama provider: {ollama_provider.get_health_status()}")

    # Create a mock provider for testing
    mock_config = ProviderConfig(
        provider=AIProvider.MOCK,
        model_name="test-model",
        temperature=0.5,
    )

    mock_provider = create_llm_provider(mock_config)
    logger.info(f"✅ Created Mock provider: {mock_provider.get_health_status()}")


def example_factory_methods():
    """Example of using factory methods."""
    logger.info("🔧 Example 2: Factory Methods")

    # Get supported providers
    supported = LLMProviderFactory.get_supported_providers()
    logger.info(f"✅ Supported providers: {supported}")

    # Get provider class
    ollama_class = LLMProviderFactory.get_provider_class(AIProvider.OLLAMA)
    logger.info(f"✅ Ollama provider class: {ollama_class.__name__}")

    # Create provider using factory
    config = ProviderConfig(
        provider=AIProvider.MOCK,
        model_name="factory-test",
        temperature=0.3,
    )

    provider = LLMProviderFactory.create_provider(config)
    logger.info(f"✅ Factory-created provider: {provider.get_health_status()}")


def example_environment_based():
    """Example of environment-based provider creation."""
    logger.info("🔧 Example 3: Environment-Based Creation")

    # Set environment variables for testing
    os.environ["AI_PROVIDER"] = "mock"
    os.environ["MOCK_MODEL"] = "env-test-model"
    os.environ["LLM_TEMPERATURE"] = "0.2"

    # Create provider from environment
    provider = create_llm_provider_from_environment()
    logger.info(f"✅ Environment-based provider: {provider.get_health_status()}")


def example_settings_based():
    """Example of settings-based provider creation."""
    logger.info("🔧 Example 4: Settings-Based Creation")

    try:
        # Create provider from application settings
        provider = create_llm_provider_from_settings()
        logger.info(f"✅ Settings-based provider: {provider.get_health_status()}")
    except Exception as e:
        logger.warning(f"⚠️  Settings-based creation failed: {e}")


async def example_llm_usage():
    """Example of using the created LLM instances."""
    logger.info("🔧 Example 5: LLM Usage")

    # Create a mock provider and LLM
    config = ProviderConfig(
        provider=AIProvider.MOCK,
        model_name="usage-example",
        temperature=0.5,
    )

    provider = create_llm_provider(config)
    llm = provider.create_llm()

    # Test the LLM
    test_messages = [
        {"role": "user", "content": "Hello, can you help me with a question?"}
    ]

    response = llm.invoke(test_messages)
    logger.info(f"✅ LLM Response: {response[:100]}...")


def example_health_monitoring():
    """Example of health monitoring."""
    logger.info("🔧 Example 6: Health Monitoring")

    # Get health status for all providers
    health_status = get_provider_health_status()

    for provider_name, status in health_status.items():
        if status.get("available", False):
            logger.info(f"✅ {provider_name}: Available")
        else:
            logger.warning(f"⚠️  {provider_name}: Unavailable - {status.get('error', 'Unknown error')}")


def example_custom_provider():
    """Example of creating a custom provider."""
    logger.info("🔧 Example 7: Custom Provider Registration")

    # Define a custom provider
    class CustomProvider(BaseLLMProvider):
        def _validate_config(self) -> None:
            pass

        def create_llm(self):
            # Return a simple mock LLM
            class CustomLLM:
                def invoke(self, messages, **kwargs):
                    return "Custom LLM response: Hello from custom provider!"

                def __call__(self, messages, **kwargs):
                    return self.invoke(messages, **kwargs)

            return CustomLLM()

        def is_available(self) -> bool:
            return True

    # Register the custom provider
    LLMProviderFactory.register_provider(AIProvider.MOCK, CustomProvider)

    # Create and use the custom provider
    config = ProviderConfig(
        provider=AIProvider.MOCK,
        model_name="custom-model",
        temperature=0.5,
    )

    provider = create_llm_provider(config)
    llm = provider.create_llm()

    response = llm.invoke([{"role": "user", "content": "Test"}])
    logger.info(f"✅ Custom provider response: {response}")


def main():
    """Run all examples."""
    logger.info("🚀 Starting LLM Provider Factory Examples...")

    # Run synchronous examples
    example_basic_usage()
    example_factory_methods()
    example_environment_based()
    example_settings_based()
    example_health_monitoring()
    example_custom_provider()

    # Run asynchronous examples
    asyncio.run(example_llm_usage())

    logger.info("✅ All examples completed!")


if __name__ == "__main__":
    main()
