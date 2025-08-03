# Testing Invitation Link Processing in Mock Telegram Tester

## Overview
This document provides instructions for testing the complete invitation link processing flow in the Mock Telegram Testing System.

## Issue Fixed
Previously, the Mock Telegram Tester was using a hardcoded `"mock_invite_id"` instead of the actual invitation ID from the URL parameters. This has been fixed to properly extract and process the real invitation ID.

## Changes Made

### 1. Frontend (`enhanced_index.html`)
- Updated `simulateJoinChat()` to pass invitation context when available
- Added `invitation_context` to message data structure
- Marked join events with `type: "new_chat_members"`

### 2. Backend (`bot_integration.py`)
- Modified `MockMessage` class to store `invitation_context`
- Added `_invitation_data` attribute to `MockUpdate` for fallback access
- Preserved invitation context through the mock object hierarchy

### 3. Message Router (`agentic_message_router.py`)
- Removed hardcoded `invite_id = "mock_invite_id"`
- Added intelligent extraction logic for invitation context:
  1. Check `update.message.invitation_context.invite_id`
  2. Fall back to `update._invitation_data.invite_id`
  3. Use default only if no context found
- Added detailed logging for debugging

## Testing Instructions

### Step 1: Start the Mock Telegram Tester
```bash
source venv311/bin/activate && PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
```

### Step 2: Open Browser with Invitation Link
Navigate to: 
```
http://localhost:8001/?invite=94deca81-ec60-424d-a99e-aaf1e3a0f6a1&type=player&chat=-4829855674&team=KTI
```

### Step 3: Verify Invitation Detection
You should see:
- 🎯 **Invitation Link Detected!** banner
- Invite ID: **94deca81-ec60-424d-a99e-aaf1e3a0f6a1**
- Type: **player**
- Chat: **-4829855674**
- Team: **KTI**

### Step 4: Select User and Chat
1. Select a test user (e.g., "Test Player")
2. Select the main chat
3. The "Simulate Join Chat" button should appear

### Step 5: Test Invitation Processing
1. Click **"Simulate Join Chat"**
2. Check browser console for: `Adding invitation context: {invite_id: "94deca81...", ...}`
3. Bot should respond with invitation-specific welcome message

### Step 6: Verify Logs
Check the backend logs for:
```
🔗 Found invitation context with invite_id: 94deca81-ec60-424d-a99e-aaf1e3a0f6a1
🔗 Processing invitation link - invite_id: 94deca81-ec60-424d-a99e-aaf1e3a0f6a1, user_id: 1001, chat_type: main_chat
```

## Expected Results

### Success Case
- Invitation ID correctly extracted from URL
- Welcome message mentions the specific player name from invitation
- Phone number linking instructions provided
- No "mock_invite_id" in logs

### Fallback Case
- If no invitation context: logs show "⚠️ No invitation context found, using default invite_id"
- Still processes invitation but with generic response

## Message Data Structure

The frontend now sends this structure for join events:
```json
{
  "user_id": 1001,
  "chat_id": "-4829855674",
  "text": "Test Player joined the chat",
  "type": "new_chat_members",
  "new_chat_members": [{
    "id": 1001,
    "username": "testuser",
    "first_name": "Test", 
    "last_name": "Player"
  }],
  "invitation_context": {
    "invite_id": "94deca81-ec60-424d-a99e-aaf1e3a0f6a1",
    "type": "player",
    "chat": "-4829855674",
    "team": "KTI"
  }
}
```

## Troubleshooting

### Issue: Still seeing "mock_invite_id" in logs
- **Solution**: Ensure you accessed the tester with invitation URL parameters
- **Check**: Browser console should show invitation context being added

### Issue: No invitation context detected
- **Solution**: Verify URL has all required parameters: `invite`, `type`, `chat`, `team`
- **Check**: Frontend should display invitation banner

### Issue: Bot not responding to join event
- **Solution**: Ensure user and chat are properly selected before clicking "Simulate Join Chat"
- **Check**: Backend logs for any errors during message processing

## Additional Testing

### Test with Different Invitation Types
Replace the `type` parameter in the URL:
- `type=player` - Player invitation
- `type=member` - Team member invitation
- `type=admin` - Admin invitation

### Test with Different Chat Types
Replace the `chat` parameter:
- `-4829855674` - Main chat
- `-4829855675` - Leadership chat

### Test Error Handling
Try with invalid/expired invitation IDs to test error responses.

## Files Modified
- `/tests/mock_telegram/frontend/enhanced_index.html`
- `/tests/mock_telegram/backend/bot_integration.py`
- `/kickai/agents/agentic_message_router.py`

The invitation link processing flow now correctly handles real invitation IDs from URL parameters and provides proper debugging information throughout the process.