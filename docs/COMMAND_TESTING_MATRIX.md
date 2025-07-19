# KICKAI Command Testing Matrix

Quick reference for testing command behavior across different scenarios.

## Test Matrix

| Command | Main Chat | Leadership Chat | Unregistered | Registered Player | Team Member | First User |
|---------|-----------|-----------------|--------------|-------------------|-------------|------------|
| `/help` | ✅ Player commands | ✅ All commands | ✅ Basic only | ✅ Player commands | ✅ All commands | ✅ All commands |
| `/start` | ✅ Welcome message | ✅ Leadership welcome | ✅ Welcome message | ✅ Welcome message | ✅ Leadership welcome | ✅ Leadership welcome |
| `/register` | ✅ Registration flow | ❌ Not available | ✅ Registration flow | ❌ Already registered | ❌ Not available | ❌ Already registered |
| `/myinfo` | ✅ Player info | ✅ Team member info | ❌ Not registered | ✅ Player info | ✅ Team member info | ✅ Full info |
| `/status` | ✅ Player status | ✅ Team member status | ❌ Not registered | ✅ Player status | ✅ Team member status | ✅ Full status |
| `/list` | ✅ Active players | ✅ All players/members | ✅ Active players | ✅ Active players | ✅ All players/members | ✅ All players/members |
| `/add` | ❌ Not available | ✅ Add player | ❌ Not available | ❌ Not available | ✅ Add player | ✅ Add player |
| `/approve` | ❌ Not available | ✅ Approve player | ❌ Not available | ❌ Not available | ✅ Approve player | ✅ Approve player |
| `/pending` | ❌ Not available | ✅ Show pending | ❌ Not available | ❌ Not available | ✅ Show pending | ✅ Show pending |
| `/team` | ✅ Team info | ✅ Detailed team info | ✅ Team info | ✅ Team info | ✅ Detailed team info | ✅ Detailed team info |
| `/invite` | ❌ Not available | ✅ Generate link | ❌ Not available | ❌ Not available | ✅ Generate link | ✅ Generate link |
| `/health` | ❌ Not available | ✅ System health | ❌ Not available | ❌ Not available | ✅ System health | ✅ System health |
| `/version` | ✅ Version info | ✅ Version info | ✅ Version info | ✅ Version info | ✅ Version info | ✅ Version info |

## Quick Test Checklist

### ✅ Available Commands
- **Main Chat**: `/help`, `/start`, `/register`, `/myinfo`, `/status`, `/list`, `/team`, `/version`
- **Leadership Chat**: All commands available
- **Unregistered Users**: `/help`, `/start`, `/register`, `/team`, `/version`

### ❌ Restricted Commands
- **Main Chat**: `/add`, `/approve`, `/reject`, `/pending`, `/invite`, `/announce`, `/health`, `/config`
- **Unregistered Users**: `/myinfo`, `/status`, `/list` (player-specific)

### 🔄 Context-Aware Commands
- `/myinfo` - Shows player info in main chat, team member info in leadership chat
- `/status` - Shows player status in main chat, team member status in leadership chat  
- `/list` - Shows active players in main chat, all players/members in leadership chat
- `/help` - Shows relevant commands based on chat type and user permissions

## Expected Response Patterns

### Success Responses
- ✅ Use checkmark for successful operations
- 📋 Use clipboard for lists
- 👤 Use person icon for user information
- 🏆 Use trophy for team information

### Error Responses
- ❌ Use X for errors
- ⚠️ Use warning for permission issues
- 🔒 Use lock for restricted access

### Information Responses
- 📊 Use chart for status information
- 📝 Use memo for registration
- 🔗 Use link for invitations
- 🏥 Use hospital for health checks

## Validation Points

### 1. Permission Validation
- [ ] Commands respect chat type restrictions
- [ ] Commands respect user permission levels
- [ ] Error messages are clear and helpful

### 2. Context Validation
- [ ] Responses adapt to chat type (main vs leadership)
- [ ] User information shows appropriate details
- [ ] Lists show relevant information based on context

### 3. Data Validation
- [ ] Team ID is retrieved from Firestore (not hardcoded)
- [ ] User data is properly retrieved and displayed
- [ ] Error handling for missing or invalid data

### 4. Formatting Validation
- [ ] Responses use proper Markdown formatting
- [ ] Emojis are used appropriately
- [ ] Information is clearly structured and readable

## Common Test Cases

### Test Case 1: New User Registration
1. Send `/start` in main chat
2. Send `/help` to see available commands
3. Send `/register` to begin registration
4. Verify registration flow works correctly

### Test Case 2: Registered Player
1. Send `/myinfo` in main chat
2. Send `/status` to check status
3. Send `/list` to see active players
4. Verify player-specific information is shown

### Test Case 3: Leadership Functions
1. Send `/add` in leadership chat
2. Send `/pending` to see pending registrations
3. Send `/approve` to approve a player
4. Verify administrative functions work

### Test Case 4: Cross-Chat Behavior
1. Send `/myinfo` in both main and leadership chats
2. Send `/list` in both chats
3. Verify context-aware responses
4. Verify appropriate information is shown in each chat

### Test Case 5: Error Handling
1. Send restricted commands in wrong chat
2. Send invalid command formats
3. Verify clear error messages
4. Verify helpful guidance is provided 