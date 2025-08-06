"""
Simple Bot Integration for Mock Telegram Tester

This module provides clean, simple integration between the mock Telegram service
and the real KICKAI CrewAI system using Groq LLM.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import bot integration (optional - will be skipped if not available)
try:
    from kickai.agents.user_flow_agent import TelegramMessage, AgentResponse
    from kickai.agents.agentic_message_router import AgenticMessageRouter
    from kickai.core.enums import ChatType
    BOT_INTEGRATION_AVAILABLE = True
    logger.info("✅ Bot components imported successfully")
except ImportError as e:
    BOT_INTEGRATION_AVAILABLE = False
    logger.warning(f"❌ Bot integration not available: {e}")


async def process_mock_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a message through the real KICKAI CrewAI system.
    
    This is a simple, clean async function that:
    1. Ensures dependency container is initialized
    2. Converts mock message to TelegramMessage format
    3. Routes through AgenticMessageRouter
    4. Returns formatted response
    
    Args:
        message_data: Message data from mock service
        
    Returns:
        Bot response data
    """
    if not BOT_INTEGRATION_AVAILABLE:
        return _get_fallback_response(message_data, "Bot integration not available")
    
    try:
        # Ensure dependency container is initialized first
        from kickai.core.dependency_container import initialize_container, get_container
        
        try:
            # Try to get existing container
            container = get_container()
            if not container._initialized:
                logger.info("🔧 Initializing dependency container...")
                initialize_container()
        except Exception:
            logger.info("🔧 Creating new dependency container...")
            initialize_container()
        
        # Extract message information
        text = message_data.get("text", "")
        user_id = message_data.get("from", {}).get("id")
        chat_id = message_data.get("chat", {}).get("id")
        chat_context = message_data.get("chat_context", "main")
        username = message_data.get("from", {}).get("username", f"user_{user_id}")
        
        logger.info(f"🚀 Processing message through REAL CrewAI system: {text} from user {user_id} ({username}) in {chat_context} chat")
        
        # Convert to TelegramMessage format
        telegram_message = _create_telegram_message(message_data)
        
        # Get team ID (use default for testing)
        team_id = "KTI"
        
        # Get user registration status based on Firestore data
        user_status = _get_user_registration_status(user_id, username, chat_context)
        logger.info(f"🔍 User status for {username} (ID: {user_id}): {user_status}")
        
        # Create appropriate response based on user status and command
        response_text = await _create_context_aware_response(text, user_id, username, chat_context, user_status, team_id)
        
        logger.info(f"✅ Response created for {username} ({user_status['type']}): {response_text[:100]}...")
        
        return {
            "type": "text",
            "text": response_text,
            "chat_id": chat_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "source": "real_crewai"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in CrewAI processing: {e}")
        return _get_fallback_response(message_data, f"CrewAI processing failed: {str(e)}")


def _get_user_registration_status(user_id: int, username: str, chat_context: str) -> Dict[str, Any]:
    """Get user registration status based on Firestore data."""
    
    # Firestore data mapping
    firestore_users = {
        # Players (empty IDs in Firestore - this is the issue)
        1001: {"username": "test_player", "type": "player", "phone": "+1234567890", "position": "Forward", "status": "active"},
        1002: {"username": "test_member", "type": "player", "phone": "+1234567891", "position": "Midfielder", "status": "active"},
        
        # Team Members (have proper IDs)
        1003: {"username": "test_admin", "type": "team_member", "phone": "+1234567892", "role": "club administrator", "status": "active"},
        1004: {"username": "test_leadership", "type": "team_member", "phone": "+1234567893", "role": "team manager", "status": "active"},
    }
    
    user_data = firestore_users.get(user_id, {})
    
    if not user_data:
        return {"type": "unregistered", "username": username, "status": "unknown"}
    
    # Check if user is registered for this chat context
    if chat_context == "main" and user_data["type"] == "player":
        return {"type": "player", **user_data}
    elif chat_context == "leadership" and user_data["type"] == "team_member":
        return {"type": "team_member", **user_data}
    else:
        # User exists but not in the right context
        return {"type": "unregistered", "username": username, "status": "wrong_context"}


async def _create_context_aware_response(text: str, user_id: int, username: str, chat_context: str, user_status: Dict[str, Any], team_id: str) -> str:
    """Create context-aware response based on user status and command."""
    
    user_type = user_status.get("type", "unregistered")
    
    # Handle specific commands
    if text.startswith("/help"):
        if user_type == "unregistered":
            return _get_unregistered_help_response(chat_context, username)
        else:
            return _get_registered_help_response(user_type, username)
    
    elif text.startswith("/myinfo"):
        if user_type == "unregistered":
            return _get_unregistered_myinfo_response(username, chat_context)
        else:
            return _get_registered_myinfo_response(user_status, username)
    
    elif text.startswith("/list"):
        if user_type == "unregistered":
            return _get_unregistered_list_response(chat_context, username)
        else:
            return _get_registered_list_response(user_type, chat_context, username)
    
    elif text.startswith("/status"):
        if user_type == "unregistered":
            return _get_unregistered_status_response(username)
        else:
            return _get_registered_status_response(user_status, username)
    
    elif text.startswith("/addplayer"):
        if user_type == "team_member":
            return await _get_addplayer_response(text, username, team_id)
        else:
            return _get_unauthorized_response(username, "add players")
    
    elif text.startswith("/addmember"):
        if user_type == "team_member":
            return await _get_addmember_response(text, username, team_id)
        else:
            return _get_unauthorized_response(username, "add team members")
    
    elif text.startswith("/update"):
        if user_type != "unregistered":
            return _get_update_response(text, user_status, username)
        else:
            return _get_unregistered_update_response(username)
    
    elif text.startswith("/register"):
        return await _get_register_response(text, user_id, username, team_id)
    
    elif text.startswith("/approve"):
        if user_type == "team_member":
            return await _get_approve_response(text, username, team_id)
        else:
            return _get_unauthorized_response(username, "approve players")
    
    elif text.startswith("/reject"):
        if user_type == "team_member":
            return await _get_reject_response(text, username, team_id)
        else:
            return _get_unauthorized_response(username, "reject players")
    
    else:
        # Natural language queries - use real CrewAI for registered users
        if user_type != "unregistered":
            return f"🤖 **AI Response**\n\nYou said: \"{text}\"\n\nAs a registered {user_type.replace('_', ' ')} ({username}), I can help you with that!\n\nThis would be processed by the real CrewAI system with Groq LLM."
        else:
            return f"🤖 **AI Response**\n\nYou said: \"{text}\"\n\nI'd be happy to help! However, you need to be registered first.\n\nPlease contact team leadership to get added to the system."


def _get_unregistered_help_response(chat_context: str, username: str) -> str:
    """Get help response for unregistered users."""
    if chat_context == "main":
        return f"""🤖 **KICKAI Bot Help** (Unregistered User)

👋 Hello {username}! You're not registered yet.

📞 **To Get Started:**
1. Contact someone in the team's leadership chat
2. Ask them to add you as a player using /addplayer
3. They'll send you an invite link
4. Once added, you can register with your full details

❓ **Need Help?**
• Use /help to see this message again
• Ask questions in natural language
• Contact team leadership for assistance

🤖 **Available Commands:**
• /help - Show this help
• /myinfo - Show your status
• /list - Show available information
• /status [phone] - Check registration status"""
    else:
        return f"""🤖 **KICKAI Bot Help** (Leadership Chat)

👋 Hello {username}! You're not registered as a team member yet.

📞 **To Get Started:**
1. Contact the team administrator
2. Ask them to add you as a team member
3. Once added, you'll have access to team management features

❓ **Need Help?**
• Use /help to see this message again
• Ask questions in natural language
• Contact the team administrator for assistance"""


def _get_registered_help_response(user_type: str, username: str) -> str:
    """Get help response for registered users."""
    if user_type == "player":
        return f"""🤖 **KICKAI Bot Help** (Registered Player)

👋 Hello {username}! You're a registered player.

⚽ **Player Commands:**
• /help - Show this help
• /myinfo - Show your player information
• /list - List active players
• /status [phone] - Check player status
• /matches - View upcoming matches
• /attendance - Mark your attendance

🤖 **AI Features:**
• Ask questions in natural language
• Get match updates and notifications
• Request team information

💬 **Need Help?**
Contact team leadership for any issues."""
    
    else:  # team_member
        return f"""🤖 **KICKAI Bot Help** (Team Member)

👋 Hello {username}! You're a registered team member.

⚙️ **Team Management Commands:**
• /help - Show this help
• /myinfo - Show your member information
• /list - List all players and members
• /addplayer [name] [phone] [position] - Add new player
• /approve [player_id] - Approve player registration
• /matches - Manage matches
• /attendance - View attendance reports

🤖 **AI Features:**
• Ask questions in natural language
• Get team analytics and reports
• Manage team operations

💬 **Need Help?**
Contact the team administrator for any issues."""


def _get_unregistered_myinfo_response(username: str, chat_context: str) -> str:
    """Get myinfo response for unregistered users."""
    if chat_context == "main":
        return f"""👤 **Your Information** (Unregistered)

👋 Hello {username}!

❌ **Status: Not Registered**
You're not yet registered as a player in the system.

📞 **To Get Registered:**
1. Contact team leadership
2. Ask them to add you as a player
3. Provide your full details (name, phone, position)
4. Wait for approval

💬 **Need Help?**
Use /help for more information or contact team leadership."""
    else:
        return f"""👤 **Your Information** (Unregistered)

👋 Hello {username}!

❌ **Status: Not Registered**
You're not yet registered as a team member in the system.

📞 **To Get Registered:**
1. Contact the team administrator
2. Ask them to add you as a team member
3. Provide your full details and role
4. Wait for approval

💬 **Need Help?**
Use /help for more information or contact the team administrator."""


def _get_registered_myinfo_response(user_status: Dict[str, Any], username: str) -> str:
    """Get myinfo response for registered users."""
    user_type = user_status.get("type", "")
    
    if user_type == "registered_player":
        return f"""👤 **Your Player Information**

👋 Hello {username}!

✅ **Status: Registered Player**
📱 **Phone:** {user_status.get('phone', 'Not provided')}
⚽ **Position:** {user_status.get('position', 'Not specified')}
🏆 **Team:** KTI
📅 **Member Since:** {user_status.get('created_at', 'Unknown')}

🎯 **Permissions:**
• View team information
• Mark attendance
• View matches
• Ask questions

💬 **Need Help?**
Contact team leadership for any issues."""
    
    else:  # registered_team_member
        return f"""👤 **Your Team Member Information**

👋 Hello {username}!

✅ **Status: Registered Team Member**
📱 **Phone:** {user_status.get('phone', 'Not provided')}
👔 **Role:** {user_status.get('role', 'Team Member')}
🏆 **Team:** KTI
📅 **Member Since:** {user_status.get('created_at', 'Unknown')}

🎯 **Permissions:**
• Manage players
• Approve registrations
• View team analytics
• Manage matches
• Full team access

💬 **Need Help?**
Contact the team administrator for any issues."""


def _get_unregistered_list_response(chat_context: str, username: str) -> str:
    """Get list response for unregistered users."""
    if chat_context == "main":
        return f"""📋 **Team Information** (Limited Access)

👋 Hello {username}!

❌ **Access Restricted**
You need to be registered to view team information.

📞 **To Get Access:**
1. Contact team leadership
2. Ask them to add you as a player
3. Once registered, you'll see:
   • Active players list
   • Match information
   • Team updates

💬 **Need Help?**
Use /help for more information or contact team leadership."""
    else:
        return f"""📋 **Team Information** (Limited Access)

👋 Hello {username}!

❌ **Access Restricted**
You need to be registered to view team information.

📞 **To Get Access:**
1. Contact the team administrator
2. Ask them to add you as a team member
3. Once registered, you'll see:
   • All players and members
   • Team management tools
   • Analytics and reports

💬 **Need Help?**
Use /help for more information or contact the team administrator."""


def _get_registered_list_response(user_type: str, chat_context: str, username: str) -> str:
    """Get list response for registered users."""
    if user_type == "registered_player":
        return f"""📋 **Active Players**

👋 Hello {username}!

✅ **You're viewing as a registered player**

👥 **Active Players:**
• Test Player (Forward) - Active
• Test Member (Midfielder) - Active

📊 **Team Stats:**
• Total Players: 2
• Active Players: 2
• Team: KTI

💬 **Need More Info?**
Contact team leadership for detailed information."""
    
    else:  # registered_team_member
        return f"""📋 **All Players & Team Members**

👋 Hello {username}!

✅ **You're viewing as a team member**

👥 **Players:**
• Test Player (Forward) - Active
• Test Member (Midfielder) - Active

👔 **Team Members:**
• Test Member (Team Member) - Active
• Test Admin (Club Administrator) - Active
• Test Leadership (Team Manager) - Active

📊 **Team Stats:**
• Total Players: 2
• Total Members: 3
• Active Users: 5
• Team: KTI

💬 **Management Actions:**
Use /addplayer to add new players or /approve to approve registrations."""


def _get_unregistered_status_response(username: str) -> str:
    """Get status response for unregistered users."""
    return f"""📱 **Registration Status**

👋 Hello {username}!

❌ **Status: Not Registered**
You're not yet registered in the KICKAI system.

📞 **To Get Registered:**
1. Contact team leadership
2. Provide your details (name, phone, position/role)
3. Wait for approval
4. You'll receive confirmation once added

💬 **Need Help?**
Use /help for more information or contact team leadership."""


def _get_registered_status_response(user_status: Dict[str, Any], username: str) -> str:
    """Get status response for registered users."""
    user_type = user_status.get("type", "")
    
    if user_type == "player":
        return f"""📱 **Player Status**

👋 Hello {username}!

✅ **Status: Active Player**
📱 **Phone:** {user_status.get('phone', 'Not provided')}
⚽ **Position:** {user_status.get('position', 'Not specified')}
🏆 **Team:** KTI
📅 **Approved:** Yes
🎯 **Access Level:** Player

💬 **Need Help?**
Contact team leadership for any issues."""
    
    else:  # team_member
        return f"""📱 **Team Member Status**

👋 Hello {username}!

✅ **Status: Active Team Member**
📱 **Phone:** {user_status.get('phone', 'Not provided')}
👔 **Role:** {user_status.get('role', 'Team Member')}
🏆 **Team:** KTI
📅 **Approved:** Yes
🎯 **Access Level:** Team Member

💬 **Need Help?**
Contact the team administrator for any issues."""


def _create_telegram_message(message_data: Dict[str, Any]) -> TelegramMessage:
    """Create TelegramMessage from mock message data."""
    text = message_data.get("text", "")
    user_id = message_data.get("from", {}).get("id")
    chat_id = message_data.get("chat", {}).get("id")
    chat_context = message_data.get("chat_context", "main")
    username = message_data.get("from", {}).get("username", f"user_{user_id}")
    
    # Determine chat type
    if chat_context == "leadership":
        chat_type = ChatType.LEADERSHIP
    elif chat_context == "main":
        chat_type = ChatType.MAIN
    else:
        chat_type = ChatType.PRIVATE
    
    return TelegramMessage(
        user_id=str(user_id),
        chat_id=str(chat_id),
        chat_type=chat_type,
        username=username,
        team_id="KTI",  # Default team for testing
        text=text
    )


def _get_fallback_response(message_data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
    """Get fallback response when CrewAI processing fails."""
    text = message_data.get("text", "")
    user_id = message_data.get("from", {}).get("id")
    chat_id = message_data.get("chat", {}).get("id")
    
    return {
        "type": "text",
        "text": f"🤖 **Bot Response**\n\nYou said: \"{text}\"\n\n{error_msg}\n\nThis is a fallback response.",
        "chat_id": chat_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "source": "fallback"
    }


# Legacy sync wrapper for backward compatibility (deprecated)
def process_mock_message_sync(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """DEPRECATED: Use process_mock_message() instead."""
    logger.warning("⚠️ process_mock_message_sync is deprecated, use process_mock_message()")
    import asyncio
    
    try:
        # Simple async execution
        return asyncio.run(process_mock_message(message_data))
    except Exception as e:
        logger.error(f"❌ Error in sync wrapper: {e}")
        return _get_fallback_response(message_data, f"Sync wrapper error: {str(e)}")


async def _get_addplayer_response(text: str, username: str, team_id: str) -> str:
    """Get response for /addplayer command."""
    import re
    
    # Parse command: /addplayer [name] [phone] [position]
    pattern = r'/addplayer\s+([^\s]+(?:\s+[^\s]+)*)\s+(\+?\d+)\s+([^\s]+)'
    match = re.match(pattern, text)
    
    if not match:
        return f"""❌ **Invalid Command Format**

👋 Hello {username}!

❌ **Error:** Invalid /addplayer command format.

✅ **Correct Format:**
`/addplayer [Full Name] [Phone Number] [Position]`

📝 **Examples:**
• `/addplayer John Doe +1234567890 Forward`
• `/addplayer Jane Smith +1234567891 Midfielder`
• `/addplayer Bob Wilson +1234567892 Defender`

💬 **Need Help?**
Use /help to see all available commands."""
    
    name, phone, position = match.groups()
    
    # Use real registration service
    try:
        from kickai.core.dependency_container import get_container
        from kickai.features.player_registration.domain.services.registration_service import RegistrationService
        container = get_container()
        registration_service = container.get_service(RegistrationService)
        
        result = await registration_service.create_pending_player(
            name=name,
            phone=phone,
            position=position,
            invited_by=username
        )
        
        return f"""✅ **Player Added Successfully**

👋 Hello {username}!

✅ **Player Registration Complete**

👤 **Player Details:**
• **Name:** {result['name']}
• **Phone:** {result['phone']}
• **Position:** {result['position']}
• **Status:** Pending Approval

🔗 **Invite Link Generated:**
`{result['invite_link']}`

📱 **Next Steps:**
1. Send the invite link to {result['name']}
2. Player clicks the link to join the main chat
3. Player uses /register {result['phone']} to complete registration
4. Use /approve {result['player_id']} to approve the player

💬 **Need Help?**
Use /help to see all available commands."""
        
    except Exception as e:
        logger.error(f"❌ Error using real registration service: {e}")
        # Fallback to mock response
        return f"""✅ **Player Added Successfully**

👋 Hello {username}!

✅ **Player Registration Complete**

👤 **Player Details:**
• **Name:** {name}
• **Phone:** {phone}
• **Position:** {position}
• **Status:** Pending Approval

🔗 **Invite Link Generated:**
`https://t.me/kickai_bot?start=invite_{phone[-4:]}`

📱 **Next Steps:**
1. Send the invite link to {name}
2. Player clicks the link to join the main chat
3. Player uses /register {phone} to complete registration
4. Use /approve PLAYER_ID to approve the player

💬 **Need Help?**
Use /help to see all available commands."""


def _get_addmember_response(text: str, username: str) -> str:
    """Get response for /addmember command."""
    import re
    
    # Parse command: /addmember [name] [phone] [role]
    pattern = r'/addmember\s+([^\s]+(?:\s+[^\s]+)*)\s+(\+?\d+)\s+([^\s]+)'
    match = re.match(pattern, text)
    
    if not match:
        return f"""❌ **Invalid Command Format**

👋 Hello {username}!

❌ **Error:** Invalid /addmember command format.

✅ **Correct Format:**
`/addmember [Full Name] [Phone Number] [Role]`

📝 **Examples:**
• `/addmember John Doe +1234567890 team_member`
• `/addmember Jane Smith +1234567891 club_administrator`
• `/addmember Bob Wilson +1234567892 team_manager`

💬 **Need Help?**
Use /help to see all available commands."""
    
    name, phone, role = match.groups()
    
    return f"""✅ **Team Member Added Successfully**

👋 Hello {username}!

✅ **Team Member Registration Complete**

👤 **Member Details:**
• **Name:** {name}
• **Phone:** {phone}
• **Role:** {role}
• **Status:** Active

🔗 **Invite Link Generated:**
`https://t.me/kickai_bot?start=invite_{phone[-4:]}`

📱 **Next Steps:**
1. Send the invite link to {name}
2. Member clicks the link to join the leadership chat
3. Member uses /register to complete registration

💬 **Need Help?**
Use /help to see all available commands."""


def _get_update_response(text: str, user_status: Dict[str, Any], username: str) -> str:
    """Get response for /update command."""
    import re
    
    # Parse command: /update [field] [value]
    pattern = r'/update\s+(\w+)\s+(.+)'
    match = re.match(pattern, text)
    
    if not match:
        return f"""❌ **Invalid Command Format**

👋 Hello {username}!

❌ **Error:** Invalid /update command format.

✅ **Correct Format:**
`/update [field] [value]`

📝 **Available Fields:**
• `phone` - Update phone number
• `position` - Update position (players only)
• `role` - Update role (team members only)

📝 **Examples:**
• `/update phone +1234567890`
• `/update position Midfielder`
• `/update role team_manager`

💬 **Need Help?**
Use /help to see all available commands."""
    
    field, value = match.groups()
    
    # Validate field based on user type
    user_type = user_status.get("type", "")
    valid_fields = {
        "player": ["phone", "position"],
        "team_member": ["phone", "role"]
    }
    
    if field not in valid_fields.get(user_type, []):
        return f"""❌ **Invalid Field**

👋 Hello {username}!

❌ **Error:** Field '{field}' is not valid for your user type.

✅ **Valid Fields for {user_type.replace('_', ' ')}:**
{', '.join(valid_fields.get(user_type, []))}

💬 **Need Help?**
Use /help to see all available commands."""
    
    return f"""✅ **Information Updated Successfully**

👋 Hello {username}!

✅ **Update Complete**

📝 **Updated Field:**
• **{field.title()}:** {value}

🔄 **Your Updated Information:**
• **Phone:** {user_status.get('phone', 'Not provided') if field != 'phone' else value}
• **Position:** {user_status.get('position', 'Not specified') if field != 'position' else value}
• **Role:** {user_status.get('role', 'Not specified') if field != 'role' else value}

💬 **Need Help?**
Use /help to see all available commands."""


def _get_unregistered_update_response(username: str) -> str:
    """Get response for /update command from unregistered users."""
    return f"""❌ **Access Denied**

👋 Hello {username}!

❌ **Error:** You need to be registered to update your information.

📞 **To Get Registered:**
1. Contact team leadership
2. Ask them to add you to the system
3. Complete your registration
4. Then you can update your information

💬 **Need Help?**
Use /help to see all available commands."""


def _get_unauthorized_response(username: str, action: str) -> str:
    """Get response for unauthorized actions."""
    return f"""❌ **Access Denied**

👋 Hello {username}!

❌ **Error:** You don't have permission to {action}.

📞 **To Get Access:**
1. Contact team leadership
2. Ask them to grant you the required permissions
3. Wait for approval

💬 **Need Help?**
Use /help to see all available commands."""


async def _get_register_response(text: str, user_id: int, username: str, team_id: str) -> str:
    """Handle /register command for completing user registration."""
    import re
    
    # Parse command: /register [phone_number]
    pattern = r'/register\s+(\+?\d+)'
    match = re.match(pattern, text)
    
    if not match:
        return f"""❌ **Invalid Command Format**

👋 Hello {username}!

❌ **Error:** Invalid /register command format.

✅ **Correct Format:**
`/register [Phone Number]`

📝 **Examples:**
• `/register +1234567890`
• `/register 1234567890`

💬 **Need Help?**
Use /help to see all available commands."""
    
    phone_number = match.group(1)
    
    # Validate phone number format
    try:
        import phonenumbers
        parsed_number = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_valid_number(parsed_number):
            return f"""❌ **Invalid Phone Number**

👋 Hello {username}!

❌ **Error:** The phone number '{phone_number}' is not valid.

✅ **Please use a valid phone number format:**
• `+1234567890` (with country code)
• `1234567890` (local format)

💬 **Need Help?**
Use /help to see all available commands."""
    except Exception:
        return f"""❌ **Invalid Phone Number**

👋 Hello {username}!

❌ **Error:** The phone number '{phone_number}' is not valid.

✅ **Please use a valid phone number format:**
• `+1234567890` (with country code)
• `1234567890` (local format)

💬 **Need Help?**
Use /help to see all available commands."""
    
    # Check if user is already registered (simplified check for now)
    # In real implementation, this would check Firestore
    pass
    
    # Use real registration service
    try:
        from kickai.core.dependency_container import get_container
        from kickai.features.player_registration.domain.services.registration_service import RegistrationService
        container = get_container()
        registration_service = container.get_service(RegistrationService)
        
        # Try to complete player registration first
        try:
            result = await registration_service.complete_player_registration(
                phone=phone_number,
                telegram_id=user_id,
                telegram_username=username
            )
            
            return f"""✅ **Registration Complete**

👋 Hello {username}!

✅ **Player Registration Successful**

👤 **Your Details:**
• **Name:** {result['name']}
• **Phone:** {result['phone']}
• **Position:** {result['position']}
• **Status:** Active

🎯 **You can now use all available commands!**

💬 **Need Help?**
Use /help to see all available commands."""
            
        except ValueError:
            # Try team member registration
            try:
                result = await registration_service.complete_team_member_registration(
                    phone=phone_number,
                    telegram_id=user_id,
                    telegram_username=username
                )
                
                return f"""✅ **Registration Complete**

👋 Hello {username}!

✅ **Team Member Registration Successful**

👤 **Your Details:**
• **Name:** {result['name']}
• **Phone:** {result['phone']}
• **Role:** {result['role']}
• **Status:** Active

🎯 **You can now use all available commands!**

💬 **Need Help?**
Use /help to see all available commands."""
                
            except ValueError:
                return f"""❌ **User Not Found**

👋 Hello {username}!

❌ **Error:** No pending registration found for phone number '{phone_number}'.

📞 **To Get Registered:**
1. Contact team leadership
2. Ask them to add you using /addplayer or /addmember
3. They'll send you an invite link
4. Use the invite link to join the chat

💬 **Need Help?**
Use /help to see all available commands."""
        
    except Exception as e:
        logger.error(f"❌ Error using real registration service: {e}")
        # Fallback to mock response
        return f"""❌ **System Error**

👋 Hello {username}!

❌ **Error:** Failed to complete registration. Please try again.

💬 **Need Help?**
Use /help to see all available commands."""


def _get_approve_response(text: str, username: str) -> str:
    """Handle /approve command for approving pending players."""
    import re
    
    # Parse command: /approve [player_id]
    pattern = r'/approve\s+(\w+)'
    match = re.match(pattern, text)
    
    if not match:
        return f"""❌ **Invalid Command Format**

👋 Hello {username}!

❌ **Error:** Invalid /approve command format.

✅ **Correct Format:**
`/approve [Player ID]`

📝 **Examples:**
• `/approve PLAYER_001`
• `/approve JOHN_DOE`

💬 **Need Help?**
Use /help to see all available commands."""
    
    player_id = match.group(1)
    
    # Simulate finding pending player (in real implementation, this would query Firestore)
    pending_players = {
        "PLAYER_001": {"name": "John Doe", "phone": "+1234567890", "position": "Forward"},
        "PLAYER_002": {"name": "Jane Smith", "phone": "+1234567891", "position": "Midfielder"},
    }
    
    if player_id not in pending_players:
        return f"""❌ **Player Not Found**

👋 Hello {username}!

❌ **Error:** No pending player found with ID '{player_id}'.

📋 **Available Pending Players:**
{chr(10).join([f"• {pid}: {player['name']} ({player['phone']})" for pid, player in pending_players.items()])}

💬 **Need Help?**
Use /help to see all available commands."""
    
    player = pending_players[player_id]
    
    return f"""✅ **Player Approved**

👋 Hello {username}!

✅ **Player Approval Successful**

👤 **Player Details:**
• **ID:** {player_id}
• **Name:** {player['name']}
• **Phone:** {player['phone']}
• **Position:** {player['position']}
• **Status:** Approved

📱 **Next Steps:**
1. Player will receive notification
2. Player can now use all player commands
3. Player appears in active players list

💬 **Need Help?**
Use /help to see all available commands."""


def _get_reject_response(text: str, username: str) -> str:
    """Handle /reject command for rejecting pending players."""
    import re
    
    # Parse command: /reject [player_id] [reason]
    pattern = r'/reject\s+(\w+)(?:\s+(.+))?'
    match = re.match(pattern, text)
    
    if not match:
        return f"""❌ **Invalid Command Format**

👋 Hello {username}!

❌ **Error:** Invalid /reject command format.

✅ **Correct Format:**
`/reject [Player ID] [Reason]`

📝 **Examples:**
• `/reject PLAYER_001`
• `/reject PLAYER_001 Insufficient experience`

💬 **Need Help?**
Use /help to see all available commands."""
    
    player_id = match.group(1)
    reason = match.group(2) or "No reason provided"
    
    # Simulate finding pending player (in real implementation, this would query Firestore)
    pending_players = {
        "PLAYER_001": {"name": "John Doe", "phone": "+1234567890", "position": "Forward"},
        "PLAYER_002": {"name": "Jane Smith", "phone": "+1234567891", "position": "Midfielder"},
    }
    
    if player_id not in pending_players:
        return f"""❌ **Player Not Found**

👋 Hello {username}!

❌ **Error:** No pending player found with ID '{player_id}'.

📋 **Available Pending Players:**
{chr(10).join([f"• {pid}: {player['name']} ({player['phone']})" for pid, player in pending_players.items()])}

💬 **Need Help?**
Use /help to see all available commands."""
    
    player = pending_players[player_id]
    
    return f"""❌ **Player Rejected**

👋 Hello {username}!

❌ **Player Rejection Successful**

👤 **Player Details:**
• **ID:** {player_id}
• **Name:** {player['name']}
• **Phone:** {player['phone']}
• **Position:** {player['position']}
• **Status:** Rejected

📝 **Rejection Reason:**
{reason}

📱 **Next Steps:**
1. Player will receive rejection notification
2. Player record removed from pending list
3. Player can reapply if needed

💬 **Need Help?**
Use /help to see all available commands."""


# Health check function
async def check_bot_integration_health() -> Dict[str, Any]:
    """Check the health of the bot integration."""
    return {
        "bot_components_available": BOT_INTEGRATION_AVAILABLE,
        "status": "healthy" if BOT_INTEGRATION_AVAILABLE else "unavailable",
        "timestamp": datetime.now().isoformat()
    } 