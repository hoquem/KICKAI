# 🧪 **KICKAI End-to-End Testing Framework**

## 🎯 **Overview**

A comprehensive, enterprise-grade testing framework for KICKAI that provides automated testing of:
- **Telegram Bot Interactions** - Real bot automation using Telethon
- **Firestore Data Validation** - Real-time database validation
- **Natural Language Processing** - NLP capability testing
- **Command Execution** - Slash command validation
- **User Interaction Flows** - End-to-end user journey testing

## 🚀 **Quick Start**

### **Option 1: Automated Setup (Recommended)**

```bash
# Run the interactive setup wizard
python quick_start.py
```

This will guide you through the entire setup process automatically.

### **Option 2: Manual Setup**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up Telegram credentials
python setup_telegram_credentials.py

# 3. Set up Firestore credentials
python setup_firestore.py

# 4. Validate setup
python validate_setup.py

# 5. Run your first test
python run_e2e_tests.py --suite smoke
```

## 📊 **Available Test Suites**

| Suite | Duration | Purpose | Use Case |
|-------|----------|---------|----------|
| **Smoke** | ~60s | Basic functionality | Pre-deployment |
| **Player Registration** | ~2min | Onboarding flow | Feature validation |
| **Match Management** | ~3min | Match operations | Core functionality |
| **Payment Processing** | ~2.5min | Financial features | Payment validation |
| **Natural Language** | ~1.5min | NLP capabilities | AI feature testing |
| **Admin Operations** | ~3.5min | Administrative tasks | Admin feature testing |
| **Comprehensive** | ~10min | Full integration | Regression testing |

## 🛠️ **Framework Components**

### **Core Architecture**

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

### **Key Components**

1. **`TelegramBotTester`** - Automated Telegram bot interaction
2. **`FirestoreValidator`** - Real-time database validation
3. **`E2ETestRunner`** - Orchestrates complex test scenarios
4. **`TestConfig`** - Environment-aware configuration management

## 📝 **Environment Variables**

### **Required Variables**

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_SESSION_STRING=your_session_string_here

# Firestore Configuration
FIRESTORE_PROJECT_ID=your_project_id_here
```

### **Optional Variables**

```bash
# Test Configuration
TEST_TIMEOUT=30
TEST_MAX_RETRIES=3
TEST_PARALLEL=false
TEST_LOG_LEVEL=INFO
TEST_TEAM_ID=test-team-123
TEST_USER_ID=test_user_123
TEST_CHAT_ID=test_chat_456

# Firestore Authentication (Optional)
FIRESTORE_CREDENTIALS_PATH=path/to/credentials.json
```

## 🧪 **Running Tests**

### **Basic Commands**

```bash
# Run smoke tests
python run_e2e_tests.py --suite smoke

# Run comprehensive tests with HTML report
python run_e2e_tests.py --suite comprehensive --report html --save

# Run natural language tests in parallel
python run_e2e_tests.py --suite natural_language --parallel

# Run example tests
python example_e2e_test.py
```

### **Advanced Options**

```bash
# Enable verbose logging
python run_e2e_tests.py --suite smoke --verbose

# Save report to file
python run_e2e_tests.py --suite comprehensive --report json --save

# Run specific test types
python run_e2e_tests.py --suite player_registration
python run_e2e_tests.py --suite match_management
python run_e2e_tests.py --suite payment_processing
```

## 📈 **Test Reports**

### **Report Formats**

1. **Text Report** (Default) - Console-friendly output
2. **JSON Report** - Machine-readable for CI/CD
3. **HTML Report** - Visual reports for stakeholders

### **Report Content**

- **Summary Statistics** - Total tests, pass/fail rates, duration
- **Test Details** - Individual test results with metadata
- **Error Information** - Detailed error messages and stack traces
- **Performance Metrics** - Timing information for optimization

## 🔧 **Customization**

### **Adding Custom Tests**

```python
from testing.e2e_framework import E2ETestRunner, TelegramTestContext

# Create test runner
runner = E2ETestRunner(telegram_tester, firestore_validator)

# Add custom command test
runner.add_command_test("/custom_command", context)

# Add custom natural language test
runner.add_nl_test("Custom question?", context)

# Add custom user flow test
runner.add_user_flow_test([
    {"type": "send_message", "message": "Hello"},
    {"type": "wait_for_response", "timeout": 30},
    {"type": "validate_response", "expected": "Hi there!"}
], context)
```

### **Custom Test Suites**

```python
# In src/testing/test_suites.py
class CustomTestSuite:
    @staticmethod
    def get_tests() -> List[Dict[str, Any]]:
        return [
            {
                "name": "Custom Test",
                "type": "command",
                "command": "/custom_command",
                "telegram_context": TelegramTestContext(...),
                "firestore_validation": FirestoreTestContext(...)
            }
        ]
```

## 🚀 **CI/CD Integration**

### **GitHub Actions**

```yaml
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

### **Railway Deployment**

```bash
# Set environment variables in Railway dashboard
railway variables set TELEGRAM_BOT_TOKEN=your_token
railway variables set FIRESTORE_PROJECT_ID=your_project
```

## 🔒 **Security Best Practices**

### **Environment Variables**

- ✅ **Use `.env` file** for local development
- ✅ **Never commit `.env` to version control**
- ✅ **Use secrets management** in production
- ❌ **Don't hardcode credentials** in code

### **Service Account Keys**

- ✅ **Store keys securely** (not in project directory)
- ✅ **Use minimal permissions** (principle of least privilege)
- ✅ **Rotate keys regularly**
- ❌ **Don't share keys** or commit to version control

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Telegram Authentication Errors**
   ```bash
   # Regenerate session string
   python setup_telegram_credentials.py
   ```

2. **Firestore Permission Errors**
   ```bash
   # Check service account roles
   # Required: Firestore Admin, Datastore User
   ```

3. **Test Timeouts**
   ```bash
   # Increase timeout in .env file
   TEST_TIMEOUT=60
   ```

4. **Environment Variables Not Found**
   ```bash
   # Install python-dotenv
   pip install python-dotenv
   ```

### **Debug Mode**

```bash
# Enable verbose logging
python run_e2e_tests.py --suite smoke --verbose
```

## 📚 **Documentation**

- **`E2E_TESTING_GUIDE.md`** - Comprehensive testing guide
- **`SETUP_GUIDE.md`** - Detailed setup instructions
- **`example_e2e_test.py`** - Usage examples
- **`validate_setup.py`** - Environment validation

## 🆘 **Support**

### **Getting Help**

1. **Check logs**: `e2e_tests.log`
2. **Validate setup**: `python validate_setup.py`
3. **Run examples**: `python example_e2e_test.py`
4. **Review documentation**: `E2E_TESTING_GUIDE.md`

### **Quick Commands**

```bash
# Validate environment
python validate_setup.py

# Run quick test
python run_e2e_tests.py --suite smoke

# Run examples
python example_e2e_test.py

# Check setup
python quick_start.py
```

## 🔮 **Future Enhancements**

### **Planned Features**

1. **Visual Test Recorder** - Record user interactions
2. **Performance Testing** - Load testing capabilities
3. **Mobile Testing** - Mobile app integration
4. **AI-Powered Testing** - Intelligent test generation

### **Contributing**

1. **Fork the repository**
2. **Create a feature branch**
3. **Add your tests**
4. **Submit a pull request**

---

**Happy Testing! 🧪✨**

*For questions and support, check the documentation or create an issue in the repository.* 