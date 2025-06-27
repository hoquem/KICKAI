# Project KICKAI: System Design & Feature Roadmap

## 1. Overview

**Project KICKAI** is an AI-powered management system for a Sunday League football team. It uses a CrewAI agent workforce to automate administrative and logistical tasks, a Supabase backend for data persistence, and **Telegram** for easy interaction with players and managers.

## 2. System Architecture

The system is composed of five primary components:

1.  **User Interface (Telegram):** ✅ **COMPLETE** - Players and managers interact via Telegram using Bot API
2.  **API Bridge (Telegram Bot API):** ✅ **COMPLETE** - Direct integration with Telegram Bot API for messaging
3.  **Backend Logic (CrewAI):** ✅ **ENHANCED** - Five specialized agents with improved reasoning and tool handling
4.  **Database & Storage (Supabase):** ✅ **COMPLETE** - PostgreSQL database with all required tables and relationships
5.  **Payment Gateway (Stripe):** 🔄 **PLANNED** - To handle online payments for match fees and fines securely

![System Architecture Diagram](https://placehold.co/800x450/1e293b/ffffff?text=Telegram+%3C-%3E+Bot+API+%3C-%3E+CrewAI+%3C-%3E+Supabase%0A%5E%0A%7C%0Av%0AStripe)

---

## 3. Telegram Integration

### 🚀 **Why Telegram for Team Management?**
- **✅ Instant Setup**: No approval process, create bot in 5 minutes
- **✅ Group Support**: Full group messaging from day one
- **✅ Interactive Polls**: Native poll support with real-time voting
- **✅ Rich Formatting**: HTML support for professional messages
- **✅ Bot Commands**: Interactive commands like `/availability`, `/squad`
- **✅ No Costs**: Completely free messaging
- **✅ Better Privacy**: More control over data and settings
- **✅ Cross-platform**: Works on all devices

---

## 4. CrewAI Agent Definitions

The system uses five specialized agents with enhanced reasoning capabilities:

* **`Team Manager` (The Orchestrator):**
    * **Goal:** Oversee all team management tasks.
    * **Function:** Interprets high-level commands and delegates tasks to the appropriate specialist agents.
    * **Status:** ✅ **ENHANCED** - Improved reasoning and tool handling

* **`Player Coordinator` (The Numbers Guy):**
    * **Goal:** Manage all data-related tasks concerning players and matches.
    * **Function:** Interacts directly with the Supabase database for player and fixture data.
    * **Tools:** `add_player`, `get_all_players`, `get_player`, `update_player`, `deactivate_player`, `add_fixture`, `get_fixtures`, `get_fixture`, `update_fixture`
    * **Status:** ✅ **ENHANCED** - Comprehensive tool set with better error handling

* **`Communication Specialist` (The Town Crier):**
    * **Goal:** Handle all outgoing communications to the team's Telegram group.
    * **Function:** Crafts and sends messages, polls, and announcements.
    * **Tools:** `send_telegram_message`, `send_telegram_poll`, `send_availability_poll`, `send_squad_announcement`, `send_payment_reminder`
    * **Status:** ✅ **ENHANCED** - Full Telegram integration with 5 message types

* **`Match Analyst` (The Coach):**
    * **Goal:** Assist with squad selection and tactical decisions.
    * **Function:** Analyzes player availability and suggests optimal squad selections.
    * **Tools:** Player and fixture management tools
    * **Status:** ✅ **ENHANCED** - Improved reasoning for squad selection

* **`Finance Manager` (The Treasurer):**
    * **Goal:** Manage all team finances and payment tracking.
    * **Function:** Handles match fees, fines, and payment reminders.
    * **Tools:** Payment tracking tools, `send_payment_reminder`
    * **Status:** ✅ **ENHANCED** - Telegram payment reminders integrated

---

## 5. Feature Roadmap

### Phase 1: MVP - Core Logistics ✅ **COMPLETE**

The goal of the MVP is to solve the most immediate and repetitive problem: getting a team out on a Sunday.

| Feature ID  | Feature Name                  | User Story                                                                                                | Agents Involved                                     | Status      |
| :---------- | :---------------------------- | :-------------------------------------------------------------------------------------------------------- | :-------------------------------------------------- | :---------- |
| **KAI-001** | Player Registration           | As a manager, I can add a new player with their name and phone number to the Supabase database.           | `Player Coordinator`                              | ✅ **COMPLETE** |
| **KAI-002** | Announce New Fixture          | As a manager, I can announce the next match details (opponent, location, time) to the team Telegram group.  | `Team Manager`, `Communication Specialist`                           | ✅ **COMPLETE** |
| **KAI-003** | Availability Polling          | As a manager, I want to automatically send a "You in?" message for the next game and track player responses. | `Team Manager`, `Player Coordinator`, `Communication Specialist`   | ✅ **COMPLETE** |
| **KAI-004** | View Availability List        | As a manager, I can ask the system "Who is available this week?" and get a simple list back.                | `Team Manager`, `Player Coordinator`                   | ✅ **COMPLETE** |
| **KAI-005** | Announce Squad                | As a manager, I can provide a list of selected players and have the system announce the squad to the group. | `Team Manager`, `Communication Specialist`                           | ✅ **COMPLETE** |
| **KAI-006** | Match Fee Tracking (Manual)   | As a manager, I want the system to know who played and needs to pay, and I can mark them as paid.         | `Team Manager`, `Player Coordinator`                   | ✅ **COMPLETE** |

### Phase 2: V2 Enhancements 🔄 **IN PROGRESS**

| Feature ID  | Feature Name                | User Story                                                                                              | Agents Involved                                                     | Status      |
| :---------- | :-------------------------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------ | :---------- |
| **KAI-007** | Automated Squad Selection   | As a manager, I want the system to suggest a squad of 11 starters and 3 subs based on availability.     | `Team Manager`, `Player Coordinator`, `Match Analyst` | 🔄 **ENHANCED** |
| **KAI-010** | Basic Stat Tracking         | As a manager, I can record goals and assists for players after a match to be stored in the database.      | `Team Manager`, `Player Coordinator`                                   | 🔄 **PLANNED** |

### Phase 3: Advanced Management & Engagement 📋 **PLANNED**

| Feature ID  | Feature Name                | User Story                                                                                              | Agents Involved                                           | Status      |
| :---------- | :-------------------------- | :------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------- | :---------- |
| **KAI-012** | Online Payments (Fees)      | As a player, I want to receive a Telegram message with a link to pay my match fees online.                | `Team Manager`, `Finance Manager`, `Communication Specialist`                    | 📋 **PLANNED** |
| **KAI-013** | Online Payments (Fines)     | As a manager, I can issue a fine to a player, and they will receive a notification with a payment link.   | `Team Manager`, `Finance Manager`, `Communication Specialist`                    | 📋 **PLANNED** |
| **KAI-014** | Peer-to-Peer Ratings        | After a match, I want players to be prompted to rate each other's performance to generate a team rating.    | `Team Manager`, `Player Coordinator`, `Communication Specialist`                    | 📋 **PLANNED** |
| **KAI-015** | Player Leaderboard          | As a player, I can request the "leaderboard" and see top players for goals, assists, and attendance.      | `Player Coordinator`, `Communication Specialist`                               | 📋 **PLANNED** |
| **KAI-016** | Task Delegation             | As a manager, I want the system to automatically assign weekly chores (e.g., "wash the kit") on a rota basis. | `Team Manager`, `Player Coordinator`, `Communication Specialist`                    | 📋 **PLANNED** |
| **KAI-017** | Automated Reminders         | I want players who haven't paid fees/fines by Tuesday to get an automatic reminder.                         | `Team Manager`, `Finance Manager`, `Communication Specialist`                    | 📋 **PLANNED** |

---

## 6. Current Implementation Status

### ✅ Completed Features
- **Supabase Database Schema**: All tables (players, fixtures, availability, ratings, tasks, equipment) implemented with relationships
- **CrewAI Framework**: ✅ **ENHANCED** - Five agents with improved system prompt and better tool handling
- **Telegram Integration**: ✅ **COMPLETE** - Bot API integration with 5 message types
- **Player Management**: Complete CRUD operations for players via Supabase
- **Fixture Management**: Complete fixture operations with availability tracking
- **Sample Data**: 14 players, 3 fixtures, availability, squad, and payment data loaded
- **Task Framework**: Player, fixture, availability, team management, and communication tasks implemented
- **Error Handling**: Comprehensive validation and error handling
- **Environment Configuration**: All required environment variables validated
- **Local Model Support**: ✅ **COMPLETE** - Works with Ollama (llama3.1:8b-instruct-q4_0)

### 🔄 In Progress
- **Enhanced Reasoning**: Further improvements to agent reasoning and tool usage
- **Advanced Features**: Automated squad selection, statistics, ratings, leaderboards

### ❌ Not Yet Implemented
- **Stripe Integration**: Payment processing for online payments
- **API Bridge**: FastAPI/Flask web service for webhooks (if needed)
- **Advanced Analytics**: Detailed player statistics and performance tracking

---

## 7. Recent System Enhancements ✅ **LATEST**

### Telegram Integration
- **Telegram Bot API**: Complete integration with interactive features
- **Interactive Polls**: Native Telegram polls with real-time voting
- **Rich Formatting**: HTML support for professional messages
- **Bot Commands**: Interactive commands for team management
- **Group Support**: Full group messaging from day one
- **No Costs**: Completely free messaging
- **Instant Setup**: No approval process required

### CrewAI System Improvements
- **Enhanced System Prompt**: Comprehensive tool cheat sheet with all valid commands
- **Improved Tool Handling**: Explicit examples of valid and invalid tool usage
- **Reduced Invalid Tool Calls**: Strong instructions to only use listed commands
- **Better Reasoning**: More structured examples for different tool types
- **Local Model Support**: Confirmed Ollama integration works with correct model format
- **Robust Error Handling**: Detailed logging and fallback mechanisms

### Messaging Integration Features
- **Basic Team Announcements**: Send general messages to the team
- **Interactive Polls**: Create polls for team decisions with real-time voting
- **Availability Polls**: Structured availability checks with match details
- **Squad Announcements**: Complete squad lists with starters and substitutes
- **Payment Reminders**: Automated payment tracking and reminders

### Database and Tools
- **Complete CRUD Operations**: All player and fixture management tools
- **Availability Tracking**: Comprehensive availability and squad management
- **Payment Tracking**: Match fee and fine tracking system
- **Sample Data**: Realistic test data for development and testing

---

## 8. Quick Start Guide

### Telegram Setup (Required)

1. **Create Telegram Bot**:
   ```bash
   # Follow TELEGRAM_SETUP_GUIDE.md
   # 1. Message @BotFather on Telegram
   # 2. Send /newbot command
   # 3. Choose name: "KICKAI Team Manager"
   # 4. Save the bot token
   ```

2. **Create Team Group**:
   ```bash
   # 1. Create Telegram group
   # 2. Add your bot to the group
   # 3. Get group chat ID
   ```

3. **Configure Environment**:
   ```bash
   # Add to .env file
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_group_chat_id_here
   ```

4. **Test Integration**:
   ```bash
   python test_telegram_features.py
   ```

---

## 9. Development Workflow

### Branch-Based Development Process

All new feature implementations should follow this workflow:

1. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/KAI-XXX-description
   ```

2. **Implement Feature**
   - Write code for the feature
   - Add tests if applicable
   - Update documentation
   - Test thoroughly

3. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: implement KAI-XXX description"
   git push origin feature/KAI-XXX-description
   ```

4. **Create Pull Request**
   - Go to GitHub and create a PR from your feature branch to main
   - Add description of changes
   - Request review if needed

5. **Merge and Cleanup**
   ```bash
   # After PR is approved and merged
   git checkout main
   git pull origin main
   git branch -d feature/KAI-XXX-description
   ```

6. **Close GitHub Issue**
   - Mark the corresponding GitHub issue as closed
   - Move to "Done" column in project board

### Next Priority Features to Implement

Based on the current state, here are the recommended next features to implement:

#### 🔴 High Priority (System Enhancement)
1. **Enhanced Agent Reasoning** - Further improve tool usage and reasoning
   - Test with different scenarios
   - Fine-tune system prompts
   - Add more specific examples

2. **Advanced Squad Selection** - Improve automated squad selection
   - Implement tactical considerations
   - Add player performance history
   - Consider availability patterns

3. **Payment Integration** - Add Stripe for online payments
   - Set up Stripe API integration

#### 🟡 Medium Priority (V2 Features)
1. **Statistics Tracking** - Record and analyze player performance
2. **Ratings System** - Peer-to-peer player ratings
3. **Leaderboards** - Player performance rankings
4. **Task Management** - Automated chore assignments

---

## 10. Getting Started

### Prerequisites
- Python 3.8+
- Supabase account and project
- Telegram account (for bot creation)
- Ollama (for local LLM)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd KICKAI

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your actual values

# Set up Supabase database
# Follow setup_multi_team_schema.sql in your Supabase project

# Test the system
python test_telegram_features.py
```

### Testing
- **Test Telegram Integration**: `python test_telegram_features.py`
- **Test CrewAI + Telegram**: `python test_crewai_telegram.py`
- **Test with Ollama**: `python test_crewai_ollama_correct.py`
- **Add sample data**: `python test_sample_data.py`

### Key Files
- **Main Application**: `src/main.py`
- **Agents/Tasks/Tools**: See `src/agents.py`, `src/tasks.py`, `src/tools/`
- **Database Schema**: See SQL scripts in Supabase or PROJECT_STATUS.md
- **Telegram Tools**: See `src/tools/telegram_tools.py`
- **Project Status**: See `PROJECT_STATUS.md` for detailed implementation status

---

## 11. Contributing

Please follow the development workflow outlined above. All contributions should be made through feature branches and pull requests.