#!/usr/bin/env python3
"""
Agentic Message Router

This module provides centralized agentic message routing following CrewAI best practices.
ALL messages go through agents - no direct processing bypasses the agentic system.
"""

from dataclasses import dataclass
from typing import Any

from loguru import logger

from src.agents.crew_agents import TeamManagementSystem
from src.agents.crew_lifecycle_manager import get_crew_lifecycle_manager
from src.agents.user_flow_agent import AgentResponse, TelegramMessage, UserFlowAgent, UserFlowDecision
from src.core.context_types import create_context_from_telegram_message
from src.core.enums import ChatType


@dataclass
class IntentResult:
    """Intent classification result."""
    intent: str
    confidence: float
    entities: dict[str, Any]


class AgenticMessageRouter:
    """
    Centralized agentic message routing following CrewAI best practices.
    
    This router ensures that ALL messages go through the agentic system.
    No direct processing bypasses agents.
    """

    def __init__(self, team_id: str, crewai_system: TeamManagementSystem = None):
        self.team_id = team_id
        self.crewai_system = crewai_system
        self.user_flow_agent = UserFlowAgent(team_id=team_id)
        self.crew_lifecycle_manager = get_crew_lifecycle_manager()
        self._setup_router()

    def _setup_router(self):
        """Set up the router configuration."""
        logger.info(f"🤖 AgenticMessageRouter initialized for team {self.team_id}")

    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """
        Route ALL messages through the agentic system.
        No direct processing bypasses agents.
        
        Args:
            message: Telegram message to route
            
        Returns:
            AgentResponse with the processed result
        """
        try:
            logger.info(f"🔄 AgenticMessageRouter: Routing message from {message.username} in {message.chat_type.value}")

            # Extract command from message text if it's a slash command
            command = None
            if message.text.startswith('/'):
                command = message.text.split()[0]  # Get the first word (the command)
                logger.info(f"🔄 AgenticMessageRouter: Detected command: {command}")

            # Determine user flow
            user_flow_result = await self.user_flow_agent.determine_user_flow(
                user_id=message.user_id,
                chat_type=message.chat_type,
                command=command
            )



            # Handle unregistered users
            if user_flow_result == UserFlowDecision.UNREGISTERED_USER:
                logger.info("🔄 AgenticMessageRouter: Unregistered user flow detected")
                return AgentResponse(
                    success=True,
                    message=self._get_unregistered_user_message(message.chat_type, message.username),
                    error=None
                )

            # Handle registered users - normal agentic processing
            logger.info("🔄 AgenticMessageRouter: Registered user flow detected")
            return await self._process_with_crewai_system(message)

        except Exception as e:
            logger.error(f"AgenticMessageRouter failed: {e}")
            return AgentResponse(
                success=False,
                message="❌ System error. Please try again.",
                error=str(e)
            )

    def _parse_registration_command(self, text: str) -> dict[str, str] | None:
        """Parse /register command and extract name, phone, and role."""
        try:
            parts = text.split()
            if len(parts) < 4:
                return None

            # Extract components
            name = parts[1]
            phone = parts[2]
            role = " ".join(parts[3:])

            return {
                'name': name,
                'phone': phone,
                'role': role
            }
        except Exception as e:
            logger.error(f"Registration command parsing failed: {e}")
            return None



    def _get_unregistered_user_message(self, chat_type: ChatType, username: str) -> str:
        """Get message for unregistered users."""
        from core.constants import BOT_VERSION
        
        if chat_type == ChatType.LEADERSHIP:
            return f"""👋 Welcome to KICKAI Leadership for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🤔 I don't see you registered as a team member yet.

📝 Please provide your details so I can add you to the team members collection.

💡 You can use:
/register [name] [phone] [role]

Example:
/register John Smith +1234567890 Assistant Coach

🎯 Your role can be:
• Team Manager, Coach, Assistant Coach
• Club Administrator, Treasurer
• Volunteer Coordinator, etc.

🚀 Once registered, you can:
• Add other team members and players
• Generate invite links for chats
• Manage the team system

Ready to get started? Use the /register command above!"""
        else:
            return f"""👋 Welcome to KICKAI for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🎯 To join the team as a player:

📞 Contact Team Leadership
You need to be added as a player by someone in the team's leadership.

💬 What to do:
1. Reach out to someone in the team's leadership chat
2. Ask them to add you as a player using the `/add` command
3. They'll send you an invite link to join the main chat
4. Once added, you can register with your full details

❓ Got here by mistake?
If you're not interested in joining the team, you can leave this chat.

🤖 Need help?
Use /help to see available commands or ask me questions!"""

    async def _process_with_crewai_system(self, message: TelegramMessage) -> AgentResponse:
        """
        Route registered user messages to specialized agents.
        
        Args:
            message: Telegram message to route
            
        Returns:
            AgentResponse with the processed result
        """
        try:
            # Get detailed registration status
            player_service = await self.user_flow_agent._get_player_service()
            team_service = await self.user_flow_agent._get_team_service()
            
            is_player = False
            is_team_member = False
            
            if player_service:
                try:
                    player = await player_service.get_player_by_telegram_id(message.user_id, message.team_id)
                    is_player = player is not None
                except Exception:
                    pass
                    
            if team_service:
                try:
                    team_member = await team_service.get_team_member_by_telegram_id(message.team_id, message.user_id)
                    is_team_member = team_member is not None
                except Exception:
                    pass
            
            # Determine registration status based on CHAT CONTEXT
            if message.chat_type == ChatType.MAIN:
                # In main chat, only players are considered registered
                is_registered = is_player
                logger.info(f"🔄 AgenticMessageRouter: Main chat - is_player={is_player}, is_team_member={is_team_member}, is_registered={is_registered}")
            elif message.chat_type == ChatType.LEADERSHIP:
                # In leadership chat, only team members are considered registered
                is_registered = is_team_member
                logger.info(f"🔄 AgenticMessageRouter: Leadership chat - is_player={is_player}, is_team_member={is_team_member}, is_registered={is_registered}")
            else:
                # Unknown chat type, assume unregistered
                is_registered = False
                logger.warning(f"⚠️ AgenticMessageRouter: Unknown chat type {message.chat_type}, assuming unregistered")
            
            # Create standardized context for CrewAI system
            standardized_context = create_context_from_telegram_message(
                user_id=message.user_id,
                team_id=message.team_id,
                chat_id=message.chat_id,
                chat_type=message.chat_type,
                message_text=message.text,
                username=message.username,
                telegram_name=message.username,  # Use username as telegram_name for now
                is_registered=is_registered,
                is_player=is_player,
                is_team_member=is_team_member
            )

            # Convert to execution context for backward compatibility
            execution_context = standardized_context.to_dict()
            execution_context.update({
                'is_leadership_chat': message.chat_type == ChatType.LEADERSHIP,
                'is_main_chat': message.chat_type == ChatType.MAIN,
            })

            logger.info(f"🔄 AgenticMessageRouter: User registration status - is_registered={is_registered}, is_player={is_player}, is_team_member={is_team_member}")

            # Use CrewAI system for registered users
            if self.crewai_system:
                logger.info("🔄 AgenticMessageRouter: Routing to CrewAI system")
                result = await self.crewai_system.execute_task(message.text, execution_context)
                return AgentResponse(message=result)
            else:
                # Use crew lifecycle manager as fallback
                logger.info("🔄 AgenticMessageRouter: Using crew lifecycle manager")
                result = await self.crew_lifecycle_manager.execute_task(
                    team_id=self.team_id,
                    task_description=message.text,
                    execution_context=execution_context
                )
                return AgentResponse(message=result)

        except Exception as e:
            logger.error(f"❌ Error routing to specialized agent: {e}")
            return AgentResponse(
                message="I encountered an error processing your request. Please try again.",
                success=False,
                error=str(e)
            )

    async def route_command(self, command_name: str, message: TelegramMessage) -> AgentResponse:
        """
        Route command messages through the agentic system with chat-type awareness.
        
        Args:
            command_name: Name of the command (e.g., "/help", "/myinfo")
            message: Telegram message to route
            
        Returns:
            AgentResponse with the processed result
        """
        try:
            logger.info(f"🔄 AgenticMessageRouter: Routing command {command_name} in {message.chat_type.value}")

            # Check if command is available for this chat type
            from core.command_registry_initializer import get_initialized_command_registry
            registry = get_initialized_command_registry()
            chat_type_str = message.chat_type.value
            available_command = registry.get_command_for_chat(command_name, chat_type_str)

            if not available_command:
                logger.warning(f"⚠️ Command {command_name} not available in {chat_type_str} chat")
                return AgentResponse(
                    message=f"❌ Command {command_name} is not available in this chat type.",
                    success=False,
                    error="Command not available in chat type"
                )

            # For commands, we still check user flow first
            user_flow = await self.user_flow_agent.determine_user_flow(message.user_id, message.chat_type, command_name)

                        # Handle unregistered user flows
            if user_flow == UserFlowDecision.UNREGISTERED_USER:
                logger.info("🔄 AgenticMessageRouter: Unregistered user command flow")
                return await self.user_flow_agent.handle_unregistered_user_flow(message)

            else:  # REGISTERED_USER
                # For registered users, route commands to CrewAI system
                logger.info("🔄 AgenticMessageRouter: Registered user command flow")
                return await self._process_with_crewai_system(message)

        except Exception as e:
            logger.error(f"❌ Error routing command: {e}")
            return AgentResponse(
                message="I encountered an error processing your command. Please try again.",
                success=False,
                error=str(e)
            )

    def convert_telegram_update_to_message(self, update: Any, command_name: str = None) -> TelegramMessage:
        """
        Convert Telegram update to domain message.
        
        Args:
            update: Telegram update object
            command_name: Optional command name for command messages
            
        Returns:
            TelegramMessage domain object
        """
        try:
            user_id = str(update.effective_user.id)
            chat_id = str(update.effective_chat.id)
            username = update.effective_user.username or update.effective_user.first_name

            # Determine chat type
            chat_type = self._determine_chat_type(chat_id)

            # Get message text
            if command_name:
                # For commands, build the full command string
                args = update.message.text.split()[1:] if len(update.message.text.split()) > 1 else []
                text = f"{command_name} {' '.join(args)}".strip()
            else:
                # For natural language, use the message text
                text = update.message.text.strip()

            return TelegramMessage(
                user_id=user_id,
                chat_id=chat_id,
                chat_type=chat_type,
                username=username,
                team_id=self.team_id,
                text=text,
                raw_update=update
            )

        except Exception as e:
            logger.error(f"❌ Error converting Telegram update to message: {e}")
            raise

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Determine the chat type based on chat ID."""
        # Use configured chat IDs if available
        if hasattr(self, 'main_chat_id') and hasattr(self, 'leadership_chat_id'):
            return self._determine_chat_type_with_ids(chat_id)

        # Fallback to simple heuristic
        if chat_id.startswith('-100'):
            # Group chat - we'd need to know which is main vs leadership
            # This should be configured in the router
            return ChatType.MAIN  # Default to main chat
        else:
            return ChatType.PRIVATE

    def set_chat_ids(self, main_chat_id: str, leadership_chat_id: str):
        """Set the chat IDs for proper chat type determination."""
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id

    def _determine_chat_type_with_ids(self, chat_id: str) -> ChatType:
        """Determine chat type using configured chat IDs."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.PRIVATE
