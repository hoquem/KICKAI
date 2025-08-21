# KICKAI E2E Test Execution Guide

Complete guide for executing the comprehensive end-to-end test suite for KICKAI commands.

## 🚀 Quick Start

### 1. Pre-flight Validation
First, validate that your environment is ready:
```bash
cd tests/e2e
node validate_setup.js
```

This will check:
- ✅ Node.js version (v16+)
- ✅ Firebase credentials
- ✅ KICKAI system configuration
- ✅ Dependencies installation
- ✅ Test file structure

### 2. Run Complete Test Suite
Execute all tests with automatic setup and cleanup:
```bash
./run_e2e_tests.sh
```

This single command will:
1. Install Node.js dependencies if needed
2. Start Mock Telegram UI server
3. Run comprehensive command tests
4. Generate detailed test reports
5. Clean up test data from Firestore
6. Stop Mock Telegram UI server

## 📋 Test Coverage

### Commands Tested
- **`/addplayer`** - Add players with invite link generation
- **`/addmember`** - Add team members with invite link generation
- **`/update`** - Player field updates (position, email, emergency contact)
- **`/updatemember`** - Team member field updates (phone, email, role)

### Scenarios Covered
- ✅ **Happy Path Workflows** - Normal command execution
- ✅ **Invite Link Processing** - End-to-end invite workflow
- ✅ **Real Firestore Integration** - Database validation
- ✅ **Permission Testing** - Role and chat type restrictions
- ✅ **Validation Rules** - Field format and constraint testing
- ✅ **Edge Cases** - Duplicate prevention, expired links
- ✅ **Cross-Entity Sync** - Player/TeamMember synchronization
- ✅ **Data Cleanup** - Automatic test data management

## 🎯 Expected Results

### Success Criteria
- **90%+ Pass Rate** for functional tests
- **100% Pass Rate** for security and permission tests
- **All invite links** must be generated and processable
- **All database records** must be created and cleaned up properly
- **All validation rules** must be enforced

### Sample Output
```
🏃‍♂️ TEST SUITE 1: /addplayer Command
✅ PASS 1.1 - Add New Player
✅ PASS 1.2 - Process Invite Link
✅ PASS 1.3 - Duplicate Phone Rejection

👔 TEST SUITE 2: /addmember Command
✅ PASS 2.1 - Add New Team Member
✅ PASS 2.2 - Process Member Invite Link

🔄 TEST SUITE 3: /update Commands
✅ PASS 3.1 - Update position
✅ PASS 3.2 - Update email
✅ PASS 3.3 - Validation: Invalid phone

📊 SUMMARY: 23/25 tests passed (92%)
🔗 Invite links generated: 4
🗂️ Database records created: 12
```

## 🔧 Individual Test Execution

### Run Specific Test Suites

#### All Commands with Invite Processing
```bash
node comprehensive_command_test.js
```

#### Update Commands Only
```bash
node update_commands_test.js
```

### Manual Setup Options

#### Check Prerequisites Only
```bash
./run_e2e_tests.sh --check-system
```

#### Install Dependencies Only
```bash
./run_e2e_tests.sh --install-deps
```

#### Start Mock Server Only
```bash
./run_e2e_tests.sh --start-server
```

## 📊 Test Reports

### Generated Files
After test execution, you'll find:

1. **Console Output** - Real-time test progress
2. **JSON Report** - `test-report-{uuid}.json`
3. **Update Report** - `update-commands-report-{timestamp}.json`

### Report Contents
```json
{
  "testRunId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-08T10:30:00.000Z",
  "summary": {
    "total": 25,
    "passed": 23,
    "failed": 2,
    "successRate": 92
  },
  "inviteLinks": [
    "http://localhost:8001?invite=test-123&action=join"
  ],
  "results": [
    {
      "test": "1.1 - Add New Player",
      "passed": true,
      "details": {
        "response_ok": true,
        "invite_link": true,
        "player_created": true
      }
    }
  ]
}
```

## 🧪 Test Data Management

### Test Users
The test suite uses these predefined users:
- **999999999** - Leadership Admin (can use /addplayer, /addmember)
- **888888888** - Regular Player (can use /update in main chat)
- **666666666** - Team Member (can use /updatemember in leadership chat)
- **777777777** - New User (for invite link processing)

### Test Phone Numbers
Unique test phone numbers:
- **+447001000001** - Primary test player
- **+447001000002** - Secondary test player
- **+447001000003** - Primary test team member
- **+447001000004** - Secondary test team member

### Automatic Cleanup
- All test records are tracked during creation
- Cleanup occurs automatically after test completion
- No manual intervention required
- Clean state guaranteed for subsequent test runs

## 🔍 Debugging

### Debug Mode
Run tests with browser visible:
```javascript
// Edit test files to set headless: false
this.browser = await puppeteer.launch({
    headless: false,  // Shows browser window
    defaultViewport: null,
    args: ['--start-maximized']
});
```

### Common Issues

#### Mock UI Not Available
```bash
# Check if server is running
curl http://localhost:8001

# Start manually if needed
cd ../../
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
```

#### Firebase Connection Issues
```bash
# Validate credentials
node -e "
const admin = require('firebase-admin');
const creds = require('./credentials/firebase_credentials_testing.json');
admin.initializeApp({credential: admin.credential.cert(creds)});
console.log('Firebase OK');
"
```

#### KICKAI System Issues
```bash
# Check system status
cd ../../
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('KICKAI System Ready')
"
```

### Verbose Logging
Enable detailed logging:
```bash
# Set environment variable for detailed output
DEBUG=kickai:* ./run_e2e_tests.sh
```

## 🚨 Troubleshooting

### Test Failures

#### Invite Link Issues
- **Symptom**: Invite links not generated
- **Check**: Leadership user permissions, team configuration
- **Fix**: Verify team has main_chat_id configured

#### Permission Errors
- **Symptom**: Commands fail with permission errors
- **Check**: User role and chat type
- **Fix**: Ensure correct user/chat combinations

#### Database Validation Failures
- **Symptom**: Records not found in Firestore
- **Check**: Firebase credentials and connection
- **Fix**: Verify testing database permissions

#### Update Command Failures
- **Symptom**: Field updates not working
- **Check**: Field validation rules and user permissions
- **Fix**: Use valid field names and formats

### Environment Issues

#### Node.js Version
```bash
# Check version
node --version

# Should be v16 or higher
# Install newer version if needed
```

#### Dependencies Missing
```bash
# Reinstall dependencies
cd tests/e2e
rm -rf node_modules package-lock.json
npm install
```

#### Python Environment
```bash
# Verify Python environment
cd ../../
python --version  # Should be 3.11+
pip list | grep kickai
```

## 🎯 Success Validation

### What Success Looks Like

1. **All tests execute without crashes**
2. **90%+ pass rate achieved**
3. **All invite links are generated and work**
4. **Database records are created and cleaned up**
5. **No permission bypasses occur**
6. **Validation rules are enforced**

### Example Successful Run
```bash
$ ./run_e2e_tests.sh

🔧 Initializing test environment...
✅ Firebase credentials found
✅ KICKAI system is ready
✅ Mock Telegram server started (PID: 12345)

🧪 Starting E2E Test Suite - Run ID: 550e8400-...

🏃‍♂️ TEST SUITE 1: /addplayer Command
📋 Test 1.1: Add New Player with Valid Data
✅ Command sent, response received (1247 chars)
🔗 Extracted invite link: http://localhost:8001?invite=...
✅ Firestore record validated in kickai_players: abc123
📋 Test 1.2: Process Player Invite Link
✅ Invite link processed successfully
✅ Firestore record validated in kickai_players: abc123

[... more tests ...]

📊 SUMMARY: 23/25 tests passed (92%)
🔗 Invite links generated: 4
🗂️ Database records created: 12
✅ Successfully cleaned up 12 records

🎉 All E2E tests completed successfully!
```

This comprehensive test suite ensures that KICKAI's core commands work correctly in real-world conditions with actual database integration and complete workflow validation.