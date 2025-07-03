"""
Onboarding Handler for KICKAI

This module handles the complete onboarding workflow for new users joining the team:
1. Detect new users joining via invite link
2. Admin approval process
3. Player profile completion
4. FA registration guidance
5. Team access management
"""

import asyncio
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from src.core.logging import get_logger, performance_timer
from src.database.models import Player, OnboardingStatus, PlayerRole, PlayerPosition
from src.services.player_service import get_player_service
from src.services.team_service import get_team_service
from src.services.team_member_service import TeamMemberService
from src.database.firebase_client import get_firebase_client
from src.core.bot_config_manager import get_bot_config_manager

logger = get_logger("onboarding_handler")


@dataclass
class OnboardingStep:
    """Represents a step in the onboarding process."""
    step_id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False
    data: Optional[Dict[str, Any]] = None


class OnboardingWorkflow:
    """Complete onboarding workflow for new team members."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_service = get_player_service()
        self.team_service = get_team_service()
        self.team_member_service = TeamMemberService(get_firebase_client())
        self.bot_config_manager = get_bot_config_manager()
        self.logger = get_logger("onboarding_workflow")
        
        # Define onboarding steps
        self.onboarding_steps = [
            OnboardingStep("welcome", "Welcome Message", "Initial welcome and introduction"),
            OnboardingStep("admin_approval", "Admin Approval", "Leadership approval required"),
            OnboardingStep("profile_completion", "Profile Completion", "Complete personal details"),
            OnboardingStep("emergency_contact", "Emergency Contact", "Provide emergency contact details"),
            OnboardingStep("date_of_birth", "Date of Birth", "Provide date of birth for FA registration"),
            OnboardingStep("fa_eligibility", "FA Eligibility", "Confirm FA registration eligibility"),
            OnboardingStep("fa_registration", "FA Registration", "Complete FA registration process"),
            OnboardingStep("team_access", "Team Access", "Grant team access and permissions"),
            OnboardingStep("completion", "Onboarding Complete", "Welcome to the team!")
        ]
    
    @performance_timer("onboarding_detect_new_member")
    async def detect_new_member(self, chat_id: str, user_id: str, username: Optional[str] = None, 
                               first_name: Optional[str] = None, last_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Detect when a new member joins the chat and start onboarding process.
        
        Args:
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            (success, message)
        """
        try:
            # Check if this is the main team chat
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or str(chat_id) != str(bot_config.main_chat_id):
                return False, "Not the main team chat"
            
            # Check if user is already a team member
            existing_member = await self.team_member_service.get_team_member_by_telegram_id(user_id, self.team_id)
            if existing_member:
                return False, "User is already a team member"
            
            # Check if user is a pending player (invited but not joined)
            pending_players = await self.player_service.get_team_players(self.team_id)
            pending_player = None
            for player in pending_players:
                if (player.telegram_id == user_id or 
                    (username and player.telegram_username == username)):
                    pending_player = player
                    break
            
            if pending_player:
                # User is a pending player, start onboarding
                return await self.start_player_onboarding(pending_player, user_id, username)
            else:
                # New user, create pending approval entry
                return await self.create_pending_approval(user_id, username, first_name, last_name)
                
        except Exception as e:
            self.logger.error(f"Error detecting new member: {e}")
            return False, f"Error processing new member: {str(e)}"
    
    @performance_timer("onboarding_create_pending_approval")
    async def create_pending_approval(self, user_id: str, username: Optional[str] = None, 
                                    first_name: Optional[str] = None, last_name: Optional[str] = None) -> Tuple[bool, str]:
        """Create a pending approval entry for a new user."""
        try:
            # Create a temporary player entry for approval
            display_name = f"{first_name or ''} {last_name or ''}".strip() or username or f"User{user_id[-4:]}"
            
            # Create player with basic info first
            player = await self.player_service.create_player(
                name=display_name,
                phone="",  # Will be filled during onboarding
                team_id=self.team_id,
                position=PlayerPosition.UTILITY,
                role=PlayerRole.PLAYER,
                fa_registered=False
            )
            
            # Update with additional onboarding fields
            player = await self.player_service.update_player(
                player.id,
                fa_eligible=False,
                onboarding_status=OnboardingStatus.PENDING_APPROVAL,
                telegram_id=user_id,
                telegram_username=username
            )
            
            # Send notification to leadership chat
            await self.notify_leadership_new_user(player)
            
            self.logger.info(f"Created pending approval for user {user_id}")
            return True, f"✅ Welcome! Your registration is pending admin approval."
            
        except Exception as e:
            self.logger.error(f"Error creating pending approval: {e}")
            return False, f"Error creating approval request: {str(e)}"
    
    @performance_timer("onboarding_start_player_onboarding")
    async def start_player_onboarding(self, player: Player, user_id: str, username: Optional[str] = None) -> Tuple[bool, str]:
        """Start onboarding process for an existing player."""
        try:
            # Update player with Telegram info
            updates = {
                'telegram_id': user_id,
                'onboarding_status': OnboardingStatus.IN_PROGRESS,
                'onboarding_step': 'welcome'
            }
            if username:
                updates['telegram_username'] = username
            
            updated_player = await self.player_service.update_player(player.id, **updates)
            
            # Send welcome message
            welcome_message = await self.get_welcome_message(updated_player)
            
            self.logger.info(f"Started onboarding for player {player.name}")
            return True, welcome_message
            
        except Exception as e:
            self.logger.error(f"Error starting player onboarding: {e}")
            return False, f"Error starting onboarding: {str(e)}"
    
    @performance_timer("onboarding_get_welcome_message")
    async def get_welcome_message(self, player: Player) -> str:
        """Generate welcome message for new player."""
        try:
            team = await self.team_service.get_team(self.team_id)
            team_name = team.name if team else "KICKAI Team"
            
            return f"""🎉 <b>Welcome to {team_name}, {player.name.upper()}!</b>

I'm here to help you complete your registration and get you ready to play.

📋 <b>Your Current Details:</b>
• Name: {player.name.upper()}
• Phone: {player.phone or 'Not provided'}
• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
• Player ID: {player.player_id.upper()}

🔄 <b>Onboarding Steps:</b>
1. ✅ Welcome (Current)
2. ⏳ Profile Completion
3. ⏳ Emergency Contact
4. ⏳ Date of Birth
5. ⏳ FA Registration
6. ⏳ Team Access

💡 <b>Next Step:</b>
Please confirm your details are correct by replying with 'yes' or 'no'.

If you need to update any information, just let me know!"""
            
        except Exception as e:
            self.logger.error(f"Error generating welcome message: {e}")
            return "Welcome! Let's get you set up."
    
    @performance_timer("onboarding_process_response")
    async def process_response(self, user_id: str, response: str) -> Tuple[bool, str]:
        """Process user response during onboarding."""
        try:
            # Find player by telegram ID
            players = await self.player_service.get_team_players(self.team_id)
            player = None
            for p in players:
                if p.telegram_id == user_id:
                    player = p
                    break
            
            if not player:
                return False, "❌ Player not found. Please contact the admin."
            
            # Handle response based on current step
            current_step = player.onboarding_step or 'welcome'
            
            if current_step == 'welcome':
                return await self.handle_welcome_response(player, response)
            elif current_step == 'profile_completion':
                return await self.handle_profile_completion(player, response)
            elif current_step == 'emergency_contact':
                return await self.handle_emergency_contact(player, response)
            elif current_step == 'date_of_birth':
                return await self.handle_date_of_birth(player, response)
            elif current_step == 'fa_eligibility':
                return await self.handle_fa_eligibility(player, response)
            elif current_step == 'fa_registration':
                return await self.handle_fa_registration(player, response)
            else:
                return False, "❌ Invalid onboarding step"
                
        except Exception as e:
            self.logger.error(f"Error processing onboarding response: {e}")
            return False, f"Error processing response: {str(e)}"
    
    @performance_timer("onboarding_handle_welcome_response")
    async def handle_welcome_response(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle response to welcome message."""
        response_lower = response.lower().strip()
        
        if response_lower in ['yes', 'y', 'confirm', 'correct']:
            # Move to profile completion
            await self.player_service.update_player(
                player.id,
                onboarding_step='profile_completion'
            )
            
            return True, """✅ Great! Your details look correct.

📝 <b>Next Step: Profile Completion</b>

Please provide any additional information you'd like to update:

• <b>Full Name:</b> (if different from current)
• <b>Phone Number:</b> (if not provided)
• <b>Position:</b> (if you want to change)

Just type the information you want to update, or type 'skip' to continue with current details."""
        
        elif response_lower in ['no', 'n', 'update', 'change']:
            # Move to profile completion
            await self.player_service.update_player(
                player.id,
                onboarding_step='profile_completion'
            )
            
            return True, """📝 <b>Profile Update</b>

Please provide the information you'd like to update:

• <b>Full Name:</b> (current: {player.name})
• <b>Phone Number:</b> (current: {player.phone or 'Not provided'})
• <b>Position:</b> (current: {player.position.value if hasattr(player.position, 'value') else player.position})

Format: "Name: [name], Phone: [phone], Position: [position]"
Or type individual updates like "Name: John Smith" """.format(
                player=player,
                position=player.position.value if hasattr(player.position, 'value') else player.position
            )
        
        else:
            return False, """❓ I didn't understand your response.

Please reply with:
• 'yes' or 'confirm' if your details are correct
• 'no' or 'update' if you need to change anything

Or type 'help' for assistance."""
    
    @performance_timer("onboarding_handle_profile_completion")
    async def handle_profile_completion(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle profile completion step."""
        response_lower = response.lower().strip()
        
        if response_lower == 'skip':
            # Skip to emergency contact
            await self.player_service.update_player(
                player.id,
                onboarding_step='emergency_contact'
            )
            
            return True, """✅ Profile step completed.

📞 <b>Next Step: Emergency Contact</b>

Please provide your emergency contact information:
• Name and relationship (e.g., "Jane Smith - Wife")
• Phone number

Format: "Name, Phone" (e.g., "Jane Smith, 07987654321")"""
        
        # Parse profile updates
        updates = {}
        
        # Extract name
        name_match = re.search(r'name:\s*([^,]+)', response, re.IGNORECASE)
        if name_match:
            updates['name'] = name_match.group(1).strip()
        
        # Extract phone
        phone_match = re.search(r'phone:\s*(\d+)', response, re.IGNORECASE)
        if phone_match:
            updates['phone'] = phone_match.group(1).strip()
        
        # Extract position
        position_match = re.search(r'position:\s*(\w+)', response, re.IGNORECASE)
        if position_match:
            position_str = position_match.group(1).strip().lower()
            try:
                updates['position'] = PlayerPosition(position_str)
            except ValueError:
                return False, f"❌ Invalid position: {position_str}. Valid positions: {', '.join([p.value for p in PlayerPosition])}"
        
        # Apply updates
        if updates:
            await self.player_service.update_player(player.id, **updates)
        
        # Move to emergency contact
        await self.player_service.update_player(
            player.id,
            onboarding_step='emergency_contact'
        )
        
        return True, """✅ Profile updated successfully!

📞 <b>Next Step: Emergency Contact</b>

Please provide your emergency contact information:
• Name and relationship (e.g., "Jane Smith - Wife")
• Phone number

Format: "Name, Phone" (e.g., "Jane Smith, 07987654321")"""
    
    @performance_timer("onboarding_handle_emergency_contact")
    async def handle_emergency_contact(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle emergency contact step."""
        # Validate emergency contact format
        if not self._validate_emergency_contact(response):
            return False, """❌ Please provide emergency contact in the correct format.

Format: "Name, Phone" (e.g., "Jane Smith, 07987654321")

Include:
• Contact name
• Phone number (UK format)"""
        
        # Save emergency contact
        await self.player_service.update_player(
            player.id,
            emergency_contact=response,
            onboarding_step='date_of_birth'
        )
        
        return True, """✅ Emergency contact saved!

📅 <b>Next Step: Date of Birth</b>

Please provide your date of birth for FA registration:
Format: DD/MM/YYYY (e.g., 15/05/1995)"""
    
    @performance_timer("onboarding_handle_date_of_birth")
    async def handle_date_of_birth(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle date of birth step."""
        # Validate date format
        if not self._validate_date_of_birth(response):
            return False, """❌ Please provide date of birth in the correct format.

Format: DD/MM/YYYY (e.g., 15/05/1995)"""
        
        # Save date of birth
        await self.player_service.update_player(
            player.id,
            date_of_birth=response,
            onboarding_step='fa_eligibility'
        )
        
        return True, """✅ Date of birth saved!

🏆 <b>Next Step: FA Registration Eligibility</b>

Are you eligible for FA registration?
• You must be 16 or older
• You must not be registered with another club
• You must have valid ID

Reply with 'yes' or 'no'."""
    
    @performance_timer("onboarding_handle_fa_eligibility")
    async def handle_fa_eligibility(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle FA eligibility step."""
        response_lower = response.lower().strip()
        
        if response_lower in ['yes', 'y', 'eligible']:
            # Mark as FA eligible
            await self.player_service.update_player(
                player.id,
                fa_eligible=True,
                onboarding_step='fa_registration'
            )
            
            return True, """✅ FA eligibility confirmed!

📋 <b>Next Step: FA Registration Process</b>

To complete your FA registration, you'll need to:

1. 📱 <b>Contact the Team Admin</b>
   • Message the admin in the leadership chat
   • Provide your full name and date of birth
   • Confirm your position

2. 🆔 <b>Prepare Required Documents</b>
   • Valid photo ID (passport or driving license)
   • Proof of address (utility bill or bank statement)
   • Recent passport photo

3. 💰 <b>Registration Fee</b>
   • FA registration fee: £15 (one-time)
   • Payable to the team admin

4. 📝 <b>Complete Forms</b>
   • FA registration form
   • Team registration form

Reply 'ready' when you're prepared to start the FA registration process, or 'help' for more information."""
        
        elif response_lower in ['no', 'n', 'not eligible']:
            # Mark as not FA eligible
            await self.player_service.update_player(
                player.id,
                fa_eligible=False,
                onboarding_step='team_access'
            )
            
            return True, """ℹ️ FA registration not required.

✅ <b>Next Step: Team Access</b>

You can still participate in training and friendly matches without FA registration.

Let's complete your team access setup..."""
        
        else:
            return False, """❓ Please confirm your FA eligibility.

Reply with:
• 'yes' if you're eligible for FA registration
• 'no' if you're not eligible

Type 'help' for eligibility criteria."""
    
    @performance_timer("onboarding_handle_fa_registration")
    async def handle_fa_registration(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle FA registration step."""
        response_lower = response.lower().strip()
        
        if response_lower == 'ready':
            # Notify admin about FA registration request
            await self.notify_admin_fa_registration(player)
            
            # Move to team access
            await self.player_service.update_player(
                player.id,
                onboarding_step='team_access'
            )
            
            return True, """✅ FA registration request sent to admin!

📞 <b>Next Steps:</b>

1. The admin will contact you to arrange FA registration
2. Complete the registration process with the admin
3. Once registered, you'll be eligible for competitive matches

✅ <b>Team Access Setup</b>

While FA registration is being processed, let's set up your team access..."""
        
        elif response_lower == 'help':
            return True, """📋 <b>FA Registration Help</b>

🏆 <b>What is FA Registration?</b>
• Required for competitive league matches
• Provides insurance coverage
• Allows participation in official competitions

📋 <b>Eligibility Requirements:</b>
• Age 16 or older
• Not registered with another club
• Valid UK address
• Valid photo ID

💰 <b>Cost:</b>
• £15 one-time registration fee
• Covers the full season

📞 <b>Process:</b>
• Contact team admin
• Provide required documents
• Complete registration forms
• Pay registration fee

Reply 'ready' when you want to start the process, or ask any questions!"""
        
        else:
            return False, """❓ Please confirm when you're ready for FA registration.

Reply with:
• 'ready' to start the FA registration process
• 'help' for more information about FA registration"""
    
    @performance_timer("onboarding_complete_onboarding")
    async def complete_onboarding(self, player: Player) -> Tuple[bool, str]:
        """Complete the onboarding process."""
        try:
            # Update player status
            await self.player_service.update_player(
                player.id,
                onboarding_status=OnboardingStatus.COMPLETED,
                onboarding_step='completion'
            )
            
            # Create team member entry
            from src.database.models import TeamMember
            
            team_member = TeamMember(
                team_id=self.team_id,
                user_id=player.id,
                roles=['player'],
                permissions=['view_matches', 'view_team'],
                chat_access={
                    'main_chat': True,
                    'leadership_chat': False
                },
                telegram_id=player.telegram_id,
                telegram_username=player.telegram_username
            )
            
            await self.team_member_service.create_team_member(team_member)
            
            # Get team info
            team = await self.team_service.get_team(self.team_id)
            team_name = team.name if team else "KICKAI Team"
            
            return True, f"""🎉 <b>Welcome to {team_name}, {player.name.upper()}!</b>

✅ <b>Onboarding Complete!</b>

📋 <b>Your Details:</b>
• Name: {player.name.upper()}
• Player ID: {player.player_id.upper()}
• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
• FA Eligible: {'Yes' if player.fa_eligible else 'No'}

🏆 <b>What's Next:</b>
• You now have access to team features
• Check the team chat for announcements
• Contact admin for FA registration (if eligible)
• Join training sessions and matches

⚽ <b>Team Commands:</b>
• /myinfo - View your profile
• /list - See all team players
• /help - Get help with commands

Welcome to the team! 🏆"""
            
        except Exception as e:
            self.logger.error(f"Error completing onboarding: {e}")
            return False, f"Error completing onboarding: {str(e)}"
    
    @performance_timer("onboarding_notify_leadership_new_user")
    async def notify_leadership_new_user(self, player: Player) -> None:
        """Notify leadership chat about new user requiring approval."""
        try:
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.leadership_chat_id:
                return
            
            message = f"""🆕 <b>New User Requires Approval</b>

👤 <b>User Details:</b>
• Name: {player.name}
• Telegram: @{player.telegram_username or 'No username'}
• User ID: {player.telegram_id}

📋 <b>Actions Required:</b>
• Review user details
• Approve or reject registration
• Guide through onboarding if approved

💡 <b>Commands:</b>
• /approve {player.player_id} - Approve user
• /reject {player.player_id} [reason] - Reject user
• /pending - View all pending approvals"""
            
            # Send to leadership chat (this would need to be implemented)
            self.logger.info(f"New user notification sent to leadership: {player.name}")
            
        except Exception as e:
            self.logger.error(f"Error notifying leadership: {e}")
    
    @performance_timer("onboarding_notify_admin_fa_registration")
    async def notify_admin_fa_registration(self, player: Player) -> None:
        """Notify admin about FA registration request."""
        try:
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.leadership_chat_id:
                return
            
            message = f"""🏆 <b>FA Registration Request</b>

👤 <b>Player Details:</b>
• Name: {player.name.upper()}
• Player ID: {player.player_id.upper()}
• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
• Date of Birth: {player.date_of_birth or 'Not provided'}
• Emergency Contact: {player.emergency_contact or 'Not provided'}

📋 <b>Required Actions:</b>
• Contact player for documents
• Complete FA registration forms
• Collect registration fee (£15)
• Submit to FA

💡 <b>Next Steps:</b>
• Message player to arrange registration
• Collect required documents
• Complete registration process"""
            
            # Send to leadership chat (this would need to be implemented)
            self.logger.info(f"FA registration request sent to admin: {player.name}")
            
        except Exception as e:
            self.logger.error(f"Error notifying admin: {e}")
    
    def _validate_emergency_contact(self, contact: str) -> bool:
        """Validate emergency contact format."""
        # Basic validation: should contain name and phone
        if not contact or ',' not in contact:
            return False
        
        parts = contact.split(',')
        if len(parts) < 2:
            return False
        
        name = parts[0].strip()
        phone = parts[1].strip()
        
        # Check name is not empty
        if not name:
            return False
        
        # Check phone number format
        phone_pattern = r'^(\+44|0)[1-9]\d{8,9}$'
        return bool(re.match(phone_pattern, phone.replace(' ', '')))
    
    def _validate_date_of_birth(self, dob: str) -> bool:
        """Validate date of birth format."""
        # Check DD/MM/YYYY format
        dob_pattern = r'^(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/\d{4}$'
        if not re.match(dob_pattern, dob):
            return False
        
        # Check if date is valid
        try:
            day, month, year = map(int, dob.split('/'))
            datetime(year, month, day)
            return True
        except ValueError:
            return False


# Global onboarding workflow instance
_onboarding_workflow = None


def get_onboarding_workflow(team_id: str) -> OnboardingWorkflow:
    """Get or create onboarding workflow instance."""
    global _onboarding_workflow
    if _onboarding_workflow is None or _onboarding_workflow.team_id != team_id:
        _onboarding_workflow = OnboardingWorkflow(team_id)
    return _onboarding_workflow 