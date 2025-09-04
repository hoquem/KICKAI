# KICKAI Tool Naming Convention

## Overview

This document defines the comprehensive tool naming convention for the KICKAI 5-Agent CrewAI System. The convention ensures clear, predictable tool names that align with agent responsibilities and eliminate confusion.

## Naming Convention Structure

```
[action]_[entity]_[modifier]

Actions: get, list, create, update, delete, send, mark, record, validate, check, show
Entities: player, member, match, squad, team, status, availability, system, help
Modifiers: self, by_identifier, info, all, active, pending, field, multiple, history, upcoming
```

## Core Principles

1. **CrewAI Semantic First**: Tool names enable intelligent selection through semantic understanding
2. **Intent-Based Naming**: `_self` vs `_by_identifier` patterns for clear intent
3. **Explicit Parameters**: `telegram_username` vs generic `username` for clarity
4. **Action-First**: Start with what the tool does
5. **Entity-Clear**: Specify what it operates on
6. **Modifier-Specific**: Add context when needed
7. **No Hardcoded Routing**: Trust CrewAI's intelligence over brittle routing rules
8. **Predictable**: Agents can infer tool purpose from semantic patterns

## CrewAI Semantic Tool Patterns (NEW 2025)

### Self vs By-Identifier Pattern
**Problem**: Agent confusion between "current user" and "specific lookup" tools
**Solution**: Clear semantic distinction through naming

#### Self Pattern (`_self`)
**Purpose**: For requesting user's own data  
**Usage Context**: `/myinfo`, `/mystatus`, "my availability"  
**Examples**:
- `get_player_self` - Current user's player information
- `get_member_self` - Current user's member/admin information
- `get_player_match_self` - Current user's upcoming matches

#### By-Identifier Pattern (`_by_identifier`) 
**Purpose**: For looking up other users/entities
**Usage Context**: `/info [name]`, `/status [player]`, "John's availability"
**Examples**:
- `get_player_by_identifier` - Look up specific player
- `get_member_by_identifier` - Look up specific team member  
- `get_player_match_by_identifier` - Look up player's matches

### Tool Description Best Practices for CrewAI
```python
@tool("get_player_self")
async def get_player_self(...):
    """Get requesting user's player information and status.
    
    USE THIS FOR:
    - /myinfo command in player context
    - "my status", "my information" queries  
    - Current user asking about themselves
    
    DO NOT USE FOR:
    - Looking up other players
    - Administrative queries about specific players
    - Use get_player_by_identifier for those cases
    """
```

### Parameter Naming for Clarity (Critical for CrewAI Success)
**Problem**: Generic parameter names cause CrewAI confusion and wrong tool selection

**Old (Ambiguous - Causes Issues)**:
- `username` - Could be Telegram username or display name  
- `player_id` - Agent confused this with username "alima_begum"
- `user_id` - Unclear if Telegram ID or internal ID

**New (Explicit - Eliminates Confusion)**:
- `telegram_username` - Explicitly Telegram @username (e.g., "@alima_begum")
- `telegram_id` - Numeric Telegram user ID (e.g., 123456789)
- `player_identifier` - Clear that it's for searching (ID, name, or phone)
- `target_identifier` - When looking up other users by any identifier

**Benefits for CrewAI**:
- Tools select correctly based on parameter clarity
- Agents understand the difference between telegram_id (123456) and telegram_username ("@user")
- Explicit naming prevents parameter misuse and tool confusion

## Complete Tool Catalog (75+ Tools)

### Information Retrieval Tools

#### Player Information (CrewAI Semantic Pattern)
- `get_player_self` - Get requesting user's player information (USE FOR: /myinfo as player)
- `get_player_by_identifier` - Get specific player details by ID/name/phone (USE FOR: /info [name])
- `list_players_all` - All players in system
- `list_players_active` - Active players only
- `list_players_pending` - Players awaiting approval
- `get_player_match_self` - Requesting user's match information
- `get_player_match_by_identifier` - Specific player's match information
- `get_player_attendance_history_self` - Requesting user's attendance record
- `get_player_attendance_history_by_identifier` - Specific player's attendance record
- `get_player_availability_history_self` - Requesting user's availability history
- `get_player_availability_history_by_identifier` - Specific player's availability history

#### Member Information (CrewAI Semantic Pattern)
- `get_member_self` - Get requesting user's member/admin information (USE FOR: /myinfo as admin)
- `get_member_by_identifier` - Get specific member details by ID/name/phone (USE FOR: admin lookup)
- `list_members_all` - All team members
- `list_members_and_players` - Combined listing
- `get_member_update_help` - Member update guidance

### Administrative Actions

#### Player Management
- `create_player` - Add new player with invitation
- `approve_player` - Approve player registration
- `update_player_field` - Update single player field
- `update_player_multiple` - Update multiple player fields
- `get_player_update_help` - Player update guidance

#### Member Management
- `create_member` - Add new team member
- `activate_member` - Activate pending member
- `update_member_field` - Update single member field
- `update_member_multiple` - Update multiple member fields
- `update_member_other` - Update another member's info
- `create_member_role` - Assign role to member
- `remove_member_role` - Remove role from member
- `promote_member_admin` - Promote member to admin

#### Team Operations
- `create_team` - Create new team

### Match & Squad Management

#### Match Operations
- `create_match` - Schedule new match
- `list_matches_all` - All matches
- `list_matches_upcoming` - Future matches
- `get_match_details` - Specific match information
- `record_match_result` - Record match outcome
- `get_match_attendance` - Match attendance data

#### Squad Selection
- `select_squad_match` - Pick squad for match
- `list_squad_available` - Available players for selection

#### Availability & Attendance
- `mark_availability_match` - Set match availability
- `get_availability_player` - Check player availability
- `get_availability_all` - All availability data
- `record_attendance_match` - Log match attendance

### Communication Tools

#### Messaging
- `send_message_player` - Message to specific player
- `send_message_team` - Team-wide message
- `send_announcement_all` - Broadcast announcement
- `send_poll_team` - Create team poll

### System & Help Tools

#### Help System
- `show_help_commands` - List available commands
- `show_help_usage` - Command usage guidance
- `show_help_welcome` - Welcome message
- `show_help_final` - Comprehensive help response

#### System Status
- `check_system_ping` - System connectivity
- `check_system_version` - Version information
- `get_system_commands` - Available system commands
- `get_version_info` - Detailed version info

#### Permission & Access
- `validate_permission_access` - Check user permissions
- `show_permission_denied` - Permission denied message
- `show_command_unavailable` - Command not available message

### Natural Language Processing Tools

#### Intent Recognition
- `analyze_intent_advanced` - Advanced intent analysis
- `extract_entities_text` - Extract entities from text
- `analyze_context_conversation` - Conversation context
- `check_similarity_semantic` - Semantic similarity check
- `recommend_routing_action` - Routing recommendations
- `analyze_context_update` - Update context analysis
- `validate_routing_permissions` - Routing permission validation

## Agent-Specific Tool Assignment

### MESSAGE_PROCESSOR (Manager Agent)
**Role**: Delegation coordinator - no direct tools

### HELP_ASSISTANT  
**Tools**: 15 tools
```
- show_help_commands
- show_help_usage  
- show_help_welcome
- show_help_final
- get_status_my
- get_status_user
- list_players_active
- list_members_and_players
- send_message_team
- send_announcement_all
- send_poll_team
- check_system_ping
- check_system_version
- show_permission_denied
- show_command_unavailable
```

### PLAYER_COORDINATOR
**Tools**: 18 tools
```
- get_player_info
- get_player_current_info
- get_status_my
- get_status_player
- list_players_all
- list_players_active
- get_player_match
- list_members_and_players
- approve_player
- update_player_field
- update_player_multiple
- get_player_update_help
- get_player_attendance_history
- get_player_availability_history
- send_message_player
- show_help_commands
- show_permission_denied
- show_command_unavailable
```

### TEAM_ADMINISTRATOR
**Tools**: 22 tools
```
- create_player
- create_member
- activate_member
- get_member_info
- get_member_current_info
- list_members_all
- list_members_and_players
- update_member_field
- update_member_multiple
- update_member_other
- get_member_update_help
- create_member_role
- remove_member_role
- promote_member_admin
- create_team
- approve_user
- list_users_pending
- list_players_active
- get_status_my
- show_help_commands
- show_permission_denied
- show_command_unavailable
```

### SQUAD_SELECTOR
**Tools**: 20 tools
```
- create_match
- list_matches_all
- list_matches_upcoming
- get_match_details
- record_match_result
- select_squad_match
- list_squad_available
- mark_availability_match
- get_availability_player
- get_availability_all
- record_attendance_match
- get_match_attendance
- get_player_attendance_history
- get_player_availability_history
- list_players_active
- get_status_my
- send_message_team
- show_help_commands
- show_permission_denied
- show_command_unavailable
```

## Implementation Rules

### Tool Function Naming
```python
# ✅ CORRECT - New Convention
@tool("get_player_info", result_as_answer=True)
async def get_player_info(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """Get detailed information about a specific player."""
    return await get_player_info_domain(telegram_id, team_id, username, chat_type)

# Domain function follows same naming
async def get_player_info_domain(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    # Implementation
```

### File Organization
```
kickai/features/[feature]/application/tools/
├── player_info_tools.py      # get_player_*, list_players_*
├── member_admin_tools.py     # create_member, update_member_*
├── match_squad_tools.py      # create_match, select_squad_*
├── communication_tools.py    # send_message_*, send_announcement_*
├── system_help_tools.py      # show_help_*, check_system_*
└── nlp_analysis_tools.py     # analyze_*, validate_*, extract_*
```

### Import Structure
```python
# Feature __init__.py exports
from .application.tools.player_info_tools import (
    get_player_info,
    list_players_active,
    list_players_all
)

from .application.tools.member_admin_tools import (
    create_member,
    update_member_field,
    activate_member
)
```

## Migration Mapping

### Complete Current → New Mapping (Including CrewAI Semantic Patterns)
```
# Status Tools - CrewAI Semantic Pattern
get_player_status_current        → get_player_self
get_player_status                → get_player_by_identifier
get_member_status_current        → get_member_self
get_member_status                → get_member_by_identifier

# Information Tools - CrewAI Semantic Pattern  
get_player_info_current          → get_player_self
get_player_info                  → get_player_by_identifier
get_member_info_current          → get_member_self
get_member_info                  → get_member_by_identifier

# Match Tools - CrewAI Semantic Pattern
get_player_match_current         → get_player_match_self
get_player_match_specific        → get_player_match_by_identifier

# Legacy Mappings (Maintained for Compatibility)
get_my_status                    → get_status_my
get_user_status                  → get_status_user  
add_player                       → create_player
add_team_member_simplified       → create_member
list_team_members_and_players    → list_members_and_players
mark_availability                → mark_availability_match
get_active_players               → list_players_active
get_all_players                  → list_players_all
approve_user                     → approve_player
get_pending_users                → list_users_pending
send_message                     → send_message_team
help_response                    → show_help_commands
FINAL_HELP_RESPONSE              → show_help_final
get_welcome_message              → show_help_welcome
ping                             → check_system_ping
version                          → check_system_version
get_available_commands           → show_help_commands
get_command_help                 → show_help_usage
permission_denied_message        → show_permission_denied
command_not_available            → show_command_unavailable
advanced_intent_recognition      → analyze_intent_advanced
entity_extraction_tool           → extract_entities_text
conversation_context_tool        → analyze_context_conversation
semantic_similarity_tool         → check_similarity_semantic
routing_recommendation_tool      → recommend_routing_action
analyze_update_context           → analyze_context_update
validate_routing_permissions     → validate_routing_permissions
get_availability                 → get_availability_all
get_match_attendance             → get_match_attendance
get_player_attendance_history    → get_player_attendance_history
get_player_availability_history  → get_player_availability_history
record_attendance                → record_attendance_match
send_announcement                → send_announcement_all
send_poll                        → send_poll_team
get_system_available_commands    → get_system_commands
get_version_info                 → get_version_info
create_match                     → create_match
get_available_players_for_match  → list_squad_available
get_match_details                → get_match_details
list_matches                     → list_matches_all
record_match_result              → record_match_result
select_squad                     → select_squad_match
activate_team_member             → activate_member
get_team_members                 → list_members_all
add_team_member_role             → create_member_role
create_team                      → create_team
get_team_member_update_help      → get_member_update_help
promote_team_member_to_admin     → promote_member_admin
remove_team_member_role          → remove_member_role
update_member_info               → update_member_field
update_team_member_field         → update_member_field
update_team_member_multiple_fields → update_member_multiple
get_player_current_info          → get_player_current_info
get_player_update_help           → get_player_update_help
update_player_field              → update_player_field
update_player_multiple_fields    → update_player_multiple
approve_player                   → approve_player
get_player_match                 → get_player_match
```

## Validation Rules

### Tool Name Validation
1. Must follow `[action]_[entity]_[modifier]` pattern
2. Action must be from approved list
3. Entity must be clear and specific
4. Modifier must add meaningful context
5. No duplicate names across system
6. Maximum 3 parts (action_entity_modifier)

### Documentation Requirements
1. Each tool must have clear docstring
2. Parameters must be documented
3. Return type must be specified
4. Usage examples preferred
5. Agent assignment documented

## Benefits

### For Agents
- **Predictable**: Can infer tool names from patterns
- **Clear Intent**: Action verbs make purpose obvious
- **Organized**: Logical grouping by function
- **Efficient**: Reduced tool selection time

### For Developers
- **Consistent**: All tools follow same pattern
- **Maintainable**: Easy to add new tools
- **Searchable**: Tools easy to find
- **Scalable**: Convention grows with system

### For System
- **No Conflicts**: Eliminates naming ambiguity
- **Agent-Friendly**: Names align with agent roles
- **Performance**: Faster tool selection
- **Quality**: Clear naming improves code quality

This comprehensive naming convention ensures the KICKAI 5-Agent system has clean, predictable tool names that enhance agent performance and system maintainability.