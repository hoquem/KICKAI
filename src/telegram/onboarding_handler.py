"""
Onboarding Handler for KICKAI

This module handles the complete onboarding workflow for new users joining the team:
1. Detect new users joining via invite link
2. Admin approval process
3. Player profile completion
4. FA registration guidance
5. Team access management

UPDATED: Now uses the improved onboarding workflow for better user experience and PRD compliance.
"""

import asyncio
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import logging

from src.database.models import Player, OnboardingStatus, PlayerRole, PlayerPosition
from src.services.player_service import get_player_service
from src.services.team_service import get_team_service
from src.services.team_member_service import TeamMemberService
from src.database.firebase_client import get_firebase_client
from src.core.bot_config_manager import get_bot_config_manager
from src.utils.llm_intent import extract_intent

# Import improved onboarding workflow
from .onboarding_handler_improved import get_improved_onboarding_workflow


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
    """Complete onboarding workflow for new team members.
    
    UPDATED: Now delegates to improved workflow for better user experience.
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_service = get_player_service()
        self.team_service = get_team_service()
        self.team_member_service = TeamMemberService(get_firebase_client())
        self.bot_config_manager = get_bot_config_manager()
        
        # Initialize improved workflow
        self.improved_workflow = get_improved_onboarding_workflow(team_id)
        
        # Define onboarding steps (kept for backward compatibility)
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
            
            # First, try to find by telegram_id (most reliable)
            for player in pending_players:
                if player.telegram_id == user_id:
                    pending_player = player
                    break
            
            # If not found by telegram_id, try by username
            if not pending_player and username:
                for player in pending_players:
                    if player.telegram_username == username:
                        pending_player = player
                        break
            
            # If still not found, try by name (for cases where user joins with same name)
            if not pending_player and first_name and last_name:
                full_name = f"{first_name} {last_name}".strip()
                for player in pending_players:
                    if player.name.lower() == full_name.lower():
                        pending_player = player
                        break
            
            if pending_player:
                # User is a pending player, start onboarding using improved workflow
                return await self.improved_workflow.start_player_onboarding(pending_player, user_id, username)
            else:
                # New user, create pending approval entry
                return await self.create_pending_approval(user_id, username, first_name, last_name)
                
        except Exception as e:
            logging.error(f"Error detecting new member: {e}")
            return False, f"Error processing new member: {str(e)}"
    
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
            
            logging.info(f"Created pending approval for user {user_id}")
            return True, "✅ Welcome! Your registration is pending admin approval."
            
        except Exception as e:
            logging.error(f"Error creating pending approval: {e}")
            return False, f"Error creating approval request: {str(e)}"
    
    async def start_player_onboarding(self, player: Player, user_id: str, username: Optional[str] = None) -> Tuple[bool, str]:
        """Start onboarding process for an existing player using improved workflow."""
        try:
            # Delegate to improved workflow
            return await self.improved_workflow.start_player_onboarding(player, user_id, username)
        except Exception as e:
            logging.error(f"Error starting player onboarding: {e}")
            return False, f"Error starting onboarding: {str(e)}"
    
    async def get_welcome_message(self, player: Player) -> str:
        """Generate welcome message for new player using improved workflow."""
        try:
            return await self.improved_workflow.get_welcome_message(player)
        except Exception as e:
            logging.error(f"Error generating welcome message: {e}")
            return "Welcome! Let's get you set up. Please provide your emergency contact details."
    
    async def process_response(self, user_id: str, response: str) -> Tuple[bool, str]:
        """Process user response during onboarding using improved workflow."""
        try:
            # Delegate to improved workflow
            return await self.improved_workflow.process_response(user_id, response)
        except Exception as e:
            logging.error(f"Error processing onboarding response: {e}")
            return False, f"Error processing response: {str(e)}"
    
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
            logging.info(f"New user notification sent to leadership: {player.name}")
            
        except Exception as e:
            logging.error(f"Error notifying leadership: {e}")
    
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
            logging.info(f"FA registration request sent to admin: {player.name}")
            
        except Exception as e:
            logging.error(f"Error notifying admin: {e}")
    
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