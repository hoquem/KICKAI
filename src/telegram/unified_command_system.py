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

from .payment_commands import PaymentCommands
from .match_commands import MatchCommands
from .player_commands import PlayerCommands

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
        return context.user_role in ['player', 'admin', 'captain', 'secretary', 'manager', 'treasurer']
    
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

class StartCommand(Command):
    """Start command implementation."""
    
    def __init__(self):
        super().__init__("/start", "Start the bot", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            message = f"""🤖 WELCOME TO KICKAI BOT!

👋 Hello! I'm your AI-powered football team management assistant.

💡 WHAT I CAN HELP YOU WITH:
• Player registration and management
• Match scheduling and coordination
• Team statistics and analytics
• Communication and notifications

📋 QUICK START:
• Type /help to see all available commands
• Use natural language: "Create a match against Arsenal on July 1st"
• Ask questions: "What's our next match?"

🔗 TEAM: {context.team_id}

Ready to get started! 🏆"""
            
            return CommandResult(success=True, message=message)
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            return CommandResult(success=False, message="❌ Error starting bot", error=str(e))


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
            # Import here to avoid circular imports
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            # Pass the chat type information to determine if this is leadership chat
            is_leadership_chat = context.chat_type == ChatType.LEADERSHIP
            result = await handler._handle_list_players(is_leadership_chat=is_leadership_chat)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in list players command: {e}")
            return CommandResult(success=False, message="❌ Error listing players", error=str(e))


class MyInfoCommand(Command):
    """MyInfo command implementation."""
    
    def __init__(self):
        super().__init__("/myinfo", "Get your player information", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            logger.info(f"MyInfoCommand: Processing for user {context.user_id} in team {context.team_id}")
            
            # Import here to avoid circular imports
            from src.telegram.player_registration_handler import PlayerRegistrationHandler
            from src.services.player_service import get_player_service
            from src.services.team_service import get_team_service
            
            player_service = get_player_service()
            team_service = get_team_service()
            player_handler = PlayerRegistrationHandler(context.team_id, player_service, team_service)
            
            logger.info(f"MyInfoCommand: Player handler created, calling get_player_info for user {context.user_id}")
            
            # Get player info by telegram user ID
            success, message = await player_handler.get_player_info(context.user_id)
            
            logger.info(f"MyInfoCommand: get_player_info returned success={success}, message_length={len(message) if message else 0}")
            
            if success:
                return CommandResult(success=True, message=message)
            else:
                logger.warning(f"MyInfoCommand: Failed to get player info for user {context.user_id}: {message}")
                return CommandResult(success=False, message=message)
                
        except Exception as e:
            logger.error(f"Error in MyInfoCommand for user {context.user_id}: {e}")
            return CommandResult(success=False, message=f"❌ Error getting player info: {str(e)}")


class StatusCommand(Command):
    """Status command implementation."""
    
    def __init__(self):
        super().__init__("/status", "Check player status (your own or by phone)", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Import here to avoid circular imports
            from src.telegram.player_registration_handler import PlayerRegistrationHandler
            from src.services.player_service import get_player_service
            from src.services.team_service import get_team_service
            
            player_service = get_player_service()
            team_service = get_team_service()
            player_handler = PlayerRegistrationHandler(context.team_id, player_service, team_service)
            
            # Parse command to see if phone number is provided
            parts = context.message_text.split()
            
            # If no phone provided, check the user's own status
            if len(parts) < 2:
                success, message = await player_handler.get_player_info(context.user_id)
                if success:
                    return CommandResult(success=True, message=f"📊 <b>Your Status</b>\n\n{message}")
                else:
                    return CommandResult(success=False, message="❌ Player not found. Please contact team admin.")
            
            # If phone provided, check that specific player's status (admin function)
            phone = parts[1]
            
            # Check if user has permission to check other players (admin/leadership)
            if context.chat_type != ChatType.LEADERSHIP:
                return CommandResult(
                    success=False, 
                    message="❌ Checking other players' status is only available in the leadership chat."
                )
            
            player = await player_handler.get_player_by_phone(phone)
            
            if not player:
                return CommandResult(success=False, message=f"❌ Player with phone {phone} not found")
            
            # Format player status for admin view
            from src.telegram.player_registration_handler import format_player_name
            
            status_message = f"""📊 <b>Player Status: {format_player_name(player.name)}</b>

📋 <b>Basic Info:</b>
• Name: {format_player_name(player.name)}
• Player ID: {player.player_id.upper()}
• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
• Phone: {player.phone}

📊 <b>Status:</b>
• Onboarding: {player.onboarding_status.value.title()}
• FA Registered: {'Yes' if player.is_fa_registered() else 'No'}
• FA Eligible: {'Yes' if player.is_fa_eligible() else 'No'}
• Match Eligible: {'Yes' if player.is_match_eligible() else 'No'}

📞 <b>Contact Info:</b>
• Emergency Contact: {player.emergency_contact or 'Not provided'}
• Date of Birth: {player.date_of_birth or 'Not provided'}
• Telegram: @{player.telegram_username or 'Not linked'}

📅 <b>Timestamps:</b>
• Created: {player.created_at.strftime('%Y-%m-%d %H:%M') if player.created_at else 'Unknown'}
• Last Updated: {player.updated_at.strftime('%Y-%m-%d %H:%M') if player.updated_at else 'Unknown'}"""
            
            return CommandResult(success=True, message=status_message)
                
        except Exception as e:
            logger.error(f"Error in StatusCommand: {e}")
            return CommandResult(success=False, message=f"❌ Error checking status: {str(e)}")


class RegisterCommand(Command):
    """Register command implementation."""
    
    def __init__(self):
        super().__init__("/register", "Register as a new player", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Check if there's a player ID parameter
            parts = context.message_text.split()
            
            # If no parameters, show registration info based on chat context
            if len(parts) == 1:
                if context.chat_type == ChatType.LEADERSHIP:
                    # Leadership chat - show admin instructions
                    message = """📝 PLAYER REGISTRATION (ADMIN)

To add a new player to the team:

1️⃣ ADD PLAYER:
   /add [name] [phone] [position]
   Example: /add John Smith 07123456789 midfielder

2️⃣ GENERATE INVITATION:
   /invite [phone_or_player_id]
   Example: /invite 07123456789

3️⃣ SEND INVITATION:
   Copy the generated message and send to the player

4️⃣ PLAYER COMPLETES ONBOARDING:
   Player uses the invitation link and completes profile

5️⃣ APPROVE PLAYER:
   /approve [player_id]
   Example: /approve JS1

💡 TIPS:
• Use /list to see all players
• Use /pending to see players awaiting approval
• Use /status [phone] to check player status"""
                else:
                    # Main chat or private - show player instructions
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
            
            # If there's a player ID parameter, handle player onboarding
            if len(parts) > 1:
                player_id = parts[1]
                
                # Import here to avoid circular imports
                from src.telegram.player_registration_handler import PlayerRegistrationHandler
                from src.services.player_service import get_player_service
                from src.services.team_service import get_team_service
                
                player_service = get_player_service()
                team_service = get_team_service()
                player_handler = PlayerRegistrationHandler(context.team_id, player_service, team_service)
                
                # Handle player join via invite
                success, message = await player_handler.player_joined_via_invite(player_id, context.user_id)
                
                if success:
                    # Get onboarding message for the player
                    onboarding_success, onboarding_message = await player_handler.get_onboarding_message(player_id)
                    if onboarding_success:
                        full_message = f"{message}\n\n{onboarding_message}"
                        return CommandResult(success=True, message=full_message)
                    else:
                        error_message = f"{message}\n\n❌ Error getting onboarding message: {onboarding_message}"
                        return CommandResult(success=False, message=error_message)
                else:
                    error_message = f"❌ {message}\n\n💡 Please contact the team admin if you believe this is an error."
                    return CommandResult(success=False, message=error_message)
            
            return CommandResult(success=False, message="❌ Invalid register command format. Use `/register` or `/register player_id`")
            
        except Exception as e:
            logger.error(f"Error in register command: {e}")
            return CommandResult(
                success=False,
                message="❌ Error processing registration request."
            )


class AddPlayerCommand(Command):
    """Add player command implementation."""
    
    def __init__(self):
        super().__init__("/add", "Add a new player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_add_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in add player command: {e}")
            return CommandResult(success=False, message="❌ Error adding player", error=str(e))


class RemovePlayerCommand(Command):
    """Remove player command implementation."""
    
    def __init__(self):
        super().__init__("/remove", "Remove a player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_remove_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in remove player command: {e}")
            return CommandResult(success=False, message="❌ Error removing player", error=str(e))


class ApprovePlayerCommand(Command):
    """Approve player command implementation."""
    
    def __init__(self):
        super().__init__("/approve", "Approve a player registration", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_approve_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result or "Command executed successfully")
        except Exception as e:
            logger.error(f"Error in approve player command: {e}")
            return CommandResult(success=False, message="❌ Error approving player", error=str(e))


class RejectPlayerCommand(Command):
    """Reject player command implementation."""
    
    def __init__(self):
        super().__init__("/reject", "Reject a player registration", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_reject_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in reject player command: {e}")
            return CommandResult(success=False, message="❌ Error rejecting player", error=str(e))


class PendingApprovalsCommand(Command):
    """Pending approvals command implementation."""
    
    def __init__(self):
        super().__init__("/pending", "List players pending approval", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_pending_approvals()
            return CommandResult(success=True, message=result or "No pending approvals")
        except Exception as e:
            logger.error(f"Error in pending approvals command: {e}")
            return CommandResult(success=False, message="❌ Error listing pending approvals", error=str(e))


class CheckFACommand(Command):
    """Check FA registration command implementation."""
    
    def __init__(self):
        super().__init__("/checkfa", "Check FA registration status", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_check_fa_registration()
            return CommandResult(success=True, message=result or "FA check completed")
        except Exception as e:
            logger.error(f"Error in check FA command: {e}")
            return CommandResult(success=False, message="❌ Error checking FA registration", error=str(e))


class DailyStatusCommand(Command):
    """Daily status command implementation."""
    
    def __init__(self):
        super().__init__("/dailystatus", "Generate daily team status report", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_daily_status()
            return CommandResult(success=True, message=result or "Daily status generated")
        except Exception as e:
            logger.error(f"Error in daily status command: {e}")
            return CommandResult(success=False, message="❌ Error generating daily status", error=str(e))


class BackgroundTasksCommand(Command):
    """Background tasks status command implementation."""
    
    def __init__(self):
        super().__init__("/background", "Check background tasks status", PermissionLevel.ADMIN)
    
    def get_help_text(self) -> str:
        return "`/background` - Check background tasks status"
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.services.background_tasks import get_background_task_status
            
            # Get background task status
            status = await get_background_task_status()
            
            # Build status message
            message = "📊 BACKGROUND TASKS STATUS\n\n"
            
            if status["running"]:
                message += "🟢 System Status: Running\n\n"
            else:
                message += "🔴 System Status: Stopped\n\n"
            
            message += f"📋 Task Summary:\n"
            message += f"• Total Tasks: {status['total_tasks']}\n"
            message += f"• Active Tasks: {status['active_tasks']}\n"
            message += f"• Completed Tasks: {status['completed_tasks']}\n"
            message += f"• Failed Tasks: {status['failed_tasks']}\n\n"
            
            if status["task_details"]:
                message += "🔍 Task Details:\n"
                for i, task in enumerate(status["task_details"]):
                    if task["done"]:
                        if task["exception"]:
                            message += f"• Task {i}: ❌ Failed - {task['exception']}\n"
                        else:
                            message += f"• Task {i}: ✅ Completed\n"
                    elif task["cancelled"]:
                        message += f"• Task {i}: ⏹️ Cancelled\n"
                    else:
                        message += f"• Task {i}: 🔄 Running\n"
            else:
                message += "ℹ️ No tasks currently running\n\n"
            
            message += "\n💡 Background Services:\n"
            message += "• FA Registration Checker (24h interval)\n"
            message += "• Daily Status Service (daily)\n"
            message += "• Onboarding Reminder Service (6h interval)\n"
            message += "• Reminder Cleanup Service (24h interval)\n"
            
            return CommandResult(success=True, message=message)
            
        except Exception as e:
            logger.error(f"Error in background tasks command: {e}")
            return CommandResult(
                success=False, 
                message=f"❌ Error checking background tasks: {str(e)}", 
                error=str(e)
            )


class RemindCommand(Command):
    """Remind player command implementation."""
    
    def __init__(self):
        super().__init__("/remind", "Send reminder to player", PermissionLevel.ADMIN)
    
    def get_help_text(self) -> str:
        return "`/remind [player_id]` - Send reminder to player"
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the remind command."""
        try:
            from src.services.reminder_service import get_reminder_service
            
            message = context.message_text
            parts = message.split()
            
            if len(parts) < 2:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a player ID.\n\nUsage: `/remind [player_id]`\nExample: `/remind AB1`",
                    error="Missing player ID"
                )
            
            player_id = parts[1].upper()
            
            # Get reminder service
            reminder_service = get_reminder_service(context.team_id)
            
            # Send manual reminder
            success, response = await reminder_service.send_manual_reminder(player_id, context.user_id)
            
            if success:
                return CommandResult(success=True, message=response)
            else:
                return CommandResult(success=False, message=response, error="Reminder failed")
                
        except Exception as e:
            logger.error(f"Error in remind command: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error sending reminder: {str(e)}",
                error=str(e)
            )


# ============================================================================
# MATCH COMMANDS
# ============================================================================

class CreateMatchCommand(Command):
    """Command to create a new match/fixture."""

    def __init__(self):
        super().__init__("/newmatch", "Create a new match/fixture", PermissionLevel.LEADERSHIP)

class CreateTeamCommand(Command):
    """Command to create a new team."""

    def __init__(self):
        super().__init__("/create_team", "Create a new team", PermissionLevel.ADMIN)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.services.team_service import get_team_service
            team_service = get_team_service()

            parts = context.message_text.split(maxsplit=2)
            if len(parts) < 2:
                return CommandResult(
                    success=False,
                    message="❌ Usage: /create_team <team_name> [description]",
                    error="Missing team name"
                )

            team_name = parts[1]
            description = parts[2] if len(parts) > 2 else None

            team = await team_service.create_team(name=team_name, description=description)
            return CommandResult(success=True, message=f"✅ Team '{team.name}' (ID: {team.id}) created successfully!")
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            return CommandResult(success=False, message=f"❌ Error creating team: {str(e)}", error=str(e))


class DeleteTeamCommand(Command):
    """Command to delete a team."""

    def __init__(self):
        super().__init__("/delete_team", "Delete a team", PermissionLevel.ADMIN)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.services.team_service import get_team_service
            team_service = get_team_service()

            parts = context.message_text.split()
            if len(parts) < 2:
                return CommandResult(
                    success=False,
                    message="❌ Usage: /delete_team <team_id>",
                    error="Missing team ID"
                )

            team_id = parts[1]
            success = await team_service.delete_team(team_id)
            if success:
                return CommandResult(success=True, message=f"✅ Team {team_id} deleted successfully!")
            else:
                return CommandResult(success=False, message=f"❌ Failed to delete team {team_id}. Team not found or an error occurred.")
        except Exception as e:
            logger.error(f"Error deleting team: {e}")
            return CommandResult(success=False, message=f"❌ Error deleting team: {str(e)}", error=str(e))


class ListTeamsCommand(Command):
    """Command to list all teams."""

    def __init__(self):
        super().__init__("/list_teams", "List all teams", PermissionLevel.ADMIN)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.services.team_service import get_team_service
            team_service = get_team_service()

            teams = await team_service.get_all_teams()
            if not teams:
                return CommandResult(success=True, message="ℹ️ No teams found.")

            message = "📋 **All Teams:**\n\n"
            for team in teams:
                message += f"• Name: {team.name} (ID: {team.id}) - Status: {team.status.value.title()}\n"
            return CommandResult(success=True, message=message)
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
            from src.tools.firebase_tools import FixtureTools
            import re
            
            fixture_tool = FixtureTools(context.team_id)
            
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
            result = fixture_tool._run('add_fixture', 
                                      opponent=opponent,
                                      match_date=date,
                                      kickoff_time=time,
                                      venue=venue,
                                      competition=competition)
            
            if "successfully" in result.lower() or "added" in result.lower():
                return CommandResult(
                    success=True,
                    message=f"✅ Match Created Successfully!\n\n🏆 {opponent}\n📅 {date} at {time}\n📍 {venue} - {competition}"
                )
            else:
                return CommandResult(
                    success=False,
                    message=f"❌ Failed to create match: {result}",
                    error=result
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
            from src.tools.firebase_tools import FixtureTools
            
            fixture_tool = FixtureTools(context.team_id)
            result = fixture_tool._run('get_all_fixtures')
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
            from src.tools.firebase_tools import FixtureTools
            import re
            
            fixture_tool = FixtureTools(context.team_id)
            message = context.message_text
            match_id = self._extract_match_id(message)
            
            if not match_id:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a match ID.\n\nExample: `/getmatch MATCH123`",
                    error="Missing match ID"
                )
            
            result = fixture_tool._run('get_fixture', fixture_id=match_id)
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
            from src.tools.firebase_tools import FixtureTools
            import re
            
            fixture_tool = FixtureTools(context.team_id)
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
            
            result = fixture_tool._run('update_fixture', fixture_id=match_id, **updates)
            return CommandResult(success=True, message=result)
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
            from src.tools.firebase_tools import FixtureTools
            import re
            
            fixture_tool = FixtureTools(context.team_id)
            message = context.message_text
            match_id = self._extract_match_id(message)
            
            if not match_id:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a match ID.\n\nExample: `/deletematch MATCH123`",
                    error="Missing match ID"
                )
            
            result = fixture_tool._run('delete_fixture', fixture_id=match_id)
            return CommandResult(success=True, message=result)
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
            match_commands = MatchCommands(context.team_id)
            args = context.message_text.split()[1:]
            result = await match_commands.handle_record_result(args)
            return CommandResult(success=not result.startswith("❌"), message=result)
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
            from src.services.player_service import PlayerService
            
            player_service = PlayerService(context.team_id)
            players = await player_service.get_team_players()
            
            if not players:
                return CommandResult(
                    success=True,
                    message="📊 TEAM STATISTICS\n\nNo players found in the team."
                )
            
            # Calculate statistics
            total_players = len(players)
            active_players = len([p for p in players if p.get('status') == 'active'])
            pending_players = len([p for p in players if p.get('status') == 'pending'])
            fa_registered = len([p for p in players if p.get('fa_registration')])
            
            # Position breakdown
            positions = {}
            for player in players:
                pos = player.get('position', 'Unknown')
                positions[pos] = positions.get(pos, 0) + 1
            
            # Format statistics
            stats = f"📊 TEAM STATISTICS\n\n"
            stats += f"👥 Total Players: {total_players}\n"
            stats += f"✅ Active Players: {active_players}\n"
            stats += f"⏳ Pending Approvals: {pending_players}\n"
            stats += f"🏆 FA Registered: {fa_registered}\n\n"
            
            stats += "Position Breakdown:\n"
            for pos, count in positions.items():
                stats += f"⚽ {pos}: {count}\n"
            
            return CommandResult(
                success=True,
                message=stats
            )
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error getting stats: {str(e)}",
                error=str(e)
            )


class InviteCommand(Command):
    """Command to invite a player to the team."""
    
    def __init__(self):
        super().__init__("/invite", "Invite a player to the team", PermissionLevel.LEADERSHIP)
    
    def get_help_text(self) -> str:
        return "`/invite [phone_or_player_id]` - Generate invitation message"
    
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the invite command."""
        try:
            import random
            import string
            from src.services.player_service import get_player_service
            
            message = context.message_text
            identifier = self._extract_identifier(message)
            
            if not identifier:
                return CommandResult(
                    success=False,
                    message="❌ Please provide phone number or player ID.\n\nExamples:\n• `/invite 07123456789`\n• `/invite AB1`",
                    error="Missing identifier"
                )
            
            # Check if identifier is a phone number or player ID
            phone = None
            player_name = None
            
            if self._is_phone_number(identifier):
                # It's a phone number
                phone = identifier
            else:
                # It's a player ID, find the player
                player_service = get_player_service()
                players = await player_service.get_team_players(context.team_id)
                
                for player in players:
                    if player.player_id and player.player_id.upper() == identifier.upper():
                        phone = player.phone
                        player_name = player.name
                        break
                
                if not phone:
                    return CommandResult(
                        success=False,
                        message=f"❌ Player with ID {identifier} not found.\n\nUse `/list` to see available players.",
                        error="Player not found"
                    )
            
            # Get team information and Telegram group link
            from src.services.team_service import get_team_service
            from src.telegram.player_registration_handler import PlayerRegistrationHandler
            
            team_service = get_team_service()
            team = await team_service.get_team(context.team_id)
            team_name = team.name if team else 'Our Team'
            
            # Get Telegram group link
            try:
                from src.core.bot_config_manager import get_bot_config_manager
                import httpx
                
                # Get bot configuration for this team
                manager = get_bot_config_manager()
                bot_config = manager.get_bot_config(context.team_id)
                if not bot_config or not bot_config.token or not bot_config.main_chat_id:
                    telegram_link = "https://t.me/+[TEAM_GROUP_LINK]"
                else:
                    # Generate real invite link using Telegram Bot API
                    url = f"https://api.telegram.org/bot{bot_config.token}/createChatInviteLink"
                    payload = {
                        "chat_id": bot_config.main_chat_id,
                        "name": f"{team_name} Team Invite",
                        "creates_join_request": False,
                        "expire_date": None,
                        "member_limit": None
                    }
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(url, json=payload, timeout=10)
                        data = response.json()
                        
                        if data.get("ok") and data.get("result"):
                            telegram_link = data["result"]["invite_link"]
                            logging.info(f"Generated Telegram invite link for {team_name}: {telegram_link}")
                        else:
                            error_msg = f"Failed to create invite link: {data.get('description', 'Unknown error')}"
                            logging.warning(error_msg)
                            telegram_link = "https://t.me/+[TEAM_GROUP_LINK]"
                            
            except Exception as e:
                logging.error(f"Error generating Telegram invite link: {e}")
                telegram_link = "https://t.me/+[TEAM_GROUP_LINK]"
            
            # Create a short, shareable version for WhatsApp/SMS/Email (plain text with minimal formatting)
            if player_name:
                short_message = f"""🎉 Welcome to {team_name}, {player_name.upper()}!

You've been invited to join our team!

📋 Your Details:
• Name: {player_name.upper()}
• Player ID: {identifier.upper()}

🔗 Join our team chat:
{telegram_link}

📱 Next Steps:
1. Click the link above to join our team group
2. Once you join, type: /start {identifier.upper()}
3. Complete your onboarding process

Welcome aboard! ⚽🏆

- {team_name} Management"""
            else:
                short_message = f"""🎉 Welcome to {team_name}!

You've been invited to join our team!

📱 Phone: {phone}

🔗 Join our team chat:
{telegram_link}

📱 Next Steps:
1. Click the link above to join our team group
2. Complete your onboarding process

Welcome aboard! ⚽🏆

- {team_name} Management"""
            
            # Create response message (plain text with minimal formatting)
            if player_name:
                response_message = f"""✅ Invitation Generated!

👤 Player: {player_name.upper()}
🆔 Player ID: {identifier.upper()}
📱 Phone: {phone}

📋 Copy & Send This Message:

{short_message}

💡 Instructions:
• Copy the message above
• Send via WhatsApp, SMS, or Email
• Player clicks the link to join Telegram group
• Once joined, they type: /start {identifier.upper()}"""
            else:
                response_message = f"""✅ Invitation Generated!

📱 Phone: {phone}

📋 Copy & Send This Message:

{short_message}

💡 Instructions:
• Copy the message above
• Send via WhatsApp, SMS, or Email
• Player clicks the link to join Telegram group
• Once joined, they complete onboarding"""
            
            return CommandResult(
                success=True,
                message=response_message
            )
                
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
        phone_match = re.search(r'/invite\s+(\d{11})', message)
        if phone_match:
            return phone_match.group(1)
        
        # Try to match player ID (letters and numbers, typically 2-4 characters)
        player_id_match = re.search(r'/invite\s+([A-Za-z0-9]{2,4})', message)
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
            from src.services.team_member_service import TeamMemberService
            
            message = context.message_text
            broadcast_message = self._extract_broadcast_message(message)
            
            if not broadcast_message:
                return CommandResult(
                    success=False,
                    message="❌ Please provide a message to broadcast.\n\nExample: `/broadcast Training cancelled tomorrow`",
                    error="Missing broadcast message"
                )
            
            # Get all team members
            team_service = TeamMemberService(context.team_id)
            members = await team_service.get_all_members()
            
            if not members:
                return CommandResult(
                    success=False,
                    message="❌ No team members found to broadcast to.",
                    error="No team members"
                )
            
            return CommandResult(
                success=True,
                message=f"✅ Broadcast Sent!\n\n📢 Message: {broadcast_message}\n👥 Recipients: {len(members)} team members"
            )
                
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
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_payment_command("create_match_fee", args, context.user_id)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
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
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_payment_command("create_membership_fee", args, context.user_id)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
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
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_payment_command("create_fine", args, context.user_id)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
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
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_payment_command("payment_status", args, context.user_id)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
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
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_payment_command("pending_payments", args, context.user_id)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
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
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_payment_command("payment_history", args, context.user_id)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
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
            payment_commands = PaymentCommands(context.team_id)
            
            result = await payment_commands.handle_payment_command("payment_stats", [], context.user_id)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
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
            payment_commands = PaymentCommands(context.team_id)
            
            help_message = payment_commands.get_help_message()
            
            return CommandResult(
                success=True,
                message=help_message
            )
            
        except Exception as e:
            logger.error(f"Payment help command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error: {str(e)}",
                error=str(e)
            )


class FinancialDashboardCommand(Command):
    """Financial dashboard command."""

    def __init__(self):
        super().__init__("/financial_dashboard", "View your financial dashboard", PermissionLevel.PLAYER)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            payment_commands = PaymentCommands(context.team_id)
            dashboard_message = await payment_commands.get_financial_dashboard(context.user_id)
            return CommandResult(success=True, message=dashboard_message)
        except Exception as e:
            logger.error(f"Financial dashboard command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error retrieving financial dashboard: {str(e)}",
                error=str(e)
            )


class AnnounceCommand(Command):
    """Announce command implementation."""

    def __init__(self):
        super().__init__("/announce", "Send a team-wide announcement", PermissionLevel.LEADERSHIP)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.services.team_member_service import get_team_member_service
            from src.core.bot_config_manager import get_bot_config_manager
            import httpx

            message_text = context.message_text.replace("/announce ", "", 1).strip()
            if not message_text:
                return CommandResult(success=False, message="❌ Please provide a message to announce.")

            team_member_service = get_team_member_service()
            all_members = await team_member_service.get_all_members_in_team(context.team_id)

            bot_config = get_bot_config_manager().get_bot_config(context.team_id)
            if not bot_config or not bot_config.token:
                return CommandResult(success=False, message="❌ Bot not configured for this team.")

            success_count = 0
            failed_count = 0
            for member in all_members:
                if member.telegram_id:
                    try:
                        url = f"https://api.telegram.org/bot{bot_config.token}/sendMessage"
                        payload = {
                            "chat_id": member.telegram_id,
                            "text": f"📢 **Team Announcement:**\n\n{message_text}",
                            "parse_mode": "Markdown"
                        }
                        async with httpx.AsyncClient() as client:
                            response = await client.post(url, json=payload, timeout=10)
                            if response.status_code == 200:
                                success_count += 1
                            else:
                                logger.warning(f"Failed to send announcement to {member.telegram_id}: {response.text}")
                                failed_count += 1
                    except Exception as e:
                        logger.error(f"Error sending announcement to {member.telegram_id}: {e}")
                        failed_count += 1

            return CommandResult(success=True, message=f"✅ Announcement sent to {success_count} members. Failed for {failed_count} members.")
        except Exception as e:
            logger.error(f"Error in announce command: {e}")
            return CommandResult(success=False, message=f"❌ Error sending announcement: {str(e)}", error=str(e))


class AttendCommand(Command):
    """Attend match command."""

    def __init__(self):
        super().__init__("/attend", "Confirm attendance for a match", PermissionLevel.PLAYER)

    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            match_commands = MatchCommands(context.team_id)
            args = context.message_text.split()[1:]
            player_id = context.user_id # Assuming telegram_id is used as player_id for attendance
            result = await match_commands.handle_attend_match(args[0], player_id)
            return CommandResult(success=not result.startswith("❌"), message=result)
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
            match_commands = MatchCommands(context.team_id)
            args = context.message_text.split()[1:]
            player_id = context.user_id # Assuming telegram_id is used as player_id for attendance
            result = await match_commands.handle_unattend_match(args[0], player_id)
            return CommandResult(success=not result.startswith("❌"), message=result)
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
            player_commands = PlayerCommands(context.team_id)
            args = context.message_text.split()[1:]
            result = await player_commands.handle_injure_player(args)
            return CommandResult(success=not result.startswith("❌"), message=result)
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
            player_commands = PlayerCommands(context.team_id)
            args = context.message_text.split()[1:]
            result = await player_commands.handle_suspend_player(args)
            return CommandResult(success=not result.startswith("❌"), message=result)
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
            player_commands = PlayerCommands(context.team_id)
            args = context.message_text.split()[1:]
            result = await player_commands.handle_recover_player(args)
            return CommandResult(success=not result.startswith("❌"), message=result)
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
            StartCommand(),
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
            InviteCommand(),
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
        return self._commands.get(name)
    
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
        # Import here to avoid circular imports
        from src.services.access_control_service import AccessControlService
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
            logger.error(f"Error determining chat type: {e}")
            return ChatType.MAIN  # Default to main chat
    
    async def _get_user_role(self, user_id: str, team_id: str) -> str:
        """Get user role for permission checking."""
        try:
            from src.services.team_member_service import TeamMemberService
            from src.database.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
            team_service = TeamMemberService(firebase_client)
            member = await team_service.get_team_member_by_telegram_id(user_id, team_id)
            if member and member.roles:
                return member.roles[0]  # Return first role
            return 'player'
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return 'player'  # Default to player
    
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
            logger.error(f"Error processing command {command_name}: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error executing command: {str(e)}",
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
    
    return parts[0].lower() 


class RefundPaymentCommand(Command):
    """Refund payment command."""
    
    def __init__(self):
        super().__init__("/refund_payment", "Refund a payment", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_refund_payment(args)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
            )
            
        except Exception as e:
            logger.error(f"Refund payment command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


class RecordExpenseCommand(Command):
    """Record expense command."""
    
    def __init__(self):
        super().__init__("/record_expense", "Record a team expense", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            payment_commands = PaymentCommands(context.team_id)
            
            # Extract command arguments
            args = context.message_text.split()[1:]  # Remove command name
            
            result = await payment_commands.handle_record_expense(args)
            
            return CommandResult(
                success=not result.startswith("❌"),
                message=result
            )
            
        except Exception as e:
            logger.error(f"Record expense command error: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Payment Error: {str(e)}",
                error=str(e)
            )


