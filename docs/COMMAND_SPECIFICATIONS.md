# KICKAI Command Specifications

**Version:** 3.0  
**Status:** Production Ready  
**Last Updated:** December 2024  
**Architecture:** Agentic Command Processing with CrewAI

This document defines the expected behavior for all KICKAI bot commands across different scenarios, chat types, and user states, using the latest agentic architecture.

## Table of Contents
- [Command Overview](#command-overview)
- [Agentic Architecture](#agentic-architecture)
- [Chat Types](#chat-types)
- [User States](#user-states)
- [Command Specifications](#command-specifications)
- [Command Processing Flow](#command-processing-flow)
- [Testing Scenarios](#testing-scenarios)

## Command Overview

### Core Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level | Agent |
|---------|-------------|-----------|-----------------|------------------|-------|
| `/help` | Show available commands | ✅ | ✅ | PUBLIC | HelpAssistantAgent |
| `/start` | Initialize bot interaction | ✅ | ✅ | PUBLIC | MessageProcessorAgent |
| `/register` | Register as a player | ✅ | ❌ | PUBLIC | PlayerCoordinatorAgent |
| `/myinfo` | Show personal information | ✅ | ✅ | PUBLIC | PlayerCoordinatorAgent |
| `/status` | Check player/team member status | ✅ | ✅ | PUBLIC | PlayerCoordinatorAgent |
| `/list` | List players/team members | ✅ | ✅ | PUBLIC | TeamManagerAgent |

### Player Management Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level | Agent |
|---------|-------------|-----------|-----------------|------------------|-------|
| `/add` | Add a new player | ❌ | ✅ | LEADERSHIP | TeamManagerAgent |
| `/approve` | Approve player registration | ❌ | ✅ | LEADERSHIP | TeamManagerAgent |
| `/reject` | Reject player registration | ❌ | ✅ | LEADERSHIP | TeamManagerAgent |
| `/pending` | Show pending registrations | ❌ | ✅ | LEADERSHIP | TeamManagerAgent |

### Team Management Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level | Agent |
|---------|-------------|-----------|-----------------|------------------|-------|
| `/team` | Team information | ✅ | ✅ | PUBLIC | TeamManagerAgent |
| `/invite` | Generate invitation link | ❌ | ✅ | LEADERSHIP | TeamManagerAgent |
| `/announce` | Make team announcement | ❌ | ✅ | LEADERSHIP | TeamManagerAgent |

### System Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level | Agent |
|---------|-------------|-----------|-----------------|------------------|-------|
| `/health` | System health check | ❌ | ✅ | SYSTEM | SystemInfrastructureAgent |
| `/version` | Bot version info | ✅ | ✅ | PUBLIC | MessageProcessorAgent |
| `/config` | Configuration info | ❌ | ✅ | SYSTEM | SystemInfrastructureAgent |

## Agentic Architecture

### Command Processing Overview

The KICKAI system uses an **agentic-first approach** where all commands are processed through specialized CrewAI agents rather than dedicated command handlers.

```mermaid
graph TD
    A[User Message] --> B{Message Type}
    B -->|Slash Command| C[Command Registry]
    B -->|Natural Language| D[Direct Processing]
    B -->|Unknown| E[Error Response]
    
    C --> F[Build Command String]
    D --> G[Extract Message Text]
    
    F --> H[_handle_crewai_processing]
    G --> H
    
    H --> I[CrewAI System]
    I --> J[Orchestration Pipeline]
    J --> K[Intent Classification]
    K --> L[Complexity Assessment]
    L --> M[Task Decomposition]
    M --> N[Agent Routing]
    N --> O[Task Execution]
    O --> P[Result Aggregation]
    P --> Q[User Response]
```

### Agent Responsibilities

#### 1. **HelpAssistantAgent**
- **Primary Commands**: `/help`, help-related natural language
- **Responsibilities**:
  - Context-aware help information
  - User status validation
  - Command availability checking
  - Registration flow guidance
- **Tools**: `get_user_status`, `get_available_commands`, `format_help_message`

#### 2. **MessageProcessorAgent**
- **Primary Commands**: `/start`, `/version`, general natural language
- **Responsibilities**:
  - Message parsing and intent classification
  - Context extraction
  - Simple query responses
  - Agent routing for complex requests
- **Tools**: Intent analysis, context extraction, message routing

#### 3. **PlayerCoordinatorAgent**
- **Primary Commands**: `/register`, `/myinfo`, `/status`
- **Responsibilities**:
  - Player registration and onboarding
  - Individual player support
  - Player status tracking
  - Personal information management
- **Tools**: Player management, registration, status tracking

#### 4. **TeamManagerAgent**
- **Primary Commands**: `/list`, `/add`, `/approve`, `/reject`, `/team`, `/invite`, `/announce`
- **Responsibilities**:
  - Team administration
  - Player management
  - Team coordination
  - Administrative oversight
- **Tools**: Team management, player administration, team coordination

#### 5. **SystemInfrastructureAgent**
- **Primary Commands**: `/health`, `/config`
- **Responsibilities**:
  - System health monitoring
  - Configuration management
  - System diagnostics
  - Infrastructure oversight
- **Tools**: Health monitoring, configuration management, system diagnostics

### Command Registration Pattern

Commands are registered using decorators but delegate to CrewAI agents:

```python
@command("/help", "Show available commands", feature="shared")
async def handle_help(update, context, **kwargs):
    # Command is registered but delegates to HelpAssistantAgent
    # No direct implementation - handled by CrewAI agent
    pass
```

### Natural Language Processing

All natural language queries are processed through the **unified CrewAI pipeline** - the same system that handles slash commands.

#### **Unified Processing Flow**

```python
# Both slash commands and natural language converge here:
async def _handle_crewai_processing(self, update, message_text, user_id, chat_id, chat_type, username):
    # Create execution context
    execution_context = {
        'user_id': user_id,
        'team_id': self.team_id,
        'chat_id': chat_id,
        'is_leadership_chat': chat_type == ChatType.LEADERSHIP,
        'username': username,
        'message_text': message_text  # ← Only difference between input types!
    }
    
    # Execute with CrewAI ← UNIFIED PROCESSING
    result = await self.crewai_system.execute_task(message_text, execution_context)
```

#### **Input Processing Examples**

**Slash Command Path:**
```python
# User types: /help
message_text = "/help"

# User types: /myinfo
message_text = "/myinfo"
```

**Natural Language Path:**
```python
# User types: "help me"
message_text = "help me"

# User types: "what's my info"
message_text = "what's my info"
```

**Both paths converge to the same processing pipeline!**

### Natural Language Security Implementation

Since both paths use the same processing pipeline, **security is automatically consistent**:

#### **1. Intent Classification**
```python
async def _classify_intent(self, message_text: str, user_id: str, chat_type: str) -> Dict[str, Any]:
    """Classify user intent from natural language."""
    # Use LLM to determine what the user wants to do
    # Return structured intent with action, parameters, and confidence
```

#### **2. Command Mapping**
```python
def _map_intent_to_command(self, intent: Dict[str, Any]) -> Optional[str]:
    """Map natural language intent to equivalent command for permission checking."""
    intent_action = intent.get('action', '').lower()
    
    # Map common natural language patterns to commands
    mappings = {
        'help': '/help',
        'show commands': '/help',
        'what can you do': '/help',
        'my info': '/myinfo',
        'my information': '/myinfo',
        'player status': '/status',
        'list players': '/list',
        'team info': '/team',
        'add player': '/add',
        'approve player': '/approve',
        'system health': '/health',
        'bot version': '/version'
    }
    
    return mappings.get(intent_action)
```

#### **3. Permission Validation**
```python
async def _check_permission(self, command: str, user_id: str, chat_type: str) -> bool:
    """Check if user has permission to execute the equivalent command."""
    # Use the same permission logic as slash commands
    registry = get_command_registry()
    command_metadata = registry.get_command(command)
    
    if not command_metadata:
        return False
    
    # Apply same permission checking logic
    user_permission = await self._get_user_permission_level(user_id, chat_type)
    return user_permission >= command_metadata.permission_level.value
```

#### **4. Access Control**
```python
async def _send_access_denied_message(self, update, command: str):
    """Send access denied message for natural language requests."""
    chat_type = self._determine_chat_type(str(update.effective_chat.id))
    
    if chat_type == ChatType.MAIN:
        message = f"""❌ **Access Denied**

🔒 The action you requested requires leadership access.
💡 Please use the leadership chat for this function."""
    else:
        message = f"""❌ **Access Denied**

🔒 You don't have permission to perform this action.
💡 Contact your team admin for access."""
    
    await update.message.reply_text(message, parse_mode='Markdown')
```

## 🔒 Security & Access Control

### **Unified Security Through Unified Processing**

The KICKAI system implements **comprehensive permission checking** through its unified processing pipeline. Since both slash commands and natural language use the same CrewAI orchestration system, security is automatically consistent.

#### **Security Flow**

```mermaid
graph TD
    A[User Input] --> B{Input Type}
    B -->|Slash Command| C[Command Registry]
    B -->|Natural Language| D[Direct Processing]
    
    C --> E[Build Command String]
    D --> F[Extract Message Text]
    
    E --> G[_handle_crewai_processing]
    F --> G
    
    G --> H[CrewAI System]
    H --> I[Orchestration Pipeline]
    I --> J[Intent Classification]
    J --> K[Permission Check]
    K -->|Allowed| L[Task Decomposition]
    K -->|Denied| M[Access Denied]
    
    L --> N[Agent Routing]
    N --> O[Task Execution]
    O --> P[Result Aggregation]
    M --> Q[Security Log]
```

#### **Permission Levels**

| Level | Description | Access |
|-------|-------------|--------|
| **PUBLIC** | Available to everyone | Basic commands, help, version |
| **PLAYER** | Available to registered players | Player-specific commands |
| **LEADERSHIP** | Available to team leadership | Administrative commands |
| **ADMIN** | Available to team admins | System configuration |
| **SYSTEM** | Available to system only | Health checks, diagnostics |

#### **Security Implementation**

**1. Unified Processing Pipeline**
- Both slash commands and natural language use the same CrewAI system
- Same permission logic applied to both input types
- No bypass of permission system through natural language

**2. Intent-to-Command Mapping**
- Natural language requests are mapped to equivalent commands
- Same permission logic applied to both input types
- No bypass of permission system through natural language

**3. Context-Aware Validation**
- Chat type validation (main vs leadership)
- User role validation (player vs team member vs admin)
- Team-based isolation (team_id scoping)

**4. Comprehensive Logging**
- All permission checks logged for audit
- Failed attempts tracked for security monitoring
- User actions traced for accountability

#### **Security Examples**

**Example 1: Unauthorized Leadership Request**
```
User (in main chat): "Add a new player to the team"
System: Maps to /add command
Permission Check: LEADERSHIP required, user has PLAYER level
Result: ❌ Access Denied - "This action requires leadership access"
```

**Example 2: Authorized Player Request**
```
User (in main chat): "Show me my player information"
System: Maps to /myinfo command
Permission Check: PUBLIC level, user has PLAYER level
Result: ✅ Access Granted - Player information displayed
```

**Example 3: Leadership Command in Leadership Chat**
```
User (in leadership chat): "Approve player registration"
System: Maps to /approve command
Permission Check: LEADERSHIP required, user has LEADERSHIP level
Result: ✅ Access Granted - Player approval processed
```

### **Benefits of Unified Security**

1. **🔒 Consistent Protection**: Same security for all input methods
2. **🔄 Single Security Logic**: No duplication of permission checking
3. **🧪 Unified Testing**: Security tested once, works everywhere
4. **🛠️ Maintainable**: Single security pipeline to maintain
5. **📈 Scalable**: New input methods automatically inherit security
6. **🎯 No Security Gaps**: Impossible to bypass through different input methods

## Chat Types

### Main Chat (`{team_config.main_chat_id}`)
**Purpose**: General team communication  
**Users**: All registered players and team members  
**Commands**: Public commands, player-focused features  
**Context**: `is_leadership_chat: false`

### Leadership Chat (`{team_config.leadership_chat_id}`)
**Purpose**: Administrative and management functions  
**Users**: Team leaders, administrators, coaches  
**Commands**: All commands including administrative functions  
**Context**: `is_leadership_chat: true`

## User States

### First User (First Team Member)
**Status**: Team owner, full permissions  
**Access**: All chats, all commands  
**Note**: This is the first user who registered in the leadership chat and became the first member in the team member collection. This user is not necessarily the bot creator. The User ID and telegram name are only known after they register in the leadership chat.

**Dynamic Assignment**: The system automatically assigns team owner status to the first user who registers in the leadership chat, regardless of their User ID or telegram name.

### Registered Player
**Status**: Active player in the system  
**Access**: Main chat commands, limited leadership chat access  
**Data**: Player record in Firestore

**Design Principle**: Commands have distinct implementations for different chat contexts to maintain clean, predictable behavior.

#### **Command Context Design**
- **Main Chat Commands**: Implemented specifically for player interactions
- **Leadership Chat Commands**: Implemented specifically for administrative functions
- **Same Command Names**: Can exist in both contexts but with different implementations
- **Clean Architecture**: No conditional logic based on chat context

#### **Example: `/list` Command**
```python
# Main Chat Implementation
@command(name="/list", description="List active players", chat_type="main")
async def list_players_main(update, context):
    """List only active players in main chat."""
    players = await get_active_players()
    return format_player_list(players, show_status=False)

# Leadership Chat Implementation  
@command(name="/list", description="List all players with status", chat_type="leadership")
async def list_players_leadership(update, context):
    """List all players with detailed status in leadership chat."""
    players = await get_all_players()
    return format_player_list(players, show_status=True, show_details=True)
```

#### **Benefits of This Approach**
- **🎯 Predictable Behavior**: Same command always behaves the same way in same context
- **🧹 Clean Code**: No complex conditional logic
- **📋 Clear Intent**: Each implementation has a single, clear purpose
- **🛠️ Maintainable**: Easy to modify behavior for specific contexts
- **🧪 Testable**: Each implementation can be tested independently

### Registered Team Member
**Status**: Member of the leadership chat with team management responsibilities  
**Access**: All commands in leadership chat, admin commands based on role  
**Data**: Team member record in Firestore  
**Registration**: Must register to provide their details

#### **Dual Role Capability**
- **Team Member**: Core role as a member of the leadership chat
- **Player**: Can also be a registered player if added to main chat and completed registration
- **Role-Based Permissions**: Admin commands only available with admin role

#### **Registration Process**
```python
# Team member registration flow
async def register_team_member(update, context):
    """Register a new team member with their details."""
    # Collect team member information
    # Store in team_members collection
    # Assign appropriate roles and permissions
    # Grant access to leadership chat commands
```

#### **Role-Based Access Control**
```python
# Example role checking for admin commands
@command(name="/approve", description="Approve player registration", chat_type="leadership")
async def approve_player(update, context):
    """Approve a player registration (admin only)."""
    user_roles = await get_user_roles(update.effective_user.id)
    
    if "admin" not in user_roles:
        return "❌ Access Denied: Admin role required for this command."
    
    # Proceed with approval logic
    return await process_player_approval(update, context)
```

#### **Available Commands**
- **All Leadership Commands**: Can run any command available in leadership chat
- **Admin Commands**: Only if they have admin role
- **Player Commands**: If also registered as a player in main chat
- **Team Management**: Access to team oversight and coordination features

#### **Example Team Member Response**
```
👔 KICKAI Leadership Commands

👤 {telegram_name} (ID: {member_id})
Role: {role} | Player: {is_player}

Team Management:
• /register - Register new player with name, phone, position
• /add - Add new player to team roster
• /list - List all players with their status
• /status - Check player status by phone number
• /myinfo - Check your team member information

Admin Commands (Admin role required):
• /approve - Approve player registration
• /reject - Reject player registration
• /pending - List pending registrations
• /announce - Send team announcement

Natural Language:
You can also ask me questions in natural language!
```

### 4. Pending Registration
- **Status**: Registration submitted, awaiting approval
- **Access**: Limited main chat access
- **Data**: Pending player record in Firestore

### Unregistered User
**Status**: No record in system  
**Access**: Basic commands only  
**Data**: No Firestore record  
**Guidance**: Users are asked to contact a member of the leadership team to be added as a player, or they can leave the chat if they got here by mistake.

## Command Specifications

### `/help` Command

#### Agentic Implementation Overview

The `/help` command is implemented using the **HelpAssistantAgent** that provides context-aware help information with proper user validation and registration flows.

**Key Components:**
- **HelpAssistantAgent**: Specialized agent for help processing
- **MessageFormattingService**: Centralized message formatting
- **Command Registry**: Dynamic command discovery
- **User Context**: Complete user context with permissions

#### Agent Implementation

**HelpAssistantAgent** (`src/features/shared/domain/agents/help_assistant_agent.py`):
```python
class HelpAssistantAgent:
    """Help Assistant Agent for processing help requests."""
    
    async def process_help_request(self, user_id: str, team_id: str, chat_type: str, 
                                 username: str, name: str) -> str:
        # 1. Get user status
        user_status = get_user_status_tool(user_id, team_id, chat_type)
        
        # 2. Get available commands
        commands_info = get_available_commands_tool(chat_type, user_id, team_id)
        
        # 3. Format response using centralized service
        formatter = get_message_formatting_service()
        context = MessageContext(...)
        return formatter.format_help_message(context, commands_info)
```

#### Context-Aware Behavior Design

The `/help` command provides **context-aware** information based on:

1. **Chat Type**: Main chat vs Leadership chat
2. **User Status**: Registered vs Unregistered
3. **Chat Context Rules**: 
   - **Main Chat**: Treat everyone as players (even if they're also team members)
   - **Leadership Chat**: Treat everyone as team members (even if they're also players)
4. **Registration Flow**: Proper guidance for unregistered users

#### Expected Behavior by Chat Type and User Status

**Main Chat - Unregistered User:**
```
👋 Welcome to KICKAI, {telegram_name}!

🤔 I don't see you registered as a player yet.

📞 Please contact a member of the leadership team to add you as a player to this team.

💡 Once you're registered, you'll be able to use all player commands!
```

**Main Chat - Registered User (Treated as Player):**
```
🤖 KICKAI Commands

👤 {telegram_name} (Player)

Player Management:
• /register - Register as a new player
• /list - List all team players
• /status - Check player status by phone number
• /myinfo - Check your player information

General Commands:
• /help - Show this help message
• /start - Start the bot

Natural Language:
You can also ask me questions in natural language!
```

**Leadership Chat - First User (Admin Setup):**
```
🎉 Welcome to KICKAI, {telegram_name}!

🌟 You're the first team member! Let's get you set up as an admin.

📝 Please provide your details:
💡 Use: /register [name] [phone] admin
```

**Leadership Chat - Unregistered User (Not First):**
```
👋 Welcome to KICKAI Leadership, {telegram_name}!

🤔 I don't see you registered as a team member yet.

📝 Please provide your details so I can add you to the team members collection.

💡 You can use: /register [name] [phone] [role]
```

**Leadership Chat - Registered User (Treated as Team Member):**
```
🤖 KICKAI Commands

👤 {telegram_name} (Team Member)

Leadership Commands:
• /add - Add a new player
• /approve - Approve player registration
• /reject - Reject player registration
• /pending - Show pending registrations
• /announce - Make team announcement

General Commands:
• /help - Show available commands
• /myinfo - Show your team member information
• /status - Check your team member status
• /list - List active players
• /team - Team information

Natural Language:
You can also ask me questions in natural language!
```

## 🏗️ Clean Design Principles

### **Command Context Architecture**

The KICKAI system follows clean software engineering principles to avoid conditional logic and maintain predictable behavior across different chat contexts.

#### **1. Context-Specific Implementations**
Instead of using conditional logic within a single command handler, the system uses separate implementations for different contexts:

```python
# ❌ Avoid: Conditional logic in single handler
@command("/list")
async def handle_list(update, context):
    chat_type = get_chat_type(update.effective_chat.id)
    
    if chat_type == "main":
        # Main chat logic
        players = await get_active_players()
        return format_simple_list(players)
    elif chat_type == "leadership":
        # Leadership chat logic
        players = await get_all_players()
        return format_detailed_list(players)
    else:
        # Error handling
        return "Invalid chat type"
```

```python
# ✅ Prefer: Separate implementations for each context
@command(name="/list", description="List active players", chat_type="main")
async def list_players_main(update, context):
    """List only active players in main chat."""
    players = await get_active_players()
    return format_player_list(players, show_status=False)

@command(name="/list", description="List all players with status", chat_type="leadership")
async def list_players_leadership(update, context):
    """List all players with detailed status in leadership chat."""
    players = await get_all_players()
    return format_player_list(players, show_status=True, show_details=True)
```

#### **2. Command Registration with Context**
Commands are registered with explicit context information:

```python
# Command registry supports context-aware registration
registry.register_command(
    name="/list",
    description="List players",
    handler=list_players_main,
    chat_type="main",
    permission_level=PermissionLevel.PLAYER
)

registry.register_command(
    name="/list", 
    description="List all players with status",
    handler=list_players_leadership,
    chat_type="leadership",
    permission_level=PermissionLevel.LEADERSHIP
)
```

#### **3. Context-Aware Routing**
The system routes commands to the appropriate implementation based on context:

```python
async def route_command(self, command_name: str, chat_type: str, update, context):
    """Route command to context-specific implementation."""
    # Find the appropriate handler for this command and context
    handler = self.registry.get_command_handler(command_name, chat_type)
    
    if handler:
        return await handler(update, context)
    else:
        return await self.fallback_handler(update, context)
```

#### **4. Benefits of This Approach**

**🎯 Predictable Behavior**
- Same command always behaves the same way in the same context
- No hidden conditional logic that could change behavior unexpectedly

**🧹 Clean Code**
- Each implementation has a single responsibility
- Easy to understand and maintain
- No complex if/else chains

**📋 Clear Intent**
- Each implementation clearly states its purpose
- Self-documenting code through function names and docstrings

**🛠️ Maintainable**
- Easy to modify behavior for specific contexts
- Changes to one context don't affect others
- Clear separation of concerns

**🧪 Testable**
- Each implementation can be tested independently
- No need to test complex conditional logic
- Clear test scenarios for each context

**📈 Scalable**
- Easy to add new contexts (e.g., private chat, group chat)
- New commands can follow the same pattern
- Consistent architecture across the system

#### **5. Implementation Examples**

**Example: `/help` Command**
```python
@command(name="/help", description="Show help", chat_type="main")
async def help_main(update, context):
    """Show player-focused help in main chat."""
    return format_help_message(
        context=context,
        show_player_commands=True,
        show_admin_commands=False,
        show_registration_help=True
    )

@command(name="/help", description="Show admin help", chat_type="leadership")
async def help_leadership(update, context):
    """Show admin-focused help in leadership chat."""
    return format_help_message(
        context=context,
        show_player_commands=True,
        show_admin_commands=True,
        show_registration_help=False
    )
```

**Example: `/status` Command**
```python
@command(name="/status", description="Check player status", chat_type="main")
async def status_main(update, context):
    """Check own status in main chat."""
    user_id = update.effective_user.id
    player = await get_player_by_user_id(user_id)
    return format_player_status(player, show_details=False)

@command(name="/status", description="Check any player status", chat_type="leadership")
async def status_leadership(update, context):
    """Check any player's status in leadership chat."""
    phone = context.args[0] if context.args else None
    player = await get_player_by_phone(phone)
    return format_player_status(player, show_details=True)
```

This clean design approach ensures the system is maintainable, testable, and follows software engineering best practices! 🚀