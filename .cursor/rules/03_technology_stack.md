# Technology Stack and Dependencies

## 🎯 **Core Technology Stack**

### **Primary Technologies**
- **Python 3.11** - Core runtime and development language
- **CrewAI** - AI agent orchestration framework
- **Firebase Firestore** - Primary database
- **python-telegram-bot** - Telegram Bot API integration
- **Groq LLM** - Primary AI provider (fail-fast configuration)
- **Ruff** - Linting, formatting, and import sorting
- **Pytest** - Testing framework
- **Loguru** - Structured logging

### **Development Tools**
- **VS Code** - Primary IDE with workspace configuration
- **Cursor** - AI-powered development with custom rules
- **Pre-commit** - Git hooks for code quality
- **Makefile** - Build and development commands

### **Deployment Platform**
- **Railway** - Production deployment platform
- **Firebase** - Database and authentication services
- **Telegram Bot API** - Bot platform

---

## 🤖 **AI and LLM Stack**

### **Primary LLM Provider: Groq**
- **Provider**: Groq (fail-fast configuration)
- **Model**: Groq's high-performance LLM models
- **Configuration**: Single provider with no fallbacks
- **Error Handling**: Fail-fast behavior with immediate error propagation
- **Startup Validation**: Comprehensive LLM connectivity checks

**Adherence to CrewAI Native Features:**
KICKAI is built to fully leverage CrewAI's native features for agent orchestration, task management, and tool utilization. When working with the AI and LLM stack, always prioritize CrewAI's built-in mechanisms for passing context (e.g., `Task.config`), managing memory, and orchestrating agent interactions. Avoid custom implementations for functionalities already supported by CrewAI. For detailed guidelines, refer to the [Architecture Documentation](docs/ARCHITECTURE.md).

### **LLM Factory Architecture**
```python
# Centralized LLM factory with Groq-only configuration
from kickai.utils.llm_factory import LLMFactory, LLMConfig

# Groq configuration with AI_MODEL_SIMPLE and AI_MODEL_ADVANCED
config = LLMConfig(
    provider=AIProvider.GROQ,
    api_key=os.getenv("GROQ_API_KEY"),
    # Model selection based on use case:
    # - AI_MODEL_SIMPLE: For lightweight agents and tools
    # - AI_MODEL_ADVANCED: For complex reasoning and creative tasks
    # - AI_MODEL_NAME: Legacy fallback
)

# Factory creates Groq instances with model selection
llm = LLMFactory.create_llm(config)

### **Model Configuration System**
The system supports three model configuration approaches:

1. **Dual Model System** (Recommended):
   - `AI_MODEL_SIMPLE`: For lightweight agents and tool execution
   - `AI_MODEL_ADVANCED`: For complex reasoning and creative tasks

2. **Legacy Single Model**:
   - `AI_MODEL_NAME`: Single model for all use cases (backward compatible)

3. **Automatic Model Selection**:
   - Agents automatically get appropriate models based on their role
   - Tool LLMs use simple models for efficiency
   - Creative LLMs use advanced models for better reasoning

### **Environment Variables for AI/LLM Configuration**

#### **Required Variables**
```bash
# AI Provider Selection
AI_PROVIDER=groq                    # Options: groq, gemini, openai, ollama

# API Keys (required based on provider)
GROQ_API_KEY=your_groq_api_key      # Required for Groq provider
GOOGLE_API_KEY=your_gemini_key      # Required for Gemini provider  
OPENAI_API_KEY=your_openai_key      # Required for OpenAI provider

# Model Configuration (at least one required)
AI_MODEL_SIMPLE=llama3-8b-8192      # For lightweight agents and tools
AI_MODEL_ADVANCED=llama3-70b-8192   # For complex reasoning tasks
AI_MODEL_NAME=llama3-8b-8192        # Legacy: single model for all use cases
```

#### **Optional Variables**
```bash
# Ollama Configuration (only if using Ollama provider)
OLLAMA_BASE_URL=http://localhost:11434

# AI Performance Tuning
AI_TEMPERATURE=0.3                  # Default temperature (0.0-1.0)
AI_MAX_TOKENS=800                   # Default max tokens
AI_TIMEOUT=120                      # Request timeout in seconds
```
```

### **LLM Health Monitoring**
- **Startup Validation**: Comprehensive LLM connectivity checks
- **Error Propagation**: Clean error handling without silent failures
- **Factory Design**: Preserved modularity for future provider switching

---

## 🏗️ **Architecture Components**

=======
# Groq-only configuration
config = LLMConfig(
    provider=AIProvider.GROQ,
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("GROQ_MODEL")
)

# Factory creates Groq instances
llm = LLMFactory.create_llm(config)
```

### **LLM Health Monitoring**
- **Startup Validation**: Comprehensive LLM connectivity checks
- **Error Propagation**: Clean error handling without silent failures
- **Factory Design**: Preserved modularity for future provider switching


### **5-Agent CrewAI System**
1. **MESSAGE_PROCESSOR** - Primary interface and routing
2. **HELP_ASSISTANT** - Help system and guidance
3. **PLAYER_COORDINATOR** - Player management and onboarding
4. **TEAM_ADMINISTRATOR** - Team member management
5. **SQUAD_SELECTOR** - Squad selection and match management

### **Enhanced Error Handling System**
- **Centralized Decorators**: `@critical_system_error_handler`, `@user_registration_check_handler`, `@command_registry_error_handler`
- **Fail-Fast Behavior**: Immediate error detection and propagation
- **Consistent Logging**: Standardized critical error messages
- **Code Reduction**: ~67% reduction in error handling code

### **Standardized Dependency Injection**
- **Service-Specific Functions**: `get_player_service()`, `get_team_service()`, etc.
- **Validation Utilities**: `validate_required_services()`
- **Container Monitoring**: `get_container_status()`, `ensure_container_initialized()`
- **Consistent Patterns**: Eliminated mixed dependency injection approaches

---

## 🗄️ **Database and Storage**

### **Firebase Firestore**
- **Primary Database**: Firebase Firestore for all data storage
- **Collections**: `kickai_teams`, `kickai_players`, `kickai_matches`, etc.
- **Client**: `kickai/database/firebase_client.py`
- **Interfaces**: `kickai/database/interfaces.py`

### **Data Models**
- **Pydantic Models**: Type-safe data validation
- **Clean Architecture**: Clear separation between domain and infrastructure
- **Repository Pattern**: Abstracted data access through repositories

---

## 🔧 **Development and Quality Tools**

### **Code Quality**
- **Ruff**: Linting, formatting, and import sorting (10-100x faster than flake8/black/isort)
- **Pre-commit**: Git hooks for automated code quality checks
- **Type Hints**: Comprehensive type annotations throughout codebase
- **Docstrings**: Detailed documentation for all functions and classes

### **Testing Framework**
- **Pytest**: Primary testing framework
- **Test Categories**: Unit, integration, and end-to-end tests
- **Mock Testing**: Custom mock Telegram framework
- **Coverage**: Comprehensive test coverage reporting

### **Logging and Monitoring**
- **Loguru**: Structured logging with emoji and formatting
- **Log Files**: `logs/kickai.log` for application logs
- **Error Tracking**: Centralized error handling with detailed logging
- **Health Checks**: System health monitoring and validation

---

## 📱 **Telegram Integration**

### **python-telegram-bot**
- **Version**: Latest stable version
- **Features**: Webhook and polling support
- **Message Handling**: Unified message processing through agentic system
- **Plain Text**: All messages sent as plain text for compatibility

### **Bot Configuration**
- **Parse Mode**: Plain text only (no Markdown/HTML)
- **Text Sanitization**: Automatic removal of formatting characters
- **Error Handling**: Robust error handling for Telegram API calls
- **Multi-Chat Support**: Main team chat and leadership chat functionality

---

## 🛠️ **Utility Libraries**

### **Core Utilities**
- **`kickai/utils/error_handling.py`**: Centralized error handling decorators
- **`kickai/utils/dependency_utils.py`**: Standardized dependency injection utilities
- **`kickai/utils/tool_validation.py`**: Tool input validation system
- **`kickai/utils/tool_context_helpers.py`**: Tool context access helpers

### **LLM and AI Utilities**
- **`kickai/utils/llm_factory.py`**: LLM provider factory (42KB, 1000 lines)
- **`kickai/utils/llm_intent.py`**: LLM intent processing
- **`kickai/utils/crewai_logging.py`**: CrewAI logging utilities

### **Validation and Security**
- **`kickai/utils/phone_validation.py`**: Phone number validation (15KB, 454 lines)
- **`kickai/utils/security_utils.py`**: Security utilities
- **`kickai/utils/validation_utils.py`**: General validation utilities

### **ID and Data Generation**
- **`kickai/utils/football_id_generator.py`**: Football ID generation (20KB, 641 lines)
- **`kickai/utils/simple_id_generator.py`**: Simple ID generation
- **`kickai/utils/user_id_generator.py`**: User ID generation

---

## 🧪 **Testing Infrastructure**

### **Test Categories**
1. **Unit Tests**: Individual components and functions
2. **Integration Tests**: Component interactions and service integration
3. **End-to-End Tests**: Complete user workflows and system behavior
4. **Mock Testing**: Simulated Telegram interactions

### **Test Frameworks**
- **Pytest**: Primary testing framework
- **Custom E2E Framework**: End-to-end testing with Telegram integration
- **Mock Telegram Framework**: Custom mock testing infrastructure
- **Test Utilities**: Comprehensive test utilities and fixtures

---

## 📦 **Package Management**

### **Dependencies**
- **Production**: `requirements.txt` (Railway deployment)
- **Development**: `requirements-local.txt` (local development)
- **Package Config**: `pyproject.toml` (Ruff, dependencies, project metadata)

### **Virtual Environment**
- **Python Version**: 3.11 (strict version requirement)
- **Environment**: `venv311/` (Python virtual environment)
- **Activation**: `source venv311/bin/activate`

---

## 🚀 **Deployment and Infrastructure**

### **Railway Deployment**
- **Platform**: Railway for production deployment
- **Startup Script**: `run_bot_railway.py`
- **Environment**: Production environment variables
- **Monitoring**: Railway's built-in monitoring and logging

### **Local Development**
- **Startup Script**: `run_bot_local.py`
- **Environment**: Local environment variables
- **Safe Startup**: `start_bot_safe.sh` with validation

### **Environment Configuration**
- **Template**: `env.example` (environment variables template)
- **Validation**: Environment validation on startup
- **Security**: Secure credential management

---

## 🔍 **Monitoring and Observability**

### **Logging Strategy**
- **Structured Logging**: Loguru with emoji and formatting
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Files**: Centralized logging to `logs/kickai.log`
- **Error Tracking**: Comprehensive error logging and tracking

### **Health Monitoring**
- **System Health**: Health check services and monitoring
- **Component Status**: Individual component health monitoring
- **Error Metrics**: Error tracking and metrics collection
- **Performance Monitoring**: System performance monitoring

---

## 🎯 **Technology Stack Benefits**

### **🏆 Key Advantages**
- **Modern Stack**: Latest stable versions of all technologies
- **Performance**: High-performance LLM and database solutions
- **Reliability**: Robust error handling and fail-fast design
- **Scalability**: Modular architecture for easy scaling
- **Maintainability**: Clean code with comprehensive testing

### **🚀 Technical Excellence**
- **Type Safety**: Comprehensive type hints and validation
- **Code Quality**: Automated linting and formatting
- **Testing**: Multi-layer testing with comprehensive coverage
- **Documentation**: Extensive documentation and guides

### **📈 Future-Ready**
- **Modular Design**: Easy to add new technologies
- **Standardized Patterns**: Consistent development approach
- **Comprehensive Testing**: Robust quality assurance
- **Extensive Documentation**: Clear development guidance

---

## 🔧 **Development Guidelines**

### **1. Technology Selection**
- **Always**: Use established, well-maintained technologies
- **Always**: Follow the technology stack for consistency
- **Always**: Use the centralized error handling and DI utilities
- **Never**: Introduce technologies that conflict with existing stack

### **2. Code Quality**
- **Always**: Use Ruff for linting and formatting
- **Always**: Include comprehensive type hints
- **Always**: Write unit tests for new functionality
- **Always**: Follow established patterns and conventions

### **3. Error Handling**
- **Always**: Use centralized error handling decorators
- **Always**: Follow fail-fast principles
- **Always**: Log errors with clear context
- **Never**: Suppress or ignore errors silently

### **4. Dependency Management**
- **Always**: Use standardized dependency injection utilities
- **Always**: Validate service availability
- **Always**: Follow clean architecture principles
- **Never**: Create circular dependencies

The technology stack provides a solid foundation for building robust, scalable, and maintainable systems! 🛠️✨