# CrewAI Best Practices & Critical Lessons Learned

**Status:** ACTIVE - CRITICAL FOR SYSTEM STABILITY  
**Last Updated:** December 2024  
**Priority:** HIGHEST - FOLLOW THESE RULES STRICTLY

## 🚨 CRITICAL RULES - NEVER VIOLATE

### 1. **Tool Independence (MANDATORY)**
- **❌ NEVER**: Tools calling other tools or services
- **✅ ALWAYS**: Tools are simple, independent functions
- **Rationale**: CrewAI tools must be lightweight and independent to work properly

```python
# ❌ WRONG - Tool calling services (CAUSES "Tool object is not callable" ERROR)
@tool("get_available_commands")
def get_available_commands(user_id: str, chat_type: str) -> str:
    service = get_container().get(PlayerService)  # DON'T DO THIS
    return service.get_commands(user_id)

# ✅ CORRECT - Independent tool
@tool("get_available_commands")
def get_available_commands(user_id: str, chat_type: str) -> str:
    if chat_type == "main_chat":
        return "Available commands: /register, /help, /status"
    return "Leadership commands: /approve, /reject, /list"
```

### 2. **Absolute Imports with PYTHONPATH (MANDATORY)**
- **ALWAYS** use absolute imports: `from src.features...`
- **ALWAYS** set `PYTHONPATH=src` when running scripts
- **ALWAYS** activate virtual environment: `source venv311/bin/activate`

```bash
# ✅ CORRECT - Always use this pattern
source venv311/bin/activate && PYTHONPATH=src python run_bot_local.py
```

### 3. **Tool Discovery Pattern (MANDATORY)**
- Tools must be discovered from `src/features/*/domain/tools/`
- Use `_register_discovered_tool()` method, not direct assignment
- Set PYTHONPATH in tool discovery to handle imports

```python
# ✅ CORRECT - Tool discovery pattern
def _discover_tools_from_file(self, file_path: Path, feature_name: str) -> int:
    # Set PYTHONPATH for imports
    src_path = file_path.parent.parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Load module and find @tool decorated functions
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if hasattr(attr, '_is_tool') and attr._is_tool:
            self._register_discovered_tool(attr_name, attr, feature_name)
```

### 4. **Telegram Message Formatting (MANDATORY)**
- **ALWAYS** use clean, readable formatting for Telegram responses
- **ALWAYS** follow Telegram MarkdownV2 best practices
- **NEVER** over-escape characters that are part of markdown formatting

```python
# ✅ CORRECT - Clean Telegram formatting
@tool("get_available_commands")
def get_available_commands(user_id: str, chat_type: str) -> str:
    result = f"📋 Available Commands for {chat_display}:\n\n"
    
    for category, cmd_list in commands.items():
        result += f"*{category}:*\n"  # Use single asterisks for italic
        for cmd_name, cmd_desc in cmd_list:
            result += f"• `{cmd_name}` - {cmd_desc}\n"  # Clean formatting
        result += "\n"
    
    result += "💡 Use `/help [command]` for detailed help on any command."
    return result

# ❌ WRONG - Messy formatting with over-escaping
@tool("get_available_commands")
def get_available_commands(user_id: str, chat_type: str) -> str:
    result = f"📋 Available Commands for {chat_type}:\n\n"
    result += f"**{category}:**\n"  # Double asterisks cause issues
    result += f"• `{cmd_name}` \\- {cmd_desc}\n"  # Over-escaping
    return result
```

## 🔧 Tool Design Patterns

### Information Retrieval Tools
```python
@tool("get_user_status")
def get_user_status_tool(user_id: str, team_id: str = None) -> str:
    """Get user status - independent tool with simple logic"""
    # Simple logic, no service calls
    if user_id and len(user_id) > 0:
        return f"User {user_id} is registered"
    return "User not found"
```

### Command Listing Tools
```python
@tool("get_available_commands")
def get_available_commands(user_id: str, chat_type: str, team_id: str = None) -> str:
    """Get available commands - static data based on context"""
    if chat_type.lower() == "main_chat":
        return "Main chat commands: /register, /help, /status, /list"
    elif chat_type.lower() == "leadership_chat":
        return "Leadership commands: /approve, /reject, /pending, /addplayer"
    return "General commands: /help"
```

### Action Tools (Limited Service Use)
```python
@tool("send_message")
def send_message_tool(chat_id: str, message: str, team_id: str = None) -> str:
    """Send message - delegates to service but tool itself is simple"""
    try:
        # Simple validation
        if not chat_id or not message:
            return "❌ Missing chat_id or message"
        
        # Delegate to service (this is acceptable for action tools)
        service = get_container().get(MessageService)
        result = service.send_message(chat_id, message)
        return f"✅ Message sent: {result}"
    except Exception as e:
        return f"❌ Failed to send message: {str(e)}"
```

## 📱 Telegram Formatting Best Practices

### 1. **MarkdownV2 Formatting**
- Use `*text*` for italic (single asterisks)
- Use `__text__` for bold (double underscores)
- Use `` `text` `` for code (backticks)
- Use `-` for lists (preserved, not escaped)
- Use `/command` for commands (preserved, not escaped)

### 2. **Clean Response Structure**
```python
# ✅ GOOD - Clean, readable structure
result = f"📋 Available Commands for {chat_type}:\n\n"
result += f"*{category}:*\n"
result += f"• `{cmd_name}` - {cmd_desc}\n"
result += "\n"
result += "💡 Use `/help [command]` for detailed help."

# ❌ BAD - Messy, over-escaped structure
result = f"📋 Available Commands for {chat_type}:\n\n"
result += f"**{category}:**\n"  # Double asterisks cause issues
result += f"• `{cmd_name}` \\- {cmd_desc}\n"  # Over-escaping
result += f"💡 Use `/help [command]` for detailed help\\."  # Unnecessary escaping
```

### 3. **Character Escaping Rules**
- **Escape these characters**: `[ ] ( ) ~ > # + = | { } . !`
- **Preserve these characters**: `_ * - /` (for markdown formatting)
- **Never escape**: Commands like `/help`, `/register`
- **Never escape**: List markers like `•` and `-`

### 4. **Response Length Guidelines**
- Keep responses concise and focused
- Use bullet points for lists
- Use emojis sparingly but effectively
- Break up long responses with line breaks

## 🚨 Common Errors & Solutions

### 1. **"Tool object is not callable" Error**
- **Cause**: Tool registry returning metadata instead of callable functions
- **Solution**: Use `_register_discovered_tool()` method, not direct assignment
- **Check**: Ensure tool discovery calls `_register_discovered_tool(attr_name, attr, feature_name)`

### 2. **"ToolRegistry object has no attribute 'items'" Error**
- **Cause**: Code trying to call `len()` or `items()` on ToolRegistry object
- **Solution**: Use `tool_registry.get_tool_names()` instead of direct object methods
- **Check**: Replace `len(tool_registry)` with `len(tool_registry.get_tool_names())`

### 3. **Import Errors in Tool Discovery**
- **Cause**: Relative imports or missing PYTHONPATH
- **Solution**: Always use absolute imports and set PYTHONPATH=src
- **Check**: All tool files use `from src.features...` imports

### 4. **Tool Dependencies**
- **Cause**: Tools trying to import and use services
- **Solution**: Make tools completely independent with static data or simple logic
- **Check**: Tools should not import services or call other tools

### 5. **Poor Telegram Formatting**
- **Cause**: Over-escaping or incorrect markdown syntax
- **Solution**: Use clean formatting and proper markdown patterns
- **Check**: Test formatting with the `_escape_markdown` method

## 🧪 Testing & Validation

### Tool Discovery Test
```bash
source venv311/bin/activate && PYTHONPATH=src python -c "
from src.agents.tool_registry import get_tool_registry
registry = get_tool_registry()
registry.auto_discover_tools()
print('Available tools:', registry.get_tool_names())
"
```

### Individual Tool Test
```bash
source venv311/bin/activate && PYTHONPATH=src python -c "
from src.features.shared.domain.tools.help_tools import get_available_commands
result = get_available_commands.func('12345', 'main_chat', 'KTI')
print('Tool result:', result)
"
```

### Telegram Formatting Test
```bash
source venv311/bin/activate && PYTHONPATH=src python -c "
from src.features.communication.infrastructure.telegram_bot_service import TelegramBotService
service = TelegramBotService('test', 'test')
result = service._escape_markdown('📋 Available Commands:\n\n*Category:*\n• `/command` - Description')
print('Escaped result:', result)
"
```

## 📋 Development Checklist

### Adding New Tools
- [ ] Tool uses `@tool` decorator with descriptive name
- [ ] Tool is independent (no service calls)
- [ ] Tool uses absolute imports: `from src.features...`
- [ ] Tool has proper error handling
- [ ] Tool returns meaningful responses
- [ ] Tool tested individually
- [ ] Tool discovered by registry
- [ ] Tool uses clean Telegram formatting

### Debugging Tool Issues
- [ ] Check tool discovery: `registry.get_tool_names()`
- [ ] Verify imports: Use absolute paths
- [ ] Test individual tool: `tool.func(args)`
- [ ] Check agent tool assignment: `agent.tools`
- [ ] Verify PYTHONPATH=src is set
- [ ] Ensure virtual environment activated
- [ ] Test Telegram formatting: `_escape_markdown()`

### Deployment Checklist
- [ ] All tools use absolute imports
- [ ] PYTHONPATH=src set in all environments
- [ ] Virtual environment activated
- [ ] Tools are independent (no service calls)
- [ ] Tool discovery working correctly
- [ ] Agent tool assignment functional
- [ ] Telegram formatting clean and readable

## 🎯 Performance Guidelines

### Tool Loading
- Tools discovered once at startup
- No runtime tool discovery (performance impact)
- Tool registry cached in memory

### Agent Initialization
- Agents created once per team
- Tool assignment happens during agent creation
- No dynamic tool reassignment

### Memory Management
- Tool functions are lightweight
- No heavy dependencies in tool functions
- Services injected only when needed

## 🔒 Security & Error Handling

### Input Validation
- All tool inputs validated before processing
- Sanitize user inputs to prevent injection
- Return clear error messages

### Exception Handling
- Tools must handle exceptions gracefully
- Return meaningful error messages
- Log errors for debugging

### Access Control
- Tools respect user permissions
- Chat type determines available commands
- Team context for multi-tenant isolation

## 📚 References

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI Tool Best Practices](https://docs.crewai.com/how-to/use-tools/)
- [Python Import System](https://docs.python.org/3/reference/import.html)
- [Telegram Bot API - MarkdownV2](https://core.telegram.org/bots/api#markdownv2-style)

## 🚨 REMEMBER

**These rules are CRITICAL for system stability. Violating them will cause:**
- "Tool object is not callable" errors
- Import failures
- Agent initialization failures
- System crashes
- Poor user experience with messy formatting

**Always follow these patterns exactly as shown.** 