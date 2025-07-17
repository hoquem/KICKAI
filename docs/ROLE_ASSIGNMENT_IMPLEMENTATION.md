# Role Assignment Implementation

This document describes the implementation of automatic role assignment based on chat membership in the KICKAI system.

## Overview

The role assignment system automatically assigns appropriate roles to users based on which Telegram chats they join, ensuring proper access control and team management.

## Key Components

### 1. ChatRoleAssignmentService

**Location**: `src/features/team_administration/domain/services/chat_role_assignment_service.py`

**Purpose**: Core service that handles automatic role assignment when users join or leave chats.

**Key Methods**:
- `add_user_to_chat()`: Assigns roles when user joins a chat
- `remove_user_from_chat()`: Updates roles when user leaves a chat
- `promote_to_admin()`: Manually promote a user to admin
- `get_user_roles()`: Get comprehensive role information for a user

### 2. Enhanced TeamMemberService

**Location**: `src/features/player_registration/domain/services/team_member_service.py`

**New Methods**:
- `is_first_user()`: Check if this would be the first user in the team
- `get_longest_tenured_leadership_member()`: Get longest-tenured leadership member
- `promote_to_admin()`: Promote user to admin (admin-only)
- `handle_last_admin_leaving()`: Handle when last admin leaves

### 3. Enhanced PlayerService

**Location**: `src/features/player_registration/domain/services/player_service.py`

**New Logic**:
- Automatically assigns admin role to first user during registration
- Integrates with team member service for role management

### 4. ChatMemberHandler

**Location**: `src/bot_telegram/chat_member_handler.py`

**Purpose**: Handles Telegram chat member updates and integrates with role assignment service.

**Features**:
- Detects when users join or leave chats
- Automatically triggers role assignment
- Generates welcome messages for new members
- Logs all role assignment events

## Role Assignment Rules

### Chat-Based Role Assignment

1. **Main Chat Membership**:
   - Users added to main chat become `players`
   - Automatically creates player record if needed

2. **Leadership Chat Membership**:
   - Users added to leadership chat become `team_members`
   - Provides access to leadership discussions and management

3. **Dual Membership**:
   - Users in both chats have both `player` and `team_member` roles
   - Full access to all team features

### First User Admin Assignment

- **First user** of a team automatically becomes `admin`
- Applies when no team members exist in the system
- First user gets all roles: `admin`, `player`, `team_member`

### Auto-Promotion Logic

- When the **last admin leaves** the leadership chat:
  - System automatically promotes the **longest-tenured leadership member**
  - Ensures team always has at least one admin
  - Prevents orphaned teams without leadership

### Manual Admin Promotion

- Existing admins can promote other users to admin using the `/promote <member_id>` command
- Only admins can promote other users
- Promoted users maintain existing roles

## Chat Type Detection

The system detects chat types based on chat titles:

- **Main Chat**: Any chat that doesn't end with "- Leadership"
- **Leadership Chat**: Chats ending with "- Leadership"

Example:
- "KickAI Testing" → Main Chat
- "KickAI Testing - Leadership" → Leadership Chat

## Welcome Messages

The system generates appropriate welcome messages based on:

1. **First User**: Special admin welcome with setup instructions
2. **Main Chat**: Player-focused welcome with registration instructions
3. **Leadership Chat**: Leadership-focused welcome with management info

## Integration Points

### Bot Startup

The chat member handler is registered in `run_bot_local.py`:

```python
from bot_telegram.chat_member_handler import register_chat_member_handler
register_chat_member_handler(application)
```

### Message Processing

The role assignment integrates with existing message processing:

- User context includes role information
- Permission checking uses assigned roles
- Commands respect role-based access control

## Testing

A test script is available at `scripts/test_role_assignment.py` that verifies:

1. First user admin assignment
2. Chat-based role assignment
3. Auto-promotion logic
4. Role removal when leaving chats
5. Welcome message generation

Run the test with:
```bash
python scripts/test_role_assignment.py
```

## Logging and Monitoring

All role assignment events are logged with:

- User ID and username
- Chat type and team ID
- Roles assigned/removed
- First user status
- Admin promotion events

Events are logged using the enhanced logging system for monitoring and debugging.

## Error Handling

The system includes robust error handling:

- Graceful handling of missing users
- Fallback to default roles on errors
- Non-critical errors don't break user experience
- Comprehensive error logging for debugging

## Future Enhancements

Potential improvements for the role assignment system:

1. **Role Hierarchy**: Implement role precedence and inheritance
2. **Temporary Roles**: Support for time-limited role assignments
3. **Role Auditing**: Track role change history and reasons
4. **Bulk Operations**: Support for bulk role assignments
5. **Custom Roles**: Allow teams to define custom roles
6. **Role Templates**: Predefined role sets for different team types

## Security Considerations

1. **Admin Promotion**: Only existing admins can promote others
2. **Role Validation**: All roles are validated against allowed values
3. **Access Control**: Chat access is tracked separately from roles
4. **Audit Trail**: All role changes are logged for security
5. **Fallback Protection**: System ensures teams always have leadership

## Configuration

The role assignment system uses the following configuration:

- **Leadership Roles**: Defined in `TeamMemberServiceConfig`
- **Chat Types**: Detected automatically from chat titles
- **Team ID**: Resolved from environment or chat context
- **Logging**: Integrated with existing logging configuration

This implementation provides a robust, automatic role assignment system that ensures proper team management while maintaining security and providing a good user experience. 