# Centralized Permission System

This document describes the centralized permission system that provides a single source of truth for all permission checks in the KICKAI system.

## Overview

The centralized permission system ensures that all permission checks use the same logic and data source, eliminating inconsistencies and providing a unified approach to access control.

## Key Components

### 1. PermissionService

**Location**: `src/features/system_infrastructure/domain/services/permission_service.py`

**Purpose**: Single source of truth for all permission checking logic.

**Key Methods**:
- `get_user_permissions()`: Get comprehensive user permissions
- `can_execute_command()`: Check if user can execute a command
- `get_user_role()`: Get user role for backward compatibility
- `get_available_commands()`: Get list of available commands for user
- `get_permission_denied_message()`: Get user-friendly denial messages

### 2. PermissionContext

**Purpose**: Encapsulates all context needed for permission checking.

**Fields**:
- `user_id`: Telegram user ID
- `team_id`: Team identifier
- `chat_id`: Telegram chat ID
- `chat_type`: Type of chat (main, leadership, private)
- `username`: Optional Telegram username

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

## Integration Points

### 1. Unified Command System

**Updated Components**:
- `PermissionStrategy` classes now use centralized service
- `CommandProcessor` uses centralized service for role resolution
- `HelpCommand` uses centralized service for available commands

**Benefits**:
- Consistent permission checking across all commands
- Single source of truth for user roles
- Unified access denied messages

### 2. Simplified Message Handler

**Updated Components**:
- `PermissionChecker` uses centralized service
- Chat-based and command-specific permission checking unified

**Benefits**:
- Consistent permission checking in message processing
- Better error messages for users

### 3. Utility Operations Adapter

**Updated Components**:
- `get_user_role()` method uses centralized service

**Benefits**:
- Consistent role resolution across all adapters
- Integration with new chat-based role assignment

## Permission Checking Flow

### Command Execution Flow

```
User sends command
    ↓
CommandProcessor.process_command()
    ↓
Get user permissions (PermissionService.get_user_permissions())
    ↓
Check command permissions (PermissionService.can_execute_command())
    ↓
Execute command or return denial message
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

#### Player Commands
- `/list` - List all players
- `/myinfo` - Get your player information
- `/update` - Update your player information
- `/status` - Check player status
- `/register` - Register as a new player
- `/listmatches` - List all matches
- `/getmatch` - Get match details
- `/stats` - Show team statistics
- `/payment_status` - Get payment status
- `/pending_payments` - Get pending payments
- `/payment_history` - Get payment history
- `/payment_help` - Get payment help
- `/financial_dashboard` - View financial dashboard
- `/attend` - Confirm match attendance
- `/unattend` - Cancel match attendance

#### Leadership Commands
- `/add` - Add a new player
- `/remove` - Remove a player
- `/approve` - Approve a player
- `/reject` - Reject a player
- `/pending` - List pending approvals
- `/checkfa` - Check FA registration
- `/dailystatus` - Get daily status
- `/background` - Run background tasks
- `/remind` - Send reminders
- `/newmatch` - Create new match
- `/updatematch` - Update match
- `/deletematch` - Delete match
- `/record_result` - Record match result
- `/invitelink` - Generate invitation
- `/broadcast` - Broadcast message
- `/create_match_fee` - Create match fee
- `/create_membership_fee` - Create membership fee
- `/create_fine` - Create fine
- `/payment_stats` - Get payment stats
- `/announce` - Send announcement
- `/injure` - Mark player injured
- `/suspend` - Suspend player
- `/recover` - Mark player recovered
- `/refund_payment` - Refund payment
- `/record_expense` - Record expense

#### Admin Commands
- `/promote` - Promote user to admin (admin only)

## Integration with Chat Role Assignment

### Automatic Role Assignment

The centralized permission system integrates with the chat role assignment service:

1. **User joins main chat** → Automatically becomes `player`
2. **User joins leadership chat** → Automatically becomes `team_member`
3. **First user** → Automatically becomes `admin`
4. **Last admin leaves** → Longest-tenured leadership member promoted to `admin`

### Permission Updates

When roles are assigned or changed:
1. Chat role assignment service updates team member record
2. Permission service reads updated roles
3. All permission checks automatically reflect new permissions

## Error Handling

### Graceful Degradation

The permission system includes robust error handling:

1. **Database errors**: Return default permissions
2. **Missing users**: Return empty permissions
3. **Invalid roles**: Filter out invalid roles
4. **Service unavailability**: Use fallback logic

### User-Friendly Messages

Permission denied messages are generated dynamically:

1. **Role-based messages**: Explain required roles
2. **Chat-based messages**: Explain required chat access
3. **Context-aware messages**: Include user's current roles

## Testing

### Test Script

A comprehensive test script is available at `scripts/test_permission_system.py` that verifies:

1. Initial user permissions
2. Role assignment through chat membership
3. Command permission checking
4. Available command listing
5. Permission denied messages
6. Backward compatibility

### Running Tests

```bash
python scripts/test_permission_system.py
```

## Benefits

### 1. Single Source of Truth

- All permission checks use the same logic
- Consistent user experience
- Easier to maintain and debug

### 2. Integration with Role Assignment

- Automatic permission updates when roles change
- Seamless integration with chat-based assignment
- No manual permission synchronization needed

### 3. Extensibility

- Easy to add new permission levels
- Easy to modify permission logic
- Easy to add new permission checks

### 4. Consistency

- Same permission logic across all components
- Consistent error messages
- Consistent user feedback

### 5. Maintainability

- Centralized permission logic
- Clear separation of concerns
- Easy to test and debug

## Future Enhancements

### Potential Improvements

1. **Role Hierarchy**: Implement role precedence and inheritance
2. **Temporary Permissions**: Support for time-limited permissions
3. **Permission Auditing**: Track permission changes and reasons
4. **Bulk Operations**: Support for bulk permission assignments
5. **Custom Permissions**: Allow teams to define custom permissions
6. **Permission Templates**: Predefined permission sets for different team types

### Performance Optimizations

1. **Caching**: Cache user permissions for better performance
2. **Batch Operations**: Batch permission checks for multiple users
3. **Lazy Loading**: Load permissions only when needed
4. **Indexing**: Optimize database queries for permission checks

This centralized permission system ensures that all permission checks in the KICKAI system are consistent, maintainable, and integrated with the chat-based role assignment system. 