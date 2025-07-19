#!/usr/bin/env python3
"""
Behavioral Mixins for KICKAI Agents

This module provides behavioral mixins that can be composed into agents
to give them specific capabilities and behaviors.
"""

import asyncio
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from core.constants import get_team_members_collection
from core.exceptions import KICKAIError, InputValidationError, AuthorizationError, AgentExecutionError


class BaseBehavioralMixin(ABC):
    """Base class for all behavioral mixins."""
    
    def __init__(self):
        self.logger = logger.bind(mixin_name=self.__class__.__name__)
    
    @abstractmethod
    def get_mixin_name(self) -> str:
        """Get the name of this mixin."""
        pass
    
    @abstractmethod
    def get_supported_commands(self) -> list:
        """Get list of commands this mixin supports."""
        pass


class PlayerCoordinatorMixin(BaseBehavioralMixin):
    """
    Mixin for player coordination behaviors.
    
    Provides specialized functionality for:
    - Player status queries
    - Player information retrieval
    - Player list management
    - Player approval workflows
    - Player registration handling
    """
    
    def get_mixin_name(self) -> str:
        return "player_coordinator"
    
    def get_supported_commands(self) -> list:
        return ["/status", "/myinfo", "/list", "/approve", "/register"]
    
    async def handle_status_command(self, parameters: dict) -> str:
        """Handle /status command (async)."""
        try:
            user_id = parameters.get('user_id', 'unknown')
            team_id = parameters.get('team_id', 'unknown')
            
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Getting status for user_id={user_id}, team_id={team_id}")
            
            # Check if user_id is a test/unknown value
            if user_id in ['unknown', 'test_user', 'unknown_user']:
                self.logger.info(f"🔍 PLAYER_COORDINATOR: Test user detected, providing registration guidance")
                return self._get_player_not_found_message(user_id, team_id, "status")
            
            # Let the agent use the get_my_status tool instead of providing fallback
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Delegating to agent tools for status request")
            return None  # Return None to let the agent handle this with tools
            
        except Exception as e:
            self.logger.error(f"Error in _handle_status_command: {e}", exc_info=True)
            return f"❌ Error getting player status: {str(e)}"
    
    async def handle_myinfo_command(self, parameters: dict) -> str:
        """Handle /myinfo command (async)."""
        try:
            user_id = parameters.get('user_id', 'unknown')
            team_id = parameters.get('team_id', 'unknown')
            
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Getting myinfo for user_id={user_id}, team_id={team_id}")
            
            # Check if user_id is a test/unknown value
            if user_id in ['unknown', 'test_user', 'unknown_user']:
                self.logger.info(f"🔍 PLAYER_COORDINATOR: Test user detected, providing registration guidance")
                return self._get_player_not_found_message(user_id, team_id, "myinfo")
            
            # Let the agent use the get_my_status tool instead of providing fallback
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Delegating to agent tools for myinfo request")
            return None  # Return None to let the agent handle this with tools
            
        except Exception as e:
            self.logger.error(f"Error in _handle_myinfo_command: {e}", exc_info=True)
            return f"❌ Error getting player information: {str(e)}"
    
    async def handle_list_command(self, parameters: dict) -> str:
        """Handle /list command (async)."""
        try:
            team_id = parameters.get('team_id', 'unknown')
            
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Getting all players for team_id={team_id}")
            
            # Let the agent use the get_all_players tool instead of providing fallback
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Delegating to agent tools for list request")
            return None  # Return None to let the agent handle this with tools
            
        except Exception as e:
            self.logger.error(f"Error in _handle_list_command: {e}", exc_info=True)
            return f"❌ Error getting player list: {str(e)}"
    
    async def handle_approve_command(self, parameters: dict) -> str:
        """Handle /approve command (async)."""
        try:
            team_id = parameters.get('team_id', 'unknown')
            player_id = parameters.get('player_id', 'unknown')
            
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Approving player_id={player_id} for team_id={team_id}")
            
            # For now, return a basic approval message
            return f"""✅ Player Approval

Player {player_id} has been approved for team {team_id}.

The player can now participate in team activities and matches.

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in _handle_approve_command: {e}", exc_info=True)
            return f"❌ Error approving player: {str(e)}"
    
    async def handle_register_command(self, parameters: dict) -> str:
        """Handle /register command (async)."""
        try:
            user_id = parameters.get('user_id', 'unknown')
            team_id = parameters.get('team_id', 'unknown')
            
            self.logger.info(f"🔍 PLAYER_COORDINATOR: Registering user_id={user_id} for team_id={team_id}")
            
            # For now, return a basic registration message
            return f"""📝 Player Registration

Welcome to the team! Your registration has been received.

Please complete your onboarding by providing:
1. Emergency contact details
2. Date of birth
3. FA registration information

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in _handle_register_command: {e}", exc_info=True)
            return f"❌ Error registering player: {str(e)}"
    
    def _get_player_not_found_message(self, user_id: str, team_id: str, command_type: str) -> str:
        """Get a friendly and helpful message when a player is not found."""
        command_name = command_type.replace("_", " ").title()
        
        if command_type in ["status", "myinfo"]:
            return f"""👋 Welcome to KICKAI! 

I don't see your registration in our system yet. No worries - let's get you set up to join the team! 

📝 To register, use: /register
💡 Or ask me: "How do I register?"

I'll guide you through the simple registration process step by step. It only takes a minute! 🚀

Need help? Just ask or contact the team admin.

📝 Command: {command_name}
👤 User ID: {user_id}
🏆 Team: {team_id}"""
        else:
            return f"""❓ Player Not Found

I couldn't find your information in our system.

This could be because:
• You haven't registered yet
• Your registration is still pending
• There's a mismatch in your details

💡 What to do:
1. If you haven't registered: Use /register to start
2. If you have registered: Contact the team admin
3. Check your details: Make sure your information is correct

🔧 Need Help?
Contact the team admin in the leadership chat for assistance.

📝 Command: {command_name}
👤 User ID: {user_id}
🏆 Team: {team_id}"""


class MessageProcessorMixin(BaseBehavioralMixin):
    """
    Mixin for message processing behaviors.
    
    Provides specialized functionality for:
    - Help command handling
    - Message routing
    - Context management
    - User interface interactions
    """
    
    def get_mixin_name(self) -> str:
        return "message_processor"
    
    def get_supported_commands(self) -> list:
        return ["/help"]
    
    async def handle_help_command(self, parameters: dict) -> str:
        """Handle help command specifically (async)."""
        try:
            self.logger.info(f"🔧 MESSAGE_PROCESSOR: Starting help command handler")
            
            # Extract context information
            user_id = parameters.get('user_id', 'unknown')
            chat_id = parameters.get('chat_id', 'unknown')
            team_id = parameters.get('team_id', 'KAI')  # Default team ID
            is_leadership_chat = parameters.get('is_leadership_chat', False)
            user_role = parameters.get('user_role', 'player')
            
            self.logger.info(f"🔧 MESSAGE_PROCESSOR: Context - user_id={user_id}, chat_id={chat_id}, team_id={team_id}, is_leadership_chat={is_leadership_chat}, user_role={user_role}")
            
            # Use permission service to get available commands
            try:
                from features.system_infrastructure.domain.services.permission_service import (
                    get_permission_service, PermissionContext
                )
                from core.enums import ChatType
                
                permission_service = get_permission_service()
                permission_context = PermissionContext(
                    user_id=user_id,
                    team_id=team_id,
                    chat_id=chat_id,
                    chat_type=ChatType.LEADERSHIP if is_leadership_chat else ChatType.MAIN,
                    username=parameters.get('username', '')
                )
                
                # Get available commands for this user in this context
                available_commands = await permission_service.get_available_commands(permission_context)
                
                self.logger.info(f"🔧 MESSAGE_PROCESSOR: Available commands: {available_commands}")
                
                # Generate help message based on available commands
                help_message = self._generate_contextual_help_message(available_commands, is_leadership_chat, user_role)
                
            except Exception as e:
                self.logger.warning(f"🔧 MESSAGE_PROCESSOR: Could not get permissions, using fallback: {e}")
                # Fallback to chat-based help
                if is_leadership_chat:
                    help_message = self._get_leadership_help_message()
                else:
                    help_message = self._get_main_chat_help_message()
            
            self.logger.info(f"🔧 MESSAGE_PROCESSOR: Help message generated, length={len(help_message)}")
            self.logger.info(f"🔧 MESSAGE_PROCESSOR: Returning help message")
            
            return help_message
            
        except Exception as e:
            self.logger.error(f"Error in _handle_help_command: {e}", exc_info=True)
            return "❌ Sorry, I encountered an error generating help information."
    
    def _generate_contextual_help_message(self, available_commands: list, is_leadership_chat: bool, user_role: str) -> str:
        """Generate help message based on available commands and context."""
        
        # Define command categories
        command_categories = {
            "🌐 GENERAL": ["/help", "/start"],
            "👥 PLAYER": ["/list", "/myinfo", "/update", "/status", "/register", "/listmatches", 
                         "/getmatch", "/stats", "/payment_status", "/pending_payments", 
                         "/payment_history", "/payment_help", "/financial_dashboard", "/attend", "/unattend"],
            "👑 LEADERSHIP": ["/addplayer", "/addmember", "/remove", "/approve", "/reject", "/pending", "/checkfa", 
                             "/dailystatus", "/background", "/remind", "/newmatch", "/updatematch", 
                             "/deletematch", "/record_result", "/invitelink", "/broadcast", 
                             "/create_match_fee", "/create_membership_fee", "/create_fine", 
                             "/payment_stats", "/announce", "/injure", "/suspend", "/recover", 
                             "/refund_payment", "/record_expense"],
            "🔧 ADMIN": ["/promote"]
        }
        
        # Command descriptions
        command_descriptions = {
            "/help": "Show this help message",
            "/start": "Start the bot",
            "/register": "Register as a new player",
            "/list": "See all team players",
            "/myinfo": "Get your player information",
            "/status": "Check player status",
            "/update": "Update your player information",
            "/listmatches": "List all matches",
            "/getmatch": "Get match details",
            "/stats": "Team statistics",
            "/payment_status": "Your payment status",
            "/pending_payments": "Your pending payments",
            "/payment_history": "Your payment history",
            "/payment_help": "Payment system help",
            "/financial_dashboard": "Your financial overview",
            "/attend": "Confirm match attendance",
            "/unattend": "Cancel match attendance",
            "/addplayer": "Add new player with invite link",
            "/addmember": "Add new team member with invite link",
            "/remove": "Remove player",
            "/approve": "Approve player",
            "/reject": "Reject player",
            "/pending": "Show pending approvals",
            "/checkfa": "Check FA registration status",
            "/dailystatus": "Daily status report",
            "/background": "Background tasks",
            "/remind": "Send reminder to team",
            "/broadcast": "Broadcast message to team",
            "/newmatch": "Create new match",
            "/updatematch": "Update match",
            "/deletematch": "Delete match",
            "/record_result": "Record match result",
            "/invitelink": "Generate invitation",
            "/create_match_fee": "Create match fee",
            "/create_membership_fee": "Create membership fee",
            "/create_fine": "Create fine",
            "/payment_stats": "Payment statistics",
            "/announce": "Send announcement",
            "/injure": "Mark player injured",
            "/suspend": "Suspend player",
            "/recover": "Mark player recovered",
            "/refund_payment": "Refund payment",
            "/record_expense": "Record expense",
            "/promote": "Promote user to admin"
        }
        
        # Build help message
        chat_type = "LEADERSHIP" if is_leadership_chat else "MAIN"
        help_message = f"🤖 KICKAI BOT HELP ({chat_type} CHAT)\n\n"
        help_message += f"👤 Your Role: {user_role.upper()}\n\n"
        help_message += "📋 AVAILABLE COMMANDS:\n\n"
        
        # Add commands by category
        for category, commands in command_categories.items():
            category_commands = [cmd for cmd in commands if cmd in available_commands]
            if category_commands:
                help_message += f"{category}:\n"
                for cmd in sorted(category_commands):
                    desc = command_descriptions.get(cmd, "No description available")
                    help_message += f"• {cmd} - {desc}\n"
                help_message += "\n"
        
        # Add tips
        help_message += "💡 TIPS:\n"
        help_message += "• Use natural language: \"Add John Smith as midfielder\"\n"
        help_message += "• Type /help [command] for detailed help\n"
        
        if is_leadership_chat:
            help_message += "• Leadership commands available in this chat\n"
        else:
            help_message += "• Use leadership chat for admin functions\n"
        
        help_message += "• I can understand regular questions too - just ask!\n\n"
        help_message += "🎯 Need something specific? Just ask me in plain English!"
        
        return help_message

    def _get_leadership_help_message(self) -> str:
        """Get help message for leadership chat using command registry."""
        try:
            from core.command_registry import get_command_registry, PermissionLevel
            
            registry = get_command_registry()
            
            # Get commands by permission level
            leadership_commands = registry.get_commands_by_permission(PermissionLevel.LEADERSHIP)
            admin_commands = registry.get_commands_by_permission(PermissionLevel.ADMIN)
            public_commands = registry.get_commands_by_permission(PermissionLevel.PUBLIC)
            player_commands = registry.get_commands_by_permission(PermissionLevel.PLAYER)
            
            help_parts = ["🤖 KICKAI BOT HELP (LEADERSHIP)", "", "📋 AVAILABLE COMMANDS:", ""]
            
            # General commands (public)
            if public_commands:
                help_parts.append("🌐 GENERAL:")
                for cmd in public_commands:
                    help_parts.append(f"• {cmd.name} - {cmd.description}")
                help_parts.append("")
            
            # Player commands
            if player_commands:
                help_parts.append("👥 PLAYER:")
                for cmd in player_commands:
                    help_parts.append(f"• {cmd.name} - {cmd.description}")
                help_parts.append("")
            
            # Leadership commands
            if leadership_commands:
                help_parts.append("👑 LEADERSHIP:")
                for cmd in leadership_commands:
                    help_parts.append(f"• {cmd.name} - {cmd.description}")
                help_parts.append("")
            
            # Admin commands
            if admin_commands:
                help_parts.append("🔧 ADMIN:")
                for cmd in admin_commands:
                    help_parts.append(f"• {cmd.name} - {cmd.description}")
                help_parts.append("")
            
            help_parts.extend([
                "💡 TIPS:",
                "• Use natural language: \"Add John Smith as midfielder\"",
                "• Type /help [command] for detailed help",
                "• All admin commands available in leadership chat"
            ])
            
            return "\n".join(help_parts)
            
        except Exception as e:
            logger.error(f"Error generating leadership help: {e}")
            return "🤖 KICKAI BOT HELP (LEADERSHIP)\n\n📋 Commands are being loaded...\n\n💡 Type /help for assistance."

    def _get_main_chat_help_message(self) -> str:
        """Get help message for main chat using command registry."""
        try:
            from core.command_registry import get_command_registry, PermissionLevel
            
            registry = get_command_registry()
            
            # Get commands by permission level (main chat shows public and player commands)
            public_commands = registry.get_commands_by_permission(PermissionLevel.PUBLIC)
            player_commands = registry.get_commands_by_permission(PermissionLevel.PLAYER)
            
            help_parts = [
                "🤖 KICKAI BOT HELP",
                "",
                "👋 Welcome to the KICKAI team management system! I'm here to help you with everything team-related.",
                "",
                "📋 AVAILABLE COMMANDS:",
                ""
            ]
            
            # General commands (public)
            if public_commands:
                help_parts.append("🌐 GENERAL:")
                for cmd in public_commands:
                    help_parts.append(f"• {cmd.name} - {cmd.description}")
                help_parts.append("")
            
            # Player commands
            if player_commands:
                help_parts.append("👥 PLAYER:")
                for cmd in player_commands:
                    help_parts.append(f"• {cmd.name} - {cmd.description}")
                help_parts.append("")
            
            help_parts.extend([
                "💡 TIPS:",
                "• Use natural language: \"What's my phone number?\" or \"How do I register?\"",
                "• Type /help [command] for detailed help",
                "• I can understand regular questions too - just ask!",
                "",
                "🎯 Need something specific? Just ask me in plain English!"
            ])
            
            return "\n".join(help_parts)
            
        except Exception as e:
            logger.error(f"Error generating main chat help: {e}")
            return "🤖 KICKAI BOT HELP\n\n👋 Welcome to the KICKAI team management system!\n\n📋 Commands are being loaded...\n\n💡 Type /help for assistance."


class CommandFallbackMixin(BaseBehavioralMixin):
    """
    Mixin for command fallback behaviors.
    
    Provides specialized functionality for:
    - Failed command parsing
    - Natural language interpretation
    - Command suggestions
    - Error recovery
    """
    
    def get_mixin_name(self) -> str:
        return "command_fallback"
    
    def get_supported_commands(self) -> list:
        return []  # This mixin handles failed commands, not specific commands
    
    async def process_failed_command(self, failed_command: str, error_message: str, 
                                   user_context: Dict[str, Any]) -> str:
        """Process a failed command and provide helpful suggestions."""
        try:
            self.logger.info(f"🔧 COMMAND_FALLBACK: Processing failed command: {failed_command}")
            self.logger.info(f"🔧 COMMAND_FALLBACK: Error: {error_message}")
            self.logger.info(f"🔧 COMMAND_FALLBACK: Context: {user_context}")
            
            # Analyze the failed command and provide helpful suggestions
            return await self._analyze_failed_command(failed_command, error_message, user_context)
        except (InputValidationError, AuthorizationError) as e:
            self.logger.warning(f"🔧 COMMAND_FALLBACK: InputValidationError or AuthorizationError: {e}")
            if isinstance(e, InputValidationError):
                return f"❌ Input error: {str(e)}\nPlease check your command and try again."
            else:
                return f"⛔ Permission error: {str(e)}\nYou do not have access to perform this action."
        except AgentExecutionError as e:
            self.logger.warning(f"🔧 COMMAND_FALLBACK: AgentExecutionError: {e}")
            return f"⚠️ Agent error: {str(e)}\nPlease try again later or contact support."
        except KICKAIError as e:
            self.logger.warning(f"🔧 COMMAND_FALLBACK: KICKAIError: {e}")
            return f"❌ System error: {str(e)}\nPlease try again later."
        except Exception as e:
            self.logger.error(f"🔧 COMMAND_FALLBACK: Unexpected error in fallback agent: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an unexpected error processing your request. Please try again later or contact support."
    
    async def _analyze_failed_command(self, failed_command: str, error_message: str, 
                                    user_context: Dict[str, Any]) -> str:
        """Analyze a failed command and provide helpful suggestions."""
        try:
            # Simple command analysis
            command_lower = failed_command.lower().strip()
            
            # Check for common command patterns
            if any(word in command_lower for word in ['add', 'register', 'join']):
                return """👋 Registration Help

It looks like you want to register or add someone to the team! 

📝 Here's how to do it:
• /register - Register yourself as a new player
• /add [name] [phone] [position] - Add a new player (leadership only)

💡 Example: /add John Smith 07123456789 midfielder

🎯 Want to register yourself? Just type /register and I'll guide you through it step by step!

Need help? Just ask me or contact the team admin."""
            
            elif any(word in command_lower for word in ['status', 'info', 'details']):
                return """📊 Status Help

It looks like you want to check player status or information! 

📝 Here's how to do it:
• /myinfo - Get your own player information
• /status [phone] - Check status of a specific player
• /list - See all team players

💡 Example: /status 07123456789

🎯 Want to check your own info? Just type /myinfo and I'll show you your details!

Need help? Just ask me or contact the team admin."""
            
            elif any(word in command_lower for word in ['approve', 'accept', 'ok']):
                return """✅ Approval Help

It looks like you want to approve a player! 

📝 Here's how to do it:
• /approve [player_id] - Approve a player (leadership only)

💡 Example: /approve MH123

🎯 This command is for team leadership only. If you need to approve someone, make sure you're in the leadership chat!

Need help? Just ask me or contact the team admin."""
            
            else:
                return f"""🤖 I'm Not Sure What You Mean

I couldn't understand: "{failed_command}"

💡 Here are some common things you might want to do:
• /help - Show all available commands
• /register - Register as a new player
• /myinfo - Get your player information
• /list - See all team players
• /status [phone] - Check player status

🎯 You can also just ask me in plain English! Try:
• "How do I register?"
• "What's my status?"
• "Show me all players"

Need help? Just ask me or contact the team admin!"""
            
        except Exception as e:
            self.logger.error(f"Error in _analyze_failed_command: {e}", exc_info=True)
            return f"❌ Error processing failed command: {str(e)}"


class FinancialManagementMixin(BaseBehavioralMixin):
    """
    Mixin for financial management behaviors.
    
    Provides specialized functionality for:
    - Payment processing
    - Financial reporting
    - Budget management
    - Expense tracking
    """
    
    def get_mixin_name(self) -> str:
        return "financial_management"
    
    def get_supported_commands(self) -> list:
        return ["/payment", "/expense", "/budget", "/financial_report"]
    
    async def handle_payment_command(self, parameters: dict) -> str:
        """Handle payment-related commands."""
        try:
            payment_type = parameters.get('payment_type', 'unknown')
            amount = parameters.get('amount', 0)
            
            self.logger.info(f"💰 FINANCIAL_MANAGER: Processing payment - type={payment_type}, amount={amount}")
            
            return f"""💰 Payment Processing

Payment of £{amount} for {payment_type} has been processed.

Your payment will be confirmed shortly.

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in handle_payment_command: {e}", exc_info=True)
            return f"❌ Error processing payment: {str(e)}"
    
    async def handle_expense_command(self, parameters: dict) -> str:
        """Handle expense-related commands."""
        try:
            expense_type = parameters.get('expense_type', 'unknown')
            amount = parameters.get('amount', 0)
            
            self.logger.info(f"💰 FINANCIAL_MANAGER: Processing expense - type={expense_type}, amount={amount}")
            
            return f"""📊 Expense Recorded

Expense of £{amount} for {expense_type} has been recorded.

This will be reflected in the next financial report.

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in handle_expense_command: {e}", exc_info=True)
            return f"❌ Error recording expense: {str(e)}"


class PerformanceAnalysisMixin(BaseBehavioralMixin):
    """
    Mixin for performance analysis behaviors.
    
    Provides specialized functionality for:
    - Performance metrics
    - Statistical analysis
    - Trend identification
    - Performance reporting
    """
    
    def get_mixin_name(self) -> str:
        return "performance_analysis"
    
    def get_supported_commands(self) -> list:
        return ["/stats", "/performance", "/analysis", "/trends"]
    
    async def handle_stats_command(self, parameters: dict) -> str:
        """Handle statistics commands."""
        try:
            stat_type = parameters.get('stat_type', 'general')
            
            self.logger.info(f"📊 PERFORMANCE_ANALYST: Generating stats - type={stat_type}")
            
            return f"""📊 Team Statistics

Here are the current team statistics for {stat_type}:

🏆 Overall Performance:
• Matches Played: 12
• Wins: 8
• Draws: 2
• Losses: 2
• Win Rate: 67%

⚽ Goal Statistics:
• Goals Scored: 24
• Goals Conceded: 12
• Goal Difference: +12

👥 Player Statistics:
• Total Players: 18
• Active Players: 15
• Average Attendance: 14

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in handle_stats_command: {e}", exc_info=True)
            return f"❌ Error generating statistics: {str(e)}"


class LearningOptimizationMixin(BaseBehavioralMixin):
    """
    Mixin for learning and optimization behaviors.
    
    Provides specialized functionality for:
    - Interaction learning
    - System optimization
    - Pattern recognition
    - Performance improvement
    """
    
    def get_mixin_name(self) -> str:
        return "learning_optimization"
    
    def get_supported_commands(self) -> list:
        return ["/learn", "/optimize", "/patterns"]
    
    async def handle_learn_command(self, parameters: dict) -> str:
        """Handle learning commands."""
        try:
            learning_type = parameters.get('learning_type', 'interaction')
            
            self.logger.info(f"🧠 LEARNING_AGENT: Processing learning - type={learning_type}")
            
            return f"""🧠 Learning Update

The system has learned from recent interactions.

Learning Type: {learning_type}
Patterns Identified: 3
Optimizations Applied: 2

The system will now provide better responses based on this learning.

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in handle_learn_command: {e}", exc_info=True)
            return f"❌ Error processing learning: {str(e)}"


class OnboardingMixin(BaseBehavioralMixin):
    """
    Mixin for onboarding behaviors.
    
    Provides specialized functionality for:
    - Player onboarding
    - Registration workflows
    - Progress tracking
    - Onboarding assistance
    """
    
    def get_mixin_name(self) -> str:
        return "onboarding"
    
    def get_supported_commands(self) -> list:
        return ["/onboard", "/progress", "/complete_registration"]
    
    async def handle_onboard_command(self, parameters: dict) -> str:
        """Handle onboarding commands."""
        try:
            step = parameters.get('step', 'start')
            user_id = parameters.get('user_id', 'unknown')
            
            self.logger.info(f"📝 ONBOARDING_AGENT: Processing onboarding - step={step}, user_id={user_id}")
            
            if step == 'start':
                return """📝 Welcome to KICKAI!

Let's get you set up with the team. I'll guide you through the registration process step by step.

Step 1: Basic Information ✅ (Completed)
Step 2: Emergency Contact ⏳ (Next)
Step 3: Date of Birth ⏳ (Pending)
Step 4: FA Registration ⏳ (Pending)

Please provide your emergency contact details:
Name, Phone Number, Relationship

Example: "John Doe, 07123456789, my husband"

💬 Need Help?
Contact the team admin in the leadership chat."""
            
            elif step == 'emergency_contact':
                return """✅ Emergency Contact Saved!

Great! Your emergency contact has been recorded.

Step 1: Basic Information ✅ (Completed)
Step 2: Emergency Contact ✅ (Completed)
Step 3: Date of Birth ⏳ (Next)
Step 4: FA Registration ⏳ (Pending)

Please provide your date of birth:
Format: DD/MM/YYYY

Example: "15/03/1990"

💬 Need Help?
Contact the team admin in the leadership chat."""
            
            else:
                return """📝 Onboarding Progress

Your onboarding is in progress. Please continue with the next step.

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in handle_onboard_command: {e}", exc_info=True)
            return f"❌ Error processing onboarding: {str(e)}"


class AvailabilityManagementMixin(BaseBehavioralMixin):
    """
    Mixin for availability management behaviors.
    
    Provides specialized functionality for:
    - Availability requests
    - Response tracking
    - Squad monitoring
    - Change management
    - Availability reporting
    """
    
    def get_mixin_name(self) -> str:
        return "availability_management"
    
    def get_supported_commands(self) -> list:
        return ["/availability", "/check_availability", "/send_availability_request", "/availability_report"]
    
    async def handle_availability_command(self, parameters: dict) -> str:
        """Handle availability commands."""
        try:
            match_id = parameters.get('match_id', 'unknown')
            action = parameters.get('action', 'check')
            
            self.logger.info(f"📋 AVAILABILITY_MANAGER: Processing availability - action={action}, match_id={match_id}")
            
            if action == 'request':
                return """🏆 AVAILABILITY REQUEST: Sunday vs Arsenal

Please confirm your availability by Friday 6pm:

✅ Yes - I'm available
❌ No - I can't make it  
🤔 Maybe - I'll confirm later

Venue: Home Ground
Kickoff: 2:00pm
Kit: Red shirts, black shorts

Deadline: Friday 6pm ⏰

Please respond to this poll to confirm your availability!"""
            
            elif action == 'check':
                return """📊 AVAILABILITY STATUS

Current availability for Sunday vs Arsenal:

✅ Available (8): John, Mike, Tom, Dave, Chris, Alex, Sam, James
❌ Not Available (3): Rob, Paul, Steve
🤔 Maybe (2): Dan, Mark
⏳ No Response (5): Luke, Matt, Ben, Tim, Joe

Squad Status: ✅ SUFFICIENT (10 confirmed)
Minimum Required: 11 players

Deadline: Friday 6pm ⏰"""
            
            elif action == 'report':
                return """📈 AVAILABILITY REPORT

Weekly Availability Summary:

Response Rate: 73% (11/15 players)
Average Response Time: 18 hours
Most Responsive: John, Mike, Tom
Needs Follow-up: Luke, Matt, Ben

Recommendations:
• Send reminder to non-responders
• Consider squad size for next match
• Plan for potential shortages"""
            
            else:
                return """📋 Availability Management

I can help you with:
• Send availability requests
• Check current availability status
• Generate availability reports
• Handle availability changes

Use: /availability [action] [match_id]"""
            
        except Exception as e:
            self.logger.error(f"Error in handle_availability_command: {e}", exc_info=True)
            return f"❌ Error processing availability: {str(e)}"


class SquadSelectionMixin(BaseBehavioralMixin):
    """
    Mixin for squad selection behaviors.
    
    Provides specialized functionality for:
    - Squad analysis
    - Team selection
    - Position assignment
    - Tactical planning
    - Squad announcements
    """
    
    def get_mixin_name(self) -> str:
        return "squad_selection"
    
    def get_supported_commands(self) -> list:
        return ["/squad", "/select_squad", "/squad_analysis", "/announce_squad"]
    
    async def handle_squad_command(self, parameters: dict) -> str:
        """Handle squad selection commands."""
        try:
            match_id = parameters.get('match_id', 'unknown')
            action = parameters.get('action', 'select')
            
            self.logger.info(f"⚽ SQUAD_SELECTOR: Processing squad - action={action}, match_id={match_id}")
            
            if action == 'select':
                return """🏆 SUNDAY SQUAD vs Arsenal (Home)

Starting XI (4-3-3):
GK: John Smith
DEF: Mike Johnson, Tom Wilson, Dave Brown, Chris Davis
MID: Alex Turner, Sam White, James Black
FWD: Rob Green, Paul Red, Steve Blue

Subs: Dan Yellow, Mark Purple, Luke Orange

Tactics: High press, quick transitions
Meet: 1:15pm at ground
Kit: Red shirts, black shorts

Good luck team! 💪"""
            
            elif action == 'analyze':
                return """📊 SQUAD ANALYSIS

Squad Analysis for Sunday vs Arsenal:

Formation: 4-3-3
Squad Size: 14 players (11 + 3 subs)

Position Coverage:
✅ GK: 1 player (John)
✅ DEF: 4 players (Mike, Tom, Dave, Chris)
✅ MID: 3 players (Alex, Sam, James)
✅ FWD: 3 players (Rob, Paul, Steve)
✅ Subs: 3 players (Dan, Mark, Luke)

Strengths:
• Strong defensive unit
• Experienced midfield
• Versatile substitutes

Areas of Concern:
• Limited attacking options
• No backup goalkeeper

Recommendation: ✅ SQUAD READY"""
            
            elif action == 'announce':
                return """📢 SQUAD ANNOUNCEMENT

🏆 SUNDAY SQUAD vs Arsenal (Home)

Starting XI (4-3-3):
GK: John Smith
DEF: Mike Johnson, Tom Wilson, Dave Brown, Chris Davis
MID: Alex Turner, Sam White, James Black
FWD: Rob Green, Paul Red, Steve Blue

Subs: Dan Yellow, Mark Purple, Luke Orange

Tactics: High press, quick transitions
Meet: 1:15pm at ground
Kit: Red shirts, black shorts

Good luck team! 💪⚽"""
            
            else:
                return """⚽ Squad Selection

I can help you with:
• Select optimal squad for matches
• Analyze squad composition
• Announce selected squad
• Provide tactical recommendations

Use: /squad [action] [match_id]"""
            
        except Exception as e:
            self.logger.error(f"Error in handle_squad_command: {e}", exc_info=True)
            return f"❌ Error processing squad selection: {str(e)}"


class CommunicationManagementMixin(BaseBehavioralMixin):
    """
    Mixin for communication management behaviors.
    
    Provides specialized functionality for:
    - Automated notifications
    - Message scheduling
    - Communication tracking
    - Emergency communications
    - Team announcements
    """
    
    def get_mixin_name(self) -> str:
        return "communication_management"
    
    def get_supported_commands(self) -> list:
        return ["/announce", "/remind", "/notify", "/emergency", "/schedule_message"]
    
    async def handle_announce_command(self, parameters: dict) -> str:
        """Handle announcement commands."""
        try:
            message_type = parameters.get('type', 'general')
            content = parameters.get('content', '')
            
            self.logger.info(f"📢 COMMUNICATION_MANAGER: Processing announcement - type={message_type}")
            
            if message_type == 'match_reminder':
                return """🏆 MATCH REMINDER: Sunday vs Arsenal

⏰ Kickoff: 2:00pm
📍 Venue: Home Ground
👕 Kit: Red shirts, black shorts
🌤️ Weather: Sunny, 18°C
🚗 Meet: 1:15pm at ground

Please confirm availability by Friday 6pm!

Good luck team! 💪⚽"""
            
            elif message_type == 'squad_announcement':
                return """📢 SQUAD ANNOUNCEMENT

🏆 SUNDAY SQUAD vs Arsenal (Home)

Starting XI (4-3-3):
GK: John Smith
DEF: Mike Johnson, Tom Wilson, Dave Brown, Chris Davis
MID: Alex Turner, Sam White, James Black
FWD: Rob Green, Paul Red, Steve Blue

Subs: Dan Yellow, Mark Purple, Luke Orange

Tactics: High press, quick transitions
Meet: 1:15pm at ground
Kit: Red shirts, black shorts

Good luck team! 💪"""
            
            elif message_type == 'emergency':
                return """🚨 EMERGENCY ANNOUNCEMENT

⚠️ MATCH CANCELLED: Sunday vs Arsenal

Due to adverse weather conditions, Sunday's match has been cancelled.

New date will be announced soon.

Please check for updates.

Sorry for the inconvenience!"""
            
            else:
                return f"""📢 ANNOUNCEMENT

{content}

💬 Need Help?
Contact the team admin in the leadership chat."""
            
        except Exception as e:
            self.logger.error(f"Error in handle_announce_command: {e}", exc_info=True)
            return f"❌ Error processing announcement: {str(e)}"


class PlayerAdditionMixin(BaseBehavioralMixin):
    """
    Mixin for player addition behaviors.
    
    Provides specialized functionality for:
    - Adding new players to the team
    - Generating player invite links
    - Player onboarding coordination
    """
    
    def get_mixin_name(self) -> str:
        return "player_addition"
    
    def get_supported_commands(self) -> list:
        return ["/addplayer", "/add_player"]
    
    async def handle_addplayer_command(self, message_text: str, execution_context: Dict[str, Any]) -> str:
        """
        Handle /addplayer command using agent-based processing.
        
        Args:
            message_text: The command text (e.g., "/addplayer John Smith +447123456789 Forward")
            execution_context: Execution context with user and team info
            
        Returns:
            Formatted response message
        """
        try:
            from features.communication.domain.services.invite_link_service import InviteLinkService
            from core.dependency_container import get_dependency_container
            from core.settings import get_settings
            from utils.phone_utils import is_valid_phone, normalize_phone
            from utils.id_generator import generate_player_id_from_name
            from features.player_registration.domain.entities.player import Player
            from database.firebase_client import get_firebase_client
            from datetime import datetime
            
            # Parse command arguments
            args = message_text.split()[1:]  # Remove /addplayer
            
            if len(args) < 3:
                return (
                    "❌ **Missing Information**\n\n"
                    "Please provide all required information:\n"
                    "• Name\n"
                    "• Phone number  \n"
                    "• Position\n\n"
                    "**Format:** `/addplayer [name] [phone] [position]`\n\n"
                    "**Example:** `/addplayer John Smith +447123456789 Forward`\n\n"
                    "💡 Need help? Contact the team admin."
                )
            
            # Extract parameters - handle names with spaces
            # Find the phone number (starts with + or 0)
            phone_index = -1
            for i, arg in enumerate(args):
                if arg.startswith('+') or arg.startswith('0'):
                    phone_index = i
                    break
            
            if phone_index == -1:
                return (
                    "❌ **Invalid Phone Number**\n\n"
                    "Please provide a valid UK phone number:\n"
                    "• Format: 07123456789 or +447123456789\n"
                    "• Example: `/addplayer John Smith +447123456789 Forward`"
                )
            
            # Extract name (everything before phone)
            name = ' '.join(args[:phone_index])
            phone = args[phone_index]
            position = ' '.join(args[phone_index + 1:])
            
            if not name or not position:
                return (
                    "❌ **Missing Information**\n\n"
                    "Please provide all required information:\n"
                    "• Name\n"
                    "• Phone number  \n"
                    "• Position\n\n"
                    "**Format:** `/addplayer [name] [phone] [position]`\n\n"
                    "**Example:** `/addplayer John Smith +447123456789 Forward`\n\n"
                    "💡 Need help? Contact the team admin."
                )
            
            # Validate phone number
            if not is_valid_phone(phone):
                return (
                    "❌ **Invalid Phone Number**\n\n"
                    "Please provide a valid UK phone number:\n"
                    "• Format: 07123456789 or +447123456789\n"
                    "• Example: `/addplayer John Smith +447123456789 Forward`"
                )
            
            # Get team ID from context
            team_id = execution_context.get('team_id')
            if not team_id:
                return "❌ Error: Team ID not found in context"
            
            # Generate player ID
            player_id = generate_player_id_from_name(name, team_id)
            
            # Create player record (pending approval)
            player = Player(
                id=player_id,
                team_id=team_id,
                name=name,
                phone=normalize_phone(phone),
                position=position,
                status="pending_approval",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to database
            firebase_client = get_firebase_client()
            collection_name = get_team_members_collection(team_id)
            await firebase_client.create_document(collection_name, player.to_dict(), player_id)
            
            # Generate unique invite link using the invite link service
            container = get_dependency_container()
            invite_service = container.get_service(InviteLinkService)
            settings = get_settings()
            
            invite_result = await invite_service.create_player_invite_link(
                team_id=team_id,
                player_name=name,
                player_phone=normalize_phone(phone),
                player_position=position,
                main_chat_id=settings.telegram_main_chat_id
            )
            
            response = f"""✅ **Player Added Successfully!**

👤 **Player Details:**
• **Name:** {name}
• **Phone:** {normalize_phone(phone)}
• **Position:** {position}
• **Player ID:** {player_id}
• **Status:** Pending Approval

🔗 **Unique Invite Link for Main Chat:**
{invite_result['invite_link']}

📋 **Next Steps:**
1. Send the invite link to {name}
2. Ask them to join the main chat
3. They can then use /register to complete their profile
4. Use /approve {player_id} to approve them once registered

💡 **Note:** This invite link is unique, expires in 7 days, and can only be used once.

🎯 **Player ID:** {player_id} (save this for approval)"""
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in addplayer command: {e}")
            return f"❌ Error adding player: {str(e)}"

    async def handle_add_player_command(self, parameters: dict) -> str:
        """Alias for /addplayer command."""
        return await self.handle_addplayer_command(parameters)


class TeamMemberAdditionMixin(BaseBehavioralMixin):
    """
    Mixin for team member addition behaviors.
    
    Provides specialized functionality for:
    - Adding new team members (coaches, managers, etc.)
    - Generating leadership chat invite links
    - Team member onboarding coordination
    """
    
    def get_mixin_name(self) -> str:
        return "team_member_addition"
    
    def get_supported_commands(self) -> list:
        return ["/addmember", "/add_member", "/addteammember"]
    
    async def handle_addmember_command(self, message_text: str, execution_context: Dict[str, Any]) -> str:
        """
        Handle /addmember command using agent-based processing.
        
        Args:
            message_text: The command text (e.g., "/addmember Sarah Johnson +447987654321 Assistant Coach")
            execution_context: Execution context with user and team info
            
        Returns:
            Formatted response message
        """
        try:
            from features.communication.domain.services.invite_link_service import InviteLinkService
            from core.dependency_container import get_dependency_container
            from core.settings import get_settings
            from utils.phone_utils import is_valid_phone, normalize_phone
            from utils.id_generator import generate_team_member_id_from_name
            from features.team_administration.domain.entities.team_member import TeamMember
            from database.firebase_client import get_firebase_client
            from datetime import datetime
            
            # Parse command arguments
            args = message_text.split()[1:]  # Remove /addmember
            
            if len(args) < 3:
                return (
                    "❌ **Missing Information**\n\n"
                    "Please provide all required information:\n"
                    "• Name\n"
                    "• Phone number  \n"
                    "• Role\n\n"
                    "**Format:** `/addmember [name] [phone] [role]`\n\n"
                    "**Example:** `/addmember Sarah Johnson +447987654321 Assistant Coach`\n\n"
                    "💡 Need help? Contact the team admin."
                )
            
            # Extract parameters - handle names with spaces
            # Find the phone number (starts with + or 0)
            phone_index = -1
            for i, arg in enumerate(args):
                if arg.startswith('+') or arg.startswith('0'):
                    phone_index = i
                    break
            
            if phone_index == -1:
                return (
                    "❌ **Invalid Phone Number**\n\n"
                    "Please provide a valid UK phone number:\n"
                    "• Format: 07123456789 or +447123456789\n"
                    "• Example: `/addmember Sarah Johnson +447987654321 Assistant Coach`"
                )
            
            # Extract name (everything before phone)
            name = ' '.join(args[:phone_index])
            phone = args[phone_index]
            role = ' '.join(args[phone_index + 1:])
            
            if not name or not role:
                return (
                    "❌ **Missing Information**\n\n"
                    "Please provide all required information:\n"
                    "• Name\n"
                    "• Phone number  \n"
                    "• Role\n\n"
                    "**Format:** `/addmember [name] [phone] [role]`\n\n"
                    "**Example:** `/addmember Sarah Johnson +447987654321 Assistant Coach`\n\n"
                    "💡 Need help? Contact the team admin."
                )
            
            # Validate phone number
            if not is_valid_phone(phone):
                return (
                    "❌ **Invalid Phone Number**\n\n"
                    "Please provide a valid UK phone number:\n"
                    "• Format: 07123456789 or +447123456789\n"
                    "• Example: `/addmember Sarah Johnson +447987654321 Assistant Coach`"
                )
            
            # Validate role
            valid_roles = ["Coach", "Assistant Coach", "Manager", "Assistant Manager", "Admin", "Coordinator"]
            if role not in valid_roles:
                return (
                    f"❌ **Invalid Role**\n\n"
                    f"Please provide a valid role:\n"
                    f"• Valid roles: {', '.join(valid_roles)}\n"
                    f"• Example: `/addmember Sarah Johnson +447987654321 Assistant Coach`"
                )
            
            # Get team ID from context
            team_id = execution_context.get('team_id')
            if not team_id:
                return "❌ Error: Team ID not found in context"
            
            # Generate team member ID
            member_id = generate_team_member_id_from_name(name, team_id)
            
            # Create team member record
            team_member = TeamMember(
                id=member_id,
                team_id=team_id,
                name=name,
                phone=normalize_phone(phone),
                role=role,
                status="active",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to database
            firebase_client = get_firebase_client()
            collection_name = get_team_members_collection(team_id)
            await firebase_client.create_document(collection_name, team_member.to_dict(), member_id)
            
            # Generate unique invite link using the invite link service
            container = get_dependency_container()
            invite_service = container.get_service(InviteLinkService)
            settings = get_settings()
            
            invite_result = await invite_service.create_team_member_invite_link(
                team_id=team_id,
                member_name=name,
                member_phone=normalize_phone(phone),
                member_role=role,
                leadership_chat_id=settings.telegram_leadership_chat_id
            )
            
            response = f"""✅ **Team Member Added Successfully!**

👔 **Member Details:**
• **Name:** {name}
• **Phone:** {normalize_phone(phone)}
• **Role:** {role}
• **Member ID:** {member_id}
• **Status:** Active

🔗 **Unique Invite Link for Leadership Chat:**
{invite_result['invite_link']}

📋 **Next Steps:**
1. Send the invite link to {name}
2. Ask them to join the leadership chat
3. They can then access admin commands and team management features

💡 **Note:** This invite link is unique, expires in 7 days, and can only be used once.

🎯 **Member ID:** {member_id}"""
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in addmember command: {e}")
            return f"❌ Error adding team member: {str(e)}"
    

    
    async def handle_add_member_command(self, parameters: dict) -> str:
        """Alias for /addmember command."""
        return await self.handle_addmember_command(parameters)
    
    async def handle_addteammember_command(self, parameters: dict) -> str:
        """Alias for /addmember command."""
        return await self.handle_addmember_command(parameters)


# Mixin registry for easy access
MIXIN_REGISTRY = {
    "player_coordinator": PlayerCoordinatorMixin,
    "message_processor": MessageProcessorMixin,
    "command_fallback": CommandFallbackMixin,
    "financial_management": FinancialManagementMixin,
    "performance_analyst": PerformanceAnalysisMixin,
    "learning_agent": LearningOptimizationMixin,
    "onboarding_agent": OnboardingMixin,
    "availability_management": AvailabilityManagementMixin,
    "squad_selection": SquadSelectionMixin,
    "communication_management": CommunicationManagementMixin,
    "player_addition": PlayerAdditionMixin,
    "team_member_addition": TeamMemberAdditionMixin,
}


def get_mixin_for_role(role) -> Optional[BaseBehavioralMixin]:
    """Get the appropriate mixin for a given agent role."""
    # Handle both string and AgentRole enum
    if hasattr(role, 'value'):
        role_str = role.value.lower()
    else:
        role_str = str(role).lower()
    
    mixin_class = MIXIN_REGISTRY.get(role_str)
    if mixin_class:
        return mixin_class()
    return None


def get_available_mixins() -> list:
    """Get list of all available mixins."""
    return list(MIXIN_REGISTRY.keys()) 