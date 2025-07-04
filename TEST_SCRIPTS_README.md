# KICKAI Test Scripts

This directory contains comprehensive test scripts to demonstrate and validate the KICKAI system's capabilities, particularly focusing on natural language processing, CrewAI agent integration, and end-to-end workflows.

## 🎯 Overview

The test scripts validate the following key aspects of the KICKAI system:

1. **Natural Language Command Processing** - Enhanced LLM-based command interpretation
2. **LLM-Enhanced Onboarding** - Intelligent player onboarding workflow
3. **CrewAI Agent Integration** - Multi-agent system capabilities
4. **End-to-End Workflow** - Complete system validation

## 📋 Test Scripts

### 1. `test_natural_language_commands.py`
**Purpose**: Demonstrates and validates the enhanced natural language command processing capabilities.

**Features Tested**:
- `/myinfo` with natural language queries
- `/list` with natural language filtering
- `/stats` with natural language queries
- `/status` command functionality
- Natural language queries without command prefixes
- Help command functionality

**Example Queries Tested**:
```bash
/myinfo What's my phone number?
/list Show me strikers
/stats How many FA registered?
What's my status?
Show me strikers
```

### 2. `test_onboarding_llm_enhanced.py`
**Purpose**: Validates the LLM-enhanced onboarding workflow with natural language responses.

**Features Tested**:
- Profile completion with natural language
- Emergency contact handling
- Date of birth processing
- FA eligibility assessment
- FA registration workflow
- New member detection

**Example Responses Tested**:
```bash
"Name: John Smith, Phone: 07987654321, Position: midfielder"
"My emergency contact is Jane Smith, 07987654321"
"I was born on 15th May 1995"
"I am eligible for FA registration"
```

### 3. `test_crewai_integration.py`
**Purpose**: Demonstrates and validates the CrewAI agent integration and capabilities.

**Features Tested**:
- Intelligent System initialization
- Crew Agents creation
- Agent routing and capabilities
- Multi-agent collaboration
- Agent learning and adaptation
- System performance metrics

**Agents Tested**:
- Message Processing Specialist
- Team Manager
- Player Coordinator
- Match Analyst
- Communication Specialist
- Finance Manager
- Squad Selection Specialist
- Analytics Specialist
- Learning Agent

### 4. `test_end_to_end_workflow.py`
**Purpose**: Comprehensive end-to-end workflow validation.

**Phases Tested**:
1. **Player Registration and Onboarding**
   - Admin player addition
   - Onboarding workflow completion
   
2. **Natural Language Command Processing**
   - All command types with natural language
   
3. **Natural Language Queries (No Command Prefix)**
   - Direct natural language interaction
   
4. **Admin Commands and Player Management**
   - Admin functionality
   - Player approval workflow
   
5. **Enhanced Features**
   - Help system
   - Invitation system
   - New member detection
   
6. **System Integration Validation**
   - Data consistency
   - Error handling
   
7. **Performance and Scalability**
   - Concurrent request handling
   - Performance metrics

## 🚀 Running the Tests

### Prerequisites
1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (if using real services):
   ```bash
   cp env.example env.local
   # Edit env.local with your configuration
   ```

### Running Individual Tests

```bash
# Test natural language commands
python test_natural_language_commands.py

# Test LLM-enhanced onboarding
python test_onboarding_llm_enhanced.py

# Test CrewAI integration
python test_crewai_integration.py

# Test end-to-end workflow
python test_end_to_end_workflow.py
```

### Running All Tests

Use the test runner script to execute all tests in sequence:

```bash
python run_all_tests.py
```

This will:
- Run all test scripts
- Provide detailed output for each test
- Generate a summary report
- Exit with appropriate status code

## 📊 Expected Results

### Natural Language Commands
- ✅ All `/myinfo` queries processed correctly
- ✅ `/list` filtering works with natural language
- ✅ `/stats` provides relevant information
- ✅ `/status` command functions properly
- ✅ Natural language queries without prefixes work

### Onboarding Workflow
- ✅ Profile completion with natural language
- ✅ Emergency contact processing
- ✅ Date of birth validation
- ✅ FA eligibility assessment
- ✅ Complete onboarding flow

### CrewAI Integration
- ✅ Intelligent System initializes
- ✅ Crew Agents created successfully
- ✅ Agent routing works correctly
- ✅ Multi-agent collaboration functions
- ✅ Learning capabilities active

### End-to-End Workflow
- ✅ Complete player lifecycle
- ✅ All command types functional
- ✅ Error handling robust
- ✅ Performance acceptable
- ✅ Data consistency maintained

## 🔧 Configuration

### Mock Data Store
All tests use the `MockDataStore` for testing, which provides:
- In-memory data storage
- No external dependencies
- Consistent test environment
- Fast execution

### Test Data
Tests create sample players:
- Alima Begum (AB1) - Striker
- Ehsaan Hoque (EH1) - Defender
- John Smith (JS1) - Midfielder
- Sarah Johnson (SJ1) - Goalkeeper
- Mike Wilson (MW1) - Forward

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the correct directory
   - Check that all dependencies are installed
   - Verify Python path includes the project root

2. **LLM Configuration Issues**
   - Tests will work with mock data even without LLM
   - For full functionality, configure AI provider in `config/bot_config.json`

3. **Timeout Issues**
   - Tests have a 5-minute timeout
   - If tests timeout, check for infinite loops or blocking operations

4. **Memory Issues**
   - Tests use mock data store (no memory issues expected)
   - If using real services, ensure adequate memory

### Debug Mode

To run tests with more verbose output:

```bash
# Set logging level
export PYTHONPATH=.
python -u test_natural_language_commands.py
```

## 📈 Performance Metrics

Expected performance metrics:
- **Response Time**: < 2 seconds per command
- **Accuracy**: 95%+ for natural language processing
- **Concurrent Requests**: Handle multiple simultaneous queries
- **Memory Usage**: Minimal (using mock data store)

## 🔄 Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run KICKAI Tests
  run: |
    python run_all_tests.py
  timeout-minutes: 10
```

## 📝 Contributing

When adding new features to KICKAI:

1. **Update existing tests** to cover new functionality
2. **Add new test cases** for new commands or workflows
3. **Ensure all tests pass** before submitting changes
4. **Update this README** if adding new test scripts

## 🎯 Success Criteria

A successful test run should show:
- ✅ All test scripts execute without errors
- ✅ Natural language processing works correctly
- ✅ CrewAI agents function properly
- ✅ End-to-end workflows complete successfully
- ✅ Performance metrics meet expectations
- ✅ Error handling works as expected

## 📞 Support

If you encounter issues with the test scripts:

1. Check the troubleshooting section above
2. Review the test output for specific error messages
3. Ensure your environment matches the prerequisites
4. Contact the development team with specific error details

---

**Note**: These tests are designed to validate the KICKAI system's capabilities and demonstrate the enhanced natural language processing and CrewAI integration features. They provide confidence that the system is working correctly and can handle real-world usage scenarios. 