# User ID Linking Rules Specification

## 🎯 **Overview**

This document establishes the rules for creating `user_id` values that link **Team Members** and **Players** when a user has both roles in the KICKAI system. The `user_id` serves as the primary key to establish relationships between different entity types for the same person.

## 🔗 **Core Linking Principle**

- **Single Person, Multiple Roles**: A person can be both a Team Member (administrator/manager) and a Player (football player)
- **Shared Identity**: Both entities share the same `user_id` to establish the relationship
- **Independent Records**: Each role has its own separate record with role-specific data
- **Optional Relationship**: A person can have only one role (just Team Member or just Player)

## 📋 **User ID Generation Rules**

### **Rule 1: Telegram-Based User ID**
```
user_id = f"user_{telegram_id}"
```

**Examples:**
- Telegram ID: `8148917292` → `user_id: "user_8148917292"`
- Telegram ID: `123456789` → `user_id: "user_123456789"`

### **Rule 2: Consistency Across All Entities**
- **TeamMember.user_id**: `"user_{telegram_id}"`
- **Player.user_id**: `"user_{telegram_id}"`
- **Any future entity types**: `"user_{telegram_id}"`

### **Rule 3: Telegram ID as Primary Identifier**
- **Source**: Always use the Telegram user ID as the base
- **Uniqueness**: Telegram IDs are globally unique per user
- **Persistence**: Telegram IDs don't change for a user
- **Availability**: Available in all Telegram interactions

## 🔄 **Entity Relationship Examples**

### **Example 1: User with Both Roles**
```json
// Team Member Record
{
  "user_id": "user_8148917292",
  "team_id": "KTI",
  "telegram_id": "8148917292",
  "role": "Club Administrator",
  "is_admin": true,
  "phone_number": "+447961103217",
  "email": "admin@kickai.com"
}

// Player Record (same person)
{
  "user_id": "user_8148917292",
  "team_id": "KTI",
  "telegram_id": "8148917292",
  "position": "Midfielder",
  "player_id": "KTI_MH_001",
  "preferred_foot": "Right",
  "jersey_number": "10"
}
```

### **Example 2: User with Only Team Member Role**
```json
// Team Member Record
{
  "user_id": "user_123456789",
  "team_id": "KTI",
  "telegram_id": "123456789",
  "role": "Team Manager",
  "is_admin": true,
  "phone_number": "+447123456789"
}

// No Player record exists for this user_id
```

### **Example 3: User with Only Player Role**
```json
// Player Record
{
  "user_id": "user_987654321",
  "team_id": "KTI",
  "telegram_id": "987654321",
  "position": "Forward",
  "player_id": "KTI_FW_002",
  "preferred_foot": "Left"
}

// No Team Member record exists for this user_id
```

## 🛠️ **Implementation Guidelines**

### **1. User ID Generation**
```python
def generate_user_id(telegram_id: int) -> str:
    """Generate consistent user_id from Telegram ID."""
    return f"user_{telegram_id}"
```

### **2. Entity Creation**
```python
# When creating a Team Member
team_member_data = {
    "user_id": generate_user_id(telegram_id),
    "telegram_id": str(telegram_id),
    # ... other team member fields
}

# When creating a Player
player_data = {
    "user_id": generate_user_id(telegram_id),
    "telegram_id": str(telegram_id),
    # ... other player fields
}
```

### **3. Relationship Queries**
```python
# Find all entities for a user
def get_user_entities(user_id: str):
    team_members = query_team_members(user_id=user_id)
    players = query_players(user_id=user_id)
    return {
        "team_members": team_members,
        "players": players,
        "has_both_roles": len(team_members) > 0 and len(players) > 0
    }
```

## 🔍 **Validation Rules**

### **1. Uniqueness Validation**
- Each `user_id` must be unique within its entity type
- Same `user_id` can exist across different entity types (Team Member + Player)

### **2. Telegram ID Consistency**
- `user_id` must always be derived from `telegram_id`
- `telegram_id` must be consistent across all entities for the same user

### **3. Team Context**
- Both Team Member and Player records must have the same `team_id`
- A user cannot have different team associations across roles

## 📊 **Database Schema Impact**

### **Team Member Collection**
```json
{
  "user_id": "user_8148917292",  // Primary linking key
  "team_id": "KTI",
  "telegram_id": "8148917292",   // Source identifier
  // ... team member specific fields
}
```

### **Player Collection**
```json
{
  "user_id": "user_8148917292",  // Primary linking key
  "team_id": "KTI",
  "telegram_id": "8148917292",   // Source identifier
  // ... player specific fields
}
```

## 🎯 **Benefits of This Approach**

1. **Clear Relationships**: Easy to identify when a person has multiple roles
2. **Consistent Identity**: Same user_id across all entity types
3. **Flexible Roles**: Users can have any combination of roles
4. **Simple Queries**: Easy to find all entities for a user
5. **Future-Proof**: Can extend to additional entity types
6. **Telegram Integration**: Leverages existing Telegram user identification

## ⚠️ **Important Considerations**

1. **Telegram Dependency**: User ID generation depends on Telegram ID availability
2. **Migration Required**: Existing data may need user_id updates
3. **Validation**: Ensure telegram_id consistency across all entities
4. **Error Handling**: Handle cases where telegram_id is not available

## 🔄 **Migration Strategy**

1. **Audit Existing Data**: Identify all existing records without proper user_id
2. **Generate User IDs**: Apply the rule to all existing records
3. **Validate Relationships**: Ensure consistency across entity types
4. **Update Queries**: Modify all queries to use user_id for linking
5. **Test Relationships**: Verify that linked entities are properly connected 