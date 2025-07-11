# LLM Factory Configuration Guide

## Overview

The KICKAI system now uses a proper factory pattern for LLM creation that supports multiple AI providers and reads configuration from environment variables.

## Environment Variables

### Required Configuration

```bash
# AI Provider (required)
AI_PROVIDER=google_gemini

# For Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# For Ollama (if using local models)
# AI_PROVIDER=ollama
# OLLAMA_MODEL=llama2
```

### Optional Configuration

```bash
# Model Selection
GEMINI_MODEL=gemini-1.5-flash  # Default for Gemini
OLLAMA_MODEL=llama2           # Default for Ollama

# LLM Settings
LLM_TEMPERATURE=0.7           # Default: 0.7
LLM_TIMEOUT=30                # Default: 30 seconds
LLM_MAX_RETRIES=3             # Default: 3
```

## Supported Providers

### Google Gemini
- **Provider ID**: `google_gemini`
- **Required**: `GOOGLE_API_KEY`
- **Models**: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-pro`
- **Uses**: Direct Gemini API (not Vertex AI)

### Ollama
- **Provider ID**: `ollama`
- **Required**: Ollama server running locally
- **Models**: Any model available in your Ollama installation
- **Uses**: Local LLM inference

## Usage Examples

### Using the Factory

```python
from utils.llm_factory import LLMFactory

# Create LLM from environment variables
llm = LLMFactory.create_from_environment()

# Create LLM with specific configuration
from utils.llm_factory import LLMConfig
from core.enums import AIProvider

config = LLMConfig(
    provider=AIProvider.GOOGLE_GEMINI,
    model_name="gemini-1.5-flash",
    api_key="your_api_key",
    temperature=0.7
)
llm = LLMFactory.create_llm(config)
```

### Adding New Providers

```python
from utils.llm_factory import LLMProvider, LLMFactory
from core.enums import AIProvider

class MyCustomProvider(LLMProvider):
    def validate_config(self, config):
        # Validate configuration
        return True
    
    def create_llm(self, config):
        # Create and return LLM instance
        return my_llm_instance

# Register the new provider
LLMFactory.register_provider(AIProvider.MY_CUSTOM, MyCustomProvider)
```

## Migration from Old System

The old system used hardcoded Gemini configuration. The new system:

1. **Reads from environment**: No more hardcoded API keys
2. **Supports multiple providers**: Easy to switch between Gemini and Ollama
3. **Factory pattern**: Clean, extensible architecture
4. **Environment-based**: Configuration through environment variables

### Old Code
```python
config = LLMConfig(
    provider=AIProvider.GOOGLE_GEMINI,
    model_name="gemini-1.5-flash",
    api_key=os.getenv('GOOGLE_API_KEY'),
    temperature=0.7
)
llm = LLMFactory.create_llm(config)
```

### New Code
```python
llm = LLMFactory.create_from_environment()
```

## Environment File Example

Create a `.env` file in your project root:

```bash
# AI Provider Configuration
AI_PROVIDER=google_gemini
GOOGLE_API_KEY=your_actual_api_key_here

# Model Configuration
GEMINI_MODEL=gemini-1.5-flash

# LLM Settings
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3
```

## Troubleshooting

### Common Issues

1. **"Invalid AI_PROVIDER"**: Make sure `AI_PROVIDER` is set to a supported value
2. **"Google Gemini requires GOOGLE_API_KEY"**: Set your `GOOGLE_API_KEY` environment variable
3. **"Unsupported AI provider"**: The provider isn't registered in the factory

### Debug Mode

Enable debug logging to see factory operations:

```python
import logging
logging.getLogger('utils.llm_factory').setLevel(logging.DEBUG)
``` 