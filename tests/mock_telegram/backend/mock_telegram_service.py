"""
Mock Telegram Service for KICKAI Testing

This service provides a mock Telegram API for testing the KICKAI bot
without requiring a real Telegram bot token or webhook setup.
"""

import os
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
import phonenumbers
from phonenumbers import NumberParseException

# Set required environment variable for bot integration
os.environ.setdefault("KICKAI_INVITE_SECRET_KEY", "test_secret_key_for_debugging_only_32_chars_long")

# Import bot integration
try:
    from .bot_integration import process_mock_message
    BOT_INTEGRATION_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Bot integration available")
except ImportError as e:
    BOT_INTEGRATION_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Bot integration not available - running in standalone mode: {e}")


class MessageType(str, Enum):
    """Types of messages that can be sent/received"""
    TEXT = "text"
    COMMAND = "command"
    PHOTO = "photo"
    DOCUMENT = "document"
    LOCATION = "location"


class MemberRole(str, Enum):
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
    role: MemberRole = MemberRole.PLAYER
    phone_number: Optional[str] = None
    is_bot: bool = False
    created_at: datetime = None
    status: Optional[str] = "active"  # Status from Firestore (pending, active, etc.)
    
    def __post_init__(self):
        """Validate user data after initialization and set defaults"""
        if not self.username or not self.first_name:
            raise ValueError("Username and first_name are required")
        if self.id == 0:
            raise ValueError("User ID cannot be zero")
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


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
        if self.id == 0:
            raise ValueError("Chat ID cannot be zero")
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
    telegram_id: int = Field(..., gt=0, description="Telegram ID must be positive")
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
    role: MemberRole = MemberRole.PLAYER
    phone_number: str = Field(..., description="Phone number (required for players/team members)")
    
    @validator('username')
    def validate_username(cls, v):
        # Clean the username
        cleaned = v.strip().lower()
        if not cleaned:
            raise ValueError("Username cannot be empty after cleaning")
        
        # Check if it contains only allowed characters
        if not cleaned.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        
        return cleaned
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Phone number is required for all users")
        
        try:
            # Parse the phone number - try with None region first (international format)
            parsed_number = phonenumbers.parse(v, None)
            
            # Validate the parsed number
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number format")
            
            # Return the number in international format for consistency
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            
        except NumberParseException as e:
            # If parsing fails without region, try with common regions
            common_regions = ['US', 'GB', 'CA', 'AU']
            for region in common_regions:
                try:
                    parsed_number = phonenumbers.parse(v, region)
                    if phonenumbers.is_valid_number(parsed_number):
                        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                except NumberParseException:
                    continue
            
            # If all parsing attempts fail, provide helpful error message
            raise ValueError(f"Invalid phone number format. Please use international format (+1234567890) or include country code. Error: {e}")
        except Exception as e:
            raise ValueError(f"Phone number validation error: {str(e)}")


class ProcessInviteRequest(BaseModel):
    """Request model for processing invite links"""
    invite_id: str = Field(..., description="Invite link ID")
    invite_type: str = Field(..., description="Type of invite (player/team_member)")
    chat_id: str = Field(..., description="Target chat ID")
    team_id: str = Field(..., description="Team ID")
    
    @validator('invite_type')
    def validate_invite_type(cls, v):
        if v not in ['player', 'team_member']:
            raise ValueError("Invite type must be 'player' or 'team_member'")
        return v


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
        """Initialize users from Firestore data or create default test users"""
        users_loaded = self._load_users_from_firestore()
        
        if not users_loaded:
            logger.warning("⚠️ No users loaded from Firestore - creating default test users")
            self._create_default_test_users()
    
    def _create_default_test_users(self):
        """Create default test users for development/testing"""
        logger.info("🔧 Creating default test users for development")
        
        # Create test users
        test_users = [
            MockUser(
                id=1001,
                username="coach_wilson",
                first_name="Coach",
                last_name="Wilson",
                role=MemberRole.LEADERSHIP,
                phone_number="+1234567890"
            ),
            MockUser(
                id=1002,
                username="player_john",
                first_name="John",
                last_name="Doe",
                role=MemberRole.PLAYER,
                phone_number="+1234567891"
            ),
            MockUser(
                id=1003,
                username="admin_sarah",
                first_name="Sarah",
                last_name="Admin",
                role=MemberRole.ADMIN,
                phone_number="+1234567892"
            ),
            MockUser(
                id=1004,
                username="member_mike",
                first_name="Mike",
                last_name="Member",
                role=MemberRole.TEAM_MEMBER,
                phone_number="+1234567893"
            )
        ]
        
        # Add users to the service
        for user in test_users:
            self.users[user.id] = user
            
            # Create private chat for each user
            chat = MockChat(
                id=user.id,
                type=ChatType.PRIVATE,
                first_name=user.first_name
            )
            self.chats[chat.id] = chat
            
            logger.info(f"✅ Created test user: {user.first_name} (ID: {user.id}, Role: {user.role.value})")
        
        logger.info(f"✅ Created {len(test_users)} default test users")
    
    def _load_users_from_firestore(self) -> bool:
        """Load users from Firestore collections (both players and team members)"""
        try:
            from kickai.database.firebase_client import get_firebase_client
            
            client = get_firebase_client()
            db = client.client
            
            users_loaded = 0
            
            with self._lock:
                # Load players from kickai_KTI_players collection
                try:
                    players_ref = db.collection('kickai_KTI_players').limit(20)  # Limit to prevent overwhelming
                    for player_doc in players_ref.stream():
                        player_data = player_doc.to_dict()
                        telegram_id = player_data.get('telegram_id')
                        
                        if telegram_id:
                            try:
                                telegram_id = int(telegram_id)
                                user = MockUser(
                                    id=telegram_id,
                                    username=player_data.get('username', f"player_{telegram_id}"),
                                    first_name=player_data.get('name', 'Unknown Player'),
                                    role=MemberRole.PLAYER,
                                    phone_number=player_data.get('phone'),  # Fixed: use 'phone' instead of 'phone_number'
                                    status=player_data.get('status', 'pending')  # Include status from Firestore
                                )
                                self.users[user.id] = user
                                
                                # Create private chat
                                chat = MockChat(
                                    id=user.id,
                                    type=ChatType.PRIVATE,
                                    first_name=user.first_name
                                )
                                self.chats[chat.id] = chat
                                users_loaded += 1
                                logger.info(f"✅ Loaded player: {user.first_name} (ID: {telegram_id})")
                                
                            except (ValueError, TypeError) as e:
                                logger.warning(f"⚠️ Invalid telegram_id for player {player_doc.id}: {telegram_id} - {e}")
                                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load players: {e}")
                
                # Load team members from kickai_KTI_team_members collection
                try:
                    members_ref = db.collection('kickai_KTI_team_members').limit(20)  # Limit to prevent overwhelming
                    for member_doc in members_ref.stream():
                        member_data = member_doc.to_dict()
                        telegram_id = member_data.get('telegram_id')
                        
                        if telegram_id:
                            try:
                                telegram_id = int(telegram_id)
                                
                                # Don't overwrite if already exists (player takes precedence)
                                if telegram_id not in self.users:
                                    # Map member role to mock role
                                    member_role = member_data.get('role', 'team_member').lower()
                                    if member_role in ['manager', 'coach', 'captain']:
                                        role = MemberRole.LEADERSHIP
                                    elif member_role == 'admin':
                                        role = MemberRole.ADMIN
                                    else:
                                        role = MemberRole.TEAM_MEMBER
                                    
                                    user = MockUser(
                                        id=telegram_id,
                                        username=member_data.get('username', f"member_{telegram_id}"),
                                        first_name=member_data.get('name', 'Unknown Member'),
                                        role=role,
                                        phone_number=member_data.get('phone'),  # Fixed: use 'phone' instead of 'phone_number'
                                        status=member_data.get('status', 'active')  # Include status from Firestore
                                    )
                                    self.users[user.id] = user
                                    
                                    # Create private chat
                                    chat = MockChat(
                                        id=user.id,
                                        type=ChatType.PRIVATE,
                                        first_name=user.first_name
                                    )
                                    self.chats[chat.id] = chat
                                    users_loaded += 1
                                    logger.info(f"✅ Loaded team member: {user.first_name} (ID: {telegram_id}, Role: {role.value})")
                                
                            except (ValueError, TypeError) as e:
                                logger.warning(f"⚠️ Invalid telegram_id for team member {member_doc.id}: {telegram_id} - {e}")
                                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load team members: {e}")
            
            logger.info(f"🎯 Loaded {users_loaded} users from Firestore")
            return users_loaded > 0
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load users from Firestore: {e}")
            return False
    
    def _initialize_group_chats(self):
        """Initialize group chats for the team"""
        # Get dynamic team name from Firestore
        team_name = self._get_team_name_from_firestore()
        
        with self._lock:
            # Main chat (all users can access)
            main_chat = MockChat(
                id=2001,  # Group chat IDs start from 2000
                type=ChatType.GROUP,
                title=team_name,
                is_main_chat=True
            )
            self.chats[main_chat.id] = main_chat
            
            # Leadership chat (only team members, admins, and leadership can access)
            leadership_chat = MockChat(
                id=2002,
                type=ChatType.GROUP,
                title=f"{team_name} - Leadership",
                is_leadership_chat=True
            )
            self.chats[leadership_chat.id] = leadership_chat
            
            logger.info(f"Created group chats: Main ({main_chat.id}), Leadership ({leadership_chat.id}) for team: {team_name}")
    
    def _get_team_name_from_firestore(self) -> str:
        """Get the team name from Firestore or use fallback"""
        try:
            from kickai.database.firebase_client import get_firebase_client
            
            client = get_firebase_client()
            db = client.client
            
            # Get the first available team from kickai_teams collection
            teams_ref = db.collection('kickai_teams')
            teams = teams_ref.limit(1).stream()
            
            for team in teams:
                team_data = team.to_dict()
                team_name = team_data.get('name', team.id)
                logger.info(f"🎯 Using dynamic team name: {team_name}")
                return team_name
            
            # Fallback if no teams found
            logger.warning("⚠️ No teams found in Firestore, using fallback team name")
            return self.team_name
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get team name from Firestore: {e}, using fallback")
            return self.team_name
    
    def _refresh_users_from_firestore(self):
        """Refresh users from Firestore (called when UI requests fresh user list)"""
        try:
            from kickai.database.firebase_client import get_firebase_client
            
            client = get_firebase_client()
            db = client.client
            
            users_loaded = 0
            new_users = 0
            
            with self._lock:
                # Load players from kickai_KTI_players collection (including pending status)
                try:
                    players_ref = db.collection('kickai_KTI_players').limit(50)  # Increased limit for refresh
                    for player_doc in players_ref.stream():
                        player_data = player_doc.to_dict()
                        telegram_id = player_data.get('telegram_id')
                        
                        if telegram_id:
                            try:
                                telegram_id = int(telegram_id)
                                
                                # Check if this user already exists
                                if telegram_id not in self.users:
                                    user = MockUser(
                                        id=telegram_id,
                                        username=player_data.get('username', f"player_{telegram_id}"),
                                        first_name=player_data.get('name', 'Unknown Player'),
                                        role=MemberRole.PLAYER,
                                        phone_number=player_data.get('phone_number') or player_data.get('phone'),
                                        status=player_data.get('status', 'pending')  # Include status from Firestore
                                    )
                                    self.users[user.id] = user
                                    
                                    # Create private chat
                                    chat = MockChat(
                                        id=user.id,
                                        type=ChatType.PRIVATE,
                                        first_name=user.first_name
                                    )
                                    self.chats[chat.id] = chat
                                    new_users += 1
                                    logger.info(f"🆕 Added new player: {user.first_name} (ID: {telegram_id}, Status: {player_data.get('status', 'unknown')})")
                                
                                users_loaded += 1
                                
                            except (ValueError, TypeError) as e:
                                logger.warning(f"⚠️ Invalid telegram_id for player {player_doc.id}: {telegram_id} - {e}")
                                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to refresh players: {e}")
                
                # Load team members from kickai_KTI_team_members collection
                try:
                    members_ref = db.collection('kickai_KTI_team_members').limit(50)  # Increased limit for refresh
                    for member_doc in members_ref.stream():
                        member_data = member_doc.to_dict()
                        telegram_id = member_data.get('telegram_id')
                        
                        if telegram_id:
                            try:
                                telegram_id = int(telegram_id)
                                
                                # Don't overwrite if already exists (player takes precedence)
                                if telegram_id not in self.users:
                                    # Map member role to mock role
                                    member_role = member_data.get('role', 'team_member').lower()
                                    if member_role in ['manager', 'coach', 'captain']:
                                        role = MemberRole.LEADERSHIP
                                    elif member_role == 'admin':
                                        role = MemberRole.ADMIN
                                    else:
                                        role = MemberRole.TEAM_MEMBER
                                    
                                    user = MockUser(
                                        id=telegram_id,
                                        username=member_data.get('username', f"member_{telegram_id}"),
                                        first_name=member_data.get('name', 'Unknown Member'),
                                        role=role,
                                        phone_number=member_data.get('phone_number') or member_data.get('phone'),
                                        status=member_data.get('status', 'active')  # Include status from Firestore
                                    )
                                    self.users[user.id] = user
                                    
                                    # Create private chat
                                    chat = MockChat(
                                        id=user.id,
                                        type=ChatType.PRIVATE,
                                        first_name=user.first_name
                                    )
                                    self.chats[chat.id] = chat
                                    new_users += 1
                                    logger.info(f"🆕 Added new team member: {user.first_name} (ID: {telegram_id}, Role: {role.value})")
                                
                                users_loaded += 1
                                
                            except (ValueError, TypeError) as e:
                                logger.warning(f"⚠️ Invalid telegram_id for team member {member_doc.id}: {telegram_id} - {e}")
                                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to refresh team members: {e}")
            
            if new_users > 0:
                logger.info(f"🔄 Refreshed users: {users_loaded} total, {new_users} newly added from Firestore")
            else:
                logger.debug(f"🔄 Refreshed users: {users_loaded} total, no new users found")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to refresh users from Firestore: {e}")
    
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
                elif chat.is_leadership_chat and user.role in [MemberRole.TEAM_MEMBER, MemberRole.ADMIN, MemberRole.LEADERSHIP]:
                    accessible_chats.append(chat)
        
        return accessible_chats
    
    def can_user_access_chat(self, user_id: int, chat_id: int) -> bool:
        """Check if a user can access a specific chat"""
        if user_id not in self.users:
            logger.warning(f"User {user_id} not found in users: {list(self.users.keys())}")
            return False
            
        if chat_id not in self.chats:
            logger.warning(f"Chat {chat_id} not found in chats: {list(self.chats.keys())}")
            # For testing purposes, if chat_id matches the user_id (private chat), allow it
            if chat_id == user_id:
                return True
            # Also allow group chat IDs 2001 (main) and 2002 (leadership) for testing
            if chat_id in [2001, 2002]:
                return True
            return False
        
        user = self.users[user_id]
        chat = self.chats[chat_id]
        
        # Private chat - only for the user
        if chat.type == ChatType.PRIVATE:
            return chat.id == user_id
        
        # Main chat - accessible to all users
        if chat.is_main_chat:
            return True
        
        # Leadership chat - allow team members, admins, and leadership
        if chat.is_leadership_chat:
            allowed_roles = [MemberRole.TEAM_MEMBER, MemberRole.ADMIN, MemberRole.LEADERSHIP]
            has_access = user.role in allowed_roles
            logger.info(f"Leadership chat access check: User {user.first_name} (role: {user.role}) -> {'ALLOWED' if has_access else 'DENIED'}")
            return has_access
        
        # For testing purposes, be more permissive
        logger.info(f"Generic chat access granted for testing: User {user.first_name} -> Chat {chat_id}")
        return True
    
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
                raise HTTPException(
                    status_code=400, 
                    detail=f"Maximum number of users reached ({self.max_users}). Cannot create new user."
                )
            
            # Check for duplicate username
            if any(user.username == request.username for user in self.users.values()):
                raise HTTPException(
                    status_code=422, 
                    detail=f"Username '{request.username}' already exists. Please choose a different username."
                )
            
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
                
                logger.info(f"Created new user: {user.first_name} (@{user.username}) with phone {user.phone_number}")
                return user
                
            except ValueError as e:
                # This is a validation error from MockUser initialization
                raise HTTPException(
                    status_code=422, 
                    detail=f"User validation failed: {str(e)}"
                )
    
    async def process_invite_link(self, request: ProcessInviteRequest) -> Dict[str, Any]:
        """Process an invite link and create a user from invite data"""
        try:
            logger.info(f"🔗 [INVITE PROCESSING] Starting invite processing for ID: {request.invite_id}")
            logger.info(f"🔗 [INVITE PROCESSING] Team: {request.team_id}, Type: {request.invite_type}, Chat: {request.chat_id}")
            
            # Import Firebase client to get invite data
            from kickai.database.firebase_client import get_firebase_client
            
            logger.info(f"🔗 [INVITE PROCESSING] Getting Firebase client...")
            client = get_firebase_client()
            db = client.client
            
            # Get invite data from Firestore using team-specific collection naming
            from kickai.core.firestore_constants import get_team_specific_collection_name
            
            # Use team-specific collection name to match InviteLinkService
            collection_name = get_team_specific_collection_name(request.team_id, "invite_links")
            logger.info(f"🔗 [INVITE PROCESSING] Using collection: {collection_name}")
            
            logger.info(f"🔗 [INVITE PROCESSING] Looking up invite document: {request.invite_id}")
            invite_doc = db.collection(collection_name).document(request.invite_id).get()
            
            if not invite_doc.exists:
                logger.error(f"❌ [INVITE PROCESSING] Invite not found: {request.invite_id} in collection {collection_name}")
                raise HTTPException(status_code=404, detail="Invite link not found or expired")
            
            logger.info(f"✅ [INVITE PROCESSING] Found invite document successfully")
            invite_data = invite_doc.to_dict()
            logger.info(f"🔗 [INVITE PROCESSING] Invite data keys: {list(invite_data.keys())}")
            
            # Extract user info based on invite type
            logger.info(f"🔗 [INVITE PROCESSING] Processing invite type: {request.invite_type}")
            
            if request.invite_type == 'player':
                # Player invite - look for player_* fields
                logger.info(f"🔗 [INVITE PROCESSING] Extracting player data from invite")
                user_info = {
                    'name': invite_data.get('player_name'),
                    'phone': invite_data.get('player_phone'),
                    'id': invite_data.get('player_id'),
                    'role': MemberRole.PLAYER
                }
                logger.info(f"🔗 [INVITE PROCESSING] Player info: {user_info['name']} ({user_info['phone']})")
                
            elif request.invite_type == 'team_member':
                # Team member invite - look for member_* fields
                logger.info(f"🔗 [INVITE PROCESSING] Extracting team member data from invite")
                user_info = {
                    'name': invite_data.get('member_name'),
                    'phone': invite_data.get('member_phone'),
                    'id': invite_data.get('member_id'),
                    'role': MemberRole.TEAM_MEMBER  # Default, will be overridden below
                }
                
                # Map the member role from invite data to MemberRole enum
                member_role_str = invite_data.get('member_role', 'team_member')
                try:
                    user_info['role'] = MemberRole(member_role_str)
                except ValueError:
                    # Fallback to TEAM_MEMBER if invalid role
                    user_info['role'] = MemberRole.TEAM_MEMBER
                
                logger.info(f"🔗 [INVITE PROCESSING] Team member info: {user_info['name']} ({user_info['phone']}) - Role: {user_info['role']}")
            else:
                logger.error(f"❌ [INVITE PROCESSING] Unknown invite type: {request.invite_type}")
                raise HTTPException(status_code=400, detail=f"Unknown invite type: {request.invite_type}")
            
            if not user_info['name']:
                invite_type_display = "player" if request.invite_type == 'player' else "team member"
                logger.error(f"❌ [INVITE PROCESSING] Missing {invite_type_display} information in invite")
                raise HTTPException(status_code=400, detail=f"Missing {invite_type_display} information in invite")
            
            logger.info(f"🔗 [INVITE PROCESSING] User info validated successfully")
            
            # Generate new telegram_id
            logger.info(f"🔗 [INVITE PROCESSING] Generating new Telegram ID...")
            with self._lock:
                new_telegram_id = max(self.users.keys()) + 1 if self.users else 1001
                logger.info(f"🔗 [INVITE PROCESSING] Assigned Telegram ID: {new_telegram_id}")
                
                # Create username from user name
                user_name = user_info.get('name', 'Unknown')
                base_username = user_name.lower().replace(' ', '_').replace('-', '_')
                # Ensure username is unique
                username = base_username
                counter = 1
                while any(user.username == username for user in self.users.values()):
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                logger.info(f"🔗 [INVITE PROCESSING] Generated username: {username}")
                
                # Create new user
                logger.info(f"🔗 [INVITE PROCESSING] Creating MockUser object...")
                user = MockUser(
                    id=new_telegram_id,
                    username=username,
                    first_name=user_name.split()[0] if user_name else 'Unknown',
                    last_name=' '.join(user_name.split()[1:]) if len(user_name.split()) > 1 else None,
                    role=user_info['role'],
                    phone_number=user_info.get('phone'),
                    status='pending'
                )
                
                self.users[new_telegram_id] = user
                logger.info(f"🔗 [INVITE PROCESSING] Added user to mock service")
                
                # Create private chat for the user
                logger.info(f"🔗 [INVITE PROCESSING] Creating private chat for user...")
                chat = MockChat(
                    id=new_telegram_id,
                    type=ChatType.PRIVATE,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                self.chats[chat.id] = chat
                logger.info(f"🔗 [INVITE PROCESSING] Added private chat to mock service")
                
                logger.info(f"✅ [INVITE PROCESSING] SUCCESS: Created user from invite: {user.first_name} (@{user.username}, ID: {new_telegram_id})")
                
                # Update the player record in Firestore with the telegram_id
                if request.invite_type == 'player' and user_info.get('id'):
                    logger.info(f"🔗 [INVITE PROCESSING] Updating player record in Firestore with telegram_id: {new_telegram_id}")
                    try:
                        # Get the player collection
                        from kickai.core.firestore_constants import get_team_players_collection
                        player_collection = get_team_players_collection(request.team_id)
                        
                        # Update the player document with telegram_id and activate them
                        player_doc_ref = db.collection(player_collection).document(user_info.get('id'))
                        player_doc_ref.update({
                            'telegram_id': new_telegram_id,
                            'username': username,
                            'status': 'active',  # Activate the player when they join via invite link
                            'updated_at': datetime.now().isoformat()
                        })
                        logger.info(f"✅ [INVITE PROCESSING] Successfully updated player {user_info.get('id')} with telegram_id {new_telegram_id}")
                    except Exception as e:
                        logger.error(f"❌ [INVITE PROCESSING] Failed to update player record: {e}")
                
                # Create invitation context for auto-activation
                logger.info(f"🔗 [INVITE PROCESSING] Creating invitation context for auto-activation...")
                invite_context = {
                    "invite_id": request.invite_id,
                    "invite_type": request.invite_type,
                    "secure_data": invite_data.get("secure_data"),  # Base64-encoded secure data from Firestore
                    "invite_link": f"mock://invite/{request.invite_id}",
                }
                logger.info(f"🔗 [INVITE PROCESSING] Invitation context created with keys: {list(invite_context.keys())}")
                
                # Add type-specific fields to invite context
                logger.info(f"🔗 [INVITE PROCESSING] Adding type-specific fields to context...")
                if request.invite_type == 'player':
                    invite_context.update({
                        "player_name": user_info.get('name'),
                        "player_phone": user_info.get('phone'),
                        "player_id": user_info.get('id')
                    })
                    logger.info(f"🔗 [INVITE PROCESSING] Added player-specific fields to context")
                elif request.invite_type == 'team_member':
                    invite_context.update({
                        "member_name": user_info.get('name'),
                        "member_phone": user_info.get('phone'),
                        "member_id": user_info.get('id')
                    })
                    logger.info(f"🔗 [INVITE PROCESSING] Added team member-specific fields to context")
                
                logger.info(f"🔗 [INVITE PROCESSING] Created invitation context for auto-activation: {user_info.get('name')}")
                
                # Simulate join event with invitation context for auto-activation
                logger.info(f"🔗 [INVITE PROCESSING] Simulating join event for user {new_telegram_id} in chat {request.chat_id}")
                await self.simulate_new_chat_member(new_telegram_id, int(request.chat_id), invite_context)
                
                logger.info(f"🔗 [INVITE PROCESSING] Preparing response data...")
                response_data = {
                    "user_id": new_telegram_id,
                    "username": username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user_info['role'].value,
                    "phone_number": user.phone_number,
                    "status": "joined",
                    "chat_id": request.chat_id,
                    "invite_processed": True
                }
                
                logger.info(f"✅ [INVITE PROCESSING] COMPLETE: Returning response for {user.first_name}")
                return response_data
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ [INVITE PROCESSING] Error processing invite: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process invite: {str(e)}")
    
    async def simulate_new_chat_member(self, user_id: int, chat_id: int, invite_context: Optional[Dict[str, Any]] = None) -> bool:
        """Simulate a new_chat_members event with optional invitation context for auto-activation"""
        try:
            if user_id not in self.users:
                logger.error(f"User {user_id} not found for join simulation")
                return False
            
            if chat_id not in self.chats:
                logger.error(f"Chat {chat_id} not found for join simulation")
                return False
            
            user = self.users[user_id]
            chat = self.chats[chat_id]
            
            # Create new_chat_members event data
            event_data = {
                "type": "new_chat_members",
                "message_id": self.message_counter,
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username
                },
                "chat": {
                    "id": chat_id,
                    "type": chat.type.value if hasattr(chat.type, 'value') else str(chat.type),
                    "title": chat.title
                },
                "date": int(datetime.now(timezone.utc).timestamp()),
                "new_chat_members": [
                    {
                        "id": user_id,
                        "is_bot": False,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username
                    }
                ]
            }
            
            # Include invitation context for auto-activation if provided
            if invite_context:
                event_data["invitation_context"] = invite_context
                logger.info(f"🔗 Including invitation context for auto-activation: {list(invite_context.keys())}")
            
            self.message_counter += 1
            
            # Send to bot integration if available
            if BOT_INTEGRATION_AVAILABLE:
                try:
                    response = await process_mock_message(event_data)
                    logger.info(f"✅ Simulated join event for {user.first_name} in chat {chat_id}")
                    
                    # Broadcast the join event to connected clients
                    await self.broadcast_message({
                        "type": "new_chat_member",
                        "event": event_data,
                        "user": {
                            "id": user_id,
                            "username": user.username,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "role": user.role.value
                        },
                        "chat_id": chat_id
                    })
                    
                    return True
                except Exception as e:
                    logger.error(f"❌ Error processing join event through bot: {e}")
                    return False
            else:
                logger.warning("Bot integration not available - join event simulated but not processed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error simulating new chat member: {e}")
            return False
    
    async def send_message(self, request: SendMessageRequest) -> MockMessage:
        """Send a message as if from a user"""
        with self._lock:
            if request.telegram_id not in self.users:
                raise HTTPException(status_code=404, detail="User not found")
            
            if request.chat_id not in self.chats:
                raise HTTPException(status_code=404, detail="Chat not found")
            
            # Check if user can access this chat
            if not self.can_user_access_chat(request.telegram_id, request.chat_id):
                raise HTTPException(status_code=403, detail="User cannot access this chat")
            
            user = self.users[request.telegram_id]
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
            logger.info(f"Bot integration available: {BOT_INTEGRATION_AVAILABLE}")
            if BOT_INTEGRATION_AVAILABLE:
                try:
                    logger.info(f"Processing message through bot: {request.text}")
                    # Add chat context to message data for bot routing
                    message_data = message.to_dict()
                    message_data["chat_context"] = chat_context
                    
                    bot_response = await process_mock_message(message_data)
                    logger.info(f"Bot response: {bot_response}")
                    if bot_response and bot_response.get("status") != "processing":
                        # Create bot message and add to chat
                        bot_message = MockMessage(
                            message_id=self.message_counter,
                            from_user=MockUser(
                                id=9999,  # Bot ID (positive number)
                                username="kickai_bot",
                                first_name="KICKAI Bot",
                                is_bot=True
                            ),
                            chat=chat,
                            date=datetime.now(timezone.utc),
                            text=bot_response.get("message", bot_response.get("text", "Bot response"))
                        )
                        self.messages.append(bot_message)
                        self.message_counter += 1
                        
                        # Broadcast bot response using the properly formatted message
                        asyncio.create_task(self.broadcast_message({
                            "type": "bot_response",
                            "message": bot_message.to_dict(),
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
        """Get all test users (includes fresh data from Firestore)"""
        # Refresh users from Firestore to include any pending users or new additions
        self._refresh_users_from_firestore()
        
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
    """Get all test users (includes fresh data from Firestore with status)"""
    users = mock_service.get_all_users()
    return [
        {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "phone_number": user.phone_number,
            "is_bot": user.is_bot,
            "status": user.status or "active",  # Include user status from Firestore
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]


@app.post("/users")
async def create_user(request: CreateUserRequest):
    """Create a new test user"""
    user = mock_service.create_user(request)
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "phone_number": user.phone_number,
        "is_bot": user.is_bot,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


@app.post("/invite/process")
async def process_invite_link(request: ProcessInviteRequest):
    """Process an invite link and simulate user joining"""
    logger.info(f"🌐 [API] Received invite processing request: {request.invite_id}")
    logger.info(f"🌐 [API] Request details: team={request.team_id}, type={request.invite_type}, chat={request.chat_id}")
    
    try:
        logger.info(f"🌐 [API] Delegating to mock service...")
        result = await mock_service.process_invite_link(request)
        logger.info(f"✅ [API] Invite processing completed successfully")
        return result
    except HTTPException:
        logger.error(f"❌ [API] HTTP exception during invite processing")
        raise
    except Exception as e:
        logger.error(f"❌ [API] Unexpected error processing invite: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chats")
async def get_chats():
    """Get all chats"""
    chats = mock_service.get_all_chats()
    return [
        {
            "id": chat.id,
            "type": chat.type,
            "title": chat.title,
            "username": chat.username,
            "first_name": chat.first_name,
            "last_name": chat.last_name,
            "is_main_chat": chat.is_main_chat,
            "is_leadership_chat": chat.is_leadership_chat
        }
        for chat in chats
    ]


@app.get("/chats/group")
async def get_group_chats():
    """Get group chats (main and leadership)"""
    chats = mock_service.get_group_chats()
    return [
        {
            "id": chat.id,
            "type": chat.type,
            "title": chat.title,
            "username": chat.username,
            "first_name": chat.first_name,
            "last_name": chat.last_name,
            "is_main_chat": chat.is_main_chat,
            "is_leadership_chat": chat.is_leadership_chat
        }
        for chat in chats
    ]


@app.get("/users/{user_id}/chats")
async def get_user_chats(user_id: int):
    """Get all chats accessible to a specific user"""
    accessible_chats = mock_service.get_accessible_chats_for_user(user_id)
    return [
        {
            "id": chat.id,
            "type": chat.type,
            "title": chat.title,
            "username": chat.username,
            "first_name": chat.first_name,
            "last_name": chat.last_name,
            "is_main_chat": chat.is_main_chat,
            "is_leadership_chat": chat.is_leadership_chat
        }
        for chat in accessible_chats
    ]


@app.post("/send_message")
async def send_message(request: SendMessageRequest):
    """Send a message as a user and process it through real KICKAI bot"""
    # First, add the user message to mock service
    message = await mock_service.send_message(request)
    
    # Process through real KICKAI bot if integration is available
    if BOT_INTEGRATION_AVAILABLE:
        try:
            # Import bot integration
            from .bot_integration import process_mock_message
            
            # Convert message to format expected by bot integration
            message_data = {
                "text": request.text,
                "from": {
                    "id": request.telegram_id,
                    "username": mock_service.users[request.telegram_id].username if request.telegram_id in mock_service.users else f"user_{request.telegram_id}",
                    "first_name": mock_service.users[request.telegram_id].first_name if request.telegram_id in mock_service.users else "Test",
                    "last_name": mock_service.users[request.telegram_id].last_name if request.telegram_id in mock_service.users else "User"
                },
                "chat": {
                    "id": request.chat_id,
                    "type": "group" if request.chat_id in [2001, 2002] else "private",
                    "title": mock_service.chats[request.chat_id].title if request.chat_id in mock_service.chats else "Test Chat"
                },
                "date": int(datetime.now().timestamp()),
                "chat_context": "leadership" if request.chat_id == 2002 else "main" if request.chat_id == 2001 else "private"
            }
            
            # Process message through real KICKAI bot
            bot_response = await process_mock_message(message_data)
            
            if bot_response.get("success", False):
                # Create bot response message and add it to mock service
                bot_message_data = {
                    "message_id": mock_service.message_counter + 1,
                    "from": {
                        "id": 999999999,  # Bot ID
                        "username": "kickai_bot",
                        "first_name": "KickAI Bot",
                        "last_name": None,
                        "is_bot": True
                    },
                    "chat": {
                        "id": request.chat_id,
                        "type": "group" if request.chat_id in [2001, 2002] else "private"
                    },
                    "date": int(datetime.now(timezone.utc).timestamp()),
                    "text": bot_response.get("message", "No response"),
                    "agent_type": bot_response.get("agent_type", "unknown"),
                    "confidence": bot_response.get("confidence", 1.0)
                }
                
                # Add bot response to mock service and broadcast via WebSocket
                await bot_response_handler(bot_message_data)
                
        except Exception as e:
            logger.error(f"❌ Error processing message through real bot: {e}")
            # Continue with mock response - don't fail the request
    
    return message.to_dict()


async def bot_response_handler(bot_message_data: dict):
    """Handle bot response and broadcast to WebSocket clients"""
    # Add bot message to mock service
    with mock_service._lock:
        mock_service.message_counter += 1
        
        # Create proper MockUser object for the bot
        bot_user = MockUser(
            id=bot_message_data["from"]["id"],
            username=bot_message_data["from"]["username"],
            first_name=bot_message_data["from"]["first_name"],
            last_name=bot_message_data["from"].get("last_name"),
            is_bot=True
        )
        
        # Create proper MockChat object
        chat_data = bot_message_data["chat"]
        bot_chat = MockChat(
            id=chat_data["id"],
            type=ChatType.GROUP if chat_data.get("type") == "group" else ChatType.PRIVATE,
            title=chat_data.get("title"),
            username=chat_data.get("username"),
            first_name=chat_data.get("first_name"),
            last_name=chat_data.get("last_name"),
            is_main_chat=chat_data.get("is_main_chat", False),
            is_leadership_chat=chat_data.get("is_leadership_chat", False)
        )
        
        # Create MockMessage with proper objects
        bot_message = MockMessage(
            message_id=bot_message_data["message_id"],
            from_user=bot_user,
            chat=bot_chat,
            text=bot_message_data["text"],
            date=datetime.fromtimestamp(bot_message_data["date"], tz=timezone.utc)
        )
        mock_service.messages.append(bot_message)
    
    # Broadcast to WebSocket clients
    await mock_service.broadcast_message(bot_message_data)


@app.post("/bot_response")
async def bot_response(response_data: dict):
    """Receive bot response and broadcast to WebSocket clients"""
    from datetime import datetime, timezone
    
    # Transform bot response to match frontend expectations
    bot_message = {
        "message_id": len(mock_service.messages) + 1,
        "from": {
            "id": 999999999,  # Bot ID
            "username": "kickai_bot",
            "first_name": "KickAI Bot",
            "last_name": None,
            "is_bot": True
        },
        "chat": {
            "id": 2002,  # Default chat ID
            "type": "group",
            "title": "KickAI Testing",
            "username": None,
            "first_name": None,
            "last_name": None,
            "is_main_chat": True,
            "is_leadership_chat": False
        },
        "date": int(datetime.now(timezone.utc).timestamp()),
        "text": response_data.get("message", response_data.get("text", "No response message"))
    }
    
    await mock_service.broadcast_message({
        "type": "bot_response",
        "message": bot_message
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


# =============================================================================
# FIREBASE ENDPOINTS (Mock implementations for enhanced frontend)
# =============================================================================

@app.get("/firebase/users")
async def get_firebase_users():
    """Get real Firebase users from Firestore - NO MOCK FALLBACK"""
    global CURRENT_TEAM_ID
    
    try:
        # Always get real data from Firestore
        from kickai.features.player_registration.domain.services.player_service import PlayerService
        from kickai.features.team_administration.domain.services.team_service import TeamService
        from kickai.core.dependency_container import initialize_container, get_service
        
        initialize_container()
        player_service = get_service(PlayerService)
        team_service = get_service(TeamService)
        
        # Get players and team members for the current team
        players = await player_service.get_players_by_team(team_id=CURRENT_TEAM_ID)
        team_members = await team_service.get_team_members(CURRENT_TEAM_ID)
        
        firebase_users = []
        
        # Convert players to Firebase format
        for player in players:
            firebase_user = {
                "id": str(player.user_id) if player.user_id else str(player.player_id),
                "username": player.username or f"player_{player.user_id or player.player_id}",
                "first_name": player.first_name or "Player",
                "last_name": player.last_name,
                "role": "player",
                "phone_number": player.phone_number,
                "is_bot": False,
                "created_at": player.created_at.isoformat() if player.created_at else None,
                "status": "active" if player.is_active else "inactive",
                "team_id": CURRENT_TEAM_ID,
                "is_active": player.is_active,
                "is_approved": player.is_approved,
                "position": player.position or "Unknown"
            }
            firebase_users.append(firebase_user)
        
        # Convert team members to Firebase format
        for member in team_members:
            firebase_user = {
                "id": str(member.user_id),
                "username": member.username or f"member_{member.user_id}",
                "first_name": member.first_name or "Member",
                "last_name": member.last_name,
                "role": member.role.value if hasattr(member.role, 'value') else str(member.role),
                "phone_number": member.phone_number,
                "is_bot": False,
                "created_at": member.created_at.isoformat() if member.created_at else None,
                "status": "active" if member.is_active else "inactive",
                "team_id": CURRENT_TEAM_ID,
                "is_active": member.is_active,
                "is_approved": True,  # Team members are always approved
                "position": "Team Member"
            }
            firebase_users.append(firebase_user)
        
        logger.info(f"✅ Retrieved {len(firebase_users)} real users from Firestore for team {CURRENT_TEAM_ID}")
        
        return {
            "users": firebase_users,
            "total": len(firebase_users),
            "status": "success",
            "team_id": CURRENT_TEAM_ID,
            "source": "firestore"
        }
        
    except Exception as e:
        logger.error(f"Error getting real Firestore users: {e}")
        return {
            "users": [],
            "total": 0,
            "status": "error",
            "error": f"Failed to get users from Firestore: {str(e)}",
            "team_id": CURRENT_TEAM_ID,
            "source": "error"
        }


@app.get("/firebase/players")
async def get_firebase_players():
    """Get real Firebase players from Firestore - NO MOCK FALLBACK"""
    global CURRENT_TEAM_ID
    
    try:
        # Always get real data from Firestore
        from kickai.features.player_registration.domain.services.player_service import PlayerService
        from kickai.core.dependency_container import initialize_container, get_service
        
        initialize_container()
        player_service = get_service(PlayerService)
        
        # Get players for the current team
        players = await player_service.get_players_by_team(team_id=CURRENT_TEAM_ID)
        
        firebase_players = []
        for player in players:
            firebase_player = {
                "id": str(player.user_id) if player.user_id else str(player.player_id),
                "username": player.username or f"player_{player.user_id or player.player_id}",
                "first_name": player.first_name or "Player",
                "last_name": player.last_name,
                "phone_number": player.phone_number,
                "position": player.position or "Unknown",
                "status": "active" if player.is_active else "inactive",
                "team_id": CURRENT_TEAM_ID,
                "is_active": player.is_active,
                "is_approved": player.is_approved,
                "created_at": player.created_at.isoformat() if player.created_at else None
            }
            firebase_players.append(firebase_player)
        
        logger.info(f"✅ Retrieved {len(firebase_players)} real players from Firestore for team {CURRENT_TEAM_ID}")
        
        return {
            "players": firebase_players,
            "total": len(firebase_players),
            "status": "success",
            "team_id": CURRENT_TEAM_ID,
            "source": "firestore"
        }
        
    except Exception as e:
        logger.error(f"Error getting real Firestore players: {e}")
        return {
            "players": [],
            "total": 0,
            "status": "error",
            "error": f"Failed to get players from Firestore: {str(e)}",
            "team_id": CURRENT_TEAM_ID,
            "source": "error"
        }


@app.get("/firebase/team_members")
async def get_firebase_team_members():
    """Get real Firebase team members from Firestore - NO MOCK FALLBACK"""
    global CURRENT_TEAM_ID
    
    try:
        # Always get real data from Firestore
        from kickai.features.team_administration.domain.services.team_service import TeamService
        from kickai.core.dependency_container import initialize_container, get_service
        
        initialize_container()
        team_service = get_service(TeamService)
        
        # Get team members for the current team
        team_members = await team_service.get_team_members(CURRENT_TEAM_ID)
        
        firebase_team_members = []
        for member in team_members:
            firebase_member = {
                "id": str(member.user_id),
                "username": member.username or f"member_{member.user_id}",
                "first_name": member.first_name or "Member",
                "last_name": member.last_name,
                "phone_number": member.phone_number,
                "role": member.role.value if hasattr(member.role, 'value') else str(member.role),
                "status": "active" if member.is_active else "inactive",
                "team_id": CURRENT_TEAM_ID,
                "is_active": member.is_active,
                "created_at": member.created_at.isoformat() if member.created_at else None
            }
            firebase_team_members.append(firebase_member)
        
        logger.info(f"✅ Retrieved {len(firebase_team_members)} real team members from Firestore for team {CURRENT_TEAM_ID}")
        
        return {
            "team_members": firebase_team_members,
            "total": len(firebase_team_members),
            "status": "success",
            "team_id": CURRENT_TEAM_ID,
            "source": "firestore"
        }
        
    except Exception as e:
        logger.error(f"Error getting real Firestore team members: {e}")
        return {
            "team_members": [],
            "total": 0,
            "status": "error",
            "error": f"Failed to get team members from Firestore: {str(e)}",
            "team_id": CURRENT_TEAM_ID,
            "source": "error"
        }


@app.get("/firebase/status")
async def get_firebase_status():
    """Mock Firebase status endpoint"""
    global CURRENT_TEAM_ID
    
    return {
        "status": "connected",
        "database": "firestore",
        "project_id": "kickai-testing",
        "team_id": CURRENT_TEAM_ID,  # Include current team ID
        "collections": [
            f"kickai_{CURRENT_TEAM_ID}_players",
            f"kickai_{CURRENT_TEAM_ID}_team_members",
            f"kickai_{CURRENT_TEAM_ID}_matches",
            f"kickai_{CURRENT_TEAM_ID}_training",
            f"kickai_{CURRENT_TEAM_ID}_payments"
        ]
    }


# Global variable to store current team ID
CURRENT_TEAM_ID = "KTI"  # Default team ID

@app.get("/teams")
async def get_available_teams():
    """Get all available teams from Firestore - NO MOCK FALLBACK"""
    try:
        # Always try to get real teams from Firestore
        from kickai.features.team_administration.domain.services.team_service import TeamService
        from kickai.core.dependency_container import initialize_container, get_service
        
        initialize_container()
        team_service = get_service(TeamService)
        teams = await team_service.get_all_teams()
        
        if not teams:
            logger.warning("No teams found in Firestore")
            return {
                "teams": [],
                "current_team_id": CURRENT_TEAM_ID,
                "status": "error",
                "error": "No teams found in Firestore"
            }
        
        team_list = [{"id": team.id, "name": getattr(team, 'name', team.id)} for team in teams]
        
        logger.info(f"✅ Retrieved {len(team_list)} real teams from Firestore")
        
        return {
            "teams": team_list,
            "current_team_id": CURRENT_TEAM_ID,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting teams from Firestore: {e}")
        return {
            "teams": [],
            "current_team_id": CURRENT_TEAM_ID,
            "status": "error",
            "error": f"Failed to get teams from Firestore: {str(e)}"
        }


@app.post("/teams/switch")
async def switch_team(request: dict):
    """Switch to a different team"""
    global CURRENT_TEAM_ID
    
    try:
        team_id = request.get("team_id")
        if not team_id:
            return {
                "status": "error",
                "error": "team_id is required"
            }
        
        # Update current team ID
        CURRENT_TEAM_ID = team_id
        logger.info(f"Switched to team: {team_id}")
        
        return {
            "status": "success",
            "current_team_id": CURRENT_TEAM_ID,
            "message": f"Switched to team {team_id}"
        }
    except Exception as e:
        logger.error(f"Error switching team: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify server is working"""
    return {
        "status": "success",
        "message": "Mock Telegram Service is running",
        "current_team_id": CURRENT_TEAM_ID,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/team_id")
async def get_team_id():
    """Get the current team ID being used by the bot integration"""
    global CURRENT_TEAM_ID
    
    try:
        if BOT_INTEGRATION_AVAILABLE:
            from .bot_integration import MockTelegramIntegration
            integration = MockTelegramIntegration()
            await integration._initialize()
            if integration.agentic_router:
                # Use the current team ID from global variable
                team_id = CURRENT_TEAM_ID
            else:
                team_id = CURRENT_TEAM_ID
        else:
            team_id = CURRENT_TEAM_ID
    except Exception as e:
        logger.warning(f"Could not get team_id from bot integration: {e}")
        team_id = CURRENT_TEAM_ID
    
    return {
        "team_id": team_id,
        "source": "team_switcher" if CURRENT_TEAM_ID != "KTI" else "bot_integration",
        "status": "success"
    }


# =============================================================================
# QUICK TEST SCENARIOS API INTEGRATION
# =============================================================================

# Include Quick Test API routes
try:
    from ..quick_tests.api_integration import router as quick_test_router
    app.include_router(quick_test_router)
    logger.info("✅ Quick Test Scenarios API routes included")
except ImportError as e:
    logger.warning(f"⚠️ Quick Test Scenarios API not available: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "mock_telegram_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 