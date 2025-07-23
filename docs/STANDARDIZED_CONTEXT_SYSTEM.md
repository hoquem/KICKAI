# Standardized Context System

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** 2025-07-22  

## Overview

The Standardized Context System ensures consistent context passing across the entire KICKAI system. This eliminates context fragmentation and ensures all agents and tools have access to the same user information regardless of how they are called.

## Problem Solved

### Before Standardized Context
- **Multiple context objects** with overlapping but different fields
- **Inconsistent data access** across system layers
- **Tools receiving individual parameters** instead of full context
- **Missing context fields** in execution context
- **Hardcoded placeholder values** in agent task descriptions

### After Standardized Context
- **Single standardized context object** with all required fields
- **Consistent data access** across all system layers
- **Tools receiving full context objects** with all user information
- **Complete context information** available to all agents and tools
- **No more placeholder values** - real user data always available

## Architecture

### Core Components

#### 1. StandardizedContext Class
```python
@dataclass
class StandardizedContext:
    # Core fields (always present)
    user_id: str
    team_id: str
    chat_id: str
    chat_type: str
    message_text: str
    username: str
    telegram_name: str
    
    # Optional fields (populated when available)
    user_permissions: Optional[UserPermissions] = None
    player_data: Optional[Dict[str, Any]] = None
    team_member_data: Optional[Dict[str, Any]] = None
    is_registered: bool = False
    is_player: bool = False
    is_team_member: bool = False
    
    # Context metadata
    source: ContextSource = ContextSource.TELEGRAM_MESSAGE
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### 2. Context Creation Functions
```python
# Create from Telegram message
context = create_context_from_telegram_message(
    user_id="123456789",
    team_id="KTI",
    chat_id="-1001234567890",
    chat_type=ChatType.MAIN,
    message_text="/help",
    username="john_doe",
    telegram_name="John Doe"
)

# Create from command
context = create_context_from_command(
    user_id="123456789",
    team_id="KTI",
    chat_id="-1001234567890",
    chat_type=ChatType.LEADERSHIP,
    command_text="/approve player123",
    username="admin_user",
    telegram_name="Admin User"
)
```

#### 3. Context Enhancement
```python
# Enhance with user data
enhanced_context = enhance_context_with_user_data(
    context=context,
    user_permissions=user_permissions,
    player_data=player_data,
    team_member_data=team_member_data
)
```

## Implementation

### 1. Context Flow

```
Telegram Update
    ↓
TelegramMessage (Domain Object)
    ↓
StandardizedContext (via create_context_from_telegram_message)
    ↓
Execution Context (for backward compatibility)
    ↓
Agent Task Description (enhanced with context)
    ↓
CrewAI Agent (with full context)
    ↓
Tools (receiving StandardizedContext)
```

### 2. Tool Signature Updates

#### Before
```python
@tool("get_user_status")
def get_user_status_tool(user_id: str, team_id: Optional[str] = None) -> str:
    # Limited access to user information
```

#### After
```python
@tool("get_user_status")
def get_user_status_tool(context: StandardizedContext) -> str:
    # Full access to all user information
    user_id = context.user_id
    team_id = context.team_id
    is_registered = context.is_registered
    # Access to permissions, player data, etc.
```

### 3. Agent Context Enhancement

The `ConfigurableAgent.execute()` method now enhances task descriptions with standardized context:

```python
def _enhance_task_with_context(self, task: str, context: Dict[str, Any]) -> str:
    # Convert to standardized context
    standardized_context = StandardizedContext.from_dict(context)
    
    # Create enhanced task description
    context_section = f"""
EXECUTION CONTEXT:
- User ID: {standardized_context.user_id}
- Team ID: {standardized_context.team_id}
- Chat Type: {standardized_context.chat_type}
- Username: {standardized_context.username}
- Telegram Name: {standardized_context.telegram_name}
- Is Registered: {standardized_context.is_registered}
- Is Player: {standardized_context.is_player}
- Is Team Member: {standardized_context.is_team_member}
- Message Text: {standardized_context.message_text}

TOOL USAGE:
- get_user_status: Use context.user_id and context.team_id
- get_available_commands: Use context.user_id, context.chat_type, and context.team_id
- format_help_message: Use context for user information
- All other tools: Use context for user and team information
"""
```

## Updated Tools

### Help Tools
- ✅ `get_user_status_tool(context: StandardizedContext)`
- ✅ `get_available_commands(context: StandardizedContext)`
- ✅ `format_help_message(commands_text: str, context: StandardizedContext)`

### Player Tools
- ✅ `get_my_status(context: StandardizedContext)`
- ✅ `get_all_players(context: StandardizedContext)`

### Communication Tools
- ✅ `send_message(context: StandardizedContext, text: str)`

## Benefits

### 1. Consistency
- **Single source of truth** for user context
- **Consistent data access** across all system layers
- **No more context fragmentation**

### 2. Completeness
- **All required fields** always present
- **Optional fields** populated when available
- **No missing context information**

### 3. Maintainability
- **Centralized context management**
- **Easy to extend** with new fields
- **Type-safe context objects**

### 4. Debugging
- **Clear context flow** through system
- **Rich context information** for debugging
- **Context validation** and error handling

## Usage Examples

### Creating Context
```python
from core.context_types import create_context_from_telegram_message, ChatType

# From Telegram message
context = create_context_from_telegram_message(
    user_id="123456789",
    team_id="KTI",
    chat_id="-1001234567890",
    chat_type=ChatType.MAIN,
    message_text="/help",
    username="john_doe",
    telegram_name="John Doe"
)
```

### Using Context in Tools
```python
@tool("my_tool")
def my_tool(context: StandardizedContext) -> str:
    # Access all context information
    user_id = context.user_id
    team_id = context.team_id
    chat_type = context.chat_type
    username = context.username
    is_registered = context.is_registered
    
    # Use context for business logic
    if context.is_leadership_chat():
        return f"Leadership command for {username}"
    else:
        return f"Main chat command for {username}"
```

### Context Validation
```python
# Check user permissions
if context.has_permission(PermissionLevel.LEADERSHIP):
    # User has leadership permissions
    pass

# Get user display name
display_name = context.get_user_display_name()

# Check chat type
if context.is_main_chat():
    # Main chat logic
    pass
```

## Migration Guide

### For Tool Developers
1. **Update tool signatures** to accept `StandardizedContext`
2. **Extract required fields** from context object
3. **Use context methods** for common operations
4. **Remove individual parameters** from tool signatures

### For Agent Developers
1. **Use standardized context** in agent task descriptions
2. **Pass context to tools** instead of individual parameters
3. **Leverage context methods** for user information
4. **Update agent configurations** if needed

### For System Integrators
1. **Use context creation functions** for new integrations
2. **Enhance context with user data** when available
3. **Pass context through** the entire call chain
4. **Validate context** before using

## Future Enhancements

### Planned Features
1. **Context persistence** across conversations
2. **Context validation** and error handling
3. **Context caching** for performance
4. **Context analytics** and monitoring

### Extension Points
1. **Custom context fields** for specific features
2. **Context transformers** for data conversion
3. **Context middleware** for processing
4. **Context serialization** for storage

## Testing

### Context Creation Tests
```python
def test_create_context_from_telegram_message():
    context = create_context_from_telegram_message(
        user_id="123",
        team_id="KTI",
        chat_id="-100123",
        chat_type=ChatType.MAIN,
        message_text="/help",
        username="test_user"
    )
    
    assert context.user_id == "123"
    assert context.team_id == "KTI"
    assert context.chat_type == "main_chat"
    assert context.is_main_chat() == True
```

### Tool Integration Tests
```python
def test_tool_with_standardized_context():
    context = create_context_from_telegram_message(...)
    result = get_user_status_tool(context)
    
    assert "registered" in result.lower()
    assert context.user_id in result
```

## Conclusion

The Standardized Context System provides a robust foundation for consistent context management across the KICKAI system. It eliminates context fragmentation, ensures complete user information availability, and provides a maintainable architecture for future enhancements.

All agents and tools now have access to the same rich context information, leading to more reliable and consistent system behavior. 