# Access Control & Team Member System

## Overview

The KICKAI system implements a sophisticated access control system based on team membership, multiple roles per member, and chat-based permissions. This ensures secure and appropriate access to different commands and features based on user roles and chat context.

## Team Member System

### Data Model
```python
@dataclass
class TeamMember:
    id: str
    team_id: str
    user_id: str
    roles: List[str]  # Multiple roles per member
    permissions: List[str]
    chat_access: Dict[str, bool]
    telegram_id: Optional[str]
    telegram_username: Optional[str]
    joined_at: datetime
    updated_at: datetime
    additional_info: Dict[str, Any]
```

### Key Features
- **Multiple Roles**: Members can have multiple roles (e.g., `['player', 'captain', 'admin']`)
- **Chat Access Control**: Different access levels for different chat types
- **Telegram Integration**: Direct mapping to Telegram user IDs
- **Role Validation**: Enforced role validation and uniqueness constraints

## Access Control Architecture

### Chat-Based Permissions
The system uses two distinct chat types with different permission levels:

#### Main Chat 
- **Access Level**: Read-only commands only
- **Purpose**: General team communication and information access
- **Commands Available**: List players, show matches, help, status

#### Leadership Chat 
- **Access Level**: All commands (admin + read-only)
- **Purpose**: Administrative operations and team management
- **Commands Available**: All commands including player management, match creation, etc.

### Command Classification

#### Admin Commands (Leadership Chat Only)
```python
admin_commands = {
    'add player', 'new player', 'create player', 'remove player', 'update player',
    'new match', 'create match', 'schedule match', 'add fixture', 'update fixture',
    'send message to team', 'create poll', 'send payment reminder', 'update team',
    'approve player', 'reject player', 'check fa registration', 'daily status'
}
```

#### Read-Only Commands (All Chats)
```python
read_only_commands = {
    'list players', 'show players', 'all players', 'get player', 'player info',
    'list matches', 'show matches', 'fixtures', 'games', 'team info', 'help', 'status',
    'my info', 'register'
}
```

## Role System

### Available Roles
- **`player`**: Basic team member
- **`captain`**: Team captain with leadership responsibilities
- **`vice_captain`**: Assistant captain
- **`manager`**: Team manager
- **`coach`**: Team coach
- **`admin`**: Administrative access
- **`volunteer`**: Volunteer helper
- **`secretary`**: Team secretarial tasks

### Role Hierarchy
```python
leadership_roles = {'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer', 'secretary'}
player_role = {'player'}
```

### Multiple Role Support
Members can have multiple roles simultaneously:
```python
# Example: Member with multiple roles
member = TeamMember(
    team_id="team_bp_hatters",
    user_id="player_ahmed_khan",
    roles=["player", "captain", "admin"],  # Multiple roles
    telegram_id="123456789",
    chat_access={"main_chat": True, "leadership_chat": True}
)
```

## Access Control Service

### Core Methods
```python
class AccessControlService:
    def __init__(self, team_member_service: TeamMemberService, config: AccessControlConfig)
    
    # Access control
    async def check_access(self, command: str, chat_id: str, telegram_id: str, team_id: str) -> bool
    async def get_user_permissions(self, telegram_id: str, team_id: str) -> Dict[str, Any]
    
    # Chat detection
    def is_leadership_chat(self, chat_id: str) -> bool
    def is_main_chat(self, chat_id: str) -> bool
    
    # Command classification
    def is_admin_command(self, command: str) -> bool
    def is_read_only_command(self, command: str) -> bool
```

### Access Control Flow
```
User Command
    ↓
Check Chat Type
    ↓
Leadership Chat? → Yes → Allow All Commands
    ↓ No
Main Chat? → Yes → Check Command Type
    ↓ No
Deny Access
    ↓
Read-Only Command? → Yes → Allow
    ↓ No
Deny Access
```

## Team Member Service

### Core Operations
```python
class TeamMemberService:
    # Core operations
    async def create_team_member(self, team_member: TeamMember) -> str
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]
    async def update_team_member(self, team_member: TeamMember) -> bool
    async def delete_team_member(self, member_id: str) -> bool
    
    # Query operations
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]
    async def get_leadership_members(self, team_id: str) -> List[TeamMember]
    async def get_players(self, team_id: str) -> List[TeamMember]
    
    # Role management
    async def add_role_to_member(self, member_id: str, role: str) -> bool
    async def remove_role_from_member(self, member_id: str, role: str) -> bool
    async def validate_member_roles(self, member: TeamMember) -> List[str]
```

## Integration with Command System

### Command Handler Integration
```python
class SimpleAgenticHandler:
    def __init__(self, team_id: str):
        # Dependency injection
        self.firebase_client = get_firebase_client()
        self.team_member_service = TeamMemberService(self.firebase_client)
        self.access_control_service = AccessControlService(self.team_member_service)
    
    async def _route_command(self, message: str, user_id: str, chat_id: str, ...):
        # Access control check
        has_access = await self.access_control_service.check_access(
            message, chat_id, telegram_id, self.team_id
        )
        if not has_access:
            return self.access_control_service.get_access_denied_message(message, chat_id)
```

### Access Denied Messages
The system provides context-aware access denied messages:

#### Main Chat Access Denied
```
❌ **Access Denied**

🔒 This command requires leadership access.
💡 Please use the leadership chat for this function.
```

#### Leadership Chat Access Denied
```
❌ **Access Denied**

🔒 This command requires admin access.
💡 Contact your team admin for access.

Your Role: {user_role.title()}
```

## Validation Rules

### Role Validation
- Members must have at least one role
- Valid roles: `player`, `captain`, `vice_captain`, `manager`, `coach`, `admin`, `volunteer`
- Invalid roles are rejected with clear error messages

### Telegram ID Uniqueness
- Telegram IDs must be unique per team
- Prevents duplicate member registrations
- Enforced at database level

### Chat Access Validation
- Chat access must be properly configured
- Default access: main_chat=True, leadership_chat=False
- Leadership roles get leadership_chat=True

## Testing Requirements

### Access Control Testing
1. **Main Chat**: Only read-only commands allowed
2. **Leadership Chat**: All commands allowed for leadership members
3. **Role Validation**: Members must have at least one role
4. **Telegram ID Uniqueness**: Enforced per team

### Command Testing
- `/help` - Works in all chats
- `/list_teams` - Works in all chats (read-only)
- Admin commands - Blocked in main chat, allowed in leadership chat
- Access denied messages - Proper user feedback

## Implementation Guidelines

### For New Commands
1. **Classify Command**: Determine if admin or read-only
2. **Add to Lists**: Add to appropriate command classification lists
3. **Test Access**: Test in both chat types
4. **Update Documentation**: Document command access requirements

### For New Roles
1. **Define Role**: Add to valid roles list
2. **Update Hierarchy**: Add to leadership_roles if applicable
3. **Update Validation**: Update role validation logic
4. **Add Tests**: Test role assignment and access control

### For Chat Changes
1. **Update Chat IDs**: Update hardcoded chat IDs
2. **Test Access**: Verify access control still works
3. **Update Documentation**: Update chat-specific documentation
4. **Notify Users**: Inform users of chat access changes 