# Unified Command System

## Overview


The KICKAI system implements a **unified command system** that serves as the single source of truth for all command definitions, permissions, and usage. This document is the **authoritative reference** for all command-related information.


## Command Architecture

### Unified Processing Pipeline
All commands (both slash commands and natural language) use the same processing pipeline:

```
User Input (Slash Command or Natural Language)
    ↓
Unified Message Handler
    ↓
Command Registry Lookup
    ↓
Permission Level Check
    ↓
Chat Type Validation
    ↓
Role Validation
    ↓
Command Execution
    ↓
Response Generation
```

### Command Definition Structure
```python
@dataclass(frozen=True)
class CommandDefinition:
    name: str                           # Command name (e.g., "/help")
    description: str                    # Human-readable description
    permission_level: PermissionLevel   # Required permission level
    chat_types: frozenset[ChatType]     # Allowed chat types
    examples: Tuple[str, ...]           # Usage examples
    feature: str                        # Feature module
```

## Complete Command Reference

### **PUBLIC Commands** (Available to Everyone)
| Command | Description | Chat Types | Examples | Feature |
|---------|-------------|------------|----------|---------|
| `/help` | Show available commands | All chats | `/help`, `/help register` | shared |
| `/list` | List team members/players (context-aware) | Main, Leadership | `/list`, `/list players` | shared |
| `/update` | Update your information | Main, Leadership | `/update phone 07123456789` | shared |
| `/info` | Show user information | All chats | `/info`, `/myinfo` | shared |
| `/ping` | Check bot status | All chats | `/ping` | shared |
| `/version` | Show bot version | All chats | `/version` | shared |

### **PLAYER Commands** (Main Chat Only)
| Command | Description | Chat Types | Examples | Feature |
|---------|-------------|------------|----------|---------|
| `/myinfo` | View your player information | Main only | `/myinfo` | shared |
| `/status` | Check your current status | Main only | `/status`, `/status MH123` | shared |
| `/markattendance` | Mark attendance for a match | Main, Leadership | `/markattendance yes` | attendance_management |
| `/attendance` | View match attendance | Main, Leadership | `/attendance`, `/attendance MATCH123` | attendance_management |
| `/attendancehistory` | View attendance history | Main, Leadership | `/attendancehistory 2024` | attendance_management |

### **LEADERSHIP Commands** (Leadership Chat Only)
| Command | Description | Chat Types | Examples | Feature |
|---------|-------------|------------|----------|---------|
| `/approve` | Approve a player for matches | Leadership only | `/approve`, `/approve MH123` | player_registration |
| `/reject` | Reject a player application | Leadership only | `/reject MH123 reason` | player_registration |
| `/pending` | List players awaiting approval | Leadership only | `/pending` | player_registration |
| `/addplayer` | Add a player directly | Leadership only | `/addplayer John Smith 07123456789` | player_registration |
| `/addmember` | Add a team member | Leadership only | `/addmember John Smith 07123456789 manager` | team_administration |
| `/creatematch` | Create a new match | Leadership only | `/creatematch vs Team B 2024-01-15` | match_management |
| `/selectsquad` | Select match squad | Leadership only | `/selectsquad MATCH123` | match_management |
| `/updatematch` | Update match information | Leadership only | `/updatematch MATCH123` | match_management |
| `/deletematch` | Delete a match | Leadership only | `/deletematch MATCH123` | match_management |
| `/availableplayers` | Get available players for match | Leadership only | `/availableplayers MATCH123` | match_management |
| `/attendanceexport` | Export attendance data | Leadership only | `/attendanceexport MATCH123` | attendance_management |
| `/announce` | Send announcement to team | Leadership only | `/announce Important match tomorrow` | communication |
| `/remind` | Send reminder to players | Leadership only | `/remind Match in 2 hours` | communication |
| `/broadcast` | Broadcast message to all chats | Leadership only | `/broadcast Emergency message` | communication |

## Permission Levels

### Permission Level Definitions
| Level | Description | Access Requirements |
|-------|-------------|-------------------|
| **PUBLIC** | Available to everyone | No restrictions |
| **PLAYER** | Available to registered players | Player role + Main chat only |
| **LEADERSHIP** | Available to team leadership | Team member role + Leadership chat |
| **ADMIN** | Available to team admins | Admin role + Leadership chat |
| **SYSTEM** | Available to system only | Internal system operations |

### Chat Type Access Control
| Chat Type | Purpose | Available Commands |
|-----------|---------|-------------------|
| **Main Chat** | General team communication | Public + Player commands only |
| **Leadership Chat** | Administrative operations | All commands (Public + Player + Leadership + Admin) |
| **Private Chat** | Individual interactions | Public commands + limited player commands |

## Command Registration System

### Automatic Command Discovery
The system automatically discovers commands from feature modules:

```python
# Command discovery process
1. Scan feature directories for @command decorators
2. Extract command metadata (name, description, permission level)
3. Register commands in centralized registry
4. Build lookup dictionaries by permission, chat type, and feature
```

### Command Registry Structure
```python
# Lookup dictionaries
COMMANDS_BY_NAME = {cmd.name: cmd for cmd in ALL_COMMANDS}
COMMANDS_BY_PERMISSION = {level: [cmd for cmd in ALL_COMMANDS if cmd.permission_level == level]}
COMMANDS_BY_CHAT_TYPE = {chat_type: [cmd for cmd in ALL_COMMANDS if chat_type in cmd.chat_types]}
COMMANDS_BY_FEATURE = {feature: [cmd for cmd in ALL_COMMANDS if cmd.feature == feature]}
```

## Permission Checking

### Permission Service Implementation
```python
class PermissionService:
    async def can_execute_command(
        self, 
        permission_level: PermissionLevel, 
        context: PermissionContext
    ) -> bool:
        """Main permission checking method used by all commands."""
        user_perms = await self.get_user_permissions(context.telegram_id, context.team_id)

        if permission_level == PermissionLevel.PUBLIC:
            return True

        elif permission_level == PermissionLevel.PLAYER:
            if not user_perms.is_player:
                return False
            return context.chat_type == ChatType.MAIN

        elif permission_level == PermissionLevel.LEADERSHIP:
            if context.chat_type != ChatType.LEADERSHIP:
                return False
            return user_perms.is_team_member or user_perms.is_admin

        elif permission_level == PermissionLevel.ADMIN:
            if context.chat_type != ChatType.LEADERSHIP:
                return False
            return user_perms.is_admin

        return False
```

### Context-Aware Access Denied Messages
```python
# Player Permission Denied
❌ Access Denied
🔒 This command requires player access.
💡 Contact your team admin for access.
Your Role: {user_role.title()}

# Leadership Permission Denied
❌ Access Denied
🔒 Leadership commands are only available in the leadership chat.
💡 Please use the leadership chat for this function.

# Admin Permission Denied
❌ Access Denied
🔒 This command requires admin access.
💡 Contact your team admin for access.
Your Role: {user_role.title()}
```

## Command Categories by Feature

### **Shared Commands** (Core system functionality)
- `/help`, `/list`, `/update`, `/info`, `/ping`, `/version`, `/myinfo`, `/status`

### **Player Registration** (Player management)
- `/approve`, `/reject`, `/pending`, `/addplayer`

### **Team Administration** (Team member management)
- `/addmember`

### **Match Management** (Match operations)
- `/creatematch`, `/selectsquad`, `/updatematch`, `/deletematch`, `/availableplayers`

### **Attendance Management** (Attendance tracking)
- `/markattendance`, `/attendance`, `/attendancehistory`, `/attendanceexport`

### **Communication** (Team communication)
- `/announce`, `/remind`, `/broadcast`

## Natural Language Integration

### Intent Mapping
Natural language requests are automatically mapped to equivalent commands:

```
"Show me the available players" → /list players
"Create a new match against Team B" → /creatematch vs Team B
"Mark my attendance as yes" → /markattendance yes
"Send an announcement about tomorrow's match" → /announce Important match tomorrow
```

### Unified Security
- **Same Permission Checking**: Natural language uses identical permission validation
- **Context Awareness**: Chat type and role validation applied consistently
- **Audit Logging**: All access attempts logged regardless of input method

## Command Development Guidelines

### **Adding New Commands**
1. **Define Command**: Create command definition with appropriate permission level
2. **Set Chat Types**: Specify which chat types can access the command
3. **Add Examples**: Provide clear usage examples
4. **Test Permissions**: Verify access control works correctly
5. **Update This Document**: Add command to appropriate table above

### **Command Naming Conventions**
- **Use descriptive names**: `/creatematch` not `/cm`
- **Use lowercase**: `/addplayer` not `/AddPlayer`
- **Use action-oriented names**: `/approve`, `/reject`, `/markattendance`
- **Be consistent**: Similar commands use similar patterns

### **Permission Level Guidelines**
- **PUBLIC**: Basic system commands, help, version
- **PLAYER**: Player-specific operations, personal information
- **LEADERSHIP**: Administrative operations, team management
- **ADMIN**: System configuration, sensitive operations
- **SYSTEM**: Internal operations, health checks

## Testing Requirements

### **Command Testing Checklist**
- [ ] Command works in appropriate chat types
- [ ] Permission checking works correctly
- [ ] Access denied messages are user-friendly
- [ ] Examples work as documented
- [ ] Natural language mapping works
- [ ] Error handling is graceful

### **Permission Testing**
- **Public Commands**: Available in all chat types
- **Player Commands**: Available only in main chat for players
- **Leadership Commands**: Available only in leadership chat for team members
- **Admin Commands**: Available only in leadership chat for admins

## Integration with Agent System

### **Agent Command Routing**
Commands are automatically routed to appropriate agents based on permission level:

- **PUBLIC/PLAYER Commands**: `HELP_ASSISTANT` or `PLAYER_COORDINATOR`
- **LEADERSHIP Commands**: `TEAM_ADMINISTRATOR` or `SQUAD_SELECTOR`
- **ADMIN Commands**: `TEAM_ADMINISTRATOR`
- **SYSTEM Commands**: `MESSAGE_PROCESSOR`

### **Agent Tool Integration**
Each agent has access to specific tools based on their role:


```python
# Example: PLAYER_COORDINATOR tools
- get_my_status
- get_player_status
- get_active_players
- approve_player
- register_player

# Example: TEAM_ADMINISTRATOR tools
- get_team_members
- add_team_member_role
- promote_team_member_to_admin
- remove_team_member_role
```

## Benefits of Unified Command System

### **1. Consistency**
- **Single Source of Truth**: All command information in one place
- **Unified Processing**: Same pipeline for all commands
- **Consistent Permissions**: Identical permission checking across all commands

### **2. Maintainability**
- **Easy Updates**: Change command information in one location
- **Clear Documentation**: Comprehensive command reference
- **Simple Testing**: Standardized testing approach

### **3. User Experience**
- **Predictable Behavior**: Commands work consistently
- **Clear Feedback**: User-friendly error messages
- **Intuitive Access**: Natural permission escalation

### **4. Developer Experience**
- **Clear Guidelines**: Well-defined development patterns
- **Easy Extension**: Simple process for adding new commands
- **Comprehensive Reference**: Complete command documentation 
