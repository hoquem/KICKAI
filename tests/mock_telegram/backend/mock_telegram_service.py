"""
Mock Telegram Bot Service

This service mimics the Telegram Bot API to enable cost-effective end-to-end testing
without requiring real phone numbers or Telegram accounts.
"""

import asyncio
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import bot integration (optional - will be skipped if not available)
try:
    from .bot_integration import process_mock_message_sync
    BOT_INTEGRATION_AVAILABLE = True
    logger.info("Bot integration available")
except ImportError:
    BOT_INTEGRATION_AVAILABLE = False
    logger.warning("Bot integration not available - running in standalone mode")
    def process_mock_message_sync(message_data):
        return {"status": "bot_integration_not_available"}


class MessageType(str, Enum):
    """Types of messages that can be sent/received"""
    TEXT = "text"
    COMMAND = "command"
    PHOTO = "photo"
    DOCUMENT = "document"
    LOCATION = "location"


class UserRole(str, Enum):
    """User roles for testing different scenarios"""
    PLAYER = "player"
    TEAM_MEMBER = "team_member"
    ADMIN = "admin"
    LEADERSHIP = "leadership"


class ChatType(str, Enum):
    """Chat types supported by the system"""
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


@dataclass
class MockUser:
    """Represents a mock Telegram user"""
    id: int
    username: str
    first_name: str
    last_name: Optional[str] = None
    role: UserRole = UserRole.PLAYER
    phone_number: Optional[str] = None
    is_bot: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Validate user data after initialization"""
        if not self.username or not self.first_name:
            raise ValueError("Username and first_name are required")
        if self.id <= 0:
            raise ValueError("User ID must be positive")


@dataclass
class MockChat:
    """Represents a mock Telegram chat"""
    id: int
    type: ChatType
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_main_chat: bool = False
    is_leadership_chat: bool = False
    
    def __post_init__(self):
        """Validate chat data after initialization"""
        if self.id <= 0:
            raise ValueError("Chat ID must be positive")
        if self.type not in [e.value for e in ChatType]:
            raise ValueError("Invalid chat type")
    
    def get_chat_context(self) -> str:
        """Get the chat context for bot routing"""
        if self.is_leadership_chat:
            return "leadership"
        elif self.is_main_chat:
            return "main"
        else:
            return "private"


@dataclass
class MockMessage:
    """Represents a mock Telegram message"""
    message_id: int
    from_user: MockUser
    chat: MockChat
    date: datetime
    text: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    reply_to_message: Optional['MockMessage'] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        return {
            "message_id": self.message_id,
            "from": {
                "id": self.from_user.id,
                "username": self.from_user.username,
                "first_name": self.from_user.first_name,
                "last_name": self.from_user.last_name,
                "is_bot": self.from_user.is_bot
            },
            "chat": {
                "id": self.chat.id,
                "type": self.chat.type,
                "title": self.chat.title,
                "username": self.chat.username,
                "first_name": self.chat.first_name,
                "last_name": self.chat.last_name,
                "is_main_chat": self.chat.is_main_chat,
                "is_leadership_chat": self.chat.is_leadership_chat
            },
            "date": int(self.date.timestamp()),
            "text": self.text
        }


class SendMessageRequest(BaseModel):
    """Request model for sending messages"""
    user_id: int = Field(..., gt=0, description="User ID must be positive")
    chat_id: int = Field(..., gt=0, description="Chat ID must be positive")
    text: str = Field(..., min_length=1, max_length=4096, description="Message text")
    message_type: MessageType = MessageType.TEXT
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Message text cannot be empty")
        return v.strip()


class CreateUserRequest(BaseModel):
    """Request model for creating test users"""
    username: str = Field(..., min_length=1, max_length=32, description="Username")
    first_name: str = Field(..., min_length=1, max_length=64, description="First name")
    last_name: Optional[str] = Field(None, max_length=64, description="Last name")
    role: UserRole = UserRole.PLAYER
    phone_number: Optional[str] = Field(None, regex=r'^\+?[1-9]\d{1,14}$', description="Phone number")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v.lower()


class MockTelegramService:
    """Main service class for mock Telegram functionality"""
    
    def __init__(self, max_messages: int = 1000, max_users: int = 100, team_name: str = "KickAI Testing"):
        self._lock = threading.RLock()  # Thread safety
        self.users: Dict[int, MockUser] = {}
        self.chats: Dict[int, MockChat] = {}
        self.messages: List[MockMessage] = []
        self.websocket_connections: Set[WebSocket] = set()  # Use set for O(1) operations
        self.message_counter = 1
        self.max_messages = max_messages
        self.max_users = max_users
        self.team_name = team_name
        
        # Initialize with some default test users and group chats
        self._initialize_default_users()
        self._initialize_group_chats()
        logger.info(f"MockTelegramService initialized with {len(self.users)} default users and group chats")
    
    def _initialize_default_users(self):
        """Initialize with default test users"""
        default_users = [
            MockUser(1001, "test_player", "Test Player", role=UserRole.PLAYER, phone_number="+1234567890"),
            MockUser(1002, "test_member", "Test Member", role=UserRole.TEAM_MEMBER, phone_number="+1234567891"),
            MockUser(1003, "test_admin", "Test Admin", role=UserRole.ADMIN, phone_number="+1234567892"),
            MockUser(1004, "test_leadership", "Test Leadership", role=UserRole.LEADERSHIP, phone_number="+1234567893"),
        ]
        
        with self._lock:
            for user in default_users:
                self.users[user.id] = user
                
                # Create private chat for each user
                chat = MockChat(
                    id=user.id,
                    type=ChatType.PRIVATE,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                self.chats[chat.id] = chat
    
    def _initialize_group_chats(self):
        """Initialize group chats for the team"""
        with self._lock:
            # Main chat (all users can access)
            main_chat = MockChat(
                id=2001,  # Group chat IDs start from 2000
                type=ChatType.GROUP,
                title=self.team_name,
                is_main_chat=True
            )
            self.chats[main_chat.id] = main_chat
            
            # Leadership chat (only team members, admins, and leadership can access)
            leadership_chat = MockChat(
                id=2002,
                type=ChatType.GROUP,
                title=f"{self.team_name} - Leadership",
                is_leadership_chat=True
            )
            self.chats[leadership_chat.id] = leadership_chat
            
            logger.info(f"Created group chats: Main ({main_chat.id}), Leadership ({leadership_chat.id})")
    
    def get_accessible_chats_for_user(self, user_id: int) -> List[MockChat]:
        """Get all chats accessible to a specific user"""
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        accessible_chats = []
        
        with self._lock:
            for chat in self.chats.values():
                # Private chat - only for the user
                if chat.type == ChatType.PRIVATE and chat.id == user_id:
                    accessible_chats.append(chat)
                
                # Main chat - accessible to all users
                elif chat.is_main_chat:
                    accessible_chats.append(chat)
                
                # Leadership chat - only for team members, admins, and leadership
                elif chat.is_leadership_chat and user.role in [UserRole.TEAM_MEMBER, UserRole.ADMIN, UserRole.LEADERSHIP]:
                    accessible_chats.append(chat)
        
        return accessible_chats
    
    def can_user_access_chat(self, user_id: int, chat_id: int) -> bool:
        """Check if a user can access a specific chat"""
        if user_id not in self.users or chat_id not in self.chats:
            return False
        
        user = self.users[user_id]
        chat = self.chats[chat_id]
        
        # Private chat - only for the user
        if chat.type == ChatType.PRIVATE:
            return chat.id == user_id
        
        # Main chat - accessible to all users
        if chat.is_main_chat:
            return True
        
        # Leadership chat - only for team members, admins, and leadership
        if chat.is_leadership_chat:
            return user.role in [UserRole.TEAM_MEMBER, UserRole.ADMIN, UserRole.LEADERSHIP]
        
        return False
    
    async def connect_websocket(self, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        with self._lock:
            self.websocket_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.websocket_connections)}")
    
    async def disconnect_websocket(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        with self._lock:
            if websocket in self.websocket_connections:
                self.websocket_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.websocket_connections)}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
            
        message_json = json.dumps(message)
        disconnected = set()
        
        # Create a copy to avoid modification during iteration
        connections = list(self.websocket_connections)
        
        for websocket in connections:
            try:
                await websocket.send_text(message_json)
            except (WebSocketDisconnect, ConnectionResetError, Exception) as e:
                logger.warning(f"WebSocket error during broadcast: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            await self.disconnect_websocket(websocket)
    
    def _cleanup_old_messages(self):
        """Remove old messages to prevent memory leaks"""
        with self._lock:
            if len(self.messages) > self.max_messages:
                # Keep only the most recent messages
                self.messages = self.messages[-self.max_messages:]
                logger.info(f"Cleaned up messages. Current count: {len(self.messages)}")
    
    def create_user(self, request: CreateUserRequest) -> MockUser:
        """Create a new test user"""
        with self._lock:
            if len(self.users) >= self.max_users:
                raise HTTPException(status_code=400, detail="Maximum number of users reached")
            
            # Check for duplicate username
            if any(user.username == request.username for user in self.users.values()):
                raise HTTPException(status_code=400, detail="Username already exists")
            
            user_id = max(self.users.keys()) + 1 if self.users else 1001
            
            try:
                user = MockUser(
                    id=user_id,
                    username=request.username,
                    first_name=request.first_name,
                    last_name=request.last_name,
                    role=request.role,
                    phone_number=request.phone_number
                )
                
                self.users[user_id] = user
                
                # Create private chat for the user
                chat = MockChat(
                    id=user_id,
                    type=ChatType.PRIVATE,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                self.chats[chat.id] = chat
                
                logger.info(f"Created new user: {user.first_name} (@{user.username})")
                return user
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
    
    def send_message(self, request: SendMessageRequest) -> MockMessage:
        """Send a message as if from a user"""
        with self._lock:
            if request.user_id not in self.users:
                raise HTTPException(status_code=404, detail="User not found")
            
            if request.chat_id not in self.chats:
                raise HTTPException(status_code=404, detail="Chat not found")
            
            # Check if user can access this chat
            if not self.can_user_access_chat(request.user_id, request.chat_id):
                raise HTTPException(status_code=403, detail="User cannot access this chat")
            
            user = self.users[request.user_id]
            chat = self.chats[request.chat_id]
            
            message = MockMessage(
                message_id=self.message_counter,
                from_user=user,
                chat=chat,
                date=datetime.now(timezone.utc),
                text=request.text,
                message_type=request.message_type
            )
            
            self.messages.append(message)
            self.message_counter += 1
            
            # Cleanup old messages
            self._cleanup_old_messages()
            
            chat_context = chat.get_chat_context()
            logger.info(f"Message sent: {user.first_name} -> {chat_context} chat -> {request.text[:50]}...")
            
            # Broadcast the message to WebSocket clients
            asyncio.create_task(self.broadcast_message({
                "type": "new_message",
                "message": message.to_dict(),
                "chat_context": chat_context
            }))
            
            # Process message through bot system with chat context
            if BOT_INTEGRATION_AVAILABLE:
                try:
                    # Add chat context to message data for bot routing
                    message_data = message.to_dict()
                    message_data["chat_context"] = chat_context
                    
                    bot_response = process_mock_message_sync(message_data)
                    if bot_response and bot_response.get("status") != "processing":
                        # Broadcast bot response
                        asyncio.create_task(self.broadcast_message({
                            "type": "bot_response",
                            "message": bot_response,
                            "chat_context": chat_context
                        }))
                except Exception as e:
                    logger.error(f"Error processing message through bot: {e}")
            
            return message
    
    def get_user_messages(self, user_id: int, limit: int = 50) -> List[MockMessage]:
        """Get messages for a specific user (from all accessible chats)"""
        with self._lock:
            if user_id not in self.users:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get all chats accessible to the user
            accessible_chat_ids = [chat.id for chat in self.get_accessible_chats_for_user(user_id)]
            
            user_messages = [
                msg for msg in self.messages 
                if msg.chat.id in accessible_chat_ids
            ]
            
            return user_messages[-limit:]
    
    def get_chat_messages(self, chat_id: int, limit: int = 50) -> List[MockMessage]:
        """Get messages for a specific chat"""
        with self._lock:
            if chat_id not in self.chats:
                raise HTTPException(status_code=404, detail="Chat not found")
            
            chat_messages = [
                msg for msg in self.messages 
                if msg.chat.id == chat_id
            ]
            
            return chat_messages[-limit:]
    
    def get_all_users(self) -> List[MockUser]:
        """Get all test users"""
        with self._lock:
            return list(self.users.values())
    
    def get_all_chats(self) -> List[MockChat]:
        """Get all chats"""
        with self._lock:
            return list(self.chats.values())
    
    def get_group_chats(self) -> List[MockChat]:
        """Get all group chats (main and leadership)"""
        with self._lock:
            return [
                chat for chat in self.chats.values()
                if chat.is_main_chat or chat.is_leadership_chat
            ]
    
    def get_all_messages(self, limit: int = 100) -> List[MockMessage]:
        """Get all messages"""
        with self._lock:
            return self.messages[-limit:]
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        with self._lock:
            return {
                "total_users": len(self.users),
                "total_chats": len(self.chats),
                "group_chats": len([c for c in self.chats.values() if c.is_main_chat or c.is_leadership_chat]),
                "total_messages": len(self.messages),
                "active_websockets": len(self.websocket_connections),
                "message_counter": self.message_counter,
                "bot_integration_available": BOT_INTEGRATION_AVAILABLE,
                "team_name": self.team_name
            }


# Global service instance
mock_service = MockTelegramService()

# FastAPI app
app = FastAPI(
    title="Mock Telegram Bot Service",
    description="A mock Telegram Bot API for end-to-end testing",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mock Telegram Bot Service",
        "version": "1.0.0",
        "status": "running",
        "team_name": mock_service.team_name
    }


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return mock_service.get_service_stats()


@app.get("/users")
async def get_users():
    """Get all test users"""
    return [asdict(user) for user in mock_service.get_all_users()]


@app.post("/users")
async def create_user(request: CreateUserRequest):
    """Create a new test user"""
    user = mock_service.create_user(request)
    return asdict(user)


@app.get("/chats")
async def get_chats():
    """Get all chats"""
    return [asdict(chat) for chat in mock_service.get_all_chats()]


@app.get("/chats/group")
async def get_group_chats():
    """Get group chats (main and leadership)"""
    return [asdict(chat) for chat in mock_service.get_group_chats()]


@app.get("/users/{user_id}/chats")
async def get_user_chats(user_id: int):
    """Get all chats accessible to a specific user"""
    accessible_chats = mock_service.get_accessible_chats_for_user(user_id)
    return [asdict(chat) for chat in accessible_chats]


@app.post("/send_message")
async def send_message(request: SendMessageRequest):
    """Send a message as a user"""
    message = mock_service.send_message(request)
    return message.to_dict()


@app.post("/bot_response")
async def bot_response(response_data: dict):
    """Receive bot response and broadcast to WebSocket clients"""
    await mock_service.broadcast_message({
        "type": "bot_response",
        "message": response_data
    })
    return {"status": "broadcasted"}


@app.get("/messages/{user_id}")
async def get_user_messages(user_id: int, limit: int = 50):
    """Get messages for a specific user (from all accessible chats)"""
    messages = mock_service.get_user_messages(user_id, limit)
    return [msg.to_dict() for msg in messages]


@app.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: int, limit: int = 50):
    """Get messages for a specific chat"""
    messages = mock_service.get_chat_messages(chat_id, limit)
    return [msg.to_dict() for msg in messages]


@app.get("/messages")
async def get_all_messages(limit: int = 100):
    """Get all messages"""
    messages = mock_service.get_all_messages(limit)
    return [msg.to_dict() for msg in messages]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await mock_service.connect_websocket(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        await mock_service.disconnect_websocket(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await mock_service.disconnect_websocket(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "mock_telegram_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 