# KICKAI Prompt Template System

A centralized, type-safe prompt management system for the NLP Processor agent and other components that need structured prompt generation.

## Overview

This system replaces hardcoded prompt strings with a maintainable, reusable template architecture that provides:

- **Type Safety** - Pydantic models ensure parameter validation
- **DRY Principle** - Reusable prompt components and inheritance
- **Maintainability** - Single source of truth for all prompts
- **Flexibility** - Easy A/B testing and experimentation
- **Performance** - Cached templates reduce string operations
- **Documentation** - Self-documenting prompt structure

## Architecture

### Core Components

```
kickai/agents/prompts/
├── nlp_prompts.py           # Core template library
├── __init__.py              # Package exports
└── README.md                # This documentation

kickai/config/
└── nlp_prompts.yaml         # Configuration and overrides

tests/unit/agents/
└── test_prompt_templates.py # Comprehensive tests
```

### Key Classes

- **`BasePromptTemplate`** - Abstract base for all templates
- **`FootballContextTemplate`** - Base for football-specific prompts
- **`PromptTemplateRegistry`** - Centralized template management
- **Context Models** - Pydantic models for parameter validation

## Quick Start

### Basic Usage

```python
from kickai.agents.prompts import render_prompt, validate_prompt_context

# Prepare context
context = {
    'telegram_id': 123456789,
    'team_id': 'KTI',
    'username': 'player1',
    'chat_type': 'main',
    'message': 'What is my status?'
}

# Validate context (optional but recommended)
if validate_prompt_context('intent_recognition', context):
    # Render prompt
    prompt = render_prompt('intent_recognition', context)
    print(prompt)
else:
    print("Invalid context")
```

### Available Templates

| Template | Purpose | Required Context |
|----------|---------|------------------|
| `intent_recognition` | Analyze user intent | telegram_id, team_id, username, chat_type, message, conversation_history |
| `entity_extraction` | Extract football entities | telegram_id, team_id, username, chat_type, message |
| `conversation_context` | Multi-turn conversation analysis | telegram_id, team_id, username, chat_type |
| `semantic_similarity` | Command similarity analysis | telegram_id, team_id, username, chat_type, message, reference_commands |
| `routing_recommendation` | Agent routing suggestions | telegram_id, team_id, username, chat_type, intent_data |
| `update_context` | Update command analysis | telegram_id, team_id, username, chat_type, message |
| `permission_validation` | Permission checking | telegram_id, team_id, username, chat_type, user_role, requested_action |

## Advanced Usage

### Creating Custom Templates

```python
from kickai.agents.prompts import FootballContextTemplate, PromptContext

@dataclass
class CustomTemplate(FootballContextTemplate):
    name: str = "custom_analysis"
    description: str = "Custom analysis template"
    
    def get_context_model(self) -> type[BaseModel]:
        return PromptContext
    
    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}
        
        Custom analysis for user $username:
        Team: $team_id
        Chat: $chat_type
        
        Perform custom analysis here.
        """

# Register the template
from kickai.agents.prompts import get_prompt_registry
registry = get_prompt_registry()
registry.register_template(CustomTemplate())
```

### Working with the Registry

```python
from kickai.agents.prompts import get_prompt_registry

# Get registry instance
registry = get_prompt_registry()

# List available templates
templates = registry.list_templates()
print(f"Available templates: {templates}")

# Get specific template
template = registry.get_template('intent_recognition')
print(f"Template: {template.name} v{template.version}")

# Render with template instance
context = {...}
prompt = template.render(context)
```

## Configuration

### YAML Configuration

The system supports YAML-based configuration in `kickai/config/nlp_prompts.yaml`:

```yaml
# Global settings
global_settings:
  defaults:
    version: "1.0"
    response_format: "json"
  performance:
    enable_caching: true
    cache_ttl_seconds: 3600

# Environment overrides
environments:
  development:
    verbose: true
    include_debug_info: true
  production:
    verbose: false
    max_length: 1500

# Template configurations
templates:
  intent_recognition:
    confidence_thresholds:
      high: 0.85
      medium: 0.65
      low: 0.40
    variants:
      default:
        include_examples: false
      enhanced:
        include_examples: true
        include_reasoning: true
```

### Feature Flags

```yaml
feature_flags:
  enable_advanced_reasoning: true
  enable_context_memory: false
  enable_user_personalization: false
```

## Integration with NLP Tools

The prompt system is integrated with all NLP processor tools:

### Before (Hardcoded)

```python
@tool("advanced_intent_recognition")
async def advanced_intent_recognition(telegram_id, team_id, username, chat_type, message):
    # Hardcoded prompt string
    analysis_prompt = f"""
    Analyze the user's intent for this request:
    Message: "{message}"
    Chat Context: {chat_type}
    ...
    """
    return create_json_response("success", data={"analysis_prompt": analysis_prompt})
```

### After (Template System)

```python
@tool("advanced_intent_recognition")
async def advanced_intent_recognition(telegram_id, team_id, username, chat_type, message):
    # Prepare context
    context = {
        'telegram_id': telegram_id,
        'team_id': team_id,
        'username': username,
        'chat_type': chat_type,
        'message': message
    }
    
    # Validate and render
    if not validate_prompt_context('intent_recognition', context):
        return create_json_response("error", message="Invalid context")
    
    analysis_prompt = render_prompt('intent_recognition', context)
    return create_json_response("success", data={"analysis_prompt": analysis_prompt})
```

## Context Models

### Base Context

```python
class PromptContext(BaseModel):
    telegram_id: int = Field(..., description="User's Telegram ID")
    team_id: str = Field(..., min_length=1, description="Team identifier")
    username: str = Field(..., min_length=1, description="Username")
    chat_type: str = Field(..., description="Chat context (main/leadership/private)")
```

### Specialized Contexts

```python
class IntentAnalysisContext(PromptContext):
    message: str = Field(..., min_length=1, description="User message to analyze")
    conversation_history: Optional[str] = Field(default="", description="Previous conversation context")

class PermissionValidationContext(PromptContext):
    user_role: str = Field(..., description="User's role in the system")
    requested_action: str = Field(..., min_length=1, description="Action being requested")
```

## Error Handling

### Validation Errors

```python
from pydantic import ValidationError

try:
    prompt = render_prompt('intent_recognition', invalid_context)
except ValueError as e:
    print(f"Template rendering failed: {e}")
    # Handle error appropriately

# Or validate first
if validate_prompt_context('intent_recognition', context):
    prompt = render_prompt('intent_recognition', context)
else:
    print("Context validation failed")
```

### Template Errors

```python
from kickai.agents.prompts import get_prompt_registry

try:
    template = get_prompt_registry().get_template('nonexistent')
except KeyError as e:
    print(f"Template not found: {e}")
```

## Performance Considerations

### Caching

The system uses LRU caching for performance:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_prompt_registry() -> PromptTemplateRegistry:
    """Cached registry instance for performance."""
    return PromptTemplateRegistry()
```

### Template Reuse

Templates are instantiated once and reused:

```python
# Registry initializes all templates once
registry = PromptTemplateRegistry()

# Templates are reused for multiple renders
template = registry.get_template('intent_recognition')
prompt1 = template.render(context1)
prompt2 = template.render(context2)  # Reuses same template instance
```

## Testing

### Running Tests

```bash
# Run all prompt template tests
PYTHONPATH=. python -m pytest tests/unit/agents/test_prompt_templates.py -v

# Run specific test class
PYTHONPATH=. python -m pytest tests/unit/agents/test_prompt_templates.py::TestPromptTemplates -v

# Run with coverage
PYTHONPATH=. python -m pytest tests/unit/agents/test_prompt_templates.py --cov=kickai.agents.prompts
```

### Test Coverage

The test suite covers:

- Template rendering with valid/invalid contexts
- Context model validation
- Registry functionality
- Convenience functions
- Integration with NLP tools
- Performance and caching
- Edge cases and error handling

### Example Test

```python
def test_intent_recognition_template():
    template = IntentRecognitionTemplate()
    
    context = {
        'telegram_id': 123456789,
        'team_id': 'KTI',
        'username': 'testuser',
        'chat_type': 'main',
        'message': 'What is my status?',
        'conversation_history': 'None'
    }
    
    prompt = template.render(context)
    
    # Verify content
    assert 'What is my status?' in prompt
    assert 'KTI' in prompt
    assert 'INTENT CATEGORIES' in prompt
    assert 'JSON format' in prompt
```

## Migration Guide

### From Hardcoded Prompts

1. **Identify prompt strings** in your code
2. **Choose appropriate template** or create a custom one
3. **Extract context variables** from the prompt
4. **Replace with template system calls**
5. **Add validation** for robustness

### Example Migration

```python
# Before
def old_function(user, team, message):
    prompt = f"Analyze: {message} for {user} in {team}"
    return process(prompt)

# After  
def new_function(user, team, message):
    context = {
        'telegram_id': user.telegram_id,
        'team_id': team,
        'username': user.name,
        'chat_type': 'main',
        'message': message
    }
    
    if validate_prompt_context('analysis_template', context):
        prompt = render_prompt('analysis_template', context)
        return process(prompt)
    else:
        raise ValueError("Invalid context for analysis")
```

## Best Practices

### 1. Always Validate Context

```python
# Good
if validate_prompt_context(template_name, context):
    prompt = render_prompt(template_name, context)
else:
    handle_error()

# Better - handle validation errors
try:
    prompt = render_prompt(template_name, context)
except ValueError as e:
    logger.error(f"Prompt validation failed: {e}")
    handle_error()
```

### 2. Use Appropriate Templates

```python
# Match template to use case
context = prepare_context(user_input)

if is_intent_analysis(user_input):
    prompt = render_prompt('intent_recognition', context)
elif is_entity_extraction(user_input):
    prompt = render_prompt('entity_extraction', context)
else:
    prompt = render_prompt('conversation_context', context)
```

### 3. Handle Errors Gracefully

```python
def safe_render_prompt(template_name, context):
    try:
        return render_prompt(template_name, context)
    except (ValueError, KeyError) as e:
        logger.error(f"Prompt rendering failed: {e}")
        return get_fallback_prompt(context)
```

### 4. Cache Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_prompt(template_name, context_hash):
    # Only cache if context is hashable
    return render_prompt(template_name, context)
```

## Troubleshooting

### Common Issues

1. **ValidationError**: Check context parameters match template requirements
2. **KeyError**: Verify template name exists in registry
3. **Template variables not substituted**: Ensure context keys match template placeholders
4. **Performance issues**: Check if caching is enabled and working

### Debug Mode

```python
import logging
logging.getLogger('kickai.agents.prompts').setLevel(logging.DEBUG)

# Enable debug information in templates
context['_debug'] = True
prompt = render_prompt('template_name', context)
```

### Logging

```python
from loguru import logger

logger.debug(f"Rendering template {template_name} with context: {context}")
prompt = render_prompt(template_name, context)
logger.debug(f"Rendered prompt length: {len(prompt)} characters")
```

## Contributing

### Adding New Templates

1. Create template class inheriting from `FootballContextTemplate`
2. Define context model with proper validation
3. Implement `get_template()` method
4. Add to registry initialization
5. Write comprehensive tests
6. Update documentation

### Template Guidelines

- Use clear, descriptive names
- Include version information
- Provide detailed docstrings
- Follow football terminology
- Ensure JSON output format
- Include proper error handling

## Future Enhancements

### Planned Features

- **Template Versioning** - A/B testing and rollback capabilities
- **Multi-language Support** - Internationalization for prompts
- **Dynamic Templates** - Runtime template modification
- **Analytics Integration** - Prompt performance tracking
- **Template Composition** - Complex templates from simpler components

### Configuration Enhancements

- **Environment-specific overrides** - Production vs development prompts
- **User personalization** - Customized prompts per user
- **Context memory** - Remember conversation history
- **Quality scoring** - Automatic prompt quality assessment

---

## Summary

The KICKAI Prompt Template System provides a robust, maintainable solution for managing LLM prompts. It eliminates hardcoded strings, ensures type safety, and enables easy experimentation while maintaining high performance through caching and optimization.

Key benefits:
- ✅ **Centralized Management** - Single source of truth
- ✅ **Type Safety** - Pydantic validation
- ✅ **Maintainability** - DRY principle and inheritance
- ✅ **Flexibility** - Easy A/B testing and customization
- ✅ **Performance** - Caching and optimization
- ✅ **Testing** - Comprehensive test coverage