# Playwright MCP Server for Telegram Bot Testing

This directory contains a Playwright-based testing framework for the KICKAI Telegram bot using the Model Context Protocol (MCP).

## Overview

The Playwright MCP server allows you to test your Telegram bot by interacting with the actual Telegram Web interface, providing a more realistic testing environment than mock implementations.

## Files

- `playwright_telegram_mcp.py` - Main Playwright testing framework
- `playwright_mcp_server.py` - MCP server implementation
- `test_playwright_mcp_client.py` - Client for testing the MCP server
- `run_playwright_help_test.py` - Simple test runner for /help command

## Setup

1. **Install Playwright** (already done):
   ```bash
   source venv311/bin/activate
   pip install playwright
   playwright install
   ```

2. **Set environment variables** (optional):
   ```bash
   export TELEGRAM_TEST_PHONE="+447123456789"  # Your phone number
   export TELEGRAM_TEST_CHAT="KickAI Testing"   # Chat name to test in
   export TELEGRAM_TEST_HEADLESS="false"        # Set to "true" for headless mode
   ```

## Usage

### Quick Test - /help Command

To test just the `/help` command:

```bash
source venv311/bin/activate
python tests/run_playwright_help_test.py
```

### Using the MCP Server

1. **Start the MCP server**:
   ```bash
   source venv311/bin/activate
   python tests/playwright_mcp_server.py
   ```

2. **Use the client**:
   ```bash
   source venv311/bin/activate
   python tests/test_playwright_mcp_client.py
   ```

### Direct Framework Usage

```python
from tests.playwright_telegram_mcp import TelegramBotTester

async def test_bot():
    tester = TelegramBotTester(
        phone_number="+447123456789",
        headless=False
    )
    
    results = await tester.run_all_tests("KickAI Testing")
    print(results)

# Run the test
import asyncio
asyncio.run(test_bot())
```

## MCP Server Methods

The MCP server supports the following methods:

- `start_browser` - Start browser and navigate to Telegram Web
- `login_telegram` - Login with phone number
- `navigate_chat` - Navigate to a specific chat
- `send_message` - Send a message in the current chat
- `wait_bot_response` - Wait for bot response
- `test_command` - Test a bot command with expected response
- `take_screenshot` - Take a screenshot
- `close_browser` - Close browser and cleanup

## Example MCP Request

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "test_command",
  "params": {
    "command": "/help",
    "expected_response": "Available commands",
    "timeout": 30
  }
}
```

## Features

- **Real Telegram Web Interface**: Tests against the actual Telegram Web interface
- **Screenshot Capture**: Automatic screenshots for debugging
- **Flexible Response Matching**: Supports partial text matching for bot responses
- **Multiple Browser Support**: Chromium, Firefox, and WebKit
- **Headless Mode**: Can run without visible browser window
- **MCP Protocol**: Standardized communication protocol

## Troubleshooting

1. **Login Issues**: Make sure your phone number is correct and you have access to Telegram Web
2. **Chat Navigation**: Ensure the chat name matches exactly
3. **Selector Issues**: Telegram Web interface may change; update selectors if needed
4. **Timeout Issues**: Increase timeout values for slower connections

## Next Steps

Once the `/help` command test is working, you can:

1. Add more command tests (`/addplayer`, `/status`, etc.)
2. Create comprehensive test suites
3. Integrate with your CI/CD pipeline
4. Add video recording for test debugging
5. Create test scenarios for different user roles

## Notes

- The server requires manual login to Telegram Web (QR code or phone verification)
- Screenshots are saved to `tests/screenshots/` directory
- The framework is designed to be extensible for additional test scenarios


