# KICKAI Command Testing Matrix

Quick reference for testing command behavior across different scenarios in the unified processing architecture.

## Test Matrix

| Command | Main Chat | Leadership Chat | Unregistered | Registered Player | Team Member | Admin |
|---------|-----------|-----------------|--------------|-------------------|-------------|-------|
| `/help` | ✅ Player commands | ✅ All commands | ✅ Basic only | ✅ Player commands | ✅ All commands | ✅ All commands |
| `/start` | ✅ Welcome message | ✅ Leadership welcome | ✅ Welcome message | ✅ Welcome message | ✅ Leadership welcome | ✅ Leadership welcome |
| `/register` | ✅ Registration flow | ✅ Registration flow | ✅ Registration flow | ❌ Already registered | ❌ Already registered | ❌ Already registered |
| `/myinfo` | ✅ Player info | ✅ Team member info | ❌ Not registered | ✅ Player info | ✅ Team member info | ✅ Full info |
| `/status` | ✅ Own status | ✅ Any player status | ❌ Not registered | ✅ Own status | ✅ Any player status | ✅ Any player status |
| `/list` | ✅ Active players | ✅ All players with status | ✅ Active players | ✅ Active players | ✅ All players with status | ✅ All players with status |
| `/add` | ❌ Not available | ✅ Add player | ❌ Not available | ❌ Not available | ✅ Add player | ✅ Add player |
| `/approve` | ❌ Not available | ❌ Admin only | ❌ Not available | ❌ Not available | ❌ Admin only | ✅ Approve player |
| `/reject` | ❌ Not available | ❌ Admin only | ❌ Not available | ❌ Not available | ❌ Admin only | ✅ Reject player |
| `/pending` | ❌ Not available | ✅ Show pending | ❌ Not available | ❌ Not available | ✅ Show pending | ✅ Show pending |
| `/announce` | ❌ Not available | ✅ Send announcement | ❌ Not available | ❌ Not available | ✅ Send announcement | ✅ Send announcement |

## Quick Test Checklist

### ✅ Available Commands
- **Main Chat**: `/help`, `/start`, `/register`, `/myinfo`, `/status`, `/list`
- **Leadership Chat**: All commands based on user role
- **Unregistered Users**: `/help`, `/start`, `/register`

### ❌ Restricted Commands
- **Main Chat**: `/add`, `/approve`, `/reject`, `/pending`, `/announce`
- **Unregistered Users**: `/myinfo`, `/status`, `/list` (player-specific)
- **Team Members**: `/approve`, `/reject` (admin only)

### 🔄 Context-Aware Commands (Separate Implementations)
- `/myinfo` - Shows player info in main chat, team member info in leadership chat
- `/status` - Shows own status in main chat, any player status in leadership chat  
- `/list` - Shows active players in main chat, all players with status in leadership chat
- `/help` - Shows relevant commands based on chat type and user permissions

## Unified Processing Architecture

### **Both Slash Commands and Natural Language**
- All inputs converge to the same CrewAI orchestration pipeline
- Same permission checking and security for both input types
- Consistent behavior regardless of input method

### **Test Both Input Methods**
```bash
# Test slash command
/list

# Test natural language (should behave identically)
"show me the player list"
"who are the active players"
"list all players"
```

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

### 1. Unified Processing Validation
- [ ] Both slash commands and natural language use same pipeline
- [ ] Same permission checking for both input types
- [ ] Consistent behavior regardless of input method

### 2. Permission Validation
- [ ] Commands respect chat type restrictions
- [ ] Commands respect user permission levels
- [ ] Error messages are clear and helpful

### 3. Context Validation
- [ ] Responses adapt to chat type (main vs leadership)
- [ ] User information shows appropriate details
- [ ] Lists show relevant information based on context

### 4. Data Validation
- [ ] Chat IDs retrieved from Firestore (`main_chat_id`, `leadership_chat_id`)
- [ ] User data is properly retrieved and displayed
- [ ] Error handling for missing or invalid data

### 5. Formatting Validation
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
3. Send `/approve` to approve a player (admin only)
4. Verify administrative functions work

### Test Case 4: Cross-Chat Behavior
1. Send `/myinfo` in both main and leadership chats
2. Send `/list` in both chats
3. Verify context-aware responses
4. Verify appropriate information is shown in each chat

### Test Case 5: Unified Processing
1. Test slash command `/list`
2. Test natural language "show me the player list"
3. Verify both produce identical results
4. Verify same permission checking applies

### Test Case 6: Error Handling
1. Send restricted commands in wrong chat
2. Send invalid command formats
3. Verify clear error messages
4. Verify helpful guidance is provided

### Test Case 7: Role-Based Access
1. Test admin commands as team member (should fail)
2. Test admin commands as admin (should succeed)
3. Verify appropriate error messages for insufficient permissions

## Natural Language Testing

### **Test Natural Language Equivalents**
```bash
# Instead of /list, try:
"show me the players"
"who is on the team"
"list all team members"

# Instead of /myinfo, try:
"what's my information"
"show my details"
"who am I"

# Instead of /status, try:
"what's my status"
"am I approved"
"check my registration status"
```

### **Expected Behavior**
- Natural language should produce identical results to slash commands
- Same permission checking should apply
- Same context-aware behavior should apply
- Same error handling should apply

## CrewAI Orchestration Testing

### **Pipeline Steps to Verify**
1. **Intent Classification** - Correctly identifies command intent
2. **Complexity Assessment** - Properly routes to appropriate agent
3. **Task Decomposition** - Breaks complex tasks into subtasks
4. **Agent Routing** - Routes to correct specialized agent
5. **Task Execution** - Executes task with proper context
6. **Result Aggregation** - Combines results into coherent response

### **Agent Selection Validation**
- [ ] HelpAssistantAgent handles help requests
- [ ] PlayerCoordinatorAgent handles player operations
- [ ] TeamManagerAgent handles team management
- [ ] FinanceManagerAgent handles financial operations
- [ ] PerformanceAnalystAgent handles analytics
- [ ] LearningAgent handles system optimization
- [ ] OnboardingAgent handles registration
- [ ] CommandFallbackAgent handles unrecognized commands

This testing matrix ensures comprehensive validation of the unified processing architecture! 🚀 