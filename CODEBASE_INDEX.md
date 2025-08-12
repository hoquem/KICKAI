# KICKAI Codebase Index - CrewAI Native Implementation

**Version:** 2.0  
**Status:** Production Ready with CrewAI Native Patterns  
**Last Updated:** December 2024  
**Focus:** CrewAI Native Implementation with Simple Parameter Passing

## 🎯 **Core Architecture Overview**

### **CrewAI Native Implementation (MANDATORY)**
All tools and agents follow CrewAI's native patterns:

```python
# ✅ CORRECT: Native CrewAI Implementation
from crewai import Agent, Task, Crew
from crewai.tools import tool

# Native Agent
agent = Agent(
    role="Player Coordinator",
    goal="Manage player registration",
    backstory="Expert in player management",
    tools=[get_my_status, add_player],
    verbose=True
)

# Native Task with Context
task = Task(
    description="Process user request",
    agent=agent,
    config={'team_id': 'TEST', 'telegram_id': '12345'}  # ✅ Use config for context
)

# Native Tool with Simple Parameters
@tool("get_my_status")
def get_my_status(telegram_id: int, team_id: str, chat_type: str) -> str:
    """Get user status using direct parameters."""
    return json_response(data=data, ui_format="User status information")
```

## 📁 **Directory Structure**

```
kickai/
├── agents/                      # CrewAI Agent System
│   ├── agentic_message_router.py    # Central message routing
│   ├── configurable_agent.py        # Native CrewAI agent wrapper
│   ├── crew_agents.py              # Agent definitions
│   └── tool_registry.py            # Tool discovery and registration
├── config/                     # Configuration Management
│   ├── agents.py               # Agent configuration
│   ├── agents.yaml             # YAML agent configs
│   └── tasks.yaml              # Task templates
├── core/                       # Core System
│   ├── dependency_container.py # DI container
│   ├── enums.py               # System enums
│   ├── exceptions.py          # Custom exceptions
│   └── startup_validation/    # System validation
├── features/                   # Feature-First Architecture
│   ├── player_registration/   # Player management
│   ├── team_administration/   # Team administration
│   ├── match_management/      # Match operations
│   ├── communication/         # Messaging system
│   ├── attendance_management/ # Attendance tracking
│   ├── system_infrastructure/ # Core services
│   └── shared/               # Shared utilities
├── database/                  # Data Layer
│   ├── firebase_client.py    # Firebase integration
│   └── interfaces.py         # Database interfaces
└── utils/                    # Utilities
    ├── json_helper.py        # JSON response helpers
    ├── tool_helpers.py       # Tool utilities
    └── format_utils.py       # Formatting utilities
```

## 🛠️ **Tool Implementation Patterns**

### **✅ Required: Native CrewAI Tool Pattern**
```python
from crewai.tools import tool
from kickai.utils.json_helper import json_response, json_error

@tool("tool_name")
def tool_function(param1: str, param2: int, team_id: str = "") -> str:
    """
    Tool description with clear parameter documentation.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        team_id: Team identifier (optional)
    
    Returns:
        JSON string response with data and UI format
    """
    try:
        # Simple validation
        if not param1:
            return json_error(message="Parameter 1 is required", error_type="Validation failed")
        
        # Business logic
        result = process_data(param1, param2)
        
        # Return structured response
        return json_response(
            data={"result": result, "param1": param1},
            ui_format=f"✅ Success: {result}"
        )
        
    except Exception as e:
        return json_error(message=str(e), error_type="Operation failed")
```

### **❌ Forbidden: Custom Patterns**
```python
# ❌ WRONG: Custom decorators
from kickai.utils.crewai_tool_decorator import json_tool

# ❌ WRONG: Complex parameter parsing
def tool_function(input_data: str) -> str:
    parsed = extract_single_value(input_data, "param1")
    
# ❌ WRONG: Old response patterns
return create_data_response(data, ui_format=ui_format)
```

## 📱 **Telegram Message Formatting**

### **✅ Required: Plain Text with Emojis**
```python
# ✅ CORRECT: Clean plain text formatting
ui_format = f"""✅ Player Registration Successful!

👤 Player Details:
• Name: {player_name}
• Position: {position}
• Status: Active

📱 Contact: {phone}
🏆 Team: {team_id}

💡 Next Steps:
• Check your status with /myinfo
• View team roster with /list
• Get help with /help"""

return json_response(data=data, ui_format=ui_format)
```

### **❌ Forbidden: Markdown/HTML**
```python
# ❌ WRONG: Markdown formatting
ui_format = f"**Player Registration Successful!**\n\n*Name:* {player_name}"

# ❌ WRONG: HTML formatting
ui_format = f"<b>Success!</b> <i>{player_name}</i> registered"
```

## 🔧 **Tool Categories by Feature**

### **Player Registration Tools**
- **Location:** `kickai/features/player_registration/domain/tools/`
- **Tools:**
  - `approve_player` - Approve player registration
  - `get_my_status` - Get user status
  - `get_player_status` - Get player by phone
  - `get_all_players` - List all players
  - `get_active_players` - List active players
  - `get_player_match` - Get match details
  - `list_team_members_and_players` - List all team members

### **Team Administration Tools**
- **Location:** `kickai/features/team_administration/domain/tools/`
- **Tools:**
  - `team_member_registration` - Register team member
  - `get_my_team_member_status` - Get team member status
  - `get_team_members` - List team members
  - `add_team_member_role` - Add role to member
  - `remove_team_member_role` - Remove role from member
  - `promote_team_member_to_admin` - Promote to admin
  - `add_team_member_simplified` - Simplified registration

### **Match Management Tools**
- **Location:** `kickai/features/match_management/domain/tools/`
- **Tools:**
  - `list_matches` - List team matches
  - `create_match` - Create new match
  - `get_match_details` - Get match information
  - `select_squad_tool` - Select match squad
  - `record_match_result` - Record match results

### **Communication Tools**
- **Location:** `kickai/features/communication/domain/tools/`
- **Tools:**
  - `send_message` - Send team message
  - `send_announcement` - Send announcement
  - `send_poll` - Send team poll
  - `send_telegram_message` - Send Telegram message

### **Help & System Tools**
- **Location:** `kickai/features/shared/domain/tools/`
- **Tools:**
  - `final_help_response` - Final help response
  - `get_available_commands` - List available commands
  - `get_command_help` - Get command help
  - `get_welcome_message` - Get welcome message
  - `get_user_status` - Get user status
  - `register_player` - Register player
  - `register_team_member` - Register team member
  - `registration_guidance` - Registration guidance

## 🎯 **Agent System Architecture**

### **5-Agent CrewAI System**
1. **MESSAGE_PROCESSOR** - Central orchestrator and router
2. **PLAYER_COORDINATOR** - Player registration and management
3. **TEAM_ADMINISTRATOR** - Team administration and member management
4. **SQUAD_SELECTOR** - Match squad selection and availability
5. **HELP_ASSISTANT** - Help system and command guidance

### **Agent Configuration**
```python
# Native CrewAI Agent Configuration
agent = Agent(
    role="Player Coordinator",
    goal="Manage player registration and status",
    backstory="Expert in player management with deep knowledge of team dynamics",
    tools=[get_my_status, approve_player, get_all_players],
    verbose=True,
    allow_delegation=True
)
```

## 🔄 **Message Processing Pipeline**

```
User Input → AgenticMessageRouter → CrewAI System → Agent Selection → Tool Execution → Response
```

### **Context Passing Pattern**
```python
# Task with context in config
task = Task(
    description=f"Process user request: {user_message}",
    agent=agent,
    config={
        'team_id': team_id,
        'telegram_id': telegram_id,
        'username': username,
        'chat_type': chat_type
    }
)
```

## 📊 **Database Schema**

### **Firestore Collections**
- `kickai_players` - Player registrations
- `kickai_team_members` - Team member data
- `kickai_matches` - Match information
- `kickai_attendance` - Attendance records
- `kickai_teams` - Team configurations

### **Data Models**
```python
# Player Model
class Player:
    player_id: str
    name: str
    phone_number: str
    position: str
    status: str
    team_id: str
    telegram_id: str
    created_at: datetime
    updated_at: datetime

# Team Member Model
class TeamMember:
    member_id: str
    name: str
    phone_number: str
    role: str
    is_admin: bool
    team_id: str
    telegram_id: str
    created_at: datetime
```

## 🚀 **Deployment & Configuration**

### **Environment Variables**
```bash
# Required Environment Variables
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_MAIN_CHAT_ID=main_chat_id
TELEGRAM_LEADERSHIP_CHAT_ID=leadership_chat_id
GOOGLE_APPLICATION_CREDENTIALS=path_to_credentials.json
GOOGLE_API_KEY=your_google_api_key
```

### **Startup Scripts**
- **Local Development:** `python run_bot_local.py`
- **Railway Deployment:** `python run_bot_railway.py`
- **Testing:** `python run_e2e_tests.py --suite smoke`

## 🔍 **Validation & Testing**

### **Tool Validation Script**
```bash
# Run CrewAI native pattern validation
python scripts/update_all_tools_validation.py
```

### **Test Categories**
- **Unit Tests:** `tests/unit/`
- **Integration Tests:** `tests/integration/`
- **End-to-End Tests:** `tests/e2e/`
- **Mock Telegram Tests:** `tests/mock_telegram/`

## 📝 **Coding Standards**

### **Tool Implementation Checklist**
- [ ] Uses `@tool` decorator from `crewai.tools`
- [ ] Accepts direct parameters (no JSON parsing)
- [ ] Returns `str` (JSON strings)
- [ ] Uses `json_response()` and `json_error()` from `json_helper`
- [ ] Includes proper error handling
- [ ] Uses plain text formatting with emojis
- [ ] Follows naming conventions
- [ ] Includes comprehensive docstrings

### **Import Standards**
```python
# ✅ CORRECT: Absolute imports
from kickai.features.player_registration.domain.tools.player_tools import get_my_status
from kickai.utils.json_helper import json_response, json_error

# ❌ WRONG: Relative imports
from .player_tools import get_my_status
```

## 🎯 **Key Principles**

### **1. CrewAI Native First**
- Always use CrewAI's built-in features
- Avoid custom wrappers and decorators
- Leverage native parameter passing via `Task.config`

### **2. Simple Parameter Passing**
- Tools accept direct parameters
- No JSON string parsing in tools
- Use `Task.config` for context passing

### **3. Plain Text Messages**
- All Telegram messages in plain text
- Use emojis for visual structure
- No markdown or HTML formatting

### **4. Clean Architecture**
- Feature-first modular structure
- Clear separation of concerns
- Dependency injection for services

### **5. Comprehensive Testing**
- Unit tests for all tools
- Integration tests for workflows
- End-to-end tests with real data

---

**Remember:** This codebase follows CrewAI native implementation patterns exclusively. All tools, agents, and workflows must adhere to these standards for consistency and maintainability. 