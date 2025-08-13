# Mock UI Integration Guide

This guide explains how to use KICKAI's enhanced Mock Telegram UI integration for development and testing.

## Overview

KICKAI now features seamless integration between its communication tools and the Mock Telegram UI. This allows you to:

- **Test communication tools visually** - See messages in real-time in a browser interface
- **Develop without real Telegram** - No need for actual bot tokens during development
- **Test all message types** - Regular messages, announcements, polls, broadcasts, etc.
- **Auto-detection** - Automatically switches to Mock UI mode in development environments

## Quick Start

### 1. Start the Mock UI

```bash
cd /Users/mahmud/projects/KICKAI
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
```

The Mock UI will start at: **http://localhost:8001**

### 2. Start KICKAI Bot

In a new terminal:

```bash
cd /Users/mahmud/projects/KICKAI
source venv311/bin/activate
PYTHONPATH=. python run_bot_local.py
```

KICKAI will automatically detect the Mock UI and integrate with it.

### 3. Test the Integration

Run the comprehensive test suite:

```bash
./scripts/test_communication_integration.sh
```

Or just the integration tests:

```bash
PYTHONPATH=. python scripts/test_mock_ui_integration.py
```

## Features

### Auto-Detection

The system automatically uses Mock UI when:

- Environment is `development`, `local`, or `testing`
- AI provider is `groq`, `ollama`, or `local`
- `KICKAI_LOCAL_MODE=true` is set
- Running in pytest environment

### Manual Control

You can explicitly control Mock UI usage:

```bash
# Force enable Mock UI
export USE_MOCK_UI=true

# Force disable Mock UI
export USE_MOCK_UI=false

# Use auto-detection (default)
unset USE_MOCK_UI
```

### Supported Message Types

All KICKAI communication tools work with Mock UI:

- **Basic Messages** - `send_message()`
- **Announcements** - `send_announcement()`
- **Polls** - `send_poll()`
- **Team Announcements** - `send_team_announcement()`
- **Broadcast Messages** - `broadcast_message()`
- **Contact Sharing** - `send_contact_share_button()`

### Chat Support

The integration supports both chat types:

- **Main Chat** (ID: 2001) - General team communication
- **Leadership Chat** (ID: 2002) - Leadership-only messages

## Testing Your Communication Tools

### Interactive Testing

1. Start Mock UI and KICKAI bot (see Quick Start)
2. Open the Mock UI at http://localhost:8001
3. Use the web interface to send commands and see bot responses in real-time

### Programmatic Testing

Use the communication service in your code:

```python
from kickai.core.dependency_container import get_service
from kickai.features.communication.domain.interfaces.telegram_bot_service_interface import TelegramBotServiceInterface

# Get the service (will be MockTelegramBotService in development)
telegram_service = get_service(TelegramBotServiceInterface)

# Send messages that will appear in Mock UI
await telegram_service.send_message("2001", "Hello team!")
await telegram_service.send_announcement("2001", "Important announcement!")
await telegram_service.send_poll("2001", "What's for lunch?", ["Pizza", "Burgers", "Salad"])
```

### Test Suite

Run the comprehensive test suite to verify everything works:

```bash
./scripts/test_communication_integration.sh
```

This tests:
- Mock UI detection and connectivity
- Message sending to both chats
- Announcements and polls
- Broadcast messaging
- Error handling and fallback behavior

## Mock UI Interface

The Mock UI provides:

- **Real User Data** - Loads actual users from your Firestore database
- **Chat Interface** - Send messages as different users
- **Real-time Updates** - See bot responses immediately via WebSocket
- **Message History** - View all conversation history
- **Chat Switching** - Switch between main and leadership chats

## Environment Configuration

### Development (Auto-enabled)

```bash
export ENVIRONMENT=development
export AI_PROVIDER=groq
# Mock UI integration is automatically enabled
```

### Testing

```bash
export USE_MOCK_UI=true
export MOCK_API_BASE_URL=http://localhost:8001/api  # Optional, defaults to this
```

### Production (Auto-disabled)

```bash
export ENVIRONMENT=production
# Mock UI integration is automatically disabled
# Real TelegramBotService will be used
```

## Troubleshooting

### Mock UI Not Detected

**Issue**: KICKAI says Mock UI not available

**Solution**:
1. Verify Mock UI is running: `curl http://localhost:8001/api/stats`
2. Check environment variables: `echo $USE_MOCK_UI`
3. Review auto-detection logs in KICKAI startup

### Messages Not Appearing in UI

**Issue**: Bot says messages sent but not visible in Mock UI

**Solution**:
1. Check browser console for errors
2. Refresh the Mock UI page
3. Verify WebSocket connection in browser dev tools
4. Check KICKAI logs for UI communication errors

### Integration Test Failures

**Issue**: `test_mock_ui_integration.py` reports failures

**Solution**:
1. Ensure Mock UI is running before starting tests
2. Wait 5 seconds after starting Mock UI
3. Check network connectivity to localhost:8001
4. Review test output for specific error details

## Advanced Usage

### Custom Chat IDs

```python
# Override default chat IDs
telegram_service = MockTelegramBotService(
    token="mock-token",
    team_id="TEST",
    main_chat_id="1001",      # Custom main chat
    leadership_chat_id="1002"  # Custom leadership chat
)
```

### Error Handling

```python
# Check Mock UI status
status = telegram_service.get_mock_ui_status()
print(f"Mock UI available: {status['mock_ui_detected']}")

# Test connectivity
connectivity = await telegram_service.test_mock_ui_connectivity()
print(f"Connection status: {connectivity['status']}")
```

### Graceful Fallback

The system gracefully handles Mock UI unavailability:

- Messages are still tracked internally for testing
- No exceptions thrown if Mock UI becomes unavailable
- Automatic retry on next message if Mock UI comes back online

## Development Workflow

### Typical Development Session

1. **Start Mock UI**: `PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py`
2. **Start KICKAI Bot**: `PYTHONPATH=. python run_bot_local.py`
3. **Test Commands**: Use Mock UI web interface to test bot commands
4. **View Responses**: See real-time bot responses in Mock UI
5. **Iterate**: Modify code, restart bot, test again

### Testing New Features

1. **Write Tests**: Add tests to `test_mock_ui_integration.py`
2. **Test Integration**: Run `./scripts/test_communication_integration.sh`
3. **Manual Testing**: Use Mock UI to manually test edge cases
4. **Verify Logs**: Check KICKAI logs for proper integration

## Benefits

### For Development
- **Visual Feedback** - See exactly what users would see
- **No External Dependencies** - No need for real Telegram bot setup
- **Fast Iteration** - Immediate feedback on changes
- **Realistic Testing** - Uses real user data from Firestore

### For Testing
- **Automated Tests** - Comprehensive test suite included
- **Isolated Testing** - No external API calls during tests
- **Error Simulation** - Test error handling scenarios
- **Performance Testing** - Measure response times

### For CI/CD
- **No External Services** - Tests run without real Telegram API
- **Deterministic** - Consistent behavior across environments
- **Fast Execution** - No network delays from real APIs
- **Complete Coverage** - Test all communication scenarios

## Conclusion

The Mock UI integration provides a powerful development and testing environment for KICKAI's communication features. It combines the convenience of local development with the realism of actual user data and message flows.

For more information, see:
- `tests/mock_telegram/start_mock_tester.py` - Mock UI startup script
- `scripts/test_mock_ui_integration.py` - Integration test suite
- `kickai/features/communication/infrastructure/mock_telegram_bot_service.py` - Implementation details