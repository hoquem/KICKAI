# CLEAN ARCHITECTURE VIOLATIONS REPORT
## Tools Calling Services Directly Instead of Domain Functions

**Date:** January 2025  
**Status:** CRITICAL - Requires Immediate Fix  
**Impact:** Breaks Clean Architecture Principles

---

## 🚨 **CRITICAL VIOLATIONS FOUND**

### **1. Communication Tools** (`kickai/features/communication/application/tools/communication_tools.py`)

**❌ VIOLATION:** Tools calling services directly via string-based service access

```python
# ❌ WRONG - String-based service access
communication_service = container.get_service("CommunicationService")
```

**Files Affected:**
- Line 55: `send_message` tool
- Line 117: `send_announcement` tool  
- Line 187: `send_poll` tool

**Clean Architecture Violation:**
- Application layer tools should NOT call services directly
- Should use domain functions instead
- String-based service access is not type-safe

**Expected Pattern:**
```python
# ✅ CORRECT - Domain function delegation
from kickai.features.communication.domain.services.communication_service import CommunicationService

# Get domain service and delegate to domain function
communication_service = CommunicationService()
result = await communication_service.send_message(message, chat_type, team_id)
```

---

### **2. User Tools** (`kickai/features/shared/application/tools/user_tools.py`)

**❌ VIOLATION:** Tools calling services directly via string-based service access

```python
# ❌ WRONG - String-based service access
player_service = container.get_service("PlayerService")
team_service = container.get_service("TeamService")
```

**Files Affected:**
- Line 75: `get_user_status` tool
- Line 76: `get_user_status` tool

**Clean Architecture Violation:**
- Application layer tools should NOT call services directly
- Should use domain functions instead
- String-based service access is not type-safe

**Expected Pattern:**
```python
# ✅ CORRECT - Domain function delegation
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService

# Get domain services and delegate to domain functions
player_service = PlayerService()
team_service = TeamService()
user_status = await player_service.get_user_status(telegram_id, team_id)
```

---

### **3. Player Tools** (`kickai/features/player_registration/application/tools/player_tools.py`)

**❌ VIOLATION:** Tools calling services directly via interface-based service access

```python
# ❌ WRONG - Interface-based service access (still violates Clean Architecture)
player_service = container.get_service(IPlayerService)
team_member_service = container.get_service(ITeamMemberService)
```

**Files Affected:**
- Line 49: `approve_player` tool
- Line 131: `get_my_status` tool
- Line 142: `get_my_status` tool
- Line 185: `get_player_status` tool
- Line 259: `get_active_players` tool
- Line 340: `register_player` tool
- Line 405: `add_player` tool
- Line 406: `add_player` tool

**Clean Architecture Violation:**
- Application layer tools should NOT call services directly
- Should use domain functions instead
- Even interface-based access violates the principle

**Expected Pattern:**
```python
# ✅ CORRECT - Domain function delegation
from kickai.features.player_registration.domain.services.player_service import PlayerService

# Get domain service and delegate to domain function
player_service = PlayerService()
result = await player_service.approve_player(player_id, team_id)
```

---

### **4. Match Tools** (`kickai/features/match_management/application/tools/match_tools.py`)

**❌ VIOLATION:** Tools calling services directly via interface-based service access

```python
# ❌ WRONG - Interface-based service access (still violates Clean Architecture)
match_service = container.get_service(IMatchService)
```

**Files Affected:**
- Line 44: `list_matches` tool
- Line 133: `create_match` tool
- Line 209: `get_match_details` tool
- Line 308: `record_match_result` tool
- Line 384: `get_upcoming_matches` tool
- Line 463: `get_match_attendance` tool

**Clean Architecture Violation:**
- Application layer tools should NOT call services directly
- Should use domain functions instead
- Even interface-based access violates the principle

**Expected Pattern:**
```python
# ✅ CORRECT - Domain function delegation
from kickai.features.match_management.domain.services.match_service import MatchService

# Get domain service and delegate to domain function
match_service = MatchService()
matches = await match_service.get_upcoming_matches(team_id, limit)
```

---

### **5. Team Administration Tools** (`kickai/features/team_administration/application/tools/team_administration_tools.py`)

**❌ VIOLATION:** Tools calling services directly via interface-based service access

```python
# ❌ WRONG - Interface-based service access (still violates Clean Architecture)
management_service = container.get_service(TeamMemberManagementService)
team_service = container.get_service(TeamService)
```

**Files Affected:**
- Line 103: `team_member_registration` tool
- Line 173: `get_team_members` tool
- Line 241: `get_my_team_member_status` tool
- Line 356: `create_team` tool

**Clean Architecture Violation:**
- Application layer tools should NOT call services directly
- Should use domain functions instead
- Even interface-based access violates the principle

**Expected Pattern:**
```python
# ✅ CORRECT - Domain function delegation
from kickai.features.team_administration.domain.services.team_member_management_service import TeamMemberManagementService

# Get domain service and delegate to domain function
management_service = TeamMemberManagementService()
result = await management_service.register_team_member(telegram_id, team_id, name, role)
```

---

## 🎯 **CLEAN ARCHITECTURE PRINCIPLES**

### **Correct Pattern for Application Layer Tools:**

```python
@tool("example_tool")
async def example_tool(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Application layer tool - framework concerns only.
    """
    try:
        # 1. Input validation (framework concern)
        if not telegram_id or not team_id:
            return create_json_response(ResponseStatus.ERROR, message="Missing parameters")
        
        # 2. Get domain service (pure business logic)
        domain_service = DomainService()
        
        # 3. Delegate to domain function (pure business logic)
        result = await domain_service.perform_business_operation(telegram_id, team_id)
        
        # 4. Format response (framework concern)
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"Error in example_tool: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Operation failed")
```

### **Domain Service Pattern:**

```python
class DomainService:
    """Pure business logic - no framework dependencies."""
    
    async def perform_business_operation(self, telegram_id: int, team_id: str) -> dict:
        """Pure business logic implementation."""
        # Business logic here - no framework concerns
        return {"result": "success"}
```

---

## 🔧 **FIX PRIORITY**

### **HIGH PRIORITY (Immediate Fix Required):**
1. **Communication Tools** - String-based service access
2. **User Tools** - String-based service access
3. **Player Tools** - Interface-based service access
4. **Match Tools** - Interface-based service access
5. **Team Administration Tools** - Interface-based service access

### **MEDIUM PRIORITY:**
- Domain service instantiation patterns
- Error handling consistency
- Response formatting standardization

---

## 📋 **FIX PLAN**

### **Phase 1: Immediate Fixes**
1. **Replace string-based service access** with domain service instantiation
2. **Replace interface-based service access** with domain service instantiation
3. **Ensure all tools follow the correct pattern**

### **Phase 2: Domain Service Refactoring**
1. **Create pure domain services** without framework dependencies
2. **Move business logic** from application layer to domain layer
3. **Ensure domain services are framework-agnostic**

### **Phase 3: Validation**
1. **Test all tools** to ensure they work correctly
2. **Verify Clean Architecture compliance**
3. **Update documentation**

---

## 🚨 **IMPACT ASSESSMENT**

### **Current Issues:**
- **Clean Architecture Violation**: Application layer calling services directly
- **Type Safety**: String-based service access is not type-safe
- **Testability**: Hard to test due to service dependencies
- **Maintainability**: Tight coupling between layers

### **Benefits After Fix:**
- **Clean Architecture Compliance**: Proper layer separation
- **Type Safety**: Domain service instantiation is type-safe
- **Testability**: Easy to test with pure domain services
- **Maintainability**: Loose coupling between layers

---

## ✅ **VALIDATION CRITERIA**

After fixes, all tools should:
1. ✅ **NOT call services directly** via container.get_service()
2. ✅ **Use domain service instantiation** for business logic
3. ✅ **Delegate to domain functions** for all business operations
4. ✅ **Handle only framework concerns** in application layer
5. ✅ **Be type-safe** with proper imports

---

*This report identifies critical Clean Architecture violations that must be fixed immediately to maintain proper separation of concerns and layer independence.*
