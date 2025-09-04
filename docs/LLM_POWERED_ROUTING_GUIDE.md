# 🧠 LLM-Powered Intelligent Routing Guide

**Version**: 1.0 | **Status**: Production Ready | **Last Updated**: December 2025

This guide explains how to work with KICKAI's new LLM-powered intelligent routing system and why it's superior to hard-coded routing patterns.

## 🚨 **CRITICAL ROUTING RULE - READ THIS FIRST!**

**ALL ROUTING IS NOW HANDLED BY THE MANAGER LLM - NO HARD-CODED ROUTING RULES!**

The system uses LLM-powered intelligent routing that understands semantic intent. Do NOT implement:
- ❌ Hard-coded command routing patterns
- ❌ Rigid if/else routing logic  
- ❌ Pattern matching for agent selection
- ❌ Manual routing decisions in tools

Instead, trust the Manager LLM to:
- ✅ Understand user intent semantically
- ✅ Route to the appropriate specialist agent
- ✅ Handle natural language variations automatically
- ✅ Consider context (chat type, permissions) intelligently

## 🎯 **How the New System Works**

### **Before: Hard-Coded Routing (Brittle)**
```python
# OLD APPROACH - Don't do this anymore!
if "/list" in user_message:
    if chat_type == "main":
        route_to("player_coordinator")
    elif chat_type == "leadership":
        route_to("team_administrator")
elif "list players" in user_message.lower():
    route_to("player_coordinator")
elif "list members" in user_message.lower():
    route_to("team_administrator")
```

**Problems with Old Approach:**
- ❌ **Brittle**: Adding new commands requires code changes
- ❌ **Maintenance Overhead**: Rules become outdated quickly
- ❌ **Limited Flexibility**: Can't handle natural language variations
- ❌ **Context Confusion**: Rigid rules don't adapt to user intent

### **After: LLM-Powered Routing (Intelligent)**
```python
# NEW APPROACH - The Manager LLM handles this automatically!
task_description_with_context = f"""
🤖 INTELLIGENT TASK ROUTING

USER REQUEST: "{task_description}"

CONTEXT:
- Username: {username}
- Chat Type: {chat_type}
- Team ID: {team_id}

🎯 YOUR ROLE AS MANAGER:
You are an intelligent task router. Analyze the user's request and delegate to the most appropriate specialist agent based on:

1. **SEMANTIC UNDERSTANDING**: What does the user actually want?
2. **AGENT EXPERTISE**: Which agent has the right tools and knowledge?
3. **CONTEXT AWARENESS**: Consider chat type and user permissions
4. **NATURAL LANGUAGE**: Understand intent beyond just commands
"""
```

**Benefits of New Approach:**
- ✅ **Adaptive**: LLM understands natural language variations
- ✅ **Maintainable**: No hard-coded rules to update
- ✅ **Intelligent**: Routes based on semantic understanding
- ✅ **Flexible**: Handles new request patterns automatically

## 🎯 **Agent Boundaries and Responsibilities**

### **Clear Agent Specialization**
Each agent has CLEAR boundaries and should NEVER handle operations outside their expertise:

| Agent | Primary Role | What They Handle | What They DON'T Handle |
|-------|--------------|------------------|------------------------|
| **HELP_ASSISTANT** | Help and guidance | Help commands, explanations, troubleshooting | Player data, team management, matches |
| **PLAYER_COORDINATOR** | Player operations | Player info, status, registration, updates | Team members, matches, system operations |
| **TEAM_ADMINISTRATOR** | Team management | Team members, roles, permissions, structure | Player operations, matches, system operations |
| **SQUAD_SELECTOR** | Match operations | Matches, availability, squad selection, attendance | Player info, team management, system operations |
| **MESSAGE_PROCESSOR** | Communication & System | Messages, announcements, system status, polls | Player data, team management, matches |

### **Routing Examples**

#### **Example 1: Natural Language Understanding**
```
User: "Who can play this weekend?"
Old System: ❌ Rigid rule matching - might route incorrectly
New System: ✅ LLM understands "player availability" → routes to squad_selector
```

#### **Example 2: Context-Aware Routing**
```
User: "/list" in main chat
Old System: ❌ Hard-coded rule → player_coordinator
New System: ✅ LLM understands context + command → player_coordinator

User: "/list" in leadership chat  
Old System: ❌ Hard-coded rule → team_administrator
New System: ✅ LLM understands context + command → team_administrator
```

#### **Example 3: Intent Recognition**
```
User: "Show me all the players"
Old System: ❌ Pattern matching on "players" → player_coordinator
New System: ✅ LLM understands "list players" intent → player_coordinator

User: "What players are available for the match?"
Old System: ❌ Might route to player_coordinator (wrong)
New System: ✅ LLM understands "match availability" → squad_selector
```

## 🔧 **How to Work with the New System**

### **1. Trust the Manager LLM**
The Manager LLM is intelligent and understands:
- **Semantic Intent**: What the user actually wants
- **Context**: Chat type, user permissions, team context
- **Agent Expertise**: Which agent has the right tools
- **Natural Language**: Variations and patterns in user requests

### **2. Focus on Tool Quality, Not Routing**
Instead of worrying about routing, focus on:
- **Clear Tool Names**: Make tool purposes obvious
- **Proper Parameters**: Only include parameters the tool needs
- **Good Docstrings**: Explain when to use the tool
- **Error Handling**: Make tools robust and user-friendly

### **3. Use Semantic Tool Naming**
```python
# ✅ GOOD - Clear semantic intent
@tool("get_player_self")           # For user's own data
@tool("get_player_by_identifier")  # For looking up others
@tool("get_player_match_self")     # For user's own match data
@tool("get_player_match_by_identifier") # For others' match data

# ❌ AVOID - Unclear or generic names
@tool("get_player")                # Unclear purpose
@tool("player_info")               # Generic name
@tool("example_tool")              # Meaningless name
```

### **4. Write Clear Tool Docstrings**
```python
@tool("get_player_self")
async def get_player_self(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get requesting user's player information.
    
    This tool retrieves the current user's own player data including status,
    position, and team membership. Use when the user wants to see their
    own information, not when looking up other players.
    
    Args:
        telegram_id: User's Telegram ID for authentication
        team_id: Team context for data retrieval
        username: User's display name for personalization
        chat_type: Chat context affecting available information
        
    Returns:
        Formatted player status information for the requesting user
    """
```

## 🚀 **Best Practices for Developers**

### **1. Don't Add Routing Logic to Tools**
```python
# ❌ WRONG - Don't do this!
@tool("get_player_info")
async def get_player_info(message: str, chat_type: str) -> str:
    # Don't add routing logic here
    if "my info" in message.lower():
        return get_my_info()
    elif "player" in message.lower():
        return get_other_player_info()
    
# ✅ CORRECT - Let the Manager LLM handle routing
@tool("get_player_self")
async def get_player_self(telegram_id: str, team_id: str) -> str:
    # Just handle the specific operation
    return get_my_player_info(telegram_id, team_id)

@tool("get_player_by_identifier")  
async def get_player_by_identifier(identifier: str, team_id: str) -> str:
    # Just handle the specific operation
    return get_other_player_info(identifier, team_id)
```

### **2. Don't Duplicate Tools Across Agents**
```python
# ❌ WRONG - Don't duplicate tools
# In player_coordinator:
@tool("get_player_info")

# In team_administrator:
@tool("get_player_info")  # Same tool name!

# ✅ CORRECT - Each agent has distinct tools
# In player_coordinator:
@tool("get_player_self")
@tool("get_player_by_identifier")

# In team_administrator:
@tool("get_member_self")
@tool("get_member_by_identifier")
```

### **3. Trust CrewAI's Tool Selection**
```python
# ✅ GOOD - Let CrewAI handle tool selection
@tool("get_player_self")
async def get_player_self(telegram_id: str, team_id: str) -> str:
    # CrewAI will automatically select this tool when user wants their own info
    pass

@tool("get_player_by_identifier")
async def get_player_by_identifier(identifier: str, team_id: str) -> str:
    # CrewAI will automatically select this tool when user wants someone else's info
    pass

# ❌ AVOID - Don't try to force tool selection
@tool("get_player_info_force_self")  # Unnecessary complexity
async def get_player_info_force_self(telegram_id: str, team_id: str) -> str:
    pass
```

### **4. Keep Tools Focused and Simple**
```python
# ✅ GOOD - Simple, focused tool
@tool("get_player_status")
async def get_player_status(telegram_id: str, team_id: str) -> str:
    """Get player status - simple and focused."""
    try:
        service = get_container().get_service(IPlayerService)
        result = service.get_player_status(int(telegram_id), team_id)
        return format_player_status(result)
    except Exception as e:
        logger.error(f"Error getting player status: {e}")
        return f"❌ Failed to get player status: {str(e)}"

# ❌ AVOID - Complex, multi-purpose tool
@tool("do_everything_with_players")
async def do_everything_with_players(
    action: str, 
    telegram_id: str, 
    team_id: str, 
    extra_data: str,
    chat_type: str,
    username: str
) -> str:
    """This tool tries to do too many things."""
    if action == "get_status":
        return get_player_status(telegram_id, team_id)
    elif action == "update_info":
        return update_player_info(telegram_id, team_id, extra_data)
    # ... more complex logic
```

## 🔍 **Debugging and Troubleshooting**

### **Common Issues and Solutions**

#### **Issue 1: Tool Not Being Selected**
```python
# Problem: Tool not being selected by CrewAI
# Solution: Check tool naming and docstring clarity

# ❌ Unclear tool name
@tool("tool")

# ✅ Clear tool name
@tool("get_player_self")
```

#### **Issue 2: Wrong Agent Being Selected**
```python
# Problem: Request going to wrong agent
# Solution: Check agent boundaries and tool assignments

# Make sure tools are assigned to the right agent
# In agents.yaml:
tools:
  - get_player_self        # Should be in PLAYER_COORDINATOR
  - get_member_self        # Should be in TEAM_ADMINISTRATOR
  - get_match_details      # Should be in SQUAD_SELECTOR
```

#### **Issue 3: Routing Not Working as Expected**
```python
# Problem: Routing not working correctly
# Solution: Check Manager LLM prompt and agent configuration

# Verify the Manager LLM prompt is clear and comprehensive
# Check that agent roles and goals are well-defined
# Ensure tools are properly assigned to agents
```

### **Debugging Commands**
```bash
# Check agent configuration
PYTHONPATH=. python -c "
from kickai.config.agents import load_agents
agents = load_agents()
for agent in agents:
    print(f'{agent.name}: {len(agent.tools)} tools')
"

# Test routing with specific input
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('TEST')
result = system.execute_task('list all players', {'chat_type': 'main'})
print(f'Routing result: {result}')
"
```

## 📚 **Learning Resources**

### **CrewAI Best Practices**
- [CrewAI Documentation](https://docs.crewai.com/)
- [Hierarchical Process Guide](https://docs.crewai.com/learn/hierarchical-process)
- [Agent Design Best Practices](https://docs.crewai.com/guides/agents/crafting-effective-agents)

### **KICKAI-Specific Resources**
- [CREWAI_TOOL_STANDARDS.md](docs/CREWAI_TOOL_STANDARDS.md) - Tool implementation standards
- [LLM_POWERED_ROUTING_ANALYSIS.md](docs/LLM_POWERED_ROUTING_ANALYSIS.md) - Technical analysis
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture overview

### **Examples and Templates**
- [Tool Implementation Examples](docs/CREWAI_TOOL_STANDARDS.md#examples)
- [Agent Configuration Templates](kickai/config/agents.yaml)
- [Routing Test Cases](tests/test_routing.py)

## 🎯 **Summary**

The new LLM-powered intelligent routing system represents a significant advancement:

1. **No More Hard-Coded Rules**: LLM handles routing automatically
2. **Natural Language Understanding**: Works with user intent, not just commands
3. **Automatic Adaptation**: New patterns handled without code changes
4. **Clear Agent Boundaries**: Each agent has distinct responsibilities
5. **CrewAI Best Practices**: Follows all recommended patterns

**Remember**: Trust the Manager LLM, focus on tool quality, and let CrewAI handle the routing intelligence!

---

**Status**: Production Ready | **Routing System**: LLM-Powered Intelligent | **Agent System**: 5-Agent with Clear Boundaries | **Maintenance**: Low Overhead

