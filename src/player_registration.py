"""
KICKAI Player Registration System
Phase 1: Core Player Management

This module handles the basic player registration functionality including:
- Player data structure
- Basic CRUD operations
- Leadership commands
- Firebase integration
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Player:
    """Core player data structure - Phase 1"""
    player_id: str  # Human-friendly ID (e.g., JS1)
    name: str
    phone: str  # Primary identifier
    position: str
    status: str = "active"  # active, inactive, pending
    date_added: Optional[str] = None
    added_by: Optional[str] = None  # Telegram user ID of leadership member
    telegram_id: Optional[str] = None
    fa_registered: bool = False
    fa_registration_date: Optional[str] = None
    fa_eligible: bool = False  # True if registered with FA, else False
    invite_link: Optional[str] = None  # Telegram invite link
    invite_status: Optional[str] = None  # pending, sent, joined, expired
    onboarding_status: str = "pending"  # pending, in_progress, completed
    onboarding_step: str = "welcome"  # welcome, confirm_info, collect_missing, complete
    emergency_contact: Optional[str] = None
    date_of_birth: Optional[str] = None
    
    def __post_init__(self):
        if self.date_added is None:
            self.date_added = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for Firebase storage"""
        d = asdict(self)
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create player from dictionary (Firebase data)"""
        return cls(**data)

class PlayerRegistrationManager:
    """Core player registration management system"""
    
    def __init__(self, firebase_client, team_id: str):
        self.firebase_client = firebase_client
        self.team_id = team_id
        self.players_ref = firebase_client.collection('teams').document(team_id).collection('players')
        
        logger.info(f"✅ PlayerRegistrationManager initialized for team {team_id}")
    
    def _generate_player_id(self, name: str) -> str:
        initials = ''.join([part[0].upper() for part in name.strip().split() if part])
        if not initials:
            initials = 'P'
        players = self.get_all_players()
        existing_ids = [p.player_id for p in players if hasattr(p, 'player_id') and p.player_id.startswith(initials)]
        number = 1
        while f"{initials}{number}" in existing_ids:
            number += 1
        return f"{initials}{number}"

    def add_player(self, name: str, phone: str, position: str, added_by: str, fa_eligible: bool = False) -> Tuple[bool, str]:
        """
        Add a new player to the team
        
        Args:
            name: Player's full name
            phone: Player's phone number (primary identifier)
            position: Player's position
            added_by: Telegram user ID of leadership member
            fa_eligible: True if player is eligible for FA registration, else False
            
        Returns:
            (success, message)
        """
        try:
            # Validate phone number format
            if not self._validate_phone(phone):
                return False, "❌ Invalid phone number format. Please use format: 07123456789"
            
            # Check if player already exists
            existing_player = self.get_player_by_phone(phone)
            if existing_player:
                return False, f"❌ Player with phone {phone} already exists: {existing_player.name}"
            
            # Create new player
            player_id = self._generate_player_id(name)
            player = Player(
                player_id=player_id,
                name=name.strip(),
                phone=phone.strip(),
                position=position.strip(),
                added_by=added_by,
                status="pending",
                fa_eligible=fa_eligible
            )
            
            # Store in Firebase
            self.players_ref.document(phone).set(player.to_dict())
            
            logger.info(f"✅ Player added: {name} ({phone}) by {added_by}")
            return True, f"✅ Player {name} ({player_id}) added successfully! Phone: {phone} (FA eligible: {'Yes' if fa_eligible else 'No'})"
            
        except Exception as e:
            logger.error(f"❌ Error adding player: {e}")
            return False, f"❌ Error adding player: {str(e)}"
    
    def remove_player(self, phone: str, removed_by: str) -> Tuple[bool, str]:
        """
        Remove a player from the team
        
        Args:
            phone: Player's phone number
            removed_by: Telegram user ID of leadership member
            
        Returns:
            (success, message)
        """
        try:
            # Check if player exists
            player = self.get_player_by_phone(phone)
            if not player:
                return False, f"❌ Player with phone {phone} not found"
            
            # Remove from Firebase
            self.players_ref.document(phone).delete()
            
            logger.info(f"✅ Player removed: {player.name} ({phone}) by {removed_by}")
            return True, f"✅ Player {player.name} removed successfully"
            
        except Exception as e:
            logger.error(f"❌ Error removing player: {e}")
            return False, f"❌ Error removing player: {str(e)}"
    
    def get_player_by_phone(self, phone: str) -> Optional[Player]:
        """Get player by phone number"""
        try:
            doc = self.players_ref.document(phone).get()
            if doc.exists:
                return Player.from_dict(doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"❌ Error getting player: {e}")
            return None
    
    def get_all_players(self) -> List[Player]:
        """Get all players for the team"""
        try:
            players = []
            docs = self.players_ref.stream()
            for doc in docs:
                players.append(Player.from_dict(doc.to_dict()))
            return players
        except Exception as e:
            logger.error(f"❌ Error getting all players: {e}")
            return []
    
    def update_player_status(self, phone: str, status: str) -> Tuple[bool, str]:
        """Update player status (active, inactive, pending)"""
        try:
            player = self.get_player_by_phone(phone)
            if not player:
                return False, f"❌ Player with phone {phone} not found"
            
            self.players_ref.document(phone).update({'status': status})
            logger.info(f"✅ Player status updated: {player.name} -> {status}")
            return True, f"✅ Player {player.name} status updated to {status}"
            
        except Exception as e:
            logger.error(f"❌ Error updating player status: {e}")
            return False, f"❌ Error updating player status: {str(e)}"
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate UK phone number format"""
        # Basic UK mobile validation (07xxx xxxxxx)
        pattern = r'^07\d{9}$'
        return bool(re.match(pattern, phone.replace(' ', '')))
    
    def get_player_stats(self) -> Dict:
        """Get player statistics for the team"""
        try:
            players = self.get_all_players()
            stats = {
                'total': len(players),
                'active': len([p for p in players if p.status == 'active']),
                'pending': len([p for p in players if p.status == 'pending']),
                'inactive': len([p for p in players if p.status == 'inactive']),
                'fa_registered': len([p for p in players if p.fa_registered])
            }
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting player stats: {e}")
            return {'total': 0, 'active': 0, 'pending': 0, 'inactive': 0, 'fa_registered': 0}

    def generate_invite_link(self, phone: str, telegram_group_invite_base: str) -> Tuple[bool, str]:
        """
        Generate and store a Telegram invite link for a player.
        Args:
            phone: Player's phone number
            telegram_group_invite_base: The base invite link for the Telegram group (e.g., https://t.me/joinchat/xxxx)
        Returns:
            (success, message or invite link)
        """
        try:
            player = self.get_player_by_phone(phone)
            if not player:
                return False, f"❌ Player with phone {phone} not found"
            # Generate a unique deep link (simulate for now)
            # In production, use Telegram API to generate a real invite link
            invite_link = f"{telegram_group_invite_base}?start={player.player_id}"
            player.invite_link = invite_link
            player.invite_status = "pending"
            self.players_ref.document(phone).update({
                'invite_link': invite_link,
                'invite_status': 'pending'
            })
            return True, invite_link
        except Exception as e:
            logger.error(f"❌ Error generating invite link: {e}")
            return False, f"❌ Error generating invite link: {str(e)}"

    def player_joined_via_invite(self, player_id: str, telegram_user_id: str, telegram_username: str = None) -> Tuple[bool, str]:
        """
        Handle when a player joins via invite link
        Args:
            player_id: The player ID from the invite link
            telegram_user_id: The Telegram user ID of the joining user
            telegram_username: The Telegram username (optional)
        Returns:
            (success, message)
        """
        try:
            # Find player by player_id
            players = self.get_all_players()
            player = None
            for p in players:
                if p.player_id == player_id:
                    player = p
                    break
            
            if not player:
                return False, f"❌ Player with ID {player_id} not found"
            
            # Update player status
            updates = {
                'status': 'active',
                'telegram_id': telegram_user_id,
                'invite_status': 'joined',
                'onboarding_status': 'in_progress',
                'onboarding_step': 'welcome'
            }
            
            self.players_ref.document(player.phone).update(updates)
            
            logger.info(f"✅ Player {player.name} ({player_id}) joined via invite")
            return True, f"Welcome {player.name or 'Player'}! Let's complete your onboarding."
            
        except Exception as e:
            logger.error(f"❌ Error handling player join: {e}")
            return False, f"❌ Error processing join: {str(e)}"
    
    def get_onboarding_message(self, player_id: str) -> Tuple[bool, str]:
        """
        Get the next onboarding message for a player
        Args:
            player_id: The player ID
        Returns:
            (success, message)
        """
        try:
            players = self.get_all_players()
            player = None
            for p in players:
                if p.player_id == player_id:
                    player = p
                    break
            
            if not player:
                return False, "❌ Player not found"
            
            if player.onboarding_step == "welcome":
                player_name = player.name or "Player"
                return True, f"""🎉 **Welcome to BP Hatters FC, {player_name}!**

I'm here to help you complete your registration. Let me confirm your details:

**Current Information:**
• **Name:** {player_name}
• **Phone:** {player.phone or 'Not provided'}
• **Position:** {player.position or 'Not provided'}
• **Player ID:** {player.player_id}

**Missing Information:**
• Emergency Contact
• Date of Birth

Please reply with:
`confirm` - if the above details are correct
`update` - if you need to change anything"""
            
            elif player.onboarding_step == "confirm_info":
                return True, """Great! Now let's collect the missing information.

**Emergency Contact:**
Please provide the name and phone number of your emergency contact.
Format: `emergency [Name] [Phone]`
Example: `emergency John Smith 07123456789`

**Date of Birth:**
Please provide your date of birth.
Format: `dob [DD/MM/YYYY]`
Example: `dob 15/03/1990`"""
            
            elif player.onboarding_step == "collect_missing":
                return True, """Perfect! Let's complete your registration.

**Final Confirmation:**
Your registration is almost complete. Please confirm:
• All information is correct
• You understand the team rules
• You're ready to join training

Reply with `complete` to finish your registration."""
            
            else:
                return True, "Onboarding completed! Welcome to the team!"
                
        except Exception as e:
            logger.error(f"❌ Error getting onboarding message: {e}")
            return False, "❌ Error getting onboarding message"
    
    def process_onboarding_response(self, player_id: str, response: str) -> Tuple[bool, str]:
        """
        Process player's response during onboarding
        Args:
            player_id: The player ID
            response: The player's response
        Returns:
            (success, message)
        """
        try:
            players = self.get_all_players()
            player = None
            for p in players:
                if p.player_id == player_id:
                    player = p
                    break
            
            if not player:
                return False, "❌ Player not found"
            
            response_lower = response.lower().strip()
            
            if player.onboarding_step == "welcome":
                if response_lower == "confirm":
                    # Move to next step
                    self.players_ref.document(player.phone).update({
                        'onboarding_step': 'confirm_info'
                    })
                    return True, "✅ Details confirmed! Let's collect the missing information."
                elif response_lower == "update":
                    return True, "Please tell me what information needs to be updated."
                else:
                    return False, "Please reply with `confirm` or `update`."
            
            elif player.onboarding_step == "confirm_info":
                if response_lower.startswith("emergency "):
                    # Extract emergency contact
                    parts = response.split(" ", 2)
                    if len(parts) >= 3:
                        emergency_contact = parts[2]
                        self.players_ref.document(player.phone).update({
                            'emergency_contact': emergency_contact
                        })
                        return True, f"✅ Emergency contact saved: {emergency_contact}"
                    else:
                        return False, "Please provide emergency contact in format: `emergency [Name] [Phone]`"
                
                elif response_lower.startswith("dob "):
                    # Extract date of birth
                    dob = response.split(" ", 1)[1]
                    self.players_ref.document(player.phone).update({
                        'date_of_birth': dob
                    })
                    return True, f"✅ Date of birth saved: {dob}"
                
                else:
                    return False, "Please provide emergency contact (`emergency [Name] [Phone]`) or date of birth (`dob [DD/MM/YYYY]`)"
            
            elif player.onboarding_step == "collect_missing":
                if response_lower == "complete":
                    # Complete onboarding
                    self.players_ref.document(player.phone).update({
                        'onboarding_status': 'completed',
                        'onboarding_step': 'complete'
                    })
                    return True, """🎉 **Registration Complete!**

Welcome to BP Hatters FC! You're now fully registered and can:
• Attend training sessions
• Play in matches (subject to FA registration)
• Receive team updates and announcements

Use `/myinfo` to view or update your information anytime.

See you on the pitch! ⚽"""
                else:
                    return False, "Please reply with `complete` to finish your registration."
            
            else:
                return False, "Onboarding already completed."
                
        except Exception as e:
            logger.error(f"❌ Error processing onboarding response: {e}")
            return False, "❌ Error processing response"
    
    def get_player_info(self, telegram_user_id: str) -> Tuple[bool, str]:
        """
        Get player information for /myinfo command
        Args:
            telegram_user_id: The Telegram user ID
        Returns:
            (success, message)
        """
        try:
            players = self.get_all_players()
            player = None
            for p in players:
                if p.telegram_id == telegram_user_id:
                    player = p
                    break
            
            if not player:
                return False, "❌ Player not found. Please contact leadership if you believe this is an error."
            
            fa_status = "✅ Registered" if player.fa_registered else "❌ Not Registered"
            eligible = "Yes" if player.fa_eligible else "No"
            
            response = f"""👤 **Your Information**

**Player ID:** {player.player_id}
**Name:** {player.name}
**Phone:** {player.phone}
**Position:** {player.position}
**Status:** {player.status.title()}
**FA Registration:** {fa_status}
**FA Eligible:** {eligible}
**Emergency Contact:** {player.emergency_contact or 'Not provided'}
**Date of Birth:** {player.date_of_birth or 'Not provided'}
**Joined:** {player.date_added[:10] if player.date_added else 'Unknown'}

**Commands:**
• `/update [field] [value]` - Update your information
• `/help` - Get help with commands"""
            
            return True, response
            
        except Exception as e:
            logger.error(f"❌ Error getting player info: {e}")
            return False, "❌ Error retrieving player information"

class PlayerCommandHandler:
    """Handle leadership commands for player management"""
    
    def __init__(self, player_manager: PlayerRegistrationManager):
        self.player_manager = player_manager
    
    def handle_command(self, command: str, user_id: str) -> str:
        """
        Handle player management commands from leadership
        
        Commands:
        - add player [name] [phone] [position]
        - remove player [phone]
        - list players
        - player status [phone]
        - player stats
        - generate invite [phone]
        - myinfo
        """
        try:
            command = command.lower().strip()
            
            if command.startswith('add player'):
                return self._handle_add_player(command, user_id)
            elif command.startswith('remove player'):
                return self._handle_remove_player(command, user_id)
            elif command == 'list players':
                return self._handle_list_players()
            elif command.startswith('player status'):
                return self._handle_player_status(command)
            elif command == 'player stats':
                return self._handle_player_stats()
            elif command.startswith('generate invite'):
                return self._handle_generate_invite(command)
            elif command == "myinfo":
                return self._handle_myinfo(user_id)
            else:
                return self._get_help_message()
                
        except Exception as e:
            logger.error(f"❌ Error handling command: {e}")
            return f"❌ Error processing command: {str(e)}"
    
    def _handle_add_player(self, command: str, user_id: str) -> str:
        """Handle 'add player [name] [phone] [position]' command"""
        try:
            # Parse command: "add player John Smith 07123456789 striker"
            parts = command.split()
            if len(parts) < 5:
                return "❌ Usage: add player [name] [phone] [position]\nExample: add player John Smith 07123456789 striker"
            
            # Extract phone number (should be the second to last part)
            phone = parts[-2]
            position = parts[-1]
            name = ' '.join(parts[2:-2])  # Everything between "add player" and phone/position
            
            if not name:
                return "❌ Player name cannot be empty"
            
            success, message = self.player_manager.add_player(name, phone, position, user_id)
            return message
            
        except Exception as e:
            logger.error(f"❌ Error parsing add player command: {e}")
            return "❌ Error parsing command. Usage: add player [name] [phone] [position]"
    
    def _handle_remove_player(self, command: str, user_id: str) -> str:
        """Handle 'remove player [phone]' command"""
        try:
            parts = command.split()
            if len(parts) != 3:
                return "❌ Usage: remove player [phone]\nExample: remove player 07123456789"
            
            phone = parts[2]
            success, message = self.player_manager.remove_player(phone, user_id)
            return message
            
        except Exception as e:
            logger.error(f"❌ Error parsing remove player command: {e}")
            return "❌ Error parsing command. Usage: remove player [phone]"
    
    def _handle_list_players(self) -> str:
        """Handle 'list players' command"""
        try:
            players = self.player_manager.get_all_players()
            
            if not players:
                return "📋 **No players registered**"
            
            # Group players by status
            active_players = [p for p in players if p.status == 'active']
            pending_players = [p for p in players if p.status == 'pending']
            inactive_players = [p for p in players if p.status == 'inactive']
            
            response = "📋 **Team Players**\n\n"
            
            if active_players:
                response += "🟢 **Active Players:**\n"
                for player in active_players:
                    fa_status = "✅ FA" if player.fa_registered else "❌ FA"
                    eligible = "(FA eligible)" if getattr(player, 'fa_eligible', False) else "(Not FA eligible)"
                    response += f"• {player.player_id} {player.name} ({player.position}) - {fa_status} {eligible}\n"
                response += "\n"
            
            if pending_players:
                response += "🟡 **Pending Players:**\n"
                for player in pending_players:
                    eligible = "(FA eligible)" if getattr(player, 'fa_eligible', False) else "(Not FA eligible)"
                    response += f"• {player.player_id} {player.name} ({player.position}) - {player.phone} {eligible}\n"
                response += "\n"
            
            if inactive_players:
                response += "🔴 **Inactive Players:**\n"
                for player in inactive_players:
                    eligible = "(FA eligible)" if getattr(player, 'fa_eligible', False) else "(Not FA eligible)"
                    response += f"• {player.player_id} {player.name} ({player.position}) {eligible}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error listing players: {e}")
            return "❌ Error listing players"
    
    def _handle_player_status(self, command: str) -> str:
        """Handle 'player status [phone]' command"""
        try:
            parts = command.split()
            if len(parts) != 3:
                return "❌ Usage: player status [phone]\nExample: player status 07123456789"
            
            phone = parts[2]
            player = self.player_manager.get_player_by_phone(phone)
            
            if not player:
                return f"❌ Player with phone {phone} not found"
            
            fa_status = "✅ Registered" if player.fa_registered else "❌ Not Registered"
            eligible = "Yes" if getattr(player, 'fa_eligible', False) else "No"
            response = f"👤 **Player Status**\n\n"
            response += f"**ID:** {player.player_id}\n"
            response += f"**Name:** {player.name}\n"
            response += f"**Phone:** {player.phone}\n"
            response += f"**Position:** {player.position}\n"
            response += f"**Status:** {player.status.title()}\n"
            response += f"**FA Registration:** {fa_status}\n"
            response += f"**FA Eligible:** {eligible}\n"
            response += f"**Added:** {player.date_added[:10] if player.date_added else 'Unknown'}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error getting player status: {e}")
            return "❌ Error getting player status"
    
    def _handle_player_stats(self) -> str:
        """Handle 'player stats' command"""
        try:
            stats = self.player_manager.get_player_stats()
            
            response = "📊 **Team Statistics**\n\n"
            response += f"👥 **Total Players:** {stats['total']}\n"
            response += f"🟢 **Active:** {stats['active']}\n"
            response += f"🟡 **Pending:** {stats['pending']}\n"
            response += f"🔴 **Inactive:** {stats['inactive']}\n"
            response += f"✅ **FA Registered:** {stats['fa_registered']}\n"
            
            if stats['total'] > 0:
                fa_percentage = (stats['fa_registered'] / stats['total']) * 100
                response += f"📈 **FA Compliance:** {fa_percentage:.1f}%\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error getting player stats: {e}")
            return "❌ Error getting player statistics"
    
    def _handle_generate_invite(self, command: str) -> str:
        """Handle 'generate invite [phone]' command"""
        try:
            parts = command.split()
            if len(parts) != 3:
                return "❌ Usage: generate invite [phone]\nExample: generate invite 07123456789"
            phone = parts[2]
            # For demo, use a placeholder base invite link
            telegram_group_invite_base = "https://t.me/joinchat/EXAMPLEGROUP"
            success, result = self.player_manager.generate_invite_link(phone, telegram_group_invite_base)
            if success:
                return f"🔗 Invite link for player {phone}: {result}\nCopy and send this link to the player."
            else:
                return result
        except Exception as e:
            logger.error(f"❌ Error generating invite: {e}")
            return "❌ Error generating invite link."
    
    def _handle_myinfo(self, user_id: str) -> str:
        """Handle '/myinfo' command for players"""
        success, message = self.player_manager.get_player_info(user_id)
        return message
    
    def _get_help_message(self) -> str:
        """Get help message for player commands"""
        return """🤖 **Player Management Commands**

**Add Player:**
`add player [name] [phone] [position]`
Example: `add player John Smith 07123456789 striker`

**Remove Player:**
`remove player [phone]`
Example: `remove player 07123456789`

**List Players:**
`list players`

**Player Status:**
`player status [phone]`
Example: `player status 07123456789`

**Team Statistics:**
`player stats`

**Generate Invite:**
`generate invite [phone]`
Example: `generate invite 07123456789`

**My Info:**
`myinfo`

**Help:**
`player help`""" 