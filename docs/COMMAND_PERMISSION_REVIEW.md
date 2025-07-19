# Command Permission System Review

## Overview

The KICKAI bot implements a hierarchical permission system that ensures commands are only available in the appropriate chat context and to users with the correct permissions.

## Permission Hierarchy

### 1. Public Commands
- **Available to**: Everyone
- **Chat Context**: All chats
- **Commands**:
  - `/help` - Show available commands
  - `/start` - Start the bot

### 2. Player Commands
- **Available to**: Registered players
- **Chat Context**: Main team chat only (NOT leadership chat)
- **Commands**:
  - `/list` - List all players
  - `/myinfo` - Show player information
  - `/update` - Update player information
  - `/status` - Check player status
  - `/register` - Register as a player
  - `/listmatches` - List upcoming matches
  - `/getmatch` - Get match details
  - `/stats` - Show player statistics
  - `/payment_status` - Check payment status
  - `/pending_payments` - Show pending payments
  - `/payment_history` - Show payment history
  - `/payment_help` - Payment help
  - `/financial_dashboard` - Financial dashboard
  - `/attend` - Attend a match
  - `/unattend` - Unattend a match

### 3. Leadership Commands
- **Available to**: Team members and admins
- **Chat Context**: Leadership chat only
- **Commands**:
  - `/add` - Add a new player
  - `/remove` - Remove a player
  - `/approve` - Approve a player
  - `/reject` - Reject a player
  - `/pending` - Show pending approvals
  - `/checkfa` - Check first aid status
  - `/dailystatus` - Daily status report
  - `/background` - Background tasks
  - `/remind` - Send reminders
  - `/newmatch` - Create a new match
  - `/updatematch` - Update match details
  - `/deletematch` - Delete a match
  - `/record_result` - Record match result
  - `/invitelink` - Generate invite link
  - `/broadcast` - Broadcast message
  - `/create_match_fee` - Create match fee
  - `/create_membership_fee` - Create membership fee
  - `/create_fine` - Create fine
  - `/payment_stats` - Payment statistics
  - `/announce` - Make announcement
  - `/injure` - Mark player as injured
  - `/suspend` - Suspend player
  - `/recover` - Mark player as recovered
  - `/refund_payment` - Refund payment
  - `/record_expense` - Record expense

### 4. Admin Commands
- **Available to**: Admins only
- **Chat Context**: Leadership chat only
- **Commands**:
  - `/promote` - Promote team member to admin
  - `/updateteaminfo` - Update team information

## Chat Context Rules

### Main Chat
- ✅ Public commands
- ✅ Player commands (for registered players)
- ❌ Leadership commands
- ❌ Admin commands

### Leadership Chat
- ✅ Public commands
- ❌ Player commands (even for players)
- ✅ Leadership commands (for team members and admins)
- ✅ Admin commands (for admins only)

## Permission Checking Logic

The permission system uses the following logic in `PermissionService.can_execute_command()`:

```python
if permission_level == PermissionLevel.PUBLIC:
    return True  # Always allowed

elif permission_level == PermissionLevel.PLAYER:
    if not user_perms.is_player:
        return False
    return context.chat_type == ChatType.MAIN  # Main chat only

elif permission_level == PermissionLevel.LEADERSHIP:
    if context.chat_type != ChatType.LEADERSHIP:
        return False
    return user_perms.is_team_member or user_perms.is_admin

elif permission_level == PermissionLevel.ADMIN:
    if context.chat_type != ChatType.LEADERSHIP:
        return False
    return user_perms.is_admin
```

## User Roles

### Player
- Has `player` role
- Can access main chat
- Can use player commands in main chat

### Team Member
- Has `team_member` role
- Can access leadership chat
- Can use leadership commands in leadership chat
- Can use player commands in main chat

### Admin
- Has `admin` role
- Can access leadership chat
- Can use all commands in leadership chat
- Can use player commands in main chat
- Can promote other team members to admin

## Backend Operations (Not Available via Commands)

The following operations are backend-only and not available as user commands:
- `/create_team` - Team creation (backend only)
- `/delete_team` - Team deletion (backend only)
- `/list_teams` - Team listing (backend only)

These operations are handled through the admin interface or system initialization.

## Help System

The help system (`/help`) dynamically shows available commands based on:
1. User's permission level
2. Current chat context
3. User's roles

This ensures users only see commands they can actually use in their current context.

## Error Messages

When permission is denied, users receive clear error messages explaining:
- Why the command is not available
- What chat context is required
- What permissions are needed
- How to get the required permissions

## Testing

The permission system can be tested by:
1. Running commands in different chat contexts
2. Testing with different user roles
3. Verifying help messages show correct commands
4. Checking error messages for denied permissions

## Implementation Files

- **Permission Service**: `src/features/system_infrastructure/domain/services/permission_service.py`
- **Permission Checker**: `src/bot_telegram/message_handling/validation/permission_checker.py`
- **Shared Enums**: `src/features/shared/domain/enums.py`
- **Command Validator**: `src/bot_telegram/command_parser/validators/command_validators.py` 