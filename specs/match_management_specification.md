# Match Management Specification

## Document Information
- **Version**: 1.0
- **Date**: July 29, 2025
- **System**: KICKAI - AI-Powered Football Team Management
- **Domain**: Match Management & Squad Selection

## Executive Summary

The Match Management system handles all aspects of football match organization for amateur Sunday League teams, from fixture creation to post-match analysis. It integrates attendance tracking, squad selection, and match logistics into a comprehensive match management solution with AI-powered assistance for tactical decisions.

## Business Context

### Sunday League Match Operations
- **Fixture Management**: League fixtures, cup matches, friendlies
- **Squad Selection**: 11 starting players + substitutes from available squad
- **Attendance Tracking**: Player availability for specific matches
- **Match Logistics**: Venue, kick-off time, travel arrangements
- **Result Recording**: Scores, goal scorers, match statistics

### Core Operational Challenges
1. **Player Availability**: Tracking who can play for each match
2. **Squad Selection**: Choosing optimal team from available players
3. **Communication**: Informing players about selection and match details
4. **Logistics Coordination**: Managing venue, transport, equipment
5. **Performance Tracking**: Recording results and player statistics

## System Architecture

### Clean Architecture Implementation
```
match_management/
├── application/
│   ├── commands/           # Match commands with @command decorator
│   └── handlers/           # Command handlers (delegate to agents)
├── domain/
│   ├── entities/          # Match, Attendance, Squad entities
│   ├── interfaces/        # Service interfaces
│   ├── repositories/      # Repository interfaces
│   ├── services/          # Business logic services
│   └── tools/            # CrewAI tools for match operations
├── infrastructure/        # Firebase repositories, external integrations
└── tests/                # Unit, integration, and E2E tests
```

### Agent Integration
- **Primary Agent**: `SQUAD_SELECTOR` - Handles squad selection and match preparation
- **Secondary Agents**: `AVAILABILITY_MANAGER`, `COMMUNICATION_MANAGER`
- **Tools**: Match-specific CrewAI tools for fixture management and squad selection

## Functional Requirements

### 1. Fixture Management

#### 1.1 Match Creation
- **Match Types**:
  - League fixtures (regular season matches)
  - Cup matches (knockout competitions)
  - Friendly matches (pre-season, training games)
  - Tournament matches (weekend tournaments)
- **Match Information**:
  - Opponent team name
  - Date and kick-off time
  - Venue (home/away/neutral)
  - Competition name
  - Referee assignments (if known)

#### 1.2 Fixture Import
- **League Integration**: Automatic import from league management systems
- **CSV Import**: Bulk import of fixtures from spreadsheets
- **Manual Entry**: Individual match creation through bot commands
- **Recurring Fixtures**: Set up weekly/monthly recurring matches

#### 1.3 Match Updates
- **Rescheduling**: Handle postponed or rearranged fixtures
- **Venue Changes**: Update match location
- **Kick-off Time Changes**: Adjust match timing
- **Competition Updates**: Modify competition details
- **Cancellation**: Handle cancelled matches with notifications

### 2. Attendance Management

#### 2.1 Availability Collection
- **Availability Requests**: Automatic requests sent to all players
- **Response Methods**:
  - `/markattendance` command with status
  - Natural language responses ("I can play", "Not available")
  - Emoji reactions (✅❌❔)
  - Bulk responses for multiple matches
- **Response Tracking**: Monitor who has/hasn't responded
- **Deadline Management**: Set response deadlines with reminders

#### 2.2 Availability Status
- **Status Types**:
  - **Available** (✅): Confirmed participation
  - **Unavailable** (❌): Cannot participate
  - **Maybe** (❔): Uncertain availability
  - **No Response** (⏳): Haven't provided status
- **Status Changes**: Allow players to update availability
- **Late Responses**: Handle responses after deadline

#### 2.3 Availability Analytics
- **Response Rates**: Track player response reliability
- **Availability Patterns**: Analyze player availability trends
- **Squad Depth Analysis**: Assess squad strength per position
- **Historical Data**: Track availability over multiple seasons

### 3. Squad Selection

#### 3.1 Automated Squad Selection
- **Formation-Based Selection**: Select players based on preferred formation
- **Position Optimization**: Ensure proper positional coverage
- **Availability Priority**: Prioritize confirmed available players
- **Performance Factors**: Consider recent form and statistics
- **Rotation Policy**: Ensure fair playing time distribution

#### 3.2 Manual Squad Override
- **Coach Selection**: Allow manual team selection
- **Tactical Adjustments**: Modify selection for specific opponents
- **Injury Considerations**: Account for player fitness concerns
- **Disciplinary Issues**: Handle suspensions and disciplinary exclusions
- **Squad Comments**: Add notes explaining selection decisions

#### 3.3 Squad Communication
- **Team Announcement**: Notify selected players
- **Squad List Distribution**: Share team sheet with all players
- **Selection Explanations**: Provide feedback to non-selected players
- **Last-Minute Changes**: Handle late availability changes
- **Match Instructions**: Communicate tactical instructions

### 4. Match Day Operations

#### 4.1 Pre-Match Preparation
- **Squad Confirmation**: Final availability check
- **Equipment Check**: Ensure kit and equipment ready
- **Travel Arrangements**: Coordinate team transport
- **Warm-up Planning**: Organize pre-match preparation
- **Opposition Research**: Brief on opponent strengths/weaknesses

#### 4.2 Match Day Management
- **Team Sheet Submission**: Submit official team sheet
- **Substitution Planning**: Prepare substitution strategy
- **Real-time Updates**: Handle late withdrawals/additions
- **Match Officials**: Liaise with referee and linesmen
- **Spectator Information**: Provide details for supporters

#### 4.3 Post-Match Processing
- **Result Recording**: Enter final score and result
- **Player Statistics**: Record goals, assists, bookings
- **Performance Notes**: Capture match observations
- **Man of the Match**: Select and announce standout performer
- **Match Report**: Generate comprehensive match summary

## Technical Specifications

### 1. Data Models

#### 1.1 Match Entity
```python
@dataclass
class Match:
    id: str
    team_id: str
    opponent: str
    date: str                    # ISO format
    location: Optional[str] = None
    status: str = "scheduled"    # scheduled, in_progress, completed, cancelled, postponed
    home_away: Optional[str] = None  # home, away, neutral
    competition: Optional[str] = None
    kick_off_time: Optional[str] = None
    referee: Optional[str] = None
    score: Optional[str] = None
    result: Optional[str] = None # win, loss, draw
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Match logistics
    travel_required: bool = False
    meet_time: Optional[str] = None
    meet_location: Optional[str] = None
    kit_colors: Optional[str] = None
    
    # Squad information
    squad_selected: bool = False
    squad_announced: bool = False
    team_sheet_submitted: bool = False
```

#### 1.2 Attendance Entity
```python
@dataclass
class Attendance:
    id: str                      # {team_id}_{match_id}_{player_id}
    player_id: str
    match_id: str
    team_id: str
    status: str                  # yes, no, maybe, not_responded
    response_timestamp: str
    response_method: str = "command"
    player_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

#### 1.3 Squad Selection Entity
```python
@dataclass
class SquadSelection:
    id: str
    match_id: str
    team_id: str
    formation: str              # 4-4-2, 4-3-3, etc.
    starting_xi: List[str]      # List of player IDs
    substitutes: List[str]      # List of substitute player IDs
    captain_id: Optional[str] = None
    vice_captain_id: Optional[str] = None
    selection_method: str = "manual"  # manual, assisted, automatic
    selected_by: str           # User ID of selector
    selection_notes: Optional[str] = None
    announced_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

### 2. Commands and Operations

#### 2.1 Match Management Commands
```python
@command(name="create_match", description="Create a new match fixture")
async def create_match_command(context: CommandContext) -> CommandResult

@command(name="matches", description="View upcoming matches")
async def list_matches_command(context: CommandContext) -> CommandResult

@command(name="match_details", description="Get detailed match information")
async def match_details_command(context: CommandContext) -> CommandResult

@command(name="reschedule", description="Reschedule a match")
async def reschedule_match_command(context: CommandContext) -> CommandResult
```

#### 2.2 Attendance Management Commands
```python
@command(name="markattendance", description="Record player availability for a match")
async def mark_attendance_command(context: CommandContext) -> CommandResult

@command(name="attendance", description="View match attendance status")
async def attendance_status_command(context: CommandContext) -> CommandResult
```

#### 2.3 Squad Selection Commands
```python
@command(name="select_squad", description="Select team for upcoming match")
async def select_squad_command(context: CommandContext) -> CommandResult

@command(name="team_sheet", description="View current team selection")
async def view_team_sheet_command(context: CommandContext) -> CommandResult

@command(name="announce_team", description="Announce team selection to players")
async def announce_team_command(context: CommandContext) -> CommandResult
```

### 3. CrewAI Tools

#### 3.1 Match Management Tools
```python
@tool
def create_match_fixture(team_id: str, opponent: str, date: str, 
                        location: str, competition: str) -> str:
    """Create a new match fixture"""

@tool
def get_upcoming_matches(team_id: str, limit: int = 5) -> str:
    """Get list of upcoming matches for team"""

@tool
def update_match_details(match_id: str, updates: dict) -> str:
    """Update match information"""

@tool
def get_match_details(match_id: str) -> str:
    """Get comprehensive match information"""
```

#### 3.2 Attendance Tools
```python
@tool
def record_player_availability(player_id: str, match_id: str, 
                             status: str, notes: str = None) -> str:
    """Record player availability for a match"""

@tool
def get_match_attendance(match_id: str) -> str:
    """Get attendance summary for a match"""

@tool
def send_availability_request(match_id: str, player_ids: List[str]) -> str:
    """Send availability request to players"""

@tool
def get_player_availability_history(player_id: str, months: int = 3) -> str:
    """Get player's availability history"""
```

#### 3.3 Squad Selection Tools
```python
@tool
def suggest_squad_selection(match_id: str, formation: str) -> str:
    """AI-powered squad selection suggestion"""

@tool
def validate_squad_selection(match_id: str, starting_xi: List[str], 
                           substitutes: List[str]) -> str:
    """Validate proposed squad selection"""

@tool
def announce_squad_selection(match_id: str, squad_selection_id: str) -> str:
    """Announce squad selection to players"""

@tool
def get_squad_selection_history(team_id: str, limit: int = 10) -> str:
    """Get historical squad selections"""
```

## ID Generation System

### Match ID Format
- **Format**: `M{DD}{MM}-{HOME}-{AWAY}` (e.g., `M1501-KAI-MAN`)
- **Examples**:
  - KickAI vs Manchester on Jan 15 → `M1501-KAI-MAN`
  - Home vs Away on Feb 20 → `M2002-HOME-AWAY`
  - Team A vs Team B on Mar 10 → `M1003-ALP-BET`

### Match ID Generation Rules
1. **Prefix**: Always starts with "M" for Match
2. **Date**: DD (day) + MM (month) format
3. **Teams**: Full team names or abbreviations (max 3-4 chars)
4. **Separator**: Hyphen (-) between date and teams
5. **Collision Resolution**: Add number suffix if needed (M1501-KAI-MAN1)

### Match ID Examples
```
Match Details → Generated IDs
KickAI vs Manchester, Jan 15 → M1501-KAI-MAN
Home vs Away, Feb 20 → M2002-HOME-AWAY
Team Alpha vs Team Beta, Mar 10 → M1003-ALP-BET
```

### Benefits for Sunday League
- ✅ **Simple**: Easy to read and understand
- ✅ **Date Context**: Clear match date information
- ✅ **Team Context**: Obvious team identification
- ✅ **Typable**: Short enough for quick entry
- ✅ **Human-readable**: Meaningful to users

## User Experience Flows

### 1. Match Creation Flow

#### 1.1 Manual Match Creation
1. **Coach**: Uses `/creatematch` command with match details
2. **System**: Validates match information and creates fixture
3. **System**: Validates date/time and checks for conflicts
4. **System**: Sends confirmation to coach and notifies players
5. **System**: Creates attendance tracking for the match

#### 1.2 Fixture Import Flow
1. **Coach**: Uploads fixture list (CSV/League API)
2. **System**: Processes and validates all fixtures
3. **System**: Creates match records for all valid fixtures
4. **System**: Identifies and reports any conflicts/errors
5. **System**: Notifies players of new fixtures

### 2. Attendance Management Flow

#### 2.1 Availability Collection
1. **System**: Sends availability request 1 week before match
2. **Players**: Receive notification with match details
3. **Players**: Respond using `/markattendance` command with status
4. **System**: Records responses and updates attendance status
5. **System**: Sends reminders to non-respondents

#### 2.2 Squad Selection Flow
1. **Coach**: Requests squad suggestion using `/selectsquad`
2. **System**: Analyzes available players and recent form
3. **System**: Suggests optimal squad based on positions and availability
4. **Coach**: Reviews and finalizes squad selection
5. **System**: Notifies selected players and reserves

### 3. Squad Selection Flow

#### 3.1 AI-Assisted Selection
1. **Coach**: Requests squad suggestion using `/select_squad`
2. **SQUAD_SELECTOR Agent**: Analyzes available players
3. **System**: Considers formation, positions, recent performance
4. **System**: Presents suggested starting XI and substitutes
5. **Coach**: Reviews, modifies, and approves selection

#### 3.2 Manual Selection Override
1. **Coach**: Manually selects players for specific positions
2. **System**: Validates selection (positions, availability)
3. **System**: Warns about potential issues (formation gaps)
4. **Coach**: Confirms final selection with optional notes
5. **System**: Creates squad selection record

### 4. Match Day Operations Flow

#### 4.1 Pre-Match Preparation
1. **System**: Sends match day reminders to selected players
2. **System**: Provides travel and logistics information
3. **Players**: Confirm final availability 2 hours before kick-off
4. **Coach**: Makes any last-minute squad changes
5. **System**: Submits official team sheet

#### 4.2 Post-Match Recording
1. **Coach**: Uses `/matchstatus` to record final score
2. **System**: Validates score format and updates match record
3. **System**: Records goal scorers and assists
4. **System**: Updates team statistics and league table
5. **System**: Notifies players of match result

## Integration Requirements

### 1. External System Integration

#### 1.1 League Management Systems
- **Fixture Import**: Automatic fixture synchronization
- **Result Submission**: Submit match results to league
- **Table Updates**: Receive league table updates
- **Player Registration**: Sync with league player databases

#### 1.2 Calendar Integration
- **Google Calendar**: Sync matches with team calendars
- **Outlook Integration**: Support Microsoft calendar sync
- **iCal Export**: Provide calendar export functionality
- **Personal Calendars**: Allow players to sync to personal calendars

### 2. Internal System Integration

#### 2.1 Player Management Integration
- **Player Availability**: Link to player status and eligibility
- **Contact Information**: Use player contact details for notifications
- **Position Data**: Utilize player position information for selection
- **Performance History**: Access player statistics for selection decisions

#### 2.2 Communication Integration
- **Notification System**: Send match-related notifications
- **Team Chat**: Integrate with team communication channels
- **Social Media**: Share match results and updates
- **Website Integration**: Update team website with fixtures/results

## Available Commands

### Leadership Commands (Leadership Chat)
- `/creatematch` - Create a new match
- `/listmatches` - List upcoming matches
- `/matchstatus` - Check match status
- `/selectsquad` - Select squad for match

### Player Commands (Main Chat)
- `/listmatches` - List upcoming matches
- `/matchstatus` - Check match status
- `/attendance` - View match attendance information
- `/markattendance` - Mark your attendance for a match
- `/attendancehistory` - View your attendance history

## Performance Requirements

### 1. Response Times
- **Match Creation**: < 2 seconds
- **Attendance Recording**: < 1 second
- **Squad Selection**: < 3 seconds for AI suggestions
- **Match Queries**: < 2 seconds for fixture lists

### 2. Scalability
- **Matches per Season**: Support 50+ matches per team per season
- **Concurrent Users**: Handle 20+ simultaneous availability responses
- **Historical Data**: Maintain 5+ years of match history
- **Multi-Team Support**: Scale to 100+ teams on platform

### 3. Reliability
- **Data Integrity**: Ensure match data consistency
- **Notification Delivery**: 99%+ notification delivery rate
- **Backup Systems**: Daily backup of all match data
- **Disaster Recovery**: 4-hour maximum recovery time

## Security and Privacy

### 1. Data Protection
- **Player Privacy**: Protect player personal information
- **Match Security**: Secure match details and squad information
- **Access Controls**: Role-based access to match management
- **Audit Trails**: Log all match data modifications

### 2. Communication Security
- **Secure Notifications**: Encrypted message delivery
- **Authentication**: Verify user identity for responses
- **Anti-Spam**: Prevent unauthorized match communications
- **Data Retention**: Appropriate retention of match communications

## Quality Assurance

### 1. Testing Strategy
- **Unit Tests**: 90%+ coverage for match logic
- **Integration Tests**: End-to-end match workflows
- **Load Testing**: Performance under peak usage
- **User Acceptance**: Real coach testing and feedback

### 2. Data Validation
- **Input Validation**: Comprehensive validation of match data
- **Business Rules**: Enforce sport-specific constraints
- **Consistency Checks**: Ensure data consistency across entities
- **Error Recovery**: Graceful handling of data issues

## Future Enhancements

### 1. Advanced Features
- **Tactical Analysis**: Pre and post-match tactical insights
- **Opposition Scouting**: Opponent analysis and preparation
- **Player Performance Analytics**: Individual performance tracking
- **Video Integration**: Match video upload and analysis

### 2. Mobile and Convenience
- **Mobile App**: Dedicated mobile match management app
- **Location Services**: GPS-based match check-in
- **Push Notifications**: Real-time match updates
- **Offline Mode**: Core functionality without internet

### 3. Integration Opportunities
- **Streaming Services**: Live match streaming integration
- **Statistics Platforms**: Professional statistics tracking
- **Betting Integration**: Responsible gambling features
- **Social Sharing**: Enhanced social media integration

## Success Metrics

### 1. Operational Efficiency
- **Response Rate**: >90% of players respond to availability requests
- **Selection Time**: <10 minutes average squad selection time
- **Communication Clarity**: <5% requests for clarification
- **Match Day Preparation**: 100% of selected players notified

### 2. User Satisfaction
- **Coach Satisfaction**: >4.5/5 match management experience
- **Player Satisfaction**: >4.0/5 communication and selection process
- **System Reliability**: <1% match data errors
- **Response Time**: 95% of operations complete within SLA

### 3. Business Impact
- **Administrative Time**: 60% reduction in match administration time
- **Squad Selection Quality**: Improved team performance metrics
- **Player Engagement**: Increased player participation rates
- **Coach Efficiency**: More time for tactical preparation

---

**Document Status**: Draft v1.0
**Next Review**: August 15, 2025
**Stakeholders**: Product Manager, Technical Lead, Team Coaches