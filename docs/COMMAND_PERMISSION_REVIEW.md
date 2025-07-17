# KICKAI Command Permission Review

This document provides a comprehensive review of all commands in the KICKAI system, showing their chat availability, permission requirements, and special conditions.

## Permission Levels

- **PUBLIC**: Available to everyone, no restrictions
- **PLAYER**: Available to users with player role in main chat or leadership chat
- **LEADERSHIP**: Available to users with team_member or admin role in leadership chat only
- **ADMIN**: Available to users with admin role in leadership chat only

## Chat Types

- **Main Chat**: General team communication chat
- **Leadership Chat**: Administrative and management chat
- **Both**: Available in both chats (may have different functionality)

## Command Review Table

| Command | Description | Chat Availability | Permission Level | Required Role | Special Conditions | Notes |
|---------|-------------|-------------------|------------------|---------------|-------------------|-------|
| **📋 PUBLIC COMMANDS** |
| `/help` | Show help information | Both | PUBLIC | None | None | Shows commands available to user |
| `/start` | Start the bot | Both | PUBLIC | None | None | Welcome message and basic info |
| `/register` | Register as a new player | Both | PUBLIC | None | None | First step for new users |
| **👥 PLAYER COMMANDS** |
| `/list` | List all players | Both | PLAYER | player | None | Shows active players in main chat, all players in leadership |
| `/myinfo` | Get your player information | Both | PLAYER | player | None | Personal player details |
| `/update` | Update your player information | Both | PLAYER | player | None | Update phone, emergency contact, etc. |
| `/status` | Check player status | Both | PLAYER | player | None | Check own status or by phone number |
| `/listmatches` | List all matches/fixtures | Both | PLAYER | player | None | View upcoming and past matches |
| `/getmatch` | Get details of a specific match | Both | PLAYER | player | None | Detailed match information |
| `/stats` | Show team statistics | Both | PLAYER | player | None | Team performance metrics |
| `/payment_status` | Get payment status | Both | PLAYER | player | None | Personal payment information |
| `/pending_payments` | Get pending payments | Both | PLAYER | player | None | Personal pending payments |
| `/payment_history` | Get payment history | Both | PLAYER | player | None | Personal payment history |
| `/payment_help` | Get payment commands help | Both | PLAYER | player | None | Payment system guidance |
| `/financial_dashboard` | View financial dashboard | Both | PLAYER | player | None | Personal financial overview |
| `/attend` | Confirm attendance for a match | Both | PLAYER | player | None | Mark attendance for specific match |
| `/unattend` | Cancel attendance for a match | Both | PLAYER | player | None | Cancel attendance for specific match |
| **👑 LEADERSHIP COMMANDS** |
| `/add` | Add a new player | Leadership Only | LEADERSHIP | team_member/admin | None | Create new player record |
| `/remove` | Remove a player | Leadership Only | LEADERSHIP | team_member/admin | None | Remove player from team |
| `/approve` | Approve a player | Leadership Only | LEADERSHIP | team_member/admin | None | Approve player for match selection |
| `/reject` | Reject a player | Leadership Only | LEADERSHIP | team_member/admin | Reason required | Reject player with reason |
| `/pending` | List players pending approval | Leadership Only | LEADERSHIP | team_member/admin | None | View pending approvals |
| `/checkfa` | Check FA registration status | Leadership Only | LEADERSHIP | team_member/admin | None | Verify FA registration |
| `/dailystatus` | Get daily status report | Leadership Only | LEADERSHIP | team_member/admin | None | Team status overview |
| `/background` | Run background tasks | Leadership Only | LEADERSHIP | team_member/admin | None | Execute maintenance tasks |
| `/remind` | Send a reminder to team members | Leadership Only | LEADERSHIP | team_member/admin | None | Send team-wide reminders |
| `/newmatch` | Create a new match/fixture | Leadership Only | LEADERSHIP | team_member/admin | None | Schedule new match |
| `/updatematch` | Update a match/fixture | Leadership Only | LEADERSHIP | team_member/admin | None | Modify match details |
| `/deletematch` | Delete a match/fixture | Leadership Only | LEADERSHIP | team_member/admin | None | Remove match from schedule |
| `/record_result` | Record a match result | Leadership Only | LEADERSHIP | team_member/admin | None | Record match outcome |
| `/invitelink` | Generate invitation link | Leadership Only | LEADERSHIP | team_member/admin | None | Create player invitations |
| `/broadcast` | Broadcast message to team | Leadership Only | LEADERSHIP | team_member/admin | None | Send team-wide message |
| `/create_match_fee` | Create match fee payment | Leadership Only | LEADERSHIP | team_member/admin | None | Set up match fees |
| `/create_membership_fee` | Create membership fee | Leadership Only | LEADERSHIP | team_member/admin | None | Set up membership fees |
| `/create_fine` | Create a fine payment | Leadership Only | LEADERSHIP | team_member/admin | None | Issue fines to players |
| `/payment_stats` | Get payment statistics | Leadership Only | LEADERSHIP | team_member/admin | None | Team payment overview |
| `/announce` | Send team-wide announcement | Leadership Only | LEADERSHIP | team_member/admin | None | Official team announcements |
| `/injure` | Mark a player as injured | Leadership Only | LEADERSHIP | team_member/admin | None | Update player injury status |
| `/suspend` | Mark a player as suspended | Leadership Only | LEADERSHIP | team_member/admin | Reason required | Suspend player with reason |
| `/recover` | Mark a player as recovered | Leadership Only | LEADERSHIP | team_member/admin | None | Clear injury/suspension status |
| `/refund_payment` | Refund a payment | Leadership Only | LEADERSHIP | team_member/admin | None | Process payment refunds |
| `/record_expense` | Record a team expense | Leadership Only | LEADERSHIP | team_member/admin | None | Log team expenses |
| **🔧 ADMIN COMMANDS** |
| `/promote` | Promote user to admin | Leadership Only | ADMIN | admin | None | Only admins can promote others |

## Special Command Behaviors

### Chat-Specific Functionality

#### Main Chat Commands
- **Limited Information**: Some commands show limited information in main chat
- **Read-Only Focus**: Most commands in main chat are for information retrieval
- **Player Self-Service**: Players can update their own information

#### Leadership Chat Commands
- **Full Access**: All commands available with full functionality
- **Administrative Actions**: Team management and administrative functions
- **Detailed Information**: Full access to all team data and statistics

### Role-Based Restrictions

#### Player Role
- Can view and update their own information
- Can view team information (limited in main chat)
- Can interact with matches (attendance, viewing)
- Can access payment information (personal only)

#### Team Member Role
- All player permissions plus:
- Can manage players (add, remove, approve, reject)
- Can manage matches (create, update, delete)
- Can manage payments and expenses
- Can send announcements and reminders

#### Admin Role
- All team member permissions plus:
- Can promote other users to admin
- Can manage teams at system level
- Has ultimate authority over team operations

## Permission Logic

### Chat-Based Access Control

1. **Main Chat Access**:
   - PUBLIC commands: Always available
   - PLAYER commands: Available to players
   - LEADERSHIP commands: Not available
   - ADMIN commands: Not available

2. **Leadership Chat Access**:
   - PUBLIC commands: Always available
   - PLAYER commands: Available to players
   - LEADERSHIP commands: Available to team_member or admin
   - ADMIN commands: Available to admin only

### Role-Based Access Control

1. **Player Role**:
   - Required for PLAYER level commands
   - Automatically assigned when joining main chat
   - Can be manually assigned by leadership

2. **Team Member Role**:
   - Required for LEADERSHIP level commands
   - Automatically assigned when joining leadership chat
   - Can be manually assigned by admin

3. **Admin Role**:
   - Required for ADMIN level commands
   - Automatically assigned to first user
   - Can be manually assigned by existing admin
   - Auto-promoted when last admin leaves

## Command Categories

### Information Commands
- Help and guidance: `/help`, `/start`, `/payment_help`
- Personal information: `/myinfo`, `/status`, `/payment_status`
- Team information: `/list`, `/stats`, `/listmatches`
- Administrative information: `/pending`, `/dailystatus`, `/payment_stats`

### Management Commands
- Player management: `/add`, `/remove`, `/approve`, `/reject`
- Match management: `/newmatch`, `/updatematch`, `/deletematch`, `/record_result`
- Payment management: `/create_match_fee`, `/create_membership_fee`, `/create_fine`, `/refund_payment`
- Communication: `/broadcast`, `/announce`, `/remind`

### System Commands
- Team administration: `/create_team`, `/delete_team`, `/list_teams`
- Maintenance: `/background`, `/checkfa`
- Player status: `/injure`, `/suspend`, `/recover`

## Security Considerations

### Access Control
- All commands respect chat-based and role-based permissions
- No command can be executed without proper authorization
- Permission checks are performed at multiple levels

### Data Protection
- Players can only access their own personal information
- Leadership can access team-wide information
- Admins have access to system-level information

### Audit Trail
- All command executions are logged
- Permission denials are tracked
- User actions are recorded for accountability

## Future Enhancements

### Potential New Commands
- `/promote` - Promote user to admin (admin only)
- `/demote` - Demote admin to team member (admin only)
- `/transfer` - Transfer player between teams (admin only)
- `/backup` - Create team data backup (admin only)
- `/restore` - Restore team data from backup (admin only)

### Permission Improvements
- Time-limited permissions for temporary access
- Command-specific role requirements
- Bulk operation permissions
- Delegated authority system

This command permission review ensures that all users understand their capabilities and limitations within the KICKAI system, promoting secure and appropriate use of the platform. 