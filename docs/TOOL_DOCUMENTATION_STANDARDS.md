# KICKAI Tool Documentation Standards

**Last Updated:** January 2025  
**Status:** Official Standard - Official Pattern from CLAUDE.md  
**Focus:** Business semantics and intent for CrewAI Agents  

---

## 📝 **Official Tool Docstring Standard**

Based on the **official KICKAI standards** from CLAUDE.md, all tools must follow this pattern:

```python
@tool("tool_name")
async def tool_name(
    param1: str,
    param2: str
) -> str:
    """[SEMANTIC ACTION] - What business action does this perform?
    
    [BUSINESS CONTEXT] - Why this action matters and its business impact
    
    Use when: [BUSINESS INTENT TRIGGER - when this business need arises]
    Required: [BUSINESS PERMISSIONS/CONDITIONS - what business rules apply]
    
    Returns: [SEMANTIC BUSINESS OUTCOME - what business result is delivered]
    """
```

### **Why This Standard?**
- **Business-focused** for intelligent CrewAI routing
- **Timeless** - survives UI and command changes
- **Semantic** - focuses on intent, not implementation
- **Agent-friendly** - optimized for CrewAI tool selection

---

## 🎯 **Core Principles**

### **1. Semantic Action (Required)**
- **Clear business action** the tool performs
- Focus on **what happens in the domain**, not technically
- Examples:
  - ✅ "Grant player eligibility for squad selection"
  - ✅ "Schedule official match with opponent"
  - ❌ "Retrieves data from database using service"

### **2. Business Context (Required)**
- **Why this action matters** and its business impact
- Focus on **domain value**, not system implementation
- Examples:
  - ✅ "Validates and activates player participation rights"
  - ✅ "Creates match record triggering availability collection"
  - ❌ "Handles framework concerns and delegates to domain service"

### **3. Use When (Required)**
- **Business conditions** that trigger this action
- Focus on **business intent**, not user commands
- Examples:
  - ✅ "Use when: Player verification is complete"
  - ✅ "Use when: Competition fixtures are confirmed"
  - ❌ "Use when: User types /approve command"

### **4. Required (Required)**
- **Business permissions and conditions** needed
- Focus on **business rules**, not technical requirements
- Examples:
  - ✅ "Required: Leadership or admin role"
  - ✅ "Required: Match coordination rights"
  - ❌ "Required: telegram_id and team_id parameters"

### **5. Returns (Required)**
- **Business outcome** the tool delivers
- Focus on **business value**, not data format
- Examples:
  - ✅ "Returns: Player activation status"
  - ✅ "Returns: Match scheduling confirmation"
  - ❌ "Returns: JSON formatted response with player data"

---

## ✅ **EXCELLENT EXAMPLES**

### **Squad Selection Tool**
```python
@tool("select_squad_optimal")
async def select_squad_optimal(
    team_id: str,
    chat_type: str,
    match_id: str,
    squad_size: int = 16
) -> str:
    """Select optimal squad composition for upcoming match.
    
    Analyzes player availability and performance to create the best
    possible squad for a specific match, considering availability status,
    priority scores, and registration dates.
    
    Use when: Finalizing squad selection for upcoming matches
    Required: Leadership permissions and match identification
    Returns: Squad selection with chosen players and waiting list
    """
```

### **Player Self-Service Tool**
```python
@tool("get_availability_player_self")
async def get_availability_player_self(
    telegram_id: str,
    team_id: str,
    match_id: str
) -> str:
    """Retrieve personal availability status for specific match.
    
    Provides current player's availability submission including status,
    submission date, and any notes for match planning and coordination.
    
    Use when: Player needs to check their own availability status
    Required: Active player registration and match access
    Returns: Personal availability status with submission details
    """
```

---

## 🔍 **Validation Checklist**

Before finalizing any docstring, verify:

### Content Quality
- [ ] First line describes semantic business action (not technical operation)
- [ ] Context paragraph explains business impact (not implementation)
- [ ] No references to specific commands, UI elements, or technical details
- [ ] Intent triggers are business conditions (not user actions)
- [ ] Permissions are business roles (not technical requirements)
- [ ] Returns describe business value (not data formats)

### Language Standards
- [ ] Uses present tense action verbs
- [ ] Avoids technical jargon and implementation details
- [ ] Consistent terminology across similar tools
- [ ] Clear and concise without unnecessary verbosity
- [ ] Professional tone appropriate for business context

### Future-Proofing
- [ ] No coupling to current UI patterns or specific commands
- [ ] Would remain valid if interface changes completely
- [ ] Focuses on business logic that remains stable over time
- [ ] Agent-friendly for intelligent routing decisions

---

## 🚀 **Implementation Guidelines**

1. **Start with High-Impact Tools**: Focus on frequently used tools first
2. **Group by Feature**: Update tools within same feature area together
3. **Maintain Consistency**: Use similar language patterns for similar actions
4. **Test Agent Understanding**: Verify docstrings support intelligent routing
5. **Review Business Context**: Ensure descriptions align with domain terminology

---

## 📖 **Reference**

**Full standards**: See `CLAUDE.md` for complete project standards and `docs/DOCSTRING_STANDARDS.md` for detailed examples.

This standard ensures KICKAI tool documentation remains maintainable, business-focused, and valuable for both human developers and AI agents.