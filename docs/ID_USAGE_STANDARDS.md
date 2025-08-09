# ID Usage Standards for KICKAI

## 🎯 Overview

This document clarifies the explicit and correct usage of different ID types in the KICKAI system to eliminate confusion and ensure consistency.

## 📋 ID Type Definitions

### **1. `telegram_id` (integer)**
- **Purpose**: Links users to their Telegram accounts
- **Format**: Native Telegram integer ID (e.g., `123456789`)
- **Usage**: User authentication, linking, message routing
- **Storage**: Integer field in database
- **Example**: `telegram_id: 1234567890`

### **2. `player_id` (string)**  
- **Purpose**: Unique player identification within a team
- **Format**: `M` + 3-digit number + initials (e.g., `M001MH`)
- **Usage**: Player management, squad selection, match records
- **Storage**: String field in database, used as document ID for players
- **Example**: `player_id: "M001MH"` (Mahmudul Hoque, first player)

### **3. `member_id` (string)**
- **Purpose**: Unique team member identification within a team  
- **Format**: `M` + 3-digit number + initials (e.g., `M001MH`)
- **Usage**: Team administration, permissions, roles
- **Storage**: String field in database, used as document ID for team members
- **Example**: `member_id: "M001MH"` (Mahmudul Hoque, first member)

### **4. `team_id` (string)**
- **Purpose**: Unique team identification  
- **Format**: 2-4 letter team code (e.g., `KA`, `MU`, `LIVE`)
- **Usage**: Team management, context setting, permissions
- **Storage**: String field in database, used as document ID for teams
- **Example**: `team_id: "KA"` (Kick AI)

### **5. `user_id` (string) - DEPRECATED**
- **Status**: LEGACY - Being phased out
- **Purpose**: Previously used for general user identification
- **Migration**: Replace with explicit `telegram_id`, `player_id`, or `member_id`
- **Current Usage**: Only for backward compatibility, avoid in new code

## 🔗 Relationship Mapping

### **Person → Multiple Roles**
A single person can have multiple roles, linked by `telegram_id`:

```python
# Same person in different roles
telegram_id: 1234567890

# As a player
player_id: "M001MH"
team_id: "KA" 

# As a team member  
member_id: "M001MH"
team_id: "KA"
```

### **Database Document Structure**

```python
# Player Document (ID: M001MH)
{
    "player_id": "M001MH",          # Primary identifier
    "telegram_id": 1234567890,      # Linking field
    "team_id": "KA",                # Team context
    "name": "Mahmudul Hoque",
    "position": "midfielder",
    "status": "active",
    # Legacy field (deprecated)
    "user_id": "12345_hash"         # Don't use in new code
}

# Team Member Document (ID: M001MH)  
{
    "member_id": "M001MH",          # Primary identifier
    "telegram_id": 1234567890,      # Linking field  
    "team_id": "KA",                # Team context
    "name": "Mahmudul Hoque",
    "role": "admin",
    "is_admin": true,
    # Legacy field (deprecated)
    "user_id": "12345_hash"         # Don't use in new code
}
```

## 🛠️ API & Service Patterns

### **✅ CORRECT Usage**

```python
# Service method signatures
async def get_player_by_telegram_id(telegram_id: int, team_id: str) -> Optional[Player]
async def get_player_by_player_id(player_id: str, team_id: str) -> Optional[Player]
async def get_team_member_by_member_id(member_id: str, team_id: str) -> Optional[TeamMember]

# Tool signatures  
@tool("approve_player")
def approve_player(team_id: str, player_id: str) -> str:

@tool("get_user_status") 
def get_user_status(telegram_id: str, team_id: str) -> str:

# Database queries
players_collection.document(player_id)  # Use player_id as document ID
members_collection.document(member_id)  # Use member_id as document ID
```

### **❌ INCORRECT Usage (Avoid)**

```python
# Confusing parameter names
def approve_player(user_id: str, player_id: str) -> str:  # Which ID to use?

# Wrong ID types
def get_player(telegram_id: str) -> Player:  # Should be int, not str

# Mixed ID usage
def update_player(user_id: str, telegram_id: int) -> Player:  # Use one or the other
```

## 🔄 Migration Guidelines

### **From `user_id` to Explicit IDs**

1. **Identify Purpose**: What is the `user_id` actually used for?
   - Telegram linking → Use `telegram_id: int`
   - Player identification → Use `player_id: str`
   - Member identification → Use `member_id: str`

2. **Update Method Signatures**:
   ```python
   # Before (confusing)
   def get_user_status(user_id: str) -> str:
   
   # After (clear)  
   def get_user_status(telegram_id: int) -> str:
   ```

3. **Update Database Queries**:
   ```python
   # Before (ambiguous)
   collection.where("user_id", "==", user_id)
   
   # After (explicit)
   collection.where("telegram_id", "==", telegram_id)
   collection.where("player_id", "==", player_id)
   ```

### **Service Layer Updates**

```python
class PlayerService:
    # ✅ Clear, explicit method names
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[Player]:
        """Get player by their Telegram ID (for linking)"""
        
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:  
        """Get player by their player ID (for identification)"""
        
    async def approve_player(self, player_id: str, team_id: str) -> Player:
        """Approve player using their player ID"""
```

## 🧪 Testing Patterns

```python
def test_player_identification():
    # Clear test data
    telegram_id = 1234567890  # Integer
    player_id = "M001MH"      # String  
    team_id = "KA"            # String
    
    # Clear assertions
    player = get_player_by_telegram_id(telegram_id, team_id)
    assert player.telegram_id == telegram_id
    assert player.player_id == player_id
    assert player.team_id == team_id
```

## 📊 Database Schema

### **Players Collection** (`kickai_players`)
```
Document ID: {player_id}  // e.g., "M001MH"
{
    "player_id": "M001MH",           // Primary key
    "telegram_id": 1234567890,       // Linking key (integer)
    "team_id": "KA",                 // Context key
    "name": "Mahmudul Hoque",
    "position": "midfielder"
}
```

### **Team Members Collection** (`kickai_team_members`)
```
Document ID: {member_id}  // e.g., "M001MH"  
{
    "member_id": "M001MH",           // Primary key
    "telegram_id": 1234567890,       // Linking key (integer)
    "team_id": "KA",                 // Context key
    "name": "Mahmudul Hoque",
    "role": "admin"
}
```

## ✅ Validation Checklist

When working with IDs, verify:

- [ ] **Parameter names** are explicit (`telegram_id`, `player_id`, `member_id`)
- [ ] **Type annotations** are correct (`int` for telegram_id, `str` for others)
- [ ] **Database queries** use appropriate ID types
- [ ] **No confusing `user_id`** parameters in new code
- [ ] **Documentation** clearly states which ID is used for what purpose
- [ ] **Error messages** specify which ID type caused the error

## 🎯 Key Benefits

1. **Crystal Clear Purpose**: Each ID type has a specific, documented purpose
2. **No Confusion**: Explicit naming eliminates guesswork
3. **Type Safety**: Proper type annotations catch errors early
4. **Maintainability**: Clear code is easier to maintain and debug
5. **Scalability**: Explicit IDs support growing team sizes and complexity

---

**Remember**: When in doubt, ask "What is this ID actually used for?" and choose the most explicit, descriptive name.