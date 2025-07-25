# Developer Quick Reference Guide

## **🚀 Essential Commands**

### **Bot Startup**
```bash
# ✅ ALWAYS use this sequence
source venv/bin/activate
PYTHONPATH=src python run_bot_local.py
```

### **Debugging**
```bash
# Clear Python cache
find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Test imports
source venv/bin/activate && PYTHONPATH=src python -c "from core.constants import BOT_VERSION"

# Check bot status
ps aux | grep python | grep run_bot_local

# Debug startup
source venv/bin/activate && PYTHONPATH=src python run_bot_local.py 2>&1 | head -50
```

### **Emergency Restart**
```bash
pkill -f run_bot_local.py
source venv/bin/activate && PYTHONPATH=src python run_bot_local.py
```

---

## **📝 Critical Code Rules**

### **1. Constants & Enums**
```python
# ✅ CORRECT
from core.constants import BOT_VERSION, get_command_by_name
from core.firestore_constants import get_team_members_collection

# ❌ WRONG
BOT_VERSION = "2.0.0"  # Hardcoded
team_collection = "kickai_team_members"  # Hardcoded
```

### **2. Import Paths**
```python
# ✅ CORRECT - Within src directory
from core.constants import BOT_VERSION
from agents.behavioral_mixins import get_mixin_for_role

# ❌ WRONG - Don't use src prefix within src
from src.core.constants import BOT_VERSION
```

### **3. Enum Usage**
```python
# ✅ CORRECT
command_type=CommandType.SLASH_COMMAND
chat_type=ChatType.LEADERSHIP

# ❌ WRONG
command_type=CommandType.UNDEFINED_VALUE
```

### **4. 🚨 CrewAI Native Implementation (MANDATORY)**
```python
# ✅ CORRECT: Use CrewAI native classes
from crewai import Agent, Task, Crew
from crewai.tools import tool

# ✅ Native Agent creation
agent = Agent(
    role="Player Coordinator",
    goal="Manage player registration",
    backstory="Expert in player management",
    tools=[get_my_status, add_player],
    verbose=True
)

# ✅ Native Task creation with context
task = Task(
    description="Process user request",
    agent=agent,
    config={'team_id': 'TEST', 'user_id': '12345'}  # ✅ Use config for context
)

# ✅ Native Crew orchestration
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()

# ✅ Native tool implementation
@tool("get_my_status")
async def get_my_status(team_id: str, user_id: str) -> str:
    """Get user status using parameters from context."""
    return f"Status for {user_id} in team {team_id}"
```

```python
# ❌ WRONG: Custom implementations
class CustomAgent:  # Don't create custom wrappers
    def __init__(self, role, tools):
        pass

class CustomTool:  # Don't create custom tool wrappers
    def __init__(self, func):
        pass

# ❌ WRONG: Manual context injection
def inject_context_manually(task, context):
    pass
```

---

## **🔧 Key Files**

### **Constants & Enums**
- `src/core/constants.py` - Command definitions and system constants
- `src/core/firestore_constants.py` - Firestore-specific constants
- `src/core/enums.py` - All system enums

### **Bot Startup**
- `run_bot_local.py` - Local bot startup script
- `src/core/settings.py` - Configuration management
- `src/database/firebase_client.py` - Database client

### **Agent System**
- `src/agents/crew_agents.py` - Main agent orchestration
- `src/agents/agentic_message_router.py` - Message routing
- `src/core/command_registry.py` - Command management

---

## **🚨 Common Issues & Solutions**

### **Import Errors**
1. Clear Python cache
2. Check import paths (no `src.` prefix within src)
3. Verify PYTHONPATH=src
4. Test imports individually

### **Bot Won't Start**
1. Check for existing processes: `ps aux | grep python`
2. Kill existing process: `pkill -f run_bot_local.py`
3. Clear cache and restart
4. Check logs: `tail -f logs/kickai.log`

### **Command Registry Issues**
1. Verify enum values are defined
2. Check import paths
3. Validate command definitions
4. Clear cache and restart

---

## **📊 Current Status**

### **✅ Operational**
- Bot Process: Running (PID: 2738)
- Telegram Bot: @KickAITesting_bot (ID: 7958401227)
- CrewAI System: Initialized
- Teams: 1 active (KickAI Testing)
- Leadership Chat: Active (-4969733370)

### **🔄 Testing**
- Command Response
- User Registration
- Leadership Commands

---

## **📞 Support**

### **Logs**
```bash
# Monitor logs
tail -f logs/kickai.log

# Check errors
grep -i error logs/kickai.log

# Check startup
grep -i "starting\|initialized" logs/kickai.log
```

### **Documentation**
- [Full Architecture](docs/ARCHITECTURE.md)
- [Lessons Learned](docs/LESSONS_LEARNED_IMPORT_FIXES.md)
- [Project Status](PROJECT_STATUS.md)

---

*Last Updated: July 23, 2025*
*Status: ✅ OPERATIONAL* 