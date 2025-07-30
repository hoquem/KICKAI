# Player Management Specification

## Document Information
- **Version**: 2.0
- **Date**: July 29, 2025
- **System**: KICKAI - AI-Powered Football Team Management
- **Domain**: Player Registration & Management

## Executive Summary

The Player Management system is a core domain within KICKAI that handles all player-related operations for amateur Sunday League football teams. It provides comprehensive player lifecycle management from initial registration through active participation, with AI-powered assistance for coaches and administrators.

## Business Context

### Sunday League Football Requirements
- **Squad Size**: Typically 16-20 players per team
- **Player Turnover**: High due to work commitments, injuries, and availability
- **Registration Process**: Leadership-driven with invite link workflow
- **Communication**: WhatsApp/Telegram based team coordination
- **Approval Workflow**: Coach/manager approval for new players

### Core Problems Solved
1. **Leadership-Driven Registration**: Team leadership adds players and sends invite links
2. **Player Information Tracking**: Centralized database for all player details
3. **Approval Workflows**: Structured process for player onboarding
4. **Contact Management**: Phone linking and emergency contacts
5. **Status Management**: Track player availability and team status

## System Architecture

### Clean Architecture Implementation
```
player_registration/
├── application/
│   ├── commands/           # Command definitions with @command decorator
│   └── handlers/           # Command handlers (delegate to agents)
├── domain/
│   ├── entities/          # Player entity and domain objects
│   ├── repositories/      # Repository interfaces
│   ├── services/          # Business logic services
│   └── tools/            # CrewAI tools for agents (@tool decorator)
├── infrastructure/        # Firebase repository implementations
└── tests/                # Unit, integration, and E2E tests
```

### Agent Integration
- **Primary Agent**: `PLAYER_COORDINATOR` - Handles all player-related requests
- **Secondary Agents**: `HELP_ASSISTANT`, `ONBOARDING_AGENT`
- **Tools**: Player-specific CrewAI tools for registration, status updates, and queries

## Functional Requirements

### 1. Player Registration

#### 1.1 Leadership-Driven Registration
- **Trigger**: Team leadership uses `/addplayer` command
- **Process**: 
  1. Leadership provides player details (name, phone, position)
  2. System creates Player entity with "pending" status
  3. Generate unique user_id and optional player_id
  4. Create invite link for player to join main chat
  5. Player joins via invite link and links phone number
  6. Submit for leadership approval

#### 1.2 Information Collection
- **Required Fields**:
  - Team ID (auto-detected from chat)
  - Telegram ID (auto-captured when joining)
  - First Name (from Telegram)
  - User ID (generated)
- **Optional Fields**:
  - Last Name, Phone Number, Email
  - Position, Preferred Foot, Jersey Number
  - Date of Birth, Emergency Contact, Medical Notes

#### 1.3 Validation Rules
- User ID format: `user_[generated_hash]`
- Position validation against `PlayerPosition` enum
- Preferred foot: "left", "right", or "both"
- Phone number format validation
- Age validation for insurance requirements

### 2. Player Status Management

#### 2.1 Status Lifecycle
```
pending → approved → active
    ↓        ↓        ↓
 rejected  rejected  inactive
```

#### 2.2 Status Transitions
- **Pending**: Initial registration state
- **Approved**: Leadership approval granted
- **Active**: Currently participating in team activities
- **Inactive**: Temporarily unavailable (injury, personal)
- **Rejected**: Registration denied

#### 2.3 Approval Workflow
- Leadership receives notification of new registration
- Review player information
- Use `/approve` or `/reject` commands
- Player receives confirmation of status change

### 3. Player Information Management

#### 3.1 Self-Service Updates
- **Command**: `/update` - Players can update their information
- **Available Fields**: Position, phone number, emergency contact
- **Validation**: All updates validated against business rules
- **Audit Trail**: All changes logged for tracking

#### 3.2 Leadership-Initiated Updates
- **Command**: `/addplayer` - Add new players
- **Command**: `/approve` - Approve pending players
- **Command**: `/reject` - Reject pending players
- **Command**: `/pending` - View pending approvals

### 4. Team Member Management

#### 4.1 Team Member vs Player Distinction
- **Players**: Active football team members
- **Team Members**: Coaches, managers, administrators
- **Separate Workflows**: Different registration and approval processes

#### 4.2 Team Member Registration
- **Command**: `/addmember` - Add team members (coaches, managers)
- **Leadership Chat**: Team members operate in leadership chat
- **Different Permissions**: Team members have administrative access

## Technical Implementation

### 4.1 Firebase Integration
- **Repository Pattern**: `FirebasePlayerRepository`
- **Async Operations**: All database operations asynchronous
- **Error Handling**: Comprehensive error handling and logging
- **Caching**: Local caching for frequently accessed data

#### 4.2 Telegram Integration
- **User Data Sync**: Automatic sync of Telegram profile changes
- **Notifications**: Registration status updates via bot
- **Phone Linking**: Secure phone number verification with contact sharing button

#### 4.3 Agent System Integration
- **Primary Agent**: PLAYER_COORDINATOR handles all player requests
- **Tool Registry**: Automatic tool discovery and registration
- **Context Passing**: Rich context for AI decision making

## User Experience Flows

### 1. New Player Registration Flow

#### 1.1 Happy Path
1. **Leadership Action**: Uses `/addplayer` command with player details
2. **System**: Creates player record with "pending" status
3. **System**: Generates invite link for main chat
4. **Leadership**: Sends invite link to player
5. **Player**: Joins main chat via invite link
6. **System**: Detects new member, sends welcome message with contact sharing button
7. **Player**: Shares phone number via contact button or manual entry
8. **System**: Links phone to player record
9. **Leadership**: Uses `/approve` to approve player
10. **System**: Status changes to "approved", then "active"

#### 1.2 Alternative Flows
- **Incomplete Information**: System prompts for missing required fields
- **Duplicate Registration**: System detects existing player, offers update
- **Leadership Rejection**: Player receives feedback and improvement suggestions

### 2. Player Information Management Flow

#### 2.1 Self-Service Updates
1. **User**: Uses `/myinfo` to view current information
2. **User**: Uses `/update` to modify personal details
3. **System**: Validates updates against business rules
4. **System**: Applies changes and confirms update
5. **System**: Logs change history for audit

#### 2.2 Leadership-Initiated Updates
1. **Leadership**: Uses `/pending` to view pending approvals
2. **Leadership**: Reviews current information
3. **Leadership**: Uses `/approve` or `/reject` commands
4. **System**: Applies changes with leadership authorization
5. **Player**: Receives notification of changes (if significant)

### 3. Team Roster Management Flow

#### 3.1 Roster Overview
1. **Leadership**: Uses `/list` command in leadership chat
2. **System**: PLAYER_COORDINATOR retrieves current squad
3. **System**: Displays all players by status and position
4. **System**: Shows recent registrations and status changes
5. **Leadership**: Can drill down for detailed player information

#### 3.2 Squad Selection
1. **Leadership**: Initiates squad selection for match
2. **System**: Shows available players by position
3. **System**: Indicates availability status and recent form
4. **Leadership**: Selects players for match squad
5. **System**: Notifies selected players

## ID Generation System

### Player ID Format
- **Format**: `{Number}{Initials}` (e.g., `01MH`, `02JS`)
- **Examples**:
  - Mahmudul Hoque → `01MH`
  - Second Mahmudul Hoque → `02MH`
  - John Smith → `01JS`
  - Second John Smith → `02JS`

### Team Member ID Format
- **Format**: `{Number}{Initials}` (same as players)
- **Examples**:
  - Coach John Smith → `01JS`
  - Manager Jane Doe → `01JD`

### ID Generation Rules
1. **Initials**: First letter of first name + first letter of last name
2. **Numbering**: Sequential numbering starting from 01
3. **Collision Resolution**: If initials exist, increment number (01, 02, 03...)
4. **Maximum**: 99 players per initials (sufficient for Sunday league teams)
5. **Fallback**: If 99+ players with same initials, use hash-based suffix

### ID Examples
```
Player Names → Generated IDs
Mahmudul Hoque → 01MH
John Smith → 01JS
Jane Smith → 02JS
Mike Johnson → 01MJ
Sarah Johnson → 02MJ
```

### Benefits for Sunday League
- ✅ **Simple**: Easy to remember and type
- ✅ **Human-readable**: Clear meaning to users
- ✅ **Scalable**: Supports up to 99 players per initials
- ✅ **Consistent**: Same format for players and team members
- ✅ **Typable**: Short enough for quick entry

## Available Commands

### Player Commands (Main Chat)
- `/myinfo` - View your player information
- `/status` - Check your current status
- `/list` - List all active players
- `/update` - Update your player information

### Leadership Commands (Leadership Chat)
- `/addplayer` - Add a new player with invite link
- `/addmember` - Add a new team member with invite link
- `/approve` - Approve a pending player/member
- `/reject` - Reject a pending player/member
- `/pending` - List pending approvals

## Performance Requirements

### 1. Response Times
- **Registration Commands**: < 2 seconds
- **Information Queries**: < 1 second
- **Roster Generation**: < 3 seconds
- **Search Operations**: < 2 seconds

### 2. Scalability
- **Players per Team**: Support up to 50 active players
- **Concurrent Operations**: Handle 10 simultaneous registrations
- **Database Queries**: Optimized indexes for common queries
- **Memory Usage**: Efficient caching for active players

### 3. Availability
- **Uptime**: 99.5% availability target
- **Error Recovery**: Graceful degradation on failures
- **Data Consistency**: Strong consistency for player status
- **Backup Strategy**: Daily automated backups

## Security and Privacy

### 1. Data Privacy
- **GDPR Compliance**: Right to erasure and data portability
- **Data Minimization**: Only collect necessary information
- **Consent Management**: Clear consent for data processing
- **Retention Policy**: Automatic deletion of inactive players (2 years)

### 2. Access Control
- **Role-Based Security**: Players, coaches, admins have different permissions
- **Telegram Authentication**: Secure user identification
- **Phone Verification**: Secure phone number linking process
- **Audit Logging**: All administrative actions logged

### 3. Data Protection
- **Encryption**: All sensitive data encrypted at rest
- **Secure Transmission**: HTTPS for all API communications
- **Access Logging**: Comprehensive access and modification logs
- **Backup Security**: Encrypted backups with access controls

## Integration Points

### 1. Telegram Bot Integration
- **New Member Detection**: Automatic detection of new chat members
- **Contact Sharing**: Secure phone number sharing via Telegram buttons
- **Message Routing**: Intelligent routing to appropriate agents
- **Status Updates**: Real-time status notifications

### 2. Firebase Integration
- **Real-time Updates**: Live data synchronization
- **Offline Support**: Graceful handling of network issues
- **Data Consistency**: Strong consistency guarantees
- **Scalability**: Automatic scaling with team growth

### 3. Agent System Integration
- **Intelligent Routing**: AI-powered request routing
- **Context Awareness**: Rich context for decision making
- **Natural Language**: Support for natural language queries
- **Learning**: Continuous improvement from user interactions

## Future Enhancements

### 1. Advanced Analytics
- **Player Performance Tracking**: Link registration data to match performance
- **Attendance Correlation**: Analyze registration patterns vs attendance
- **Team Dynamics**: Understand team composition and balance

### 2. Enhanced Communication
- **Automated Reminders**: Proactive notifications for pending actions
- **Multi-language Support**: Support for international teams
- **Rich Media**: Support for photos and documents

### 3. Integration Opportunities
- **League Management Systems**: Integration with league databases
- **Insurance Providers**: Direct integration for player insurance
- **Equipment Suppliers**: Automated equipment ordering