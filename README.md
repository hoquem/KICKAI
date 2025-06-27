# KICKAI - AI-Powered Sunday League Football Management

An intelligent system for managing Sunday League football teams using AI agents, Telegram integration, and a Supabase backend.

## 🚀 Features

### Core Capabilities
* **🤖 AI-Powered Management**: CrewAI agents handle team operations intelligently
* **📱 Telegram Integration**: Seamless team communication via Telegram Bot API
* **🗄️ Database Management**: Supabase PostgreSQL for reliable data storage
* **👥 Multi-Team Support**: Manage multiple teams with role-based access
* **📊 Interactive Polls**: Real-time availability and decision voting
* **💰 Payment Tracking**: Automated payment reminders and tracking
* **🏆 Squad Selection**: AI-assisted squad selection based on availability

### AI Agents
* **`Team Manager` (The Orchestrator):**
  - High-level team management and coordination
  - Squad selection and tactical decisions
  - Performance analysis and team strategy

* **`Player Coordinator` (The Organizer):**
  - Player registration and profile management
  - Availability tracking and squad compilation
  - Match day logistics and player communication

* **`Communication Specialist` (The Messenger):**
  - Team announcements and updates via Telegram
  - Interactive polls for availability and decisions
  - Automated reminders and notifications

* **`Finance Manager` (The Treasurer):**
  - Payment tracking and reminders
  - Financial reporting and fee management
  - Budget planning and expense tracking

* **`Match Analyst` (The Tactician):**
  - Performance analysis and statistics
  - Opposition research and tactical planning
  - Player ratings and development tracking

## 📋 Feature Matrix

| Feature | Description | Agents Involved | Status |
|---------|-------------|-----------------|---------|
| 📱 Send team announcements (fixtures, time) to the team Telegram group. | `Team Manager`, `Communication Specialist` | ✅ **COMPLETE** |
| 📊 Create availability polls for next game and track player responses. | `Team Manager`, `Player Coordinator`, `Communication Specialist` | ✅ **COMPLETE** |
| 👥 Get current squad list and return a simple list back. | `Team Manager`, `Player Coordinator` | ✅ **COMPLETE** |
| 🏆 Have the system announce the squad to the group. | `Team Manager`, `Communication Specialist` | ✅ **COMPLETE** |
| 💰 Track who has paid match fees and I can mark them as paid. | `Team Manager`, `Player Coordinator` | ✅ **COMPLETE** |
| 🎯 Select squad of 11 starters and 3 subs based on availability. | `Team Manager`, `Player Coordinator`, `Match Analyst` | 🔄 **ENHANCED** |
| 📈 Track player performance and ratings to be stored in the database. | `Player Coordinator` | 🔄 **PLANNED** |
| 💳 Integrate payment system so players can pay my match fees online. | `Finance Manager`, `Communication Specialist` | 📋 **PLANNED** |
| 🔔 Send payment notification with a payment link. | `Finance Manager`, `Communication Specialist` | 📋 **PLANNED** |
| ⭐ Rate players after each match and use performance to generate a team rating. | `Team Manager`, `Player Coordinator`, `Communication Specialist` | 📋 **PLANNED** |
| 🧹 Assign tasks (e.g., "wash the kit") on a rota basis. | `Team Manager`, `Player Coordinator`, `Communication Specialist` | 📋 **PLANNED** |
| ⏰ Send automatic reminder. | `Finance Manager`, `Communication Specialist` | 📋 **PLANNED** |

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd KICKAI
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your credentials
```

### 3. Set up Supabase Database
```bash
# Run the consolidated schema in your Supabase project
# See kickai_schema.sql and kickai_sample_data.sql
```

### 4. Set up Telegram Bot
   ```bash
   # Follow TELEGRAM_SETUP_GUIDE.md
   # 1. Create bot with @BotFather
   # 2. Get bot token
   # 3. Create team group
   # 4. Add bot to group
   # 5. Get group chat ID
   ```

### 5. Test the system
   ```bash
   python test_telegram_features.py
   python test_crewai_ollama_correct.py
   ```

## 📱 Telegram Setup

### 1. Create Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "Your Team Name Team Manager")
4. Choose a username (e.g., "yourteam_bot")
5. Copy the bot token

### 2. Create Team Group
1. Create a new Telegram group
2. Add your bot to the group
3. Make the bot an admin (required for polls)
4. Send a message in the group
5. Get the group chat ID using the API

### 3. Configure Environment
```bash
# Add to your .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_group_chat_id_here
TEAM_NAME=Your Team Name
```

## 🗄️ Database Schema

The system uses a comprehensive multi-team schema with the following tables:

* **`teams`**: Team information and configuration
* **`team_members`**: Team members with roles and permissions
* **`players`**: Player profiles and statistics
* **`fixtures`**: Match schedules and details
* **`availability`**: Player availability for matches
* **`squad_selections`**: Selected squads for matches
* **`ratings`**: Peer-to-peer player ratings
* **`tasks`**: Recurring team tasks and chores
* **`task_assignments`**: Task assignments per fixture
* **`equipment`**: Team equipment inventory
* **`team_bots`**: Telegram bot mappings per team

### Database Setup
1. **Run the schema**: Execute `kickai_schema.sql` in your Supabase SQL Editor
2. **Add sample data**: Execute `kickai_sample_data.sql` for realistic test data
3. **Manage bot mappings**: Use `python manage_team_bots.py` for bot configuration

## 🤖 AI Configuration

### Local Models (Recommended)
The system is configured to use Ollama with local models:

```python
# Uses llama3.1:8b-instruct-q4_0 model
llm = Ollama(model="ollama/llama3.1:8b-instruct-q4_0")
```

### Cloud Models (Alternative)
You can also use cloud-based models by updating the LLM configuration in `src/agents.py`.

## 🧪 Testing

### Run All Tests
```bash
# Test Telegram integration
python test_telegram_features.py

# Test CrewAI with Ollama
python test_crewai_ollama_correct.py

# Test database setup
python test_database_setup.py

# Test team management
python test_team_setup.py
```

### Test Individual Components
```bash
# Test specific features
python demo_telegram_features.py
python test_sample_data.py
```

## 📊 Usage Examples

### Send Team Announcement
```python
from src.tools.telegram_tools import SendTelegramMessageTool

tool = SendTelegramMessageTool()
tool._run("🏆 Squad announcement for Sunday's match!")
```

### Create Availability Poll
```python
from src.tools.telegram_tools import SendAvailabilityPollTool

tool = SendAvailabilityPollTool()
tool._run("vs Thunder FC", "Sunday, July 7th", "2:00 PM", "Central Park")
```

### Get Team Information
```python
from src.tools.team_management_tools import TeamManagementTools

tool = TeamManagementTools()
tool._run("get_team_info", team_id="your-team-id")
```

### Manage Bot Mappings
```bash
# List all bot mappings
python manage_team_bots.py list

# Add a new bot mapping
python manage_team_bots.py add --team "Team Name" --token "bot_token" --chat-id "chat_id" --username "@bot_username"

# Test a bot mapping
python manage_team_bots.py test --team "Team Name"
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional
TEAM_NAME=Your Team Name
```

### Team Configuration
Teams can be configured with:
* Custom team names
* Role-based member management
* Telegram group integration
* Payment settings
* Match preferences

## 🚀 Deployment

### Local Development
```bash
# Run with local Ollama
python src/main.py
```

### Production Deployment
1. Set up Supabase production database
2. Configure production Telegram bot
3. Deploy to your preferred hosting platform
4. Set up monitoring and logging

## 📈 Roadmap

### Phase 1: Core Features ✅
- [x] Basic team management
- [x] Telegram integration
- [x] AI agent system
- [x] Database schema

### Phase 2: Enhanced Features 🔄
- [ ] Payment integration
- [ ] Player ratings
- [ ] Advanced analytics
- [ ] Mobile app

### Phase 3: Advanced Features 📋
- [ ] Multi-league support
- [ ] Tournament management
- [ ] Performance tracking
- [ ] Social features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
1. Check the documentation in the `/docs` folder
2. Review the setup guides
3. Run the test scripts to verify your configuration
4. Open an issue on GitHub

---

**KICKAI** - Making Sunday League football management effortless with AI! ⚽🤖