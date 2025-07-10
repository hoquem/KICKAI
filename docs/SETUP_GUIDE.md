# 🔐 **KICKAI E2E Testing - Environment Setup Guide**

## 📋 **Overview**

This guide will walk you through setting up all the required environment variables and credentials for the KICKAI E2E testing framework.

## 🚀 **Quick Setup (Automated)**

### **Option 1: Interactive Setup Scripts**

```bash
# 1. Set up Telegram credentials
python setup_telegram_credentials.py

# 2. Set up Firestore credentials
python setup_firestore.py

# 3. Test the setup
python run_e2e_tests.py --suite smoke
```

### **Option 2: Manual Setup**

Follow the detailed steps below if you prefer manual setup.

## 🤖 **Step 1: Telegram Bot Setup**

### **1.1 Get Bot Token**

1. **Open Telegram** and search for `@BotFather`
2. **Send `/newbot`** or use an existing bot
3. **Follow the instructions** to create your bot
4. **Copy the bot token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### **1.2 Get API ID and Hash**

1. **Go to** https://my.telegram.org
2. **Log in** with your phone number
3. **Navigate to** "API development tools"
4. **Create a new application** or use existing
5. **Copy the API ID** (numbers only)
6. **Copy the API Hash** (32-character string)

### **1.3 Generate Session String**

```bash
# Install Telethon if not already installed
pip install telethon

# Run the interactive setup
python setup_telegram_credentials.py
```

**Or manually:**

```python
from telethon import TelegramClient
from telethon.sessions import StringSession

# Replace with your credentials
api_id = "YOUR_API_ID"
api_hash = "YOUR_API_HASH"

# Create client
client = TelegramClient(StringSession(), int(api_id), api_hash)

# Start client (this will prompt for phone number and code)
client.start()

# Get session string
session_string = client.session.save()
print(f"Session string: {session_string}")

# Stop client
client.disconnect()
```

## 🔥 **Step 2: Firestore Setup**

### **2.1 Get Project ID**

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Select your project** or create a new one
3. **Copy the Project ID** (not the project name)

### **2.2 Set Up Authentication**

#### **Option A: Service Account Key (Recommended for Production)**

1. **Go to** IAM & Admin > Service Accounts
2. **Create a new service account** or select existing
3. **Add roles**: Firestore Admin, Datastore User
4. **Create a new key** (JSON format)
5. **Download the JSON file** to a secure location

#### **Option B: Application Default Credentials (Local Development)**

```bash
# Install Google Cloud SDK
# macOS: brew install google-cloud-sdk
# Windows: Download from https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login
```

### **2.3 Test Firestore Connection**

```bash
# Run the interactive setup
python setup_firestore.py
```

## 📝 **Step 3: Create .env File**

Create a `.env` file in your project root:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_SESSION_STRING=your_session_string_here

# Firestore Configuration
FIRESTORE_PROJECT_ID=your_project_id_here
FIRESTORE_CREDENTIALS_PATH=path/to/credentials.json  # Optional for ADC

# Test Configuration
TEST_TIMEOUT=30
TEST_MAX_RETRIES=3
TEST_PARALLEL=false
TEST_LOG_LEVEL=INFO
TEST_TEAM_ID=test-team-123
TEST_USER_ID=test_user_123
TEST_CHAT_ID=test_chat_456
```

## 🧪 **Step 4: Test Your Setup**

### **4.1 Run Smoke Tests**

```bash
# Test basic functionality
python run_e2e_tests.py --suite smoke
```

### **4.2 Run Example Tests**

```bash
# Run example tests
python example_e2e_test.py
```

### **4.3 Run Comprehensive Tests**

```bash
# Run all tests with HTML report
python run_e2e_tests.py --suite comprehensive --report html --save
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Telegram Authentication Errors**

```bash
# Error: Invalid session string
# Solution: Regenerate session string
python setup_telegram_credentials.py
```

#### **2. Firestore Permission Errors**

```bash
# Error: Permission denied
# Solution: Check service account roles
# Required roles: Firestore Admin, Datastore User
```

#### **3. Bot Not Responding**

```bash
# Check if bot is running
# Ensure bot token is correct
# Verify bot has necessary permissions
```

#### **4. Environment Variables Not Found**

```bash
# Install python-dotenv
pip install python-dotenv

# Or set variables manually
export TELEGRAM_BOT_TOKEN="your_token"
export FIRESTORE_PROJECT_ID="your_project"
```

### **Debug Mode**

```bash
# Enable verbose logging
python run_e2e_tests.py --suite smoke --verbose
```

## 🔒 **Security Best Practices**

### **1. Environment Variables**

- ✅ **Use `.env` file** for local development
- ✅ **Never commit `.env` to version control**
- ✅ **Use secrets management** in production
- ❌ **Don't hardcode credentials** in code

### **2. Service Account Keys**

- ✅ **Store keys securely** (not in project directory)
- ✅ **Use minimal permissions** (principle of least privilege)
- ✅ **Rotate keys regularly**
- ❌ **Don't share keys** or commit to version control

### **3. Telegram Session**

- ✅ **Keep session string secure**
- ✅ **Regenerate if compromised**
- ❌ **Don't share session strings**

## 📊 **Environment-Specific Configuration**

### **Development Environment**

```bash
TEST_LOG_LEVEL=DEBUG
TEST_TIMEOUT=60
TEST_SAVE_REPORTS=true
```

### **Staging Environment**

```bash
TEST_LOG_LEVEL=INFO
TEST_TIMEOUT=30
TEST_SAVE_REPORTS=true
```

### **Production Environment**

```bash
TEST_LOG_LEVEL=WARNING
TEST_TIMEOUT=20
TEST_SAVE_REPORTS=false
```

## 🚀 **CI/CD Integration**

### **GitHub Actions Example**

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
          FIRESTORE_CREDENTIALS_PATH: ${{ secrets.FIRESTORE_CREDENTIALS_PATH }}
```

### **Railway Deployment**

```bash
# Set environment variables in Railway dashboard
# Or use railway CLI
railway variables set TELEGRAM_BOT_TOKEN=your_token
railway variables set FIRESTORE_PROJECT_ID=your_project
```

## 📚 **Next Steps**

1. **Run your first test**: `python run_e2e_tests.py --suite smoke`
2. **Customize test suites** for your specific needs
3. **Set up CI/CD** for automated testing
4. **Read the full guide**: `E2E_TESTING_GUIDE.md`
5. **Explore examples**: `example_e2e_test.py`

## 🆘 **Need Help?**

- **Check logs**: `e2e_tests.log`
- **Review documentation**: `E2E_TESTING_GUIDE.md`
- **Run examples**: `example_e2e_test.py`
- **Enable debug mode**: `--verbose` flag

---

**Happy Testing! 🧪✨** 