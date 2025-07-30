"""
Mock Telegram Bot Service

This service mimics the Telegram Bot API to enable cost-effective end-to-end testing
without requiring real phone numbers or Telegram accounts.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import bot integration (optional - will be skipped if not available)
try:
    from .bot_integration import process_mock_message_sync
    BOT_INTEGRATION_AVAILABLE = True
except ImportError:
    BOT_INTEGRATION_AVAILABLE = False
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


@dataclass
class MockChat:
    """Represents a mock Telegram chat"""
    id: int
    type: str  # "private", "group", "supergroup", "channel"
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


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
                "last_name": self.chat.last_name
            },
            "date": int(self.date.timestamp()),
            "text": self.text
        }


class SendMessageRequest(BaseModel):
    """Request model for sending messages"""
    user_id: int
    chat_id: int
    text: str
    message_type: MessageType = MessageType.TEXT


class CreateUserRequest(BaseModel):
    """Request model for creating test users"""
    username: str
    first_name: str
    last_name: Optional[str] = None
    role: UserRole = UserRole.PLAYER
    phone_number: Optional[str] = None


class MockTelegramService:
    """Main service class for mock Telegram functionality"""
    
    def __init__(self):
        self.users: Dict[int, MockUser] = {}
        self.chats: Dict[int, MockChat] = {}
        self.messages: List[MockMessage] = []
        self.websocket_connections: List[WebSocket] = []
        self.message_counter = 1
        
        # Initialize with some default test users
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Initialize with default test users"""
        default_users = [
            MockUser(1001, "test_player", "Test Player", role=UserRole.PLAYER, phone_number="+1234567890"),
            MockUser(1002, "test_member", "Test Member", role=UserRole.TEAM_MEMBER, phone_number="+1234567891"),
            MockUser(1003, "test_admin", "Test Admin", role=UserRole.ADMIN, phone_number="+1234567892"),
            MockUser(1004, "test_leadership", "Test Leadership", role=UserRole.LEADERSHIP, phone_number="+1234567893"),
        ]
        
        for user in default_users:
            self.users[user.id] = user
            
            # Create private chat for each user
            chat = MockChat(
                id=user.id,
                type="private",
                first_name=user.first_name,
                last_name=user.last_name
            )
            self.chats[chat.id] = chat
    
    async def connect_websocket(self, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.websocket_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.websocket_connections)}")
    
    async def disconnect_websocket(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.websocket_connections)}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
            
        message_json = json.dumps(message)
        disconnected = []
        
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(message_json)
            except WebSocketDisconnect:
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            await self.disconnect_websocket(websocket)
    
    def create_user(self, request: CreateUserRequest) -> MockUser:
        """Create a new test user"""
        user_id = max(self.users.keys()) + 1 if self.users else 1001
        
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
            type="private",
            first_name=user.first_name,
            last_name=user.last_name
        )
        self.chats[chat.id] = chat
        
        return user
    
    def send_message(self, request: SendMessageRequest) -> MockMessage:
        """Send a message as if from a user"""
        if request.user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        if request.chat_id not in self.chats:
            raise HTTPException(status_code=404, detail="Chat not found")
        
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
        
        # Broadcast the message to WebSocket clients
        asyncio.create_task(self.broadcast_message({
            "type": "new_message",
            "message": message.to_dict()
        }))
        
        # Process message through bot system
        try:
            bot_response = process_mock_message_sync(message.to_dict())
            if bot_response and bot_response.get("status") != "processing":
                # Broadcast bot response
                asyncio.create_task(self.broadcast_message({
                    "type": "bot_response",
                    "message": bot_response
                }))
        except Exception as e:
            print(f"Error processing message through bot: {e}")
        
        return message
    
    def get_user_messages(self, user_id: int, limit: int = 50) -> List[MockMessage]:
        """Get messages for a specific user"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_messages = [
            msg for msg in self.messages 
            if msg.chat.id == user_id
        ]
        
        return user_messages[-limit:]
    
    def get_all_users(self) -> List[MockUser]:
        """Get all test users"""
        return list(self.users.values())
    
    def get_all_messages(self, limit: int = 100) -> List[MockMessage]:
        """Get all messages"""
        return self.messages[-limit:]


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
        "status": "running"
    }


@app.get("/users")
async def get_users():
    """Get all test users"""
    return [asdict(user) for user in mock_service.get_all_users()]


@app.post("/users")
async def create_user(request: CreateUserRequest):
    """Create a new test user"""
    user = mock_service.create_user(request)
    return asdict(user)


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
    """Get messages for a specific user"""
    messages = mock_service.get_user_messages(user_id, limit)
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


if __name__ == "__main__":
    uvicorn.run(
        "mock_telegram_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 