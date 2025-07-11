# KICKAI E2E Testing Architecture

## Overview

End-to-End (E2E) testing for KICKAI involves testing the complete user interaction flow through Telegram clients and validating data persistence in Firestore. This document outlines the architecture, requirements, and implementation approach.

## Architecture Components

### 1. Multiple Telegram Clients

#### Bot Client (Existing)
- **Purpose**: Handles commands and responses
- **Role**: Admin in both main and leadership chats
- **Credentials**: Bot token, API ID, API Hash
- **Capabilities**: Send messages, receive updates, process commands

#### Player Client (New)
- **Purpose**: Simulates player interactions
- **Role**: Regular user in main chat
- **Credentials**: Real user phone number, API ID, API Hash, session string
- **Capabilities**: Send messages, read responses, interact with bot

#### Admin Client (New)
- **Purpose**: Simulates admin interactions
- **Role**: Admin in leadership chat
- **Credentials**: Real user phone number, API ID, API Hash, session string
- **Capabilities**: Send admin commands, read responses, manage players

### 2. Test Environment

#### Telegram Groups
- **Main Chat**: `-4889304885` (KickAI Testing)
- **Leadership Chat**: `-4814449926` (KickAI Testing - Leadership)

#### Firestore Database
- **Project**: `kickai-954c2`
- **Collections**: players, teams, matches, payments, etc.

## Required Credentials

### Environment Variables

```bash
# Bot Configuration (Existing)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_USERNAME=KickAITesting_bot

# Chat IDs (Existing)
TELEGRAM_MAIN_CHAT_ID=-4889304885
TELEGRAM_LEADERSHIP_CHAT_ID=-4814449926

# Player Client (New)
TELEGRAM_PLAYER_PHONE=+1234567890
TELEGRAM_PLAYER_SESSION_STRING=player_session_string

# Admin Client (New)
TELEGRAM_ADMIN_PHONE=+0987654321
TELEGRAM_ADMIN_SESSION_STRING=admin_session_string

# Firestore (Existing)
FIRESTORE_PROJECT_ID=kickai-954c2
FIRESTORE_CREDENTIALS_PATH=./credentials/firebase_credentials_testing.json

# Google API (Existing)
GOOGLE_API_KEY=your_google_api_key
```

## Test User Requirements

### Real User Accounts Required
- **Player Account**: Real Telegram account with phone number
- **Admin Account**: Real Telegram account with phone number
- **Bot Account**: Already configured

### User Setup Process
1. **Create Test Accounts**: Use real phone numbers for Telegram accounts
2. **Join Groups**: Add both accounts to the test groups
3. **Generate Session Strings**: Use `generate_session.py` for each account
4. **Configure Permissions**: Ensure proper roles in groups

## Test Scenarios

### 1. Player Registration Flow
```
Player Client → /register [name] [phone] [position] → Main Chat
Bot → Process registration → Firestore
Admin Client → /approve [player_id] → Leadership Chat
Bot → Process approval → Firestore
Player Client → Check status → Main Chat
```

### 2. Match Management Flow
```
Admin Client → /create_match [details] → Leadership Chat
Bot → Create match → Firestore
Player Client → /attend [match_id] → Main Chat
Bot → Update attendance → Firestore
```

### 3. Payment Processing Flow
```
Admin Client → /create_payment [details] → Leadership Chat
Bot → Create payment → Firestore
Player Client → /pay [payment_id] → Main Chat
Bot → Process payment → Firestore
```

## Implementation Approach

### 1. Multi-Client Framework
```python
class MultiClientE2ETester:
    def __init__(self):
        self.bot_client = TelegramClient(bot_token, api_id, api_hash)
        self.player_client = TelegramClient(player_session, api_id, api_hash)
        self.admin_client = TelegramClient(admin_session, api_id, api_hash)
        self.firestore_validator = FirestoreValidator(project_id)
```

### 2. Test Execution Flow
```python
async def test_player_registration():
    # Player sends registration command
    await player_client.send_message(main_chat_id, "/register John 07123456789 midfielder")
    
    # Wait for bot response
    bot_response = await wait_for_bot_response(main_chat_id)
    
    # Validate Firestore data
    player_data = await firestore_validator.get_document("players", "john_123")
    
    # Admin approves player
    await admin_client.send_message(leadership_chat_id, "/approve john_123")
    
    # Validate approval in Firestore
    updated_data = await firestore_validator.get_document("players", "john_123")
```

### 3. Response Validation
- **Bot Responses**: Check for success/error messages
- **Firestore Data**: Validate document creation/updates
- **Timing**: Ensure responses within acceptable timeframes
- **State Consistency**: Verify data consistency across operations

## Setup Instructions

### 1. Create Test Accounts
```bash
# Create two real Telegram accounts with different phone numbers
# Account 1: Player (regular user)
# Account 2: Admin (admin user)
```

### 2. Generate Session Strings
```bash
# For Player Account
python generate_session.py
# Enter: API_ID, API_HASH, PLAYER_PHONE_NUMBER

# For Admin Account  
python generate_session.py
# Enter: API_ID, API_HASH, ADMIN_PHONE_NUMBER
```

### 3. Update Environment
```bash
# Add to .env file
TELEGRAM_PLAYER_PHONE=+1234567890
TELEGRAM_PLAYER_SESSION_STRING=player_session_string
TELEGRAM_ADMIN_PHONE=+0987654321
TELEGRAM_ADMIN_SESSION_STRING=admin_session_string
```

### 4. Join Test Groups
- Add both accounts to main chat (-4889304885)
- Add both accounts to leadership chat (-4814449926)
- Ensure bot is admin in both groups

## Test Execution

### Running Tests
```bash
# Run all E2E tests
python run_e2e_tests.py --suite comprehensive

# Run specific test suite
python run_e2e_tests.py --suite player_registration

# Run with parallel execution
python run_e2e_tests.py --suite comprehensive --parallel
```

### Test Reports
- **Text Reports**: Console output with detailed results
- **JSON Reports**: Machine-readable test results
- **HTML Reports**: Visual test reports with charts

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Clean up test data after each test
- Use unique identifiers for test data

### 2. Error Handling
- Handle network timeouts gracefully
- Validate all responses before proceeding
- Log detailed error information

### 3. Data Validation
- Verify Firestore data after each operation
- Check for data consistency
- Validate business rules

### 4. Performance
- Set reasonable timeouts for responses
- Monitor test execution times
- Optimize for parallel execution

## Troubleshooting

### Common Issues
1. **Session Expired**: Regenerate session strings
2. **Group Access**: Ensure all clients are in groups
3. **Bot Permissions**: Verify bot has admin rights
4. **Firestore Access**: Check credentials and permissions

### Debug Tools
- `check_group_access.py`: Verify group membership
- `validate_setup.py`: Check all credentials
- Test logs: Detailed execution information

## Future Enhancements

### 1. Test Data Management
- Automated test data cleanup
- Test data factories for consistent data
- Database snapshots for test isolation

### 2. Advanced Scenarios
- Multi-player interactions
- Complex workflow testing
- Performance testing under load

### 3. CI/CD Integration
- Automated test execution
- Test result reporting
- Failure notifications 