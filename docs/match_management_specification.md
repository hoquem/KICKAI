# KICKAI Match Management & Attendance Specification
## Product Specification for Sunday League Team Management

**Document Version**: 1.0  
**Date**: August 2025  
**Product Owner**: KICKAI Team  
**Target Users**: Sunday League Teams, Players, Team Managers  

---

## 🎯 **EXECUTIVE SUMMARY**

This specification defines the **Match Management Integration** and **Availability & Attendance Tracking** features for the KICKAI Sunday league team management system. These features are **critical priorities** that address the core operational needs of Sunday league teams.

### **Business Value**
- **Streamlined Match Operations**: Reduce administrative overhead for team managers
- **Improved Player Engagement**: Clear visibility of upcoming matches and attendance
- **Better Squad Planning**: Informed decision-making for team selection
- **Enhanced Communication**: Automated notifications and status updates

---

## 🏆 **PRIORITY 2: MATCH MANAGEMENT INTEGRATION**

### **2.1 Feature Overview**

Match Management provides comprehensive tools for creating, scheduling, and managing football matches throughout the season. This feature enables team managers to efficiently organize fixtures while keeping players informed about upcoming games.

### **2.2 User Stories**

#### **As a Team Manager, I want to:**
- Create new matches with all necessary details
- Schedule matches with proper date/time information
- View all upcoming and past matches
- Get detailed match information for planning
- Select the final squad for each match
- Track match results and outcomes

#### **As a Player, I want to:**
- See all upcoming matches in my team
- Get detailed information about each match
- Know when squad selection happens
- Receive notifications about match changes
- View match history and results

### **2.3 Core Commands**

#### **2.3.1 `/creatematch` - Create New Match**
**Permission**: LEADERSHIP  
**Chat Type**: LEADERSHIP  

**Parameters**:
- `opponent` (required): Name of opposing team
- `date` (required): Match date (YYYY-MM-DD)
- `time` (required): Match time (HH:MM)
- `venue` (required): Match location/ground
- `competition` (optional): League/cup name
- `notes` (optional): Additional match details

**Examples**:
```
/creatematch "FC United" 2025-08-15 14:00 "Victoria Park"
/creatematch "Rovers FC" 2025-08-22 15:30 "Community Ground" "League Cup"
```

**Response Format**:
```
🏆 **Match Created Successfully**

**Opponent**: FC United  
**Date**: Saturday, 15th August 2025  
**Time**: 2:00 PM  
**Venue**: Victoria Park  
**Competition**: League Match  
**Match ID**: MATCH_001  

📋 **Next Steps**:
• Players will be notified automatically
• Availability requests will be sent 7 days before
• Squad selection will open 3 days before match
```

#### **2.3.2 `/listmatches` - List All Matches**
**Permission**: PLAYER  
**Chat Type**: MAIN, LEADERSHIP  

**Parameters**:
- `status` (optional): upcoming, past, all
- `limit` (optional): Number of matches to show (default: 10)

**Examples**:
```
/listmatches
/listmatches upcoming
/listmatches past 5
```

**Response Format**:
```
📅 **Upcoming Matches** (Next 10)

1️⃣ **MATCH_001** - vs FC United
   📅 Saturday, 15th August 2025
   🕐 2:00 PM | 🏟️ Victoria Park
   📊 Availability: 8/15 confirmed

2️⃣ **MATCH_002** - vs Rovers FC  
   📅 Saturday, 22nd August 2025
   🕐 3:30 PM | 🏟️ Community Ground
   📊 Availability: 5/15 confirmed

📋 **Quick Actions**:
• /matchdetails MATCH_001 - View full details
• /markattendance MATCH_001 - Mark availability
```

#### **2.3.3 `/matchdetails` - Get Match Details**
**Permission**: PLAYER  
**Chat Type**: MAIN, LEADERSHIP  

**Parameters**:
- `match_id` (required): Match identifier

**Examples**:
```
/matchdetails MATCH_001
```

**Response Format**:
```
🏆 **Match Details: MATCH_001**

**Opponent**: FC United  
**Date**: Saturday, 15th August 2025  
**Time**: 2:00 PM  
**Venue**: Victoria Park  
**Competition**: League Match  
**Status**: Upcoming  

👥 **Squad Status**:
• **Available**: 8 players
• **Unavailable**: 3 players  
• **Pending**: 4 players
• **Selected**: 0 players

📋 **Actions**:
• /markattendance MATCH_001 - Mark availability
• /selectsquad MATCH_001 - Select final squad (Leadership only)
```

#### **2.3.4 `/selectsquad` - Select Match Squad**
**Permission**: LEADERSHIP  
**Chat Type**: LEADERSHIP  

**Parameters**:
- `match_id` (required): Match identifier
- `players` (optional): Space-separated list of player IDs

**Examples**:
```
/selectsquad MATCH_001
/selectsquad MATCH_001 PLAYER_001 PLAYER_002 PLAYER_003
```

**Response Format**:
```
👥 **Squad Selection: MATCH_001**

**Available Players** (8):
1. John Smith (PLAYER_001) - Midfielder
2. Mike Johnson (PLAYER_002) - Defender
3. Tom Wilson (PLAYER_003) - Forward
...

**Selected Squad** (0):
No players selected yet

📋 **Actions**:
• /selectsquad MATCH_001 PLAYER_001 PLAYER_002 - Select players
• /clearsquad MATCH_001 - Clear selection
```

### **2.4 Data Models**

#### **2.4.1 Match Entity**
```python
@dataclass
class Match:
    match_id: str
    team_id: str
    opponent: str
    match_date: datetime
    match_time: time
    venue: str
    competition: str
    status: MatchStatus  # SCHEDULED, AVAILABILITY_OPEN, SQUAD_SELECTION, COMPLETED
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str  # Team member ID
    squad_size: int = 11
    result: Optional[MatchResult] = None
```

#### **2.4.2 Match Status Enum**
```python
class MatchStatus(Enum):
    SCHEDULED = "scheduled"
    AVAILABILITY_OPEN = "availability_open"
    SQUAD_SELECTION = "squad_selection"
    SQUAD_SELECTED = "squad_selected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

#### **2.4.3 Match Result Entity**
```python
@dataclass
class MatchResult:
    match_id: str
    home_score: int
    away_score: int
    scorers: List[str]  # Player IDs
    assists: List[str]  # Player IDs
    notes: Optional[str]
    recorded_by: str  # Team member ID
    recorded_at: datetime
```

### **2.5 Business Rules**

#### **2.5.1 Match Creation Rules**
- Only team managers and administrators can create matches
- Match date must be at least 7 days in the future
- Match time must be between 9:00 AM and 8:00 PM
- Venue must be specified and non-empty
- Match ID is auto-generated using pattern: `MATCH_{SEQUENTIAL_NUMBER}`

#### **2.5.2 Availability Window Rules**
- Availability requests are automatically sent 7 days before match
- Players have 4 days to respond to availability requests
- Squad selection opens 3 days before match
- Squad selection closes 1 day before match

#### **2.5.3 Squad Selection Rules**
- Maximum squad size is 11 players (default)
- Only available players can be selected
- Team managers can modify squad until 1 day before match
- Selected players are automatically notified

---

## 📊 **PRIORITY 3: AVAILABILITY & ATTENDANCE TRACKING**

### **3.1 Feature Overview**

Availability & Attendance Tracking enables players to indicate their availability for upcoming matches and allows team managers to track attendance for completed matches. This feature provides clear visibility of player commitment and helps with squad planning.

### **3.2 User Stories**

#### **As a Player, I want to:**
- Mark my availability for upcoming matches
- Update my availability if circumstances change
- See my availability history
- Get reminders about upcoming matches
- Know when I've been selected for the squad

#### **As a Team Manager, I want to:**
- See availability status for all players
- Track actual attendance at matches
- Get reports on player attendance patterns
- Identify reliable players for squad selection
- Export attendance data for analysis

### **3.3 Core Commands**

#### **3.3.1 `/markattendance` - Mark Match Availability**
**Permission**: PLAYER  
**Chat Type**: MAIN, LEADERSHIP  

**Parameters**:
- `match_id` (required): Match identifier
- `status` (required): available, unavailable, maybe

**Examples**:
```
/markattendance MATCH_001 available
/markattendance MATCH_001 unavailable "Work commitment"
/markattendance MATCH_001 maybe "Will confirm by Thursday"
```

**Response Format**:
```
✅ **Availability Updated**

**Match**: vs FC United (MATCH_001)  
**Date**: Saturday, 15th August 2025  
**Your Status**: ✅ Available  
**Reason**: None provided  

📊 **Team Availability**:
• Available: 8 players
• Unavailable: 3 players  
• Maybe: 2 players
• Pending: 2 players

💡 **Tip**: You can update your availability anytime before squad selection
```

#### **3.3.2 `/attendance` - View Match Attendance**
**Permission**: PLAYER  
**Chat Type**: MAIN, LEADERSHIP  

**Parameters**:
- `match_id` (required): Match identifier

**Examples**:
```
/attendance MATCH_001
```

**Response Format**:
```
📊 **Match Attendance: vs FC United**

**Date**: Saturday, 15th August 2025  
**Status**: Upcoming  

👥 **Availability Status**:
✅ **Available** (8):
• John Smith - Midfielder
• Mike Johnson - Defender
• Tom Wilson - Forward
...

❌ **Unavailable** (3):
• David Brown - "Work commitment"
• Chris Lee - "Family event"
• Alex Green - "Injury"

❓ **Maybe** (2):
• Sam White - "Will confirm by Thursday"
• Rob Black - "Travel plans uncertain"

⏳ **Pending** (2):
• James Red
• Paul Blue
```

#### **3.3.3 `/attendancehistory` - View Attendance History**
**Permission**: PLAYER  
**Chat Type**: MAIN, LEADERSHIP  

**Parameters**:
- `player_id` (optional): Specific player ID
- `limit` (optional): Number of matches to show (default: 10)

**Examples**:
```
/attendancehistory
/attendancehistory PLAYER_001
/attendancehistory 5
```

**Response Format**:
```
📈 **Attendance History**

**Your Record** (Last 10 matches):
✅ vs FC United (15/08/2025) - Available
✅ vs Rovers FC (08/08/2025) - Available  
❌ vs City FC (01/08/2025) - Unavailable (Work)
✅ vs United FC (25/07/2025) - Available
...

📊 **Statistics**:
• **Attendance Rate**: 85% (17/20 matches)
• **Available**: 17 matches
• **Unavailable**: 3 matches
• **Most Common Reason**: Work commitments

🏆 **Reliability Rating**: ⭐⭐⭐⭐⭐ (Excellent)
```

#### **3.3.4 `/markmatchattendance` - Mark Actual Match Attendance**
**Permission**: LEADERSHIP  
**Chat Type**: LEADERSHIP  

**Parameters**:
- `match_id` (required): Match identifier
- `player_id` (required): Player identifier
- `status` (required): attended, absent, late

**Examples**:
```
/markmatchattendance MATCH_001 PLAYER_001 attended
/markmatchattendance MATCH_001 PLAYER_002 absent "No show"
/markmatchattendance MATCH_001 PLAYER_003 late "Arrived 15 mins late"
```

**Response Format**:
```
✅ **Match Attendance Recorded**

**Match**: vs FC United (MATCH_001)  
**Player**: John Smith (PLAYER_001)  
**Status**: ✅ Attended  
**Recorded by**: Sarah Johnson  
**Time**: 15:30  

📊 **Match Summary**:
• Attended: 8 players
• Absent: 2 players
• Late: 1 player
• Pending: 0 players
```

### **3.4 Data Models**

#### **3.4.1 Availability Entity**
```python
@dataclass
class Availability:
    availability_id: str
    match_id: str
    player_id: str
    status: AvailabilityStatus  # AVAILABLE, UNAVAILABLE, MAYBE
    reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    updated_by: str  # Player ID
```

#### **3.4.2 Match Attendance Entity**
```python
@dataclass
class MatchAttendance:
    attendance_id: str
    match_id: str
    player_id: str
    status: AttendanceStatus  # ATTENDED, ABSENT, LATE
    reason: Optional[str]
    recorded_at: datetime
    recorded_by: str  # Team member ID
    arrival_time: Optional[time] = None
```

#### **3.4.3 Status Enums**
```python
class AvailabilityStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAYBE = "maybe"
    PENDING = "pending"

class AttendanceStatus(Enum):
    ATTENDED = "attended"
    ABSENT = "absent"
    LATE = "late"
    NOT_RECORDED = "not_recorded"
```

### **3.5 Business Rules**

#### **3.5.1 Availability Rules**
- Players can mark availability for matches up to 1 day before squad selection
- Players can update their availability status multiple times
- "Maybe" status requires a reason or timeline for confirmation
- Availability is automatically set to "pending" when match is created

#### **3.5.2 Attendance Recording Rules**
- Only team managers can record actual match attendance
- Attendance can only be recorded for completed matches
- Players marked as "unavailable" cannot be marked as "attended"
- Late arrivals should include arrival time and reason

#### **3.5.3 Notification Rules**
- Players receive availability requests 7 days before match
- Players receive reminders 3 days before match if no response
- Selected squad members receive confirmation 2 days before match
- Match day reminders sent 2 hours before kickoff

---

## 🔧 **TECHNICAL IMPLEMENTATION**

### **4.1 Database Schema**

#### **4.1.1 Match Collections**
```
kickai_{team_id}_matches
├── match_id (string, primary key)
├── team_id (string)
├── opponent (string)
├── match_date (timestamp)
├── match_time (string)
├── venue (string)
├── competition (string)
├── status (string)
├── notes (string, optional)
├── squad_size (integer)
├── created_at (timestamp)
├── updated_at (timestamp)
├── created_by (string)
└── result (object, optional)
    ├── home_score (integer)
    ├── away_score (integer)
    ├── scorers (array)
    ├── assists (array)
    ├── notes (string)
    ├── recorded_by (string)
    └── recorded_at (timestamp)
```

#### **4.1.2 Availability Collections**
```
kickai_{team_id}_match_availability
├── availability_id (string, primary key)
├── match_id (string)
├── player_id (string)
├── status (string)
├── reason (string, optional)
├── created_at (timestamp)
├── updated_at (timestamp)
└── updated_by (string)
```

#### **4.1.3 Attendance Collections**
```
kickai_{team_id}_match_attendance
├── attendance_id (string, primary key)
├── match_id (string)
├── player_id (string)
├── status (string)
├── reason (string, optional)
├── recorded_at (timestamp)
├── recorded_by (string)
└── arrival_time (string, optional)
```

### **4.2 Service Architecture**

#### **4.2.1 Match Service**
```python
class MatchService:
    async def create_match(self, match_data: CreateMatchRequest) -> Match
    async def get_match(self, match_id: str) -> Match
    async def list_matches(self, filters: MatchFilters) -> List[Match]
    async def update_match(self, match_id: str, updates: MatchUpdates) -> Match
    async def delete_match(self, match_id: str) -> bool
    async def select_squad(self, match_id: str, player_ids: List[str]) -> SquadSelection
    async def record_result(self, match_id: str, result: MatchResult) -> Match
```

#### **4.2.2 Availability Service**
```python
class AvailabilityService:
    async def mark_availability(self, availability_data: MarkAvailabilityRequest) -> Availability
    async def get_availability(self, match_id: str, player_id: str) -> Availability
    async def list_match_availability(self, match_id: str) -> List[Availability]
    async def get_player_history(self, player_id: str, limit: int) -> List[Availability]
    async def send_availability_reminders(self, match_id: str) -> bool
```

#### **4.2.3 Attendance Service**
```python
class AttendanceService:
    async def record_attendance(self, attendance_data: RecordAttendanceRequest) -> MatchAttendance
    async def get_match_attendance(self, match_id: str) -> List[MatchAttendance]
    async def get_player_attendance_history(self, player_id: str, limit: int) -> List[MatchAttendance]
    async def calculate_attendance_stats(self, player_id: str) -> AttendanceStats
```

### **4.3 CrewAI Integration**

#### **4.3.1 Match Management Agent**
```python
class MatchManagementAgent:
    role = "Match Manager"
    goal = "Efficiently manage match scheduling, squad selection, and match operations"
    
    tools = [
        CreateMatchTool(),
        ListMatchesTool(),
        GetMatchDetailsTool(),
        SelectSquadTool(),
        RecordMatchResultTool()
    ]
```

#### **4.3.2 Availability Management Agent**
```python
class AvailabilityManagementAgent:
    role = "Availability Coordinator"
    goal = "Track player availability and manage attendance for optimal squad planning"
    
    tools = [
        MarkAvailabilityTool(),
        GetAvailabilityTool(),
        SendRemindersTool(),
        RecordAttendanceTool(),
        GenerateReportsTool()
    ]
```

---

## 📋 **IMPLEMENTATION PHASES**

### **Phase 1: Core Match Management (Week 1-2)**
1. **Database Schema**: Create match and availability collections
2. **Domain Layer**: Implement Match and Availability entities
3. **Repository Layer**: Create Firestore repositories
4. **Service Layer**: Implement core match and availability services
5. **Basic Commands**: `/creatematch`, `/listmatches`, `/markattendance`

### **Phase 2: Advanced Features (Week 3-4)**
1. **Squad Selection**: Implement squad selection logic
2. **Attendance Tracking**: Add match day attendance recording
3. **Notifications**: Implement automated reminders
4. **Advanced Commands**: `/selectsquad`, `/markmatchattendance`, `/attendancehistory`

### **Phase 3: Integration & Testing (Week 5-6)**
1. **CrewAI Integration**: Create specialized agents
2. **Command Integration**: Integrate with existing command system
3. **End-to-End Testing**: Test complete workflows
4. **Performance Optimization**: Optimize database queries

---

## 🎯 **SUCCESS METRICS**

### **4.1 User Engagement**
- **Match Creation**: 90% of teams create matches within 1 week of feature launch
- **Availability Response**: 80% of players respond to availability requests within 48 hours
- **Command Usage**: 70% of active users use match management commands weekly

### **4.2 Operational Efficiency**
- **Squad Planning Time**: Reduce squad selection time by 50%
- **Communication Overhead**: Reduce match-related messages by 60%
- **Attendance Accuracy**: Achieve 95% accurate attendance tracking

### **4.3 System Performance**
- **Response Time**: All match commands respond within 2 seconds
- **Data Consistency**: 99.9% data consistency across collections
- **Error Rate**: Less than 1% error rate for all match operations

---

## 🚀 **FUTURE ENHANCEMENTS**

### **4.1 Advanced Analytics**
- Player performance tracking
- Attendance pattern analysis
- Squad optimization recommendations

### **4.2 Integration Features**
- Calendar integration (Google Calendar, Outlook)
- Weather integration for match planning
- Location services for venue directions

### **4.3 Mobile Optimization**
- Push notifications for match updates
- Offline availability marking
- Quick squad selection interface

---

## 📞 **SUPPORT & MAINTENANCE**

### **4.1 Monitoring**
- Track command usage patterns
- Monitor database performance
- Alert on system errors

### **4.2 User Support**
- In-app help system for new features
- Video tutorials for complex workflows
- Feedback collection for continuous improvement

### **4.3 Maintenance**
- Regular database optimization
- Performance monitoring and tuning
- Feature updates based on user feedback

---

**Document End**  
*This specification serves as the authoritative guide for implementing Match Management and Attendance Tracking features in the KICKAI system.*