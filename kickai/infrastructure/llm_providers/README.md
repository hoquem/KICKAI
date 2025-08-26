# LLM Provider Factory

This module provides a factory pattern for managing different LLM providers with proper configuration, error handling, and integration with the existing LLM factory system.

## Overview

The LLM Provider Factory provides a clean, extensible interface for creating and managing different LLM providers. It integrates seamlessly with the existing `kickai.utils.llm_factory` system while providing additional abstraction and management capabilities.

## Features

- **Multiple Provider Support**: Ollama, Gemini, Hugging Face, Mock, and more
- **Configuration Management**: Centralized configuration with validation
- **Health Monitoring**: Provider availability and health status tracking
- **Environment Integration**: Easy configuration from environment variables
- **Settings Integration**: Integration with application settings
- **Extensibility**: Easy to add new providers
- **Error Handling**: Robust error handling and fallback mechanisms

## Quick Start

### Basic Usage

```python
from kickai.core.enums import AIProvider
from kickai.infrastructure.llm_providers.factory import (
    ProviderConfig,
    create_llm_provider
)

# Create an Ollama provider
config = ProviderConfig(
    provider=AIProvider.OLLAMA,
    model_name="llama2",
    base_url="http://localhost:11434",
    temperature=0.7,
)

provider = create_llm_provider(config)
llm = provider.create_llm()

# Use the LLM
response = llm.invoke([{"role": "user", "content": "Hello!"}])
```

### Environment-Based Configuration

```python
from kickai.infrastructure.llm_providers.factory import create_llm_provider_from_environment

# Set environment variables
os.environ["AI_PROVIDER"] = "ollama"
os.environ["OLLAMA_MODEL"] = "llama2"
os.environ["LLM_TEMPERATURE"] = "0.7"

# Create provider from environment
provider = create_llm_provider_from_environment()
llm = provider.create_llm()
```

### Settings-Based Configuration

```python
from kickai.infrastructure.llm_providers.factory import create_llm_provider_from_settings

# Create provider from application settings
provider = create_llm_provider_from_settings()
llm = provider.create_llm()
```

## Supported Providers

### Ollama Provider

For local Ollama models:

```python
config = ProviderConfig(
    provider=AIProvider.OLLAMA,
    model_name="llama2",
    base_url="http://localhost:11434",  # Optional, defaults to localhost
    temperature=0.7,
)
```

### Gemini Provider

For Google Gemini models:

```python
config = ProviderConfig(
    provider=AIProvider.GEMINI,
    model_name="gemini-1.5-flash",
    api_key="your-api-key",
    temperature=0.3,
)
```

### Hugging Face Provider

For Hugging Face models:

```python
config = ProviderConfig(
    provider=AIProvider.HUGGINGFACE,
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    api_key="your-api-key",
    temperature=0.5,
)
```

### Mock Provider

For testing and development:

```python
config = ProviderConfig(
    provider=AIProvider.MOCK,
    model_name="test-model",
    temperature=0.5,
)
```

## Factory Methods

### LLMProviderFactory

The main factory class provides several methods:

```python
from kickai.infrastructure.llm_providers.factory import LLMProviderFactory

# Get supported providers
providers = LLMProviderFactory.get_supported_providers()

# Get provider class
provider_class = LLMProviderFactory.get_provider_class(AIProvider.OLLAMA)

# Create provider
provider = LLMProviderFactory.create_provider(config)

# Create from settings
provider = LLMProviderFactory.create_from_settings()

# Create from environment
provider = LLMProviderFactory.create_from_environment()

# Get health status
health_status = LLMProviderFactory.get_provider_health_status()
```

## Health Monitoring

Monitor provider health and availability:

```python
from kickai.infrastructure.llm_providers.factory import get_provider_health_status

# Get health status for all providers
health_status = get_provider_health_status()

for provider_name, status in health_status.items():
    if status.get("available", False):
        print(f"✅ {provider_name}: Available")
    else:
        print(f"⚠️  {provider_name}: Unavailable")
```

## Custom Providers

You can easily add custom providers by extending the `BaseLLMProvider` class:

```python
from kickai.infrastructure.llm_providers.factory import BaseLLMProvider, LLMProviderFactory

class CustomProvider(BaseLLMProvider):
    def _validate_config(self) -> None:
        # Validate custom configuration
        pass
    
    def create_llm(self):
        # Create and return your custom LLM
        return CustomLLM()
    
    def is_available(self) -> bool:
        # Check if provider is available
        return True

# Register the custom provider
LLMProviderFactory.register_provider(AIProvider.CUSTOM, CustomProvider)
```

## Configuration

### ProviderConfig

The `ProviderConfig` dataclass provides configuration for all providers:

```python
@dataclass
class ProviderConfig:
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3
    additional_params: Optional[Dict[str, Any]] = None
```

### Environment Variables

The factory supports configuration via environment variables:

- `AI_PROVIDER`: The provider to use (ollama, gemini, huggingface, mock)
- `AI_MODEL_SIMPLE`: Simple model for lightweight operations
- `AI_MODEL_ADVANCED`: Advanced model for complex operations
- `AI_MODEL_NLP`: Specialized NLP model (e.g., gpt-oss-20b)
- `LLM_TEMPERATURE`: Temperature setting
- `LLM_TIMEOUT`: Timeout in seconds
- `LLM_MAX_RETRIES`: Maximum retry attempts

Provider-specific variables:
- `OLLAMA_BASE_URL`: Ollama server URL
- `OLLAMA_MODEL`: Ollama model name
- `GOOGLE_API_KEY`: Google API key for Gemini
- `GOOGLE_AI_MODEL_NAME`: Gemini model name
- `HUGGINGFACE_API_TOKEN`: Hugging Face API token
- `HUGGINGFACE_MODEL`: Hugging Face model name

## Integration with Existing System

The factory integrates seamlessly with the existing `kickai.utils.llm_factory` system:

- Uses the same `LLMConfig` and `LLMFactory` classes
- Maintains compatibility with existing code
- Provides additional abstraction layer
- Supports all existing providers

## Testing

Run the test suite to verify functionality:

```bash
python kickai/infrastructure/llm_providers/test_factory.py
```

Run the example usage script:

```bash
python kickai/infrastructure/llm_providers/example_usage.py
```

## Error Handling

The factory provides robust error handling:

- Configuration validation with descriptive error messages
- Provider availability checking
- Graceful fallbacks for unavailable providers
- Comprehensive logging for debugging

## Best Practices

1. **Use Settings for Production**: Use `create_llm_provider_from_settings()` for production environments
2. **Environment for Development**: Use `create_llm_provider_from_environment()` for development and testing
3. **Health Monitoring**: Regularly check provider health status
4. **Error Handling**: Always handle potential provider creation failures
5. **Configuration Validation**: Validate configuration before creating providers

## Examples

See `example_usage.py` for comprehensive examples of all features.

## Architecture

The factory follows clean architecture principles:

- **Abstraction**: `BaseLLMProvider` provides the interface
- **Implementation**: Concrete provider classes implement the interface
- **Factory**: `LLMProviderFactory` manages provider creation
- **Configuration**: `ProviderConfig` provides type-safe configuration
- **Integration**: Seamless integration with existing LLM factory system 