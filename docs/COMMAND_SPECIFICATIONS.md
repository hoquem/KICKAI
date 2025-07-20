# KICKAI Command Specifications

This document defines the expected behavior for all KICKAI bot commands across different scenarios, chat types, and user states.

## Table of Contents
- [Command Overview](#command-overview)
- [Chat Types](#chat-types)
- [User States](#user-states)
- [Command Specifications](#command-specifications)
- [Implementation Architecture](#implementation-architecture)
- [Command Implementation & Processing Flow](#command-implementation--processing-flow)
- [Testing Scenarios](#testing-scenarios)

## Command Overview

### Core Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level |
|---------|-------------|-----------|-----------------|------------------|
| `/help` | Show available commands | ✅ | ✅ | PUBLIC |
| `/start` | Initialize bot interaction | ✅ | ✅ | PUBLIC |
| `/register` | Register as a player | ✅ | ❌ | PUBLIC |
| `/myinfo` | Show personal information | ✅ | ✅ | PUBLIC |
| `/status` | Check player/team member status | ✅ | ✅ | PUBLIC |
| `/list` | List players/team members | ✅ | ✅ | PUBLIC |

### Player Management Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level |
|---------|-------------|-----------|-----------------|------------------|
| `/add` | Add a new player | ❌ | ✅ | LEADERSHIP |
| `/approve` | Approve player registration | ❌ | ✅ | LEADERSHIP |
| `/reject` | Reject player registration | ❌ | ✅ | LEADERSHIP |
| `/pending` | Show pending registrations | ❌ | ✅ | LEADERSHIP |

### Team Management Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level |
|---------|-------------|-----------|-----------------|------------------|
| `/team` | Team information | ✅ | ✅ | PUBLIC |
| `/invite` | Generate invitation link | ❌ | ✅ | LEADERSHIP |
| `/announce` | Make team announcement | ❌ | ✅ | LEADERSHIP |

### System Commands
| Command | Description | Main Chat | Leadership Chat | Permission Level |
|---------|-------------|-----------|-----------------|------------------|
| `/health` | System health check | ❌ | ✅ | SYSTEM |
| `/version` | Bot version info | ✅ | ✅ | PUBLIC |
| `/config` | Configuration info | ❌ | ✅ | SYSTEM |

## Chat Types

### Main Chat (`-4829855674`)
- **Purpose**: General team communication
- **Users**: All registered players and team members
- **Commands**: Public commands, player-focused features
- **Context**: `is_leadership_chat: false`

### Leadership Chat (`-4969733370`)
- **Purpose**: Administrative and management functions
- **Users**: Team leaders, administrators, coaches
- **Commands**: All commands including administrative functions
- **Context**: `is_leadership_chat: true`

## User States

### 1. First User (Bot Creator)
- **User ID**: `8148917292` (doods2000)
- **Status**: Team owner, full permissions
- **Access**: All chats, all commands

### 2. Registered Player
- **Status**: Active player in the system
- **Access**: Main chat commands, limited leadership chat access
- **Data**: Player record in Firestore

### 3. Team Member (Non-Player)
- **Status**: Team staff, coach, or administrator
- **Access**: Leadership chat, administrative commands
- **Data**: Team member record in Firestore

### 4. Pending Registration
- **Status**: Registration submitted, awaiting approval
- **Access**: Limited main chat access
- **Data**: Pending player record in Firestore

### 5. Unregistered User
- **Status**: No record in system
- **Access**: Basic commands only
- **Data**: No Firestore record

## Command Specifications

### `/help` Command

#### Implementation Overview

The `/help` command is implemented using a **comprehensive agent-based framework** that provides context-aware help information with proper user validation and registration flows.

**Key Components:**
- **HelpAssistantAgent**: Specialized agent for help processing
- **CommandProcessingService**: Centralized command processing with user validation
- **Help Tools**: 5 specialized tools for different operations
- **Registry Integration**: Uses agent and tool registries for discovery

#### Architecture Implementation

**1. Help Assistant Agent** (`src/features/shared/domain/agents/help_assistant_agent.py`)
```python
@register_agent_decorator(
    agent_id="help_assistant",
    agent_type=AgentType.HELP_ASSISTANT,
    category=AgentCategory.CORE,
    description="Provides context-aware help information to KICKAI users",
    tools=[
        "get_user_status",
        "get_available_commands", 
        "format_help_message",
        "process_user_registration_flow",
        "get_user_display_info"
    ],
    feature_module="shared"
)
class HelpAssistantAgent:
    """Help Assistant Agent for processing help requests."""
```

**2. Command Processing Service** (`src/features/shared/domain/services/command_processing_service.py`)
- **UserContext**: Complete user context with all necessary information
- **CommandResponse**: Standardized response format
- **User Validation**: Comprehensive validation flows
- **Registration Handling**: Proper flows for unregistered users

**3. Help Tools** (`src/features/shared/domain/tools/help_tools.py`)
- **get_user_status**: User status validation
- **get_available_commands**: Command availability checking
- **format_help_message**: Context-aware message formatting
- **process_user_registration_flow**: Registration flow handling
- **get_user_display_info**: User display information

#### Context-Aware Behavior Design

The `/help` command provides **context-aware** information based on:

1. **Chat Type**: Main chat vs Leadership chat
2. **User Status**: Player vs Team Member vs Unregistered
3. **User Permissions**: What commands the user can actually execute
4. **Registration Flow**: Proper guidance for unregistered users

#### Agent Implementation Strategy

**How the Help Assistant Agent Works:**

1. **User Context Building**: Builds complete user context with permissions and data
2. **User Status Validation**: Validates user status and handles registration flows
3. **Command Discovery**: Queries command registry for available commands
4. **Context-Aware Formatting**: Formats help message based on user context
5. **Registration Flow Handling**: Provides appropriate guidance for unregistered users

**Agent Task Description:**
```
You are a help assistant for the KICKAI football team management system.

CONTEXT:
- Chat Type: {main_chat|leadership_chat}
- User ID: {user_id}
- Team ID: {team_id}
- Telegram Username: {telegram_username}
- Telegram Name: {telegram_name}

AVAILABLE TOOLS:
- get_user_status: Get current user's player/team member status
- get_available_commands: Get list of commands available to this user
- format_help_message: Format help message based on context
- process_user_registration_flow: Handle user registration flows
- get_user_display_info: Get user display information for message formatting

TASK:
1. Determine user's current status using get_user_status
2. If user is not registered:
   - For main_chat: Ask them to contact leadership team to add them as a player
   - For leadership_chat: 
     - If first user: Welcome them and ask for admin registration
     - If not first user: Ask them to provide details for team member registration
3. If user is registered:
   - Get available commands using get_available_commands
   - Get user display info using get_user_display_info
   - Format appropriate help message using format_help_message
4. Return contextually appropriate help information

IMPORTANT RULES:
- Internally refer to users by their telegram ID and player/member ID
- In messages to users, always refer to them using their telegram name and player/member ID
- When displaying user's actual name, use their actual name, not telegram name
- Always validate user status before providing help
- Provide clear, actionable guidance for unregistered users
- Format messages with proper Markdown for Telegram
```

#### Expected Behavior by Chat Type and User Status

**Main Chat - Unregistered User:**
```
👋 Welcome to KICKAI, {telegram_name}!

🤔 I don't see you registered as a player yet.

📞 Please contact a member of the leadership team to add you as a player to this team.

💡 Once you're registered, you'll be able to use all player commands!
```

**Main Chat - Registered Player:**
```
🤖 KICKAI Commands

👤 {telegram_name} (ID: {player_id})

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

**Main Chat - Team Member (Non-Player):**
```
🤖 KICKAI Commands

👤 {telegram_name} (ID: {member_id})

Note: You're registered as a team member, not a player.

Available Commands:
• /help - Show available commands
• /myinfo - Show your team member information
• /status - Check your team member status
• /list - List active players
• /team - Team information

For player registration, contact team leadership.

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

**Leadership Chat - Registered Team Member:**
```
👔 KICKAI Leadership Commands

👤 {telegram_name} (ID: {member_id})

Player Management:
• /register - Register new player with name, phone, position
• /add - Add new player to team roster
• /list - List all players with their status
• /status - Check player status by phone number
• /myinfo - Check your admin information

Team Management:
• /help - Show this help message
• /start - Start the bot

Natural Language:
You can also ask me questions in natural language!
```

**Specific Command Help** (e.g., `/help register`):
```
📋 /register Command Help

Description: Register as a new player or team member

Usage:
• /register [name] [phone] [position] - Register as a player
• /register [name] [phone] admin - Register as admin (leadership only)

Examples:
• /register John Smith 07123456789 Forward
• /register Jane Doe 07987654321 admin

Permission Required: PUBLIC
Available in: Main Chat, Leadership Chat
```

#### Command Availability Matrix

| Command | Main Chat | Leadership Chat | Unregistered | Player | Team Member |
|---------|-----------|-----------------|--------------|--------|-------------|
| `/help` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/start` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/register` | ✅ | ❌ | ✅ | ✅ | ❌ |
| `/myinfo` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/status` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/list` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/team` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/add` | ❌ | ✅ | ❌ | ❌ | ✅ |
| `/approve` | ❌ | ✅ | ❌ | ❌ | ✅ |
| `/reject` | ❌ | ✅ | ❌ | ❌ | ✅ |
| `/pending` | ❌ | ✅ | ❌ | ❌ | ✅ |
| `/invite` | ❌ | ✅ | ❌ | ❌ | ✅ |
| `/announce` | ❌ | ✅ | ❌ | ❌ | ✅ |
| `/health` | ❌ | ✅ | ❌ | ❌ | ✅ |
| `/version` | ✅ | ✅ | ✅ | ✅ | ✅ |

#### Implementation Requirements

**Agent Tools Implementation:**

1. **`get_user_status` Tool:**
   ```python
   @tool("get_user_status")
   def get_user_status_tool(user_id: str, team_id: str, chat_type: str) -> str:
       """Get current user's player/team member status."""
       # Returns JSON with user status information
   ```

2. **`get_available_commands` Tool:**
   ```python
   @tool("get_available_commands")
   def get_available_commands_tool(chat_type: str, user_id: str, team_id: str) -> str:
       """Get list of commands available to this user."""
       # Returns JSON with available commands
   ```

3. **`format_help_message` Tool:**
   ```python
   @tool("format_help_message")
   def format_help_message_tool(chat_type: str, user_id: str, team_id: str, user_status: str) -> str:
       """Format help message based on context."""
       # Returns formatted help message
   ```

4. **`process_user_registration_flow` Tool:**
   ```python
   @tool("process_user_registration_flow")
   def process_user_registration_flow_tool(chat_type: str, user_id: str, team_id: str, user_status: str) -> str:
       """Process user registration flow based on user status and chat type."""
       # Returns registration flow message
   ```

5. **`get_user_display_info` Tool:**
   ```python
   @tool("get_user_display_info")
   def get_user_display_info_tool(user_id: str, team_id: str, user_status: str) -> str:
       """Get user display information for message formatting."""
       # Returns JSON with user display information
   ```

**Registry Integration:**
- **Agent Registry**: HelpAssistantAgent registered with `@register_agent_decorator`
- **Tool Registry**: All 5 help tools auto-discovered and registered
- **Command Registry**: Commands registered with permission levels and metadata
- **Registry Manager**: Coordinates all registries for single source of truth

**User Validation Flows:**
- **Main Chat**: Unregistered users directed to contact leadership
- **Leadership Chat**: First user gets admin setup flow
- **Leadership Chat**: Non-first users get team member registration flow
- **Registered Users**: Get context-aware help based on their role

**Error Handling:**
- **Graceful degradation**: Fallback messages if tools fail
- **User-friendly guidance**: Clear next steps for all scenarios
- **Context preservation**: Maintains user context across operations
- **Logging**: Comprehensive logging for debugging and monitoring

**Message Formatting:**
- **Markdown support**: Proper Telegram Markdown formatting
- **Emoji usage**: Consistent emoji usage for better UX
- **User personalization**: Uses actual names and IDs
- **Context awareness**: Different formatting for different chat types

#### Command Handler Implementation

**Help Command Handler** (`src/features/shared/application/commands/help_commands.py`)
```python
@command("/help", "Show available commands and help information",
         command_type=CommandType.SLASH_COMMAND,
         permission_level=PermissionLevel.PUBLIC,
         feature="shared",
         aliases=["/h", "/commands"],
         examples=["/help", "/help register", "/help add"],
         help_text="Show available commands. Use /help [command] for detailed help on a specific command.")
async def handle_help_command(update: Update, context: CallbackContext) -> None:
    """Handle /help command with context-aware help information using the new framework."""
    
    # Extract command parameters
    command_args = context.args if context.args else []
    specific_command = command_args[0] if command_args else None
    
    # Create help assistant agent
    help_agent = HelpAssistantAgent()
    
    if specific_command:
        # Get help for specific command
        response = await help_agent.process_specific_command_help(
            update.effective_user.id,
            update.effective_chat.id,
            specific_command
        )
    else:
        # Get general help
        response = await help_agent.process_general_help(
            update.effective_user.id,
            update.effective_chat.id
        )
    
    # Send response
    await update.message.reply_text(response, parse_mode='Markdown')
```

**Key Features:**
- **Context-aware processing**: Different responses based on chat type and user status
- **Specific command help**: Support for `/help [command]` syntax
- **Agent-based processing**: Uses HelpAssistantAgent for all processing
- **Error handling**: Graceful fallback if agent processing fails
- **Markdown formatting**: Proper Telegram message formatting

#### Testing Scenarios

**Scenario 1: Unregistered User in Main Chat**
- **Input**: `/help`
- **Expected**: Welcome message + contact leadership guidance
- **Collection**: `kickai_KTI_players` (empty)
- **Agent Flow**: get_user_status → process_user_registration_flow

**Scenario 2: Registered Player in Main Chat**
- **Input**: `/help`
- **Expected**: Player-focused commands with user info
- **Collection**: `kickai_KTI_players` (user found)
- **Agent Flow**: get_user_status → get_available_commands → get_user_display_info → format_help_message

**Scenario 3: Team Member in Leadership Chat**
- **Input**: `/help`
- **Expected**: Leadership commands with admin info
- **Collection**: `kickai_KTI_team_members` (user found)
- **Agent Flow**: get_user_status → get_available_commands → get_user_display_info → format_help_message

**Scenario 4: First User in Leadership Chat**
- **Input**: `/help`
- **Expected**: Admin setup flow
- **Collection**: `kickai_KTI_team_members` (empty)
- **Agent Flow**: get_user_status → process_user_registration_flow (first user flow)

**Scenario 5: Specific Command Help**
- **Input**: `/help register`
- **Expected**: Detailed help for register command
- **Agent Flow**: get_user_status → get_available_commands → format_help_message (specific command)

#### Registry Framework Integration

**Agent Registry Integration:**
```python
# HelpAssistantAgent is registered in the agent registry
@register_agent_decorator(
    agent_id="help_assistant",
    agent_type=AgentType.HELP_ASSISTANT,
    category=AgentCategory.CORE,
    description="Provides context-aware help information to KICKAI users",
    tools=[
        "get_user_status",
        "get_available_commands", 
        "format_help_message",
        "process_user_registration_flow",
        "get_user_display_info"
    ],
    feature_module="shared"
)
```

**Tool Registry Integration:**
```python
# All help tools are auto-discovered and registered
# Tools are categorized by type and feature
# Legacy compatibility maintained with GLOBAL_TOOL_REGISTRY
```

**Registry Manager Coordination:**
```python
# Registry manager coordinates all registries
manager = get_registry_manager()
manager.initialize_registries()

# Health check validates all dependencies
health = manager.health_check()

# Feature overview shows all help-related components
help_overview = manager.get_feature_overview("shared")
```

**Benefits of Registry Framework:**
- **Single source of truth**: All components registered centrally
- **Auto-discovery**: No manual registration required
- **Dependency validation**: Cross-registry dependency checking
- **Health monitoring**: Comprehensive system health checks
- **Scalability**: Easy to add new components and features
- **Input**: `/help`
- **Expected**: Full leadership commands
- **Collection**: `kickai_KTI_team_members` (user found)

**Scenario 4: Unregistered User in Leadership Chat**
- **Input**: `/help`
- **Expected**: Access denied message
- **Collection**: `kickai_KTI_team_members` (empty)

### `/start` Command

#### Expected Behavior

**Main Chat:**
```
👋 Welcome to KICKAI for KickAI Testing!

🤖 KICKAI v1.0.0 is your AI-powered football team assistant.
- Organize matches, manage attendance, and more.
- Use /help to see what you can do!

Let's kick off a smarter season! ⚽️
```

**Leadership Chat:**
```
👔 KICKAI Leadership for KickAI Testing is now online!

🤖 KICKAI v1.0.0 is ready to assist with team management.
- Access admin commands and team oversight.
- Use /help for leadership commands.

Leadership dashboard is active! 🏆
```

### `/register` Command

#### Expected Behavior

**Main Chat - Unregistered User:**
```
📝 Player Registration

To register as a player, please provide:
• Your full name
• Phone number (format: 07XXXXXXXXX)
• Preferred position (Forward, Midfielder, Defender, Goalkeeper)
• FA eligibility (yes/no)

Example: /register John Smith 07123456789 Forward yes

Your registration will be reviewed by team leadership.
```

**Main Chat - Already Registered:**
```
❌ You are already registered as a player.

Use /myinfo to view your current information.
Use /status to check your player status.
```

**Leadership Chat:**
```
❌ Registration is only available in the main team chat.

Please use the main chat for player registration.
```

### `/myinfo` Command

#### Expected Behavior by User State

**First User - Main Chat:**
```
👤 Player Information

Name: doods2000
Player ID: DO001
Status: Active
Position: Not specified
Phone: Not specified
Team: KickAI Testing
Registration Date: 2025-07-13

Use /status to check your current status.
```

**First User - Leadership Chat:**
```
👔 Team Member Information

Name: doods2000
Role: Team Owner
Status: Active
Team: KickAI Testing
Member Since: 2025-07-13

Administrative Access: Full
```

**Registered Player - Main Chat:**
```
👤 Player Information

Name: [Player Name]
Player ID: [Player ID]
Status: Active
Position: [Position]
Phone: [Phone Number]
Team: KickAI Testing
Registration Date: [Date]

Use /status to check your current status.
```

**Unregistered User - Main Chat:**
```
❌ You are not registered as a player.

Use /register to create your player account.
Use /help to see available commands.
```

### `/status` Command

#### Expected Behavior by User State

**Registered Player - Main Chat:**
```
📊 Player Status

Name: [Player Name]
Player ID: [Player ID]
Status: Active
Position: [Position]
Phone: [Phone Number]
Team: KickAI Testing
Registration Date: [Date]

Recent Activity: [Last match/activity]
```

**Registered Player - Leadership Chat:**
```
📊 Team Member Status

Name: [Player Name]
Role: Player
Status: Active
Team: KickAI Testing
Member Since: [Date]

Player Details:
• Player ID: [Player ID]
• Position: [Position]
• Phone: [Phone Number]
```

**Unregistered User - Main Chat:**
```
❌ You are not registered as a player.

Use /register to create your player account.
```

**Unregistered User - Leadership Chat:**
```
❌ You are not registered as a team member.

Contact team leadership for access.
```

### `/list` Command

#### Expected Behavior by Chat Type

**Main Chat:**
```
📋 Active Players

• DO001 - doods2000 (Not specified)
• [Player ID] - [Name] ([Position])

Total: [X] active players

Use /status [player_id] to check specific player status.
```

**Leadership Chat:**
```
📋 All Players and Team Members

Active Players:
• DO001 - doods2000 (Not specified) - 07XXXXXXXXX
• [Player ID] - [Name] ([Position]) - [Phone]

Pending Registrations:
• [Player ID] - [Name] ([Position]) - Awaiting approval

Team Members:
• [Member ID] - [Name] ([Role]) - [Phone]

Total: [X] players, [Y] team members, [Z] pending
```

### `/add` Command

#### Expected Behavior

**Main Chat:**
```
❌ This command is only available in the leadership chat.

Contact team leadership to add new players.
```

**Leadership Chat - Valid Input:**
```
✅ Player Added Successfully

Name: John Smith
Player ID: JS001
Position: Forward
Phone: 07123456789
Status: Active
Team: KickAI Testing

The player has been added to the team roster.
```

**Leadership Chat - Invalid Input:**
```
❌ Invalid input format.

Usage: /add [name] [phone] [position] [fa_eligible]

Example: /add John Smith 07123456789 Forward true
```

### `/approve` Command

#### Expected Behavior

**Main Chat:**
```
❌ This command is only available in the leadership chat.

Contact team leadership for player approval.
```

**Leadership Chat - Valid Player ID:**
```
✅ Player Approved

Player ID: JS001
Name: John Smith
Status: Active → Approved

The player can now participate in team activities.
```

**Leadership Chat - Invalid Player ID:**
```
❌ Player not found.

Use /pending to see players awaiting approval.
Use /list to see all players.
```

### `/pending` Command

#### Expected Behavior

**Main Chat:**
```
❌ This command is only available in the leadership chat.

Contact team leadership to view pending registrations.
```

**Leadership Chat - With Pending Players:**
```
⏳ Pending Registrations

• JS001 - John Smith (Forward) - 07123456789
• AB002 - Alice Brown (Midfielder) - 07987654321

Total: 2 pending registrations

Use /approve [player_id] to approve
Use /reject [player_id] [reason] to reject
```

**Leadership Chat - No Pending Players:**
```
✅ No pending registrations

All player registrations have been processed.
```

### `/team` Command

#### Expected Behavior

**Main Chat:**
```
🏆 Team Information

Team: KickAI Testing
League: Test League - Division 1
Home Pitch: Test Stadium
Division: Division 1

Current Squad: [X] players
Team Status: Active

Use /list to see all players.
```

**Leadership Chat:**
```
🏆 Team Information

Team: KickAI Testing
League: Test League - Division 1
Home Pitch: Test Stadium
Division: Division 1

Current Squad: [X] players
Team Members: [Y] staff
Team Status: Active

Budget: £[Amount]
Payment Status: [Enabled/Disabled]

Use /list to see all players and team members.
```

### `/invite` Command

#### Expected Behavior

**Main Chat:**
```
❌ This command is only available in the leadership chat.

Contact team leadership to generate invitations.
```

**Leadership Chat:**
```
🔗 Team Invitation Link

Invitation Link: https://t.me/KickAITesting_bot?start=invite_[code]

This link can be shared with potential new players.
The link expires in 24 hours.

Use /add to directly add players to the team.
```

### `/health` Command

#### Expected Behavior

**Main Chat:**
```
❌ This command is only available in the leadership chat.

Contact team leadership for system status.
```

**Leadership Chat:**
```
🏥 System Health Check

Bot Status: ✅ Online
Database: ✅ Connected
LLM Service: ✅ Available
CrewAI Agents: ✅ Active

Active Agents: 11/11
Last Health Check: [Timestamp]

System is healthy and operational.
```

### `/version` Command

#### Expected Behavior

**All Chats:**
```
📦 KICKAI Version Information

Version: v1.0.0
Build Date: 2025-07-19
Python Version: 3.11.13
CrewAI Version: [Version]
Telegram Bot API: [Version]

For support, contact team leadership.
```

## Implementation Architecture

### 🏗️ **System Architecture Principles**

#### **1. Single Source of Truth**
- **Command Definitions**: All commands must be defined in their respective feature modules under `src/features/*/application/commands/`
- **Command Registry**: Centralized command discovery and metadata management in `src/core/command_registry.py`
- **Team Configuration**: Team IDs and settings retrieved from Firestore, never hardcoded
- **User Data**: All user information retrieved from Firestore collections, no local caching

#### **2. Modular Feature-Based Implementation**
```
src/features/
├── player_registration/
│   ├── application/commands/     # Command handlers
│   ├── domain/tools/            # Business logic tools
│   ├── infrastructure/          # Data access layer
│   └── tests/                   # Feature-specific tests
├── team_administration/
├── communication/
└── shared/                      # Cross-cutting concerns
```

**Architecture Rules:**
- ✅ Commands defined in feature modules
- ✅ Business logic in domain tools
- ✅ Data access in infrastructure layer
- ❌ No cross-feature dependencies
- ❌ No hardcoded values in any layer

#### **3. Command Registry System**
```python
# Command registration in feature modules
@command("/help", "Show available commands", 
         permission_level=PermissionLevel.PUBLIC,
         feature="shared",
         examples=["/help", "/help register"])

# Auto-discovery by command registry
registry.auto_discover_commands()  # Scans all feature modules
```

**Registry Responsibilities:**
- **Command Discovery**: Automatically find commands in feature modules
- **Permission Management**: Track command access levels
- **Metadata Storage**: Store descriptions, examples, feature associations
- **Context Filtering**: Filter commands by chat type and user permissions

#### **4. No Hardcoding Policy**
**❌ FORBIDDEN:**
```python
# WRONG - Hardcoded team ID
team_id = "KTI"

# WRONG - Hardcoded command list
commands = ["/help", "/start", "/register"]

# WRONG - Hardcoded chat IDs
main_chat = "-4829855674"
```

**✅ REQUIRED:**
```python
# RIGHT - Dynamic team ID from context
team_id = execution_context.get("team_id")

# RIGHT - Commands from registry
commands = registry.list_all_commands()

# RIGHT - Chat IDs from configuration
main_chat = team_config.main_chat_id
```

### 🤖 **Agent Configuration & Prompts**

#### **Agent Prompt Structure**
Each CrewAI agent must receive the following context and instructions:

```python
AGENT_PROMPT_TEMPLATE = """
You are a {role} agent for the KICKAI football team management system.

## SYSTEM CONTEXT
- Team ID: {team_id} (retrieved from Firestore)
- Chat Type: {chat_type} (main_chat or leadership_chat)
- User ID: {user_id}
- User Role: {user_role}

## ARCHITECTURE RULES
1. SINGLE SOURCE OF TRUTH: All data comes from Firestore collections
2. NO HARDCODING: Never use hardcoded team IDs, chat IDs, or user data
3. CONTEXT-AWARE: Responses must adapt to chat type and user permissions
4. MODULAR DESIGN: Use tools from the appropriate feature modules

## AVAILABLE TOOLS
{available_tools}

## COMMAND PROCESSING RULES
1. Always check user permissions before executing commands
2. Use context variables for team_id, chat_type, user_id
3. Return responses in the exact format specified in the command specifications
4. Handle errors gracefully with clear, helpful messages

## RESPONSE FORMATTING
- Use Markdown formatting
- Include appropriate emojis
- Keep responses concise but informative
- Provide clear next steps when applicable

## ERROR HANDLING
- Permission denied: "❌ You don't have permission to use this command."
- Invalid input: "❌ Invalid input format. Usage: /command [parameters]"
- System error: "❌ An error occurred. Please try again or contact support."

## COMMAND SPECIFICATIONS
{command_specifications}

Your task: {task_description}
"""
```

#### **Context Variables for Agents**
```python
execution_context = {
    "user_id": "8148917292",
    "team_id": "KTI",  # From Firestore, not hardcoded
    "chat_id": "-4829855674",
    "is_leadership_chat": False,
    "username": "doods2000",
    "message_text": "/list",
    "user_role": "player",  # player, team_member, admin
    "permission_level": "PUBLIC"  # PUBLIC, LEADERSHIP, SYSTEM
}
```

#### **Tool Configuration**
```python
# Tools must implement configure_with_context
class GetAllPlayersTool(BaseTool):
    def configure_with_context(self, context: Dict[str, Any]):
        self.team_id = context.get("team_id")
        self.is_leadership_chat = context.get("is_leadership_chat")
        self.user_id = context.get("user_id")
    
    def _run(self, **kwargs):
        # Use self.team_id from context, not hardcoded
        players = await self.player_repository.get_players_by_team(self.team_id)
        return self.format_response(players, self.is_leadership_chat)
```

### 🔧 **Implementation Guidelines**

#### **1. Command Handler Implementation**
```python
# In src/features/shared/application/commands/help_commands.py
@command("/help", "Show available commands", 
         permission_level=PermissionLevel.PUBLIC,
         feature="shared")
async def handle_help_command(update, context):
    """Handle /help command with context-aware responses."""
    
    # Get context from execution environment
    execution_context = {
        "user_id": str(update.effective_user.id),
        "team_id": context.get("team_id"),  # From Firestore
        "chat_id": str(update.effective_chat.id),
        "is_leadership_chat": context.get("is_leadership_chat"),
        "username": update.effective_user.username
    }
    
    # Delegate to CrewAI agent with proper context
    return await crewai_system.execute_task(
        message_text="/help",
        execution_context=execution_context
    )
```

#### **2. Tool Implementation**
```python
# In src/features/player_registration/domain/tools/player_tools.py
class GetMyStatusTool(BaseTool):
    name = "get_my_status"
    description = "Get the current user's player/team member status"
    
    def configure_with_context(self, context: Dict[str, Any]):
        """Configure tool with execution context."""
        self.team_id = context.get("team_id")
        self.user_id = context.get("user_id")
        self.is_leadership_chat = context.get("is_leadership_chat")
        
        if not self.team_id:
            raise ValueError("Team ID is required from context")
    
    async def _run(self, **kwargs):
        """Execute tool with context-aware logic."""
        try:
            if self.is_leadership_chat:
                # Get team member info
                member = await self.team_member_repository.get_by_user_id(
                    self.user_id, self.team_id
                )
                return self.format_team_member_status(member)
            else:
                # Get player info
                player = await self.player_repository.get_by_user_id(
                    self.user_id, self.team_id
                )
                return self.format_player_status(player)
        except Exception as e:
            logger.error(f"Error in GetMyStatusTool: {e}")
            return "❌ Unable to retrieve your status. Please try again."
```

#### **3. Data Access Layer**
```python
# In src/features/player_registration/infrastructure/firebase_player_repository.py
class FirebasePlayerRepository(PlayerRepositoryInterface):
    def __init__(self, firebase_client):
        self.firebase_client = firebase_client
        self.collection_name = "kickai_players"  # Single source of truth
    
    async def get_by_user_id(self, user_id: str, team_id: str) -> Optional[Player]:
        """Get player by user ID and team ID."""
        try:
            # Query by user_id and team_id (no hardcoding)
            query = self.firebase_client.collection(self.collection_name)
            query = query.where("user_id", "==", user_id)
            query = query.where("team_id", "==", team_id)
            
            docs = await query.get()
            if docs:
                return Player.from_dict(docs[0].to_dict())
            return None
        except Exception as e:
            logger.error(f"Error retrieving player: {e}")
            raise PlayerRepositoryError(f"Failed to retrieve player: {e}")
```

### 📚 **Documentation Requirements**

#### **Code Documentation**
```python
"""
Command Handler: /help

Purpose: Show available commands based on chat type and user permissions
Architecture: Uses command registry for single source of truth
Context: Requires team_id, chat_type, user_permissions
Tools: Uses help formatting tools from shared module
Response: Context-aware command list with proper formatting

Specification Reference: docs/COMMAND_SPECIFICATIONS.md#help-command
"""
```

#### **Agent Documentation**
```python
"""
Agent: Player Coordinator

Role: Handle player-related commands and queries
Context Required: team_id, user_id, chat_type, permission_level
Tools: GetMyStatusTool, GetPlayerStatusTool, GetAllPlayersTool
Architecture: Uses modular feature-based design
Data Source: kickai_players Firestore collection

Specification Reference: docs/COMMAND_SPECIFICATIONS.md#implementation-architecture
"""
```

This implementation architecture ensures:
- **Single source of truth** for all command definitions and data
- **Modular, feature-based** implementation without cross-dependencies
- **No hardcoding** of team IDs, chat IDs, or user data
- **Context-aware** responses based on chat type and user permissions
- **Proper error handling** with clear, helpful messages
- **Consistent formatting** across all commands and responses

## Command Implementation & Processing Flow

### 🏗️ **Command Implementation Guidelines**

#### **1. Command Definition Pattern**
All commands must follow this implementation pattern:

```python
@command("/command_name", "Command description", 
         permission_level=PermissionLevel.PUBLIC,
         feature="feature_name",
         examples=["/command_name", "/command_name param"])
def handle_command_name(update, context):
    """Handle /command_name command."""
    # Implementation here
    pass
```

#### **2. Tool Implementation Pattern**
All tools must implement context configuration:

```python
class MyTool(BaseTool):
    def __init__(self):
        super().__init__(name="my_tool", description="Tool description")
        # Don't set _context during initialization
        # It will be set during execution via configure_with_context
    
    def configure_with_context(self, context: Dict[str, Any]):
        """Configure tool with execution context."""
        self._context = context
    
    def _run(self, *args, **kwargs) -> str:
        """Tool execution using context."""
        team_id = self._context.get('team_id')
        user_id = self._context.get('user_id')
        # Use context for proper execution
        return "Tool result"
```

#### **3. Agent Configuration Pattern**
Agents must properly configure tools with context:

```python
def _configure_tools_with_context(self, context: Dict[str, Any]) -> None:
    """Configure all tools with execution context."""
    for tool in self.tools:
        if hasattr(tool, 'configure_with_context'):
            tool.configure_with_context(context)
```

### 🔄 **Command Processing Flow**

#### **Sequence Diagram**
```
User → Telegram Bot → Command Handler → CrewAI System → Agent → Tool → Response
  ↓         ↓              ↓              ↓           ↓      ↓       ↓
Context   Context      Context        Context     Context  Context  Context
```

#### **Object Interaction Diagram**
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │ Telegram Bot │    │ CrewAI      │    │   Tool      │
│             │    │              │    │ System      │    │             │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │ Command           │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ Create Context    │                   │
       │                   │──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ Configure Tools   │
       │                   │                   │──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ Execute Task      │
       │                   │                   │──────────────────▶│
       │                   │                   │                   │
       │                   │                   │                   │ Return Result
       │                   │                   │◀──────────────────│
       │                   │                   │                   │
       │                   │◀──────────────────│                   │
       │                   │                   │                   │
       │◀──────────────────│                   │                   │
       │                   │                   │                   │
```

### 🚫 **Common Anti-Patterns to Avoid**

#### **1. Hardcoded Command Definitions**
❌ **WRONG**: Hardcoding command definitions in utility files
```python
# src/utils/id_processor.py - WRONG!
self.command_patterns = {
    '/approve': {'description': 'Approve player', ...},
    '/register': {'description': 'Register player', ...},
    # ... more hardcoded commands
}
```

✅ **CORRECT**: Define commands in feature modules
```python
# src/features/player_registration/application/commands/player_commands.py - CORRECT!
@command("/approve", "Approve a player registration")
def handle_approve_command(update, context):
    # Implementation here
    pass
```

#### **2. Missing Context Configuration**
❌ **WRONG**: Tools not receiving execution context
```python
class MyTool(BaseTool):
    def _run(self, *args, **kwargs) -> str:
        # No access to team_id, user_id, etc.
        return "Result without context"
```

✅ **CORRECT**: Tools properly configured with context
```python
class MyTool(BaseTool):
    def configure_with_context(self, context: Dict[str, Any]):
        self._context = context
    
    def _run(self, *args, **kwargs) -> str:
        team_id = self._context.get('team_id')
        user_id = self._context.get('user_id')
        return f"Result for team {team_id}, user {user_id}"
```

#### **3. Direct Command Handlers**
❌ **WRONG**: Implementing direct handlers in bot code
```python
# In telegram_bot_service.py - WRONG!
def _handle_help_command(self, update, context):
    # Direct implementation bypassing CrewAI
    return "Help information"
```

✅ **CORRECT**: Delegate to CrewAI agents
```python
# In telegram_bot_service.py - CORRECT!
def _handle_registered_command(self, update, context):
    # Delegate to CrewAI for processing
    return await self._handle_crewai_processing(update, context)
```

### 🔧 **Context Flow Implementation**

#### **1. Context Creation**
```python
def _create_execution_context(self, update, context) -> Dict[str, Any]:
    """Create execution context for CrewAI processing."""
    return {
        'user_id': str(update.effective_user.id),
        'team_id': self._get_team_id_from_firestore(),  # Dynamic, not hardcoded
        'chat_id': str(update.effective_chat.id),
        'is_leadership_chat': self._is_leadership_chat(update.effective_chat.id),
        'username': update.effective_user.username,
        'message_text': update.message.text
    }
```

#### **2. Context Propagation**
```python
def _configure_tools_with_context(self, context: Dict[str, Any]) -> None:
    """Configure all tools with execution context."""
    for agent in self.agents.values():
        for tool in agent.get_tools():
            if hasattr(tool, 'configure_with_context'):
                tool.configure_with_context(context)
```

#### **3. Context Usage in Tools**
```python
def _run(self, *args, **kwargs) -> str:
    """Tool execution using context."""
    if not hasattr(self, '_context'):
        return "❌ Error: Tool not properly configured with context"
    
    team_id = self._context.get('team_id')
    user_id = self._context.get('user_id')
    is_leadership_chat = self._context.get('is_leadership_chat', False)
    
    # Use context for proper execution
    return f"Result for team {team_id}, user {user_id}"
```

### 📋 **Implementation Checklist**

- [ ] **Commands defined in feature modules** (not utility files)
- [ ] **Tools implement `configure_with_context`** method
- [ ] **Agents configure tools with context** before execution
- [ ] **No hardcoded team IDs** - read from Firestore
- [ ] **Context-aware responses** based on chat type
- [ ] **Proper error handling** with context information
- [ ] **Single source of truth** for all command definitions
- [ ] **CrewAI agents handle processing** (not direct handlers) 