# 🚀 Quick Start: E2E Testing Guide

## **Prerequisites**

1. **Python 3.11+** installed
2. **Virtual environment** activated (`venv311`)
3. **Environment variables** configured (see `.env` setup below)
4. **Mock Telegram Tester** running (see setup below)

---

## **Step 1: Environment Setup**

### **1.1 Activate Virtual Environment**
```bash
source venv311/bin/activate
```

### **1.2 Configure Environment Variables**
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your values
nano .env
```

**Required Environment Variables:**
```bash
# CRITICAL: Invite Link Secret Key
KICKAI_INVITE_SECRET_KEY=test_secret_key_for_debugging_only_32_chars_long

# FIREBASE CONFIGURATION
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials_testing.json

# AI/LLM CONFIGURATION (GROQ)
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here

# TELEGRAM MOCK CONFIGURATION
MOCK_TELEGRAM_BASE_URL=http://localhost:8001
MOCK_TELEGRAM_PORT=8001


### **1.3 Initialize Clean KTI Environment**
```bash
# Clean up existing collections and initialize only team KTI
python setup_clean_kti_environment.py
```

---

## **Step 2: Start Mock Telegram Tester**

### **2.1 Start the Mock Service**
```bash
# In a new terminal window
source venv311/bin/activate
python tests/mock_telegram/start_mock_tester.py
```

### **2.2 Verify Service is Running**
```bash
# Check health endpoint
curl http://localhost:8001/health

# Expected response: {"status": "healthy"}
```

### **2.3 Access Web Interface**
Open your browser and go to:
- **Enhanced Frontend**: http://localhost:8001
- **Legacy Frontend**: http://localhost:8001/legacy

---

## **Step 3: Run E2E Tests**

### **3.1 Run All Tests**
```bash
# Run complete test suite
python run_comprehensive_e2e_tests.py
```

### **3.2 Run Specific Phase**
```bash
# Run only environment setup
python run_comprehensive_e2e_tests.py --phase 1

# Run only component testing
python run_comprehensive_e2e_tests.py --phase 2

# Run only command testing
python run_comprehensive_e2e_tests.py --phase 4
```

### **3.3 Run with Verbose Logging**
```bash
# Run with detailed logging
python run_comprehensive_e2e_tests.py --verbose
```

---

## **Step 4: Manual Testing**

### **4.1 Test via Web Interface**
1. Open http://localhost:8001
2. Select a test user (e.g., "Test Player")
3. Select a chat (e.g., "Main Chat")
4. Send test messages:
   - `/help` - Get help information
   - `/addplayer John Smith +1234567890 Forward` - Add player
   - `I want to register as a player` - Natural language

### **4.2 Test via API**
```bash
# Test help command
curl -X POST http://localhost:8001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "text": "/help", "chat_id": 2001}'

# Test player registration
curl -X POST http://localhost:8001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "text": "/addplayer John Smith +1234567890 Forward", "chat_id": 2001}'

# Test natural language
curl -X POST http://localhost:8001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "text": "How do I register as a player?", "chat_id": 2001}'
```

---

## **Step 5: Verify Results**

### **5.1 Check Test Reports**
After running tests, check the generated report:
```bash
# View latest test report
ls -la test_report_*.json
cat test_report_YYYYMMDD_HHMMSS.json
```

### **5.2 Check Firestore Data**
```bash
# Verify KTI team data persistence
python -c "
import asyncio
from kickai.database.firebase_client import get_firebase_client
client = get_firebase_client()
async def check_data():
    kti_players = await client.query_documents('kickai_KTI_players')
    kti_members = await client.query_documents('kickai_KTI_team_members')
    print(f'KTI Players: {len(kti_players)}')
    print(f'KTI Team Members: {len(kti_members)}')
asyncio.run(check_data())
"
```

### **5.3 Check Logs**
```bash
# View application logs
tail -f logs/kickai.log

# View mock service logs
# (Check the terminal where mock service is running)
```

---

## **Step 6: Troubleshooting**

### **6.1 Common Issues**

#### **Mock Telegram Service Not Starting**
```bash
# Check if port 8001 is available
lsof -i :8001

# Kill any existing process
kill -9 $(lsof -t -i:8001)

# Restart service
python tests/mock_telegram/start_mock_tester.py
```

#### **Firebase Connection Issues**
```bash
# Verify credentials file exists
ls -la credentials/firebase_credentials_testing.json

# Test Firebase connection
python -c "
from kickai.database.firebase_client import get_firebase_client
client = get_firebase_client()
print('Firebase connection successful')
"
```

#### **Groq LLM Issues**
```bash
# Verify API key is set
echo $GROQ_API_KEY

# Test Groq connection
python -c "
from kickai.config.llm_config import LLMConfiguration
config = LLMConfiguration()
llm = config.main_llm
response = llm.invoke([{'role': 'user', 'content': 'Hello'}])
print('Groq LLM working:', response[:50])
"
```

### **6.2 Debug Mode**
```bash
# Run tests with debug logging
python run_comprehensive_e2e_tests.py --verbose --phase 1
```

---

## **Step 7: Performance Monitoring**

### **7.1 Monitor Response Times**
```bash
# Test response time
time curl -X POST http://localhost:8001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "text": "/help", "chat_id": 2001}'
```

### **7.2 Monitor Memory Usage**
```bash
# Check memory usage
ps aux | grep python | grep -v grep
```

### **7.3 Monitor System Resources**
```bash
# Monitor CPU and memory
top -p $(pgrep -f "python.*mock_telegram")
```

---

## **Expected Results**

### **✅ Successful Test Run**
```
🧪 COMPREHENSIVE E2E TEST REPORT
================================================================================

📊 SUMMARY:
   Total Tests: 45
   Passed: 43
   Failed: 2
   Success Rate: 95.6%
   Total Duration: 45.23s

📋 PHASE RESULTS:
   Phase 1: ✅ PASS (5/5 tests)
   Phase 2: ✅ PASS (4/4 tests)
   Phase 3: ✅ PASS (3/3 tests)
   Phase 4: ✅ PASS (10/10 tests)
   Phase 5: ✅ PASS (5/5 tests)
   Phase 6: ✅ PASS (3/3 tests)
   Phase 7: ✅ PASS (3/3 tests)
   Phase 8: ✅ PASS (3/3 tests)

🎉 All tests completed successfully!
```

### **✅ System Health Check**
- Mock Telegram Tester: ✅ Running on http://localhost:8001
- CrewAI Agents: ✅ All 5 agents initialized
- Groq LLM: ✅ Connected and responding
- Firestore: ✅ Connected and storing data
- All Commands: ✅ Working (slash and natural language)

---

## **Next Steps**

1. **Review Test Results**: Check the generated test report for any failures
2. **Fix Issues**: Address any failed tests or configuration issues
3. **Optimize Performance**: If response times are slow, optimize LLM calls
4. **Scale Testing**: Add more test scenarios and edge cases
5. **Production Readiness**: Ensure all components work reliably

---

## **Support**

If you encounter issues:

1. **Check Logs**: Review application and test logs for error messages
2. **Verify Configuration**: Ensure all environment variables are set correctly
3. **Test Components**: Run individual component tests to isolate issues
4. **Check Dependencies**: Verify all required packages are installed
5. **Restart Services**: Restart mock Telegram service and re-run tests

The comprehensive testing strategy ensures your KICKAI system is working end-to-end with all components properly integrated and validated! 🚀
