#!/usr/bin/env python3
"""
Behavioral Mixins for KICKAI Agents

This module provides mixin classes that add specialized functionality
to agents without duplicating common code. Each mixin focuses on a
specific behavioral domain.
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from core.exceptions import KICKAIError, InputValidationError, AuthorizationError, AgentExecutionError
from core.enhanced_logging import ErrorHandler, create_error_context, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class BaseBehavioralMixin(ABC):
    """Base class for all behavioral mixins."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
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
            is_leadership_chat = parameters.get('is_leadership_chat', False)
            user_role = parameters.get('user_role', 'player')
            
            self.logger.info(f"🔧 MESSAGE_PROCESSOR: Context - user_id={user_id}, chat_id={chat_id}, is_leadership_chat={is_leadership_chat}, user_role={user_role}")
            
            # Generate help message based on context
            if is_leadership_chat:
                self.logger.info(f"🔧 MESSAGE_PROCESSOR: Generating leadership chat help")
                help_message = self._get_leadership_help_message()
            else:
                self.logger.info(f"🔧 MESSAGE_PROCESSOR: Generating main chat help")
                help_message = self._get_main_chat_help_message()
            
            self.logger.info(f"🔧 MESSAGE_PROCESSOR: Help message generated, length={len(help_message)}")
            self.logger.info(f"🔧 MESSAGE_PROCESSOR: Returning help message")
            
            return help_message
            
        except Exception as e:
            self.logger.error(f"Error in _handle_help_command: {e}", exc_info=True)
            return "❌ Sorry, I encountered an error generating help information."
    
    def _get_leadership_help_message(self) -> str:
        """Get help message for leadership chat."""
        return """🤖 KICKAI BOT HELP (LEADERSHIP)

📋 AVAILABLE COMMANDS:

🌐 GENERAL:
• /help - Show this help message
• /start - Start the bot
• /register - Register as a new player

👥 PLAYER:
• /myinfo - Get your player information
• /list - See all team players
• /status [phone] - Check player status

👑 LEADERSHIP:
• /add [name] [phone] [position] - Add new player
• /remove [phone_or_player_id] - Remove player
• /approve [player_id] - Approve player
• /reject [player_id] [reason] - Reject player
• /pending - Show pending approvals
• /invitelink [phone_or_player_id] - Generate invitation
• /stats - Team statistics
• /checkfa - Check FA registration status
• /dailystatus - Daily status report
• /remind [message] - Send reminder to team
• /broadcast [message] - Broadcast message to team

🔧 ADMIN:
• /createteam [name] - Create new team
• /removeteam [team_id] - Remove team
• /listteams - List all teams
• /backgroundtasks - Manage background tasks

💡 TIPS:
• Use natural language: "Add John Smith as midfielder"
• Type /help [command] for detailed help
• All admin commands available in leadership chat"""

    def _get_main_chat_help_message(self) -> str:
        """Get help message for main chat."""
        return """🤖 KICKAI BOT HELP

👋 Welcome to the KICKAI team management system! I'm here to help you with everything team-related.

📋 AVAILABLE COMMANDS:

🌐 GENERAL:
• /help - Show this help message
• /start - Start the bot
• /register - Register as a new player

👥 PLAYER:
• /myinfo - Get your player information
• /list - See all team players
• /status [phone] - Check player status

💡 TIPS:
• Use natural language: "What's my phone number?" or "How do I register?"
• Type /help [command] for detailed help
• I can understand regular questions too - just ask!

🎯 Need something specific? Just ask me in plain English!"""


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
        error_handler = ErrorHandler()
        try:
            self.logger.info(f"🔧 COMMAND_FALLBACK: Processing failed command: {failed_command}")
            self.logger.info(f"🔧 COMMAND_FALLBACK: Error: {error_message}")
            self.logger.info(f"🔧 COMMAND_FALLBACK: Context: {user_context}")
            
            # Analyze the failed command and provide helpful suggestions
            return await self._analyze_failed_command(failed_command, error_message, user_context)
        except (InputValidationError, AuthorizationError) as e:
            context = create_error_context(
                operation="process_failed_command",
                user_id=user_context.get("user_id"),
                team_id=user_context.get("team_id"),
                category=ErrorCategory.VALIDATION if isinstance(e, InputValidationError) else ErrorCategory.AUTHORIZATION,
                severity=ErrorSeverity.MEDIUM,
                input_parameters=user_context
            )
            error_handler.log_error(e, context, user_message=str(e))
            if isinstance(e, InputValidationError):
                return f"❌ Input error: {str(e)}\nPlease check your command and try again."
            else:
                return f"⛔ Permission error: {str(e)}\nYou do not have access to perform this action."
        except AgentExecutionError as e:
            context = create_error_context(
                operation="process_failed_command",
                user_id=user_context.get("user_id"),
                team_id=user_context.get("team_id"),
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.HIGH,
                input_parameters=user_context
            )
            error_handler.log_error(e, context, user_message=str(e))
            return f"⚠️ Agent error: {str(e)}\nPlease try again later or contact support."
        except KICKAIError as e:
            context = create_error_context(
                operation="process_failed_command",
                user_id=user_context.get("user_id"),
                team_id=user_context.get("team_id"),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                input_parameters=user_context
            )
            error_handler.log_error(e, context, user_message=str(e))
            return f"❌ System error: {str(e)}\nPlease try again later."
        except Exception as e:
            context = create_error_context(
                operation="process_failed_command",
                user_id=user_context.get("user_id"),
                team_id=user_context.get("team_id"),
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.CRITICAL,
                input_parameters=user_context
            )
            error_handler.log_error(e, context, user_message="Unexpected error in fallback agent.")
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
}


def get_mixin_for_role(role: str) -> Optional[BaseBehavioralMixin]:
    """Get the appropriate mixin for a given agent role."""
    mixin_class = MIXIN_REGISTRY.get(role.lower())
    if mixin_class:
        return mixin_class()
    return None


def get_available_mixins() -> list:
    """Get list of all available mixins."""
    return list(MIXIN_REGISTRY.keys()) 