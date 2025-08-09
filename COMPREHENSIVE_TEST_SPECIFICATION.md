# KICKAI Bot Comprehensive Test Specification

## Test Environment Setup

### LLM Configuration
- **Provider**: Groq
- **Model**: Llama-3.1-8B-Instruct (or available Groq model)
- **Context**: Real-time conversation with full memory

### Database Configuration
- **Database**: Real Firebase Firestore
- **Environment**: Test environment with cleanup before/after tests
- **Collections**: kickai_teams, kickai_players, kickai_team_members, kickai_matches

### Test Infrastructure
- **Tool**: Mock Telegram Tester
- **Agents**: All 5 KICKAI agents (message_processor, help_assistant, player_coordinator, team_administrator, squad_selector)
- **Commands**: Both slash commands and natural language queries

## Test Data Setup

### Teams to Create
1. **Team ID**: TEST1
   - **Name**: "KickAI Test Team 1"
   - **Main Chat ID**: -1001234567890
   - **Leadership Chat ID**: -1001234567891

2. **Team ID**: TEST2
   - **Name**: "KickAI Test Team 2"
   - **Main Chat ID**: -1001234567892
   - **Leadership Chat ID**: -1001234567893

### Test Players
1. **Player 1**: John Smith (JS)
   - **Phone**: +1234567890
   - **Position**: Forward
   - **Status**: Active

2. **Player 2**: Sarah Johnson (SJ)
   - **Phone**: +1234567891
   - **Position**: Midfielder
   - **Status**: Pending

3. **Player 3**: Mike Davis (MD)
   - **Phone**: +1234567892
   - **Position**: Defender
   - **Status**: Active

### Test Team Members
1. **Team Member 1**: Coach Wilson
   - **Role**: Head Coach
   - **Admin**: Yes
   - **Phone**: +1234567893

2. **Team Member 2**: Manager Brown
   - **Role**: Team Manager
   - **Admin**: No
   - **Phone**: +1234567894

## Test Categories

### 1. System Initialization Tests
**Objective**: Verify system startup and basic functionality

#### Test 1.1: Bot Startup
- **Command**: `/start`
- **Expected**: Welcome message with available commands
- **Agent**: message_processor
- **Validation**: Check response contains help information

#### Test 1.2: Help System
- **Command**: `/help`
- **Expected**: Comprehensive help message
- **Agent**: help_assistant
- **Validation**: Verify all command categories are listed

#### Test 1.3: Command Help
- **Command**: `/help register`
- **Expected**: Specific help for registration command
- **Agent**: help_assistant
- **Validation**: Detailed registration instructions

### 2. Player Registration Tests
**Objective**: Test player registration workflow

#### Test 2.1: Player Registration (Slash Command)
- **Command**: `/register JS`
- **Expected**: Player registration success
- **Agent**: player_coordinator
- **Validation**: Check Firestore for player record

#### Test 2.2: Player Registration (Natural Language)
- **Query**: "I want to register as a player with ID JS"
- **Expected**: Same as above
- **Agent**: player_coordinator
- **Validation**: Verify natural language processing

#### Test 2.3: Duplicate Registration
- **Command**: `/register JS`
- **Expected**: Error message about existing player
- **Agent**: player_coordinator
- **Validation**: No duplicate records created

#### Test 2.4: Player Status Check
- **Command**: `/myinfo`
- **Expected**: Current player status
- **Agent**: message_processor
- **Validation**: Correct status displayed

### 3. Team Member Management Tests
**Objective**: Test team member registration and management

#### Test 3.1: Team Member Registration (Leadership Chat)
- **Command**: `/register Coach Wilson`
- **Expected**: Team member registration
- **Agent**: player_coordinator
- **Validation**: Check Firestore for team member record

#### Test 3.2: Team Member Status
- **Command**: `/myinfo` (in leadership chat)
- **Expected**: Team member status
- **Agent**: message_processor
- **Validation**: Correct role and permissions

### 4. Player Management Tests
**Objective**: Test player approval and management

#### Test 4.1: Player Approval (Leadership)
- **Command**: `/approve SJ`
- **Expected**: Player approved successfully
- **Agent**: player_coordinator
- **Validation**: Status changed to Active in Firestore

#### Test 4.2: Player List (Main Chat)
- **Command**: `/list`
- **Expected**: Only active players listed
- **Agent**: message_processor
- **Validation**: Pending players not shown

#### Test 4.3: Player List (Leadership Chat)
- **Command**: `/list`
- **Expected**: All players with status
- **Agent**: message_processor
- **Validation**: Both active and pending players shown

#### Test 4.4: Player Status by Phone
- **Command**: `/status +1234567890`
- **Expected**: Player status for John Smith
- **Agent**: message_processor
- **Validation**: Correct player information

### 5. Match Management Tests
**Objective**: Test match creation and management

#### Test 5.1: Create Match (Leadership)
- **Command**: `/creatematch "City Rivals" 2024-08-15 19:00 "Central Stadium"`
- **Expected**: Match created successfully
- **Agent**: squad_selector
- **Validation**: Match record in Firestore

#### Test 5.2: List Matches
- **Command**: `/listmatches`
- **Expected**: List of upcoming matches
- **Agent**: squad_selector
- **Validation**: Match details displayed correctly

#### Test 5.3: Squad Selection
- **Command**: `/selectsquad MATCH001 JS,MD`
- **Expected**: Squad selected successfully
- **Agent**: squad_selector
- **Validation**: Squad record in Firestore

### 6. Communication Tests
**Objective**: Test messaging and announcements

#### Test 6.1: Send Announcement (Leadership)
- **Command**: `/announce "Team meeting tomorrow at 6 PM"`
- **Expected**: Announcement sent
- **Agent**: team_administrator
- **Validation**: Message sent to appropriate chats

#### Test 6.2: Send Poll
- **Command**: `/poll "Best training time?" "6 PM,7 PM,8 PM"`
- **Expected**: Poll created
- **Agent**: message_processor
- **Validation**: Poll message sent

### 7. Natural Language Processing Tests
**Objective**: Test natural language understanding

#### Test 7.1: Status Query
- **Query**: "What's my current status?"
- **Expected**: User status information
- **Agent**: message_processor
- **Validation**: Correct status based on user type

#### Test 7.2: Player Information
- **Query**: "Who are the active players?"
- **Expected**: List of active players
- **Agent**: message_processor
- **Validation**: Same as /list command

#### Test 7.3: Match Information
- **Query**: "When is our next match?"
- **Expected**: Next match details
- **Agent**: squad_selector
- **Validation**: Upcoming match information

#### Test 7.4: Help Request
- **Query**: "How do I register as a player?"
- **Expected**: Registration instructions
- **Agent**: help_assistant
- **Validation**: Clear step-by-step instructions

### 8. Error Handling Tests
**Objective**: Test system error handling

#### Test 8.1: Invalid Command
- **Command**: `/invalidcommand`
- **Expected**: Helpful error message
- **Agent**: help_assistant
- **Validation**: Graceful error handling

#### Test 8.2: Missing Parameters
- **Command**: `/register`
- **Expected**: Parameter requirement message
- **Agent**: player_coordinator
- **Validation**: Clear parameter instructions

#### Test 8.3: Unauthorized Access
- **Command**: `/approve JS` (from main chat)
- **Expected**: Access denied message
- **Agent**: message_processor
- **Validation**: Proper permission checking

### 9. Cross-Chat Functionality Tests
**Objective**: Test functionality across different chat types

#### Test 9.1: Main Chat vs Leadership Chat
- **Test**: Same command in different chats
- **Expected**: Different responses based on chat type
- **Agent**: message_processor
- **Validation**: Context-aware responses

#### Test 9.2: User Flow Detection
- **Test**: User interaction patterns
- **Expected**: Appropriate agent selection
- **Validation**: Correct agent routing

## Test Execution Plan

### Phase 1: Environment Setup
1. Clean Firestore test collections
2. Create test teams and initial data
3. Configure mock Telegram tester
4. Set up Groq LLM connection

### Phase 2: Basic Functionality Tests
1. System initialization tests
2. Help system tests
3. Basic command recognition

### Phase 3: Core Feature Tests
1. Player registration workflow
2. Team member management
3. Player approval process
4. List and status commands

### Phase 4: Advanced Feature Tests
1. Match management
2. Squad selection
3. Communication features

### Phase 5: Natural Language Tests
1. Various natural language queries
2. Context understanding
3. Agent routing validation

### Phase 6: Error Handling Tests
1. Invalid commands
2. Missing parameters
3. Permission violations

### Phase 7: Integration Tests
1. Cross-chat functionality
2. End-to-end workflows
3. Data consistency validation

## Success Criteria

### Functional Requirements
- All commands execute successfully
- Natural language queries are understood
- Data is correctly stored in Firestore
- Agent routing works correctly
- Error handling is graceful

### Performance Requirements
- Response time < 5 seconds for all commands
- LLM calls are efficient and relevant
- Memory usage remains stable
- No memory leaks or resource issues

### Quality Requirements
- All test cases pass
- No critical errors or crashes
- Data integrity maintained
- User experience is smooth

## Reporting Requirements

### Test Execution Log
- Timestamp for each test
- Command/query executed
- Agent used
- LLM calls made
- Response received
- Pass/fail status

### LLM Interaction Log
- All Groq API calls
- Prompts sent
- Responses received
- Token usage
- Response time

### Agent Performance Log
- Agent selection logic
- Tool usage patterns
- Success/failure rates
- Response quality

### Data Validation Log
- Firestore operations
- Data consistency checks
- Record creation/updates
- Query results

## Expected Outcomes

### Success Metrics
- 100% test case pass rate
- All agents functioning correctly
- Natural language processing working
- Data integrity maintained
- User experience smooth

### Deliverables
1. Complete test execution report
2. LLM interaction analysis
3. Agent performance metrics
4. Data validation results
5. Recommendations for improvements

This specification provides a comprehensive framework for testing the KICKAI bot's functionality using the mock Telegram tester with Groq LLM and real Firestore.
