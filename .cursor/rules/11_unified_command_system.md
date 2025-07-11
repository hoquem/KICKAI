# Unified Command System

## Overview

The KICKAI system implements a clean, maintainable command architecture using proven design patterns. This replaces multiple overlapping routing systems with a single, clean architecture that provides consistent command processing, permission management, and error handling.

## Design Patterns Used

### 1. Command Pattern - Command Objects

**Purpose**: Each command is a separate object that encapsulates the action and its parameters.

**Implementation**: Abstract `Command` base class with concrete command implementations.

**Benefits**:
- Encapsulation of command logic
- Easy to add new commands
- Consistent command structure
- Testable in isolation

```python
class Command(ABC):
    def __init__(self, name: str, description: str, permission_level: PermissionLevel):
        self.name = name
        self.description = description
        self.permission_level = permission_level
        self._permission_strategy = self._get_permission_strategy()
    
    @abstractmethod
    async def execute(self, context: CommandContext) -> CommandResult:
        pass
```

### 2. Strategy Pattern - Permission Strategies

**Purpose**: Different permission strategies for different access levels.

**Implementation**: `PermissionStrategy` abstract base class with concrete implementations.

**Benefits**:
- Flexible permission management
- Easy to add new permission levels
- Clear separation of permission logic
- Testable permission strategies

```python
class PermissionStrategy(ABC):
    @abstractmethod
    def can_execute(self, context: CommandContext) -> bool:
        pass
    
    @abstractmethod
    def get_access_denied_message(self, context: CommandContext) -> str:
        pass

class LeadershipPermissionStrategy(PermissionStrategy):
    def can_execute(self, context: CommandContext) -> bool:
        return context.chat_type == ChatType.LEADERSHIP
```

### 3. Chain of Responsibility - Command Processing

**Purpose**: Process commands through a chain of handlers.

**Implementation**: Command processing chain with validation, permission checking, and execution.

**Benefits**:
- Modular command processing
- Easy to add processing steps
- Clear processing flow
- Flexible processing pipeline

```python
class CommandProcessor:
    def __init__(self, command_registry: CommandRegistry):
        self.command_registry = command_registry
        self._setup_chain()
    
    def _setup_chain(self):
        # Setup processing chain
        pass
```

### 4. Factory Pattern - Command Creation

**Purpose**: Centralize command creation logic.

**Implementation**: `CommandRegistry` with factory methods for command creation.

**Benefits**:
- Centralized command creation
- Easy to register new commands
- Consistent command initialization
- Type-safe command creation

```python
class CommandRegistry:
    def __init__(self):
        self._commands = {}
        self._register_default_commands()
    
    def register_command(self, command: Command):
        self._commands[command.name] = command
```

### 5. Observer Pattern - Command Logging

**Purpose**: Log and monitor command execution.

**Implementation**: Command logging and monitoring system.

**Benefits**:
- Comprehensive command tracking
- Performance monitoring
- Error tracking
- Audit trails

## Command Architecture

### Command Context
```python
@dataclass
class CommandContext:
    user_id: str
    chat_id: str
    chat_type: ChatType
    user_role: str
    team_id: str
    message_text: str
    username: Optional[str] = None
    raw_update: Optional[Any] = None
```

### Command Result
```python
@dataclass
class CommandResult:
    success: bool
    message: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

### Permission Levels
```python
class PermissionLevel(Enum):
    PUBLIC = "public"      # Available to everyone
    PLAYER = "player"      # Available to team members
    LEADERSHIP = "leadership"  # Available in leadership chat
    ADMIN = "admin"        # Available to admins only
```

### Chat Types
```python
class ChatType(Enum):
    MAIN = "main"          # Main team chat
    LEADERSHIP = "leadership"  # Leadership chat
    PRIVATE = "private"    # Private messages
```

## Command Categories

### Player Management Commands
- **`/add`** - Add a new player to the team
- **`/remove`** - Remove a player from the team
- **`/list`** - List all team players
- **`/status`** - Check player status
- **`/approve`** - Approve player for match squad
- **`/reject`** - Reject player from match squad
- **`/pending`** - List players pending approval

### Registration Commands
- **`/register`** - Start player registration process
- **`/invite`** - Generate invitation link for player

### Match Management Commands
- **`/creatematch`** - Create a new match
- **`/listmatches`** - List upcoming matches
- **`/getmatch`** - Get match details
- **`/updatematch`** - Update match information
- **`/deletematch`** - Delete a match

### Communication Commands
- **`/broadcast`** - Send message to team
- **`/invite`** - Invite player to team

### System Commands
- **`/start`** - Start the bot
- **`/help`** - Show help information
- **`/myinfo`** - Show user information
- **`/stats`** - Show team statistics
- **`/background`** - Check background tasks status
- **`/remind`** - Send manual reminder to player

## Command Implementation Examples

### Start Command
```python
class StartCommand(Command):
    def __init__(self):
        super().__init__("/start", "Start the bot", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            message = f"""🤖 WELCOME TO KICKAI BOT!

👋 Hello! I'm your AI-powered football team management assistant.

💡 WHAT I CAN HELP YOU WITH:
• Player registration and management
• Match scheduling and coordination
• Team statistics and analytics
• Communication and notifications"""
            
            return CommandResult(
                success=True,
                message=message
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message="❌ Error starting bot",
                error=str(e)
            )
```

### Add Player Command
```python
class AddPlayerCommand(Command):
    def __init__(self):
        super().__init__("/add", "Add a new player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Extract player information from message
            # Create player in database
            # Return success result
            return CommandResult(
                success=True,
                message="✅ Player added successfully"
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message="❌ Error adding player",
                error=str(e)
            )
```

## Permission Strategies

### Public Permission Strategy
```python
class PublicPermissionStrategy(PermissionStrategy):
    def can_execute(self, context: CommandContext) -> bool:
        return True  # Available to everyone
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return "❌ This command should be available to everyone. Please contact admin."
```

### Player Permission Strategy
```python
class PlayerPermissionStrategy(PermissionStrategy):
    def can_execute(self, context: CommandContext) -> bool:
        return context.user_role in ['player', 'admin', 'captain', 'secretary', 'manager', 'treasurer']
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 This command requires player access.
💡 Contact your team admin for access.

Your Role: {context.user_role.title()}"""
```

### Leadership Permission Strategy
```python
class LeadershipPermissionStrategy(PermissionStrategy):
    def can_execute(self, context: CommandContext) -> bool:
        return context.chat_type == ChatType.LEADERSHIP
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 Leadership commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""
```

## Command Processing Flow

### Message Flow
```
User Message
    ↓
Unified Message Handler
    ↓
Check Message Type
    ↓
Slash Command? → Yes → Unified Command System
    ↓ No
Natural Language? → Yes → Intelligent Router
    ↓ No
Error: Unrecognized message type
```

### Command Processing Chain
```
Command Registry
    ↓
Find Command
    ↓
Permission Check
    ↓
Command Execution
    ↓
Result Generation
    ↓
Response to User
```

### Error Handling
```
Command Execution
    ↓
Try Execute
    ↓
Success? → Yes → Return Success Result
    ↓ No
Catch Exception
    ↓
Log Error
    ↓
Return Error Result
```

## Integration with Access Control

### Chat-Based Access Control
- **Main Chat**: Only read-only commands allowed
- **Leadership Chat**: All commands allowed
- **Private Messages**: Limited command set

### Role-Based Access Control
- **Public**: Available to everyone
- **Player**: Available to team members
- **Leadership**: Available to leadership roles
- **Admin**: Available to admins only

## Benefits

### 1. Clean Architecture
- Clear separation of concerns
- Single responsibility principle
- Easy to understand and maintain
- Consistent command structure

### 2. Extensibility
- Easy to add new commands
- Flexible permission system
- Modular command processing
- Pluggable architecture

### 3. Testability
- Each command can be tested in isolation
- Mock dependencies for testing
- Clear command contracts
- Comprehensive test coverage

### 4. Maintainability
- Consistent error handling
- Centralized command management
- Clear command documentation
- Easy debugging

### 5. User Experience
- Consistent command responses
- Clear error messages
- Helpful feedback
- Intuitive command structure

## Implementation Requirements

### For New Commands
1. **Create Command Class**: Extend `Command` base class
2. **Implement Execute Method**: Add command logic
3. **Set Permission Level**: Choose appropriate permission level
4. **Register Command**: Add to command registry
5. **Add Tests**: Write comprehensive tests
6. **Update Documentation**: Document command usage

### For New Permission Levels
1. **Create Strategy**: Implement new permission strategy
2. **Add to Enum**: Add to `PermissionLevel` enum
3. **Update Factory**: Add strategy to factory method
4. **Add Tests**: Test permission logic
5. **Update Documentation**: Document permission requirements

### For Command Modifications
1. **Update Command**: Modify command implementation
2. **Update Tests**: Update existing tests
3. **Update Documentation**: Update command documentation
4. **Test Integration**: Test with other commands
5. **Validate Permissions**: Ensure permissions still work correctly 