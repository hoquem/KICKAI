#!/usr/bin/env python3
"""
Chat Member Handler for KICKAI

This module handles chat member updates (join/leave) and automatically
assigns appropriate roles based on chat membership.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.ext import ContextTypes

from core.context_manager import get_context_manager
from core.enhanced_logging import ErrorCategory, ErrorSeverity
from features.team_administration.domain.services.chat_role_assignment_service import ChatRoleAssignmentService
from enums import ChatType
from database.firebase_client import FirebaseClient
from loguru import logger

logger = logging.getLogger(__name__)


class ChatMemberHandler:
    """Handles chat member updates and role assignment."""
    
    def __init__(self, team_id: str = None):
        """Initialize the chat member handler."""
        self.team_id = team_id or self._get_default_team_id()
        self.context_manager = get_context_manager()
        
        # Initialize services
        self.firebase_client = FirebaseClient()
        self.chat_role_service = ChatRoleAssignmentService(self.firebase_client)
        
        logger.info(f"✅ ChatMemberHandler initialized for team {self.team_id}")
    
    def _get_default_team_id(self) -> str:
        """Get default team ID."""
        try:
            from core.settings import get_settings
            return get_settings().default_team_id
        except:
            return 'KAI'  # Fallback
    
    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Handle chat member updates (join/leave)."""
        try:
            if not update.chat_member:
                return None
            
            chat_member_update = update.chat_member
            chat = chat_member_update.chat
            new_chat_member = chat_member_update.new_chat_member
            old_chat_member = chat_member_update.old_chat_member
            
            # Determine if this is a join or leave event
            if self._is_user_joining(new_chat_member, old_chat_member):
                return await self._handle_user_joining(chat_member_update)
            elif self._is_user_leaving(new_chat_member, old_chat_member):
                return await self._handle_user_leaving(chat_member_update)
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling chat member update: {e}", exc_info=True)
            logger.error(
                f"Chat member update failed: {e}",
                context={"team_id": self.team_id, "error": str(e)}
            )
            return None
    
    def _is_user_joining(self, new_chat_member: ChatMember, old_chat_member: ChatMember) -> bool:
        """Check if a user is joining the chat."""
        # User was not a member before and is now a member
        return (old_chat_member.status in ['left', 'kicked', 'restricted'] and 
                new_chat_member.status in ['member', 'administrator', 'creator'])
    
    def _is_user_leaving(self, new_chat_member: ChatMember, old_chat_member: ChatMember) -> bool:
        """Check if a user is leaving the chat."""
        # User was a member before and is now not a member
        return (old_chat_member.status in ['member', 'administrator', 'creator'] and 
                new_chat_member.status in ['left', 'kicked', 'restricted'])
    
    async def _handle_user_joining(self, chat_member_update: ChatMemberUpdated) -> Optional[str]:
        """Handle when a user joins a chat."""
        try:
            chat = chat_member_update.chat
            new_chat_member = chat_member_update.new_chat_member
            user = new_chat_member.user
            
            # Determine chat type
            chat_type = self._determine_chat_type(chat.title)
            if not chat_type:
                logger.info(f"Unknown chat type for {chat.title}, skipping role assignment")
                return None
            
            # Add user to chat and assign roles
            result = await self.chat_role_service.add_user_to_chat(
                team_id=self.team_id,
                user_id=str(user.id),
                chat_type=chat_type,
                username=user.username
            )
            
            if result["success"]:
                # Log the event
                logger.info(
                    f"User {user.username or user.id} joined {chat_type} with roles: {result['roles']}",
                    extra={
                        "user_id": str(user.id),
                        "event_type": "user_joined_chat",
                        "chat_id": str(chat.id),
                        "chat_title": chat.title,
                        "chat_type": chat_type,
                        "team_id": self.team_id,
                        "roles_assigned": result["roles"],
                        "is_first_user": result["is_first_user"],
                        "is_admin": result["is_admin"]
                    }
                )
                
                # Generate welcome message
                welcome_message = self._generate_welcome_message(user, result, chat_type)
                logger.info(f"User {user.username or user.id} joined {chat_type} with roles: {result['roles']}")
                return welcome_message
            else:
                logger.warning(f"Failed to assign roles for user {user.id} joining {chat_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error handling user joining: {e}")
            return None
    
    async def _handle_user_leaving(self, chat_member_update: ChatMemberUpdated) -> Optional[str]:
        """Handle when a user leaves a chat."""
        try:
            chat = chat_member_update.chat
            new_chat_member = chat_member_update.new_chat_member
            user = new_chat_member.user
            
            # Determine chat type
            chat_type = self._determine_chat_type(chat.title)
            if not chat_type:
                logger.info(f"Unknown chat type for {chat.title}, skipping role removal")
                return None
            
            # Remove user from chat and update roles
            result = await self.chat_role_service.remove_user_from_chat(
                team_id=self.team_id,
                user_id=str(user.id),
                chat_type=chat_type
            )
            
            if result["success"]:
                # Log the event
                logger.info(
                    f"User {user.username or user.id} left {chat_type}, remaining roles: {result['roles']}",
                    extra={
                        "user_id": str(user.id),
                        "event_type": "user_left_chat",
                        "chat_id": str(chat.id),
                        "chat_title": chat.title,
                        "chat_type": chat_type,
                        "team_id": self.team_id,
                        "remaining_roles": result["roles"]
                    }
                )
                
                logger.info(f"User {user.username or user.id} left {chat_type}, remaining roles: {result['roles']}")
                return None
            else:
                logger.warning(f"Failed to update roles for user {user.id} leaving {chat_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error handling user leaving: {e}")
            return None
    
    def _determine_chat_type(self, chat_title: str) -> Optional[str]:
        """Determine the chat type based on chat title."""
        if not chat_title:
            return None
        
        # Check for leadership chat (ends with "- Leadership")
        if chat_title.endswith(" - Leadership"):
            return ChatType.LEADERSHIP
        
        # Check for main chat (doesn't end with "- Leadership")
        # This is a simplified check - you might want to make this more robust
        return ChatType.MAIN
    
    def _generate_welcome_message(self, user, result: Dict[str, Any], chat_type: str) -> str:
        """Generate a welcome message for new chat members."""
        username = user.username or user.first_name or f"User {user.id}"
        
        if result["is_first_user"]:
            return f"""🎉 <b>Welcome to KICKAI, {username}!</b>

You're the first member of the team! As the first user, you've been automatically assigned admin privileges.

👑 <b>Your Roles:</b>
• Admin (Team Administrator)
• Player (Match Participant)
• Team Member (Leadership Access)

📋 <b>What You Can Do:</b>
• Manage team settings and members
• Approve new player registrations
• Access both main and leadership chats
• Use all admin commands

🎯 <b>Next Steps:</b>
1. Set up your team configuration
2. Invite other team members
3. Start managing your team

Welcome aboard, Team Admin! 🏆

---
<i>This is the {chat_type.replace('_', ' ').title()}</i>"""
        
        elif chat_type == ChatType.MAIN:
            return f"""👋 <b>Welcome to the team, {username}!</b>

You've been added to the main team chat and assigned the player role.

⚽ <b>Your Role:</b>
• Player (Match Participant)

📋 <b>What You Can Do:</b>
• Register as a player: <code>/register [PLAYER_ID]</code>
• Check your status: <code>/myinfo</code>
• Get help: <code>/help</code>

🎯 <b>Next Steps:</b>
1. Complete your player registration
2. Get approved by team admin
3. Start participating in matches

Welcome to the team! ⚽

---
<i>This is the Main Team Chat</i>"""
        
        elif chat_type == ChatType.LEADERSHIP:
            return f"""👔 <b>Welcome to Leadership, {username}!</b>

You've been added to the leadership chat and assigned team member role.

👥 <b>Your Role:</b>
• Team Member (Leadership Access)

📋 <b>What You Can Do:</b>
• Access leadership discussions
• View team management information
• Participate in decision-making

🎯 <b>Next Steps:</b>
1. Familiarize yourself with team operations
2. Contribute to team leadership
3. Help manage team activities

Welcome to the leadership team! 🏆

---
<i>This is the Leadership Chat</i>"""
        
        else:
            return f"""👋 <b>Welcome, {username}!</b>

You've been added to the team chat.

📋 <b>What You Can Do:</b>
• Get help: <code>/help</code>
• Check your status: <code>/myinfo</code>

Welcome to the team! ⚽

---
<i>This is the {chat_type.replace('_', ' ').title()}</i>"""


# Global instance and convenience functions
_chat_member_handler: Optional[ChatMemberHandler] = None


def get_chat_member_handler(team_id: str = None) -> ChatMemberHandler:
    """Get the global chat member handler instance."""
    global _chat_member_handler
    if _chat_member_handler is None:
        _chat_member_handler = ChatMemberHandler(team_id=team_id)
    return _chat_member_handler


async def handle_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Global chat member update handler function."""
    handler = get_chat_member_handler()
    return await handler.handle_chat_member_update(update, context)


def register_chat_member_handler(app):
    """
    Register the chat member handler with the telegram application.
    """
    try:
        from telegram.ext import ChatMemberHandler as TelegramChatMemberHandler
        
        # Register handler for chat member updates
        # Use the correct constant for the telegram library version
        try:
            # For newer versions (22+)
            app.add_handler(TelegramChatMemberHandler(handle_chat_member_update, ChatMemberUpdated.CHAT_MEMBER))
        except AttributeError:
            # For older versions (20+)
            app.add_handler(TelegramChatMemberHandler(handle_chat_member_update, "chat_member"))
        
        logger.info("✅ Chat member handler registered successfully")
        logger.info("   Features: Automatic role assignment, first user admin, welcome messages")
        
    except Exception as e:
        logger.error(f"❌ Failed to register chat member handler: {e}")
        raise 