#!/usr/bin/env python3
"""
Registration Agent

This module provides a CrewAI agent for handling player and team member registration workflows.
"""

import re

from crewai import Agent
from loguru import logger

from kickai.agents.base_agent import BaseAgent
from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.registration_service import (
    RegistrationService,
)


class RegistrationAgent(BaseAgent):
    """CrewAI agent for handling registration workflows."""

    def __init__(self, team_id: str):
        super().__init__()
        self.team_id = team_id
        self.registration_service = self._get_registration_service()

    def _get_registration_service(self) -> RegistrationService:
        """Get registration service from dependency container."""
        try:
            container = get_container()
            return container.get_singleton(RegistrationService)
        except Exception as e:
            logger.error(f"❌ Failed to get registration service: {e}")
            raise

    def create_agent(self) -> Agent:
        """Create the CrewAI agent."""
        return Agent(
            role="Registration Specialist",
            goal="Handle player and team member registration workflows efficiently and accurately",
            backstory="""You are a specialized registration agent for the KICKAI football team management system. 
            You handle all aspects of player and team member registration including creating pending registrations, 
            completing registrations, and managing approval workflows. You ensure data accuracy and provide 
            clear, helpful responses to users.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.create_pending_player_tool,
                self.create_pending_team_member_tool,
                self.complete_player_registration_tool,
                self.complete_team_member_registration_tool,
                self.approve_player_tool,
                self.reject_player_tool,
                self.get_pending_players_tool,
                self.get_pending_team_members_tool,
            ],
        )

    async def process_registration_command(self, command: str, user_id: int, username: str) -> str:
        """
        Process registration commands.

        Args:
            command: The registration command
            user_id: User's Telegram ID
            username: User's Telegram username

        Returns:
            Response message
        """
        try:
            # Parse command
            if command.startswith("/addplayer"):
                return await self._handle_addplayer_command(command, username)
            elif command.startswith("/addmember"):
                return await self._handle_addmember_command(command, username)
            elif command.startswith("/register"):
                return await self._handle_register_command(command, user_id, username)
            elif command.startswith("/approve"):
                return await self._handle_approve_command(command, username)
            elif command.startswith("/reject"):
                return await self._handle_reject_command(command, username)
            else:
                return "❌ Unknown registration command. Use /help for available commands."

        except Exception as e:
            logger.error(f"❌ Error processing registration command: {e}")
            return f"❌ Error processing command: {e!s}"

    async def _handle_addplayer_command(self, command: str, username: str) -> str:
        """Handle /addplayer command."""
        try:
            # Parse command: /addplayer [name] [phone] [position]
            pattern = r'/addplayer\s+([^\s]+(?:\s+[^\s]+)*)\s+(\+?\d+)\s+([^\s]+)'
            match = re.match(pattern, command)

            if not match:
                return f"""❌ Invalid Command Format

👋 Hello {username}!

❌ Error: Invalid /addplayer command format.

✅ Correct Format:
`/addplayer [Full Name] [Phone Number] [Position]`

📝 Examples:
• `/addplayer John Doe +1234567890 Forward`
• `/addplayer Jane Smith +1234567891 Midfielder`
• `/addplayer Bob Wilson +1234567892 Defender`

💬 Need Help?
Use /help to see all available commands."""

            name = match.group(1).strip()
            phone = match.group(2).strip()
            position = match.group(3).strip()

            # Create pending player
            result = await self.registration_service.create_pending_player(
                name=name,
                phone=phone,
                position=position,
                invited_by=username
            )

            return f"""✅ Player Added Successfully

👋 Hello {username}!

✅ Player Registration Complete

👤 Player Details:
• Name: {result['name']}
• Phone: {result['phone']}
• Position: {result['position']}
• Status: Pending Approval

🔗 Invite Link Generated:
`{result['invite_link']}`

📱 Next Steps:
1. Send the invite link to {result['name']}
2. Player clicks the link to join the chat
3. Player uses /register {result['phone']} to complete registration
4. Use /approve {result['player_id']} to approve the player

💬 Need Help?
Use /help to see all available commands."""

        except ValueError as e:
            return f"""❌ Registration Error

👋 Hello {username}!

❌ Error: {e!s}

💬 Need Help?
Use /help to see all available commands."""

        except Exception as e:
            logger.error(f"❌ Error in addplayer command: {e}")
            return f"""❌ System Error

👋 Hello {username}!

❌ Error: Failed to add player. Please try again.

💬 Need Help?
Use /help to see all available commands."""

    async def _handle_addmember_command(self, command: str, username: str) -> str:
        """Handle /addmember command."""
        try:
            # Parse command: /addmember [name] [phone] [role]
            pattern = r'/addmember\s+([^\s]+(?:\s+[^\s]+)*)\s+(\+?\d+)\s+([^\s]+)'
            match = re.match(pattern, command)

            if not match:
                return f"""❌ Invalid Command Format

👋 Hello {username}!

❌ Error: Invalid /addmember command format.

✅ Correct Format:
`/addmember [Full Name] [Phone Number] [Role]`

📝 Examples:
• `/addmember Alex Manager +1234567896 team_manager`
• `/addmember Sarah Coach +1234567897 coach`
• `/addmember Mike Admin +1234567898 administrator`

💬 Need Help?
Use /help to see all available commands."""

            name = match.group(1).strip()
            phone = match.group(2).strip()
            role = match.group(3).strip()

            # Create pending team member
            result = await self.registration_service.create_pending_team_member(
                name=name,
                phone=phone,
                role=role,
                invited_by=username
            )

            return f"""✅ Team Member Added Successfully

👋 Hello {username}!

✅ Team Member Registration Complete

👤 Member Details:
• Name: {result['name']}
• Phone: {result['phone']}
• Role: {result['role']}
• Status: Pending Approval

🔗 Invite Link Generated:
`{result['invite_link']}`

📱 Next Steps:
1. Send the invite link to {result['name']}
2. Member clicks the link to join the leadership chat
3. Member uses /register {result['phone']} to complete registration

💬 Need Help?
Use /help to see all available commands."""

        except ValueError as e:
            return f"""❌ Registration Error

👋 Hello {username}!

❌ Error: {e!s}

💬 Need Help?
Use /help to see all available commands."""

        except Exception as e:
            logger.error(f"❌ Error in addmember command: {e}")
            return f"""❌ System Error

👋 Hello {username}!

❌ Error: Failed to add team member. Please try again.

💬 Need Help?
Use /help to see all available commands."""

    async def _handle_register_command(self, command: str, user_id: int, username: str) -> str:
        """Handle /register command."""
        try:
            # Parse command: /register [phone]
            pattern = r'/register\s+(\+?\d+)'
            match = re.match(pattern, command)

            if not match:
                return f"""❌ Invalid Command Format

👋 Hello {username}!

❌ Error: Invalid /register command format.

✅ Correct Format:
`/register [Phone Number]`

📝 Examples:
• `/register +1234567890`
• `/register 1234567890`

💬 Need Help?
Use /help to see all available commands."""

            phone = match.group(1).strip()

            # Try to complete player registration first
            try:
                result = await self.registration_service.complete_player_registration(
                    phone=phone,
                    telegram_id=user_id,
                    telegram_username=username
                )

                return f"""✅ Registration Complete

👋 Hello {username}!

✅ Player Registration Successful

👤 Your Details:
• Name: {result['name']}
• Phone: {result['phone']}
• Position: {result['position']}
• Status: Active

🎯 You can now use all available commands!

💬 Need Help?
Use /help to see all available commands."""

            except ValueError:
                # Try team member registration
                try:
                    result = await self.registration_service.complete_team_member_registration(
                        phone=phone,
                        telegram_id=user_id,
                        telegram_username=username
                    )

                    return f"""✅ Registration Complete

👋 Hello {username}!

✅ Team Member Registration Successful

👤 Your Details:
• Name: {result['name']}
• Phone: {result['phone']}
• Role: {result['role']}
• Status: Active

🎯 You can now use all available commands!

💬 Need Help?
Use /help to see all available commands."""

                except ValueError:
                    return f"""❌ User Not Found

👋 Hello {username}!

❌ Error: No pending registration found for phone number '{phone}'.

📞 To Get Registered:
1. Contact team leadership
2. Ask them to add you using /addplayer or /addmember
3. They'll send you an invite link
4. Use the invite link to join the chat

💬 Need Help?
Use /help to see all available commands."""

        except Exception as e:
            logger.error(f"❌ Error in register command: {e}")
            return f"""❌ System Error

👋 Hello {username}!

❌ Error: Failed to complete registration. Please try again.

💬 Need Help?
Use /help to see all available commands."""

    async def _handle_approve_command(self, command: str, username: str) -> str:
        """Handle /approve command."""
        try:
            # Parse command: /approve [player_id]
            pattern = r'/approve\s+(\w+)'
            match = re.match(pattern, command)

            if not match:
                return f"""❌ Invalid Command Format

👋 Hello {username}!

❌ Error: Invalid /approve command format.

✅ Correct Format:
`/approve [Player ID]`

📝 Examples:
• `/approve PLAYER_001`
• `/approve JOHN_DOE`

💬 Need Help?
Use /help to see all available commands."""

            player_id = match.group(1).strip()

            # Approve player
            result = await self.registration_service.approve_player(
                player_id=player_id,
                approved_by=username
            )

            return f"""✅ Player Approved

👋 Hello {username}!

✅ Player Approval Successful

👤 Player Details:
• ID: {result['player_id']}
• Name: {result['name']}
• Phone: {result['phone']}
• Position: {result['position']}
• Status: Approved

📱 Next Steps:
1. Player will receive notification
2. Player can now use all player commands
3. Player appears in active players list

💬 Need Help?
Use /help to see all available commands."""

        except ValueError as e:
            return f"""❌ Approval Error

👋 Hello {username}!

❌ Error: {e!s}

💬 Need Help?
Use /help to see all available commands."""

        except Exception as e:
            logger.error(f"❌ Error in approve command: {e}")
            return f"""❌ System Error

👋 Hello {username}!

❌ Error: Failed to approve player. Please try again.

💬 Need Help?
Use /help to see all available commands."""

    async def _handle_reject_command(self, command: str, username: str) -> str:
        """Handle /reject command."""
        try:
            # Parse command: /reject [player_id] [reason]
            pattern = r'/reject\s+(\w+)(?:\s+(.+))?'
            match = re.match(pattern, command)

            if not match:
                return f"""❌ Invalid Command Format

👋 Hello {username}!

❌ Error: Invalid /reject command format.

✅ Correct Format:
`/reject [Player ID] [Reason]`

📝 Examples:
• `/reject PLAYER_001`
• `/reject PLAYER_001 Insufficient experience`

💬 Need Help?
Use /help to see all available commands."""

            player_id = match.group(1).strip()
            reason = match.group(2) or "No reason provided"

            # Reject player
            result = await self.registration_service.reject_player(
                player_id=player_id,
                rejected_by=username,
                reason=reason
            )

            return f"""❌ Player Rejected

👋 Hello {username}!

❌ Player Rejection Successful

👤 Player Details:
• ID: {result['player_id']}
• Name: {result['name']}
• Phone: {result['phone']}
• Position: {result['position']}
• Status: Rejected

📝 Rejection Reason:
{reason}

📱 Next Steps:
1. Player will receive rejection notification
2. Player record removed from pending list
3. Player can reapply if needed

💬 Need Help?
Use /help to see all available commands."""

        except ValueError as e:
            return f"""❌ Rejection Error

👋 Hello {username}!

❌ Error: {e!s}

💬 Need Help?
Use /help to see all available commands."""

        except Exception as e:
            logger.error(f"❌ Error in reject command: {e}")
            return f"""❌ System Error

👋 Hello {username}!

❌ Error: Failed to reject player. Please try again.

💬 Need Help?
Use /help to see all available commands."""

    # CrewAI Tools
    async def create_pending_player_tool(self, name: str, phone: str, position: str, invited_by: str) -> str:
        """Create a pending player registration."""
        try:
            result = await self.registration_service.create_pending_player(
                name=name,
                phone=phone,
                position=position,
                invited_by=invited_by
            )
            return f"✅ Created pending player {result['player_id']} with invite link: {result['invite_link']}"
        except Exception as e:
            return f"❌ Failed to create pending player: {e!s}"

    async def create_pending_team_member_tool(self, name: str, phone: str, role: str, invited_by: str) -> str:
        """Create a pending team member registration."""
        try:
            result = await self.registration_service.create_pending_team_member(
                name=name,
                phone=phone,
                role=role,
                invited_by=invited_by
            )
            return f"✅ Created pending team member {result['member_id']} with invite link: {result['invite_link']}"
        except Exception as e:
            return f"❌ Failed to create pending team member: {e!s}"

    async def complete_player_registration_tool(self, phone: str, telegram_id: int, telegram_username: str) -> str:
        """Complete player registration by linking Telegram account."""
        try:
            result = await self.registration_service.complete_player_registration(
                phone=phone,
                telegram_id=telegram_id,
                telegram_username=telegram_username
            )
            return f"✅ Completed player registration for {result['player_id']}"
        except Exception as e:
            return f"❌ Failed to complete player registration: {e!s}"

    async def complete_team_member_registration_tool(self, phone: str, telegram_id: int, telegram_username: str) -> str:
        """Complete team member registration by linking Telegram account."""
        try:
            result = await self.registration_service.complete_team_member_registration(
                phone=phone,
                telegram_id=telegram_id,
                telegram_username=telegram_username
            )
            return f"✅ Completed team member registration for {result['member_id']}"
        except Exception as e:
            return f"❌ Failed to complete team member registration: {e!s}"

    async def approve_player_tool(self, player_id: str, approved_by: str) -> str:
        """Approve a pending player."""
        try:
            result = await self.registration_service.approve_player(
                player_id=player_id,
                approved_by=approved_by
            )
            return f"✅ Approved player {result['player_id']}"
        except Exception as e:
            return f"❌ Failed to approve player: {e!s}"

    async def reject_player_tool(self, player_id: str, rejected_by: str, reason: str) -> str:
        """Reject a pending player."""
        try:
            result = await self.registration_service.reject_player(
                player_id=player_id,
                rejected_by=rejected_by,
                reason=reason
            )
            return f"❌ Rejected player {result['player_id']}: {reason}"
        except Exception as e:
            return f"❌ Failed to reject player: {e!s}"

    async def get_pending_players_tool(self) -> str:
        """Get all pending players."""
        try:
            players = await self.registration_service.get_pending_players()
            if not players:
                return "No pending players found."

            player_list = "\n".join([
                f"• {p['player_id']}: {p['name']} ({p['phone']}) - {p['position']}"
                for p in players
            ])
            return f"Pending players:\n{player_list}"
        except Exception as e:
            return f"❌ Failed to get pending players: {e!s}"

    async def get_pending_team_members_tool(self) -> str:
        """Get all pending team members."""
        try:
            members = await self.registration_service.get_pending_team_members()
            if not members:
                return "No pending team members found."

            member_list = "\n".join([
                f"• {m['member_id']}: {m['name']} ({m['phone']}) - {m['role']}"
                for m in members
            ])
            return f"Pending team members:\n{member_list}"
        except Exception as e:
            return f"❌ Failed to get pending team members: {e!s}"
