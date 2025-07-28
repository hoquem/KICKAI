# Configuration System

## Overview

The KICKAI system implements a modular, extensible configuration architecture using proven design patterns. This provides better maintainability, testability, and flexibility while maintaining backward compatibility.

## Design Patterns Used

### 1. Strategy Pattern - Configuration Sources

**Purpose**: Allow different configuration sources to be used interchangeably.

**Implementation**: `ConfigurationSource` abstract base class with concrete implementations:
- `EnvironmentConfigurationSource`: Loads from environment variables
- `FileConfigurationSource`: Loads from JSON files
- `DatabaseConfigurationSource`: Loads from database (for production)
- `DefaultConfigurationSource`: Provides default values

**Benefits**:
- Easy to add new configuration sources
- Clear separation of concerns
- Testable in isolation
- Priority-based loading

```python
# Example: Adding a new configuration source
class KubernetesConfigurationSource(ConfigurationSource):
    def load_configuration(self, environment: Environment) -> Dict[str, Any]:
        # Load from Kubernetes ConfigMaps
        pass
    
    def get_priority(self) -> int:
        return 75  # Between environment and file
    
    def is_available(self, environment: Environment) -> bool:
        return environment == Environment.PRODUCTION
```

### 2. Factory Pattern - Configuration Object Creation

**Purpose**: Centralize object creation logic and ensure consistent configuration objects.

**Implementation**: `ConfigurationFactory` with static methods for each configuration type.

**Benefits**:
- Consistent object creation
- Easy to modify creation logic
- Type safety
- Validation during creation

```python
# Example usage
db_config = ConfigurationFactory.create_database_config({
    "project_id": "my-project",
    "collection_prefix": "custom",
    "source": ConfigSource.FILE
})
```

### 3. Builder Pattern - Complex Configuration Building

**Purpose**: Construct complex configuration objects step by step.

**Implementation**: `ConfigurationBuilder` with fluent interface.

**Benefits**:
- Readable configuration construction
- Optional parameters
- Validation at build time
- Immutable final objects

```python
# Example usage
config = (ConfigurationBuilder()
    .environment(Environment.PRODUCTION)
    .database(DatabaseConfig(project_id="prod-project"))
    .ai(AIConfig(provider=AIProvider.GOOGLE_GEMINI, api_key="key"))
    .metadata("version", "2.0")
    .build()
)
```

### 4. Observer Pattern - Configuration Change Notifications

**Purpose**: Notify components when configuration changes.

**Implementation**: `ConfigurationObserver` interface and `ConfigurationChangeNotifier`.

**Benefits**:
- Loose coupling between configuration and consumers
- Automatic updates when configuration changes
- Multiple observers can react to changes
- Easy to add/remove observers

```python
# Example observer
class LoggingObserver(ConfigurationObserver):
    def on_configuration_changed(self, config: Configuration):
        # Update logging configuration
        logging.getLogger().setLevel(config.logging.level)

# Usage
manager = get_improved_config()
manager.add_observer(LoggingObserver())
```

### 5. Chain of Responsibility - Configuration Validation

**Purpose**: Validate configuration through a chain of validators.

**Implementation**: `ConfigurationValidator` abstract class with concrete validators:
- `EnvironmentValidator`: Environment-specific validation
- `DatabaseValidator`: Database configuration validation
- `AIValidator`: AI configuration validation

**Benefits**:
- Modular validation logic
- Easy to add new validators
- Clear error messages
- Environment-specific validation

```python
# Example: Adding a new validator
class SecurityValidator(ConfigurationValidator):
    def validate(self, config: Configuration) -> List[str]:
        errors = []
        if len(config.security.jwt_secret) < 32:
            errors.append("JWT secret must be at least 32 characters")
        return self._validate_next(config, errors)
```

### 6. Singleton Pattern - Global Configuration Manager

**Purpose**: Ensure single configuration instance across the application.

**Implementation**: `ImprovedConfigurationManager` with singleton behavior.

**Benefits**:
- Consistent configuration across application
- Memory efficiency
- Thread-safe access
- Centralized configuration management

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ImprovedConfigurationManager (Singleton)                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Configuration   │  │ Configuration   │  │ Configuration│ │
│  │ Sources         │  │ Validators      │  │ Observers    │ │
│  │ (Strategy)      │  │ (Chain of       │  │ (Observer)   │ │
│  │                 │  │  Responsibility)│  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Configuration Layer                      │
├─────────────────────────────────────────────────────────────┤
│  ConfigurationFactory (Factory)                            │
│  ConfigurationBuilder (Builder)                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ DatabaseConfig  │  │ AIConfig        │  │ TelegramConfig│ │
│  │ LoggingConfig   │  │ PerformanceConfig│  │ SecurityConfig│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Data Sources                             │
├─────────────────────────────────────────────────────────────┤
│  Environment Variables │ JSON Files │ Database │ Defaults   │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Types

### Database Configuration
```python
@dataclass
class DatabaseConfig:
    project_id: str
    collection_prefix: str = "kickai"
    source: ConfigSource = ConfigSource.ENVIRONMENT
    credentials_path: Optional[str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
```

### AI Configuration
```python
@dataclass
class AIConfig:
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3
```

### Telegram Configuration
```python
@dataclass
class TelegramConfig:
    bot_token: str
    main_chat_id: str
    leadership_chat_id: str
    webhook_url: Optional[str] = None
    polling_interval: int = 1
    timeout_seconds: int = 30
```

### Logging Configuration
```python
@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
```

## Configuration Sources

### Environment Variables
- **Priority**: Highest (100)
- **Usage**: Production deployments
- **Format**: Standard environment variable format
- **Example**: `AI_PROVIDER=google_gemini`, `AI_API_KEY=your_key`

### JSON Files
- **Priority**: Medium (50)
- **Usage**: Development and testing
- **Format**: JSON configuration files
- **Example**: `config/local.json`, `config/testing.json`

### Database
- **Priority**: Low (25)
- **Usage**: Dynamic configuration in production
- **Format**: Firestore documents
- **Example**: `configurations/team_bp_hatters`

### Defaults
- **Priority**: Lowest (0)
- **Usage**: Fallback values
- **Format**: Hardcoded defaults
- **Example**: Default AI provider, timeouts, etc.

## Validation Rules

### Environment-Specific Validation
- **Development**: Relaxed validation, more defaults
- **Testing**: Strict validation, mock configurations
- **Production**: Strict validation, required fields enforced

### Required Fields by Environment
```python
# Development
required_fields_dev = ["TEAM_ID", "BOT_TOKEN"]

# Production
required_fields_prod = [
    "TEAM_ID", "BOT_TOKEN", "AI_PROVIDER", "AI_API_KEY",
    "FIREBASE_CREDENTIALS_JSON", "MAIN_CHAT_ID", "LEADERSHIP_CHAT_ID"
]
```

### AI Provider Validation
- **Google Gemini**: Requires `GOOGLE_API_KEY`
- **OpenAI**: Requires `OPENAI_API_KEY`

## Usage Patterns

### Basic Configuration Loading
```python
# Get configuration manager
config_manager = get_improved_config()

# Access configuration
ai_config = config_manager.get_ai_config()
db_config = config_manager.get_database_config()
telegram_config = config_manager.get_telegram_config()
```

### Environment-Specific Configuration
```python
# Load configuration for specific environment
config = config_manager.load_configuration(Environment.PRODUCTION)

# Validate configuration
errors = config_manager.validate_configuration(config)
if errors:
    raise ConfigurationError(f"Configuration errors: {errors}")
```

### Dynamic Configuration Updates
```python
# Add observer for configuration changes
class MyObserver(ConfigurationObserver):
    def on_configuration_changed(self, config: Configuration):
        # React to configuration changes
        pass

config_manager.add_observer(MyObserver())
```

## Benefits

### 1. Modularity
- Each configuration source is independent
- Easy to add/remove sources without affecting others
- Clear separation of concerns

### 2. Extensibility
- New configuration sources can be added easily
- New validators can be chained
- New observers can be registered

### 3. Testability
- Each component can be tested in isolation
- Mock sources for testing
- Validation can be tested independently

### 4. Maintainability
- Clear, focused classes
- Single responsibility principle
- Easy to understand and modify

### 5. Flexibility
- Multiple configuration sources
- Priority-based loading
- Environment-specific behavior

### 6. Type Safety
- Strong typing throughout
- IDE support and autocomplete
- Runtime type checking

## Implementation Requirements

### For New Configuration Types
1. **Define Config Class**: Create dataclass with required fields
2. **Add to Factory**: Add creation method to ConfigurationFactory
3. **Add Validation**: Create validator in validation chain
4. **Add to Manager**: Add getter method to configuration manager
5. **Add Tests**: Test configuration loading and validation

### For New Configuration Sources
1. **Implement Interface**: Create class implementing ConfigurationSource
2. **Set Priority**: Define appropriate priority level
3. **Add Validation**: Ensure source availability checking
4. **Add Tests**: Test source loading and error handling
5. **Update Documentation**: Document new source usage

### For New Validators
1. **Extend Base Class**: Create validator extending ConfigurationValidator
2. **Implement Validation**: Add validation logic
3. **Add to Chain**: Register validator in validation chain
4. **Add Tests**: Test validation scenarios
5. **Update Documentation**: Document validation rules 