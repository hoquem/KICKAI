# CrewAI Semantic Tool Implementation Standards

This document establishes the mandatory standards for implementing CrewAI semantic tools in the KICKAI project.

## 🚨 **CRITICAL ROUTING RULE - READ THIS FIRST!** 🚨

**ALL ROUTING IS NOW HANDLED BY THE MANAGER LLM - NO HARD-CODED ROUTING RULES!**

The system uses LLM-powered intelligent routing that understands semantic intent. Do NOT implement:
- ❌ Hard-coded command routing patterns
- ❌ Rigid if/else routing logic  
- ❌ Pattern matching for agent selection
- ❌ Manual routing decisions in tools

Instead, trust the Manager LLM to:
- ✅ Understand user intent semantically
- ✅ Route to the appropriate specialist agent
- ✅ Handle natural language variations automatically
- ✅ Consider context (chat type, permissions) intelligently

## 🚨 CRITICAL SEMANTIC PRINCIPLES - READ THIS FIRST! 🚨

**Tools should follow CrewAI semantic patterns for intelligent tool selection.**

### ✅ SEMANTIC NAMING PATTERNS:
- **Use `_self` for requesting user's own data** (`get_player_self`, `get_member_self`)
- **Use `_by_identifier` for looking up others** (`get_player_by_identifier`)
- **Use explicit parameters** (`telegram_username` not `username`)
- **Trust CrewAI semantic understanding** over hardcoded routing

### ❌ WHAT NOT TO DO:
- **NEVER use generic tool names** (`get_player`, `example_tool`)
- **NEVER use ambiguous parameters** (`username`, `player_id`)
- **NEVER rely on hardcoded routing** - let semantic names guide selection
- **NEVER copy-paste parameter lists between tools**

### ✅ SEMANTIC TOOL DEVELOPMENT:
- **Analyze semantic intent** - is this for self or lookup?
- **Use explicit parameter naming** for CrewAI clarity
- **Add clear docstrings** following official KICKAI pattern from CLAUDE.md
- **System tools still need NO user context**
- **Help tools use semantic patterns** when applicable

### 📋 PARAMETER EXAMPLES:

#### System Tools (NO user context needed):
```python
@tool("check_system_ping")
async def check_system_ping() -> str:  # ✅ NO parameters needed
```

#### Help Tools (semantic patterns when applicable):
```python
@tool("show_help_commands")
async def show_help_commands(
    chat_type: str,           # ✅ Only needs chat type
    telegram_username: str = "user"  # ✅ Explicit parameter naming
) -> str:
```

#### Error Tools (explicit naming):
```python
@tool("show_permission_error")
async def show_permission_error(
    telegram_username: str,   # ✅ Explicit parameter naming
    chat_type: str,           # ✅ Only needs chat type
    action: str = "perform this action"  # ✅ Optional action description
) -> str:
```

#### User-Specific Tools (semantic self pattern):
```python
@tool("get_player_self")
async def get_player_self(
    telegram_id: str,         # ✅ Needs user ID
    telegram_username: str,   # ✅ Explicit parameter naming
    team_id: str,             # ✅ Context needed for player lookup
    chat_type: str            # ✅ Context affects behavior
) -> str:
    """Get requesting user's player information.
    
    This tool retrieves the current user's own player data including status,
    position, and team membership. Use when the user wants to see their
    own information, not when looking up other players.
    
    Use when: Player needs status verification
    Required: Active player registration
    Returns: Personal player status summary
    """

@tool("get_player_by_identifier")
async def get_player_by_identifier(
    telegram_id: str,         # ✅ Context for permission check
    team_id: str,             # ✅ Context needed
    target_identifier: str    # ✅ Explicit: who to look up
) -> str:
    """Look up specific player by identifier.
    
    This tool retrieves information about other players in the team
    using their name, phone number, or ID. Use when looking up
    specific players, not when the current user wants their own data.
    
    Use when: Looking up other players by identifier
    Required: Team membership and player identification
    Returns: Player information for specified identifier
    """
```

## 🎯 **AGENT BOUNDARIES AND ROUTING PRINCIPLES**

### **Agent Specialization Rules**
Each agent has CLEAR boundaries and should NEVER handle operations outside their expertise:

- **HELP_ASSISTANT**: Help and guidance ONLY - no data operations
- **PLAYER_COORDINATOR**: Player data and operations ONLY - no team administration
- **TEAM_ADMINISTRATOR**: Team member management ONLY - no player operations  
- **SQUAD_SELECTOR**: Match and squad operations ONLY - no player data
- **MESSAGE_PROCESSOR**: Communication and system operations ONLY - no data operations

### **Routing Principles**
- **Trust the Manager LLM**: It understands semantic intent and routes intelligently
- **No Tool Duplication**: Each tool should have a single, clear purpose
- **Semantic Understanding**: Tool names should guide CrewAI's automatic selection
- **Context Awareness**: The LLM considers chat type and permissions automatically

### **What NOT to Do**
- ❌ **Don't add routing logic to tools** - the Manager LLM handles this
- ❌ **Don't duplicate tools across agents** - each agent has distinct responsibilities
- ❌ **Don't implement command parsing** - let the LLM understand natural language
- ❌ **Don't add hard-coded routing patterns** - trust semantic understanding

## Tool Structure

### Required Imports
```python
#!/usr/bin/env python3
from crewai.tools import tool
from loguru import logger
from kickai.core.dependency_container import get_container
from kickai.features.shared.domain.interfaces.[service]_interface import I[Service]
from kickai.utils.native_crewai_helpers import validate_required_strings  # Only if needed
```

### Tool Decorator (Semantic Naming)
```python
@tool("get_entity_self")              # For user's own data
async def get_entity_self() -> str:

@tool("get_entity_by_identifier")     # For looking up others
async def get_entity_by_identifier() -> str:

@tool("action_entity_modifier")       # General pattern
async def action_entity_modifier() -> str:
```

## Parameter Handling (Semantic Approach)

**REMEMBER: Tools should use explicit parameter naming and semantic patterns.**

### Semantic Parameter Guidelines
- **Use explicit parameter names** (`telegram_username` not `username`)
- **Trust CrewAI semantic understanding** for tool selection
- **Context parameters only when the tool needs user context**
- **System-wide operations typically need NO context parameters**
- **Semantic tools need clear intent** (`_self` vs `_by_identifier`)

### Parameter Validation (Semantic Approach)
```python
# Validate with explicit parameter names
if telegram_username:  # Explicit naming
    validation_error = validate_required_strings(
        telegram_username,
        names=["telegram_username"]  # Clear parameter name
    )
    if validation_error:
        return validation_error

# For semantic tools, validate based on intent
if not target_identifier:  # For _by_identifier tools
    return "❌ Please specify who you want to look up"
    
if not telegram_id:  # For _self tools
    return "❌ User identification required"
```

## 📝 Docstring Standards

**Official KICKAI Pattern - Mandatory for All Tools**

All CrewAI tools must follow this **official pattern** from CLAUDE.md:

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

### Key Principles
- **Focus on WHAT (semantics)** not HOW (implementation)
- **Business intent** over UI commands (/status vs "when status verification needed")
- **Timeless descriptions** that survive interface changes
- **Agent-friendly** for intelligent routing decisions

### Anti-Patterns to Avoid
❌ Implementation details ("serves as application boundary")
❌ Command examples ("USE THIS FOR: /info [player]") 
❌ UI coupling ("JSON formatted response")
❌ Technical parameters ("telegram_id: User's Telegram ID")

**Full standards**: See `docs/DOCSTRING_STANDARDS.md` and `CLAUDE.md`

## Error Handling and Robustness

### Required Pattern
```python
try:
    # Main business logic
    result = service.operation()
    return formatted_response
    
except Exception as e:
    logger.error(f"❌ Error in tool_name: {e}")
    return f"❌ Operation failed: {str(e)}"
```

### Enhanced Robustness Patterns

#### Service Availability Checks
```python
# Get domain service through dependency injection with availability check
container = get_container()
try:
    service = container.get_service(IServiceInterface)
    if not service:
        return "❌ Service is not available"
except Exception as e:
    logger.error(f"❌ Failed to get service: {e}")
    return "❌ Service is not available"
```

#### Graceful Service Operation Handling
```python
# Execute pure business logic with graceful error handling
try:
    result = service.operation()
    formatted_response = service.format_response(result)
except Exception as e:
    logger.warning(f"⚠️ Service operation failed: {e}")
    return f"⚠️ Operation failed: {str(e)}"
```

#### Permission Checks
```python
# Check if user has permission for this action
if chat_type != "leadership":
    return "❌ This action requires leadership access"
```

## Return Values and Formatting

### NO MARKDOWN FORMATTING
- **All responses must be plain text**
- **Use emojis for visual structure**
- **Format for Telegram compatibility**

### Examples
```python
# ✅ CORRECT - Plain text with emojis
return f"👤 User Status for {username}\n\n🏃 Player Info:\n   • ID: {player_id}"

# ❌ WRONG - Markdown formatting
return f"👤 **User Status for {username}**\n\n🏃 **Player Info:**\n   • **ID:** {player_id}"
```

### Enhanced User Experience
- **Provide helpful error messages**
- **Include suggestions for next steps**
- **Use consistent emoji patterns**

## Logging Standards

### Required Log Levels
```python
logger.info(f"✅ Operation completed successfully for {username}")
logger.warning(f"⚠️ Non-critical issue occurred: {issue}")
logger.error(f"❌ Critical error in tool_name: {error}")
logger.debug(f"🔍 Debug information: {debug_data}")
```

### Logging Context
- **Include relevant identifiers (username, telegram_id)**
- **Log both success and failure cases**
- **Provide enough context for debugging**

## Clean Architecture Compliance

### Service Access
- **Use dependency injection: `container.get_service(IServiceInterface)`**
- **Remove any direct service instantiation**
- **Access services through interfaces, not concrete classes**

### Domain Logic
- **Tools should only orchestrate service calls**
- **Business logic belongs in domain services**
- **Tools handle formatting and error presentation**

## Tool Naming Convention

### Pattern: `[action]_[entity]_[modifier]`
- **`get_user_status_my`** - Get current user's status
- **`get_user_status_other`** - Get another user's status
- **`show_permission_error`** - Show permission denied message
- **`send_team_message`** - Send message to team
- **`check_system_ping`** - Check system connectivity

### Examples
```python
@tool("get_user_status_my")      # ✅ Clear and specific
@tool("show_permission_error")   # ✅ Action + entity + modifier
@tool("check_system_health")     # ✅ System operation
@tool("send_team_announcement")  # ✅ Team communication
```

## Implementation Checklist

Before committing any tool, verify:

- [ ] **Tool only has parameters it actually needs**
- [ ] **NO unnecessary context parameters added**
- [ ] **Uses dependency injection for services**
- [ ] **Implements comprehensive error handling**
- [ ] **NO MARKDOWN FORMATTING in responses**
- [ ] **Implements permission checks where needed**
- [ ] **Follows tool naming convention**
- [ ] **Includes service availability checks**
- [ ] **Provides graceful degradation**
- [ ] **Uses proper logging levels**
- [ ] **Returns plain text with emojis**
- [ ] **Validates only required parameters**

## Example 1: Simple System Tool (No Context Needed)

```python
@tool("check_system_ping")
async def check_system_ping() -> str:
    """
    Check system connectivity and response time.

    Use this tool to test if the KICKAI system is responsive.
    This performs a simple ping test to verify system connectivity.

    Returns:
        System ping response with timing and status information
    """
    try:
        logger.info(f"🏓 System ping request initiated")
        
        container = get_container()
        try:
            system_service = container.get_service(ISystemService)
            if not system_service:
                return "❌ System service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get system service: {e}")
            return "❌ System service is not available"
        
        try:
            ping_result = system_service.perform_ping()
            formatted_response = system_service.format_ping_response(ping_result)
        except Exception as e:
            logger.warning(f"⚠️ System ping operation failed: {e}")
            return f"⚠️ System ping operation failed: {str(e)}"
        
        logger.info(f"✅ Ping response completed in {ping_result.response_time}ms")
        return formatted_response
        
    except Exception as e:
        logger.error(f"❌ Error in ping tool: {e}")
        return f"❌ System ping failed: {str(e)}"
```

## Example 2: Context-Aware Tool (Minimal Context)

```python
@tool("show_help_commands")
async def show_help_commands(
    chat_type: str,
    username: str = "user"
) -> str:
    """
    Show comprehensive help and available commands based on user's context.

    Use this tool to display help content appropriate for the user's chat type.
    This provides context-aware command listings and guidance.

    Args:
        chat_type: Chat type context (main/leadership/private) - determines available commands
        username: User's name for personalization (defaults to 'user')

    Returns:
        Formatted help text string for direct display
    """
    try:
        if not chat_type or not chat_type.strip():
            return "❌ Chat type is required"

        logger.info(f"🔧 Help request from user {username} in {chat_type} chat")

        container = get_container()
        try:
            help_service = container.get_service(IHelpService)
            if not help_service:
                return "❌ Help service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get help service: {e}")
            return "❌ Help service is not available"

        try:
            help_content = help_service.generate_help_content(chat_type, username)
            formatted_message = help_service.format_help_message(help_content)
        except Exception as e:
            logger.warning(f"⚠️ Help service operation failed: {e}")
            return f"⚠️ Unable to generate help content: {str(e)}"

        logger.info(f"✅ Generated help message for {username}")
        return formatted_message

    except Exception as e:
        logger.error(f"❌ Error generating help response: {e}")
        return f"❌ Sorry, I couldn't generate the help information right now. Error: {str(e)}"
```

## Example 3: Robust Tool with Enhanced Error Handling

```python
@tool("get_user_permissions")
async def get_user_permissions(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get comprehensive user permissions and capabilities.

    Use this tool to determine what actions a user can perform.
    This provides detailed permission information based on user roles and context.

    Args:
        telegram_id: User's Telegram ID (string)
        team_id: Team identifier (required)
        username: User's name for display
        chat_type: Chat type context for permission calculation

    Returns:
        Detailed user permissions list with role information
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            telegram_id, team_id, username, chat_type,
            names=["telegram_id", "team_id", "username", "chat_type"]
        )
        if validation_error:
            return validation_error

        logger.info(f"🔐 Permission check for {username} in team {team_id}")

        # Get services through dependency injection with availability checks
        container = get_container()
        
        # Check player service availability
        try:
            player_service = container.get_service(IPlayerService)
            if not player_service:
                return "❌ Player service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get player service: {e}")
            return "❌ Player service is not available"

        # Check team member service availability
        try:
            team_member_service = container.get_service(ITeamMemberService)
            if not team_member_service:
                return "❌ Team member service is not available"
        except Exception as e:
            logger.error(f"❌ Failed to get team member service: {e}")
            return "❌ Team member service is not available"

        # Execute business logic with graceful error handling
        try:
            player = player_service.get_player_by_telegram_id(int(telegram_id))
        except Exception as e:
            logger.warning(f"⚠️ Failed to get player info: {e}")
            player = None

        try:
            team_member = team_member_service.get_team_member_by_telegram_id(int(telegram_id))
        except Exception as e:
            logger.warning(f"⚠️ Failed to get team member info: {e}")
            team_member = None

        # Build permissions text
        permissions_text = f"🔐 User Permissions for {username}\n\n"

        if team_member:
            permissions_text += f"👥 Team Member Role: {team_member.role}\n"
            permissions_text += f"🏢 Team: {team_member.team_id}\n\n"
            
            # Role-based permissions
            if team_member.role in ["admin", "manager", "captain", "coach"]:
                permissions_text += "👑 Administrative Permissions:\n"
                permissions_text += "   • Manage team members\n"
                permissions_text += "   • Send team announcements\n"
                permissions_text += "   • Create and manage polls\n"
                permissions_text += "   • Access leadership commands\n"
            else:
                permissions_text += "👤 Member Permissions:\n"
                permissions_text += "   • View team information\n"
                permissions_text += "   • Update personal status\n"
                permissions_text += "   • Participate in polls\n"

        if player:
            permissions_text += f"\n🏃 Player Permissions:\n"
            permissions_text += "   • Update availability\n"
            permissions_text += "   • View match schedules\n"
            permissions_text += "   • Update personal info\n"

        if not team_member and not player:
            permissions_text += "❌ No permissions found\n"
            permissions_text += "💡 Contact team leadership to get access"

        logger.info(f"✅ Permissions provided for {username}")
        return permissions_text

    except Exception as e:
        logger.error(f"❌ Error getting user permissions for {telegram_id}: {e}")
        return f"❌ Failed to get user permissions: {str(e)}"
```

## Common Anti-Patterns to Avoid

### ❌ Adding Unnecessary Context Parameters
```python
# WRONG - System tool doesn't need user context
@tool("check_system_ping")
async def check_system_ping(
    telegram_id: str,  # ❌ NOT needed for system ping
    team_id: str,      # ❌ NOT needed for system ping
    username: str,     # ❌ NOT needed for system ping
    chat_type: str     # ❌ NOT needed for system ping
) -> str:
```

### ❌ Using Markdown Formatting
```python
# WRONG - Markdown in responses
return f"👤 **User Status for {username}**\n\n🏃 **Player Info:**\n   • **ID:** {player_id}"

# CORRECT - Plain text with emojis
return f"👤 User Status for {username}\n\n🏃 Player Info:\n   • ID: {player_id}"
```

### ❌ Direct Service Instantiation
```python
# WRONG - Direct instantiation
system_service = SystemService()

# CORRECT - Dependency injection
system_service = container.get_service(ISystemService)
```

## Testing Requirements

### Unit Tests
- **Test with minimal required parameters**
- **Verify error handling for missing services**
- **Test parameter validation**
- **Verify plain text output (no markdown)**

### Integration Tests
- **Test service availability scenarios**
- **Verify graceful degradation**
- **Test permission checks**
- **Verify logging output**

## Maintenance

### Regular Reviews
- **Monthly tool parameter audit**
- **Verify no unnecessary context parameters added**
- **Check for markdown formatting**
- **Review service access patterns**

### Code Reviews
- **Mandatory checklist verification**
- **Parameter necessity validation**
- **Architecture compliance check**
- **Error handling review**

---

**Remember: When in doubt, ask yourself "Does this tool actually need this parameter to function?" If the answer is no, don't add it!**
