# Player Management Specification

## Document Information
- **Version**: 1.0
- **Date**: July 29, 2025
- **System**: KICKAI - AI-Powered Football Team Management
- **Domain**: Player Registration & Management

## Executive Summary

The Player Management system is a core domain within KICKAI that handles all player-related operations for amateur Sunday League football teams. It provides comprehensive player lifecycle management from initial registration through active participation, with AI-powered assistance for coaches and administrators.

## Business Context

### Sunday League Football Requirements
- **Squad Size**: Typically 16-20 players per team
- **Player Turnover**: High due to work commitments, injuries, and availability
- **Registration Process**: Often informal, requiring structured digital approach
- **Communication**: WhatsApp/Telegram based team coordination
- **Approval Workflow**: Coach/manager approval for new players

### Core Problems Solved
1. **Manual Player Registration**: Eliminates paper forms and manual data entry
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

#### 1.1 Initial Registration
- **Trigger**: New user joins team Telegram chat or uses `/register` command
- **Process**: 
  1. Capture Telegram user data (name, username, phone)
  2. Create Player entity with "pending" status
  3. Generate unique user_id and optional player_id
  4. Request additional information (position, emergency contact)
  5. Submit for coach approval

#### 1.2 Information Collection
- **Required Fields**:
  - Team ID (auto-detected from chat)
  - Telegram ID (auto-captured)
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
- **Approved**: Coach/admin approval granted
- **Active**: Currently participating in team activities
- **Inactive**: Temporarily unavailable (injury, personal)
- **Rejected**: Registration denied

#### 2.3 Approval Workflow
- Coach receives notification of new registration
- Review player information
- Approve/reject with optional comments
- Automated notification to player

### 3. Player Information Management

#### 3.1 Profile Updates
- **Self-Service**: Players can update personal information
- **Admin Updates**: Coaches can update all fields
- **Version Control**: Track changes with timestamps
- **Validation**: Business rules applied to all updates

#### 3.2 Football-Specific Data
- **Position Management**: Primary and secondary positions
- **Jersey Numbers**: Unique within team, coach assignment
- **Performance Tracking**: Goals, assists, appearances (future)
- **Availability**: Weekly availability for matches/training

#### 3.3 Contact Information
- **Phone Linking**: Link Telegram account to phone number
- **Emergency Contacts**: Required for insurance/safety
- **Communication Preferences**: Match notifications, reminders

### 4. Player Queries and Reporting

#### 4.1 Player Search
- Search by name, position, status
- Filter by registration date, activity level
- Quick lookup by Telegram username

#### 4.2 Team Roster Management
- Current active players list
- Squad selection assistance
- Position-based filtering
- Availability overview

#### 4.3 Registration Analytics
- New registrations per week/month
- Approval rates and timelines
- Player retention metrics
- Position distribution analysis

## Technical Specifications

### 1. Data Model

#### 1.1 Player Entity
```python
@dataclass
class Player:
    # Core identification
    user_id: str              # Primary key - user_[hash]
    team_id: str              # Foreign key to team
    telegram_id: Optional[str]
    player_id: Optional[str]   # Team-specific ID (e.g., "KTI_MH_001")
    
    # Personal information
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    username: Optional[str]
    
    # Football-specific
    position: Optional[str]
    preferred_foot: Optional[str]
    jersey_number: Optional[str]
    
    # Contact and personal
    phone_number: Optional[str]
    email: Optional[str]
    date_of_birth: Optional[str]
    emergency_contact: Optional[str]
    medical_notes: Optional[str]
    
    # Status and workflow
    status: str = "pending"
    
    # Metadata
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    source: Optional[str]
    sync_version: Optional[str]
```

#### 1.2 Database Schema (Firestore)
- **Collection**: `kickai_players`
- **Document ID**: `{team_id}_{user_id}`
- **Indexes**: team_id, status, position, created_at
- **Security Rules**: Role-based access control

### 2. API Endpoints (Commands)

#### 2.1 Registration Commands
```python
@command(name="register", description="Register as a new player")
async def register_player_command(context: CommandContext) -> CommandResult

@command(name="myinfo", description="View your player information") 
async def get_player_info_command(context: CommandContext) -> CommandResult

@command(name="update", description="Update player information")
async def update_player_command(context: CommandContext) -> CommandResult
```

#### 2.2 Administrative Commands
```python
@command(name="approve", description="Approve player registration")
async def approve_player_command(context: CommandContext) -> CommandResult

@command(name="roster", description="View team roster")
async def get_team_roster_command(context: CommandContext) -> CommandResult

@command(name="players", description="Search and manage players")
async def manage_players_command(context: CommandContext) -> CommandResult
```

### 3. CrewAI Tools

#### 3.1 Registration Tools
```python
@tool
def register_new_player(team_id: str, telegram_data: dict) -> str:
    """Register a new player with initial Telegram data"""

@tool
def update_player_information(user_id: str, updates: dict) -> str:
    """Update player information with validation"""

@tool
def get_player_status(user_id: str) -> str:
    """Get current player status and information"""
```

#### 3.2 Management Tools
```python
@tool
def approve_player_registration(user_id: str, approver_id: str) -> str:
    """Approve a pending player registration"""

@tool
def get_team_players(team_id: str, status_filter: str = None) -> str:
    """Get list of team players with optional status filter"""

@tool
def search_players(team_id: str, search_term: str) -> str:
    """Search players by name, position, or other criteria"""
```

### 4. Integration Points

#### 4.1 Firebase Integration
- **Repository Pattern**: `FirebasePlayerRepository`
- **Async Operations**: All database operations asynchronous
- **Error Handling**: Comprehensive error handling and logging
- **Caching**: Local caching for frequently accessed data

#### 4.2 Telegram Integration
- **User Data Sync**: Automatic sync of Telegram profile changes
- **Notifications**: Registration status updates via bot
- **Phone Linking**: Secure phone number verification

#### 4.3 Agent System Integration
- **Primary Agent**: PLAYER_COORDINATOR handles all player requests
- **Tool Registry**: Automatic tool discovery and registration
- **Context Passing**: Rich context for AI decision making

## User Experience Flows

### 1. New Player Registration Flow

#### 1.1 Happy Path
1. **User Action**: New member joins Telegram chat
2. **System**: Detects new member, sends welcome message
3. **User**: Responds with registration intent or uses `/register`
4. **System**: ONBOARDING_AGENT guides through registration
5. **User**: Provides required information (position, emergency contact)
6. **System**: Creates Player entity with "pending" status
7. **Coach**: Receives approval notification
8. **Coach**: Reviews and approves registration
9. **User**: Receives approval confirmation
10. **System**: Status changes to "approved", then "active"

#### 1.2 Alternative Flows
- **Incomplete Information**: System prompts for missing required fields
- **Duplicate Registration**: System detects existing player, offers update
- **Coach Rejection**: Player receives feedback and improvement suggestions

### 2. Player Information Management Flow

#### 2.1 Self-Service Updates
1. **User**: Uses `/myinfo` to view current information
2. **User**: Uses `/update` to modify personal details
3. **System**: Validates updates against business rules
4. **System**: Applies changes and confirms update
5. **System**: Logs change history for audit

#### 2.2 Coach-Initiated Updates
1. **Coach**: Uses `/players [name]` to find player
2. **Coach**: Reviews current information
3. **Coach**: Uses administrative commands to update
4. **System**: Applies changes with coach authorization
5. **Player**: Receives notification of changes (if significant)

### 3. Team Roster Management Flow

#### 3.1 Roster Overview
1. **Coach**: Uses `/roster` command
2. **System**: PLAYER_COORDINATOR retrieves current squad
3. **System**: Displays active players by position
4. **System**: Shows recent registrations and status changes
5. **Coach**: Can drill down for detailed player information

#### 3.2 Squad Selection
1. **Coach**: Initiates squad selection for match
2. **System**: Shows available players by position
3. **System**: Indicates availability status and recent form
4. **Coach**: Selects players for match squad
5. **System**: Notifies selected players

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
- **API Security**: Rate limiting and input validation
- **Audit Logging**: Track all data modifications

### 3. Data Protection
- **Encryption**: All personal data encrypted at rest
- **Secure Transport**: HTTPS/TLS for all communications
- **Phone Number Privacy**: Secure phone linking process
- **Emergency Contact Security**: Restricted access to sensitive information

## Quality Assurance

### 1. Testing Strategy
- **Unit Tests**: 90%+ code coverage for business logic
- **Integration Tests**: Database and external service integration
- **E2E Tests**: Complete user workflow testing
- **Performance Tests**: Load testing for peak usage

### 2. Validation Framework
- **Input Validation**: Comprehensive validation for all user inputs
- **Business Rule Validation**: Enforce domain constraints
- **Cross-Field Validation**: Ensure data consistency
- **Error Handling**: User-friendly error messages

### 3. Monitoring and Alerts
- **Registration Metrics**: Track registration success rates
- **Performance Monitoring**: Response time tracking
- **Error Tracking**: Automated error reporting
- **User Feedback**: Collect and analyze user satisfaction

## Future Enhancements

### 1. Advanced Features
- **Player Statistics**: Performance tracking and analytics
- **Injury Management**: Injury history and recovery tracking
- **Player Development**: Skill progression tracking
- **Social Features**: Player profiles and achievements

### 2. Integration Opportunities
- **FA Registration**: Integration with Football Association systems
- **Insurance Integration**: Automated insurance enrollment
- **Equipment Management**: Kit and equipment tracking
- **Calendar Integration**: Personal calendar sync for availability

### 3. Mobile Experience
- **Mobile App**: Dedicated mobile application
- **Offline Support**: Core functionality without internet
- **Push Notifications**: Real-time updates and reminders
- **Location Services**: Training ground check-in

## Success Metrics

### 1. Registration Metrics
- **Registration Completion Rate**: >85% of started registrations completed
- **Approval Time**: <24 hours average approval time
- **Information Accuracy**: <5% data correction requests
- **User Satisfaction**: >4.5/5 registration experience rating

### 2. Usage Metrics
- **Active Player Ratio**: >80% of registered players remain active
- **Information Updates**: >60% of players update info quarterly
- **Coach Adoption**: >90% of coaches use player management features
- **System Reliability**: <0.1% data loss or corruption incidents

### 3. Business Impact
- **Administrative Time Savings**: 70% reduction in manual processes
- **Communication Efficiency**: 50% reduction in clarification requests
- **Team Organization**: Improved match day organization and preparation
- **Player Retention**: 15% improvement in player retention rates

---

**Document Status**: Draft v1.0
**Next Review**: August 15, 2025
**Stakeholders**: Product Manager, Technical Lead, Coach Representatives