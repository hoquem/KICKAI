# KICKAI - AI-Powered Football Team Management

**Status:** ✅ **PRODUCTION READY** - v1.7.0  
**Deployment:** 🚀 **Live on Railway**  
**AI Provider:** 🤖 **Google Gemini (Production) / OpenAI**  
**Architecture:** 🏗️ **7-Agent CrewAI System with Unified Interface**

A comprehensive AI-powered football team management system with Telegram bot interface, Firebase backend, and intelligent agent orchestration featuring a refined task execution system.

## 🎉 **Production Status**

KICKAI is **fully operational** in production with **advanced AI capabilities**:
- ✅ **Stable Railway deployment** with health monitoring
- ✅ **Google AI (Gemini) integration** for natural language processing
- ✅ **Firebase Firestore database** with real-time synchronization
- ✅ **7-agent CrewAI system** with unified execution interface
- ✅ **Refined TaskExecutionOrchestrator** with robust agent coordination
- ✅ **Advanced Memory System** with persistent conversation history
- ✅ **Intelligent Routing System** with LLM-powered agent selection
- ✅ **Dynamic Task Decomposition** for complex request handling
- ✅ **Player Registration & Onboarding** with automated workflows
- ✅ **Multi-team Management** with isolated environments
- ✅ **Role-based Access Control** for leadership and members
- ✅ **FA Registration Checking** with automated status updates
- ✅ **Daily Status Reports** with comprehensive team analytics
- ✅ **Human-readable IDs** for teams, players, and matches
- ✅ **Payment System Integration** with Collectiv for match fees and fines
- ✅ **Advanced Onboarding System** with multi-step registration
- ✅ **Unified Command System** with permission-based access control
- ✅ **Comprehensive Testing Suite** with automated test coverage
- ✅ **User Preference Learning** with personalized responses

## 🏗️ **Architecture Overview**

### **Agentic Architecture**
KICKAI uses a sophisticated 7-agent CrewAI system with **unified execution interface**:

1. **Message Processor** - Primary user interface and command parsing
2. **Team Manager** - Strategic coordination and high-level planning
3. **Player Coordinator** - Operational player management and registration
4. **Performance Analyst** - Performance analysis and tactical insights
5. **Finance Manager** - Financial tracking and payment management
6. **Learning Agent** - Continuous learning and system improvement
7. **Onboarding Agent** - Specialized player onboarding and registration

### **Unified Agent Interface**
All agents now use a **standardized `execute()` method** for task execution:
- **Primary Interface**: `agent.execute(description, parameters)` - Unified execution method
- **Fallback Support**: Legacy methods (`execute_task`, `process`, `handle`) for backward compatibility
- **Robust Error Handling**: Comprehensive validation and error reporting
- **Enhanced Logging**: Detailed execution tracking with interface identification

### **Refined TaskExecutionOrchestrator**
The orchestrator now features:
- **Unified Interface Priority**: Primarily uses `agent.execute()` method
- **Intelligent Fallback System**: Graceful handling of legacy agent interfaces
- **Enhanced Metadata Tracking**: Execution interface type and agent type logging
- **Comprehensive Error Handling**: Clear error messages with available methods
- **Performance Monitoring**: Execution time tracking and analytics

### **Code Architecture**
KICKAI follows **Clean Architecture** principles with a **layered, feature-first organization**:

```
src/
├── agents/                 # AI Agent System (Application Layer)
│   ├── crew_agents.py     # 7-agent CrewAI definitions with unified interface
│   ├── intelligent_system.py # Refined TaskExecutionOrchestrator and routing
│   ├── capabilities.py    # Agent capability definitions
│   └── __init__.py        # Agent system initialization
├── core/                  # Core System Components (Infrastructure Layer)
│   ├── improved_config_system.py # Advanced configuration management
│   ├── enhanced_logging.py # Structured logging system
│   └── exceptions.py     # Custom exceptions
├── services/             # Business Logic Layer (Application Layer)
│   ├── player_service.py # Player management service
│   ├── team_service.py   # Team management service
│   ├── fa_registration_checker.py # FA registration checking
│   ├── daily_status_service.py # Daily status reports
│   ├── reminder_service.py # Automated reminder system
│   ├── background_tasks.py # Scheduled operations
│   ├── message_routing_service.py # Message handling
│   └── team_member_service.py # Team membership management
├── tools/                # LangChain Tools (Presentation Layer)
│   └── __init__.py       # Tools package initialization
├── telegram/             # Telegram Integration (Presentation Layer)
│   ├── unified_command_system.py # Unified command architecture
│   ├── player_registration_handler.py # Advanced player onboarding
│   └── unified_message_handler.py # Message processing and routing
├── tasks/                # Task Definitions (Application Layer)
│   ├── tasks.py         # CrewAI task definitions
│   └── task_templates.py # Task templates
├── database/             # Database Layer (Infrastructure Layer)
│   ├── firebase_client.py # Firebase client
│   └── models_improved.py # Improved data models
├── utils/                # Utilities (Infrastructure Layer)
│   └── id_generator.py   # Human-readable ID generation
└── testing/              # Testing Infrastructure
    └── __init__.py       # Test package
```

### **Architectural Principles**
- **Clean Architecture**: Layered dependencies with clear separation of concerns
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Interface Segregation**: Services depend on interfaces, not implementations
- **Single Responsibility**: Each module has one clear purpose
- **Feature-First Organization**: Related functionality grouped together
- **Unified Interface**: Standardized agent execution interface across all agents

📖 **For detailed architectural rules and dependency guidelines, see [ARCHITECTURE.md](ARCHITECTURE.md)**

### **Technology Stack**
- **AI Engine**: CrewAI with Google Gemini/OpenAI
- **Database**: Firebase Firestore with real-time sync
- **Bot Platform**: Telegram Bot API
- **Payment Processing**: Collectiv API integration
- **Deployment**: Railway with Docker
- **Testing**: pytest with comprehensive test suite
- **Monitoring**: Custom health checks and structured logging
- **Configuration**: Advanced config system with design patterns

## 🚀 **Quick Deploy to Railway**

### 1. Environment Variables

Set these in your Railway project:

**Firebase Service Account:**
```
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-id",...}  # REQUIRED: Must be a JSON string with all service account fields. No base64 or other formats are supported.
```

**AI Provider:**
```
GOOGLE_API_KEY=your_google_api_key_here
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro
```

**Telegram Bot:**
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
MAIN_CHAT_ID=your_main_chat_id
LEADERSHIP_CHAT_ID=your_leadership_chat_id
```

**Payment System (Optional):**
```
COLLECTIV_API_KEY=your_collectiv_api_key
COLLECTIV_BASE_URL=https://api.collectiv.com
PAYMENT_ENABLED=true
```

**Environment:**
```
ENVIRONMENT=production
```

### 2. Deploy

1. Connect Railway to this GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main

### 3. Test

Send "help" to your Telegram bot to verify it's working.

## 🏗️ **Local Development**

### Prerequisites
- Python 3.11+
- Firebase project with service account
- Google AI API key or OpenAI API key

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/KICKAI.git
cd KICKAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (SECURE - uses system environment variables)
python setup_local_environment.py
# Follow the prompts and set the generated environment variables

# Run tests
pytest tests/

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_integration/

# Start development server
PYTHONPATH=src python run_telegram_bot.py
```

**🔒 Security Note**: This setup uses system environment variables instead of `.env` files to keep secrets out of source control. See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed instructions.

### Development Workflow
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_integration/

# Check code quality
flake8 src/
mypy src/

# Deploy to Railway
railway up
```

## 🆕 **Latest Features (v1.7.0)**

### **Refined TaskExecutionOrchestrator**
- **Unified Interface**: All agents now use standardized `execute()` method
- **Intelligent Fallbacks**: Robust fallback system for legacy agent interfaces
- **Enhanced Logging**: Detailed execution tracking with interface identification
- **Performance Monitoring**: Execution time tracking and analytics
- **Error Handling**: Comprehensive error reporting with available methods

### **User Preference Learning System**
- **Persistent Storage**: In-memory storage with JSON persistence and backups
- **Learning from Interactions**: System learns from user interactions and preferences
- **Personalized Responses**: Tailored responses based on learned preferences
- **Communication Style Adaptation**: Formal, casual, concise, or detailed responses
- **Skill Level Tracking**: Adaptive responses based on user expertise

### **Enhanced Agent System**
- **Memory-Enhanced Agents**: Agents with pattern learning and memory capabilities
- **Dynamic Task Decomposition**: LLM-powered task breakdown with recursion limits
- **Capability-Based Routing**: Intelligent agent selection based on capabilities
- **Load Balancing**: Agent load management and availability tracking
- **Analytics Integration**: Comprehensive execution analytics and performance metrics

### **Payment System Integration**
- **Collectiv API Integration**: Complete payment processing system
- **Match Fees**: Automated match fee creation and tracking
- **Membership Fees**: Subscription and membership fee management
- **Fines System**: Automated fine creation and payment tracking
- **Payment History**: Comprehensive payment records and analytics
- **Payment Statistics**: Detailed financial reporting

### **Advanced Onboarding System**
- **Multi-step Registration**: Guided player onboarding process
- **Natural Language Processing**: Conversational registration flow
- **Progress Tracking**: Real-time onboarding progress monitoring
- **Automated Reminders**: Smart reminder system for incomplete registrations
- **FA Registration Integration**: Automated FA status checking

### **Unified Command System**
- **Permission-based Access**: Role-based command access control
- **Design Pattern Implementation**: Clean, maintainable command architecture
- **Comprehensive Command Set**: 20+ commands for all team management needs
- **Error Handling**: Robust error handling and user feedback
- **Command Logging**: Detailed command execution logging

### **Enhanced Configuration System**
- **Design Patterns**: Strategy, Factory, Builder, Observer patterns
- **Multiple Sources**: Environment, file, database configuration
- **Validation Chain**: Comprehensive configuration validation
- **Hot Reloading**: Dynamic configuration updates
- **Environment Detection**: Automatic environment configuration

### **Improved Data Models**
- **OOP Principles**: Clean, maintainable data models
- **Validation**: Comprehensive input validation
- **Factory Methods**: Easy object creation
- **Type Safety**: Full type annotations
- **Serialization**: Efficient data serialization

## 📚 **Documentation**

### **Core Documentation**
- [CODEBASE_INDEX.md](CODEBASE_INDEX.md) - Comprehensive codebase overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design principles
- [E2E_TESTING_GUIDE.md](E2E_TESTING_GUIDE.md) - End-to-end testing guide

### **Development Documentation**
- [CODE_HYGIENE.md](CODE_HYGIENE.md) - Code quality and hygiene guidelines
- [LOGGING_GUIDE.md](LOGGING_GUIDE.md) - Logging standards and practices

## 🛠️ **Development Setup**

### **Environment Configuration**
```bash
# Set up environment variables securely
python setup_local_environment.py

# Key settings for local development:
export AI_PROVIDER=google_gemini
export AI_MODEL_NAME=gemini-pro
export ENVIRONMENT=development
```

**📚 See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for comprehensive setup instructions.**

### **Model Performance**
- **Response Time**: ~2-5 seconds for typical queries
- **Memory Usage**: ~8GB RAM during inference
- **Quality**: Excellent for development and testing
- **Context Length**: 8K tokens (sufficient for most tasks)

## 🔧 **Core Features**

### **AI-Powered Natural Language Processing**
- Understand complex commands like "Create a match against Arsenal on July 1st at 2pm"
- Intelligent agent selection based on request type
- Context-aware responses with conversation memory
- Multi-agent coordination for complex tasks
- **Unified execution interface** for all agents

### **Player Management System**
- **Registration**: Automated player onboarding with invite links
- **Profiles**: Comprehensive player profiles with FA registration status
- **Onboarding**: AI-guided onboarding process with status tracking
- **Leadership Commands**: Admin tools for player management
- **Human-readable IDs**: Player IDs like "JS1" for John Smith
- **FA Registration**: Automated checking of FA registration status
- **Daily Status**: Comprehensive team analytics and reports

### **Match & Fixture Management**
- **Smart ID Generation**: Human-readable match IDs (e.g., BP-ARS-2024-07-01)
- **Date Parsing**: Natural language date interpretation
- **Venue Management**: Match location tracking
- **Squad Selection**: AI-assisted squad selection based on availability

### **Team Management**
- **Multi-team Support**: Isolated environments for multiple teams
- **Role-based Access**: Different permissions for admins and members
- **Communication Tools**: Polls, announcements, and messaging
- **Financial Tracking**: Payment reminders and financial management
- **Human-readable IDs**: Team IDs like "BH" for BP Hatters FC

### **Advanced AI Capabilities**
- **Intelligent Routing**: LLM-powered request routing to appropriate agents
- **Dynamic Task Decomposition**: Complex requests broken into manageable tasks
- **Memory System**: Persistent conversation history and context
- **Performance Analytics**: AI-driven insights and recommendations
- **Unified Agent Interface**: Standardized execution across all agents
- **User Preference Learning**: Personalized responses based on interaction history

## 📝 **Commands & Usage**

### **Player Commands**
- `/myinfo` - View your player profile
- `/start` - Start player registration process

### **Leadership Commands**
- `/add <name> <phone> <position>` - Add a new player to the team
- `/remove <phone>` - Remove a player from the team
- `/list` - List all team players
- `/status <phone>` - Check player onboarding status
- `/invite <phone_or_player_id>` - Generate player invite link
- `/approve <player_id>` - Approve a player registration
- `/reject <player_id> [reason]` - Reject a player registration
- `/pending` - List players pending approval
- `/checkfa` - Check FA registration status for all players
- `/dailystatus` - Generate daily team status report

### **Team Commands**
- `/teams` - List all teams
- `/players` - List players for a team
- `/matches` - List upcoming matches
- `/creatematch` - Create a new match
- `/squad` - View current squad

### **General Commands**
- `/help` - Show available commands
- `/status` - Check system status
- `/memory` - View conversation memory

### **Natural Language Commands**
- "Add player John Smith with phone 07123456789 as midfielder"
- "List all players"
- "Show player with phone 07123456789"
- "Create a match against Arsenal on July 1st at 2pm"
- "Check FA registration status"
- "Generate daily status report"

## 🔧 **Code Quality & Architecture**

### **Architectural Enforcement**
KICKAI enforces strict architectural and code quality standards:

- **Clean Architecture**: Layered dependencies with clear separation of concerns
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Interface Segregation**: Services depend on interfaces, not implementations
- **Single Responsibility**: Each module has one clear purpose
- **Feature-First Organization**: Related functionality grouped together
- **Unified Interface**: Standardized agent execution interface across all agents

### **Quality Tools & Scripts**
```bash
# Run architectural checks
python scripts/check_architectural_imports.py
python scripts/check_circular_imports.py
python scripts/check_in_function_imports.py

# Run all quality checks
pre-commit run --all-files

# Format code
black src/
isort src/

# Type checking
mypy src/

# Security scanning
bandit -r src/
```

### **Development Scripts**
- `scripts/check_architectural_imports.py` - Enforces dependency hierarchy
- `scripts/check_circular_imports.py` - Detects circular dependencies
- `scripts/check_in_function_imports.py` - Identifies problematic imports
- `scripts/check_test_coverage.py` - Ensures adequate test coverage

📖 **For detailed architectural rules and quality guidelines, see [ARCHITECTURE.md](ARCHITECTURE.md) and [scripts/README.md](scripts/README.md)**

## 🧪 **Testing**

### **Test Coverage**
- Unit tests for all core components
- Integration tests for agent interactions
- End-to-end tests for complete workflows
- Performance tests for system optimization

### **Running Tests**
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_integration/
pytest tests/test_services/

# Run with coverage
pytest --cov=src tests/

# Check test coverage
python scripts/check_test_coverage.py

# Run end-to-end tests
PYTHONPATH=src python run_e2e_tests.py --suite smoke
PYTHONPATH=src python run_e2e_tests.py --suite comprehensive
```

## 📊 **Monitoring & Health**

### **Health Checks**
- Real-time monitoring with structured logging
- Performance metrics and error tracking
- Automated alerting for system issues

### **Logging**
- Structured logging with correlation IDs
- Performance timing for all operations
- Error tracking with full stack traces
- Environment-aware log levels

## 🔒 **Security**

### **Access Control**
- Role-based permissions (Leadership vs Members)
- Team isolation for multi-team environments
- Secure API key management
- Environment variable protection

### **Data Protection**
- Firebase security rules
- Encrypted communication
- Secure credential storage
- Audit logging for all operations

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

For support and questions:
- Check the [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review the [E2E_TESTING_GUIDE.md](E2E_TESTING_GUIDE.md) for testing
- Open an issue on GitHub

## Multi-Team Support and Dynamic Team ID Resolution

KICKAI now supports multiple teams (multi-tenancy) with dynamic team ID resolution for every incoming message. This ensures that all commands, onboarding, and role checks are scoped to the correct team, based on the context of the message.

### How Team ID is Determined
The system uses the following strategies (in order of priority):
1. **Bot Token**: If you run multiple bots, each with its own token, each can map to a different team.
2. **Bot Username**: Useful if you have multiple bots with different usernames.
3. **Chat ID**: If each team has its own group chat(s), the chat ID is mapped to a team.
4. **User Context**: (Future) If users can belong to multiple teams, this can be extended to query the database.
5. **Default Team ID**: Fallback if no mapping is found.

### Environment Variables
- `DEFAULT_TEAM_ID`: The fallback team ID (required for single-team setups).
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`: Used for mapping the bot to a team.
- `TELEGRAM_MAIN_CHAT_ID`, `TELEGRAM_LEADERSHIP_CHAT_ID`: Used for mapping chats to a team.
- `TEAM_MAPPINGS`: (Optional, advanced) JSON string for multiple teams. Example:
  ```json
  {
    "team1-id": {"bot_token": "token1", "bot_username": "bot1", "chat_ids": ["-100123", "-100124"]},
    "team2-id": {"bot_token": "token2", "bot_username": "bot2", "chat_ids": ["-100125"]}
  }
  ```

### How to Add More Teams
1. Add each team's bot token, username, and chat IDs to the `TEAM_MAPPINGS` JSON.
2. Set `DEFAULT_TEAM_ID` to the fallback team.
3. Restart the bot.

### Migration Guide
- Remove all hardcoded `team_id` values from your code.
- Use the new team mapping service for all team lookups.
- The system will log all loaded team mappings on startup for verification.

---

**KICKAI v1.7.0** - AI-Powered Football Team Management System with Unified Agent Interface

# KICKAI Telegram Bot

## Running the Bot

**Always run scripts from the project root with `PYTHONPATH=src`.**

Example:

```
PYTHONPATH=src python run_telegram_bot.py
```

This is required for all scripts at the project root to ensure imports work correctly. 