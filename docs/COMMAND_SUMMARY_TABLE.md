# KICKAI Command Summary Table

## Quick Reference

| Command | Chat | Permission | Description |
|---------|------|------------|-------------|
| **🔓 PUBLIC** |
| `/help` | Both | None | Show available commands |
| `/start` | Both | None | Start the bot |
| `/register` | Both | None | Register as player |
| **👤 PLAYER** |
| `/list` | Both | player | List players |
| `/myinfo` | Both | player | Your player info |
| `/update` | Both | player | Update your info |
| `/status` | Both | player | Check status |
| `/listmatches` | Both | player | List matches |
| `/getmatch` | Both | player | Match details |
| `/stats` | Both | player | Team statistics |
| `/payment_status` | Both | player | Your payments |
| `/pending_payments` | Both | player | Your pending payments |
| `/payment_history` | Both | player | Your payment history |
| `/payment_help` | Both | player | Payment help |
| `/financial_dashboard` | Both | player | Your finances |
| `/attend` | Both | player | Confirm attendance |
| `/unattend` | Both | player | Cancel attendance |
| **👑 LEADERSHIP** |
| `/add` | Leadership | team_member/admin | Add player |
| `/remove` | Leadership | team_member/admin | Remove player |
| `/approve` | Leadership | team_member/admin | Approve player |
| `/reject` | Leadership | team_member/admin | Reject player |
| `/pending` | Leadership | team_member/admin | Pending approvals |
| `/checkfa` | Leadership | team_member/admin | Check FA status |
| `/dailystatus` | Leadership | team_member/admin | Daily report |
| `/background` | Leadership | team_member/admin | Background tasks |
| `/remind` | Leadership | team_member/admin | Send reminder |
| `/newmatch` | Leadership | team_member/admin | Create match |
| `/updatematch` | Leadership | team_member/admin | Update match |
| `/deletematch` | Leadership | team_member/admin | Delete match |
| `/record_result` | Leadership | team_member/admin | Record result |
| `/invitelink` | Leadership | team_member/admin | Generate invite |
| `/broadcast` | Leadership | team_member/admin | Broadcast message |
| `/create_match_fee` | Leadership | team_member/admin | Create match fee |
| `/create_membership_fee` | Leadership | team_member/admin | Create membership fee |
| `/create_fine` | Leadership | team_member/admin | Create fine |
| `/payment_stats` | Leadership | team_member/admin | Payment statistics |
| `/announce` | Leadership | team_member/admin | Send announcement |
| `/injure` | Leadership | team_member/admin | Mark injured |
| `/suspend` | Leadership | team_member/admin | Suspend player |
| `/recover` | Leadership | team_member/admin | Mark recovered |
| `/refund_payment` | Leadership | team_member/admin | Refund payment |
| `/record_expense` | Leadership | team_member/admin | Record expense |
| `/promote` | Leadership | admin | Promote member to admin |
| **🔧 ADMIN** |

## Permission Levels

- **🔓 PUBLIC**: Available to everyone
- **👤 PLAYER**: Available to players in main or leadership chat
- **👑 LEADERSHIP**: Available to team members/admins in leadership chat only
- **🔧 ADMIN**: Available to admins in leadership chat only

## Chat Types

- **Both**: Available in main chat and leadership chat
- **Leadership**: Available only in leadership chat

## Key Differences

### Main Chat vs Leadership Chat

| Command | Main Chat | Leadership Chat |
|---------|-----------|-----------------|
| `/list` | Active players only | All players with status |
| `/help` | Player commands only | All available commands |

### Role Requirements

| Role | Can Access | Commands Available |
|------|------------|-------------------|
| **None** | Main Chat | Public only |
| **Player** | Both Chats | Public + Player |
| **Team Member** | Both Chats | Public + Player + Leadership |
| **Admin** | Both Chats | Public + Player + Leadership + Admin |

## Special Notes

- **First User**: Automatically becomes admin
- **Last Admin**: Auto-promotes longest-tenured leadership member
- **Chat Membership**: Determines role assignment
- **Permission Inheritance**: Higher roles include lower role permissions 