# 🧪 KICKAI End-to-End Testing Framework

## 📋 Overview

The KICKAI E2E Testing Framework provides comprehensive testing capabilities for:
- **Telegram Bot Automation**: Automated interaction with your Telegram bot
- **Firestore Data Validation**: Real-time validation of database operations
- **Natural Language Processing**: Testing of NLP capabilities
- **Command Execution**: Validation of slash commands
- **User Interaction Flows**: End-to-end user journey testing

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Runner   │───▶│ Telegram Tester │───▶│  Telegram Bot   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Firestore       │    │ Test Suites     │    │ Test Reports    │
│ Validator       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Firestore DB    │    │ Test Data       │    │ HTML/JSON/TXT   │
│                 │    │ Factories       │    │ Reports         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file with your credentials:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_SESSION_STRING=your_session_string_here

# Firestore Configuration
FIRESTORE_PROJECT_ID=your_project_id_here
FIRESTORE_CREDENTIALS_PATH=path/to/credentials.json  # Optional

# Test Configuration
TEST_TIMEOUT=30
TEST_MAX_RETRIES=3
TEST_PARALLEL=false
TEST_LOG_LEVEL=INFO
```

### 3. Run Tests

```bash
# Run smoke tests
python run_e2e_tests.py --suite smoke

# Run comprehensive tests with HTML report
python run_e2e_tests.py --suite comprehensive --report html --save

# Run natural language tests in parallel
python run_e2e_tests.py --suite natural_language --parallel
```

## 📊 Available Test Suites

### 1. **Smoke Tests** (`smoke`)
- Basic bot functionality
- Quick validation of core features
- **Duration**: ~60 seconds
- **Use Case**: Pre-deployment validation

### 2. **Player Registration** (`player_registration`)
- Complete player onboarding flow
- Registration, approval, status checks
- **Duration**: ~2 minutes
- **Use Case**: New feature validation

### 3. **Match Management** (`match_management`)
- Match creation and management
- Attendance tracking
- **Duration**: ~3 minutes
- **Use Case**: Core functionality testing

### 4. **Payment Processing** (`payment_processing`)
- Payment creation and management
- Status tracking and validation
- **Duration**: ~2.5 minutes
- **Use Case**: Financial feature testing

### 5. **Natural Language** (`natural_language`)
- NLP query processing
- Intent recognition and responses
- **Duration**: ~1.5 minutes
- **Use Case**: AI feature validation

### 6. **Admin Operations** (`admin_operations`)
- Administrative functions
- Team management and reporting
- **Duration**: ~3.5 minutes
- **Use Case**: Admin feature testing

### 7. **Comprehensive** (`comprehensive`)
- Full system integration
- All features combined
- **Duration**: ~10 minutes
- **Use Case**: Full regression testing

## 🛠️ Framework Components

### 1. **TelegramBotTester**
```python
from testing.e2e_framework import TelegramBotTester

# Initialize tester
tester = TelegramBotTester(bot_token, api_id, api_hash, session_string)
await tester.start()

# Send message and wait for response
await tester.send_message(chat_id, "/register John Smith 07123456789 midfielder")
response = await tester.wait_for_response(chat_id, timeout=30)

await tester.stop()
```

### 2. **FirestoreValidator**
```python
from testing.e2e_framework import FirestoreValidator

# Initialize validator
validator = FirestoreValidator(project_id)

# Validate document
context = FirestoreTestContext(
    collection="players",
    document_id="user_123",
    expected_data={"name": "John Smith", "status": "active"},
    validation_rules={"phone": {"type": "regex", "pattern": r"^07\d{9}$"}}
)

result = await validator.validate_document(context)
```

### 3. **E2ETestRunner**
```python
from testing.e2e_framework import E2ETestRunner

# Create test runner
runner = E2ETestRunner(telegram_tester, firestore_validator)

# Add tests
runner.add_command_test("/register John Smith 07123456789 midfielder", context)
runner.add_nl_test("What's my player status?", context)

# Run tests
results = await runner.run_tests()
```

## 📝 Test Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your bot token | Required |
| `TELEGRAM_API_ID` | Telegram API ID | Required |
| `TELEGRAM_API_HASH` | Telegram API hash | Required |
| `TELEGRAM_SESSION_STRING` | Session string | Required |
| `FIRESTORE_PROJECT_ID` | Firestore project ID | Required |
| `TEST_TIMEOUT` | Default timeout (seconds) | 30 |
| `TEST_MAX_RETRIES` | Maximum retry attempts | 3 |
| `TEST_PARALLEL` | Run tests in parallel | false |
| `TEST_LOG_LEVEL` | Logging level | INFO |

### Test Data Templates

```python
from testing.test_config import get_test_data_template

# Get player template
player_data = get_test_data_template("player")
# Returns: {"name": "Test Player", "phone": "07123456789", ...}

# Get match template
match_data = get_test_data_template("match")
# Returns: {"opponent": "Test Opponent", "date": "2024-12-20T19:30:00", ...}
```

### Validation Rules

```python
from testing.test_config import get_validation_rules

# Get validation rules for players collection
rules = get_validation_rules("players")
# Returns: {"name": {"type": "exists"}, "phone": {"type": "regex", "pattern": r"^07\d{9}$"}, ...}
```

## 📈 Test Reports

### Report Formats

1. **Text Report** (Default)
   ```bash
   python run_e2e_tests.py --suite smoke --report text
   ```

2. **JSON Report**
   ```bash
   python run_e2e_tests.py --suite comprehensive --report json --save
   ```

3. **HTML Report**
   ```bash
   python run_e2e_tests.py --suite natural_language --report html --save
   ```

### Report Content

- **Summary Statistics**: Total tests, pass/fail rates, duration
- **Test Details**: Individual test results with metadata
- **Error Information**: Detailed error messages and stack traces
- **Performance Metrics**: Timing information for optimization

## 🔧 Advanced Usage

### Custom Test Suites

```python
from testing.test_suites import create_test_runner_with_suite

# Create custom test suite
custom_tests = [
    {
        "name": "Custom Test",
        "type": "command",
        "command": "/custom_command",
        "telegram_context": TelegramTestContext(...),
        "firestore_validation": FirestoreTestContext(...)
    }
]

# Run custom suite
runner = create_test_runner_with_suite("custom", telegram_tester, firestore_validator)
results = await runner.run_tests()
```

### Parallel Testing

```bash
# Enable parallel execution
python run_e2e_tests.py --suite natural_language --parallel
```

### Continuous Integration

```yaml
# GitHub Actions example
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run E2E tests
        run: python run_e2e_tests.py --suite smoke --report json --save
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_API_ID: ${{ secrets.TELEGRAM_API_ID }}
          TELEGRAM_API_HASH: ${{ secrets.TELEGRAM_API_HASH }}
          TELEGRAM_SESSION_STRING: ${{ secrets.TELEGRAM_SESSION_STRING }}
          FIRESTORE_PROJECT_ID: ${{ secrets.FIRESTORE_PROJECT_ID }}
```

## 🐛 Troubleshooting

### Common Issues

1. **Telegram Authentication**
   ```bash
   # Error: Invalid session string
   # Solution: Generate new session string using Telethon
   ```

2. **Firestore Permissions**
   ```bash
   # Error: Permission denied
   # Solution: Check service account permissions
   ```

3. **Test Timeouts**
   ```bash
   # Error: Test timeout
   # Solution: Increase TEST_TIMEOUT environment variable
   ```

### Debug Mode

```bash
# Enable verbose logging
python run_e2e_tests.py --suite smoke --verbose
```

### Test Isolation

```python
# Clean up test data after each test
async def cleanup_test_data():
    await firestore_validator.delete_test_document("players", "test_user_123")
```

## 📚 Best Practices

### 1. **Test Data Management**
- Use unique identifiers for test data
- Clean up test data after tests
- Use data factories for consistent test data

### 2. **Test Organization**
- Group related tests in suites
- Use descriptive test names
- Include both positive and negative test cases

### 3. **Performance Optimization**
- Use parallel execution for independent tests
- Optimize timeouts based on environment
- Cache expensive operations

### 4. **Error Handling**
- Implement proper error handling in tests
- Use retry mechanisms for flaky tests
- Provide detailed error messages

## 🔮 Future Enhancements

### Planned Features

1. **Visual Test Recorder**
   - Record user interactions
   - Generate test scripts automatically

2. **Performance Testing**
   - Load testing capabilities
   - Performance benchmarking

3. **Mobile Testing**
   - Mobile app integration
   - Cross-platform testing

4. **AI-Powered Testing**
   - Intelligent test generation
   - Automated test maintenance

## 📞 Support

For questions and support:
- Check the troubleshooting section
- Review test logs in `e2e_tests.log`
- Create issues in the project repository

---

**Happy Testing! 🧪✨** 