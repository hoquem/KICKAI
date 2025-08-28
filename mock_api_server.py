#!/usr/bin/env python3
"""
Mock API Server for KICKAI Bot Testing
Provides API endpoints for the mock Telegram UI to communicate with the actual bot system
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import KICKAI modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from kickai.core.dependency_container import get_container
from kickai.core.enums import ChatType, ResponseStatus
from kickai.utils.tool_helpers import create_json_response
from kickai.features.shared.application.tools.help_tools import help_response
from kickai.features.shared.application.tools.system_tools import ping, version
from kickai.features.player_registration.application.tools.player_tools import get_my_status, get_active_players
from kickai.features.team_administration.application.tools.team_member_tools import get_team_members
from kickai.features.player_registration.application.tools.player_update_tools import update_player_field
from kickai.features.team_administration.application.tools.player_management_tools import add_player
from kickai.features.team_administration.application.tools.team_member_tools import add_team_member_simplified

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="KICKAI Mock API Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class MessageRequest(BaseModel):
    telegram_id: int
    chat_id: str
    text: str

class UserRequest(BaseModel):
    username: str
    first_name: str
    last_name: Optional[str] = None
    role: str = "player"
    phone_number: Optional[str] = None

class InviteRequest(BaseModel):
    invite_token: str
    telegram_id: int
    username: str
    first_name: str
    last_name: Optional[str] = None

# Mock data storage
mock_users = []
mock_chats = [
    {"id": "main_chat", "name": "KickAI Testing", "type": "main"},
    {"id": "leadership_chat", "name": "KickAI Testing - Leadership", "type": "leadership"}
]
mock_messages = {}

# Command routing logic
async def route_command_to_bot(telegram_id: int, chat_id: str, text: str) -> str:
    """Route commands to the appropriate bot tools"""
    try:
        # Determine chat type
        chat_type = "main"
        if "leadership" in chat_id:
            chat_type = "leadership"
        
        # Extract command and arguments
        parts = text.strip().split()
        if not parts:
            return "Please enter a command or message."
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Route to appropriate tool based on command
        if command == "/help":
            return await help_response(telegram_id, "KAI", "test_user", chat_type)
        
        elif command == "/ping":
            return await ping(telegram_id, "KAI", "test_user", chat_type)
        
        elif command == "/version":
            return await version(telegram_id, "KAI", "test_user", chat_type)
        
        elif command == "/myinfo":
            return await get_my_status(telegram_id, "KAI", "test_user", chat_type)
        
        elif command == "/list":
            if chat_type == "main":
                return await get_active_players(telegram_id, "KAI", "test_user", chat_type)
            else:
                return await get_team_members(telegram_id, "KAI", "test_user", chat_type)
        
        elif command == "/status":
            return await get_my_status(telegram_id, "KAI", "test_user", chat_type)
        
        elif command == "/addplayer":
            if len(args) >= 2:
                name = args[0]
                phone = args[1] if len(args) > 1 else ""
                return await add_player(telegram_id, "KAI", "test_user", chat_type, name, phone)
            else:
                return "Usage: /addplayer [name] [phone]"
        
        elif command == "/addmember":
            if len(args) >= 2:
                name = args[0]
                phone = args[1] if len(args) > 1 else ""
                return await add_team_member_simplified(telegram_id, "KAI", "test_user", chat_type, name, phone)
            else:
                return "Usage: /addmember [name] [phone]"
        
        elif command == "/update":
            if len(args) >= 2:
                field = args[0]
                value = " ".join(args[1:])
                return await update_player_field(telegram_id, "KAI", "test_user", chat_type, field, value)
            else:
                return "Usage: /update [field] [value]"
        
        # Natural language processing
        elif "phone" in text.lower() and "number" in text.lower():
            return await get_my_status(telegram_id, "KAI", "test_user", chat_type)
        
        elif "status" in text.lower():
            return await get_my_status(telegram_id, "KAI", "test_user", chat_type)
        
        elif "help" in text.lower():
            return await help_response(telegram_id, "KAI", "test_user", chat_type)
        
        # Default response for unknown commands
        else:
            return f"🤖 KICKAI Bot\n\nCommand '{command}' received. This is a mock response.\n\nAvailable commands:\n• /help - Show available commands\n• /myinfo - Show your information\n• /list - List team members\n• /status - Check your status\n• /addplayer [name] [phone] - Add new player\n• /addmember [name] [phone] - Add team member\n• /update [field] [value] - Update your information"
    
    except Exception as e:
        logger.error(f"Error routing command: {e}")
        return f"❌ Error processing command: {str(e)}"

# API Endpoints
@app.get("/")
async def root():
    return {"message": "KICKAI Mock API Server", "status": "running"}

@app.get("/users")
async def get_users():
    """Get all mock users"""
    return mock_users

@app.post("/users")
async def create_user(user: UserRequest):
    """Create a new mock user"""
    new_user = {
        "id": len(mock_users) + 1,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "phone_number": user.phone_number,
        "created_at": datetime.now().isoformat()
    }
    mock_users.append(new_user)
    return new_user

@app.get("/chats")
async def get_chats():
    """Get all mock chats"""
    return mock_chats

@app.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: str):
    """Get messages for a specific chat"""
    return mock_messages.get(chat_id, [])

@app.post("/send_message")
async def send_message(request: MessageRequest):
    """Send a message and get bot response"""
    try:
        # Store the user message
        if request.chat_id not in mock_messages:
            mock_messages[request.chat_id] = []
        
        user_message = {
            "id": len(mock_messages[request.chat_id]) + 1,
            "telegram_id": request.telegram_id,
            "text": request.text,
            "timestamp": datetime.now().isoformat(),
            "is_bot": False
        }
        mock_messages[request.chat_id].append(user_message)
        
        # Get bot response
        bot_response = await route_command_to_bot(request.telegram_id, request.chat_id, request.text)
        
        # Store the bot response
        bot_message = {
            "id": len(mock_messages[request.chat_id]) + 1,
            "telegram_id": 0,  # Bot ID
            "text": bot_response,
            "timestamp": datetime.now().isoformat(),
            "is_bot": True
        }
        mock_messages[request.chat_id].append(bot_message)
        
        return {"message": bot_response, "success": True}
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/invite/process")
async def process_invite(request: InviteRequest):
    """Process an invite token"""
    try:
        # Mock invite processing
        result = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "username": request.username,
            "telegram_id": request.telegram_id,
            "role": "player" if "player" in request.invite_token else "team_member",
            "team_id": "KAI",
            "status": "active"
        }
        return result
    
    except Exception as e:
        logger.error(f"Error processing invite: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    logger.info("🚀 Starting KICKAI Mock API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
