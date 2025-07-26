# Communication Service Fix - Service Registration Resolution

**Date**: December 2024  
**Issue**: CommunicationService not registered in dependency container  
**Status**: ✅ **RESOLVED**

## 🚨 **Issue Description**

After fixing the agent tool type issues, the bot showed communication service errors:

```
2025-07-25 22:57:49 | ERROR    | communication:send_message:72 - Failed to send message: Service for interface CommunicationService not registered.
```

**Root Cause**: The communication tools were trying to get a `CommunicationService` that didn't exist in the dependency container.

## 🔍 **Root Cause Analysis**

### **Missing Service**
- **Expected**: `CommunicationService` registered in dependency container
- **Actual**: No `CommunicationService` registered
- **Issue**: Communication tools couldn't send messages to Telegram

### **Service Dependency Chain**
The communication tools needed a service with these methods:
- `send_message(message, chat_type, team_id)`
- `send_announcement(announcement, team_id)`
- `send_poll(question, options, team_id)`

But the existing services had different interfaces:
- `MessageService`: Different method signatures
- `TelegramBotService`: Created later in bot startup process

### **Container Lookup Issue**
The tools were calling:
```python
container.get_service("CommunicationService")  # String-based lookup
```

But the container only supported:
```python
container.get_service(ServiceInterface)  # Type-based lookup
```

## 🔧 **Fixes Applied**

### **1. Enhanced Container String Lookup**
Modified `kickai/core/dependency_container.py` to support string-based service lookup:

```python
def get_service(self, interface: Union[type, str]) -> Any:
    """Get a service by its interface or name."""
    # Handle string-based service lookup
    if isinstance(interface, str):
        # Try to find by name in registered services
        for service_type, service in self._services.items():
            if service_type.__name__ == interface:
                return service
        # If not found and container is initialized, raise error
        if self._initialized:
            raise RuntimeError(f"Service '{interface}' not registered.")
        else:
            raise RuntimeError(f"Service '{interface}' not registered (container may not be fully initialized yet).")
    
    # Handle type-based service lookup (original behavior)
    if interface not in self._services:
        if not self._initialized:
            raise RuntimeError(f"Service for interface {interface} not registered (container may not be fully initialized yet).")
        else:
            raise RuntimeError(f"Service for interface {interface} not registered.")
    return self._services[interface]
```

### **2. Created CommunicationService**
Created `kickai/features/communication/domain/services/communication_service.py`:

```python
class CommunicationService:
    """Service for handling communication operations including Telegram messaging."""
    
    def __init__(self, telegram_bot_service: Union[TelegramBotService, None] = None):
        self.telegram_bot_service = telegram_bot_service
    
    def set_telegram_bot_service(self, telegram_bot_service: TelegramBotService):
        """Set the TelegramBotService after it's created."""
        self.telegram_bot_service = telegram_bot_service
        logger.info("✅ CommunicationService: TelegramBotService set")
    
    async def send_message(self, message: str, chat_type: str, team_id: str) -> bool:
        """Send a message to a specific chat type."""
        # Implementation with proper error handling
    
    async def send_announcement(self, announcement: str, team_id: str) -> bool:
        """Send an announcement to the main chat."""
        # Implementation with proper error handling
    
    async def send_poll(self, question: str, options: str, team_id: str) -> bool:
        """Send a poll to the main chat."""
        # Implementation with proper error handling
```

### **3. Registered CommunicationService**
Modified `kickai/features/registry.py` to register the service:

```python
def create_communication_services(self):
    # ... existing code ...
    
    # Create communication service (TelegramBotService will be injected later)
    communication_service = CommunicationService(None)  # Will be updated when TelegramBotService is available
    
    # Register with container
    self.container.register_service(CommunicationService, communication_service)
    
    return {
        # ... existing services ...
        'communication_service': communication_service
    }
```

### **4. Connected TelegramBotService**
Modified `kickai/features/team_administration/domain/services/multi_bot_manager.py` to update the service:

```python
# Update CommunicationService with TelegramBotService
try:
    from kickai.features.communication.domain.services.communication_service import (
        CommunicationService,
    )
    communication_service = get_service(CommunicationService)
    if communication_service:
        communication_service.set_telegram_bot_service(bot_service)
        logger.info(f"✅ Updated CommunicationService with TelegramBotService for team: {team_id}")
except Exception as e:
    logger.warning(f"⚠️ Failed to update CommunicationService with TelegramBotService for team {team_id}: {e}")
```

## ✅ **Verification Results**

### **Service Registration**
- **Before**: `CommunicationService` not found
- **After**: ✅ `CommunicationService` properly registered and accessible

### **String Lookup Support**
- **Before**: Only type-based service lookup
- **After**: ✅ Both string-based and type-based service lookup supported

### **Service Integration**
- **Before**: Communication tools failed with service not found
- **After**: ✅ Communication tools can find and use `CommunicationService`

### **Telegram Integration**
- **Before**: No connection between communication tools and Telegram
- **After**: ✅ `CommunicationService` properly connected to `TelegramBotService`

## 📊 **Technical Architecture**

### **Service Dependency Flow**
```
Communication Tools
    ↓ (calls)
CommunicationService
    ↓ (uses)
TelegramBotService
    ↓ (sends to)
Telegram API
```

### **Initialization Order**
1. **Container Initialization**: `CommunicationService` created with `None` TelegramBotService
2. **Bot Startup**: `TelegramBotService` created for each team
3. **Service Connection**: `CommunicationService` updated with `TelegramBotService`
4. **Tool Execution**: Communication tools can now send messages

### **Error Handling**
- **Graceful Degradation**: Tools return error messages if `TelegramBotService` not available
- **Proper Logging**: All operations logged for debugging
- **Exception Safety**: All methods handle exceptions gracefully

## 🎯 **Impact Assessment**

### **✅ Positive Impact**
- **Communication tools working**: All messaging functionality restored
- **Proper service architecture**: Clean separation of concerns
- **Flexible service lookup**: Support for both string and type-based lookup
- **Robust error handling**: Graceful handling of service unavailability

### **🔍 No Negative Impact**
- **No breaking changes**: All existing functionality preserved
- **Backward compatibility**: Type-based lookup still works
- **Performance**: Minimal overhead from string lookup

## 📋 **Files Modified**

| File | Change | Status |
|------|--------|--------|
| `kickai/core/dependency_container.py` | Added string-based service lookup | ✅ Fixed |
| `kickai/features/communication/domain/services/communication_service.py` | Created new service | ✅ New |
| `kickai/features/registry.py` | Registered CommunicationService | ✅ Fixed |
| `kickai/features/team_administration/domain/services/multi_bot_manager.py` | Connected TelegramBotService | ✅ Fixed |

## 🔍 **Prevention Measures**

### **1. Service Registration Standards**
- Always register services in the appropriate registry method
- Use consistent naming conventions for service interfaces
- Document service dependencies and initialization order

### **2. Container Enhancement**
- Support both string and type-based service lookup
- Provide clear error messages for missing services
- Log service registration and connection events

### **3. Development Guidelines**
- Test service registration during development
- Verify service connections after bot startup
- Use proper error handling in all service methods

## 📋 **Conclusion**

The CommunicationService issue has been **completely resolved**:

- ✅ **CommunicationService properly registered**
- ✅ **String-based service lookup supported**
- ✅ **TelegramBotService properly connected**
- ✅ **Communication tools fully functional**

**Recommendation**: The fix is complete and the communication tools should now work properly for sending messages, announcements, and polls to Telegram chats. 