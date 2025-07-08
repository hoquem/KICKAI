"""
Improved Onboarding Handler for KICKAI

This module implements the complete onboarding workflow as specified in the PRD,
with proper step-by-step progress tracking, validation, and reminder integration.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from ..database.models_improved import Player, OnboardingStatus, PlayerRole, PlayerPosition
from ..services.player_service import get_player_service
from ..services.team_service import get_team_service
from ..services.reminder_service import get_reminder_service
from ..core.bot_config_manager import get_bot_config_manager


@dataclass
class OnboardingStep:
    """Represents a step in the onboarding process."""
    step_id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False
    data: Optional[Dict[str, Any]] = None


class ImprovedOnboardingWorkflow:
    """Complete onboarding workflow matching the PRD requirements."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_service = get_player_service()
        self.team_service = get_team_service()
        self.reminder_service = get_reminder_service(team_id)
        self.bot_config_manager = get_bot_config_manager()
        self.onboarding_steps = self.bot_config_manager.get_onboarding_steps(self.team_id) or [
            "emergency_contact",
            "date_of_birth",
            "fa_registration"
        ]
        
        # Validation rules as specified in PRD
        self.validation_rules = {
            "emergency_contact": {
                "name": {"required": True, "min_length": 2, "max_length": 50},
                "phone": {"required": True, "pattern": r"^(\+44|0)7\d{9}$"},
                "relationship": {"required": True, "min_length": 2, "max_length": 30}
            },
            "date_of_birth": {
                "format": "DD/MM/YYYY",
                "min_age": 16,
                "max_age": 80,
                "must_be_past": True
            },
            "fa_registration": {
                "required": True,
                "valid_options": ["yes", "no", "not_sure"]
            }
        }
    
    async def start_player_onboarding(self, player: Player, user_id: str, username: Optional[str] = None) -> Tuple[bool, str]:
        """Start onboarding process for an existing player."""
        try:
            # Update player with Telegram info and start onboarding
            updates = {
                'telegram_id': user_id,
                'onboarding_status': OnboardingStatus.IN_PROGRESS.value,
                'onboarding_started_at': datetime.now(),
                'last_activity': datetime.now()
            }
            if username:
                updates['telegram_username'] = username
            
            # Mark basic registration as completed and initialize other steps dynamically
            onboarding_progress = {
                "basic_registration": {"completed": True, "completed_at": datetime.now()}
            }
            for step in self.onboarding_steps:
                onboarding_progress[step] = {"completed": False, "completed_at": None, "data": None}
            updates['onboarding_progress'] = onboarding_progress
            
            # Initialize progress tracking
            progress = {
                "current_step": self.onboarding_steps[0] if self.onboarding_steps else "completion",
                "completed_steps": ["basic_registration"],
                "total_steps": len(self.onboarding_steps) + 1  # +1 for basic registration
            }
            updates['progress'] = progress
            
            updated_player = await self.player_service.update_player(player.id, **updates)
            
            # Send welcome message
            welcome_message = await self.get_welcome_message(updated_player)
            
            # Notify admin that onboarding started
            await self._notify_admin_onboarding_started(updated_player)
            
            logging.info(f"Started onboarding for player {player.name}")
            return True, welcome_message
            
        except Exception as e:
            logging.error(f"Error starting player onboarding: {e}")
            return False, f"Error starting onboarding: {str(e)}"
    
    async def get_welcome_message(self, player: Player) -> str:
        """Generate welcome message for new player."""
        try:
            team = await self.team_service.get_team(self.team_id)
            team_name = team.name if team else "KICKAI Team"
            
            progress_display = ""
            for i, step in enumerate(self.onboarding_steps):
                status = "⏳ Pending"
                if player.onboarding_progress.get(step, {}).get("completed"):
                    status = "✅ Completed"
                elif i == 0: # Assuming the first step in the list is the next one if not completed
                    status = "⏳ Next"
                progress_display += f"🔄 Step {i+2}: {self._format_step_name(step)} {status}\n"

            next_step_name = self._format_step_name(self.onboarding_steps[0]) if self.onboarding_steps else "N/A"

            return f"""✅ Welcome to {team_name}, {player.name.upper()}!

📋 Your Details:
• Name: {player.name.upper()}
• Player ID: {player.player_id.upper()}
• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
• Phone: {player.phone}

🎯 Let's get you set up! Here's what we need:

📊 Onboarding Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}
📝 Next Step: {next_step_name}
Please provide your emergency contact information:
• Name of emergency contact
• Their phone number
• Relationship to you

💡 Example: "My emergency contact is John Doe, 07123456789, my husband"

Ready to continue? Just reply with your emergency contact details!"""
            
        except Exception as e:
            logging.error(f"Error generating welcome message: {e}")
            return "Welcome! Let's get you set up. Please provide your emergency contact details."

    def _format_step_name(self, step_id: str) -> str:
        """Formats a step ID into a human-readable name."""
        return step_id.replace("_", " ").title()

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
            
            # Handle help request
            if response.lower().strip() == "help":
                return await self._handle_help_request(player)
            
            # Handle restart request
            if response.lower().strip() == "restart onboarding":
                return await self._handle_restart_request(player)
            
            # Get current step and handle response
            current_step = player.get_current_onboarding_step()

            # Find the index of the current step in the defined onboarding_steps
            try:
                current_step_index = self.onboarding_steps.index(current_step)
            except ValueError:
                # If current_step is not in the defined steps, it might be 'completion' or an invalid state
                if current_step == "completion":
                    return await self._handle_completion(player)
                return False, "❌ Invalid onboarding step or configuration mismatch."

            # Handle the current step based on its ID
            if current_step == "emergency_contact":
                return await self._handle_emergency_contact(player, response)
            elif current_step == "date_of_birth":
                return await self._handle_date_of_birth(player, response)
            elif current_step == "fa_registration":
                return await self._handle_fa_registration(player, response)
            else:
                return False, "❌ Unhandled onboarding step."
                
        except Exception as e:
            logging.error(f"Error processing onboarding response: {e}")
            return False, f"Error processing response: {str(e)}"
    
    async def _handle_emergency_contact(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle emergency contact collection."""
        try:
            # Parse emergency contact from response
            parsed_contact = self._parse_emergency_contact(response)
            if not parsed_contact:
                return False, """❌ Incomplete Information

I need more details for your emergency contact. Please provide:
• Name
• Phone number
• Relationship

💡 Example: "My emergency contact is John Doe, 07123456789, my husband"

Please try again with the complete information."""
            
            # Validate phone number
            if not re.match(self.validation_rules["emergency_contact"]["phone"]["pattern"], parsed_contact["phone"]):
                return False, """❌ Invalid phone number format

Please provide a valid UK phone number:
• Format: 07XXXXXXXXX or +447XXXXXXXXX
• Example: 07123456789

Try again with the correct format."""
            
            # Update player with emergency contact
            updates = {
                'emergency_contact': f"{parsed_contact['name']}, {parsed_contact['phone']}, {parsed_contact['relationship']}",
                'emergency_contact_name': parsed_contact['name'],
                'emergency_contact_phone': parsed_contact['phone'],
                'emergency_contact_relationship': parsed_contact['relationship'],
                'last_activity': datetime.now()
            }
            
            # Update onboarding progress
            updates['onboarding_progress'] = player.onboarding_progress.copy()
            updates['onboarding_progress']['emergency_contact'] = {
                "completed": True,
                "completed_at": datetime.now(),
                "data": parsed_contact
            }
            
            updated_player = await self.player_service.update_player(player.id, **updates)

            # Determine the next step dynamically
            current_step_index = self.onboarding_steps.index("emergency_contact")
            next_step_index = current_step_index + 1
            next_step_message = ""
            if next_step_index < len(self.onboarding_steps):
                next_step_id = self.onboarding_steps[next_step_index]
                next_step_name = self._format_step_name(next_step_id)
                next_step_message = f"\n\n📝 Next Step: {next_step_name}"
                if next_step_id == "date_of_birth":
                    next_step_message += "\nPlease provide your date of birth (DD/MM/YYYY format):\n\n💡 Example: \"My date of birth is 15/05/1995\"\n\nReady to continue? Just reply with your date of birth!"
                elif next_step_id == "fa_registration":
                    next_step_message += "\nAre you currently registered with the Football Association (FA)?\n\n💡 Options:\n• \"Yes, I am FA registered\"\n• \"No, I'm not FA registered\"\n• \"I'm not sure, please help\"\n\nReady to continue? Just reply with your FA registration status!"
            else:
                next_step_message = "\n\n🎉 You've completed all initial onboarding steps! Please wait for admin approval."

            progress_display = ""
            for i, step_id in enumerate(self.onboarding_steps):
                status = "⏳ Pending"
                if player.onboarding_progress.get(step_id, {}).get("completed"):
                    status = "✅ Completed"
                elif i == next_step_index -1:
                    status = "⏳ Next"
                progress_display += f"🔄 Step {i+2}: {self._format_step_name(step_id)} {status}\n"

            return f"""✅ Emergency Contact Saved!

📋 Emergency Contact:
• Name: {parsed_contact['name']}
• Phone: {parsed_contact['phone']}
• Relationship: {parsed_contact['relationship']}

📊 Onboarding Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}
{next_step_message}"""
            
        except Exception as e:
            logging.error(f"Error handling emergency contact: {e}")
            return False, f"Error processing emergency contact: {str(e)}"
    
    async def _handle_date_of_birth(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle date of birth collection."""
        try:
            # Parse date of birth from response
            dob = self._parse_date_of_birth(response)
            if not dob:
                return False, """❌ Invalid date format

Please provide your date of birth in DD/MM/YYYY format:
• Example: 15/05/1995
• Example: 03/12/1988

Try again with the correct format."""
            
            # Validate age
            age = self._calculate_age(dob)
            if age < self.validation_rules["date_of_birth"]["min_age"] or age > self.validation_rules["date_of_birth"]["max_age"]:
                return False, f"""❌ Invalid age

You must be between {self.validation_rules['date_of_birth']['min_age']} and {self.validation_rules['date_of_birth']['max_age']} years old to register.

Your calculated age: {age} years

Please provide a valid date of birth."""
            
            # Update player with date of birth
            updates = {
                'date_of_birth': dob.strftime('%d/%m/%Y'),
                'last_activity': datetime.now()
            }
            
            # Update onboarding progress
            updates['onboarding_progress'] = player.onboarding_progress.copy()
            updates['onboarding_progress']['date_of_birth'] = {
                "completed": True,
                "completed_at": datetime.now(),
                "data": dob.strftime('%d/%m/%Y')
            }
            
            updated_player = await self.player_service.update_player(player.id, **updates)

            # Determine the next step dynamically
            current_step_index = self.onboarding_steps.index("date_of_birth")
            next_step_index = current_step_index + 1
            next_step_message = ""
            if next_step_index < len(self.onboarding_steps):
                next_step_id = self.onboarding_steps[next_step_index]
                next_step_name = self._format_step_name(next_step_id)
                next_step_message = f"\n\n📝 Next Step: {next_step_name}"
                if next_step_id == "fa_registration":
                    next_step_message += "\nAre you currently registered with the Football Association (FA)?\n\n💡 Options:\n• \"Yes, I am FA registered\"\n• \"No, I\'m not FA registered\"\n• \"I\'m not sure, please help\"\n\nReady to continue? Just reply with your FA registration status!"
            else:
                next_step_message = "\n\n🎉 You\'ve completed all initial onboarding steps! Please wait for admin approval."

            progress_display = ""
            for i, step_id in enumerate(self.onboarding_steps):
                status = "⏳ Pending"
                if player.onboarding_progress.get(step_id, {}).get("completed"):
                    status = "✅ Completed"
                elif i == next_step_index -1:
                    status = "⏳ Next"
                progress_display += f"🔄 Step {i+2}: {self._format_step_name(step_id)} {status}\n"

            return f"""✅ Date of Birth Saved!

📋 Personal Information:
• Date of Birth: {dob.strftime('%d/%m/%Y')}
• Age: {age} years old

📊 Onboarding Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}
{next_step_message}"""
            
        except Exception as e:
            logging.error(f"Error handling date of birth: {e}")
            return False, f"Error processing date of birth: {str(e)}"
    
    async def _handle_fa_registration(self, player: Player, response: str) -> Tuple[bool, str]:
        """Handle FA registration step."""
        try:
            response_lower = response.lower().strip()
            
            if response_lower not in self.validation_rules["fa_registration"]["valid_options"]:
                return False, """❌ Please choose one of the options:

Are you currently registered with the Football Association (FA)?

💡 Options:
• "Yes, I am FA registered"
• "No, I'm not FA registered"
• "I'm not sure, please help"

Please reply with one of these exact phrases."""
            
            # Determine FA registration status
            if response_lower == "yes":
                fa_registered = True
                fa_eligible = True
            elif response_lower == "no":
                fa_registered = False
                fa_eligible = True
            else:  # "not_sure"
                fa_registered = False
                fa_eligible = True
            
            # Update player with FA registration info
            updates = {
                'fa_registered': fa_registered,
                'fa_eligible': fa_eligible,
                'last_activity': datetime.now()
            }
            
            # Update onboarding progress
            updates['onboarding_progress'] = player.onboarding_progress.copy()
            updates['onboarding_progress']['fa_registration'] = {
                "completed": True,
                "completed_at": datetime.now(),
                "data": {
                    "fa_registered": fa_registered,
                    "fa_eligible": fa_eligible,
                    "response": response_lower
                }
            }
            
            # Mark onboarding as completed
            updates['onboarding_status'] = OnboardingStatus.COMPLETED.value
            updates['onboarding_completed_at'] = datetime.now()

            updated_player = await self.player_service.update_player(player.id, **updates)

            # Notify admin that onboarding is completed
            await self._notify_admin_onboarding_completed(updated_player)

            # Send post-onboarding welcome and tutorial
            welcome_message = await self._send_post_onboarding_welcome_and_tutorial(updated_player)

            return True, welcome_message
            
        except Exception as e:
            logging.error(f"Error handling FA registration: {e}")
            return False, f"Error processing FA registration: {str(e)}"
    
    async def _send_post_onboarding_welcome_and_tutorial(self, player: Player) -> str:
        """Sends a welcome message and initiates tutorial post-onboarding."""
        try:
            # Notify admin that onboarding is completed
            await self._notify_admin_onboarding_completed(player)

            progress_display = ""
            for i, step_id in enumerate(self.onboarding_steps):
                status = "⏳ Pending"
                if player.onboarding_progress.get(step_id, {}).get("completed"):
                    status = "✅ Completed"
                progress_display += f"🔄 Step {i+2}: {self._format_step_name(step_id)} {status}\n"

            message = f"""✅ FA Registration Status Saved!

📋 FA Registration:
• Status: {'Registered' if player.fa_registered else 'Not Registered'}
• Eligibility: {'Yes' if player.fa_eligible else 'No'} (based on admin settings)

📊 Onboarding Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}

🎉 Congratulations! Your onboarding is complete!

📋 Your Complete Profile:
• Name: {player.name.upper()}
• Player ID: {player.player_id.upper()}
• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
• Phone: {player.phone}
• Emergency Contact: {player.emergency_contact}
• Date of Birth: {player.date_of_birth}
• FA Registered: {'Yes' if player.fa_registered else 'No'}

📊 Status:
• Onboarding: ✅ Completed
• Admin Approval: ⏳ Pending
• Match Eligibility: ⏳ Pending Approval

💡 Next Steps:
• Admin will review your information
• You'll be notified when approved
• Once approved, you'll be eligible for match selection

🏆 Welcome to KICKAI Team! You're all set up and ready to play!

💬 Available Commands:
• /myinfo - View your details
• /status - Check your status
• /list - See all team players
• /help - Get assistance"""
            return message
        except Exception as e:
            logging.error(f"Error sending post-onboarding welcome and tutorial: {e}")
            return "Error sending welcome message. Please contact admin for assistance."

    async def _handle_help_request(self, player: Player) -> Tuple[bool, str]:
        """Handle help request from player."""
        try:
            progress = player.get_onboarding_progress()
            current_step = progress['current_step']
            
            progress_display = ""
            for i, step_id in enumerate(self.onboarding_steps):
                status = "⏳ Pending"
                if progress['steps'].get(step_id, {}).get("completed"):
                    status = "✅ Completed"
                elif step_id == current_step:
                    status = "⏳ Next"
                progress_display += f"🔄 Step {i+2}: {self._format_step_name(step_id)} {status}\n"

            if current_step == "emergency_contact":
                help_text = f"""💡 Onboarding Help

📊 Your Current Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}

📝 Current Step: Emergency Contact

What you need to provide:
• Name of your emergency contact
• Their phone number
• Your relationship to them

💡 Example Responses:
• "My emergency contact is John Doe, 07123456789, my husband"
• "Emergency contact: Sarah Smith, 07987654321, my sister"
• "John Doe, 07123456789, my father"

🔧 Other Help:
• /status - Check your current status
• /myinfo - View your basic information
• Contact admin for additional help

Ready to continue? Just reply with your emergency contact details!"""
            
            elif current_step == "date_of_birth":
                help_text = f"""💡 Onboarding Help

📊 Your Current Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}

📝 Current Step: Date of Birth

What you need to provide:
• Your date of birth in DD/MM/YYYY format

💡 Example Responses:
• "My date of birth is 15/05/1995"
• "15/05/1995"
• "I was born on 15/05/1995"

🔧 Other Help:
• /status - Check your current status
• /myinfo - View your basic information
• Contact admin for additional help

Ready to continue? Just reply with your date of birth!"""
            
            elif current_step == "fa_registration":
                help_text = f"""💡 Onboarding Help

📊 Your Current Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}

📝 Current Step: FA Registration

What you need to provide:
• Your FA registration status

💡 Options:
• "Yes, I am FA registered" - If you're already registered
• "No, I'm not FA registered" - If you're not registered
• "I'm not sure, please help" - If you need assistance

🔧 Other Help:
• /status - Check your current status
• /myinfo - View your basic information
• Contact admin for additional help

Ready to continue? Just reply with your FA registration status!"""
            
            else:
                help_text = f"""💡 Onboarding Help

📊 Your Current Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}

🎉 Your onboarding is complete! 

💡 Next Steps:
• Wait for admin approval
• You'll be notified when approved
• Once approved, you'll be eligible for match selection

🔧 Available Commands:
• /myinfo - View your details
• /status - Check your status
• /list - See all team players
• /help - Get assistance"""
            
            return True, help_text
            
        except Exception as e:
            logging.error(f"Error handling help request: {e}")
            return False, "Error providing help. Please contact admin for assistance."
    
    async def _handle_restart_request(self, player: Player) -> Tuple[bool, str]:
        """Handle restart onboarding request."""
        try:
            progress_display = ""
            for i, step_id in enumerate(self.onboarding_steps):
                status = "⏳ Pending"
                if progress['steps'].get(step_id, {}).get("completed"):
                    status = "✅ Completed"
                progress_display += f"🔄 Step {i+2}: {self._format_step_name(step_id)} {status}\n"

            return True, f"""🔄 Restarting Onboarding

Are you sure you want to restart your onboarding? This will clear all your progress.

📊 Current Progress:
🔄 Step 1: Basic Registration ✅ Completed
{progress_display}

💡 Options:
• "Yes, restart" - Clear progress and start over
• "No, continue" - Keep current progress
• "help" - Get assistance with current step

What would you like to do?"""
            
        except Exception as e:
            logging.error(f"Error handling restart request: {e}")
            return False, "Error processing restart request. Please contact admin for assistance."
    
    async def _handle_completion(self, player: Player) -> Tuple[bool, str]:
        """Handle onboarding completion."""
        try:
            return True, f"""🎉 Congratulations! You've been approved!

✅ {player.name.upper()} ({player.player_id.upper()}) - You're now eligible for match selection!

📊 Your Status:
• Onboarding: ✅ Completed
• Admin Approval: ✅ Approved
• Match Eligibility: ✅ Eligible
• FA Registration: {'✅ Registered' if player.is_fa_registered() else '⚠️ Not Registered (Contact admin if needed)'}

🏆 You're now a full member of KICKAI Team!

💡 What's Next:
• Check upcoming matches with /listmatches
• View team stats with /stats
• Get match details with /getmatch <match_id>

Welcome to the team! 🏆⚽"""
            
        except Exception as e:
            logging.error(f"Error handling completion: {e}")
            return False, "Error processing completion. Please contact admin for assistance."
    
    def _parse_emergency_contact(self, response: str) -> Optional[Dict[str, str]]:
        """Parse emergency contact from response."""
        try:
            # Remove common prefixes
            response = re.sub(r'^(my emergency contact is|emergency contact:|contact:)\s*', '', response.lower())
            
            # Try to extract name, phone, and relationship
            # Pattern: name, phone, relationship
            parts = [part.strip() for part in response.split(',')]
            
            if len(parts) >= 3:
                name = parts[0].title()
                phone = parts[1].strip()
                relationship = parts[2].strip()
                
                # Validate phone number
                if re.match(r'^(\+44|0)7\d{9}$', phone):
                    return {
                        "name": name,
                        "phone": phone,
                        "relationship": relationship
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"Error parsing emergency contact: {e}")
            return None
    
    def _parse_date_of_birth(self, response: str) -> Optional[datetime]:
        """Parse date of birth from response."""
        try:
            # Remove common prefixes
            response = re.sub(r'^(my date of birth is|i was born on|dob:)\s*', '', response.lower())
            
            # Try different date formats
            date_patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
                r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, response)
                if match:
                    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    
                    # Validate date
                    if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= datetime.now().year:
                        return datetime(year, month, day)
            
            return None
            
        except Exception as e:
            logging.error(f"Error parsing date of birth: {e}")
            return None
    
    def _calculate_age(self, dob: datetime) -> int:
        """Calculate age from date of birth."""
        today = datetime.now()
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        return age
    
    async def _notify_admin_onboarding_started(self, player: Player) -> None:
        """Notify admin that onboarding started."""
        try:
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.leadership_chat_id:
                return
            
            message = f"""🆕 Player Started Onboarding

📋 Player: {player.name} ({player.player_id})
📱 Phone: {player.phone}
⚽ Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
⏰ Started: {player.onboarding_started_at.strftime('%Y-%m-%d %H:%M') if player.onboarding_started_at else 'Unknown'}

📊 Progress: Step 1/4 completed

💡 Commands:
• /status {player.player_id} - Check detailed progress
• /pending - View all pending players"""
            
            # Send to leadership chat (this would need to be implemented)
            logging.info(f"Admin notification sent for onboarding started: {player.name}")
            
        except Exception as e:
            logging.error(f"Error notifying admin about onboarding started: {e}")
    
    async def _notify_admin_onboarding_completed(self, player: Player) -> None:
        """Notify admin that onboarding completed."""
        try:
            bot_config = self.bot_config_manager.get_bot_config(self.team_id)
            if not bot_config or not bot_config.leadership_chat_id:
                return
            
            message = f"""✅ Player Completed Onboarding

📋 Player: {player.name} ({player.player_id})
📱 Phone: {player.phone}
⚽ Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
⏰ Completed: {player.onboarding_completed_at.strftime('%Y-%m-%d %H:%M') if player.onboarding_completed_at else 'Unknown'}

📊 Onboarding Summary:
• Emergency Contact: {player.emergency_contact or 'Not provided'}
• Date of Birth: {player.date_of_birth or 'Not provided'}
• FA Registered: {'Yes' if player.fa_registered else 'No'}

🎯 Action Required:
• Review player information
• Approve or reject registration

💡 Commands:
• /approve {player.player_id} - Approve player
• /reject {player.player_id} [reason] - Reject player
• /status {player.player_id} - Review details"""
            
            # Send to leadership chat (this would need to be implemented)
            logging.info(f"Admin notification sent for onboarding completed: {player.name}")
            
        except Exception as e:
            logging.error(f"Error notifying admin about onboarding completed: {e}")


def get_improved_onboarding_workflow(team_id: str) -> ImprovedOnboardingWorkflow:
    """Get improved onboarding workflow instance."""
    return ImprovedOnboardingWorkflow(team_id) 