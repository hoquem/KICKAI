# Mock Testing - Interactive Development UI

## Mock Telegram UI
**Interactive testing interface for KICKAI development**

**Start:** `PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py`
**Access:** http://localhost:8001

## Features
- **Multiple User Types:** Leadership, Player, Unregistered users
- **Real-time Testing:** Test commands instantly without real Telegram
- **Command Validation:** Verify agent routing and responses
- **Interactive:** Click-to-send common commands

## User Types & Permissions
```javascript
// Switch between user types for testing
users: {
  leadership: { telegram_id: 999999999, permissions: ['ALL'] },
  player: { telegram_id: 123456789, permissions: ['PLAYER'] },
  unregistered: { telegram_id: 555555555, permissions: ['PUBLIC'] }
}
```

## Testing Workflow
1. **Start Mock UI:** `PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py`
2. **Switch User Type:** Leadership/Player/Unregistered
3. **Test Commands:** Click buttons or type commands
4. **Verify Responses:** Check agent routing and response format

## Command Testing Examples
**Leadership Commands:**
- `/addplayer "Test Player" "+447123456789"`
- `/addmember "Test Member" "+447123456789"`

**Player Commands:**
- `/update position goalkeeper`
- `/myinfo`
- `/help`

**Natural Language:**
- "What is my current status?"
- "I want to update my availability"

## System Integration
- **Routes through:** `AgenticMessageRouter`
- **Uses real:** 6-agent CrewAI system, Firebase database
- **Mocks only:** Telegram API calls

**Files:**
- `tests/mock_telegram/start_mock_tester.py` - Main interface
- `tests/mock_telegram/backend/` - Mock service backend