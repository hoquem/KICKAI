# KICKAI Bot Commands - Product Requirements Document (PRD)

## Overview
This document defines all commands supported by the KICKAI bot, including their syntax, natural language alternatives, access control, and display requirements for different chat types.

## Command Categories

### 1. Player Management Commands
### 2. Team Information Commands  
### 3. Match Management Commands
### 4. Administrative Commands
### 5. Utility Commands

---

## 1. PLAYER MANAGEMENT COMMANDS

### 1.1 Add Player
**Command**: `/add <name> <phone> <position> [fa_eligible]`
**Natural Language**: 
- "Add a new player called John Smith with phone 07123456789 as a midfielder"
- "Create player Jane Doe, contact 07123456789"
- "Add John Smith 07123456789"
- "New player: John Smith, 07123456789, striker"

**Access Control**: Leadership Chat Only
**Purpose**: Add new players to the team roster

**Parameters**:
- `name`: Player's full name
- `phone`: UK phone number (07XXXXXXXXX or +447XXXXXXXXX)
- `position`: goalkeeper, defender, midfielder, forward, striker, utility
- `fa_eligible`: Optional boolean (true/false, yes/no)

**Response**: Confirmation message with player ID and next steps

---

### 1.2 Remove Player
**Command**: `/remove <phone>`
**Natural Language**:
- "Remove player with phone 07123456789"
- "Delete player John Smith"
- "Remove 07123456789 from team"

**Access Control**: Leadership Chat Only
**Purpose**: Remove players from the team roster

**Parameters**:
- `phone`: Player's phone number

**Response**: Confirmation of player removal

---

### 1.3 List Players
**Command**: `/list [query]`
**Natural Language**:
- "Show all players"
- "List team members"
- "Who are the strikers?"
- "Show me FA registered players"
- "Active players only"
- "Show match eligible players"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Display team player information

**Main Chat Display**:
```
📋 Team Players

✅ Active Players:
• Alima Begum - Forward
• Ehsaan Hoque - Midfielder

⏳ Pending Players:
• John Smith - Striker

💡 Note: For detailed player information, check the leadership chat.
```

**Leadership Chat Display**:
```
📋 Team Players

✅ Active Players:
• Alima Begum (AB1) - Forward
  📱 07123456789 | ⚠️ FA: Not Registered | ⏳ Match: Pending Approval
  🚨 Emergency: Not provided
  📅 DOB: Not provided

• Ehsaan Hoque (EH1) - Midfielder
  📱 07987654321 | 🏆 FA: Registered | ✅ Match: Eligible
  🚨 Emergency: John Doe, 07123456789
  📅 DOB: 15/05/1995

📊 Legend:
🏆 FA Registered | ⚠️ FA Not Registered
✅ Match Eligible | ⏳ Pending Approval
```

---

### 1.4 Player Status
**Command**: `/status [phone]`
**Natural Language**:
- "What's my status?"
- "Check my player info"
- "Show my details"
- "Status for 07123456789" (admin only)

**Access Control**: 
- Own status: Both Main and Leadership Chats
- Other players: Leadership Chat Only

**Purpose**: Check player status and information

**Own Status Display** (Main/Leadership):
```
📊 Your Status

📋 Basic Info:
• Name: Alima Begum
• Player ID: AB1
• Position: Forward
• Phone: 07123456789

📊 Status:
• Onboarding: Pending
• FA Registered: No
• FA Eligible: Yes
• Match Eligible: No

📞 Contact Info:
• Emergency Contact: Not provided
• Date of Birth: Not provided
• Telegram: @alima_begum
```

**Other Player Status Display** (Leadership Only):
```
📊 Player Status: Ehsaan Hoque

📋 Basic Info:
• Name: Ehsaan Hoque
• Player ID: EH1
• Position: Midfielder
• Phone: 07987654321

📊 Status:
• Onboarding: Completed
• FA Registered: Yes
• FA Eligible: Yes
• Match Eligible: Yes

📞 Contact Info:
• Emergency Contact: John Doe, 07123456789
• Date of Birth: 15/05/1995
• Telegram: @ehsaan_hoque

📅 Timestamps:
• Created: 2024-01-15 10:30
• Last Updated: 2024-01-20 14:45
```

---

### 1.5 My Info
**Command**: `/myinfo [query]`
**Natural Language**:
- "What's my phone number?"
- "Show me my position"
- "Am I FA registered?"
- "What's my player ID?"
- "My emergency contact"
- "My date of birth"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Get detailed personal player information

**Display**: Same as own status display above

---

### 1.6 Invite Player
**Command**: `/invite <phone_or_player_id>`
**Natural Language**:
- "Invite player with phone 07123456789"
- "Send invitation to AB1"
- "Invite John Smith"

**Access Control**: Leadership Chat Only
**Purpose**: Generate invitation messages for new players

**Response**:
```
📱 Invitation Generated for Alima Begum (AB1)

📋 Player Details:
• Name: Alima Begum
• Phone: 07123456789
• Position: Forward

📨 Invitation Message:
Welcome to KICKAI Team, Alima Begum!

You've been invited to join our team. Here's what you need to do:

1. Join our Telegram group: [Group Link]
2. Use /start AB1 to begin your registration
3. Complete the onboarding process

For WhatsApp/SMS sharing:
"Hi Alima! You're invited to join KICKAI Team. 
Join our Telegram group: [Group Link]
Then use: /start AB1

Contact admin if you need help!"

✅ Invitation ready to send!
```

---

### 1.7 Approve Player
**Command**: `/approve <player_id>`
**Natural Language**:
- "Approve player AB1"
- "Approve Alima Begum"
- "Make AB1 match eligible"

**Access Control**: Leadership Chat Only
**Purpose**: Approve players for match squad selection

**Response**:
```
✅ Player Alima Begum approved for match squad selection!

📋 Player Details:
• Name: Alima Begum
• Player ID: AB1
• Position: Forward
• Phone: 07123456789

📊 Status Updates:
• FA Registration: ⚠️ Not Registered (Contact admin)
• Match Eligibility: ✅ Now Eligible
• Onboarding: ✅ Completed

🏆 Player is now available for match selection!
```

---

### 1.8 Reject Player
**Command**: `/reject <player_id> [reason]`
**Natural Language**:
- "Reject player AB1"
- "Reject AB1 - incomplete information"
- "Reject Alima Begum due to missing FA registration"

**Access Control**: Leadership Chat Only
**Purpose**: Reject player registrations

**Response**:
```
❌ Player Alima Begum rejected

📋 Player Details:
• Name: Alima Begum
• Player ID: AB1
• Reason: Incomplete FA registration

💡 Next Steps:
• Contact player for clarification
• Request missing information
• Re-approve when ready
```

---

### 1.9 Pending Approvals
**Command**: `/pending`
**Natural Language**:
- "Show pending approvals"
- "Who needs approval?"
- "Pending players"
- "Players waiting for approval"

**Access Control**: Leadership Chat Only
**Purpose**: View players awaiting approval

**Display**:
```
⏳ Pending Approvals

📋 Players Awaiting Approval:
• Alima Begum (AB1) - Forward
  📱 07123456789 | ⚠️ FA: Not Registered
  📅 Added: 2024-01-15 10:30

• John Smith (JS1) - Striker
  📱 07987654321 | 🏆 FA: Registered
  📅 Added: 2024-01-16 14:20

💡 Commands:
• /approve AB1 - Approve player
• /reject AB1 [reason] - Reject player
```

---

### 1.10 Check FA Registration
**Command**: `/checkfa`
**Natural Language**:
- "Check FA registrations"
- "FA registration status"
- "Who's FA registered?"
- "FA eligibility check"

**Access Control**: Leadership Chat Only
**Purpose**: Check FA registration status for all players

**Display**:
```
🏆 FA Registration Status

✅ FA Registered Players:
• Ehsaan Hoque (EH1) - Midfielder
• John Smith (JS1) - Striker

⚠️ FA Not Registered:
• Alima Begum (AB1) - Forward
• Sarah Wilson (SW1) - Defender

📊 Summary:
• Total Players: 4
• FA Registered: 2 (50%)
• Not Registered: 2 (50%)

💡 Action Required:
Contact unregistered players for FA registration
```

---

### 1.11 Daily Status
**Command**: `/dailystatus`
**Natural Language**:
- "Daily team status"
- "Team summary"
- "Today's status"
- "Team overview"

**Access Control**: Leadership Chat Only
**Purpose**: Get daily team status summary

**Display**:
```
📊 Daily Team Status - 2024-01-20

👥 Team Overview:
• Total Players: 15
• Active Players: 12
• Pending Approval: 3
• FA Registered: 10 (67%)

📋 Recent Activity:
• New Registrations: 2
• Approvals: 1
• FA Registrations: 1

🎯 Action Items:
• 3 players need approval
• 5 players need FA registration
• 2 players need emergency contact

📅 Next Matches:
• Thunder FC - 2024-01-25 (Home)
• Lightning United - 2024-02-01 (Away)
```

---

### 1.12 Register Player
**Command**: `/register <name> <phone> <position>`
**Natural Language**:
- "Register as a new player"
- "Sign up as John Smith"
- "I want to join the team"
- "Register me as a midfielder"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Allow players to self-register

**Parameters**:
- `name`: Player's full name
- `phone`: UK phone number (07XXXXXXXXX or +447XXXXXXXXX)
- `position`: goalkeeper, defender, midfielder, forward, striker, utility

**Response**:
```
✅ Registration Successful!

📋 Your Details:
• Name: John Smith
• Player ID: JS1
• Position: Midfielder
• Phone: 07123456789

🎯 Next Steps:
1. Complete your onboarding
2. Provide emergency contact
3. Confirm FA eligibility
4. Wait for admin approval

💡 Commands:
• /myinfo - View your details
• /status - Check your status
• /help - Get assistance

Welcome to KICKAI Team! 🏆
```

---

### 1.13 Remind Player
**Command**: `/remind <player_id>`
**Natural Language**:
- "Send reminder to AB1"
- "Remind Alima to complete onboarding"
- "Send reminder to player AB1"
- "Remind player to finish registration"

**Access Control**: Leadership Chat Only
**Purpose**: Send manual reminders to players with incomplete onboarding

**Parameters**:
- `player_id`: Player's ID (e.g., AB1, JS1)

**Response**: Confirmation of reminder sent with current status

**Display**:
```
📢 Reminder Sent to Alima Begum (AB1)

📋 Reminder Details:
• Type: Manual Admin Reminder
• Message: Custom reminder message
• Sent: 2024-01-20 16:45

📊 Current Status:
• Onboarding Progress: 1/4 steps completed
• Time Since Last Activity: 2 hours
• Previous Reminders: 1 (automated)

✅ Reminder delivered successfully
```

---

## 2. TEAM INFORMATION COMMANDS

### 2.1 Team Stats
**Command**: `/stats [query]`
**Natural Language**:
- "Team statistics"
- "Show team stats"
- "Player statistics"
- "Team performance"
- "Stats for strikers"
- "FA registration stats"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Display team and player statistics

**Main Chat Display**:
```
📊 Team Statistics

👥 Player Counts:
• Total Players: 15
• Active Players: 12
• Pending: 3

⚽ Position Breakdown:
• Goalkeepers: 2
• Defenders: 4
• Midfielders: 5
• Forwards: 4

💡 For detailed stats, check the leadership chat.
```

**Leadership Chat Display**:
```
📊 Team Statistics

👥 Player Counts:
• Total Players: 15
• Active Players: 12
• Pending Approval: 3
• FA Registered: 10 (67%)
• Match Eligible: 8 (53%)

⚽ Position Breakdown:
• Goalkeepers: 2 (13%)
• Defenders: 4 (27%)
• Midfielders: 5 (33%)
• Forwards: 4 (27%)

📊 FA Registration:
• Registered: 10 players
• Not Registered: 5 players
• Registration Rate: 67%

📈 Recent Activity:
• New Players (7 days): 3
• Approvals (7 days): 2
• FA Registrations (7 days): 1
```

---

## 3. MATCH MANAGEMENT COMMANDS

### 3.1 Create Match
**Command**: `/creatematch <opponent> <date> <time> <venue> [competition]`
**Natural Language**:
- "Create match against Thunder FC on 25th January at 2pm"
- "Schedule match with Lightning United, 1st Feb, 3pm, Central Park"
- "New match: Thunder FC, 25/01/2024, 14:00, Home, League"

**Access Control**: Leadership Chat Only
**Purpose**: Create new match fixtures

**Response**:
```
⚽ Match Created Successfully!

🏆 Thunder FC vs KICKAI Team
📅 Date: 2024-01-25
🕐 Time: 14:00
📍 Venue: Central Park (Home)
🏆 Competition: League

🆔 Match ID: MATCH-2024-001

✅ Match added to schedule
📋 Next: Add players to squad
```

---

### 3.2 List Matches
**Command**: `/listmatches [filter]`
**Natural Language**:
- "Show all matches"
- "List fixtures"
- "Upcoming games"
- "Match schedule"
- "Home matches only"
- "League matches"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Display match schedule

**Main Chat Display**:
```
📋 Upcoming Matches:

🏆 Thunder FC vs KICKAI Team
📅 2024-01-25 at 14:00
📍 Home - Central Park

🏆 KICKAI Team vs Lightning United
📅 2024-02-01 at 15:00
📍 Away - Sports Complex

💡 For match details and squad info, check the leadership chat.
```

**Leadership Chat Display**:
```
📋 Upcoming Matches:

🏆 Thunder FC vs KICKAI Team
📅 2024-01-25 at 14:00
📍 Home - Central Park
🏆 Competition: League
🆔 Match ID: MATCH-2024-001
👥 Squad: 0/18 players selected

🏆 KICKAI Team vs Lightning United
📅 2024-02-01 at 15:00
📍 Away - Sports Complex
🏆 Competition: League
🆔 Match ID: MATCH-2024-002
👥 Squad: 0/18 players selected

📊 Summary:
• Total Matches: 2
• Home: 1 | Away: 1
• League: 2 | Cup: 0
```

---

### 3.3 Get Match Details
**Command**: `/getmatch <match_id>`
**Natural Language**:
- "Show match MATCH-2024-001"
- "Match details for MATCH-2024-001"
- "Get match info"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Get detailed information about a specific match

**Main Chat Display**:
```
🏆 Thunder FC vs KICKAI Team

📅 Date: 2024-01-25
🕐 Time: 14:00
📍 Venue: Central Park (Home)
🏆 Competition: League

👥 Squad: 0/18 players selected

💡 For squad management, check the leadership chat.
```

**Leadership Chat Display**:
```
🏆 Thunder FC vs KICKAI Team

📅 Date: 2024-01-25
🕐 Time: 14:00
📍 Venue: Central Park (Home)
🏆 Competition: League
🆔 Match ID: MATCH-2024-001

👥 Squad (0/18):
No players selected yet

📋 Available Players:
• Alima Begum (AB1) - Forward ✅
• Ehsaan Hoque (EH1) - Midfielder ✅
• John Smith (JS1) - Striker ✅

💡 Commands:
• /addplayer MATCH-2024-001 AB1 - Add to squad
• /removeplayer MATCH-2024-001 AB1 - Remove from squad
```

---

### 3.4 Update Match
**Command**: `/updatematch <match_id> <field> <value>`
**Natural Language**:
- "Update match MATCH-2024-001 time to 3pm"
- "Change venue for MATCH-2024-001 to Sports Complex"
- "Update MATCH-2024-001 date to 26th January"

**Access Control**: Leadership Chat Only
**Purpose**: Update match details

**Response**:
```
✅ Match Updated Successfully!

🏆 Thunder FC vs KICKAI Team
📅 Date: 2024-01-26 (Updated)
🕐 Time: 15:00 (Updated)
📍 Venue: Sports Complex (Updated)
🏆 Competition: League

🆔 Match ID: MATCH-2024-001
```

---

### 3.5 Delete Match
**Command**: `/deletematch <match_id>`
**Natural Language**:
- "Delete match MATCH-2024-001"
- "Cancel match MATCH-2024-001"
- "Remove fixture MATCH-2024-001"

**Access Control**: Leadership Chat Only
**Purpose**: Delete/cancel matches

**Response**:
```
❌ Match Deleted Successfully!

🏆 Thunder FC vs KICKAI Team
📅 2024-01-25 at 14:00
🆔 Match ID: MATCH-2024-001

✅ Match removed from schedule
📢 Players will be notified
```

---

## 4. ADMINISTRATIVE COMMANDS

### 4.1 Broadcast Message
**Command**: `/broadcast <message>`
**Natural Language**:
- "Broadcast training cancelled tomorrow"
- "Send message to all players"
- "Announce team meeting"

**Access Control**: Leadership Chat Only
**Purpose**: Send messages to all team members

**Response**:
```
✅ Broadcast Sent!

📢 Message: Training cancelled tomorrow
👥 Recipients: 15 team members

✅ Message delivered to all active players
```

---

### 4.2 Bot Configuration
**Command**: `/botconfig`
**Natural Language**:
- "Show bot configuration"
- "Bot settings"
- "Configuration info"

**Access Control**: Leadership Chat Only
**Purpose**: View bot configuration

**Display**:
```
🤖 Bot Configuration

📋 Team Info:
• Team Name: KICKAI Team
• Team ID: 0854829d-445c-4138-9fd3-4db562ea46ee

💬 Chat Configuration:
• Main Chat: -4889304885
• Leadership Chat: -1234567890

🔧 Bot Settings:
• AI Provider: OpenAI
• Model: gpt-4
• Language: English

📊 Statistics:
• Commands Processed: 1,234
• Active Players: 15
• Total Matches: 8
```

---

## 5. UTILITY COMMANDS

### 5.1 Start
**Command**: `/start [player_id]`
**Natural Language**:
- "Start the bot"
- "Hello"
- "Begin"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Start the bot and begin onboarding

**Response** (without player_id):
```
🎉 Welcome to KICKAI Team Management Bot!

I'm here to help you manage your football team. Here's what I can do:

📋 Player Management:
• Add and remove players
• Track player status and statistics
• Generate invitation messages
• Manage player registrations

👑 Leadership Features:
• Approve/reject player registrations
• View pending approvals
• Team management tools

💡 Getting Started:
• Type `/help` to see all available commands
• Use `/add <name> <phone> <position>` to add a player
• Use `/list` to see all team players

⚽ Need Help?
Type `/help` for a complete list of commands and examples.

🏆 Team Access:
• Main team chat: For all players and general communication
• Leadership chat: For team management (access granted separately)

Welcome to the team! 🏆
```

**Response** (with player_id):
```
✅ Welcome to KICKAI Team, Alima Begum!

You've been invited to join our team. Let's get you set up:

📋 Your Details:
• Name: Alima Begum
• Player ID: AB1
• Position: Forward
• Phone: 07123456789

🎯 Next Steps:
1. Complete your onboarding
2. Provide emergency contact
3. Confirm FA eligibility
4. Wait for admin approval

💡 Commands:
• /myinfo - View your details
• /help - Get assistance

Let's get started! Reply with any questions.
```

---

### 5.2 Help
**Command**: `/help [category]`
**Natural Language**:
- "Help"
- "What can you do?"
- "Show commands"
- "Help with player management"

**Access Control**: Both Main and Leadership Chats
**Purpose**: Show available commands and help

**Main Chat Display**:
```
💡 KICKAI Bot Help

📋 Available Commands:

👤 Player Commands:
• /myinfo - View your player information
• /status - Check your status
• /list - See all team players (limited info)
• /register - Register as a new player

⚽ Match Commands:
• /listmatches - View upcoming matches
• /getmatch <id> - Get match details

💬 Utility:
• /help - Show this help message
• /start - Start the bot

💡 Natural Language:
You can also ask me things like:
• "What's my phone number?"
• "Show me my position"
• "Am I FA registered?"
• "When's the next match?"

🔧 Need More?
For admin functions, use the leadership chat.
```

**Leadership Chat Display**:
```
💡 KICKAI Bot Help - Leadership

📋 Available Commands:

👥 Player Management:
• /add <name> <phone> <position> - Add new player
• /remove <phone> - Remove player
• /list - View all players (full details)
• /status [phone] - Check player status
• /register <name> <phone> <position> - Register new player
• /invite <phone/id> - Generate invitation
• /approve <id> - Approve player
• /reject <id> [reason] - Reject player
• /pending - View pending approvals
• /remind <id> - Send reminder to player
• /checkfa - Check FA registrations
• /dailystatus - Daily team summary

⚽ Match Management:
• /creatematch <opponent> <date> <time> <venue> - Create match
• /listmatches - View all matches
• /getmatch <id> - Get match details
• /updatematch <id> <field> <value> - Update match
• /deletematch <id> - Delete match

📊 Team Information:
• /stats - Team statistics
• /botconfig - Bot configuration

📢 Communication:
• /broadcast <message> - Send to all players

💡 Natural Language:
You can also use natural language for most commands:
• "Add a new player called John Smith"
• "Show me all strikers"
• "Create match against Thunder FC"
• "Who needs FA registration?"

🔧 Examples:
• /add "John Smith" 07123456789 striker
• /invite 07123456789
• /approve AB1
• /creatematch "Thunder FC" "2024-01-25" "14:00" "Home" "League"
```

---

## 6. NATURAL LANGUAGE PROCESSING

### 6.1 Intent Recognition
The bot supports natural language processing for:
- Player queries and updates
- Team information requests
- Match scheduling
- Administrative tasks

### 6.2 Update Requests
**Natural Language Examples**:
- "Change my date of birth to 10/02/1975"
- "Update my phone number to 07987654321"
- "My emergency contact is Jane Smith, 07123456789"
- "Change my position to midfielder"

**Response**:
```
📅 Date of Birth Update Request

I understand you want to update your date of birth to: 10/02/1975

📋 Current Information:
[Current player info]

⚠️ Important: Date of birth updates require admin approval.

💡 Next Steps:
1. Contact the team admin in the leadership chat
2. Provide your new date of birth: 10/02/1975
3. Admin will update your information

🔒 Security Note: This helps maintain accurate player records.
```

---

## 7. ACCESS CONTROL MATRIX

| Command | Main Chat | Leadership Chat | Notes |
|---------|-----------|-----------------|-------|
| `/start` | ✅ | ✅ | Welcome message |
| `/help` | ✅ | ✅ | Different content per chat |
| `/myinfo` | ✅ | ✅ | Own information only |
| `/status` | ✅ (own) | ✅ (all) | Own status in main, all in leadership |
| `/list` | ✅ | ✅ | Limited info in main, full in leadership |
| `/register` | ✅ | ✅ | Self-registration |
| `/listmatches` | ✅ | ✅ | Limited info in main, full in leadership |
| `/getmatch` | ✅ | ✅ | Limited info in main, full in leadership |
| `/add` | ❌ | ✅ | Admin only |
| `/remove` | ❌ | ✅ | Admin only |
| `/invite` | ❌ | ✅ | Admin only |
| `/approve` | ❌ | ✅ | Admin only |
| `/reject` | ❌ | ✅ | Admin only |
| `/pending` | ❌ | ✅ | Admin only |
| `/checkfa` | ❌ | ✅ | Admin only |
| `/dailystatus` | ❌ | ✅ | Admin only |
| `/remind` | ❌ | ✅ | Admin only |
| `/creatematch` | ❌ | ✅ | Admin only |
| `/updatematch` | ❌ | ✅ | Admin only |
| `/deletematch` | ❌ | ✅ | Admin only |
| `/broadcast` | ❌ | ✅ | Admin only |
| `/botconfig` | ❌ | ✅ | Admin only |
| `/stats` | ✅ | ✅ | Limited info in main, full in leadership |

---

## 8. DISPLAY STANDARDS

### 8.1 Main Chat Display Principles
- **Minimal Information**: Show only essential details
- **Privacy Protection**: No phone numbers, emergency contacts, or personal details
- **Action Guidance**: Direct users to leadership chat for detailed info
- **Read-Only**: No administrative functions

### 8.2 Leadership Chat Display Principles
- **Full Information**: Complete player and match details
- **Administrative Functions**: All management capabilities
- **Detailed Statistics**: Comprehensive team analytics
- **Action Items**: Clear next steps and recommendations

### 8.3 Message Formatting
- **Emojis**: Use relevant emojis for visual clarity
- **Bold Text**: Use `<b>` tags for headers and important information
- **Bullet Points**: Use `•` for lists
- **Sections**: Clear section breaks with headers
- **Legends**: Include legends for status indicators

---

## 9. ERROR HANDLING

### 9.1 Access Denied Messages
```
❌ Access Denied

🔒 This command requires leadership access.
💡 Please use the leadership chat for this function.

Your Role: player
```

### 9.2 Invalid Command Messages
```
❌ Invalid command format

💡 Usage: /add <name> <phone> <position>
📋 Example: /add "John Smith" 07123456789 striker

🔧 Need help? Type /help for all commands.
```

### 9.3 Player Not Found Messages
```
❌ Player not found

💡 Possible reasons:
• Phone number is incorrect
• Player hasn't been added yet
• Player was removed from team

🔧 Contact admin for assistance.
```

---

## 10. FUTURE ENHANCEMENTS

### 10.1 Planned Features
- **Squad Selection**: Add/remove players from match squads
- **Attendance Tracking**: Track player attendance at matches
- **Performance Stats**: Individual and team performance metrics
- **Training Schedule**: Manage training sessions
- **Payment Tracking**: Track membership fees and payments
- **Integration**: WhatsApp/SMS integration for notifications

### 10.2 Command Extensions
- **Advanced Filtering**: More sophisticated player and match filtering
- **Bulk Operations**: Add/remove multiple players at once
- **Templates**: Predefined message templates for common communications
- **Automation**: Automated reminders and notifications
- **Reporting**: Generate detailed reports and analytics

---

## 11. MAINTENANCE AND UPDATES

### 11.1 Version Control
- Track command changes and additions
- Maintain backward compatibility
- Document breaking changes

### 11.2 Testing
- Test all commands in both chat types
- Verify access control works correctly
- Ensure natural language processing functions properly
- Validate display formatting in different contexts

### 11.3 Documentation Updates
- Update this PRD when adding new commands
- Maintain examples and usage patterns
- Keep access control matrix current
- Document any configuration changes

---

*This document should be updated whenever new commands are added or existing commands are modified. Last updated: 2024-01-20*

## Summary

This comprehensive PRD documents all 23 commands currently supported by the KICKAI bot:

### Command Count by Category:
- **Player Management**: 13 commands
- **Team Information**: 1 command  
- **Match Management**: 5 commands
- **Administrative**: 2 commands
- **Utility**: 2 commands

### Key Features Documented:
- ✅ Command syntax and parameters
- ✅ Natural language alternatives
- ✅ Access control specifications
- ✅ Display requirements for both chat types
- ✅ Error handling examples
- ✅ Complete access control matrix
- ✅ Display standards and formatting
- ✅ Future enhancement roadmap
- ✅ Maintenance guidelines

### Recent Updates:
- Added `/register` command for self-registration
- Added `/remind` command for player reminders
- Updated access control matrix
- Enhanced help documentation
- Improved natural language processing examples 