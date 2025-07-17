# Command Chat Differences

This document details the specific differences in command behavior between main chat and leadership chat for commands that are available in both contexts.

## Overview

Some commands are available in both main chat and leadership chat, but their functionality and output may differ based on the chat context and user permissions.

## Command Behavior Differences

| Command | Main Chat Behavior | Leadership Chat Behavior | Key Differences |
|---------|-------------------|--------------------------|-----------------|
| **📋 PUBLIC COMMANDS** |
| `/help` | Shows commands available to user in main chat | Shows commands available to user in leadership chat | Context-aware command filtering |
| `/start` | Welcome message for new users | Welcome message for new users | Same behavior in both chats |
| `/register` | Player registration process | Player registration process | Same behavior in both chats |
| **👥 PLAYER COMMANDS** |
| `/list` | Shows only active players | Shows all players with status | Leadership chat shows more detailed information |
| `/myinfo` | Personal player information | Personal player information | Same behavior in both chats |
| `/update` | Update personal information | Update personal information | Same behavior in both chats |
| `/status` | Check own status or by phone | Check own status or by phone | Same behavior in both chats |
| `/listmatches` | View upcoming and past matches | View upcoming and past matches | Same behavior in both chats |
| `/getmatch` | Detailed match information | Detailed match information | Same behavior in both chats |
| `/stats` | Team performance metrics | Team performance metrics | Same behavior in both chats |
| `/payment_status` | Personal payment information | Personal payment information | Same behavior in both chats |
| `/pending_payments` | Personal pending payments | Personal pending payments | Same behavior in both chats |
| `/payment_history` | Personal payment history | Personal payment history | Same behavior in both chats |
| `/payment_help` | Payment system guidance | Payment system guidance | Same behavior in both chats |
| `/financial_dashboard` | Personal financial overview | Personal financial overview | Same behavior in both chats |
| `/attend` | Mark attendance for match | Mark attendance for match | Same behavior in both chats |
| `/unattend` | Cancel attendance for match | Cancel attendance for match | Same behavior in both chats |

## Detailed Differences

### `/help` Command

**Main Chat:**
- Shows only commands available to players in main chat
- Filters out leadership and admin commands
- Focuses on player self-service commands

**Leadership Chat:**
- Shows all commands available to user based on their role
- Includes leadership and admin commands if user has appropriate permissions
- Provides comprehensive command overview

### `/list` Command

**Main Chat:**
- Shows only active players (approved and match-eligible)
- Displays basic player information
- Focuses on current team roster

**Leadership Chat:**
- Shows all players regardless of status
- Displays detailed status information (pending, injured, suspended, etc.)
- Includes administrative information for team management

## Permission Context Differences

### User Role Resolution

**Main Chat:**
- User must have `player` role to access PLAYER commands
- Role is determined by chat membership and team member record
- Limited to player-level permissions

**Leadership Chat:**
- User can have multiple roles (`player`, `team_member`, `admin`)
- Role is determined by chat membership and team member record
- Access to higher-level permissions based on roles

### Command Availability

**Main Chat:**
- PUBLIC commands: Always available
- PLAYER commands: Available to players
- LEADERSHIP commands: Not available
- ADMIN commands: Not available

**Leadership Chat:**
- PUBLIC commands: Always available
- PLAYER commands: Available to players
- LEADERSHIP commands: Available to team_member or admin
- ADMIN commands: Available to admin only

## Security Implications

### Data Access

**Main Chat:**
- Users can only access their own personal information
- Team information is limited to active players
- No access to administrative functions

**Leadership Chat:**
- Users can access team-wide information based on their role
- Administrative functions available to appropriate roles
- Full access to team management capabilities

### Command Execution

**Main Chat:**
- Commands execute with player-level permissions
- Limited to self-service and information retrieval
- No administrative actions possible

**Leadership Chat:**
- Commands execute with user's highest available role
- Full administrative capabilities for appropriate roles
- Team management and administrative actions available

## User Experience Differences

### Information Display

**Main Chat:**
- Simplified information display
- Focus on essential information
- User-friendly messaging

**Leadership Chat:**
- Detailed information display
- Administrative details included
- Professional management interface

### Error Messages

**Main Chat:**
- Simple error messages
- Focus on user guidance
- Limited technical details

**Leadership Chat:**
- Detailed error messages
- Technical information included
- Administrative troubleshooting guidance

## Implementation Notes

### Permission Checking

The system uses the centralized permission service to determine command availability:

1. **Chat Type Detection**: System detects whether command is executed in main or leadership chat
2. **Role Resolution**: User's roles are determined from team member record
3. **Permission Validation**: Command permission level is checked against user's capabilities
4. **Context-Aware Execution**: Command behavior is adjusted based on chat context

### Command Registration

Commands are registered with their permission levels:

```python
# Example command registration
class ListPlayersCommand(Command):
    def __init__(self):
        super().__init__("/list", "List all players", PermissionLevel.PLAYER)
```

### Permission Strategy

The permission strategies handle chat-based access control:

```python
class PlayerPermissionStrategy(PermissionStrategy):
    def can_execute(self, context: CommandContext) -> bool:
        # Available in main chat or leadership chat
        return context.chat_type in [ChatType.MAIN, ChatType.LEADERSHIP]
```

## Best Practices

### For Users

1. **Main Chat**: Use for general team communication and personal information
2. **Leadership Chat**: Use for team management and administrative tasks
3. **Role Awareness**: Understand your role and available commands
4. **Context Switching**: Be aware of different command behavior in different chats

### For Developers

1. **Permission Consistency**: Always use centralized permission service
2. **Context Awareness**: Design commands to be context-aware
3. **User Experience**: Provide appropriate information for each context
4. **Security**: Ensure proper access control at all levels

### For Administrators

1. **Role Management**: Properly assign roles to team members
2. **Chat Management**: Ensure users are in appropriate chats
3. **Permission Monitoring**: Monitor command usage and permissions
4. **User Training**: Educate users on command differences

This detailed breakdown ensures that users and developers understand the nuances of command behavior across different chat contexts, promoting proper usage and security. 