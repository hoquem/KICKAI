# KICKAI End-to-End Test Suite

Comprehensive end-to-end testing framework for KICKAI commands using Puppeteer automation and real Firestore database integration.

## Overview

This test suite validates the complete workflow of KICKAI's core commands:

- **`/addplayer`** - Add new players with invite link generation
- **`/addmember`** - Add new team members with invite link generation  
- **`/update`** - Player field updates in main chat
- **`/updatemember`** - Team member field updates in leadership chat
- **`/updateplayer`** - Admin updates for players

### Key Features

- ✅ **Real Firestore Integration** - Tests against actual database
- ✅ **Mock Telegram UI Automation** - Puppeteer-driven UI testing
- ✅ **Invite Link Processing** - End-to-end invite link workflows
- ✅ **Cross-Entity Synchronization** - Validates player/team member sync
- ✅ **Permission Testing** - Chat type and role-based access control
- ✅ **Data Validation** - Field validation and duplicate prevention
- ✅ **Automatic Cleanup** - Test data management and cleanup

## Prerequisites

### System Requirements

1. **Node.js** (v16+ recommended)
2. **Python 3.11+** with KICKAI system configured
3. **Firebase Admin Credentials** for testing environment
4. **Mock Telegram UI** server capability

### Environment Setup

1. **Install Node.js dependencies:**
   ```bash
   cd tests/e2e
   npm install
   ```

2. **Firebase Credentials:**
   Ensure you have Firebase testing credentials at:
   ```
   credentials/firebase_credentials_testing.json
   ```

3. **KICKAI System:**
   Verify the KICKAI system is properly configured:
   ```bash
   cd ../../  # Back to project root
   make setup-dev
   PYTHONPATH=. python -c "from kickai.core.dependency_container import ensure_container_initialized; ensure_container_initialized()"
   ```

## Test Execution

### Quick Start

Run the complete test suite:
```bash
./run_e2e_tests.sh
```

This script will:
- Check all prerequisites
- Start Mock Telegram UI server
- Install dependencies if needed
- Run comprehensive tests
- Generate detailed report
- Clean up test data
- Stop Mock Telegram UI server

### Individual Test Components

#### 1. Comprehensive Command Tests
```bash
node comprehensive_command_test.js
```
Tests all commands with invite link processing and Firestore validation.

#### 2. Update Commands Specific Tests
```bash
node update_commands_test.js
```
Focused testing of all `/update` command variations.

### Manual Testing Options

#### Install Dependencies Only
```bash
./run_e2e_tests.sh --install-deps
```

#### Start Mock Server Only
```bash
./run_e2e_tests.sh --start-server
```

#### Check System Status
```bash
./run_e2e_tests.sh --check-system
```

## Test Structure

### Test Suites

#### Suite 1: `/addplayer` Command
- **Test 1.1:** Add new player with valid data
- **Test 1.2:** Process player invite link
- **Test 1.3:** Duplicate phone number rejection

#### Suite 2: `/addmember` Command  
- **Test 2.1:** Add new team member
- **Test 2.2:** Process team member invite link

#### Suite 3: `/update` Commands
- **Test 3.1:** Player self-update (main chat)
- **Test 3.2:** Team member self-update (leadership chat)
- **Test 3.3:** Field validation tests

#### Suite 4: Invite Link Edge Cases
- **Test 4.1:** Expired invite link handling
- **Test 4.2:** Already used invite link prevention
- **Test 4.3:** Invalid invite link format handling

#### Suite 5: Cross-Entity Synchronization
- **Test 5.1:** Player-TeamMember field sync
- **Test 5.2:** Bidirectional sync validation

#### Suite 6: Permission & Access Control
- **Test 6.1:** Non-leadership user restrictions
- **Test 6.2:** Chat type restrictions
- **Test 6.3:** Protected field access control

### Test Data Management

#### Test Users
The test suite uses predefined test users:

- **Leadership Admin** (999999999) - Can use `/addplayer`, `/addmember`
- **Regular Player** (888888888) - Can use `/update` in main chat
- **Team Member** (666666666) - Can use `/updatemember` in leadership chat
- **New User** (777777777) - Used for invite link processing

#### Test Phone Numbers
Unique phone numbers with test prefix:
```
+447001000001 - Player 1
+447001000002 - Player 2
+447001000003 - Member 1
+447001000004 - Member 2
```

#### Automatic Cleanup
- All test records are tracked during creation
- Automatic cleanup occurs after test completion
- Firestore batch deletion for efficiency
- Cleanup summary provided in test report

## Validation Components

### Firestore Validation
- **Player Records:** Name, phone, status, player_id validation
- **Team Member Records:** Name, phone, role, member_id validation
- **Invite Links:** Generation, expiration, usage tracking
- **Field Updates:** Before/after value verification
- **Cross-Entity Sync:** Linked record synchronization

### Response Validation
- **Success Messages:** Proper formatting and content
- **Error Messages:** Appropriate error handling
- **Invite Links:** Valid format and extractability
- **Command Responses:** Complete and properly formatted

### Security Validation
- **Permission Enforcement:** Role-based access control
- **Chat Restrictions:** Proper chat type enforcement
- **Field Protection:** Protected field modification prevention
- **Duplicate Prevention:** Phone number uniqueness

## Test Reports

### Report Generation
Each test run generates:

1. **Console Output:** Real-time test progress and results
2. **JSON Report:** Detailed test results with metadata
3. **Cleanup Summary:** Test data management report

### Report Contents
```json
{
  "testRunId": "uuid-v4",
  "timestamp": "ISO-8601",
  "summary": {
    "total": 25,
    "passed": 23,
    "failed": 2,
    "successRate": 92
  },
  "inviteLinks": ["array of generated links"],
  "results": ["detailed test results"],
  "environment": {
    "mockUI": "http://localhost:8001",
    "firestoreRecords": 12
  }
}
```

### Success Criteria
- **Functional Requirements:** 90%+ pass rate
- **Response Validation:** All commands return properly formatted responses
- **Data Integrity:** All database operations complete successfully
- **Security:** All permission checks pass

## Troubleshooting

### Common Issues

#### Mock Telegram UI Not Starting
```bash
# Check if port 8001 is available
lsof -i :8001

# Start manually
cd ../../
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
```

#### Firebase Permission Errors
```bash
# Verify credentials file exists and is valid
ls -la credentials/firebase_credentials_testing.json

# Test Firebase connection
node -e "
const admin = require('firebase-admin');
const serviceAccount = require('./credentials/firebase_credentials_testing.json');
admin.initializeApp({credential: admin.credential.cert(serviceAccount)});
console.log('Firebase connected successfully');
"
```

#### KICKAI System Not Ready
```bash
# Check system initialization
cd ../../
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('System ready')
"
```

#### Test Failures
1. **Check Prerequisites:** Ensure all dependencies are installed
2. **Verify Environment:** Confirm Firebase credentials and KICKAI system
3. **Review Logs:** Check browser console and test output
4. **Manual Testing:** Test commands manually in Mock UI
5. **Database State:** Verify Firestore is accessible and has proper permissions

### Debug Mode
Run tests with browser visible for debugging:
```javascript
// In test files, set headless: false
this.browser = await puppeteer.launch({
    headless: false,  // Shows browser window
    defaultViewport: null,
    args: ['--start-maximized']
});
```

### Cleanup Issues
If automatic cleanup fails:
```bash
# Manual cleanup (use with caution)
node -e "
const admin = require('firebase-admin');
const serviceAccount = require('./credentials/firebase_credentials_testing.json');
admin.initializeApp({credential: admin.credential.cert(serviceAccount)});
const db = admin.firestore();

// Query and delete test records
// This would be a custom cleanup script
"
```

## Continuous Integration

### GitHub Actions Integration
Add to `.github/workflows/e2e-tests.yml`:
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Setup KICKAI
        run: make setup-dev
      - name: Run E2E Tests
        run: cd tests/e2e && ./run_e2e_tests.sh
        env:
          FIREBASE_CREDENTIALS: ${{ secrets.FIREBASE_CREDENTIALS }}
```

### Local CI Testing
```bash
# Simulate CI environment
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace/tests/e2e \
  node:18 \
  ./run_e2e_tests.sh
```

## Development

### Adding New Tests

1. **Extend Existing Suites:**
   ```javascript
   // Add to comprehensive_command_test.js
   async runTestSuiteX() {
       // New test suite implementation
   }
   ```

2. **Create New Test Files:**
   ```javascript
   // Follow the pattern of update_commands_test.js
   class NewTestSuite {
       // Test implementation
   }
   ```

3. **Update Test Runner:**
   ```bash
   # Add new test file to run_e2e_tests.sh if needed
   ```

### Test Data Patterns
```javascript
// Use consistent test data patterns
const TEST_PHONE_NUMBERS = {
    PLAYER_1: '+447001000001',
    MEMBER_1: '+447001000003'
};

const TEST_USERS = {
    LEADERSHIP: { telegram_id: 999999999, name: 'Leadership Admin' },
    PLAYER: { telegram_id: 888888888, name: 'Test Player' }
};
```

### Validation Helpers
```javascript
// Use Firestore validation utilities
const firestoreUtils = new FirestoreTestUtils();

// Validate player creation
const playerRecord = await firestoreUtils.validatePlayerCreated(
    phone, 
    { name: 'Expected Name', status: 'pending' }
);

// Validate field updates
const updateResult = await firestoreUtils.validateFieldUpdate(
    'kickai_players',
    { phone: testPhone },
    'position',
    'Striker'
);
```

## Architecture

### Test Framework Components

```
tests/e2e/
├── comprehensive_command_test.js    # Main test suite
├── update_commands_test.js          # Update commands specific tests
├── firestore_utils.js               # Database validation utilities
├── run_e2e_tests.sh                # Test runner script
├── package.json                     # Node.js dependencies
└── README.md                        # This documentation
```

### Integration Points

1. **Mock Telegram UI** (`http://localhost:8001`)
   - User simulation and command sending
   - Response capture and validation
   - Chat type switching

2. **KICKAI System** (Python backend)
   - Command processing and routing
   - Business logic execution
   - Database operations

3. **Firebase Firestore** (Real database)
   - Data persistence and validation
   - Cross-entity relationships
   - Transaction consistency

4. **Puppeteer Browser** (Test automation)
   - UI interaction automation
   - Response capture
   - Multi-tab invite processing

This E2E test suite provides comprehensive validation of KICKAI's core functionality with real-world conditions and complete workflow testing.