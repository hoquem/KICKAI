# Unified Command System

## Overview

The KICKAI system implements a clean, maintainable command architecture using proven design patterns. This replaces multiple overlapping routing systems with a single, clean architecture that provides consistent command processing, permission management, and error handling.

## Current Implementation Status

### ✅ **Fully Implemented Commands**

#### Core Commands
- `/help` - Show available commands (PUBLIC)
- `/myinfo` - Show personal information (PUBLIC)
- `/status` - Check player/team member status (PUBLIC)
- `/list` - List players/team members (context-aware) (PUBLIC)
- `/update` - Update personal information (PUBLIC)
- `/ping` - Check bot status (PUBLIC)
- `/version` - Show bot version (PUBLIC)

#### Leadership Commands
- `/addplayer` - Add a new player (LEADERSHIP)
- `/addmember` - Add a team member (LEADERSHIP)
- `/approve` - Approve a player (LEADERSHIP)
- `/reject` - Reject a player application (LEADERSHIP)
- `/pending` - List players awaiting approval (LEADERSHIP)

#### Match Management Commands
- `/creatematch` - Create a new match (LEADERSHIP)
- `/listmatches` - List upcoming matches (PLAYER)
- `/matchdetails` - Get match details (PLAYER)
- `/selectsquad` - Select match squad (LEADERSHIP)
- `/updatematch` - Update match information (LEADERSHIP)
- `/deletematch` - Delete a match (LEADERSHIP)
- `/availableplayers` - Get available players for match (LEADERSHIP)

#### Attendance Management Commands
- `/markattendance` - Mark attendance for a match (PLAYER)
- `/attendance` - View match attendance (PLAYER)
- `/attendancehistory` - View attendance history (PLAYER)
- `/attendanceexport` - Export attendance data (LEADERSHIP)

#### Payment Management Commands
- `/createpayment` - Create a new payment (LEADERSHIP)
- `/payments` - View payment history (LEADERSHIP)
- `/budget` - View budget information (LEADERSHIP)
- `/markpaid` - Mark payment as paid (LEADERSHIP)
- `/paymentexport` - Export payment data (LEADERSHIP)

#### Communication Commands
- `/announce` - Send announcement to team (LEADERSHIP)
- `/remind` - Send reminder to players (LEADERSHIP)
- `/broadcast` - Broadcast message to all chats (LEADERSHIP)

### 🚧 **Partially Implemented Commands**

#### Training Management Commands
**Status**: Commands defined in `training_commands.py` but not integrated into main command system

- `/scheduletraining` - Schedule a training session (LEADERSHIP)
- `/listtrainings` - List upcoming training sessions (PLAYER)
- `/marktraining` - Mark attendance for training session (PLAYER)
- `/canceltraining` - Cancel a training session (LEADERSHIP)
- `/trainingstats` - Show training statistics (PLAYER)
- `/mytrainings` - Show personal training schedule (PLAYER)

**Missing Integration**:
- Training commands not added to `constants.py` command definitions
- Training commands not registered in main command registry
- Training tools not integrated with agent system

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
```

## Command Registration Pattern

### Current Implementation

Commands are registered using decorators and delegate to CrewAI agents:

```python
@command(
    name="/help",
    description="Show available commands",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PUBLIC,
    feature="shared",
    chat_type=ChatType.MAIN,
)
async def handle_help_command(update, context, **kwargs):
    """Handle /help command."""
    # This will be handled by the agent system
    return None
```

### Command Definition Structure

Commands are defined in `kickai/core/constants.py` using `CommandDefinition` dataclass:

```python
@dataclass(frozen=True)
class CommandDefinition:
    name: str
    description: str
    permission_level: PermissionLevel
    chat_types: frozenset[ChatType]
    examples: tuple[str, ...] = field(default_factory=tuple)
    feature: str = "shared"
```

### Example Command Definitions

```python
SYSTEM_COMMANDS = {
    CommandDefinition(
        name="/help",
        description="Show available commands",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP, ChatType.PRIVATE]),
        examples=("/help", "/help register"),
        feature="shared",
    ),
    CommandDefinition(
        name="/list",
        description="List team members or players (context-aware)",
        permission_level=PermissionLevel.PUBLIC,
        chat_types=frozenset([ChatType.MAIN, ChatType.LEADERSHIP]),
        examples=("/list", "/list players", "/list members"),
        feature="shared",
    ),
}
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

## Next Steps for Training Management Integration

### 1. Add Training Commands to Constants
```python
TRAINING_COMMANDS = {
    CommandDefinition(
        name="/scheduletraining",
        description="Schedule a training session",
        permission_level=PermissionLevel.LEADERSHIP,
        chat_types=frozenset([ChatType.LEADERSHIP]),
        examples=("/scheduletraining", "/scheduletraining Technical 2024-01-15 18:00"),
        feature="training_management",
    ),
    # ... other training commands
}
```

### 2. Update ALL_COMMANDS Collection
```python
ALL_COMMANDS = (
    PLAYER_COMMANDS
    | LEADERSHIP_COMMANDS
    | SYSTEM_COMMANDS
    | MATCH_COMMANDS
    | ATTENDANCE_COMMANDS
    | PAYMENT_COMMANDS
    | COMMUNICATION_COMMANDS
    | TEAM_ADMIN_COMMANDS
    | TRAINING_COMMANDS  # Add this line
)
```

### 3. Integrate Training Tools with Agents
- Register training tools with agent system
- Update agent configurations to include training tools
- Test training command execution through agents

### 4. Add E2E Tests
- Create training management E2E test suite
- Test training session creation and management
- Test attendance tracking functionality 