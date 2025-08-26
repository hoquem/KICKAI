# Access Control & Permission System

## Overview

The KICKAI system implements a **simplified yet comprehensive access control system** based on permission levels, chat types, and user roles. This ensures secure and appropriate access to different commands and features while maintaining a clean, maintainable architecture.

## Core Permission Architecture

### Permission Levels
The system uses five distinct permission levels, each with specific access requirements:

| Permission Level | Description | Access Requirements |
|------------------|-------------|-------------------|
| **PUBLIC** | Available to everyone | No restrictions |
| **PLAYER** | Available to registered players | Player role + Main chat only |
| **LEADERSHIP** | Available to team leadership | Team member role + Leadership chat |
| **ADMIN** | Available to team admins | Admin role + Leadership chat |
| **SYSTEM** | Available to system only | Internal system operations |

### Chat-Based Access Control
The system implements **context-aware permissions** based on chat type:

#### **Main Chat** (`ChatType.MAIN`)
- **Purpose**: General team communication and player operations
- **Access**: Public commands + Player commands only
- **Restrictions**: Leadership and admin commands blocked

#### **Leadership Chat** (`ChatType.LEADERSHIP`)
- **Purpose**: Administrative operations and team management
- **Access**: All commands (Public + Player + Leadership + Admin)
- **Features**: Full administrative capabilities

#### **Private Chat** (`ChatType.PRIVATE`)
- **Purpose**: Individual user interactions
- **Access**: Public commands + limited player commands
- **Features**: Personal information and basic operations

## Permission Service Implementation

### Core Permission Checking
```python
class PermissionService:
    async def can_execute_command(
        self, 
        permission_level: PermissionLevel, 
        context: PermissionContext
    ) -> bool:
        """
        Main permission checking method used by all commands.
        """
        # Get user permissions
        user_perms = await self.get_user_permissions(context.telegram_id, context.team_id)

        # Check permission level
        if permission_level == PermissionLevel.PUBLIC:
            return True  # Public commands are always allowed

        elif permission_level == PermissionLevel.PLAYER:
            # Player commands require player role and main chat access only
            if not user_perms.is_player:
                return False
            # Must be in main chat only (not leadership chat)
            return context.chat_type == ChatType.MAIN

        elif permission_level == PermissionLevel.LEADERSHIP:
            # Leadership commands require leadership chat access
            if context.chat_type != ChatType.LEADERSHIP:
                return False
            # Must have team member role or be admin
            return user_perms.is_team_member or user_perms.is_admin

        elif permission_level == PermissionLevel.ADMIN:
            # Admin commands require leadership chat access and admin role
            if context.chat_type != ChatType.LEADERSHIP:
                return False
            return user_perms.is_admin

        return False
```

### Context-Aware Permission Messages
The system provides **user-friendly access denied messages** based on context:

#### **Player Permission Denied**
```
❌ Access Denied

🔒 This command requires player access.
💡 Contact your team admin for access.

Your Role: {user_role.title()}
```

#### **Leadership Permission Denied**
```
❌ Access Denied

🔒 Leadership commands are only available in the leadership chat.
💡 Please use the leadership chat for this function.
```

#### **Admin Permission Denied**
```
❌ Access Denied

🔒 This command requires admin access.
💡 Contact your team admin for access.

Your Role: {user_role.title()}
```

## Command Reference

**📋 For complete command information, see [11_unified_command_system.md](11_unified_command_system.md)**

This file focuses on access control and permissions. The complete command reference with all commands, examples, and usage is maintained in the unified command system documentation.

## User Role System

### Role Hierarchy
The system supports a **simplified role hierarchy** with clear access patterns:

```python
# Role definitions
PLAYER_ROLES = {'player'}
LEADERSHIP_ROLES = {'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer', 'secretary'}

# Permission mapping
user_perms = {
    'is_player': user_has_player_role,
    'is_team_member': user_has_leadership_role,
    'is_admin': user_has_admin_role,
    'roles': user_roles_list
}
```

### Role Validation
- **Player Role**: Basic team member with access to player commands
- **Team Member Role**: Leadership roles with access to administrative functions
- **Admin Role**: Highest level with full system access
- **Multiple Roles**: Users can have multiple roles simultaneously

## Integration with Command System

### Unified Command Processing
All commands use the **same permission checking pipeline**:

```
User Command
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

### Automatic Permission Detection
The system **automatically determines permission levels** based on command names:

```python
def _determine_permission_level(self, function_name: str, feature_name: str) -> PermissionLevel:
    """Determine permission level based on function name and feature."""
    function_lower = function_name.lower()

    # Admin commands
    if any(keyword in function_lower for keyword in ["admin", "approve", "reject", "delete"]):
        return PermissionLevel.ADMIN

    # Leadership commands
    if any(keyword in function_lower for keyword in ["leadership", "team", "squad", "announce"]):
        return PermissionLevel.LEADERSHIP

    # Player commands
    if any(keyword in function_lower for keyword in ["player", "register", "status", "myinfo"]):
        return PermissionLevel.PLAYER

    # System commands
    if any(keyword in function_lower for keyword in ["system", "health", "config"]):
        return PermissionLevel.SYSTEM

    # Default to public
    return PermissionLevel.PUBLIC
```

## Security Features

### **Unified Security Pipeline**
- **Consistent Permission Checking**: All commands use the same permission service
- **Context-Aware Validation**: Chat type and user role validation
- **Audit Logging**: All permission checks and access attempts logged
- **Fail-Safe Design**: Deny by default, explicit allow patterns

### **Chat-Based Security**
- **Main Chat Isolation**: Player commands only, no administrative access
- **Leadership Chat Control**: Full administrative access for authorized users
- **Private Chat Limitations**: Restricted command set for individual users

### **Role-Based Security**
- **Hierarchical Permissions**: Clear permission escalation path
- **Role Validation**: Enforced role checking at runtime
- **Multi-Role Support**: Users can have multiple roles with appropriate access

## Implementation Guidelines

### **Adding New Commands**
1. **Define Command**: Create command definition with appropriate permission level
2. **Set Chat Types**: Specify which chat types can access the command
3. **Add Examples**: Provide clear usage examples
4. **Test Permissions**: Verify access control works correctly
5. **Update Documentation**: Document command access requirements

### **Adding New Permission Levels**
1. **Define Level**: Add new permission level to enum
2. **Update Service**: Add permission checking logic
3. **Add Messages**: Create appropriate access denied messages
4. **Update Tests**: Add comprehensive permission testing
5. **Document Changes**: Update this documentation

### **Modifying Chat Access**
1. **Update Chat Types**: Modify command chat type definitions
2. **Test Access**: Verify access control in all chat types
3. **Update Messages**: Modify access denied messages if needed
4. **Notify Users**: Inform users of access changes

## Testing Requirements

### **Permission Testing**
- **Public Commands**: Available in all chat types
- **Player Commands**: Available only in main chat for players
- **Leadership Commands**: Available only in leadership chat for team members
- **Admin Commands**: Available only in leadership chat for admins

### **Chat Type Testing**
- **Main Chat**: Player commands work, leadership commands blocked
- **Leadership Chat**: All commands work for appropriate roles
- **Private Chat**: Limited command set available

### **Role Testing**
- **Player Role**: Access to player commands only
- **Team Member Role**: Access to leadership commands
- **Admin Role**: Access to all commands
- **Multiple Roles**: Appropriate access based on highest role

### **Error Handling Testing**
- **Access Denied Messages**: Proper user feedback
- **Invalid Commands**: Graceful error handling
- **Permission Errors**: Clear error messages
- **System Failures**: Fallback error responses

## Benefits of Simplified Access Control

### **1. Maintainability**
- **Clear Permission Levels**: Five well-defined permission levels
- **Consistent Implementation**: Unified permission checking across all commands
- **Easy to Understand**: Simple role and chat-based access control

### **2. Security**
- **Defense in Depth**: Multiple layers of permission checking
- **Context Awareness**: Chat type and role-based validation
- **Audit Trail**: Comprehensive logging of all access attempts

### **3. User Experience**
- **Clear Feedback**: User-friendly access denied messages
- **Contextual Help**: Appropriate commands shown based on user role
- **Intuitive Access**: Natural permission escalation

### **4. Extensibility**
- **Easy to Add Commands**: Simple command definition structure
- **Flexible Permissions**: Easy to modify permission levels
- **Scalable Architecture**: Supports multiple teams and roles 