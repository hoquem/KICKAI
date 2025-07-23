# Team Member vs Player Entity Separation Specification

## 🎯 **Overview**

This specification defines how to properly separate **Team Members** (administrators/managers) and **Players** (football players) as distinct entities in the KICKAI system. A person can be both a Team Member and a Player, but they should be represented as separate entities with clear relationships.

## 🏗️ **Entity Architecture**

### **Core Principle**
- **TeamMember**: Represents administrative/management roles within a team
- **Player**: Represents football-specific data and capabilities
- **Relationship**: A person can have both a TeamMember record and a Player record, linked by `user_id`

## 📊 **Entity Definitions**

### 1. **TeamMember Entity**

```python
@dataclass
class TeamMember:
    """Represents administrative/management roles within a team."""
    
    # Core identification
    id: Optional[str] = None
    user_id: str = ""  # Links to Player.user_id if person is also a player
    team_id: str = ""
    
    # Personal information
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    
    # Telegram integration
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    
    # Administrative roles (NO "player" role)
    roles: List[str] = field(default_factory=list)  # ["admin", "manager", "captain", "vice_captain"]
    permissions: List[str] = field(default_factory=list)  # ["read", "write", "admin", "approve_players"]
    chat_access: Dict[str, bool] = field(default_factory=dict)  # {"main_chat": True, "leadership_chat": True}
    
    # Timestamps
    created_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Metadata
    source: Optional[str] = None  # "telegram_sync", "manual", "import"
    sync_version: Optional[str] = None
```

**Valid Roles**: `["admin", "manager", "captain", "vice_captain", "coach", "secretary"]`
**❌ NO "player" role** - Players are handled by the Player entity

### 2. **Player Entity**

```python
@dataclass
class Player:
    """Represents football-specific data and capabilities."""
    
    # Core identification
    id: str
    user_id: str = ""  # Links to TeamMember.user_id if person is also a team member
    team_id: str = ""
    
    # Personal information
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    date_of_birth: Optional[str] = None
    
    # Football-specific data
    position: str = ""  # "goalkeeper", "defender", "midfielder", "forward", "utility"
    jersey_number: Optional[str] = None
    preferred_foot: Optional[str] = None  # "left", "right", "both"
    
    # Medical and safety
    medical_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    # Status and approval
    status: str = "pending"  # "pending", "approved", "rejected", "active", "inactive", "injured", "suspended"
    admin_approved: bool = False
    admin_approved_at: Optional[datetime] = None
    admin_approved_by: Optional[str] = None
    
    # FA registration
    fa_registered: bool = False
    fa_registration_number: Optional[str] = None
    
    # Telegram integration
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    # Metadata
    source: Optional[str] = None  # "registration", "import", "manual"
    sync_version: Optional[str] = None
```

## 🗄️ **Firestore Collection Structure**

### **Team-Specific Collections (Recommended)**
```
kickai_{team_id}_team_members  # Administrative roles
kickai_{team_id}_players       # Football players
kickai_{team_id}_matches       # Team matches
kickai_{team_id}_attendance    # Match attendance
```

### **Global Collections (For system-wide data)**
```
kickai_teams                   # Team configurations
```

### **Collection Naming Functions**
```python
def get_team_members_collection(team_id: str) -> str:
    """Get team members collection name for a specific team."""
    return f"kickai_{team_id}_team_members"

def get_team_players_collection(team_id: str) -> str:
    """Get players collection name for a specific team."""
    return f"kickai_{team_id}_players"

def get_team_matches_collection(team_id: str) -> str:
    """Get matches collection name for a specific team."""
    return f"kickai_{team_id}_matches"
```

## 🔗 **Entity Relationships**

### **Relationship Model**
```
Person (Real World)
├── TeamMember Record (Administrative roles)
│   ├── user_id: "user_123"
│   ├── roles: ["admin", "captain"]
│   └── permissions: ["read", "write", "admin"]
│
└── Player Record (Football data)
    ├── user_id: "user_123"  # Same user_id for linking
    ├── position: "midfielder"
    ├── jersey_number: "10"
    └── status: "active"
```

### **Linking Strategy**
- **Primary Key**: `user_id` (unique identifier for a person)
- **TeamMember.user_id** = **Player.user_id** when same person
- **Query Strategy**: Use `user_id` to find related records across collections

## 🛠️ **Service Layer Design**

### 1. **TeamMemberService**
```python
class TeamMemberService:
    """Handles administrative team member operations."""
    
    async def create_team_member(self, team_id: str, user_id: str, roles: List[str], **kwargs) -> TeamMember:
        """Create a new team member (administrative role)."""
        
    async def get_team_member_by_user_id(self, user_id: str, team_id: str) -> Optional[TeamMember]:
        """Get team member by user_id."""
        
    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get all team members with a specific role."""
        
    async def update_team_member_roles(self, user_id: str, team_id: str, roles: List[str]) -> bool:
        """Update team member roles."""
```

### 2. **PlayerService**
```python
class PlayerService:
    """Handles football player operations."""
    
    async def create_player(self, team_id: str, user_id: str, position: str, **kwargs) -> Player:
        """Create a new player."""
        
    async def get_player_by_user_id(self, user_id: str, team_id: str) -> Optional[Player]:
        """Get player by user_id."""
        
    async def approve_player(self, user_id: str, team_id: str, approved_by: str) -> bool:
        """Approve a player for matches."""
        
    async def get_players_by_position(self, team_id: str, position: str) -> List[Player]:
        """Get all players in a specific position."""
```

### 3. **PersonService** (New - Coordinates both entities)
```python
class PersonService:
    """Coordinates operations involving both TeamMember and Player entities."""
    
    async def register_person_as_both(self, team_id: str, user_id: str, 
                                    team_member_data: dict, player_data: dict) -> tuple[TeamMember, Player]:
        """Register a person as both team member and player."""
        
    async def get_person_complete_profile(self, user_id: str, team_id: str) -> dict:
        """Get complete profile (both team member and player data)."""
        
    async def update_person_data(self, user_id: str, team_id: str, 
                               team_member_updates: dict, player_updates: dict) -> bool:
        """Update both team member and player data."""
        
    async def is_person_team_member(self, user_id: str, team_id: str) -> bool:
        """Check if person is a team member."""
        
    async def is_person_player(self, user_id: str, team_id: str) -> bool:
        """Check if person is a player."""
```

## 🎯 **Tool Specifications**

### 1. **Team Member Management Tools**
```python
@tool("create_team_member")
def create_team_member(name: str, phone: str, roles: List[str], team_id: str, user_id: str = None) -> str:
    """Create a new team member (administrative role)."""
    
@tool("update_team_member_roles")
def update_team_member_roles(user_id: str, team_id: str, roles: List[str]) -> str:
    """Update team member roles."""
    
@tool("get_team_members")
def get_team_members(team_id: str, role: Optional[str] = None) -> str:
    """Get team members, optionally filtered by role."""
```

### 2. **Player Management Tools**
```python
@tool("register_player")
def register_player(name: str, phone: str, position: str, team_id: str, user_id: str = None) -> str:
    """Register a new football player."""
    
@tool("approve_player")
def approve_player(user_id: str, team_id: str, approved_by: str) -> str:
    """Approve a player for matches."""
    
@tool("get_players")
def get_players(team_id: str, position: Optional[str] = None, status: Optional[str] = None) -> str:
    """Get players, optionally filtered by position or status."""
```

### 3. **Person Management Tools**
```python
@tool("register_person_complete")
def register_person_complete(name: str, phone: str, team_id: str, 
                           team_member_roles: List[str], player_position: str, user_id: str = None) -> str:
    """Register a person as both team member and player."""
    
@tool("get_person_profile")
def get_person_profile(user_id: str, team_id: str) -> str:
    """Get complete person profile (both team member and player data)."""
```

## 🔄 **Migration Strategy**

### **Phase 1: Data Structure Updates**
1. Update TeamMember entity to remove "player" role
2. Update Player entity with new fields
3. Update collection naming functions
4. Update service layer interfaces

### **Phase 2: Data Migration**
1. Create migration script to separate existing data
2. Move team member data to team-specific collections
3. Create proper Player records for existing players
4. Link TeamMember and Player records by user_id

### **Phase 3: Code Updates**
1. Update all tools to use new service methods
2. Update command handlers
3. Update agent configurations
4. Update documentation

### **Phase 4: Testing and Validation**
1. Test entity separation
2. Validate data consistency
3. Test relationship queries
4. Performance testing

## 📋 **Validation Rules**

### **TeamMember Validation**
- Must have at least one administrative role
- Cannot have "player" role (handled by Player entity)
- user_id must be unique within team
- Required fields: name, phone, team_id, roles

### **Player Validation**
- Must have valid position
- user_id must be unique within team
- Required fields: name, phone, position, team_id
- Status must be valid enum value

### **Relationship Validation**
- If person has both TeamMember and Player records, user_id must match
- TeamMember and Player must have same team_id
- Name and phone should be consistent between records

## 🎯 **Benefits of This Design**

1. **Clear Separation**: Administrative roles vs football data
2. **Flexibility**: Person can be team member, player, or both
3. **Scalability**: Team-specific collections for better performance
4. **Maintainability**: Clear service boundaries
5. **Data Integrity**: Proper validation and relationships
6. **Future-Proof**: Easy to extend with new roles or player attributes

---

**Specification Version**: 1.0  
**Date**: December 2024  
**Status**: Ready for Implementation 