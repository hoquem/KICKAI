#!/usr/bin/env python3
"""
Agentic Message Router

This module provides centralized agentic message routing following CrewAI best practices.
ALL messages go through agents - no direct processing bypasses the agentic system.
"""

from dataclasses import dataclass
from typing import Any

from loguru import logger

# Lazy imports to avoid circular dependencies
# from kickai.agents.crew_agents import TeamManagementSystem
# from kickai.agents.crew_lifecycle_manager import get_crew_lifecycle_manager
from kickai.agents.user_flow_agent import (
    AgentResponse,
    TelegramMessage,
    UserFlowAgent,
    UserFlowDecision,
)
from kickai.core.context_types import create_context_from_telegram_message
from kickai.core.enums import ChatType


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

    def __init__(self, team_id: str, crewai_system=None):
        self.team_id = team_id
        self.crewai_system = crewai_system
        self.user_flow_agent = UserFlowAgent(team_id=team_id)
        # Lazy initialization to avoid circular dependencies
        self._crew_lifecycle_manager = None
        self._helper_agent = None
        self._setup_router()

    @property
    def crew_lifecycle_manager(self):
        """Lazy load crew lifecycle manager to avoid circular imports."""
        if self._crew_lifecycle_manager is None:
            from kickai.agents.crew_lifecycle_manager import get_crew_lifecycle_manager

            self._crew_lifecycle_manager = get_crew_lifecycle_manager()
        return self._crew_lifecycle_manager

    @property
    def helper_agent(self):
        """Lazy load helper agent to avoid circular imports."""
        if self._helper_agent is None:
            from kickai.agents.helper_task_manager import HelperTaskManager

            self._helper_agent = HelperTaskManager()
        return self._helper_agent

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
            logger.info(
                f"🔄 AgenticMessageRouter: Routing message from {message.username} in {message.chat_type.value}"
            )

            # Check for new chat members event (invite link processing)
            if hasattr(message, 'raw_update') and message.raw_update:
                if self._is_new_chat_members_event(message.raw_update):
                    logger.info("🔗 AgenticMessageRouter: Detected new_chat_members event")
                    return await self.route_new_chat_members(message)

            # Extract command from message text if it's a slash command
            command = None
            if message.text.startswith("/"):
                command = message.text.split()[0]  # Get the first word (the command)
                logger.info(f"🔄 AgenticMessageRouter: Detected command: {command}")

            # Check if this is a helper system command
            if self._is_helper_command(command):
                logger.info(f"🔄 AgenticMessageRouter: Routing to Helper Agent: {command}")
                return await self.route_help_request(message)

            # Check if command is available for this chat type (for registered users)
            if command and not self._is_helper_command(command):
                try:
                    from kickai.core.command_registry_initializer import (
                        get_initialized_command_registry,
                    )

                    registry = get_initialized_command_registry()
                    chat_type_str = message.chat_type.value
                    available_command = registry.get_command_for_chat(command, chat_type_str)

                    if not available_command:
                        logger.warning(f"⚠️ Command {command} not available in {chat_type_str} chat")
                        return AgentResponse(
                            message=self._get_unrecognized_command_message(
                                command, message.chat_type
                            ),
                            success=False,
                            error="Command not available in chat type",
                        )
                except RuntimeError as e:
                    if "Command registry not initialized" in str(e):
                        logger.warning(
                            "⚠️ Command registry not accessible, proceeding without validation"
                        )
                    else:
                        raise

            # Determine user flow
            user_flow_result = await self.user_flow_agent.determine_user_flow(
                user_id=message.user_id, chat_type=message.chat_type, command=command
            )

            # Handle unregistered users
            if user_flow_result == UserFlowDecision.UNREGISTERED_USER:
                logger.info("🔄 AgenticMessageRouter: Unregistered user flow detected")

                # Check if the message looks like a phone number
                if self._looks_like_phone_number(message.text):
                    logger.info(
                        "📱 AgenticMessageRouter: Detected phone number in message from unregistered user"
                    )
                    return await self._handle_phone_number_from_unregistered_user(message)

                # Show welcome message for unregistered users
                message_text = self._get_unregistered_user_message(
                    message.chat_type, message.username
                )

                return AgentResponse(
                    success=True,
                    message=message_text,
                    error=None,
                    # Contact sharing button only works in private chats, not group chats
                    needs_contact_button=False,
                )

            # Handle registered users - normal agentic processing
            logger.info("🔄 AgenticMessageRouter: Registered user flow detected")
            return await self._process_with_crewai_system(message)

        except Exception as e:
            logger.error(f"AgenticMessageRouter failed: {e}")
            return AgentResponse(
                success=False, message="❌ System error. Please try again.", error=str(e)
            )

    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """
        Route contact sharing messages for phone number linking.

        Args:
            message: Telegram message with contact information

        Returns:
            AgentResponse with the linking result
        """
        try:
            logger.info(
                f"📱 AgenticMessageRouter: Processing contact share from {message.username}"
            )

            # Check if message has contact information
            if not hasattr(message, "contact_phone") or not message.contact_phone:
                return AgentResponse(
                    success=False,
                    message="❌ No contact information found in message.",
                    error="Missing contact phone",
                )

            # Use the phone linking service to link the user
            from kickai.features.player_registration.domain.services.player_linking_service import (
                PlayerLinkingService,
            )

            linking_service = PlayerLinkingService(self.team_id)

            # Attempt to link the user
            linked_player = await linking_service.link_telegram_user_by_phone(
                phone=message.contact_phone, telegram_id=message.user_id, username=message.username
            )

            if linked_player:
                return AgentResponse(
                    success=True,
                    message=f"✅ Successfully linked to your player record: {linked_player.full_name} ({linked_player.player_id})",
                    error=None,
                )
            else:
                return AgentResponse(
                    success=False,
                    message="❌ No player record found with that phone number. Please contact team leadership.",
                    error="No matching player record",
                )

        except Exception as e:
            logger.error(f"AgenticMessageRouter contact share failed: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error linking account. Please try again or contact team leadership.",
                error=str(e),
            )

    def _get_unregistered_user_message(self, chat_type: ChatType, username: str) -> str:
        """Get message for unregistered users based on chat type."""
        from kickai.core.constants import BOT_VERSION

        if chat_type == ChatType.LEADERSHIP:
            return f"""👋 Welcome to KICKAI Leadership for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🤔 You're not registered as a team member yet.

📞 Contact Team Administrator
You need to be added as a team member by the team administrator.

💡 What to do:
1. Contact the team administrator
2. Ask them to add you as a team member using the /addmember command
3. They'll send you an invite link to join the leadership chat
4. Once added, you can access leadership functions

❓ Got here by mistake?
If you're not part of the team leadership, please leave this chat.

Need help? Contact the team administrator."""
        else:
            return f"""👋 Welcome to KICKAI for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🤔 You're not registered as a player yet.

📞 Contact Team Leadership
You need to be added as a player by someone in the team's leadership.

💬 What to do:
1. Reach out to someone in the team's leadership chat
2. Ask them to add you as a player using the /addplayer command
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
                    player = await player_service.get_player_by_telegram_id(
                        message.user_id, message.team_id
                    )
                    is_player = player is not None
                except Exception:
                    pass

            if team_service:
                try:
                    team_member = await team_service.get_team_member_by_telegram_id(
                        message.team_id, message.user_id
                    )
                    is_team_member = team_member is not None
                except Exception:
                    pass

            # SIMPLIFIED LOGIC: Chat type determines user type
            if message.chat_type == ChatType.MAIN:
                # In main chat, treat as player
                is_registered = is_player
                is_team_member = False  # Force team member to False in main chat
                logger.info(
                    f"🔄 AgenticMessageRouter: Main chat - treating as player, is_player={is_player}, is_registered={is_registered}"
                )
            elif message.chat_type == ChatType.LEADERSHIP:
                # In leadership chat, treat as team member
                is_registered = is_team_member
                is_player = False  # Force player to False in leadership chat
                logger.info(
                    f"🔄 AgenticMessageRouter: Leadership chat - treating as team member, is_team_member={is_team_member}, is_registered={is_registered}"
                )
            else:
                # Unknown chat type, assume unregistered
                is_registered = False
                is_player = False
                is_team_member = False
                logger.warning(
                    f"⚠️ AgenticMessageRouter: Unknown chat type {message.chat_type}, assuming unregistered"
                )

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
                is_team_member=is_team_member,
            )

            # Convert to execution context for backward compatibility
            execution_context = standardized_context.to_dict()
            execution_context.update(
                {
                    "chat_type": message.chat_type.value,  # Add chat_type for simplified logic
                    "is_leadership_chat": message.chat_type == ChatType.LEADERSHIP,
                    "is_main_chat": message.chat_type == ChatType.MAIN,
                }
            )

            logger.info(
                f"🔄 AgenticMessageRouter: User registration status - is_registered={is_registered}, is_player={is_player}, is_team_member={is_team_member}"
            )

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
                    execution_context=execution_context,
                )
                return AgentResponse(message=result)

        except Exception as e:
            logger.error(f"❌ Error routing to specialized agent: {e}")
            return AgentResponse(
                message="I encountered an error processing your request. Please try again.",
                success=False,
                error=str(e),
            )

    def convert_telegram_update_to_message(
        self, update: Any, command_name: str = None
    ) -> TelegramMessage:
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
                args = (
                    update.message.text.split()[1:] if len(update.message.text.split()) > 1 else []
                )
                text = f"{command_name} {' '.join(args)}".strip()
            else:
                # For natural language, use the message text
                text = update.message.text.strip()

            # Extract contact information if available
            contact_phone = None
            contact_user_id = None
            if hasattr(update.message, "contact") and update.message.contact:
                contact_phone = update.message.contact.phone_number
                contact_user_id = (
                    str(update.message.contact.user_id)
                    if update.message.contact.user_id
                    else user_id
                )

            return TelegramMessage(
                user_id=user_id,
                chat_id=chat_id,
                chat_type=chat_type,
                username=username,
                team_id=self.team_id,
                text=text,
                raw_update=update,
                contact_phone=contact_phone,
                contact_user_id=contact_user_id,
            )

        except Exception as e:
            logger.error(f"❌ Error converting Telegram update to message: {e}")
            raise

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Determine the chat type based on chat ID."""
        # Use configured chat IDs if available
        if hasattr(self, "main_chat_id") and hasattr(self, "leadership_chat_id"):
            return self._determine_chat_type_with_ids(chat_id)

        # Fallback to simple heuristic
        if chat_id.startswith("-100"):
            # Group chat - we'd need to know which is main vs leadership
            # This should be configured in the router
            return ChatType.MAIN  # Default to main chat
        else:
            return ChatType.PRIVATE

    def set_chat_ids(self, main_chat_id: str, leadership_chat_id: str):
        """Set the chat IDs for proper chat type determination."""
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id

    def _looks_like_phone_number(self, text: str) -> bool:
        """Check if text looks like a phone number."""
        if not text or len(text.strip()) < 10:
            return False

        # Remove common separators and check if it's mostly digits
        cleaned = "".join(c for c in text if c.isdigit() or c in "+()-")

        # Must have at least 10 digits
        digit_count = sum(1 for c in cleaned if c.isdigit())
        if digit_count < 10:
            return False

        # Must start with + or be all digits
        if (
            cleaned.startswith("+")
            or cleaned.replace("+", "").replace("-", "").replace("(", "").replace(")", "").isdigit()
        ):
            return True

        return False

    async def _handle_phone_number_from_unregistered_user(
        self, message: TelegramMessage
    ) -> AgentResponse:
        """Handle phone number input from unregistered users."""
        try:
            logger.info(f"📱 Processing phone number from unregistered user: {message.username}")

            # Use the phone linking service to link the user
            from kickai.features.player_registration.domain.services.player_linking_service import (
                PlayerLinkingService,
            )

            linking_service = PlayerLinkingService(self.team_id)

            # Attempt to link the user
            linked_player = await linking_service.link_telegram_user_by_phone(
                phone=message.text.strip(), telegram_id=message.user_id, username=message.username
            )

            if linked_player:
                return AgentResponse(
                    success=True,
                    message=f"✅ Successfully linked to your player record: {linked_player.full_name} ({linked_player.player_id})\n\n🎉 Welcome to the team! You can now use all team features.",
                    error=None,
                )
            else:
                return AgentResponse(
                    success=False,
                    message="❌ No player record found with that phone number.\n\n💡 **What to do:**\n1. Make sure you were added by team leadership using /addplayer\n2. Check that the phone number matches what was used when you were added\n3. Contact team leadership if you need help",
                    error="No matching player record",
                )

        except Exception as e:
            logger.error(f"❌ Error processing phone number from unregistered user: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your phone number. Please try again or contact team leadership.",
                error=str(e),
            )

    def _determine_chat_type_with_ids(self, chat_id: str) -> ChatType:
        """Determine chat type using configured chat IDs."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.PRIVATE

    def _is_helper_command(self, command: str) -> bool:
        """
        Check if a command is a helper system command.

        Args:
            command: The command to check

        Returns:
            True if it's a helper command, False otherwise
        """
        # Helper system is now proactive - no command-driven interactions
        return False

    async def route_help_request(self, message: TelegramMessage) -> AgentResponse:
        """
        Route help requests to the Helper Agent using CrewAI tasks.

        Args:
            message: The Telegram message containing the help request

        Returns:
            AgentResponse with the helper's response
        """
        try:
            logger.info("🔄 AgenticMessageRouter: Routing help request to Helper Agent")

            # Extract the query from the message
            query = message.text
            if query.startswith("/"):
                # Remove the command and get the rest as the query
                parts = query.split(" ", 1)
                if len(parts) > 1:
                    query = parts[1]
                else:
                    query = "general help"

            # Create context for the helper agent
            context = {
                "user_id": message.user_id,
                "team_id": self.team_id,
                "chat_type": message.chat_type.value,
                "username": message.username,
                "query": query,
            }

            # Execute help task using the task manager
            response = await self.helper_agent.execute_help_task(
                user_query=query, user_id=message.user_id, team_id=self.team_id, context=context
            )

            return AgentResponse(success=True, message=response, error=None)

        except Exception as e:
            logger.error(f"❌ Error routing help request: {e}")
            return AgentResponse(
                success=False,
                message="❌ Sorry, I encountered an error while helping you. Please try again.",
                error=str(e),
            )

    async def send_proactive_suggestions(self, user_id: str, team_id: str) -> None:
        """
        Send proactive suggestions based on user behavior.

        Args:
            user_id: The user's ID
            team_id: The team's ID
        """
        try:
            # Get the reminder service using the new interface
            from kickai.core.dependency_container import get_container

            container = get_container()
            reminder_service = container.get_service("IReminderService")

            if reminder_service:
                # Schedule periodic reminders
                await reminder_service.schedule_periodic_reminders(user_id, team_id)

        except Exception as e:
            logger.error(f"Error sending proactive suggestions to user {user_id}: {e}")

    async def check_and_send_reminders(self, user_id: str, team_id: str) -> None:
        """
        Check and send pending reminders for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
        """
        try:
            # Get the reminder service using the new interface
            from kickai.core.dependency_container import get_container

            container = get_container()
            reminder_service = container.get_service("IReminderService")

            if reminder_service:
                # Get pending reminders
                reminders = await reminder_service.get_pending_reminders(user_id, team_id)

                # Send reminders (in a full implementation, this would send via Telegram)
                for reminder in reminders:
                    logger.info(f"Sending reminder to user {user_id}: {reminder.title}")
                    # TODO: Implement actual Telegram message sending

        except Exception as e:
            logger.error(f"Error checking reminders for user {user_id}: {e}")

    def _get_unrecognized_command_message(self, command: str, chat_type: ChatType) -> str:
        """Get a courteous message for unrecognized commands."""
        if chat_type == ChatType.LEADERSHIP:
            return f"""🤔 I don't recognize the command `{command}` in the leadership chat.

📋 Available commands in leadership chat:
• /help - Show all available commands
• /addplayer - Add a new player
• /addmember - Add a team member
• /approve - Approve a player
• /reject - Reject a player
• /pending - List pending approvals
• /list - List all players and members
• /update - Update your team member information
• /myinfo - View your information
• /status - Check player/team member status

💡 Need help? Try /help to see all available commands."""
        else:  # Main chat
            return f"""🤔 I don't recognize the command `{command}` in the main chat.

📋 Available commands in main chat:
• /help - Show all available commands
• /myinfo - View your player information
• /status - Check your status
• /list - List active players
• /update - Update your player information

💡 Need help? Try /help to see all available commands."""

    def _is_new_chat_members_event(self, raw_update) -> bool:
        """
        Check if the raw update contains a new_chat_members event.
        
        Args:
            raw_update: Raw update data from Telegram or mock service
            
        Returns:
            True if this is a new_chat_members event, False otherwise
        """
        try:
            # Check for mock Telegram format
            if isinstance(raw_update, dict):
                # Mock telegram format
                if raw_update.get("type") == "new_chat_members":
                    return True
                # Check for new_chat_members field in message
                if "new_chat_members" in raw_update:
                    return True
                    
            # Check for real Telegram format
            if hasattr(raw_update, 'message') and raw_update.message:
                if hasattr(raw_update.message, 'new_chat_members') and raw_update.message.new_chat_members:
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking for new_chat_members event: {e}")
            return False

    async def route_new_chat_members(self, message: TelegramMessage) -> AgentResponse:
        """
        Route new chat members events for invite link processing.
        
        Args:
            message: Telegram message containing new_chat_members event
            
        Returns:
            AgentResponse with the processing result
        """
        try:
            logger.info("🔗 Processing new_chat_members event for invite link validation")
            
            # Extract new members from the update
            new_members = self._extract_new_members(message.raw_update)
            if not new_members:
                logger.warning("⚠️ No new members found in new_chat_members event")
                return AgentResponse(
                    success=False,
                    message="No new members found in event",
                    error="No new members"
                )
            
            # Process each new member (usually just one for invite links)
            for member in new_members:
                user_id = str(member.get("id", 0))
                username = member.get("username") or member.get("first_name", "Unknown")
                
                logger.info(f"🔗 Processing new member: {username} (ID: {user_id})")
                
                # Extract invite link information
                invite_link = self._extract_invite_link_from_event(message.raw_update)
                invite_id = self._extract_invite_id_from_event(message.raw_update)
                
                if invite_id:
                    logger.info(f"🔗 Found invite_id in event: {invite_id}")
                    # Process invite link validation
                    return await self._process_invite_link_validation(
                        invite_id=invite_id,
                        invite_link=invite_link,
                        user_id=user_id,
                        username=username,
                        chat_id=message.chat_id,
                        chat_type=message.chat_type
                    )
                else:
                    logger.info("🔗 No invite context found, treating as regular new member")
                    # Regular new member welcome (no invite link)
                    return await self._handle_regular_new_member(
                        user_id=user_id,
                        username=username,
                        chat_type=message.chat_type
                    )
            
            # Fallback response
            return AgentResponse(
                success=True,
                message="👋 Welcome to the team!",
                error=None
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing new_chat_members event: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your join. Please contact team leadership.",
                error=str(e)
            )

    def _extract_new_members(self, raw_update) -> list:
        """Extract new members from the raw update."""
        try:
            # Mock Telegram format
            if isinstance(raw_update, dict):
                if "new_chat_members" in raw_update:
                    return raw_update["new_chat_members"]
                    
            # Real Telegram format
            if hasattr(raw_update, 'message') and raw_update.message:
                if hasattr(raw_update.message, 'new_chat_members'):
                    members = raw_update.message.new_chat_members
                    # Convert Telegram User objects to dict format
                    if members:
                        return [
                            {
                                "id": member.id,
                                "username": member.username,
                                "first_name": member.first_name,
                                "last_name": member.last_name
                            }
                            for member in members
                        ]
                        
            return []
            
        except Exception as e:
            logger.error(f"❌ Error extracting new members: {e}")
            return []

    def _extract_invite_link_from_event(self, raw_update) -> str | None:
        """Extract invite link from the event if available."""
        try:
            # Mock format may have invitation_context
            if isinstance(raw_update, dict):
                invitation_context = raw_update.get("invitation_context", {})
                if invitation_context:
                    return invitation_context.get("invite_link")
                    
            # For real Telegram, we'd need to store the invite link differently
            # This is a limitation of the Telegram API - we can't get the specific invite link used
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting invite link: {e}")
            return None

    def _extract_invite_id_from_event(self, raw_update) -> str | None:
        """Extract invite ID from the event."""
        try:
            # Mock format with invitation_context
            if isinstance(raw_update, dict):
                invitation_context = raw_update.get("invitation_context", {})
                if invitation_context:
                    invite_id = invitation_context.get("invite_id")
                    if invite_id:
                        logger.info(f"🔗 Found invitation context with invite_id: {invite_id}")
                        return invite_id
                        
                # Fallback to check _invitation_data (backup field)
                if hasattr(raw_update, '_invitation_data'):
                    invitation_data = getattr(raw_update, '_invitation_data', {})
                    invite_id = invitation_data.get("invite_id")
                    if invite_id:
                        logger.info(f"🔗 Found backup invitation data with invite_id: {invite_id}")
                        return invite_id
                        
            logger.warning("⚠️ No invitation context found, using default invite_id")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting invite ID: {e}")
            return None

    async def _process_invite_link_validation(
        self,
        invite_id: str,
        invite_link: str | None,
        user_id: str,
        username: str,
        chat_id: str,
        chat_type: ChatType
    ) -> AgentResponse:
        """Process invite link validation and player linking."""
        try:
            logger.info(f"🔗 Processing invitation link - invite_id: {invite_id}, user_id: {user_id}, chat_type: {chat_type.value}")
            
            # Get invite link service
            from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
            from kickai.core.dependency_container import get_container
            
            container = get_container()
            database = container.get_database()
            
            invite_service = InviteLinkService(database=database)
            
            # Validate and use the invite link (pass invite_id as invite_link for direct lookup)
            invite_data = await invite_service.validate_and_use_invite_link(
                invite_link=invite_id,  # Pass invite_id directly
                user_id=user_id,
                username=username,
                secure_data=None
            )
            
            if not invite_data:
                logger.warning(f"❌ Invalid or expired invite link: {invite_id}")
                return AgentResponse(
                    success=False,
                    message="❌ Invalid or expired invite link. Please contact team leadership for a new invitation.",
                    error="Invalid invite link"
                )
            
            # Extract player information from invite
            player_phone = invite_data.get("player_phone")
            player_name = invite_data.get("player_name")
            member_phone = invite_data.get("member_phone")
            member_name = invite_data.get("member_name")
            
            # Determine if this is a player or team member invite
            if player_phone and player_name:
                return await self._process_player_invite_link(
                    player_phone=player_phone,
                    player_name=player_name,
                    user_id=user_id,
                    username=username,
                    invite_data=invite_data
                )
            elif member_phone and member_name:
                return await self._process_team_member_invite_link(
                    member_phone=member_phone,
                    member_name=member_name,
                    user_id=user_id,
                    username=username,
                    invite_data=invite_data
                )
            else:
                logger.warning(f"⚠️ Invite data missing required fields: {invite_data}")
                return AgentResponse(
                    success=False,
                    message="❌ Invalid invite data. Please contact team leadership.",
                    error="Missing invite data fields"
                )
                
        except Exception as e:
            logger.error(f"❌ Error processing invite link validation: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your invitation. Please contact team leadership.",
                error=str(e)
            )

    async def _process_player_invite_link(
        self,
        player_phone: str,
        player_name: str,
        user_id: str,
        username: str,
        invite_data: dict
    ) -> AgentResponse:
        """Process player invite link and link the user."""
        try:
            # Use PlayerLinkingService to link the user
            from kickai.features.player_registration.domain.services.player_linking_service import PlayerLinkingService
            
            linking_service = PlayerLinkingService(self.team_id)
            
            # Link the user by phone number
            linked_player = await linking_service.link_telegram_user_by_phone(
                phone=player_phone,
                telegram_id=user_id,
                username=username
            )
            
            if linked_player:
                logger.info(f"✅ Successfully linked player {player_name} to user {user_id}")
                return AgentResponse(
                    success=True,
                    message=f"🎉 Welcome to the team, {player_name}!\n\n✅ Your Telegram account has been successfully linked to your player record.\n\n⚽ You can now use all team features. Try /help to see what you can do!",
                    error=None
                )
            else:
                logger.warning(f"❌ Failed to link player {player_name} to user {user_id}")
                return AgentResponse(
                    success=False,
                    message=f"❌ Unable to link your account to the player record for {player_name}.\n\n📞 Please contact team leadership for assistance.",
                    error="Player linking failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Error processing player invite: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error linking your player account. Please contact team leadership.",
                error=str(e)
            )

    async def _process_team_member_invite_link(
        self,
        member_phone: str,
        member_name: str,
        user_id: str,
        username: str,
        invite_data: dict
    ) -> AgentResponse:
        """Process team member invite link and link the user."""
        try:
            # TODO: Implement team member linking service
            # For now, provide a basic welcome message
            logger.info(f"🔗 Processing team member invite for {member_name}")
            
            return AgentResponse(
                success=True,
                message=f"👋 Welcome to the leadership team, {member_name}!\n\n✅ You have joined the leadership chat.\n\n📋 You can now manage team operations. Try /help to see available commands.",
                error=None
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing team member invite: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your team member invitation. Please contact the team administrator.",
                error=str(e)
            )

    async def _handle_regular_new_member(
        self,
        user_id: str,
        username: str,
        chat_type: ChatType
    ) -> AgentResponse:
        """Handle new members who joined without an invite link."""
        try:
            if chat_type == ChatType.MAIN:
                return AgentResponse(
                    success=True,
                    message=f"👋 Welcome to the team, {username}!\n\n🤔 I notice you joined without an invite link. Please contact team leadership to get properly registered as a player.",
                    error=None
                )
            elif chat_type == ChatType.LEADERSHIP:
                return AgentResponse(
                    success=True,
                    message=f"👋 Welcome to the leadership chat, {username}!\n\n🤔 I notice you joined without an invite link. Please contact the team administrator to get properly registered as a team member.",
                    error=None
                )
            else:
                return AgentResponse(
                    success=True,
                    message=f"👋 Welcome, {username}!",
                    error=None
                )
                
        except Exception as e:
            logger.error(f"❌ Error handling regular new member: {e}")
            return AgentResponse(
                success=True,
                message=f"👋 Welcome, {username}!",
                error=None
            )
