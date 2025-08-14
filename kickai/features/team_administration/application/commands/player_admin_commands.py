#!/usr/bin/env python3
"""
Player Administration Commands

This module provides commands for player management by team administrators,
including adding new players with invite link generation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# PLAYER MANAGEMENT COMMANDS
# ============================================================================


@command(
    name="/addplayer",
    description="Add a new player and generate invite link (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    chat_type=ChatType.LEADERSHIP,
    examples=[
        "/addplayer \"John Smith\" \"+447123456789\"",  # Quoted name (recommended)
        "/addplayer John +447123456789",                # Single name (works too) 
        "/addplayer John Smith 07123456789"              # Unquoted multi-word name (smart parsing)
    ],
    parameters={
        "player_name": "Player's full name (use quotes if contains spaces)",
        "phone_number": "Player's phone number (UK format: +447123456789 or 07123456789)",
    },
    help_text="""
🏃‍♂️ Add Player (Leadership Only)

Add a new player to the team and generate an invite link for them to join the main chat.

📝 **Flexible Usage:**
/addplayer <player_name> <phone_number>

✅ **All these formats work:**
• `/addplayer "John Smith" "+447123456789"` (quoted - best for names with spaces)
• `/addplayer John +447123456789` (unquoted single name)
• `/addplayer John Smith 07123456789` (smart parsing - detects phone at end)

📱 **Phone Number Format:**
• UK format: `+447123456789` or `07123456789`
• Must be unique within the team

⚡ **What happens:**
1. Player record created with "pending_activation" status
2. Secure invite link generated (expires in 7 days)  
3. You get formatted message with link to send to player
4. Player joins via link → uses /update → ready to play!

💡 **Smart Features:**
• Automatically detects names vs phone numbers
• Works with or without quotes around names
• Handles multi-word names intelligently
• Phone number validation prevents duplicates
• Only works in leadership chat
    """,
)
async def handle_addplayer_command(update, context, **kwargs):
    """
    Handle /addplayer command for adding new players with invite links.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        **kwargs: Additional context including team_id, user permissions, etc.
    
    Returns:
        Response message with player details and invite link
    """
    try:
        from kickai.core.dependency_container import get_container
        from kickai.core.types import TelegramMessage
        from kickai.core.enums import ChatType
        from kickai.utils.validation_utils import sanitize_input
        import re
        
        # Get message info
        message = update.message
        chat_id = str(message.chat_id)
        telegram_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Get team_id from context
        team_id = kwargs.get("team_id")
        if not team_id:
            return "❌ Team ID not available. Please contact system administrator."
        
        # Parse command arguments
        command_text = message.text.strip()
        
        # Remove the command name to get arguments
        if command_text.startswith("/addplayer"):
            args_text = command_text[10:].strip()  # Remove "/addplayer"
        else:
            return "❌ Invalid command format."
        
        if not args_text:
            return """❌ **Missing Arguments**

Usage: `/addplayer <player_name> <phone_number>`

Examples:
• `/addplayer "John Smith" "+447123456789"`
• `/addplayer "Sarah Johnson" "07987654321"`

💡 Use quotes around names with spaces."""
        
        # Parse arguments - handle both quoted and unquoted formats intelligently
        args = _parse_addplayer_arguments(args_text)
        
        if len(args) < 2:
            return """❌ **Missing Information**

To add a player, I need both a name and phone number.

💡 **Examples that work:**
• `/addplayer "John Smith" "+447123456789"` (quoted name)
• `/addplayer John "+447123456789"` (single name)
• `/addplayer "Sarah Johnson" "07987654321"` (UK format)

📝 **What you provided:** """ + args_text + """
🎯 **What I need:** Player name and phone number"""
        
        if len(args) > 2:
            return """❌ **Too Much Information**

I can only add one player at a time.

💡 **If the name has spaces, use quotes:**
• Correct: `/addplayer "John Smith" "+447123456789"`
• Incorrect: `/addplayer John Smith +447123456789`

📝 **What you provided:** """ + args_text + """
🎯 **Try:** Player name in quotes + phone number"""
        
        player_name = sanitize_input(args[0], 100)
        phone_number = sanitize_input(args[1], 20)
        
        # Validate inputs (check for missing data indicators)
        if not player_name or not player_name.strip() or player_name == "[MISSING_NAME]":
            return "❌ **Player name is required**\n\n💡 Please provide a player name (at least 2 characters)."
        
        if not phone_number or not phone_number.strip() or phone_number == "[MISSING_PHONE]":
            return "❌ **Phone number is required**\n\n💡 Please provide a UK phone number (+447123456789 or 07123456789)."
        
        if len(player_name.strip()) < 2:
            return "❌ **Name too short**\n\n💡 Player name must be at least 2 characters long."
        
        # Route to CrewAI agent via AgenticMessageRouter
        from kickai.agents.agentic_message_router import AgenticMessageRouter
        router = AgenticMessageRouter(team_id)
        
        # Create structured message for the agent
        agent_message_text = f"/addplayer {player_name} {phone_number}"
        
        telegram_message = TelegramMessage(
            telegram_id=telegram_id,
            text=agent_message_text,
            chat_id=chat_id,
            chat_type=ChatType.LEADERSHIP,
            team_id=team_id,
            username=username,
            raw_update=update
        )
        
        # Route to CrewAI system
        response = await router.route_message(telegram_message)
        
        if response and response.success:
            return response.message
        else:
            error_msg = response.error if response else "Unknown error"
            return f"❌ Failed to add player: {error_msg}"
            
    except Exception as e:
        from loguru import logger
        logger.error(f"❌ Error in handle_addplayer_command: {e}")
        return f"❌ System error: {str(e)}"


def _parse_addplayer_arguments(args_text: str) -> list:
    """
    Intelligent argument parser for /addplayer command.
    
    Handles both quoted and unquoted formats:
    - "/addplayer \"John Smith\" \"+447123456789\"" -> ["John Smith", "+447123456789"]  
    - "/addplayer John +447123456789" -> ["John", "+447123456789"]
    - "/addplayer John Smith 07123456789" -> ["John Smith", "07123456789"] (assumes last token is phone)
    
    Args:
        args_text: Raw argument text after /addplayer command
        
    Returns:
        List of parsed arguments [player_name, phone_number]
    """
    import re
    import shlex
    
    if not args_text or not args_text.strip():
        return []
    
    args_text = args_text.strip()
    
    # Try shell-like parsing first (handles quotes properly)
    try:
        args = shlex.split(args_text)
        if len(args) == 2:
            return args
        elif len(args) == 1:
            # Single argument - check if it looks like a phone number
            arg = args[0]
            if _looks_like_phone_number(arg):
                return ["[MISSING_NAME]", arg]  # Clear indicator of missing name
            else:
                return [arg, "[MISSING_PHONE]"]  # Clear indicator of missing phone
        elif len(args) > 2:
            # Multiple arguments - scan for phone number in any position
            phone_index = None
            for i, arg in enumerate(args):
                if _looks_like_phone_number(arg):
                    phone_index = i
                    break
            
            if phone_index is not None:
                # Found phone number - combine other args as name
                phone = args[phone_index]
                name_parts = args[:phone_index] + args[phone_index+1:]
                return [" ".join(name_parts), phone]
            else:
                # No phone found - all args are probably name
                return [" ".join(args), "[MISSING_PHONE]"]
        else:
            return []
    except ValueError:
        # Shlex parsing failed, fall back to manual parsing
        pass
    
    # Manual parsing for edge cases
    # Look for quoted strings first
    quoted_pattern = r'"([^"]*)"'
    quoted_matches = list(re.finditer(quoted_pattern, args_text))
    
    if len(quoted_matches) >= 2:
        # Two quoted strings
        return [quoted_matches[0].group(1), quoted_matches[1].group(1)]
    elif len(quoted_matches) == 1:
        # One quoted string - determine if it's name or phone
        quoted_text = quoted_matches[0].group(1)
        remaining_text = args_text.replace(quoted_matches[0].group(0), "").strip()
        
        if _looks_like_phone_number(quoted_text):
            # Quoted phone number
            return [remaining_text, quoted_text]
        else:
            # Quoted name
            return [quoted_text, remaining_text]
    
    # No quotes - split on whitespace and use heuristics
    tokens = args_text.split()
    if len(tokens) == 2:
        return tokens
    elif len(tokens) == 1:
        # Single token
        if _looks_like_phone_number(tokens[0]):
            return ["[MISSING_NAME]", tokens[0]]
        else:
            return [tokens[0], "[MISSING_PHONE]"]
    elif len(tokens) > 2:
        # Multiple tokens - scan for phone number in any position
        phone_index = None
        for i, token in enumerate(tokens):
            if _looks_like_phone_number(token):
                phone_index = i
                break
        
        if phone_index is not None:
            # Found phone number - combine other tokens as name
            phone = tokens[phone_index]
            name_tokens = tokens[:phone_index] + tokens[phone_index+1:]
            return [" ".join(name_tokens), phone]
        else:
            # No phone found - all tokens are probably name
            return [" ".join(tokens), "[MISSING_PHONE]"]
    
    return []


def _looks_like_phone_number(text: str) -> bool:
    """
    Simple heuristic to identify if text looks like a phone number.
    
    Args:
        text: Text to check
        
    Returns:
        True if text looks like a phone number
    """
    import re
    
    if not text:
        return False
    
    # Check for common UK phone patterns first
    if text.startswith(('+44', '07', '44')):
        digits_only = re.sub(r'[+\-\s\(\)]', '', text)
        return digits_only.isdigit() and 10 <= len(digits_only) <= 15
    
    # Check if text starts with + and has reasonable digit count  
    if text.startswith('+'):
        digits_only = re.sub(r'[+\-\s\(\)]', '', text)
        return digits_only.isdigit() and 10 <= len(digits_only) <= 15
        
    # Check if it's all digits with reasonable length (for cases like "07123456789")
    digits_only = re.sub(r'[+\-\s\(\)]', '', text)
    if digits_only.isdigit() and 10 <= len(digits_only) <= 15:
        return True
        
    return False