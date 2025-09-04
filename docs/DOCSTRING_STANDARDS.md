# KICKAI Docstring Standards

## 🎯 Official Tool Docstring Standards

**Source**: CLAUDE.md - Official KICKAI Project Standards  
**Status**: Mandatory for all CrewAI tools  
**Focus**: Business semantics and intent, not technical implementation  

---

## 📝 Core Pattern

All CrewAI tools must follow this **official pattern**:

```python
@tool("tool_name")
async def tool_name(...) -> str:
    """
    [SEMANTIC ACTION] - What business action does this perform?
    
    [BUSINESS CONTEXT] - Why this action matters and its business impact
    
    Use when: [BUSINESS INTENT TRIGGER - when this business need arises]
    Required: [BUSINESS PERMISSIONS/CONDITIONS - what business rules apply]
    
    Returns: [SEMANTIC BUSINESS OUTCOME - what business result is delivered]
    """
```

---

## 🔑 Key Principles

- **Focus on WHAT (semantics)** not HOW (implementation)
- **Business intent** over UI commands (/status vs "when status verification needed")
- **Timeless descriptions** that survive interface changes
- **Agent-friendly** for intelligent routing decisions

---

## ❌ Anti-Patterns to Avoid

- ❌ Implementation details ("serves as application boundary")
- ❌ Command examples ("USE THIS FOR: /info [player]") 
- ❌ UI coupling ("JSON formatted response")
- ❌ Technical parameters ("telegram_id: User's Telegram ID")

---

## 📚 Examples by Category

### Player Management
```python
@tool("create_player")
async def create_player(...) -> str:
    """Register new player in team roster.
    
    Establishes player profile with contact information and position
    assignment, initiating the verification and approval workflow.
    
    Use when: New team member joins as player
    Required: Basic player information
    Returns: Player registration confirmation
    """
```

### Team Administration  
```python
@tool("promote_member_admin")
async def promote_member_admin(...) -> str:
    """Elevate member to administrative role.
    
    Grants enhanced permissions for team management activities
    including player approval and match administration.
    
    Use when: Leadership expansion is needed
    Required: Current admin privileges
    Returns: Role elevation confirmation
    """
```

### Match Management
```python
@tool("create_match")
async def create_match(...) -> str:
    """Schedule official match with opponent.
    
    Creates match record with date, venue, and competition details,
    triggering availability collection and squad selection processes.
    
    Use when: Competition fixtures are confirmed
    Required: Match coordination rights
    Returns: Match scheduling confirmation
    """
```

### Communication
```python
@tool("send_team_announcement")
async def send_team_announcement(...) -> str:
    """Broadcast official team communication.
    
    Delivers important information to all team members through
    established communication channels with delivery confirmation.
    
    Use when: Team-wide notification is required
    Required: Communication privileges  
    Returns: Message delivery status
    """
```

### Status & Information
```python
@tool("get_player_status_self")
async def get_player_status_self(...) -> str:
    """Retrieve personal player information.
    
    Provides current registration status, position assignment,
    and participation eligibility for the requesting player.
    
    Use when: Player needs status verification
    Required: Active player registration
    Returns: Personal player status summary
    """
```

---

## 🔍 Validation Checklist

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

## 🚀 Implementation Guidelines

1. **Start with High-Impact Tools**: Focus on frequently used tools first
2. **Group by Feature**: Update tools within same feature area together
3. **Maintain Consistency**: Use similar language patterns for similar actions
4. **Test Agent Understanding**: Verify docstrings support intelligent routing
5. **Review Business Context**: Ensure descriptions align with domain terminology

---

## 📖 Reference

**Full standards**: See `CLAUDE.md` for complete project standards and guidelines.

This standard ensures KICKAI tool documentation remains maintainable, business-focused, and valuable for both human developers and AI agents.