# 🤖 Mock Telegram Tester

A comprehensive testing system that mimics Telegram Bot API behavior, allowing you to test your KICKAI bot system without requiring real phone numbers or Telegram accounts.

## 🎯 **Features**

- ✅ **Cost-Effective Testing** - No phone numbers or Telegram API costs
- ✅ **Multi-User Simulation** - Create and switch between different user personas
- ✅ **Real-Time Messaging** - Send messages and see bot responses instantly
- ✅ **Full Bot Integration** - Uses your existing bot system without modifications
- ✅ **Web UI Dashboard** - Modern, responsive interface for testing
- ✅ **User Management** - Create test users with different roles
- ✅ **Chat History** - Maintain conversation context per user
- ✅ **WebSocket Support** - Real-time message updates

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web UI        │    │  Mock Telegram   │    │  KICKAI Bot     │
│   (Frontend)    │◄──►│  Service         │◄──►│  System         │
│                 │    │  (Backend)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
   User Interface         Message Routing          Bot Processing
   - User Selection       - WebSocket              - Agent Routing
   - Message Input        - API Endpoints          - Command Handling
   - Chat Display         - State Management       - Response Generation
```

## 🚀 **Quick Start**

### 1. **Install Dependencies**

```bash
# Install backend dependencies
pip install -r tests/mock_telegram/backend/requirements.txt

# The frontend is a simple HTML file - no build process needed!
```

### 2. **Start the Mock Tester**

```bash
# From the project root directory
python tests/mock_telegram/start_mock_tester.py
```

### 3. **Access the Testing Interface**

Open your browser and go to: **http://localhost:8001**

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

## 🔍 **Debugging & Monitoring**

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
  -d '{"user_id": 1001, "chat_id": 1001, "text": "/help"}'
```

### **WebSocket Testing**
Use browser dev tools to monitor WebSocket messages:
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8001/api/ws');
ws.onmessage = (event) => console.log('WS Message:', JSON.parse(event.data));
```

## 🛠️ **Development**

### **Adding New Features**

1. **Backend Extensions**: Modify `mock_telegram_service.py` to add new API endpoints
2. **Frontend Enhancements**: Edit `frontend/index.html` to improve the UI
3. **Integration Updates**: Update `bot_integration.py` for new bot features

### **Customizing User Roles**

Edit the `UserRole` enum in `mock_telegram_service.py`:
```python
class UserRole(str, Enum):
    PLAYER = "player"
    TEAM_MEMBER = "team_member"
    ADMIN = "admin"
    LEADERSHIP = "leadership"
    # Add new roles here
    COACH = "coach"
    REFEREE = "referee"
```

### **Message Types**

Extend the `MessageType` enum for different message types:
```python
class MessageType(str, Enum):
    TEXT = "text"
    COMMAND = "command"
    PHOTO = "photo"
    DOCUMENT = "document"
    LOCATION = "location"
    # Add new types here
    VOICE = "voice"
    VIDEO = "video"
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Import Errors**: Ensure you're running from the project root directory
2. **Port Conflicts**: Change the port in `start_mock_tester.py` if 8001 is in use
3. **WebSocket Disconnection**: The UI automatically reconnects every 5 seconds
4. **Bot Integration Issues**: Check that your bot system is properly configured

### **Error Messages**

- **"User not found"**: The user ID doesn't exist in the mock system
- **"Chat not found"**: The chat ID doesn't exist (should match user ID for private chats)
- **"Connection refused"**: The mock service isn't running on the expected port

## 📋 **Testing Checklist**

- [ ] Mock service starts without errors
- [ ] Web UI loads and connects to WebSocket
- [ ] Default users are displayed in sidebar
- [ ] Can create new users with different roles
- [ ] Can send messages and receive bot responses
- [ ] Bot commands work correctly
- [ ] Chat history is preserved
- [ ] Real-time updates work via WebSocket
- [ ] Different user roles get appropriate responses

## 🤝 **Integration with Existing Tests**

The mock system can be integrated with your existing test suite:

```python
# In your test files
from tests.mock_telegram.backend.bot_integration import process_mock_message_sync

def test_player_registration():
    # Send registration message
    response = process_mock_message_sync({
        "user_id": 1001,
        "text": "/addplayer John Smith +1234567890 Forward"
    })
    
    # Assert expected response
    assert "registration" in response.get("text", "").lower()
```

## 📈 **Performance**

- **Response Time**: < 100ms for most operations
- **Concurrent Users**: Supports multiple simultaneous connections
- **Memory Usage**: Minimal overhead, stores messages in memory
- **Scalability**: Can handle hundreds of test users and messages

---

**Happy Testing! 🎉**

This mock system provides a powerful, cost-effective way to test your KICKAI bot system without the overhead of real Telegram accounts or phone numbers. 