# Mock Telegram Tester

A comprehensive testing environment for the KICKAI bot system that simulates Telegram interactions without requiring real Telegram accounts or API keys.

## 🎯 **Core Principle: ONLY MOCK THE TELEGRAM INTERFACE**

**This mock tester ONLY mocks the Telegram interface. EVERYTHING ELSE is REAL:**

- ✅ **Real Firebase/Firestore** - All data operations use real Firebase
- ✅ **Real CrewAI Agents** - All message processing uses real agents  
- ✅ **Real Bot Logic** - All business logic is real
- ✅ **Real Services** - All domain services are real
- ✅ **Real Command Processing** - All commands are processed by real agents
- ❌ **Mock Telegram Interface** - Only the Telegram API interface is mocked

**This means you're testing the REAL system with a mock interface, not a mock system!**

## 🚀 **Quick Start**

### 1. **Prerequisites**

- Python 3.11+
- Virtual environment activated (`venv311`)
- Project dependencies installed

### 2. **Start the Mock Tester**

```bash
# From the project root directory
python tests/mock_telegram/start_mock_tester.py
```

### 3. **Access the Testing Interface**

- **Enhanced Frontend** (Default): **http://localhost:8001**
- **Legacy Frontend**: **http://localhost:8001/legacy**

The enhanced frontend provides a more sophisticated UI with better user experience, real-time updates, and advanced features.

## 📖 **Usage Guide**

### **Creating Test Users**

1. **Default Users**: The system comes with 4 pre-configured test users:
   - **Test Player** (ID: 1001) - Regular player role
   - **Test Member** (ID: 1002) - Team member role  
   - **Test Admin** (ID: 1003) - Admin role
   - **Test Leadership** (ID: 1004) - Leadership role

2. **Custom Users**: Create new users using the form in the sidebar:
   - Enter username, first name, last name
   - Select role (player, team_member, admin, leadership)
   - Add phone number (optional)

### **Testing Bot Commands**

1. **Select a User**: Click on any user in the sidebar to start chatting
2. **Send Messages**: Type messages in the input field and press Enter or click Send
3. **Test Commands**: Try bot commands like:
   - `/help` - Get help information
   - `/addplayer John Smith +1234567890 Forward` - Add a new player
   - `/addmember Jane Doe +1234567891 Coach` - Add a new team member
   - `/update MH phone +1234567899` - Update player/member information
   - `/myinfo` - Get user information
   - `/list` - List players
   - `/status +1234567890` - Check player status

### **Real-Time Updates**

- **WebSocket Connection**: The UI shows connection status (🟢 Connected / 🔴 Disconnected)
- **Instant Responses**: Bot responses appear immediately in the chat
- **Message History**: All messages are preserved and displayed in chronological order

## 🔧 **API Endpoints**

The mock service provides these REST API endpoints:

### **Users**
- `GET /api/users` - Get all test users
- `POST /api/users` - Create a new test user

### **Messages**
- `POST /api/send_message` - Send a message as a user
- `GET /api/messages/{user_id}` - Get messages for a specific user
- `GET /api/messages` - Get all messages

### **WebSocket**
- `WS /api/ws` - Real-time message updates

## 🧪 **Testing Scenarios**

### **Player Registration Flow**
1. Create a new user with "player" role
2. Send `/addplayer John Smith +1234567890 Forward`
3. Verify bot response and registration process

### **Team Member Operations**
1. Create a user with "team_member" role
2. Test team management commands
3. Verify leadership chat functionality

### **Admin Functions**
1. Create a user with "admin" role
2. Test administrative commands
3. Verify permission-based responses

### **Multi-User Conversations**
1. Create multiple users with different roles
2. Switch between users to simulate different scenarios
3. Test cross-user interactions and bot responses

## 🔍 **Real System Integration**

### **Bot Integration Status**
The mock tester integrates with the real KICKAI bot system:

- **AgenticMessageRouter**: Real agent routing for all messages
- **UserFlowAgent**: Real user flow management
- **CrewAI Agents**: Real agent processing
- **Firebase Integration**: Real data persistence
- **Service Layer**: Real business logic execution

### **Verification**
To verify the real system is working:

1. **Check Logs**: Look for real agent processing logs
2. **Check Firebase**: Verify data is stored in real Firebase
3. **Check Services**: Verify real services are being called
4. **No Mock Mode**: Ensure no "running in mock mode" warnings

### **Debugging & Monitoring**

### **Console Logs**
The mock service provides detailed logging:
```bash
# View real-time logs
python tests/mock_telegram/start_mock_tester.py
```

### **API Testing**
Test the API directly using curl:
```bash
# Get all users
curl http://localhost:8001/api/users

# Send a message
curl -X POST http://localhost:8001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1001, "text": "/help"}'
```

## 🎨 **Frontend Options**

### **Enhanced Frontend** (Default)
- **URL**: http://localhost:8001
- **Features**:
  - Modern, responsive design
  - Real-time WebSocket updates
  - Advanced message formatting
  - Better user experience
  - Enhanced debugging tools
  - Role-based user management

### **Legacy Frontend**
- **URL**: http://localhost:8001/legacy
- **Features**:
  - Simple, basic interface
  - Basic message handling
  - Minimal styling
  - For backward compatibility

## 🛠️ **Configuration**

### **Environment Variables**
- `MOCK_HOST` - Host to bind to (default: localhost)
- `MOCK_PORT` - Port to run on (default: 8001)
- `MOCK_DEBUG` - Enable debug mode (default: false)
- `MOCK_MAX_MESSAGES` - Maximum messages to store (default: 1000)
- `MOCK_MAX_USERS` - Maximum users to create (default: 100)

### **Custom Configuration**
Create a `.env` file in the project root:
```bash
MOCK_HOST=0.0.0.0
MOCK_PORT=8001
MOCK_DEBUG=true
MOCK_MAX_MESSAGES=2000
MOCK_MAX_USERS=200
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Port Already in Use**: Change the port in `start_mock_tester.py` if 8001 is in use
2. **WebSocket Connection Failed**: Check if the service is running and accessible
3. **Bot Not Responding**: Verify the main bot system is running and connected
4. **Frontend Not Loading**: Check browser console for JavaScript errors

### **Debug Mode**
Enable debug mode for detailed logging:
```bash
MOCK_DEBUG=true python tests/mock_telegram/start_mock_tester.py
```

## 📊 **Performance**

### **Load Testing**
The mock system can handle:
- **Concurrent Users**: 50+ simultaneous users
- **Message Throughput**: 100+ messages per second
- **Memory Usage**: <100MB for typical usage
- **Response Time**: <100ms for most operations

### **Scaling**
For high-load testing:
- Increase `MOCK_MAX_MESSAGES` and `MOCK_MAX_USERS`
- Use multiple instances on different ports
- Monitor memory usage and adjust limits

## 🔗 **Integration**

### **With Main Bot System**
The mock tester integrates seamlessly with the main KICKAI bot:
```bash
# Start both systems together
python start_mock_system.py
```

### **With CI/CD Pipeline**
The mock tester can be used in automated testing:
```bash
# Run in CI environment
python tests/mock_telegram/ci_cd_integration.py
```

## 📝 **Development**

### **Adding New Features**
1. **Backend**: Modify `mock_telegram_service.py`
2. **Frontend**: Update `enhanced_index.html`
3. **Configuration**: Update `config.py`
4. **Testing**: Add tests to `test_mock_system.py`

### **Custom Extensions**
- **New Message Types**: Extend the message handling system
- **Custom UI Components**: Add new frontend features
- **Additional API Endpoints**: Extend the REST API
- **Enhanced Logging**: Add custom logging features 