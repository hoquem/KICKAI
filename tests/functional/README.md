# KICKAI Functional Testing Suite

Comprehensive functional testing framework for KICKAI commands using real Firestore, Mock Telegram UI, and Puppeteer automation.

## Overview

This testing suite validates KICKAI command functionality with:
- **Real Firestore Database** - Tests against actual KTI team data
- **Mock Telegram UI** - Liverpool FC themed interface for user simulation
- **Puppeteer MCP** - Browser automation for UI monitoring
- **Data Integrity Validation** - Real-time Firestore validation
- **Comprehensive Reporting** - Detailed test results and recommendations

## Quick Start

### 1. Environment Validation
First, validate your testing environment:

```bash
cd /Users/mahmud/projects/KICKAI
PYTHONPATH=. python tests/functional/test_environment_setup.py
```

This checks:
- ✅ Python 3.11+ environment
- ✅ Firestore connectivity
- ✅ KICKAI bot functionality
- ⚠️ Mock UI availability (needs manual start)
- ⚠️ Puppeteer MCP configuration

### 2. Setup Test Data
Create comprehensive test data in KTI team:

```bash
PYTHONPATH=. python tests/functional/setup_kti_test_data.py
```

Creates:
- 3 test players (active, pending, inactive)
- 2 test team members (coach, manager)
- Test data markers for tracking
- Baseline data for validation

### 3. Start Mock UI
Start the Liverpool FC themed Mock Telegram UI:

```bash
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
```

Access at: http://localhost:8001

### 4. Start KICKAI Bot
In a separate terminal, start the KICKAI bot:

```bash
PYTHONPATH=. python run_bot_local.py
```

### 5. Run Functional Tests
Execute the complete test suite:

```bash
PYTHONPATH=. python tests/functional/functional_test_runner.py
```

### 6. Cleanup Test Data
After testing, clean up test data:

```bash
PYTHONPATH=. python tests/functional/cleanup_kti_test_data.py
```

## Test Components

### 📊 KTI Test Data Manager
`kti_test_data_manager.py`

Manages test data lifecycle:
- Creates realistic test players and team members
- Ensures data integrity and relationships
- Provides cleanup and validation capabilities
- Tracks all created data for complete removal

**Usage:**
```python
from tests.functional.kti_test_data_manager import KTITestDataManager

manager = KTITestDataManager("KTI")
await manager.initialize()
await manager.setup_test_data()
# ... run tests ...
await manager.cleanup_test_data()
```

### 🎮 Mock UI Controller
`mock_ui_controller.py`

Controls Mock Telegram UI automation:
- Simulates different user types (leadership, player, unregistered)
- Sends commands and captures responses
- Validates response content against expectations
- Takes screenshots for visual verification

**Usage:**
```python
from tests.functional.mock_ui_controller import MockUIController

controller = MockUIController("http://localhost:8001")
await controller.initialize()
await controller.switch_user("leadership")
result = await controller.send_command("/addplayer John +447123456789")
```

### 🔍 Firestore Validator
`firestore_validator.py`

Real-time data integrity validation:
- Validates document schemas and data types
- Ensures phone number uniqueness
- Checks invite link integrity
- Compares against baseline snapshots
- Generates comprehensive validation reports

**Usage:**
```python
from tests.functional.firestore_validator import FirestoreValidator

validator = FirestoreValidator("KTI")
await validator.initialize()
report = await validator.generate_validation_report()
```

### 🎯 Functional Test Runner
`functional_test_runner.py`

Orchestrates complete testing workflow:
- Coordinates all test components
- Executes command tests in sequence
- Monitors data changes and integrity
- Generates comprehensive test reports
- Handles cleanup and error recovery

## Commands Tested

### `/help` Command Tests
- Context-aware help in different chats
- Help for specific commands
- Error handling for invalid requests
- **Expected**: No data modifications

### `/list` Command Tests  
- Player listing in main chat (active only)
- Full listing in leadership chat (all players/members)
- Empty state handling
- **Expected**: No data modifications

### `/info` Command Tests
- Personal info for registered/unregistered users
- Status lookup by phone number
- Error handling for invalid phone numbers
- **Expected**: No data modifications

### `/addplayer` Command Tests
- Valid player addition with various name formats
- Phone number validation and uniqueness
- Permission enforcement (leadership only)
- Chat type restrictions
- **Expected**: New player records, invite links

### `/addmember` Command Tests
- Valid team member addition
- Cross-collection phone uniqueness
- Leadership permission validation
- Member vs player distinction
- **Expected**: New member records, leadership invite links

## Test Scenarios

### Valid Test Cases
```bash
# Help commands
/help
/help /addplayer

# List commands  
/list (from different chat types)

# Info commands
/myinfo
/status +447111111111

# Add player commands
/addplayer "John Smith" "+447999111222"
/addplayer Jane +447999333444
/addplayer Test Player 07999555666

# Add member commands
/addmember "Sarah Manager" "+447999888777"
```

### Error Test Cases
```bash
# Invalid parameters
/addplayer
/addplayer "Bad Phone" "invalid"
/addplayer "Duplicate" "+447111111111"  # existing phone

# Permission violations
/addplayer "Test" "+447999123456"  # from player user
/addmember "Test" "+447999123456"  # from player user

# Invalid phone formats
/status invalid-phone
/addplayer "Test" "123"
```

## Data Validation

### Schema Validation
All documents validated against strict schemas:

**Players:**
- `player_id`: string (required)
- `name`: string, ≥2 chars (required)
- `phone`: UK format (required, unique)
- `telegram_id`: positive integer (required)
- `status`: active|pending|inactive (required)
- `team_id`: matches KTI (required)

**Members:**
- `member_id`: string (required)  
- `name`: string, ≥2 chars (required)
- `phone`: UK format (required, unique across players/members)
- `telegram_id`: positive integer (required)
- `role`: coach|manager|team_member (required)
- `status`: active|pending|inactive (required)

**Invite Links:**
- `link_id`: string (required)
- `secure_token`: string, ≥32 chars (required, unique)
- `expires_at`: future ISO datetime (required)
- `team_id`: matches KTI (required)

### Relationship Validation
- Phone number uniqueness across players and members
- Team ID consistency across all documents
- Invite link relationships to players/members
- Status workflow compliance

## Environment Requirements

### Prerequisites
- Python 3.11+
- Firebase credentials configured
- KICKAI bot environment variables set
- Node.js (for Puppeteer MCP)

### Required Environment Variables
```bash
KICKAI_INVITE_SECRET_KEY=test-secret-key-for-testing-only
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_FILE=credentials/your-credentials.json
AI_PROVIDER=groq  # or other provider
```

### MCP Server Setup
Install Puppeteer MCP server:
```bash
claude mcp add puppeteer -s user -- npx -y @modelcontextprotocol/server-puppeteer
```

## Test Reports

### Execution Report
Generated after each test run:
- Test execution summary (passed/failed counts)
- Command-specific results with validation details
- Response time analysis
- Data integrity verification
- Screenshot collection

### Validation Report  
Real-time Firestore validation:
- Document schema compliance
- Data relationship integrity
- Baseline comparison analysis
- Phone number uniqueness verification
- Invite link security validation

### Example Report Structure
```json
{
  "report_id": "functional_test_report_...",
  "session": {
    "session_id": "functional_test_...",
    "duration": 180.5,
    "status": "completed"
  },
  "test_results": {
    "overall_statistics": {
      "total_tests": 25,
      "passed_tests": 23, 
      "failed_tests": 2,
      "success_rate": 92.0
    },
    "command_results": {
      "help": {"success_rate": 100.0},
      "addplayer": {"success_rate": 85.7}
    }
  },
  "firestore_validation": {
    "overall_status": "PASS",
    "validation_success_rate": 98.5
  },
  "overall_success": true
}
```

## Troubleshooting

### Common Issues

**Environment Validation Fails:**
```bash
# Check Python version
python --version  # Must be 3.11+

# Check PYTHONPATH
echo $PYTHONPATH  # Should include project root

# Validate Firestore credentials
ls credentials/  # Firebase credentials file exists
```

**Mock UI Not Accessible:**
```bash
# Start Mock UI manually
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py

# Check if port 8001 is available
lsof -i :8001
```

**Test Data Issues:**
```bash
# Clean and recreate test data
PYTHONPATH=. python tests/functional/cleanup_kti_test_data.py
PYTHONPATH=. python tests/functional/setup_kti_test_data.py

# Validate data integrity
PYTHONPATH=. python -c "
from tests.functional.kti_test_data_manager import validate_kti_test_data
import asyncio
result = asyncio.run(validate_kti_test_data())
print(result)
"
```

**KICKAI Bot Connection Issues:**
```bash
# Test bot initialization
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('✅ Bot initialization successful')
"

# Check environment variables
env | grep KICKAI
env | grep FIREBASE
```

### Performance Issues

**Slow Test Execution:**
- Check Firestore connection latency
- Verify Mock UI responsiveness
- Monitor system resource usage
- Increase test timeouts if needed

**Memory Issues:**
- Ensure proper cleanup after each test
- Monitor process memory usage
- Restart components if memory leaks detected

## Best Practices

### Before Testing
1. ✅ Run environment validation
2. ✅ Ensure Mock UI is accessible
3. ✅ Verify KICKAI bot can start
4. ✅ Create fresh test data
5. ✅ Take Firestore backup if needed

### During Testing  
1. 🔍 Monitor test execution logs
2. 📸 Capture screenshots on failures
3. 📊 Validate data changes in real-time
4. ⏱️ Track response times
5. 🚨 Alert on validation failures

### After Testing
1. 🧹 Clean up all test data
2. 📊 Review test reports
3. 🔍 Investigate failed tests
4. 📝 Document issues found
5. 🚀 Implement improvements

## Integration with CI/CD

### GitHub Actions Integration
```yaml
name: KICKAI Functional Tests
on: [push, pull_request]
jobs:
  functional-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Setup test data
        run: PYTHONPATH=. python tests/functional/setup_kti_test_data.py
      - name: Run functional tests
        run: PYTHONPATH=. python tests/functional/functional_test_runner.py
      - name: Cleanup test data
        run: PYTHONPATH=. python tests/functional/cleanup_kti_test_data.py
        if: always()
```

This comprehensive testing suite ensures KICKAI commands work correctly with real data while maintaining data integrity and providing detailed validation reports.