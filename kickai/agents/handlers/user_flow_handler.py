"""
User flow handler for determining user registration status and flow.

This handler extracts user flow determination logic from AgenticMessageRouter,
implementing single responsibility principle.
"""

from __future__ import annotations

from loguru import logger

from kickai.core.enums import ChatType
from kickai.core.interfaces import IAgentResponse, IUserFlowHandler, IUserService
from kickai.core.value_objects import EntityContext


# Import centralized types
from kickai.core.types import AgentResponse


class UserFlowHandler(IUserFlowHandler):
    """
    Handles user flow determination and unregistered user processing.

    This class is responsible for:
    - Determining if a user is registered
    - Handling unregistered user messages
    - Routing to appropriate registration flows
    """

    def __init__(self, user_service: IUserService, team_id: str):
        self.user_service = user_service
        self.team_id = team_id
        self._phone_number_pattern = r"^(\+44|0)[0-9]{10}$"

    async def determine_user_flow(
        self,
        message: str,
        context: EntityContext
    ) -> str:
        """
        Determine the appropriate user flow for a message.

        Args:
            message: User message
            context: Entity context

        Returns:
            User flow identifier
        """
        try:
            # Check user registration status
            user_registration = await self.user_service.get_user_registration(
                context.user_id,
                context.team_id
            )

            if not user_registration.is_registered:
                if self._looks_like_phone_number(message):
                    return "phone_number_registration"
                elif context.chat_type == ChatType.PRIVATE:
                    return "private_chat_unregistered"
                else:
                    return "group_chat_unregistered"

            # User is registered
            if user_registration.is_player and user_registration.is_team_member:
                return "dual_role_user"
            elif user_registration.is_player:
                return "player_user"
            elif user_registration.is_team_member:
                return "team_member_user"
            else:
                return "registered_no_role"

        except Exception as e:
            logger.error(f"Error determining user flow: {e}")
            return "error_fallback"

    async def handle_unregistered_user(
        self,
        message: str,
        context: EntityContext
    ) -> IAgentResponse:
        """
        Handle messages from unregistered users.

        Args:
            message: User message
            context: Entity context

        Returns:
            Response for unregistered user
        """
        try:
            if self._looks_like_phone_number(message):
                return await self._handle_phone_number_registration(message, context)

            if context.chat_type == ChatType.PRIVATE:
                return self._create_private_chat_welcome_response(context)
            else:
                return self._create_group_chat_guidance_response(context)

        except Exception as e:
            logger.error(f"Error handling unregistered user: {e}")
            return AgentResponse(
                content="❌ Sorry, I encountered an error. Please try again later.",
                metadata={"error": str(e), "user_flow": "error"}
            )

    def _looks_like_phone_number(self, message: str) -> bool:
        """Check if message looks like a phone number."""
        import re
        # Remove spaces, dashes, and brackets
        cleaned = re.sub(r'[\s\-\(\)]', '', message.strip())

        # Check UK phone number patterns
        patterns = [
            r'^\+44[0-9]{10}$',     # +44XXXXXXXXXX
            r'^0[0-9]{10}$',        # 0XXXXXXXXXX
            r'^44[0-9]{10}$',       # 44XXXXXXXXXX
            r'^07[0-9]{9}$',        # 07XXXXXXXXX
        ]

        return any(re.match(pattern, cleaned) for pattern in patterns)

    async def _handle_phone_number_registration(
        self,
        phone_message: str,
        context: EntityContext
    ) -> IAgentResponse:
        """Handle phone number for registration."""
        # This would typically delegate to registration service
        return AgentResponse(
            content="""📱 **Phone Number Received**

Thank you for sharing your phone number! 

**Next Steps:**
1️⃣ Please share your contact using the Telegram contact button
2️⃣ Or reply with your full name for manual registration

**Format:** FirstName LastName Position
**Example:** John Smith Midfielder

Type /help for more assistance.""",
            metadata={
                "user_flow": "phone_registration",
                "phone_number": phone_message,
                "next_step": "name_required"
            }
        )

    def _create_private_chat_welcome_response(
        self,
        context: EntityContext
    ) -> IAgentResponse:
        """Create welcome response for private chat."""
        return AgentResponse(
            content="""👋 **Welcome to KICKAI!**

I'm the team management assistant. To get started:

**Option 1: Quick Registration**
Share your contact using the contact button below

**Option 2: Manual Registration**
Send your phone number in this format: +44XXXXXXXXXX

**Need Help?**
Type /help for available commands

Let's get you connected with your team! ⚽""",
            metadata={
                "user_flow": "private_welcome",
                "chat_type": "private",
                "registration_required": True
            }
        )

    def _create_group_chat_guidance_response(
        self,
        context: EntityContext
    ) -> IAgentResponse:
        """Create guidance response for group chat."""
        return AgentResponse(
            content=f"""👋 Hi there! I notice you're not registered yet.

**To register with the team:**
📱 Send me a private message to get started
🔗 Click here: @{context.username or 'the_bot_username'}

**Or register in this chat:**
Share your contact or send your phone number

Type /help for more information! ⚽""",
            metadata={
                "user_flow": "group_guidance",
                "chat_type": context.chat_type.value,
                "registration_required": True
            }
        )
