# Mock Testing - Mock Telegram UI & Testing Framework

## Mock Telegram UI
Interactive web-based testing interface that simulates Telegram interactions:

```bash
# Start Mock Telegram UI
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001 (Liverpool FC themed)
```

## Mock UI Features
- **Multi-User Simulation**: Switch between different user roles
- **Chat Type Testing**: Main, leadership, and private chat simulation
- **Real-Time Interaction**: Direct communication with KICKAI agents
- **Visual Feedback**: Liverpool FC themed interface with response visualization
- **Command Testing**: All bot commands available through web interface

## User Role Simulation
The Mock UI supports testing with different user personas:

```python
# Available test users
users = {
    "leadership": {
        "telegram_id": 999999999,
        "username": "admin_user",
        "chat_type": "leadership"
    },
    "player": {
        "telegram_id": 888888888,
        "username": "player_user", 
        "chat_type": "main"
    },
    "unregistered": {
        "telegram_id": 777777777,
        "username": "new_user",
        "chat_type": "main"
    }
}
```

## Testing Frameworks

### Mock UI Controller
```python
from tests.functional.mock_ui_controller import MockUIController

async def test_scenario():
    controller = MockUIController()
    await controller.initialize()
    
    # Switch to leadership user
    controller.set_user('leadership')
    result = await controller.send_command('/addplayer "Test Player" "+447123456789"')
    
    # Verify response
    assert "Team Member Added Successfully" in result['response_text']
```

### Test Categories
1. **Unit Tests**: Component isolation (`tests/unit/`)
2. **Integration Tests**: Service interactions (`tests/integration/`)
3. **E2E Tests**: Complete workflows (`tests/e2e/`)
4. **Mock UI Tests**: Interactive testing (`tests/mock_telegram/`)
5. **Functional Tests**: Real bot integration (`tests/functional/`)

## Key Mock Testing Files
- `tests/mock_telegram/start_mock_tester.py` - Main UI launcher
- `tests/mock_telegram/backend/mock_telegram_service.py` - Mock service implementation
- `tests/functional/mock_ui_controller.py` - Programmatic test controller
- `tests/mock_telegram/backend/bot_integration.py` - Bot integration layer
- `mock_tester.html` - Web interface template

## Mock Service Configuration
```python
# Mock service settings
MOCK_BOT_TOKEN = "mock_bot_token_for_testing"
MOCK_CHAT_IDS = {
    "main": -1001001,
    "leadership": -1002002,
    "private": 123456789
}
```