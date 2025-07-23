# Message Formatting Framework & Agent Communication Patterns

**Version:** 5.0  
**Status:** Production Ready  
**Last Updated:** July 2025  
**Architecture:** Plain Text with Emojis - Simple and Reliable

## Overview

This document outlines the centralized message formatting framework and design patterns for consistent bot responses in the KICKAI system, using plain text with emojis for maximum reliability and simplicity.

## Architecture Principles

### 1. **Plain Text with Emojis**
- **No Markdown or HTML formatting** - eliminates parsing errors
- **Emojis for visual appeal** - maintains user engagement
- **Universal compatibility** - works across all platforms
- **Simple and reliable** - no format conversion needed

### 2. **Context-Aware Formatting**
- **Chat type awareness** (main vs leadership)
- **User role integration** (player vs team member vs admin)
- **Dynamic content** based on user permissions
- **Registration flow guidance** for unregistered users

### 3. **Agent Responsibility Model**
- **MessageProcessorAgent**: Handles initial message processing and routing
- **HelpAssistantAgent**: Responsible for all help-related responses
- **PlayerCoordinatorAgent**: Handles player-related responses
- **TeamManagerAgent**: Handles team management responses
- **FinanceManagerAgent**: Handles financial operations
- **PerformanceAnalystAgent**: Handles analytics and insights
- **LearningAgent**: Handles system optimization
- **OnboardingAgent**: Handles new user registration
- **CommandFallbackAgent**: Handles unrecognized commands

## Unified Processing Architecture

### Core Flow

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

### Orchestration Pipeline

```python
# CrewAI orchestration pipeline steps:
1. Intent Classification
2. Complexity Assessment
3. Task Decomposition
4. Agent Routing
5. Task Execution
6. Result Aggregation
```

## Message Formatting Service

### Core Components

```python
@dataclass
class MessageContext:
    user_id: str
    team_id: str
    chat_type: ChatType
    user_name: Optional[str] = None
    is_player: bool = False
    is_team_member: bool = False
    is_admin: bool = False

class MessageFormattingService:
    def format_help_message(self, context: MessageContext, commands_info: Dict[str, Any]) -> str
    def format_welcome_message(self, context: MessageContext) -> str
    def format_error_message(self, error: str, context: Optional[MessageContext] = None) -> str
    def format_success_message(self, message: str, context: Optional[MessageContext] = None) -> str
    def format_info_message(self, message: str, context: Optional[MessageContext] = None) -> str
    def format_player_list(self, players: List[Dict[str, Any]], context: MessageContext) -> str
    def format_team_member_list(self, members: List[Dict[str, Any]], context: MessageContext) -> str
    def format_user_info(self, user_data: Dict[str, Any], context: MessageContext) -> str
```

### Usage Patterns

#### 1. **Help Messages**
```python
# In HelpAssistantAgent
context = MessageContext(
    user_id=user_id,
    team_id=team_id,
    chat_type=chat_type,
    is_player=is_player,
    is_team_member=is_team_member
)

formatter = get_message_formatting_service()
help_message = formatter.format_help_message(context, commands_info)
```

#### 2. **Error Messages**
```python
# In any agent
formatter = get_message_formatting_service()
error_message = formatter.format_error_message("User not found", context)
```

#### 3. **Success Messages**
```python
# In any agent
formatter = get_message_formatting_service()
success_message = formatter.format_success_message("Player registered successfully", context)
```

## Agent Communication Patterns

### 1. **Unified Processing Pattern**
```python
# Both slash commands and natural language use the same pattern:
async def _handle_registered_command(self, update, context, command_name: str):
    # Build the full command with arguments
    args = context.args if context.args else []
    message_text = f"{command_name} {' '.join(args)}".strip()
    
    # Delegate to unified CrewAI processing
    await self._handle_crewai_processing(update, message_text, user_id, chat_id, chat_type, username)

async def _handle_natural_language_message(self, update, context):
    message_text = update.message.text.strip()
    
    # Delegate to unified CrewAI processing
    await self._handle_crewai_processing(update, message_text, user_id, chat_id, chat_type, username)
```

### 2. **Context-Aware Command Implementation**
```python
# Separate implementations for different contexts (clean design)
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

## Message Formatting Standards

### 1. **Emoji Usage**
- **✅ Success**: `✅ Success: message`
- **❌ Error**: `❌ Error: message`
- **ℹ️ Info**: `ℹ️ Info: message`
- **👤 User**: `👤 User Information`
- **👔 Leadership**: `👔 Leadership Commands`
- **🤖 Bot**: `🤖 KICKAI Commands`
- **📋 Lists**: `📋 Team Players`
- **👥 Members**: `👥 Team Members`
- **🎉 Welcome**: `🎉 Welcome to KICKAI`
- **📞 Contact**: `📞 Contact Information`

### 2. **Plain Text Formatting**
- **Headers**: `Header` (no bold formatting)
- **Commands**: `/command` (no backticks)
- **Lists**: `• Item` or `- Item`
- **Sections**: `Section Name:`

### 3. **Chat Type Specific Formatting**

#### Leadership Chat
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

#### Main Chat
```
🤖 KICKAI Commands

👤 {telegram_name} (ID: {player_id})

General Commands:
• /myinfo - Show your player or team member information
• /list - List players and team members

Player Commands:
• /register - Register as a new player

Leadership Commands (available in leadership chat):
• /add - Add a new player with invite link
• /approve - Approve a player for team participation

Natural Language:
You can also ask me questions in natural language!
```

## Benefits of Unified Processing

### 1. **Consistent Security**
- Same permission checking for both input types
- No bypass of permission system through natural language
- Unified access control across all interactions

### 2. **Single Source of Truth**
- No code duplication between paths
- Same agent selection and execution logic
- Consistent behavior regardless of input method

### 3. **Maintainable Architecture**
- Single processing pipeline to maintain
- Easy to add new input methods
- Clean separation of concerns

### 4. **Scalable Design**
- Easy to add new contexts (voice, buttons, etc.)
- Consistent architecture across the system
- Test once, works everywhere

This unified approach ensures the system is secure, maintainable, and provides a consistent user experience across all interaction methods! 🚀 