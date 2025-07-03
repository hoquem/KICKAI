# KICKAI - AI-Powered Football Team Management

**Status:** ✅ **PRODUCTION READY** - v1.5.0  
**Deployment:** 🚀 **Live on Railway**  
**AI Provider:** 🤖 **Google Gemini (Production)**  
**Architecture:** 🏗️ **8-Agent CrewAI System**

A comprehensive AI-powered football team management system with Telegram bot interface, Firebase backend, and intelligent agent orchestration.

## 🎉 **Production Status**

KICKAI is **fully operational** in production with **advanced AI capabilities**:
- ✅ **Stable Railway deployment** with health monitoring
- ✅ **Google AI (Gemini) integration** for natural language processing
- ✅ **Firebase Firestore database** with real-time synchronization
- ✅ **8-agent CrewAI system** for intelligent task processing
- ✅ **Advanced Memory System** with persistent conversation history
- ✅ **Intelligent Routing System** with LLM-powered agent selection
- ✅ **Dynamic Task Decomposition** for complex request handling
- ✅ **Player Registration & Onboarding** with automated workflows
- ✅ **Multi-team Management** with isolated environments
- ✅ **Role-based Access Control** for leadership and members
- ✅ **Comprehensive Testing Infrastructure** with pytest
- ✅ **Human-readable IDs** for teams, players, and matches

## 🏗️ **Architecture Overview**

### **Agentic Architecture**
KICKAI uses a sophisticated 8-agent CrewAI system:

1. **Message Processing Specialist** - Primary user interface and command parsing
2. **Team Manager** - Strategic coordination and high-level planning
3. **Player Coordinator** - Operational player management and registration
4. **Match Analyst** - Tactical analysis and match planning
5. **Communication Specialist** - Broadcast management and team communications
6. **Finance Manager** - Financial tracking and payment management
7. **Squad Selection Specialist** - Optimal squad selection based on availability
8. **Analytics Specialist** - Performance analytics and insights

### **Code Architecture**
```
src/
├── agents/                 # AI Agent System
│   ├── crew_agents.py     # 8-agent CrewAI definitions
│   ├── handlers.py        # SimpleAgenticHandler for message processing
│   ├── routing.py         # Intelligent request routing
│   └── capabilities.py    # Agent capability definitions
├── core/                  # Core System Components
│   ├── config.py         # Configuration management
│   ├── advanced_memory.py # Persistent memory system
│   ├── logging.py        # Structured logging
│   └── exceptions.py     # Custom exceptions
├── services/             # Business Logic Layer
│   ├── player_service.py # Player management service
│   ├── team_service.py   # Team management service
│   └── monitoring.py     # System monitoring
├── tools/                # LangChain Tools
│   ├── firebase_tools.py # Database operations
│   ├── telegram_tools.py # Telegram integration
│   └── team_management_tools.py # Team-specific operations
├── telegram/             # Telegram Integration
│   ├── telegram_command_handler.py # Command processing
│   └── player_registration_handler.py # Player onboarding
├── tasks/                # Task Definitions
│   ├── tasks.py         # CrewAI task definitions
│   └── task_templates.py # Task templates
├── database/             # Database Layer
│   ├── firebase_client.py # Firebase client
│   └── models.py         # Data models
├── utils/                # Utilities
│   ├── id_generator.py   # Human-readable ID generation
│   └── match_id_generator.py # Match ID generation
└── testing/              # Testing Infrastructure
    └── __init__.py       # Test package
```

### **Technology Stack**
- **AI Engine**: CrewAI with Google Gemini/OpenAI/Ollama
- **Database**: Firebase Firestore with real-time sync
- **Bot Platform**: Telegram Bot API
- **Deployment**: Railway with Docker
- **Testing**: pytest with comprehensive test suite
- **Monitoring**: Custom health checks and structured logging

## 🚀 **Quick Deploy to Railway**

### 1. Environment Variables

Set these in your Railway project:

**Firebase Service Account:**
```
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-id",...}
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

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Run tests
pytest tests/

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
- `/register` - Start player registration process
- `/profile` - View your player profile
- `/status` - Check your onboarding status

### **Leadership Commands**
- `/addplayer` - Add a new player to the team
- `/removeplayer` - Remove a player from the team
- `/listplayers` - List all team players
- `/playerstatus` - Check player onboarding status
- `/generateinvite` - Generate player invite link

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

## 🧪 **Testing**

### **Mock Data Generation**
```bash
# Generate mock data for testing
python railway_mock_data.py  # For Railway environment
python generate_mock_data.py  # For local environment
```

### **Test Coverage**
- Unit tests for all core components
- Integration tests for agent interactions
- End-to-end tests for complete workflows
- Performance tests for system optimization

## 📊 **Monitoring & Health**

### **Health Checks**
- `/health` - System health endpoint
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

**KICKAI v1.5.0** - AI-Powered Football Team Management System 