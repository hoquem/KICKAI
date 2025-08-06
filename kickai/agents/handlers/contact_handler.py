"""
Contact handler for processing Telegram contact sharing.

This handler extracts contact sharing logic from AgenticMessageRouter,
implementing single responsibility principle.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from kickai.core.enums import ChatType
from kickai.core.interfaces import IAgentResponse, IContactHandler, IPlayerService, ITeamService
from kickai.core.value_objects import EntityContext, PhoneNumber


class AgentResponse:
    """Simple agent response implementation."""

    def __init__(self, content: str, metadata: dict = None):
        self._content = content
        self._metadata = metadata or {}

    @property
    def content(self) -> str:
        return self._content

    @property
    def metadata(self) -> dict:
        return self._metadata


class ContactHandler(IContactHandler):
    """
    Handles contact sharing operations from Telegram.

    This class is responsible for:
    - Processing contact data from Telegram
    - Validating contact information
    - Determining registration type (player vs team member)
    - Delegating to appropriate services
    """

    def __init__(
        self,
        player_service: IPlayerService,
        team_service: ITeamService,
        team_id: str
    ):
        self.player_service = player_service
        self.team_service = team_service
        self.team_id = team_id

    async def handle_contact_share(
        self,
        contact_data: dict[str, Any],
        context: EntityContext
    ) -> IAgentResponse:
        """
        Handle contact sharing from Telegram.

        Args:
            contact_data: Contact information from Telegram
            context: Entity context

        Returns:
            Response to contact sharing
        """
        try:
            if not self.validate_contact_data(contact_data):
                return self._create_invalid_contact_response()

            # Extract contact information
            first_name = contact_data.get('first_name', '').strip()
            last_name = contact_data.get('last_name', '').strip()
            phone_number = contact_data.get('phone_number', '').strip()

            # Combine name
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                return self._create_missing_name_response()

            # Validate and create phone number
            try:
                phone = PhoneNumber.from_string(phone_number)
            except ValueError as e:
                return self._create_invalid_phone_response(str(e))

            # Determine registration type based on chat context
            registration_type = self._determine_registration_type(context)

            # Delegate to appropriate service
            if registration_type == "player":
                return await self._handle_player_registration(
                    full_name, phone, context
                )
            elif registration_type == "team_member":
                return await self._handle_team_member_registration(
                    full_name, phone, context
                )
            else:
                return await self._handle_ambiguous_registration(
                    full_name, phone, context
                )

        except Exception as e:
            logger.error(f"Error handling contact share: {e}")
            return AgentResponse(
                content="❌ Sorry, I encountered an error processing your contact. Please try again.",
                metadata={"error": str(e), "operation": "contact_share"}
            )

    def validate_contact_data(self, contact_data: dict[str, Any]) -> bool:
        """
        Validate contact data structure.

        Args:
            contact_data: Contact data to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(contact_data, dict):
            return False

        # Must have phone number
        phone = contact_data.get('phone_number')
        if not phone or not isinstance(phone, str) or not phone.strip():
            return False

        # Must have at least first name
        first_name = contact_data.get('first_name')
        if not first_name or not isinstance(first_name, str) or not first_name.strip():
            return False

        return True

    def _determine_registration_type(self, context: EntityContext) -> str:
        """Determine registration type based on context."""
        if context.chat_type == ChatType.LEADERSHIP:
            # In leadership chat, assume team member registration
            return "team_member"
        elif context.chat_type == ChatType.MAIN:
            # In main chat, assume player registration
            return "player"
        else:
            # Private chat - need to ask
            return "ambiguous"

    async def _handle_player_registration(
        self,
        name: str,
        phone: PhoneNumber,
        context: EntityContext
    ) -> IAgentResponse:
        """Handle player registration."""
        try:
            # Default position - will be asked later if needed
            default_position = "Any"

            result = await self.player_service.register_player(
                name=name,
                phone=phone,
                position=default_position,
                team_id=context.team_id,
                context=context
            )

            return AgentResponse(
                content=f"""✅ **Player Registration Submitted**

**Name:** {name}
**Phone:** {phone.display_format}
**Position:** {default_position} (you can update this later)

Your registration has been submitted for approval. You'll be notified when approved!

**Next Steps:**
- Wait for approval from team leadership
- You can update your position using /update
- Type /help for available commands

Welcome to the team! ⚽""",
                metadata={
                    "operation": "player_registration",
                    "player_id": result.get("player_id"),
                    "status": "pending_approval"
                }
            )

        except Exception as e:
            logger.error(f"Error in player registration: {e}")
            return AgentResponse(
                content=f"❌ Registration failed: {e!s}",
                metadata={"error": str(e), "operation": "player_registration"}
            )

    async def _handle_team_member_registration(
        self,
        name: str,
        phone: PhoneNumber,
        context: EntityContext
    ) -> IAgentResponse:
        """Handle team member registration."""
        try:
            # Default role - will be specified later if needed
            default_role = "Member"

            result = await self.team_service.add_team_member(
                name=name,
                phone=phone,
                role=default_role,
                team_id=context.team_id,
                context=context
            )

            return AgentResponse(
                content=f"""✅ **Team Member Registration Submitted**

**Name:** {name}
**Phone:** {phone.display_format}
**Role:** {default_role} (you can update this later)

Your team member registration has been submitted!

**Next Steps:**
- You can specify your role using /update
- Type /help for available commands
- Access leadership features if applicable

Welcome to the team management! 👥""",
                metadata={
                    "operation": "team_member_registration",
                    "member_id": result.get("member_id"),
                    "status": "active"
                }
            )

        except Exception as e:
            logger.error(f"Error in team member registration: {e}")
            return AgentResponse(
                content=f"❌ Registration failed: {e!s}",
                metadata={"error": str(e), "operation": "team_member_registration"}
            )

    async def _handle_ambiguous_registration(
        self,
        name: str,
        phone: PhoneNumber,
        context: EntityContext
    ) -> IAgentResponse:
        """Handle ambiguous registration (ask user to choose)."""
        return AgentResponse(
            content=f"""👋 **Registration Started**

**Name:** {name}
**Phone:** {phone.display_format}

**Please choose your registration type:**

🏃‍♂️ **Player Registration**
Reply with: `player [position]`
Example: `player midfielder`

👥 **Team Member Registration**
Reply with: `member [role]`
Example: `member coach`

**Available Positions:** Goalkeeper, Defender, Midfielder, Forward, Any
**Available Roles:** Coach, Manager, Assistant, Coordinator, Volunteer

What would you like to register as?""",
            metadata={
                "operation": "ambiguous_registration",
                "name": name,
                "phone": str(phone),
                "next_step": "choose_type"
            }
        )

    def _create_invalid_contact_response(self) -> IAgentResponse:
        """Create response for invalid contact data."""
        return AgentResponse(
            content="""❌ **Invalid Contact Data**

The contact information appears to be incomplete or invalid.

**To register:**
1️⃣ Use the contact sharing button in Telegram
2️⃣ Make sure your contact has name and phone number
3️⃣ Try sharing your contact again

Need help? Type /help for assistance.""",
            metadata={"error": "invalid_contact_data"}
        )

    def _create_missing_name_response(self) -> IAgentResponse:
        """Create response for missing name."""
        return AgentResponse(
            content="""❌ **Name Required**

Your contact is missing a name. Please:

1️⃣ Update your Telegram profile with your name
2️⃣ Share your contact again
3️⃣ Or send your name manually

**Format:** FirstName LastName
**Example:** John Smith""",
            metadata={"error": "missing_name"}
        )

    def _create_invalid_phone_response(self, error: str) -> IAgentResponse:
        """Create response for invalid phone number."""
        return AgentResponse(
            content=f"""❌ **Invalid Phone Number**

{error}

**Valid UK phone formats:**
- +44XXXXXXXXXX
- 0XXXXXXXXXX
- 07XXXXXXXXX

Please share your contact again with a valid UK phone number.""",
            metadata={"error": "invalid_phone", "details": error}
        )
