# Tool Chat Type Parameter Audit

## Issue Summary

The "my info" natural language command in the leadership chat responded with player information instead of team member information because the tools are missing the `chat_type` parameter. This causes context-aware routing to fail.

## Root Cause

Tools that should be context-aware (returning different information based on chat type) are missing the `chat_type` parameter, causing them to always return the same type of information regardless of context.

## Tools Missing chat_type Parameter

### 1. Status/Information Tools

#### `get_my_status` (player_tools.py:328) ✅ **FIXED**
- **Current Parameters**: `team_id: str, user_id: str, chat_type: str`
- **Status**: ✅ **IMPLEMENTED** - Now accepts chat_type parameter
- **Fix**: Tool now routes to appropriate service based on chat_type:
  - `main_chat` → PlayerService
  - `leadership_chat` → TeamMemberService
- **Testing**: ✅ Verified tool accepts chat_type parameter and routes correctly

#### `get_my_team_member_status` (team_member_tools.py:21)
- **Current Parameters**: `team_id: str, user_id: str`
- **Missing**: `chat_type: str`
- **Issue**: Should only be used in leadership chat, but no validation
- **Impact**: Could be called in wrong context

### 2. List/Display Tools

#### `get_active_players` (player_tools.py:532)
- **Current Parameters**: `team_id: str, user_id: str`
- **Missing**: `chat_type: str`
- **Issue**: Should only show active players in main chat, not leadership chat
- **Impact**: Leadership chat users see player list instead of team member list

#### `list_team_members_and_players` (player_tools.py:708)
- **Current Parameters**: `team_id: str`
- **Missing**: `chat_type: str`
- **Issue**: Shows both team members and players, but should be context-aware
- **Impact**: Main chat users might see team member information they shouldn't

### 3. Other Potentially Affected Tools

#### `get_all_players` (player_tools.py:473)
- **Current Parameters**: `team_id: str, user_id: str`
- **Missing**: `chat_type: str`
- **Issue**: Should be restricted to leadership chat only
- **Impact**: Main chat users could access all player data

## Implemented Fixes

### 1. ✅ Fixed `get_my_status` Tool

**Changes Made:**
- Added `chat_type: str` parameter to function signature
- Implemented routing logic based on chat_type:
  ```python
  if chat_type == "leadership_chat":
      # Use team member service
      return await team_member_service.get_my_status(user_id, team_id)
  else:
      # Use player service
      return await player_service.get_player_by_telegram_id(user_id, team_id)
  ```
- Updated tool documentation to explain chat_type routing
- Added validation for chat_type parameter

**Files Modified:**
- `kickai/features/player_registration/domain/tools/player_tools.py`

### 2. ✅ Updated Agent Context Passing

**Changes Made:**
- Enhanced task description to include specific instructions for chat_type
- Updated MESSAGE_PROCESSOR agent backstory to emphasize using chat_type parameter
- Added explicit instructions for myinfo commands

**Files Modified:**
- `kickai/agents/configurable_agent.py`
- `kickai/config/agents.py`

### 3. ✅ Updated Orchestration Pipeline

**Changes Made:**
- Confirmed that `chat_type` is already being extracted and passed to agent context
- Enhanced task description to include tool instructions for chat_type

## Remaining Work

### Priority 1: Fix `get_my_team_member_status`
- Add `chat_type` parameter for validation
- Ensure it's only used in leadership chat context

### Priority 2: Fix `get_active_players`
- Add `chat_type` parameter
- Restrict to main chat only

### Priority 3: Fix `list_team_members_and_players`
- Add `chat_type` parameter
- Make context-aware for different chat types

## Testing Required

After all fixes, test:
- `/myinfo` in main chat → player information ✅ **VERIFIED**
- `/myinfo` in leadership chat → team member information ✅ **VERIFIED**
- `/list` in main chat → active players only
- `/list` in leadership chat → team members and players

## Verification

The fix for `get_my_status` has been verified:
- ✅ Tool accepts `chat_type` parameter
- ✅ Routes to PlayerService for `main_chat`
- ✅ Routes to TeamMemberService for `leadership_chat`
- ✅ Agent context includes `chat_type` parameter
- ✅ Task description includes explicit instructions for chat_type usage