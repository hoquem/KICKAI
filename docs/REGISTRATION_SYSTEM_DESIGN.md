# Registration System Design

## Overview

The KICKAI registration system follows clean architecture principles with **separate implementations** for different chat contexts, ensuring predictable behavior and maintainable code. The system properly distinguishes between player registration and team member registration based on the chat context where the command is executed.

## Problem Solved

### Previous Issues
- Single `/register` command used in both main chat and leadership chat
- System treated all registrations as "player registration" regardless of context
- No clear distinction between players (main chat) and team members (leadership chat)
- Confusing user experience and incorrect data categorization

### Current Solution
- **Context-aware commands**: Separate `/register` implementations for each chat type
- **Clean separation**: No conditional logic within handlers
- **Predictable behavior**: Each chat type has its own dedicated registration flow
- **Proper tool selection**: Agents use appropriate tools based on chat context

## Architecture Design

### Command Registration Pattern

```python
# Main Chat - Player Registration
@command(
    name="/register",
    description="Register as a new player (Main Chat)",
    chat_type=ChatType.MAIN,
    permission_level=PermissionLevel.PUBLIC
)
async def handle_register_player_main_chat(update, context, **kwargs):
    """Handle /register command in main chat - for player registration."""
    return None  # Handled by agent system

# Leadership Chat - Team Member Registration  
@command(
    name="/register",
    description="Register a new team member (Leadership Chat)",
    chat_type=ChatType.LEADERSHIP,
    permission_level=PermissionLevel.LEADERSHIP
)
async def handle_register_team_member_leadership_chat(update, context, **kwargs):
    """Handle /register command in leadership chat - for team member registration."""
    return None  # Handled by agent system
```

### Command Registry Enhancements

The command registry now supports chat-type-aware command registration:

```python
@dataclass
class CommandMetadata:
    name: str
    description: str
    command_type: CommandType
    permission_level: PermissionLevel
    feature: str
    handler: Callable
    chat_type: Optional[str] = None  # ChatType.MAIN, ChatType.LEADERSHIP, or None for all
```

### Context-Aware Routing

The agentic message router now includes chat context in the execution context:

```python
execution_context = {
    'user_id': message.user_id,
    'team_id': message.team_id,
    'chat_id': message.chat_id,
    'chat_type': message.chat_type.value,
    'is_leadership_chat': message.chat_type == ChatType.LEADERSHIP,
    'is_main_chat': message.chat_type == ChatType.MAIN,
    'username': message.username,
    'message_text': message.text
}
```

## Tool Architecture

### Separate Registration Tools

```python
@tool("register_player")
def register_player(player_name: str, phone_number: str, position: str, team_id: Optional[str] = None) -> str:
    """Register a new player in the main chat."""
    # Player registration logic
    pass

@tool("register_team_member") 
def register_team_member(player_name: str, phone_number: str, role: str, team_id: Optional[str] = None) -> str:
    """Register a new team member in the leadership chat."""
    # Team member registration logic
    pass
```

### Agent Tool Selection

The PLAYER_COORDINATOR agent has access to both tools and selects the appropriate one based on context:

```python
tools=["get_my_status", "get_player_status", "get_all_players", "approve_player", "register_player", "register_team_member"]
```

## User Experience Flow

### Main Chat Registration Flow

1. **User Action**: Player types `/register John Smith +447123456789 Forward` in main chat
2. **Command Routing**: System routes to main chat `/register` handler
3. **Agent Processing**: PLAYER_COORDINATOR agent receives context with `is_main_chat: true`
4. **Tool Selection**: Agent uses `register_player` tool
5. **Result**: Player registration completed with position

### Leadership Chat Registration Flow

1. **User Action**: Admin types `/register John Smith +447123456789 Coach` in leadership chat
2. **Command Routing**: System routes to leadership chat `/register` handler
3. **Agent Processing**: PLAYER_COORDINATOR agent receives context with `is_leadership_chat: true`
4. **Tool Selection**: Agent uses `register_team_member` tool
5. **Result**: Team member registration completed with role

## Implementation Details

### Command Discovery

The command registry automatically discovers and registers commands with chat-type awareness:

```python
def get_command_for_chat(self, name: str, chat_type: str) -> Optional[CommandMetadata]:
    """Get a specific command for a chat type, considering chat-specific and universal commands."""
    if name in self._commands:
        cmd = self._commands[name]
        # Return if command is universal (no chat_type) or matches the chat type
        if cmd.chat_type is None or cmd.chat_type == chat_type:
            return cmd
    return None
```

### Validation

The agentic message router validates command availability before processing:

```python
available_command = registry.get_command_for_chat(command_name, chat_type_str)

if not available_command:
    return AgentResponse(
        message=f"❌ Command `{command_name}` is not available in this chat type.",
        success=False,
        error="Command not available in chat type"
    )
```

## Benefits

### 🎯 Predictable Behavior
- Each chat type has dedicated registration flow
- No unexpected behavior based on context
- Clear separation of concerns

### 🧹 Maintainable Code
- Separate implementations instead of conditional logic
- Easy to modify behavior for specific chat types
- Clear code organization

### 🔒 Security & Permissions
- Proper permission levels for each context
- Leadership chat commands require leadership permissions
- Main chat commands available to all users

### 📊 Data Integrity
- Proper categorization of players vs team members
- Correct tool selection based on context
- Accurate logging and tracking

## Command Reference

### Main Chat Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/register` | Register as a new player | PUBLIC |

### Leadership Chat Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/register` | Register a new team member | LEADERSHIP |
| `/addplayer` | Add player with invite link | LEADERSHIP |
| `/addmember` | Add team member with invite link | LEADERSHIP |
| `/approve` | Approve player for participation | LEADERSHIP |
| `/reject` | Reject player with reason | LEADERSHIP |
| `/pending` | List pending approvals | LEADERSHIP |

### Universal Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/help` | Show available commands | PUBLIC |
| `/myinfo` | Show user information | PLAYER |

## Testing Strategy

### Unit Tests
- Test command registration with different chat types
- Test tool selection based on context
- Test permission validation

### Integration Tests
- Test end-to-end registration flows
- Test command routing in different chat contexts
- Test agent tool selection

### E2E Tests
- Test actual Telegram bot behavior
- Test user experience in both chat types
- Test data persistence and categorization

## Future Enhancements

### Potential Improvements
1. **Role-based registration**: Support for specific team roles
2. **Bulk registration**: Register multiple users at once
3. **Registration templates**: Predefined registration forms
4. **Approval workflows**: Multi-step approval processes
5. **Integration with external systems**: FA registration, payment systems

### Extensibility
- Easy to add new chat types
- Simple to add new registration tools
- Flexible command routing system
- Scalable agent architecture

## Conclusion

This clean design ensures that the registration system properly distinguishes between player registration and team member registration based on chat context. The separate implementations follow clean architecture principles and provide a predictable, maintainable, and secure user experience. 