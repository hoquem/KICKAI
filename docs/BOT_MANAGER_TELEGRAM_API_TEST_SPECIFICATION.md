# Bot Manager & Telegram API Integration - Comprehensive Test Specification

## Overview

This document outlines comprehensive testing requirements for the Bot Manager and Telegram API integration in the KICKAI system. The integration involves multiple components working together to provide seamless bot management and Telegram communication.

## Architecture Overview

### Core Components

1. **MultiBotManager**: Manages multiple bot instances for different teams
2. **TelegramBotService**: Handles Telegram API communication and message routing
3. **AgenticMessageRouter**: Routes all messages through the CrewAI agentic system
4. **CrewAI System**: AI agents that process and respond to messages
5. **Team Configuration**: Bot tokens and chat IDs stored in Firestore

### Integration Flow

```
Team Configuration (Firestore) 
    ↓
MultiBotManager (Loads Config)
    ↓
TelegramBotService (Creates Bot Instance)
    ↓
AgenticMessageRouter (Routes Messages)
    ↓
CrewAI System (Processes & Responds)
    ↓
Telegram API (Sends Response)
```

## Test Categories

### 1. Bot Manager Tests

#### 1.1 MultiBotManager Initialization Tests
- **Test Manager Creation**: Verify MultiBotManager initializes correctly
- **Test Configuration Loading**: Test loading bot configurations from Firestore
- **Test CrewAI Integration**: Verify CrewAI lifecycle manager integration
- **Test Error Handling**: Test initialization failures and recovery

#### 1.2 Bot Lifecycle Management Tests
- **Test Bot Startup**: Verify all bots start correctly
- **Test Bot Shutdown**: Verify clean shutdown of all bots
- **Test Bot Status Monitoring**: Test running status checks
- **Test Bot Configuration Validation**: Test incomplete configuration handling

#### 1.3 Multi-Team Bot Management Tests
- **Test Multiple Teams**: Verify handling of multiple team configurations
- **Test Team Isolation**: Ensure teams don't interfere with each other
- **Test Configuration Updates**: Test dynamic configuration updates
- **Test Team-Specific Features**: Test team-specific bot features

### 2. Telegram API Integration Tests

#### 2.1 TelegramBotService Tests
- **Test Service Creation**: Verify TelegramBotService initializes with valid token
- **Test Token Validation**: Test invalid token handling
- **Test Chat ID Configuration**: Test main and leadership chat ID setup
- **Test Service Lifecycle**: Test start/stop operations

#### 2.2 Message Handling Tests
- **Test Command Processing**: Test slash command handling
- **Test Natural Language**: Test natural language message processing
- **Test Contact Sharing**: Test phone number contact sharing
- **Test Message Routing**: Test message routing to appropriate handlers

#### 2.3 Response Handling Tests
- **Test Response Sending**: Test sending responses to users
- **Test Error Responses**: Test error message handling
- **Test Contact Button**: Test contact sharing button functionality
- **Test Message Formatting**: Test message formatting and escaping

### 3. Agentic Message Router Tests

#### 3.1 Message Conversion Tests
- **Test Telegram Update Conversion**: Test converting Telegram updates to domain messages
- **Test Command Extraction**: Test extracting commands from message text
- **Test Chat Type Detection**: Test determining chat type (main/leadership/private)
- **Test User Context**: Test user context extraction and validation

#### 3.2 Message Routing Tests
- **Test Agentic Routing**: Test routing messages through CrewAI system
- **Test Command Routing**: Test routing registered commands
- **Test Natural Language Routing**: Test routing natural language messages
- **Test Contact Share Routing**: Test routing contact sharing events

#### 3.3 Context Management Tests
- **Test User Registration Status**: Test checking if user is registered
- **Test Player/Member Status**: Test checking user roles
- **Test Chat Type Context**: Test chat type context handling
- **Test Execution Context**: Test execution context creation

### 4. CrewAI Integration Tests

#### 4.1 CrewAI System Tests
- **Test Crew Initialization**: Test CrewAI system initialization
- **Test Agent Creation**: Test creating and managing agents
- **Test Task Execution**: Test executing tasks through CrewAI
- **Test Response Processing**: Test processing CrewAI responses

#### 4.2 Agent Communication Tests
- **Test Agent Coordination**: Test agent coordination and communication
- **Test Tool Integration**: Test agent tool usage
- **Test Context Passing**: Test passing context between agents
- **Test Error Handling**: Test agent error handling and recovery

### 5. Configuration Management Tests

#### 5.1 Team Configuration Tests
- **Test Bot Token Storage**: Test storing bot tokens in Firestore
- **Test Chat ID Storage**: Test storing chat IDs in Firestore
- **Test Configuration Validation**: Test validating team configurations
- **Test Configuration Updates**: Test updating team configurations

#### 5.2 Environment Configuration Tests
- **Test Environment Variables**: Test environment variable loading
- **Test Configuration Overrides**: Test configuration override handling
- **Test Default Values**: Test default configuration values
- **Test Configuration Validation**: Test configuration validation

### 6. Integration Tests

#### 6.1 End-to-End Workflow Tests
- **Test Complete Message Flow**: Test complete message processing workflow
- **Test Multi-Team Operations**: Test operations across multiple teams
- **Test Bot Startup/Shutdown**: Test complete bot lifecycle
- **Test Error Recovery**: Test error recovery and system resilience

#### 6.2 Real Telegram API Tests
- **Test Bot Token Validation**: Test with real Telegram bot tokens
- **Test Message Sending**: Test sending messages to real Telegram chats
- **Test Webhook Handling**: Test webhook message handling
- **Test Rate Limiting**: Test Telegram API rate limiting

### 7. Security Tests

#### 7.1 Token Security Tests
- **Test Token Validation**: Test bot token validation
- **Test Token Storage**: Test secure token storage
- **Test Token Rotation**: Test token rotation procedures
- **Test Token Revocation**: Test token revocation handling

#### 7.2 Access Control Tests
- **Test Chat Access**: Test access control for different chat types
- **Test User Permissions**: Test user permission validation
- **Test Command Authorization**: Test command authorization
- **Test Data Privacy**: Test data privacy and protection

### 8. Performance Tests

#### 8.1 Load Testing
- **Test Concurrent Messages**: Test handling multiple concurrent messages
- **Test Multiple Teams**: Test performance with multiple teams
- **Test Message Queue**: Test message queue performance
- **Test Response Time**: Test response time under load

#### 8.2 Resource Management Tests
- **Test Memory Usage**: Test memory usage patterns
- **Test Connection Pooling**: Test connection pool management
- **Test Resource Cleanup**: Test resource cleanup on shutdown
- **Test Error Recovery**: Test error recovery performance

## Test Data Requirements

### Sample Bot Configurations
```python
test_bot_configs = [
    {
        "team_id": "test_team_alpha",
        "name": "Test Team Alpha",
        "bot_token": "test_bot_token_alpha",
        "main_chat_id": "-1001234567890",
        "leadership_chat_id": "-1001234567891"
    },
    {
        "team_id": "test_team_beta",
        "name": "Test Team Beta", 
        "bot_token": "test_bot_token_beta",
        "main_chat_id": "-1001234567892",
        "leadership_chat_id": "-1001234567893"
    }
]
```

### Sample Telegram Updates
```python
test_telegram_updates = [
    {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 987654321,
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe"
            },
            "chat": {
                "id": -1001234567890,
                "type": "supergroup",
                "title": "Test Team Alpha"
            },
            "text": "/help",
            "date": 1640995200
        }
    },
    {
        "update_id": 123456790,
        "message": {
            "message_id": 2,
            "from": {
                "id": 987654322,
                "first_name": "Jane",
                "last_name": "Smith",
                "username": "janesmith"
            },
            "chat": {
                "id": -1001234567891,
                "type": "supergroup",
                "title": "Test Team Alpha - Leadership"
            },
            "text": "What's the team status?",
            "date": 1640995260
        }
    }
]
```

### Sample Contact Shares
```python
test_contact_shares = [
    {
        "update_id": 123456791,
        "message": {
            "message_id": 3,
            "from": {
                "id": 987654323,
                "first_name": "Bob",
                "last_name": "Wilson",
                "username": "bobwilson"
            },
            "chat": {
                "id": -1001234567890,
                "type": "supergroup"
            },
            "contact": {
                "phone_number": "+1234567890",
                "first_name": "Bob",
                "last_name": "Wilson",
                "user_id": 987654323
            },
            "date": 1640995320
        }
    }
]
```

## Test Environment Setup

### Required Dependencies
- pytest
- pytest-asyncio
- pytest-mock
- python-telegram-bot
- firebase-admin
- telethon (for end-to-end tests)

### Test Configuration
```python
# test_config.py
TEST_BOT_TOKEN = "test_bot_token"
TEST_MAIN_CHAT_ID = "-1001234567890"
TEST_LEADERSHIP_CHAT_ID = "-1001234567891"
TEST_TEAM_ID = "test_team_alpha"

# Mock configurations
MOCK_TELEGRAM_UPDATE = {...}
MOCK_CREWAI_RESPONSE = {...}
```

### Test Environment Variables
```bash
# .env.test
TELEGRAM_BOT_TOKEN=test_bot_token
TELEGRAM_MAIN_CHAT_ID=-1001234567890
TELEGRAM_LEADERSHIP_CHAT_ID=-1001234567891
FIREBASE_PROJECT_ID=test-project
AI_PROVIDER=mock
```

## Test Execution Strategy

### 1. Unit Tests
- **Execution**: `pytest tests/unit/ -v`
- **Coverage**: Aim for 90%+ code coverage
- **Isolation**: Each test should be independent

### 2. Integration Tests
- **Execution**: `pytest tests/integration/ -v`
- **Database**: Use test database or mocks
- **External Services**: Mock external dependencies

### 3. End-to-End Tests
- **Execution**: `pytest tests/e2e/ -v`
- **Environment**: Use test environment with real services
- **Data**: Use test data sets

### 4. Performance Tests
- **Execution**: `pytest tests/performance/ -v`
- **Metrics**: Measure response times and throughput
- **Load**: Test under various load conditions

## Success Criteria

### Code Coverage
- **Minimum Coverage**: 90% for all modules
- **Critical Paths**: 100% coverage for core business logic
- **Error Handling**: 100% coverage for error scenarios

### Performance Benchmarks
- **Response Time**: < 2 seconds for message processing
- **Throughput**: > 10 messages/second for single bot
- **Memory Usage**: < 100MB for typical operations
- **Startup Time**: < 30 seconds for bot initialization

### Quality Gates
- **All Tests Pass**: 100% test pass rate
- **No Critical Bugs**: Zero critical security or data integrity issues
- **Documentation**: All public APIs documented
- **Error Handling**: Comprehensive error handling and logging

## Test Reporting

### Reports Generated
- **Coverage Report**: HTML coverage report
- **Performance Report**: Performance metrics and benchmarks
- **Security Report**: Security scan results
- **Test Summary**: Overall test results summary

### Metrics Tracked
- **Test Execution Time**: Total time for test suite
- **Coverage Percentage**: Code coverage metrics
- **Error Rate**: Percentage of failed tests
- **Performance Metrics**: Response times and throughput

## Maintenance

### Test Maintenance
- **Regular Updates**: Update tests when requirements change
- **Refactoring**: Refactor tests when code changes
- **Documentation**: Keep test documentation current

### Continuous Integration
- **Automated Testing**: Run tests on every commit
- **Quality Gates**: Block merges if tests fail
- **Monitoring**: Monitor test results over time

## Conclusion

This comprehensive test specification ensures the Bot Manager and Telegram API integration is thoroughly tested across all layers and scenarios. The testing strategy covers unit, integration, and end-to-end testing with proper isolation and realistic test data. 