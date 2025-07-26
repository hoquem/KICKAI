# 🚫 Team ID Policy: NO DEFAULTS ALLOWED

## **🎯 Core Principle**

**Team IDs must NEVER have defaults, fallbacks, or hardcoded values. They must ALWAYS come from Firestore team configuration.**

## **❌ WHAT IS FORBIDDEN**

### **1. Environment Variable Defaults**
```python
# ❌ WRONG - Never do this
team_id = os.getenv('TEAM_ID', 'KTI')  # Hardcoded fallback
team_id = os.getenv('TEAM_ID', 'KAI')  # Hardcoded fallback
```

### **2. Configuration Defaults**
```python
# ❌ WRONG - Never do this
default_team_id: str = Field(default="KAI")  # Hardcoded default
```

### **3. Hardcoded Values**
```python
# ❌ WRONG - Never do this
team_id = "KTI"  # Hardcoded value
team_id = "KAI"  # Hardcoded value
```

### **4. Optional Parameters with Fallbacks**
```python
# ❌ WRONG - Never do this
def some_function(team_id: str | None = None) -> str:
    if not team_id:
        team_id = "KTI"  # Fallback to hardcoded value
```

## **✅ WHAT IS REQUIRED**

### **1. Firestore Team Configuration**
```python
# ✅ CORRECT - Get team ID from Firestore
from kickai.features.team_administration.domain.services.team_service import TeamService

team_service = container.get_service(TeamService)
team = await team_service.get_team(team_id=actual_team_id)
```

### **2. Required Parameters**
```python
# ✅ CORRECT - Make team_id required
def some_function(team_id: str) -> str:
    # team_id is required, no fallbacks
    pass
```

### **3. Execution Context**
```python
# ✅ CORRECT - Get team_id from execution context
team_id = execution_context.get('team_id')
if not team_id:
    raise ValueError("team_id is required from execution context")
```

### **4. Explicit Error Handling**
```python
# ✅ CORRECT - Fail explicitly if team_id is missing
if not team_id:
    return "❌ Error: Team ID is required but not provided"
```

## **🔧 IMPLEMENTATION GUIDELINES**

### **For Tools:**
```python
@tool("some_tool")
def some_tool(param1: str, team_id: str) -> str:
    """
    Tool description. Requires: param1, team_id
    
    Args:
        param1: Description
        team_id: Team ID (required - must come from execution context)
    """
    # team_id is required, no fallbacks
    pass
```

### **For Services:**
```python
class SomeService:
    async def some_method(self, *, team_id: str) -> Result:
        # team_id is required, no fallbacks
        pass
```

### **For Tests:**
```python
# ✅ CORRECT - Get team ID from actual team configuration
async def test_something():
    # Get team from Firestore or use actual team configuration
    team_service = container.get_service(TeamService)
    teams = await team_service.list_teams()
    if not teams:
        pytest.skip("No teams configured in Firestore")
    
    team_id = teams[0].team_id  # Use actual team ID
```

## **🚨 COMMON MISTAKES TO AVOID**

### **1. Environment Variable Fallbacks**
```python
# ❌ DON'T DO THIS
team_id = os.getenv('TEAM_ID', 'KTI')
```

### **2. Configuration Defaults**
```python
# ❌ DON'T DO THIS
default_team_id: str = Field(default="KAI")
```

### **3. Optional Parameters**
```python
# ❌ DON'T DO THIS
def function(team_id: str | None = None):
    if not team_id:
        team_id = "KTI"  # Fallback
```

### **4. Hardcoded Values**
```python
# ❌ DON'T DO THIS
team_id = "KTI"  # Hardcoded
```

## **📋 VALIDATION CHECKLIST**

### **Code Review Questions:**
- [ ] Does any code use `os.getenv('TEAM_ID', 'default')`?
- [ ] Does any configuration have `default_team_id`?
- [ ] Are there any hardcoded team IDs like `"KTI"` or `"KAI"`?
- [ ] Do any functions have optional `team_id` parameters?
- [ ] Are there any fallback patterns for missing team IDs?

### **Acceptance Criteria:**
- [ ] All team IDs come from Firestore team configuration
- [ ] No hardcoded team ID values anywhere
- [ ] No environment variable fallbacks for team IDs
- [ ] All tools require explicit `team_id` parameter
- [ ] All services require explicit `team_id` parameter
- [ ] Tests use actual team configuration from Firestore

## **🔍 WHY THIS MATTERS**

### **1. Multi-Tenant Architecture**
- Each team must have its own isolated data
- No cross-team data contamination
- Clear ownership of all operations

### **2. Data Integrity**
- Prevents accidental operations on wrong team data
- Ensures all operations are traceable to specific team
- Maintains data consistency

### **3. Scalability**
- Supports multiple teams without code changes
- No hardcoded limits on team count
- Dynamic team management

### **4. Security**
- Prevents unauthorized access to team data
- Ensures proper team context for all operations
- Maintains data isolation

## **🚀 MIGRATION STRATEGY**

### **Phase 1: Remove Defaults**
- Remove all `default_team_id` from settings
- Remove all hardcoded team ID fallbacks
- Make `team_id` required in all functions

### **Phase 2: Update Tools**
- Make all tools require explicit `team_id`
- Update all input models to require `team_id`
- Remove optional `team_id` parameters

### **Phase 3: Update Tests**
- Update tests to use actual team configuration
- Remove hardcoded team IDs from tests
- Use Firestore team data for testing

### **Phase 4: Validation**
- Add linting rules to prevent team ID defaults
- Add code review checklist for team ID usage
- Document the policy for all developers

## **📝 CONCLUSION**

**Team IDs must ALWAYS come from Firestore team configuration. No exceptions. No defaults. No fallbacks. No hardcoded values.**

This policy ensures:
- ✅ Multi-tenant data isolation
- ✅ Data integrity and consistency
- ✅ Scalable architecture
- ✅ Proper security boundaries
- ✅ Maintainable codebase

**Remember: If you need a team ID, get it from Firestore. If you can't get it from Firestore, the operation should fail explicitly.** 