# KICKAI - AI-Powered Football Team Management

**Status:** ✅ **PRODUCTION READY** - v1.6.0  
**Deployment:** 🚀 **Live on Railway**  
**AI Provider:** 🤖 **Google Gemini (Production)**  
**Architecture:** 🏗️ **10-Agent CrewAI System**

A comprehensive AI-powered football team management system with Telegram bot interface, Firebase backend, and intelligent agent orchestration.

## 🎉 **Production Status**

KICKAI is **fully operational** in production with **advanced AI capabilities**:
- ✅ **Stable Railway deployment** with health monitoring
- ✅ **Google AI (Gemini) integration** for natural language processing
- ✅ **Firebase Firestore database** with real-time synchronization
- ✅ **10-agent CrewAI system** for intelligent task processing
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

## 🏗️ **Architecture Overview**

### **Agentic Architecture**
KICKAI uses a sophisticated 10-agent CrewAI system:

1. **Message Processing Specialist** - Primary user interface and command parsing
2. **Team Manager** - Strategic coordination and high-level planning
3. **Player Coordinator** - Operational player management and registration
4. **Match Analyst** - Tactical analysis and match planning
5. **Communication Specialist** - Broadcast management and team communications
6. **Finance Manager** - Financial tracking and payment management
7. **Squad Selection Specialist** - Optimal squad selection based on availability
8. **Analytics Specialist** - Performance analytics and insights
9. **Learning Agent** - Continuous learning and system improvement
10. **Onboarding Agent** - Specialized player onboarding and registration

### **Code Architecture**
```
src/
├── agents/                 # AI Agent System
│   ├── crew_agents.py     # 10-agent CrewAI definitions
│   ├── capabilities.py    # Agent capability definitions
│   └── __init__.py        # Agent system initialization
├── core/                  # Core System Components
│   ├── improved_config_system.py # Advanced configuration management
│   └── exceptions.py     # Custom exceptions
├── services/             # Business Logic Layer
│   ├── player_service.py # Player management service
│   ├── team_service.py   # Team management service
│   ├── fa_registration_checker.py # FA registration checking
│   ├── daily_status_service.py # Daily status reports
│   ├── reminder_service.py # Automated reminder system
│   ├── background_tasks.py # Scheduled operations
│   ├── message_routing_service.py # Message handling
│   └── team_member_service.py # Team membership management
├── tools/                # LangChain Tools
│   └── __init__.py       # Tools package initialization
├── telegram/             # Telegram Integration
│   ├── unified_command_system.py # Unified command architecture
│   ├── player_registration_handler.py # Advanced player onboarding
│   └── unified_message_handler.py # Message processing and routing
├── tasks/                # Task Definitions
│   ├── tasks.py         # CrewAI task definitions
│   └── task_templates.py # Task templates
├── database/             # Database Layer
│   ├── firebase_client.py # Firebase client
│   └── models_improved.py # Improved data models
├── utils/                # Utilities
│   └── id_generator.py   # Human-readable ID generation
└── testing/              # Testing Infrastructure
    └── __init__.py       # Test package
```

### **Technology Stack**
- **AI Engine**: CrewAI with Google Gemini/OpenAI/Ollama
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
- Google AI API key (or Ollama for local development)

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/KICKAI.git
cd KICKAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-local.txt

# Set up Firebase credentials
python setup_credentials.py
# Follow the prompts to set up your Firebase credentials

# Install and start Ollama (for local development)
# Download from https://ollama.ai
ollama serve  # Start Ollama service
ollama pull llama3.1:8b-instruct-q4_0  # Download the model

# Test Ollama setup
python test_ollama_setup.py

# Set up environment variables
cp env.local.example .env
# Edit .env with your configuration

# Run tests
pytest tests/

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_integration/

# Start development server
python run_telegram_bot.py
```

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

### Local Development with Ollama

For local development, KICKAI uses **Ollama** with **Llama 3.1 8B Instruct** for fast, efficient AI processing:

#### **Why Ollama for Local Development?**
- **Fast**: Local inference with no API latency
- **Efficient**: 4.7GB model size, perfect for development
- **Private**: No data sent to external APIs
- **Cost-effective**: No API costs during development
- **Reliable**: No internet dependency for AI features

#### **Ollama Setup**
```bash

## 🆕 **Latest Features (v1.6.0)**

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
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current project status and roadmap
- [ENVIRONMENT_VARIABLES_GUIDE.md](ENVIRONMENT_VARIABLES_GUIDE.md) - Environment setup guide

### **Feature Documentation**
- [PLAYER_ONBOARDING_PRD.md](PLAYER_ONBOARDING_PRD.md) - Player onboarding system
- [COLLECTIV_PAYMENT_SYSTEM_PRD.md](COLLECTIV_PAYMENT_SYSTEM_PRD.md) - Payment system documentation
- [COMMANDS_PRD.md](COMMANDS_PRD.md) - Command system documentation
- [TEAM_MANAGEMENT_PRD.md](TEAM_MANAGEMENT_PRD.md) - Team management features

### **Development Documentation**
- [BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md) - Git workflow guidelines
- [CI_CD_CONFIGURATION_GUIDE.md](CI_CD_CONFIGURATION_GUIDE.md) - CI/CD setup
- [DEPLOYMENT_PIPELINE_GUIDE.md](DEPLOYMENT_PIPELINE_GUIDE.md) - Deployment process
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Security guidelines

### **Setup Guides**
- [FIREBASE_PROJECTS_SETUP.md](FIREBASE_PROJECTS_SETUP.md) - Firebase configuration
- [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md) - Telegram bot setup
- [IMPROVED_CONFIGURATION_SYSTEM.md](IMPROVED_CONFIGURATION_SYSTEM.md) - Configuration system

## 🛠️ **Development Setup**

### **Install Ollama**
# Download from https://ollama.ai

# Start Ollama service
ollama serve

# Download the required model
ollama pull llama3.1:8b-instruct-q4_0

# Test the setup
python test_ollama_setup.py
```

#### **Environment Configuration**
```bash
# Copy local development config
cp env.local.example .env

# Key settings for local development:
AI_PROVIDER=ollama
AI_MODEL_NAME=llama3.1:8b-instruct-q4_0
ENVIRONMENT=development
```

#### **Model Performance**
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
- Check the [BOT_CONFIGURATION_GUIDE.md](BOT_CONFIGURATION_GUIDE.md)
- Review the [ENVIRONMENT_VARIABLES_GUIDE.md](ENVIRONMENT_VARIABLES_GUIDE.md)
- Check the [DEPLOYMENT_PIPELINE_GUIDE.md](DEPLOYMENT_PIPELINE_GUIDE.md)
- Open an issue on GitHub

---

**KICKAI v1.6.0** - AI-Powered Football Team Management System 