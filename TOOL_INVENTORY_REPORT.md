# Tool Inventory Audit Report

## Executive Summary

The KICKAI system has **31 implemented tools** with **10 assigned to agents** and **21 unused tools** that can be safely deleted. There are **7 missing tools** that are referenced in `agents.yaml` but not implemented.

## Tool Statistics

- **Total Tools**: 31
- **Assigned Tools**: 10 (32%)
- **Unused Tools**: 21 (68%)
- **Missing Tools**: 7

## Tool Categories

| Category | Count | Assigned | Unused |
|----------|-------|----------|--------|
| **shared** | 8 | 2 | 6 |
| **player_registration** | 7 | 4 | 3 |
| **team_administration** | 6 | 0 | 6 |
| **system_infrastructure** | 5 | 0 | 5 |
| **match_management** | 4 | 4 | 0 |
| **communication** | 1 | 0 | 1 |

## Assigned Tools (10)

### message_processor
- ✅ `get_available_commands` (shared)
- ✅ `get_active_players` (player_registration)
- ✅ `get_all_players` (match_management)
- ✅ `get_my_status` (player_registration)

### help_assistant
- ✅ `get_available_commands` (shared)
- ✅ `get_command_help` (shared)

### player_coordinator
- ✅ `get_my_status` (player_registration)
- ✅ `get_player_status` (player_registration)
- ✅ `get_all_players` (match_management)
- ✅ `approve_player` (player_registration)

### squad_selector
- ✅ `get_available_players_for_match` (match_management)
- ✅ `select_squad` (match_management)
- ✅ `get_match` (match_management)
- ✅ `get_all_players` (match_management)

## Missing Tools (7)

These tools are referenced in `agents.yaml` but not implemented:

1. **`send_message`** - Referenced by: message_processor, player_coordinator, team_administrator, squad_selector
2. **`get_user_status`** - Referenced by: message_processor
3. **`send_announcement`** - Referenced by: message_processor, team_administrator
4. **`send_poll`** - Referenced by: message_processor
5. **`get_welcome_message`** - Referenced by: help_assistant
6. **`team_member_registration`** - Referenced by: player_coordinator
7. **`list_matches`** - Referenced by: squad_selector

## Unused Tools (21) - Can Be Deleted

### player_registration (3)
- `add_player`
- `get_player_match`
- `list_team_members_and_players`

### team_administration (6)
- `create_team`
- `get_my_team_member_status`
- `get_team_members`
- `add_team_member_role`
- `remove_team_member_role`
- `promote_team_member_to_admin`

### system_infrastructure (5)
- `get_version_info`
- `get_system_available_commands`
- `log_command`
- `log_error`
- `get_firebase_document`

### shared (6)
- `FINAL_HELP_RESPONSE`
- `get_new_member_welcome_message`
- `register_player`
- `register_team_member`
- `registration_guidance`
- `team_member_guidance`

### communication (1)
- `send_telegram_message`

## Recommendations

### 1. Immediate Actions
- **Delete 21 unused tools** to clean up the codebase
- **Implement 7 missing tools** to complete the agent functionality

### 2. Tool Implementation Priority
**High Priority (Core Functionality):**
1. `send_message` - Used by 4 agents
2. `send_announcement` - Used by 2 agents
3. `get_user_status` - Used by message_processor

**Medium Priority:**
4. `send_poll` - Used by message_processor
5. `get_welcome_message` - Used by help_assistant
6. `team_member_registration` - Used by player_coordinator
7. `list_matches` - Used by squad_selector

### 3. Agent Tool Assignment Review
- **team_administrator** has no working tools assigned
- **message_processor** missing 4/8 tools
- **squad_selector** missing 2/6 tools

### 4. Code Quality Issues
- Several tool files have malformed import statements that need fixing
- Some tools have syntax errors preventing discovery

## Files to Clean Up

### Unused Tools by File
1. `kickai/features/player_registration/domain/tools/player_tools.py` - 3 tools
2. `kickai/features/team_administration/domain/tools/team_member_tools.py` - 5 tools
3. `kickai/features/team_administration/domain/tools/team_management_tools.py` - 1 tool
4. `kickai/features/system_infrastructure/domain/tools/help_tools.py` - 2 tools
5. `kickai/features/system_infrastructure/domain/tools/logging_tools.py` - 2 tools
6. `kickai/features/system_infrastructure/domain/tools/firebase_tools.py` - 1 tool
7. `kickai/features/shared/domain/tools/help_tools.py` - 2 tools
8. `kickai/features/shared/domain/tools/simple_onboarding_tools.py` - 3 tools
9. `kickai/features/shared/domain/tools/onboarding_tools.py` - 1 tool
10. `kickai/features/communication/domain/tools/telegram_tools.py` - 1 tool

## Next Steps

1. **Clean up unused tools** using the generated cleanup script
2. **Implement missing tools** starting with high-priority ones
3. **Fix import syntax issues** in tool files
4. **Update agents.yaml** to reflect actual tool availability
5. **Test agent functionality** after cleanup and implementation
