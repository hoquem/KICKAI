# Unified Command System - KICKAI Bot

## Overview

The KICKAI bot now uses a **unified command system** that consolidates all commands into a single, clean architecture following the Command Pattern. All commands are implemented in `src/telegram/unified_command_system.py` and follow consistent design patterns.

## Architecture

### Design Patterns Used

1. **Command Pattern**: Each command is a separate object implementing the `Command` interface
2. **Strategy Pattern**: Different permission strategies for different access levels
3. **Chain of Responsibility**: Command routing and validation
4. **Factory Pattern**: Command creation and registration
5. **Observer Pattern**: Command logging and monitoring

### Core Components

- **Command**: Abstract base class for all commands
- **CommandContext**: Context data for command execution
- **CommandResult**: Result of command execution
- **CommandRegistry**: Registry for all available commands
- **CommandProcessor**: Main processor using Chain of Responsibility
- **PermissionStrategy**: Different strategies for access control

## Available Commands

### Utility Commands (Public Access)

| Command | Description | Usage |
|---------|-------------|-------|
| `/start` | Start the bot | `/start` |
| `/help` | Show available commands | `/help` |

### Player Commands (Player Access)

| Command | Description | Usage |
|---------|-------------|-------|
| `/list` | List all players | `/list` |
| `/myinfo` | Get your player information | `/myinfo` |
| `/register` | Register as a new player | `/register John Smith 07123456789 midfielder` |
| `/stats` | Show team statistics | `/stats` |

### Leadership Commands (Leadership Chat Only)

| Command | Description | Usage |
|---------|-------------|-------|
| `/add` | Add a new player | `/add John Smith 07123456789 midfielder` |
| `/remove` | Remove a player | `/remove JS` |
| `/approve` | Approve a player registration | `/approve JS` |
| `/reject` | Reject a player registration | `/reject JS` |
| `/pending` | List pending approvals | `/pending` |
| `/checkfa` | Check FA registration | `/checkfa JS` |
| `/invite` | Invite a player | `/invite 07123456789` |
| `/broadcast` | Broadcast message | `/broadcast Training cancelled tomorrow` |

### Match Commands

| Command | Description | Usage | Access Level |
|---------|-------------|-------|--------------|
| `/newmatch` | Create a new match | `/newmatch Arsenal on July 1st at 2pm` | Leadership |
| `/listmatches` | List all matches | `/listmatches` | Player |
| `/getmatch` | Get match details | `/getmatch MATCH123` | Player |
| `/updatematch` | Update a match | `/updatematch MATCH123 opponent=Arsenal` | Leadership |
| `/deletematch` | Delete a match | `/deletematch MATCH123` | Leadership |

### Admin Commands (Leadership Chat Only)

| Command | Description | Usage |
|---------|-------------|-------|
| `/dailystatus` | Generate daily status report | `/dailystatus` |

## Permission System

### Permission Levels

1. **PUBLIC**: Available to everyone
2. **PLAYER**: Available to registered players
3. **LEADERSHIP**: Available only in leadership chat
4. **ADMIN**: Available only in leadership chat

### Chat-Based Access Control

- **Main Chat**: Public and Player commands only
- **Leadership Chat**: All commands available
- **Private Chat**: Public commands only

## Command Implementation Details

### Command Structure

Each command follows this structure:

```python
class CommandName(Command):
    def __init__(self):
        super().__init__("/commandname", "Description", PermissionLevel.LEVEL)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        # Command logic here
        return CommandResult(success=True, message="Response")
```

### Context Information

The `CommandContext` provides:
- `user_id`: Telegram user ID
- `chat_id`: Chat ID
- `chat_type`: Chat type (MAIN, LEADERSHIP, PRIVATE)
- `user_role`: User role in team
- `team_id`: Team ID
- `message_text`: Full message text
- `username`: Telegram username
- `raw_update`: Raw Telegram update

### Result Format

Commands return `CommandResult` with:
- `success`: Boolean indicating success
- `message`: Response message
- `error`: Error message (if any)
- `metadata`: Additional data (optional)

## Natural Language Processing

The bot also supports natural language commands through the LLM/agentic system:

- "Add John Smith as a midfielder"
- "Create a match against Arsenal on July 1st"
- "Show me the team stats"
- "List all players"

## Integration Points

### Services Used

- **PlayerService**: Player management operations
- **TeamMemberService**: Team member operations
- **FixtureTools**: Match/fixture operations
- **FARegistrationChecker**: FA registration checks
- **DailyStatusService**: Daily status reports

### Database Integration

- **Firebase Firestore**: Primary data storage
- **Real-time updates**: Live data synchronization
- **Team-based isolation**: Data separated by team ID

## Benefits of Unified System

1. **Consistency**: All commands follow the same pattern
2. **Maintainability**: Single location for all command logic
3. **Extensibility**: Easy to add new commands
4. **Testing**: Simplified testing with consistent interfaces
5. **Documentation**: Centralized command documentation
6. **Permission Management**: Unified access control
7. **Logging**: Consistent command logging and monitoring

## Adding New Commands

To add a new command:

1. Create a new class inheriting from `Command`
2. Implement the `execute` method
3. Add the command to the registry in `_register_default_commands`
4. Update this documentation

Example:

```python
class NewCommand(Command):
    def __init__(self):
        super().__init__("/newcommand", "Description", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        # Implementation here
        return CommandResult(success=True, message="Response")
```

## Error Handling

All commands include comprehensive error handling:
- Input validation
- Service error handling
- Graceful fallbacks
- User-friendly error messages
- Detailed logging for debugging

## Performance Considerations

- Commands are lightweight and efficient
- Database queries are optimized
- Caching where appropriate
- Async/await for non-blocking operations
- Minimal memory footprint

## Security Features

- Permission-based access control
- Input validation and sanitization
- Team-based data isolation
- Audit logging for all operations
- Secure credential management 