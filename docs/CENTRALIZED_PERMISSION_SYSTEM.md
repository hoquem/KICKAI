# Centralized Permission System

This document describes the centralized permission system that provides a single source of truth for all permission checks in the KICKAI unified processing architecture. All permission messages use plain text with emojis for maximum reliability.

## Overview

The centralized permission system ensures that all permission checks use the same logic and data source, eliminating inconsistencies and providing a unified approach to access control across both slash commands and natural language inputs.

## Key Components

### 1. PermissionService

**Location**: `src/features/system_infrastructure/domain/services/permission_service.py`

**Purpose**: Single source of truth for all permission checking logic in the unified processing pipeline.

**Key Methods**:
- `get_user_permissions()`: Get comprehensive user permissions
- `can_execute_command()`: Check if user can execute a command
- `get_user_role()`: Get user role for backward compatibility
- `get_available_commands()`: Get list of available commands for user
- `get_permission_denied_message()`: Get user-friendly denial messages

### 2. PermissionContext

**Purpose**: Encapsulates all context needed for permission checking in the unified pipeline.

**Fields**:
- `user_id`: Telegram user ID
- `team_id`: Team identifier
- `chat_id`: Telegram chat ID
- `chat_type`: Type of chat (main, leadership, private)
- `username`: Optional Telegram username
- `message_text`: The input message (slash command or natural language)

### 3. UserPermissions

**Purpose**: Comprehensive user permissions information.

**Fields**:
- `user_id`: User identifier
- `team_id`: Team identifier
- `roles`: List of user roles
- `chat_access`: Chat access permissions
- `is_admin`: Whether user is admin
- `is_player`: Whether user is player
- `is_team_member`: Whether user is team member
- `is_first_user`: Whether user is first user
- `can_access_main_chat`: Can access main chat
- `can_access_leadership_chat`: Can access leadership chat

## Permission Levels

### PermissionLevel Enum

```python
class PermissionLevel(Enum):
    PUBLIC = "public"        # Available to everyone
    PLAYER = "player"        # Available to players
    LEADERSHIP = "leadership" # Available to leadership
    ADMIN = "admin"          # Available to admins only
```

### Permission Logic

1. **PUBLIC**: Always allowed
2. **PLAYER**: 
   - User must have `player` role
   - Must be in main chat or leadership chat
3. **LEADERSHIP**:
   - Must be in leadership chat
   - Must have `team_member` role or be `admin`
4. **ADMIN**:
   - Must be in leadership chat
   - Must have `admin` role

## Unified Processing Integration

### **Same Permission Checking for All Inputs**

The centralized permission system ensures that both slash commands and natural language inputs use identical permission checking:

```python
# Both input types converge to the same permission checking:
async def _handle_crewai_processing(self, update, message_text, user_id, chat_id, chat_type, username):
    # Create execution context
    execution_context = {
        'user_id': user_id,
        'team_id': self.team_id,
        'chat_id': chat_id,
        'is_leadership_chat': chat_type == ChatType.LEADERSHIP,
        'username': username,
        'message_text': message_text  # ← Same permission checking regardless of input type
    }
    
    # Execute with CrewAI ← UNIFIED PERMISSION CHECKING
    result = await self.crewai_system.execute_task(message_text, execution_context)
```

### **Benefits of Unified Permission Checking**

1. **Consistent Security**: No bypass of permission system through natural language
2. **Single Source of Truth**: Same permission logic for all input methods
3. **Maintainable**: One permission system to maintain and update
4. **Testable**: Test permission logic once, works for all inputs

## Integration Points

### 1. CrewAI Orchestration Pipeline

**Updated Components**:
- All agents use centralized permission service
- Permission checking happens at orchestration level
- Consistent access control across all agents

**Benefits**:
- Consistent permission checking across all commands
- Single source of truth for user roles
- Unified access denied messages

### 2. Command Registry

**Updated Components**:
- Command registry provides metadata only
- Permission checking delegated to orchestration pipeline
- Context-aware command routing

**Benefits**:
- Clean separation of concerns
- Permission checking at execution time
- Dynamic permission resolution

### 3. Agent Selection

**Updated Components**:
- Agents receive permission context
- Permission-aware agent behavior
- Consistent security across all agents

**Benefits**:
- Agents can adapt behavior based on permissions
- Secure agent execution
- Context-aware responses

## Permission Checking Flow

### Unified Processing Flow

```
User sends input (slash command or natural language)
    ↓
Unified CrewAI Processing Pipeline
    ↓
Permission Context Creation
    ↓
PermissionService.get_user_permissions()
    ↓
PermissionService.can_execute_command()
    ↓
Agent Selection and Execution
    ↓
Return result or denial message
```

### Permission Resolution Flow

```
PermissionService.get_user_permissions()
    ↓
Get team member from database
    ↓
Extract roles and chat access
    ↓
Determine permission flags
    ↓
Return UserPermissions object
```

## Command Availability

### Available Commands by Permission Level

#### Public Commands
- `/help` - Show help information
- `/start` - Start the bot
- `/register` - Register as a new player

#### Player Commands
- `/list` - List players (context-aware)
- `/myinfo` - Get your player information
- `/status` - Check player status (context-aware)

#### Leadership Commands
- `/add` - Add a new player
- `/pending` - List pending approvals
- `/announce` - Send announcement

#### Admin Commands
- `/approve` - Approve player registration (admin only)
- `/reject` - Reject player registration (admin only)
- `/promote` - Promote user to admin (admin only)

## Context-Aware Command Behavior

### **Separate Implementations for Different Contexts**

Commands can have different implementations for different chat contexts while maintaining the same permission checking:

```python
# Main Chat Implementation
@command(name="/list", description="List active players", chat_type="main")
async def list_players_main(update, context):
    """List only active players in main chat."""
    # Same permission checking as leadership chat
    players = await get_active_players()
    return format_player_list(players, show_status=False)

# Leadership Chat Implementation  
@command(name="/list", description="List all players with status", chat_type="leadership")
async def list_players_leadership(update, context):
    """List all players with detailed status in leadership chat."""
    # Same permission checking as main chat
    players = await get_all_players()
    return format_player_list(players, show_status=True, show_details=True)
```

## Integration with Chat Role Assignment

### Automatic Role Assignment

The centralized permission system integrates with the chat role assignment service:

1. **User joins main chat** → Automatically becomes `player`
2. **User joins leadership chat** → Automatically becomes `team_member`
3. **First user** → Automatically becomes `admin`
4. **Last admin leaves** → Auto-promotes longest-tenured leadership member

### Dynamic Role Resolution

```python
# Permission service dynamically resolves roles
async def get_user_permissions(user_id: str, team_id: str, chat_type: str) -> UserPermissions:
    # Get team member record
    team_member = await get_team_member(user_id, team_id)
    
    # Determine roles based on chat membership and team member record
    roles = []
    if team_member:
        if team_member.is_first_user:
            roles.extend(['admin', 'team_member', 'player'])
        elif team_member.is_admin:
            roles.extend(['admin', 'team_member', 'player'])
        elif team_member.is_team_member:
            roles.extend(['team_member', 'player'])
        elif team_member.is_player:
            roles.append('player')
    
    return UserPermissions(
        user_id=user_id,
        team_id=team_id,
        roles=roles,
        is_admin='admin' in roles,
        is_team_member='team_member' in roles,
        is_player='player' in roles
    )
```

## Security Benefits

### **Unified Security Model**

1. **No Permission Bypass**: Natural language cannot bypass permission system
2. **Consistent Access Control**: Same rules apply to all input methods
3. **Context-Aware Security**: Permissions adapt to chat context
4. **Role-Based Security**: Access based on user roles and chat membership

### **Audit Trail**

All permission checks are logged for security auditing:

```python
# Permission checking with audit logging
async def can_execute_command(self, command_name: str, context: PermissionContext) -> bool:
    user_perms = await self.get_user_permissions(context.user_id, context.team_id, context.chat_type)
    
    # Log permission check
    logger.info(f"Permission check: {command_name} for user {context.user_id} in {context.chat_type}")
    
    # Check permission
    can_execute = self._check_permission(command_name, user_perms, context)
    
    # Log result
    logger.info(f"Permission result: {can_execute} for {command_name}")
    
    return can_execute
```

## Testing

### **Unified Permission Testing**

Test permission checking works consistently across all input methods:

```python
# Test slash command permission
result1 = await test_command("/list", user_id, chat_type)

# Test natural language permission (should be identical)
result2 = await test_command("show me the player list", user_id, chat_type)

# Verify same permission checking applies
assert result1.permission_check == result2.permission_check
```

This centralized permission system ensures consistent, secure, and maintainable access control across the entire KICKAI system! 🚀 