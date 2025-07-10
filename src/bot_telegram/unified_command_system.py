#!/usr/bin/env python3
"""
Unified Command System for KICKAI Bot

This module implements a clean, maintainable command architecture using:
- Command Pattern: Each command is a separate object
- Strategy Pattern: Different permission strategies
- Chain of Responsibility: Command routing and validation
- Factory Pattern: Command creation
- Observer Pattern: Command logging and monitoring

This replaces the multiple overlapping routing systems with a single, clean architecture.
"""

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any

from domain.interfaces.command_operations import ICommandOperations
from services.command_operations_factory import get_command_operations
from services.access_control_service import AccessControlService
from core.enhanced_logging import (
    log_command_error, log_error, ErrorCategory, ErrorSeverity, 
    ErrorMessageTemplates, create_error_context
)
from services.background_tasks import get_background_tasks_service
from bot_telegram.improved_command_parser import parse_command, CommandType
from core.exceptions import (
    KICKAIError, PlayerError, TeamError, ValidationError, 
    PlayerDuplicateError, PlayerNotFoundError, TeamNotFoundError
)

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class PermissionLevel(Enum):
    """Permission levels for commands."""
    PUBLIC = "public"
    PLAYER = "player"
    LEADERSHIP = "leadership"
    ADMIN = "admin"


class ChatType(Enum):
    """Chat types for context."""
    MAIN = "main"
    LEADERSHIP = "leadership"
    PRIVATE = "private"


@dataclass
class CommandContext:
    """Context for command execution."""
    user_id: str
    chat_id: str
    chat_type: ChatType
    user_role: str
    team_id: str
    message_text: str
    username: Optional[str] = None
    raw_update: Optional[Any] = None


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# PERMISSION STRATEGIES (Strategy Pattern)
# ============================================================================

class PermissionStrategy(ABC):
    """Abstract base class for permission strategies."""
    
    @abstractmethod
    def can_execute(self, context: CommandContext) -> bool:
        """Check if command can be executed in given context."""
        pass
    
    @abstractmethod
    def get_access_denied_message(self, context: CommandContext) -> str:
        """Get access denied message."""
        pass


class PublicPermissionStrategy(PermissionStrategy):
    """Strategy for public commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        return True
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return "❌ This command should be available to everyone. Please contact admin."


class PlayerPermissionStrategy(PermissionStrategy):
    """Strategy for player commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        # CHAT-BASED: Allow in main chat or leadership chat
        return context.chat_type in [ChatType.MAIN, ChatType.LEADERSHIP]
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 This command requires player access.
💡 Contact your team admin for access.

Your Role: {context.user_role.title()}"""


class LeadershipPermissionStrategy(PermissionStrategy):
    """Strategy for leadership commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        # CHAT-BASED: Only allow in leadership chat (no role check)
        return context.chat_type == ChatType.LEADERSHIP
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 Leadership commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""


class AdminPermissionStrategy(PermissionStrategy):
    """Strategy for admin commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        # CHAT-BASED: Only allow in leadership chat (no role check)
        return context.chat_type == ChatType.LEADERSHIP
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 Admin commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""


# ============================================================================
# COMMAND INTERFACE (Command Pattern)
# ============================================================================

class Command(ABC):
    """Abstract base class for all commands."""
    
    def __init__(self, name: str, description: str, permission_level: PermissionLevel):
        self.name = name
        self.description = description
        self.permission_level = permission_level
        self._permission_strategy = self._get_permission_strategy()
    
    def _get_permission_strategy(self) -> PermissionStrategy:
        """Get the appropriate permission strategy."""
        strategies = {
            PermissionLevel.PUBLIC: PublicPermissionStrategy(),
            PermissionLevel.PLAYER: PlayerPermissionStrategy(),
            PermissionLevel.LEADERSHIP: LeadershipPermissionStrategy(),
            PermissionLevel.ADMIN: AdminPermissionStrategy(),
        }
        return strategies[self.permission_level]
    
    def can_execute(self, context: CommandContext) -> bool:
        """Check if command can be executed."""
        return self._permission_strategy.can_execute(context)
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        """Get access denied message."""
        return self._permission_strategy.get_access_denied_message(context)
    
    @abstractmethod
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the command."""
        pass
    
    def get_help_text(self) -> str:
        """Get help text for this command."""
        return f"`{self.name}` - {self.description}"


# ============================================================================
# CONCRETE COMMANDS
# ============================================================================

class HelpCommand(Command):
    """Help command implementation."""
    
    def __init__(self, command_registry: 'CommandRegistry'):
        super().__init__("/help", "Show available commands", PermissionLevel.PUBLIC)
        self.command_registry = command_registry
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # CHAT-BASED PERMISSIONS: Show commands based on chat type only
            all_commands = self.command_registry.get_all_commands()
            
            if context.chat_type == ChatType.LEADERSHIP:
                # Leadership chat: Show ALL commands (public, player, leadership, admin)
                public_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PUBLIC]
                player_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PLAYER]
                leadership_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.LEADERSHIP]
                admin_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.ADMIN]
            else:
                # Main chat: Show only public and player commands
                public_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PUBLIC]
                player_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PLAYER]
                leadership_commands = []
                admin_commands = []
            
            # Build help message
            if context.chat_type == ChatType.LEADERSHIP:
                title = "🤖 KICKAI BOT HELP (LEADERSHIP)"
            else:
                title = "🤖 KICKAI BOT HELP"
            
            message = f"{title}\n\n📋 AVAILABLE COMMANDS:\n\n"
            
            if public_commands:
                message += "🌐 GENERAL:\n"
                for cmd in public_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            if player_commands:
                message += "👥 PLAYER:\n"
                for cmd in player_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            if leadership_commands:
                message += "👑 LEADERSHIP:\n"
                for cmd in leadership_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            if admin_commands:
                message += "🔧 ADMIN:\n"
                for cmd in admin_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            message += "💡 TIPS:\n"
            message += "• Use natural language: \"Add John Smith as midfielder\"\n"
            message += "• Type /help [command] for detailed help\n"
            if context.chat_type != ChatType.LEADERSHIP:
                message += "• Admin commands available in leadership chat\n"
            
            return CommandResult(success=True, message=message)
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            return CommandResult(success=False, message="❌ Error displaying help", error=str(e))


class ListPlayersCommand(Command):
    """List players command implementation."""
    
    def __init__(self):
        super().__init__("/list", "List all players", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Pass the chat type information to determine if this is leadership chat
            is_leadership_chat = context.chat_type == ChatType.LEADERSHIP
            result = await command_operations.list_players(context.team_id, is_leadership_chat)
            return CommandResult(success=True, message=result)
            
        except KICKAIError as user_error:
            # User-facing error
            logger.info(f"[ListPlayersCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[ListPlayersCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while listing players. Please try again later.",
                error=str(e)
            )


class MyInfoCommand(Command):
    """MyInfo command implementation."""
    
    def __init__(self):
        super().__init__("/myinfo", "Get your player information", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            logger.info(f"[MyInfoCommand] Processing for user {context.user_id} in team {context.team_id}")
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            
            logger.info(f"[MyInfoCommand] Command operations created, calling get_player_info for user {context.user_id}")
            
            # Get player info by telegram user ID
            success, message = await command_operations.get_player_info(context.user_id, context.team_id)
            
            logger.info(f"[MyInfoCommand] get_player_info returned success={success}, message_length={len(message) if message else 0}")
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                logger.warning(f"[MyInfoCommand] Failed to get player info for user {context.user_id}: {message}")
                return CommandResult(success=False, message=message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., player not found)
            logger.info(f"[MyInfoCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[MyInfoCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while getting your information. Please try again later.",
                error=str(e)
            )


class StatusCommand(Command):
    """Status command implementation."""
    
    def __init__(self):
        super().__init__("/status", "Check player status (your own or by phone)", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Parse command to see if phone number is provided
            parts = context.message_text.split()
            
            # If no phone provided, check the user's own status
            if len(parts) < 2:
                command_operations = get_command_operations(team_id=context.team_id)
                success, message = await command_operations.get_player_info(context.user_id, context.team_id)
                
                if success:
                    return CommandResult(success=True, message=f"📊 <b>Your Status</b>\n\n{message}")
                else:
                    return CommandResult(success=False, message="❌ Player not found. Please contact team admin.")
            
            # If phone provided, check that specific player's status (admin function)
            raw_phone = parts[1]
            
            # Normalize phone number as early as possible
            from utils.phone_utils import normalize_phone
            normalized_phone = normalize_phone(raw_phone)
            if not normalized_phone:
                return CommandResult(success=False, message=f"❌ Invalid phone number format: {raw_phone}. Must be valid UK mobile format (07xxx or +447xxx)")
            
            # Check if user has permission to check other players (admin/leadership)
            if context.chat_type != ChatType.LEADERSHIP:
                return CommandResult(
                    success=False, 
                    message="❌ Checking other players' status is only available in the leadership chat."
                )
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            player_info = await command_operations.get_player_by_phone(normalized_phone, context.team_id)
            
            if not player_info:
                return CommandResult(success=False, message=f"❌ Player with phone {raw_phone} not found")
            
            # Format player status for admin view
            status_message = f"""📊 <b>Player Status: {player_info.name}</b>

📋 <b>Basic Info:</b>
• Name: {player_info.name}
• Player ID: {player_info.player_id.upper()}
• Position: {player_info.position.title()}
• Phone: {player_info.phone}

📊 <b>Status:</b>
• Onboarding: {player_info.onboarding_status.title()}
• FA Registered: {'Yes' if player_info.is_fa_registered else 'No'}
• FA Eligible: {'Yes' if player_info.is_fa_eligible else 'No'}
• Match Eligible: {'Yes' if player_info.is_match_eligible else 'No'}

📞 <b>Contact Info:</b>
• Emergency Contact: {player_info.emergency_contact or 'Not provided'}
• Date of Birth: {player_info.date_of_birth or 'Not provided'}
• Telegram: @{player_info.telegram_username or 'Not linked'}

📅 <b>Timestamps:</b>
• Created: {player_info.created_at or 'Unknown'}
• Last Updated: {player_info.updated_at or 'Unknown'}"""
            
            return CommandResult(success=True, message=status_message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., player not found, invalid phone)
            logger.info(f"[StatusCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[StatusCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while checking player status. Please try again later.",
                error=str(e)
            )


class RegisterCommand(Command):
    """Register command implementation."""
    
    def __init__(self):
        super().__init__("/register", "Register as a new player", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Check if this is just /register (no arguments)
            if context.message_text.strip() == "/register":
                if context.chat_type == ChatType.LEADERSHIP:
                    message = """📝 PLAYER REGISTRATION (ADMIN)

To add a new player to the team:

1️⃣ ADD PLAYER:
   /add [name] [phone] [position]
   Example: /add John Smith 07123456789 midfielder

2️⃣ GENERATE INVITATION:
   /invitelink [phone_or_player_id]
   Example: /invitelink 07123456789

3️⃣ PLAYER APPROVAL:
   /approve [player_id]
   Example: /approve AB1

4️⃣ CHECK STATUS:
   /status [phone_or_player_id]
   Example: /status 07123456789

5️⃣ LIST PLAYERS:
   /list [filter]
   Example: /list pending

6️⃣ REMOVE PLAYER:
   /remove [phone_or_player_id]
   Example: /remove 07123456789

7️⃣ REJECT PLAYER:
   /reject [player_id] [reason]
   Example: /reject AB1 "Not available"

8️⃣ PENDING APPROVALS:
   /pending
   Shows all players awaiting approval

🔟 TEAM MANAGEMENT:
   /addteam [name] [description]
   /removeteam [team_id]
   /listteams [filter]
   /updateteaminfo [team_id] [field] [value]

⚽ MATCH MANAGEMENT:
   /creatematch [date] [time] [location] [opponent]
   /attendmatch [match_id] [availability]
   /unattendmatch [match_id]
   /listmatches [filter]
   /recordresult [match_id] [our_score] [their_score]

💰 PAYMENT MANAGEMENT:
   /createpayment [amount] [description] [player_id]
   /paymentstatus [payment_id/player_id]
   /pendingpayments [filter]
   /paymenthistory [player_id] [period]
   /financialdashboard [period]

👑 ADMIN COMMANDS:
   /broadcast [message] [target]
   /promoteuser [user_id] [role]
   /demoteuser [user_id] [reason]
   /systemstatus [detailed]"""
                else:
                    message = """📝 PLAYER REGISTRATION

To register as a new player, you need an invitation from a team admin.

HOW TO REGISTER:
1. Ask a team admin to add you to the team
2. The admin will generate an invitation link for you
3. Click the invitation link to join the team
4. Complete your profile information

ALTERNATIVE:
If you have a player ID, use:
/register [player_id]

NEED HELP?
Contact a team admin in the leadership chat for assistance."""
                return CommandResult(success=True, message=message)
            
            # Parse command with arguments
            from bot_telegram.improved_command_parser import parse_command, CommandType
            
            parsed = parse_command(context.message_text)
            if not parsed.is_valid or parsed.command_type != CommandType.REGISTER:
                return CommandResult(success=False, message="❌ Usage: /register [player_id]")
            
            # Extract player_id parameter
            player_id = parsed.get_parameter("player_id")
            if not player_id:
                return CommandResult(success=False, message="❌ Usage: /register [player_id]")
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            success, message = await command_operations.register_player(context.user_id, context.team_id, player_id)
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                error_message = f"❌ {message}\n\n💡 Please contact the team admin if you believe this is an error."
                return CommandResult(success=False, message=error_message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., invalid player ID, already registered)
            logger.info(f"[RegisterCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[RegisterCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while processing your registration. Please try again later.",
                error=str(e)
            )


class AddPlayerCommand(Command):
    """Add player command implementation."""
    
    def __init__(self):
        super().__init__("/add", "Add a new player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        logger.info(f"[AddPlayerCommand] execute called with context: user_id={context.user_id}, team_id={context.team_id}, message='{context.message_text}'")
        try:
            # Parse command
            parsed = parse_command(context.message_text)
            if not parsed.is_valid:
                logger.warning(f"[AddPlayerCommand] Command parsing failed: {parsed.error_message}")
                return CommandResult(success=False, message=f"❌ {parsed.error_message or 'Parameter validation failed'}")
            
            # Extract parameters
            name = parsed.get_parameter("name")
            phone = parsed.get_parameter("phone")
            position = parsed.get_parameter("position")
            player_id = parsed.get_parameter("player_id")
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            success, message = await command_operations.add_player(name, phone, position, context.team_id)
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., duplicate player, validation error)
            logger.info(f"[AddPlayerCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error (e.g., database connection, code bug)
            logger.error(f"[AddPlayerCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while adding the player. Please try again later.",
                error=str(e)
            )


class RemovePlayerCommand(Command):
    """Remove player command implementation."""
    
    def __init__(self):
        super().__init__("/remove", "Remove a player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Parse command
            parts = context.message_text.split()
            if len(parts) < 2:
                return CommandResult(success=False, message="❌ Usage: /remove [player_id]")
            
            player_id = parts[1]
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            success, message = await command_operations.remove_player(player_id, context.team_id)
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., player not found)
            logger.info(f"[RemovePlayerCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[RemovePlayerCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while removing the player. Please try again later.",
                error=str(e)
            )


class ApprovePlayerCommand(Command):
    """Approve player command implementation."""
    
    def __init__(self):
        super().__init__("/approve", "Approve a player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Use centralized ID processor for entity extraction
            from utils.id_processor import extract_entities_from_command, IDType
            
            # Extract player_id using centralized processor
            result = extract_entities_from_command(context.message_text, "/approve")
            player_id = result.entities.get('player_id')
            
            if not player_id or not player_id.is_valid:
                return CommandResult(success=False, message="❌ Usage: /approve [player_id]")
            
            # Use the normalized player_id value
            normalized_player_id = player_id.normalized_value
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            success, message = await command_operations.approve_player(normalized_player_id, context.team_id)
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., player not found, already approved)
            logger.info(f"[ApprovePlayerCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[ApprovePlayerCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while approving the player. Please try again later.",
                error=str(e)
            )


class RejectPlayerCommand(Command):
    """Reject player command implementation."""
    
    def __init__(self):
        super().__init__("/reject", "Reject a player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Parse command
            parts = context.message_text.split()
            if len(parts) < 3:
                return CommandResult(success=False, message="❌ Usage: /reject [player_id] [reason]")
            
            player_id = parts[1]
            reason = " ".join(parts[2:])
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            success, message = await command_operations.reject_player(player_id, reason, context.team_id)
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., player not found, already rejected)
            logger.info(f"[RejectPlayerCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[RejectPlayerCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while rejecting the player. Please try again later.",
                error=str(e)
            )


class PendingApprovalsCommand(Command):
    """Pending approvals command implementation."""
    
    def __init__(self):
        super().__init__("/pending", "List players pending approval", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            result = await command_operations.get_pending_approvals(context.team_id)
            return CommandResult(success=True, message=result)
            
        except KICKAIError as user_error:
            # User-facing error
            logger.info(f"[PendingApprovalsCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[PendingApprovalsCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while getting pending approvals. Please try again later.",
                error=str(e)
            )


class CheckFACommand(Command):
    """Check FA registration command implementation."""
    
    def __init__(self):
        super().__init__("/checkfa", "Check FA registration status", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Parse command
            parts = context.message_text.split()
            if len(parts) < 2:
                return CommandResult(success=False, message="❌ Usage: /checkfa [player_id]")
            
            player_id = parts[1]
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            success, message = await command_operations.check_fa_registration(player_id, context.team_id)
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message)
                
        except KICKAIError as user_error:
            # User-facing error (e.g., player not found)
            logger.info(f"[CheckFACommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[CheckFACommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while checking FA registration. Please try again later.",
                error=str(e)
            )


class DailyStatusCommand(Command):
    """Daily status command implementation."""
    
    def __init__(self):
        super().__init__("/dailystatus", "Get daily status report", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            result = await command_operations.get_daily_status(context.team_id)
            return CommandResult(success=True, message=result)
            
        except KICKAIError as user_error:
            # User-facing error
            logger.info(f"[DailyStatusCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[DailyStatusCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while getting daily status. Please try again later.",
                error=str(e)
            )


class BackgroundTasksCommand(Command):
    """Background tasks command implementation."""
    
    def __init__(self):
        super().__init__("/background", "Run background tasks", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            result = await command_operations.run_background_tasks(context.team_id)
            return CommandResult(success=True, message=result)
            
        except KICKAIError as user_error:
            # User-facing error
            logger.info(f"[BackgroundTasksCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[BackgroundTasksCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while running background tasks. Please try again later.",
                error=str(e)
            )


class RemindCommand(Command):
    """Remind command implementation."""
    
    def __init__(self):
        super().__init__("/remind", "Send a reminder to team members", PermissionLevel.LEADERSHIP)
    
    def get_help_text(self) -> str:
        return "`/remind [message]` - Send a reminder to all team members"
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Parse command
            parts = context.message_text.split(maxsplit=1)
            if len(parts) < 2:
                return CommandResult(success=False, message="❌ Usage: /remind [message]")
            
            message = parts[1]
            
            # Execute command
            command_operations = get_command_operations(team_id=context.team_id)
            success, result = await command_operations.send_reminder(message, context.team_id)
            
            if success:
                return CommandResult(success=True, message=result)
            else:
                return CommandResult(success=False, message=result)
                
        except KICKAIError as user_error:
            # User-facing error
            logger.info(f"[RemindCommand] User-facing error: {user_error}")
            return CommandResult(success=False, message=str(user_error))
            
        except Exception as e:
            # System error
            logger.error(f"[RemindCommand] System error: {e}", exc_info=True)
            return CommandResult(
                success=False, 
                message="❌ Sorry, something went wrong while sending the reminder. Please try again later.",
                error=str(e)
            )


# ============================================================================
# MATCH COMMANDS
# ============================================================================

class CreateTeamCommand(Command):
    """Command to create a new team."""

    def __init__(self):
        super().__init__("/create_team", "Create a new team", PermissionLevel.ADMIN)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)

            parts = context.message_text.split(maxsplit=2)
            if len(parts) < 2:
                return CommandResult(
                    success=False,
                    message="❌ Usage: /create_team <team_name> [description]",
                    error="Missing team name"
                )

            team_name = parts[1]
            description = parts[2] if len(parts) > 2 else None

            success, message = await command_operations.create_team(team_name, description, context.user_id)
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message, error=message)
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            return CommandResult(success=False, message=f"❌ Error creating team: {str(e)}", error=str(e))


class DeleteTeamCommand(Command):
    """Command to delete a team."""

    def __init__(self):
        super().__init__("/delete_team", "Delete a team", PermissionLevel.ADMIN)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)

            parts = context.message_text.split()
            if len(parts) < 2:
                return CommandResult(
                    success=False,
                    message="❌ Usage: /delete_team <team_id>",
                    error="Missing team ID"
                )

            team_id = parts[1]
            success, message = await command_operations.delete_team(team_id)
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message, error=message)
        except Exception as e:
            logger.error(f"Error deleting team: {e}")
            return CommandResult(success=False, message=f"❌ Error deleting team: {str(e)}", error=str(e))


class ListTeamsCommand(Command):
    """Command to list all teams."""

    def __init__(self):
        super().__init__("/list_teams", "List all teams", PermissionLevel.ADMIN)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)

            result = await command_operations.list_teams()
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error listing teams: {e}")
            return CommandResult(success=False, message=f"❌ Error listing teams: {str(e)}", error=str(e))


class CreateMatchCommand(Command):
    """Command to create a new match/fixture."""
    
    def __init__(self):
        super().__init__("/newmatch", "Create a new match/fixture", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the create match command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            import re
            
            # Parse the message for match details
            message = context.message_text.lower()
            
            # Extract match details using regex patterns
            opponent = self._extract_opponent(message)
            date = self._extract_date(message)
            time = self._extract_time(message)
            venue = self._extract_venue(message) or "Home"
            competition = self._extract_competition(message) or "League"
            
            # Validate required fields
            if not opponent:
                return CommandResult(
                    success=False,
                    message="❌ Please specify an opponent.\n\nExample: `/newmatch Arsenal on July 1st at 2pm`",
                    error="Missing opponent"
                )
            
            if not date:
                return CommandResult(
                    success=False,
                    message="❌ Please specify a date.\n\nExample: `/newmatch Arsenal on July 1st at 2pm`",
                    error="Missing date"
                )
            
            if not time:
                return CommandResult(
                    success=False,
                    message="❌ Please specify a time.\n\nExample: `/newmatch Arsenal on July 1st at 2pm`",
                    error="Missing time"
                )
            
            # Create the fixture
            success, message = await command_operations.create_match(
                context.team_id, opponent, date, time, venue, competition
            )
            
            if success:
                return CommandResult(
                    success=True,
                    message=message
                )
            else:
                return CommandResult(
                    success=False,
                    message=message,
                    error=message
                )
                
        except Exception as e:
            logger.error(f"Error creating match: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error creating match: {str(e)}",
                error=str(e)
            )
    
    def _extract_opponent(self, message: str) -> str:
        """Extract opponent from message."""
        patterns = [
            r'against\s+([a-zA-Z\s]+?)(?:\s+on|\s+at|\s+vs|\s+v|\s+versus|$)',
            r'vs\s+([a-zA-Z\s]+?)(?:\s+on|\s+at|$)',
            r'v\s+([a-zA-Z\s]+?)(?:\s+on|\s+at|$)',
            r'versus\s+([a-zA-Z\s]+?)(?:\s+on|\s+at|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_date(self, message: str) -> str:
        """Extract date from message."""
        patterns = [
            r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_time(self, message: str) -> str:
        """Extract time from message."""
        patterns = [
            r'(\d{1,2}:\d{2})',
            r'(\d{1,2}(?:am|pm))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_venue(self, message: str) -> str:
        """Extract venue from message."""
        if 'home' in message:
            return "Home"
        elif 'away' in message:
            return "Away"
        return None
    
    def _extract_competition(self, message: str) -> str:
        """Extract competition from message."""
        competitions = ['league', 'cup', 'friendly', 'tournament']
        for comp in competitions:
            if comp in message:
                return comp.title()
        return None


class ListMatchesCommand(Command):
    """Command to list all matches/fixtures."""
    
    def __init__(self):
        super().__init__("/listmatches", "List all matches/fixtures", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the list matches command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            result = await command_operations.list_matches(context.team_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error listing matches: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error listing matches: {str(e)}",
                error=str(e)
            )


class GetMatchCommand(Command):
    """Command to get details of a specific match."""
    
    def __init__(self):
        super().__init__("/getmatch", "Get details of a specific match", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the get match command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            import re
            
            message = context.message_text
            match_id = self._extract_match_id(message)
            
            if not match_id:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a match ID.\n\nExample: `/getmatch MATCH123`",
                    error="Missing match ID"
                )
            
            result = await command_operations.get_match(context.team_id, match_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error getting match: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error getting match: {str(e)}",
                error=str(e)
            )
    
    def _extract_match_id(self, message: str) -> str:
        """Extract match ID from message."""
        match = re.search(r'/getmatch\s+(\w+)', message)
        return match.group(1) if match else None


class UpdateMatchCommand(Command):
    """Command to update a match/fixture."""
    
    def __init__(self):
        super().__init__("/updatematch", "Update a match/fixture", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the update match command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            import re
            
            message = context.message_text
            match_id = self._extract_match_id(message)
            
            if not match_id:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a match ID.\n\nExample: `/updatematch MATCH123 opponent=Arsenal`",
                    error="Missing match ID"
                )
            
            updates = self._extract_updates(message)
            if not updates:
                return CommandResult(
                    success=False,
                    message="❌ Please provide at least one field to update.\n\nExample: `/updatematch MATCH123 opponent=Arsenal time=15:00`",
                    error="No updates provided"
                )
            
            success, message = await command_operations.update_match(context.team_id, match_id, updates)
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message, error=message)
        except Exception as e:
            logger.error(f"Error updating match: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error updating match: {str(e)}",
                error=str(e)
            )
    
    def _extract_match_id(self, message: str) -> str:
        """Extract match ID from message."""
        match = re.search(r'/updatematch\s+(\w+)', message)
        return match.group(1) if match else None
    
    def _extract_updates(self, message: str) -> dict:
        """Extract update fields from message."""
        updates = {}
        pattern = r'(\w+)=([^,\s]+)'
        matches = re.findall(pattern, message)
        
        for key, value in matches:
            updates[key] = value
        
        return updates


class DeleteMatchCommand(Command):
    """Command to delete a match/fixture."""
    
    def __init__(self):
        super().__init__("/deletematch", "Delete a match/fixture", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the delete match command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            import re
            
            message = context.message_text
            match_id = self._extract_match_id(message)
            
            if not match_id:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a match ID.\n\nExample: `/deletematch MATCH123`",
                    error="Missing match ID"
                )
            
            success, message = await command_operations.delete_match(context.team_id, match_id)
            if success:
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message=message, error=message)
        except Exception as e:
            logger.error(f"Error deleting match: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error deleting match: {str(e)}",
                error=str(e)
            )
    
    def _extract_match_id(self, message: str) -> str:
        """Extract match ID from message."""
        match = re.search(r'/deletematch\s+(\w+)', message)
        return match.group(1) if match else None


class RecordResultCommand(Command):
    """Record match result command."""

    def __init__(self):
        super().__init__("/record_result", "Record a match result", PermissionLevel.LEADERSHIP)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            args = context.message_text.split()[1:]
            success, message = await command_operations.record_match_result(context.team_id, args)
            return CommandResult(success=success, message=message)
        except Exception as e:
            logger.error(f"Record result command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error recording result: {str(e)}",
                error=str(e)
            )


# ============================================================================
# ADDITIONAL ADMIN COMMANDS


# ============================================================================
# ADDITIONAL ADMIN COMMANDS
# ============================================================================

class StatsCommand(Command):
    """Command to show team statistics."""
    
    def __init__(self):
        super().__init__("/stats", "Show team statistics", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the stats command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            result = await command_operations.get_team_stats(context.team_id)
            return CommandResult(success=True, message=result)
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error getting stats: {str(e)}",
                error=str(e)
            )


class InviteLinkCommand(Command):
    """Command to invite a player to the team."""
    
    def __init__(self):
        super().__init__("/invitelink", "Generate invitation link for a player", PermissionLevel.LEADERSHIP)
    
    def get_help_text(self) -> str:
        return "`/invitelink [phone_or_player_id]` - Generate invitation message"
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the invitelink command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            import re
            
            message = context.message_text
            identifier = self._extract_identifier(message)
            
            if not identifier:
                return CommandResult(
                    success=False,
                    message="❌ Please provide phone number or player ID.\n\nExamples:\n• `/invitelink 07123456789`\n• `/invitelink AB1`",
                    error="Missing identifier"
                )
            
            # Normalize phone number if it's a phone number
            if self._is_phone_number(identifier):
                from utils.phone_utils import normalize_phone
                normalized_phone = normalize_phone(identifier)
                if not normalized_phone:
                    return CommandResult(
                        success=False,
                        message=f"❌ Invalid phone number format: {identifier}. Must be valid UK mobile format (07xxx or +447xxx)",
                        error="Invalid phone number"
                    )
                identifier = normalized_phone
            
            success, message = await command_operations.generate_invitation(context.team_id, identifier)
            return CommandResult(success=success, message=message)
                
        except Exception as e:
            logger.error(f"Error sending invitation: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error sending invitation: {str(e)}",
                error=str(e)
            )
    
    def _extract_identifier(self, message: str) -> Optional[str]:
        """Extract phone number or player ID from message."""
        # Try to match phone number first (11 digits)
        phone_match = re.search(r'/invitelink\s+(\d{11})', message)
        if phone_match:
            return phone_match.group(1)
        
        # Try to match player ID (letters and numbers, typically 2-4 characters)
        player_id_match = re.search(r'/invitelink\s+([A-Za-z0-9]{2,4})', message)
        if player_id_match:
            return player_id_match.group(1)
        
        return None
    
    def _is_phone_number(self, identifier: str) -> bool:
        """Check if identifier is a phone number."""
        return bool(re.match(r'^\d{11}$', identifier))


class BroadcastCommand(Command):
    """Command to broadcast a message to all team members."""
    
    def __init__(self):
        super().__init__("/broadcast", "Broadcast a message to all team members", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the broadcast command."""
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            message = context.message_text
            broadcast_message = self._extract_broadcast_message(message)
            
            if not broadcast_message:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a message to broadcast.\n\nExample: `/broadcast Training cancelled tomorrow`",
                    error="Missing broadcast message"
                )
            
            success, message = await command_operations.send_broadcast(context.team_id, broadcast_message)
            return CommandResult(success=success, message=message)
                
        except Exception as e:
            logger.error(f"Error sending broadcast: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error sending broadcast: {str(e)}",
                error=str(e)
            )
    
    def _extract_broadcast_message(self, message: str) -> str:
        """Extract broadcast message from command."""
        match = re.search(r'/broadcast\s+(.+)', message)
        return match.group(1).strip() if match else None


# ============================================================================
# PAYMENT COMMANDS
# ============================================================================

class CreateMatchFeeCommand(Command):
    """Create match fee payment command."""
    
    def __init__(self):
        super().__init__("/create_match_fee", "Create a match fee payment", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.create_match_fee(context.team_id, context.user_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Create match fee command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class CreateMembershipFeeCommand(Command):
    """Create membership fee payment command."""
    
    def __init__(self):
        super().__init__("/create_membership_fee", "Create a membership fee payment", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.create_membership_fee(context.team_id, context.user_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Create membership fee command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class CreateFineCommand(Command):
    """Create fine payment command."""
    
    def __init__(self):
        super().__init__("/create_fine", "Create a fine payment", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.create_fine(context.team_id, context.user_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Create fine command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class PaymentStatusCommand(Command):
    """Get payment status command."""
    
    def __init__(self):
        super().__init__("/payment_status", "Get payment status", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.get_payment_status(context.team_id, context.user_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Payment status command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class PendingPaymentsCommand(Command):
    """Get pending payments command."""
    
    def __init__(self):
        super().__init__("/pending_payments", "Get pending payments", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.get_pending_payments(context.team_id, context.user_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Pending payments command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class PaymentHistoryCommand(Command):
    """Get payment history command."""
    
    def __init__(self):
        super().__init__("/payment_history", "Get payment history", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.get_payment_history(context.team_id, context.user_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Payment history command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class PaymentStatsCommand(Command):
    """Get payment statistics command."""
    
    def __init__(self):
        super().__init__("/payment_stats", "Get payment statistics", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            success, message = await command_operations.get_payment_stats(context.team_id, context.user_id)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Payment stats command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class PaymentHelpCommand(Command):
    """Payment help command."""
    
    def __init__(self):
        super().__init__("/payment_help", "Get payment commands help", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            message = await command_operations.get_payment_help()
            
            return CommandResult(
                success=True,
                message=message
            )
            
        except Exception as e:
            error_msg = log_command_error(
                error=e,
                command="/payment_help",
                team_id=context.team_id,
                user_id=context.user_id,
                chat_id=context.chat_id,
                user_message="❌ Error retrieving payment help. Please try again."
            )
            return CommandResult(
                success=False,
                message=error_msg,
                error=str(e)
            )


class FinancialDashboardCommand(Command):
    """Financial dashboard command."""

    def __init__(self):
        super().__init__("/financial_dashboard", "View your financial dashboard", PermissionLevel.PLAYER)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            success, message = await command_operations.get_financial_dashboard(context.team_id, context.user_id)
            return CommandResult(success=success, message=message)
        except Exception as e:
            error_msg = log_command_error(
                error=e,
                command="/financial_dashboard",
                team_id=context.team_id,
                user_id=context.user_id,
                chat_id=context.chat_id,
                user_message="❌ Error retrieving financial dashboard. Please try again."
            )
            return CommandResult(
                success=False,
                message=error_msg,
                error=str(e)
            )


class AnnounceCommand(Command):
    """Announce command implementation."""

    def __init__(self):
        super().__init__("/announce", "Send a team-wide announcement", PermissionLevel.LEADERSHIP)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)

            message_text = context.message_text.replace("/announce ", "", 1).strip()
            if not message_text:
                return CommandResult(success=False, message="❌ Please provide a message to announce.")

            success, message = await command_operations.send_announcement(context.team_id, message_text)
            return CommandResult(success=success, message=message)

        except Exception as e:
            error_msg = log_command_error(
                error=e,
                command="/announce",
                team_id=context.team_id,
                user_id=context.user_id,
                chat_id=context.chat_id,
                user_message="❌ Error sending announcement. Please try again."
            )
            return CommandResult(
                success=False,
                message=error_msg,
                error=str(e)
            )


class AttendCommand(Command):
    """Attend match command."""

    def __init__(self):
        super().__init__("/attend", "Confirm attendance for a match", PermissionLevel.PLAYER)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            args = context.message_text.split()[1:]
            player_id = context.user_id # Assuming telegram_id is used as player_id for attendance
            success, message = await command_operations.attend_match(context.team_id, args[0], player_id)
            return CommandResult(success=success, message=message)
        except Exception as e:
            logger.error(f"Attend command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error confirming attendance: {str(e)}",
                error=str(e)
            )


class UnattendCommand(Command):
    """Unattend match command."""

    def __init__(self):
        super().__init__("/unattend", "Cancel attendance for a match", PermissionLevel.PLAYER)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            args = context.message_text.split()[1:]
            player_id = context.user_id # Assuming telegram_id is used as player_id for attendance
            success, message = await command_operations.unattend_match(context.team_id, args[0], player_id)
            return CommandResult(success=success, message=message)
        except Exception as e:
            logger.error(f"Unattend command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error canceling attendance: {str(e)}",
                error=str(e)
            )




class InjurePlayerCommand(Command):
    """Injure player command implementation."""

    def __init__(self):
        super().__init__("/injure", "Mark a player as injured", PermissionLevel.LEADERSHIP)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            args = context.message_text.split()[1:]
            success, message = await command_operations.injure_player(context.team_id, args)
            return CommandResult(success=success, message=message)
        except Exception as e:
            logger.error(f"Injure player command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error marking player as injured: {str(e)}",
                error=str(e)
            )


class SuspendPlayerCommand(Command):
    """Suspend player command implementation."""

    def __init__(self):
        super().__init__("/suspend", "Mark a player as suspended", PermissionLevel.LEADERSHIP)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            args = context.message_text.split()[1:]
            success, message = await command_operations.suspend_player(context.team_id, args)
            return CommandResult(success=success, message=message)
        except Exception as e:
            logger.error(f"Suspend player command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error marking player as suspended: {str(e)}",
                error=str(e)
            )


class RecoverPlayerCommand(Command):
    """Recover player command implementation."""

    def __init__(self):
        super().__init__("/recover", "Mark a player as recovered", PermissionLevel.LEADERSHIP)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            args = context.message_text.split()[1:]
            success, message = await command_operations.recover_player(context.team_id, args)
            return CommandResult(success=success, message=message)
        except Exception as e:
            logger.error(f"Recover player command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error recovering player: {str(e)}",
                error=str(e)
            )

class CommandRegistry:
    """Registry for all available commands."""

    def __init__(self):
        self._commands: Dict[str, Command] = {}
        self._help_command: Optional[HelpCommand] = None
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register all default commands."""
        # Create help command first (it needs reference to registry)
        self._help_command = HelpCommand(self)
        
        # Register all commands
        commands = [
            # Utility Commands
            self._help_command,
            
            # Player Commands
            ListPlayersCommand(),
            MyInfoCommand(),
            StatusCommand(),
            RegisterCommand(),
            AddPlayerCommand(),
            RemovePlayerCommand(),
            
            # Admin Commands
            ApprovePlayerCommand(),
            RejectPlayerCommand(),
            PendingApprovalsCommand(),
            CheckFACommand(),
            DailyStatusCommand(),
            BackgroundTasksCommand(),
            RemindCommand(),
            CreateTeamCommand(),
            DeleteTeamCommand(),
            ListTeamsCommand(),
            
            # Match Commands
            CreateMatchCommand(),
            ListMatchesCommand(),
            GetMatchCommand(),
            UpdateMatchCommand(),
            DeleteMatchCommand(),
            RecordResultCommand(),
            AttendCommand(),
            UnattendCommand(),
            
            # Additional Admin Commands
            StatsCommand(),
            InviteLinkCommand(),
            BroadcastCommand(),
            InjurePlayerCommand(),
            SuspendPlayerCommand(),
            RecoverPlayerCommand(),
            AnnounceCommand(),
            
            # Payment Commands
            CreateMatchFeeCommand(),
            CreateMembershipFeeCommand(),
            CreateFineCommand(),
            PaymentStatusCommand(),
            PendingPaymentsCommand(),
            PaymentHistoryCommand(),
            PaymentStatsCommand(),
            PaymentHelpCommand(),
            FinancialDashboardCommand(),
            RefundPaymentCommand(),
            RecordExpenseCommand(),
        ]
        
        for command in commands:
            self.register_command(command)
    
    def register_command(self, command: Command):
        """Register a command."""
        self._commands[command.name] = command
        logger.info(f"Registered command: {command.name}")
    
    def get_command(self, name: str) -> Optional[Command]:
        """Get a command by name."""
        # Try exact match first
        if name in self._commands:
            return self._commands[name]
        
        # Try case-insensitive match
        for command_name, command in self._commands.items():
            if command_name.lower() == name.lower():
                return command
        
        return None
    
    def get_all_commands(self) -> List[Command]:
        """Get all registered commands."""
        return list(self._commands.values())
    
    def get_available_commands(self, context: CommandContext) -> List[Command]:
        """Get all commands available for the given context."""
        return [cmd for cmd in self._commands.values() if cmd.can_execute(context)]

# ============================================================================
# COMMAND PROCESSOR (Chain of Responsibility Pattern)
# ============================================================================

class CommandProcessor:
    """Main command processor using Chain of Responsibility pattern."""
    
    def __init__(self, command_registry: CommandRegistry):
        self.command_registry = command_registry
        self._setup_chain()
    
    def _setup_chain(self):
        """Set up the processing chain."""
        # Use the access control service directly
        self.access_control = AccessControlService()
    
    def _get_chat_type(self, chat_id: str, team_id: str) -> ChatType:
        """Determine chat type based on chat ID."""
        try:
            if self.access_control.is_leadership_chat(chat_id, team_id):
                return ChatType.LEADERSHIP
            elif self.access_control.is_main_chat(chat_id, team_id):
                return ChatType.MAIN
            else:
                # Default to main chat
                return ChatType.MAIN
        except Exception as e:
            log_error(
                error=e,
                operation="determine_chat_type",
                team_id=team_id,
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.LOW,
                user_message=None  # Internal error, no user message needed
            )
            return ChatType.MAIN  # Default to main chat
    
    async def _get_user_role(self, user_id: str, team_id: str) -> str:
        """Get user role for permission checking."""
        logger.info(f"[CommandProcessor] _get_user_role called with user_id={user_id}, team_id={team_id}")
        try:
            logger.info(f"[CommandProcessor] Getting command operations for team_id={team_id}")
            command_operations = get_command_operations(team_id=team_id)
            logger.info(f"[CommandProcessor] Command operations obtained: {type(command_operations)}")
            
            logger.info(f"[CommandProcessor] Calling command_operations.get_user_role({user_id}, {team_id})")
            role = await command_operations.get_user_role(user_id, team_id)
            logger.info(f"[CommandProcessor] get_user_role returned: {role}")
            return role
        except Exception as e:
            logger.error(f"[CommandProcessor] Error getting user role: {e}", exc_info=True)
            log_error(
                error=e,
                operation="get_user_role",
                team_id=team_id,
                user_id=user_id,
                category=ErrorCategory.AUTHORIZATION,
                severity=ErrorSeverity.MEDIUM,
                user_message=None  # Internal error, no user message needed
            )
            logger.info(f"[CommandProcessor] Returning default role 'player' due to error")
            return 'player'  # Default to player for chat-based permissions
    
    async def process_command(self, command_name: str, user_id: str, chat_id: str, 
                            team_id: str, message_text: str, username: str = None, 
                            raw_update: Any = None) -> CommandResult:
        """Process a command through the chain."""
        try:
            # Step 1: Create context
            context = CommandContext(
                user_id=user_id,
                chat_id=chat_id,
                chat_type=self._get_chat_type(chat_id, team_id),
                user_role=await self._get_user_role(user_id, team_id),
                team_id=team_id,
                message_text=message_text,
                username=username,
                raw_update=raw_update
            )
            
            # Step 2: Get command
            command = self.command_registry.get_command(command_name)
            if not command:
                return CommandResult(
                    success=False,
                    message=f"❌ Unknown command: `{command_name}`\n\nType `/help` for available commands."
                )
            
            # Step 3: Check permissions
            if not command.can_execute(context):
                return CommandResult(
                    success=False,
                    message=command.get_access_denied_message(context)
                )
            
            # Step 4: Execute command
            result = await command.execute(context)
            
            # Step 5: Log command execution
            self._log_command_execution(context, command, result)
            
            return result
            
        except Exception as e:
            error_msg = log_command_error(
                error=e,
                command=command_name,
                team_id=team_id,
                user_id=user_id,
                chat_id=chat_id,
                user_message="❌ Error executing command. Please try again."
            )
            return CommandResult(
                success=False,
                message=error_msg,
                error=str(e)
            )
    
    def _log_command_execution(self, context: CommandContext, command: Command, result: CommandResult):
        """Log command execution for monitoring."""
        logger.info(
            f"Command executed: {command.name} by {context.user_id} in {context.chat_id} "
            f"(role: {context.user_role}, chat: {context.chat_type.value}) - "
            f"Success: {result.success}"
        )


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Global command registry
_command_registry: Optional[CommandRegistry] = None
_command_processor: Optional[CommandProcessor] = None


def get_command_registry() -> CommandRegistry:
    """Get the global command registry."""
    global _command_registry
    if _command_registry is None:
        _command_registry = CommandRegistry()
    return _command_registry


def get_command_processor() -> CommandProcessor:
    """Get the global command processor."""
    global _command_processor
    if _command_processor is None:
        registry = get_command_registry()
        _command_processor = CommandProcessor(registry)
    return _command_processor


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def process_command(command_name: str, user_id: str, chat_id: str, 
                         team_id: str, message_text: str, username: str = None, 
                         raw_update: Any = None) -> CommandResult:
    """Convenience function to process a command."""
    processor = get_command_processor()
    return await processor.process_command(
        command_name, user_id, chat_id, team_id, message_text, username, raw_update
    )


def is_slash_command(message: str) -> bool:
    """Check if message is a slash command."""
    return message.startswith('/')


def extract_command_name(message: str) -> Optional[str]:
    """Extract command name from message."""
    if not is_slash_command(message):
        return None
    
    # Split by space and take first part
    parts = message.split()
    if not parts:
        return None
    
    # Return the command name as-is (with slash, case-preserved)
    return parts[0] 


class RefundPaymentCommand(Command):
    """Refund payment command."""
    
    def __init__(self):
        super().__init__("/refund_payment", "Refund a payment", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.refund_payment(context.team_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            error_msg = log_command_error(
                error=e,
                command="/refund_payment",
                team_id=context.team_id,
                user_id=context.user_id,
                chat_id=context.chat_id,
                user_message="❌ Error processing refund. Please try again."
            )
            return CommandResult(
                success=False,
                message=error_msg,
                error=str(e)
            )


class RecordExpenseCommand(Command):
    """Record expense command."""
    
    def __init__(self):
        super().__init__("/record_expense", "Record a team expense", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            command_operations = get_command_operations(team_id=context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            success, message = await command_operations.record_expense(context.team_id, args)
            
            return CommandResult(
                success=success,
                message=message
            )
            
        except Exception as e:
            error_msg = log_command_error(
                error=e,
                command="/record_expense",
                team_id=context.team_id,
                user_id=context.user_id,
                chat_id=context.chat_id,
                user_message="❌ Error recording expense. Please try again."
            )
            return CommandResult(
                success=False,
                message=error_msg,
                error=str(e)
            )


