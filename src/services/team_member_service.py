"""
Team Member Service for KICKAI

This service manages team membership, roles, and access control.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from database.interfaces import DataStoreInterface
from services.interfaces.team_member_service_interface import ITeamMemberService
from domain.interfaces.player_operations import IPlayerOperations
from domain.interfaces.team_operations import ITeamOperations
from database.models_improved import TeamMember
from utils.phone_utils import normalize_phone


logger = logging.getLogger(__name__)


@dataclass
class TeamMemberServiceConfig:
    """Configuration for TeamMemberService."""
    require_roles: bool = True
    leadership_roles: set = None
    
    def __post_init__(self):
        if self.leadership_roles is None:
            self.leadership_roles = {'captain', 'vice_captain', 'manager', 'coach', 'admin', 'volunteer'}


class TeamMemberService(ITeamMemberService):
    """Service for managing team members and their roles."""
    
    def __init__(self, data_store: DataStoreInterface, player_operations: IPlayerOperations, team_operations: ITeamOperations, config: Optional[TeamMemberServiceConfig] = None):
        self.data_store = data_store
        self.player_operations = player_operations
        self.team_operations = team_operations
        self.config = config or TeamMemberServiceConfig()

    async def create_team_member(self, team_member: TeamMember) -> str:
        """Create a new team member."""
        try:
            team_member.created_at = datetime.now()
            team_member.updated_at = datetime.now()
            member_id = await self.data_store.create_team_member(team_member)
            logger.info(f"✅ Created team member: {team_member.name} ({member_id})")
            return member_id
        except Exception as e:
            logger.error(f"❌ Failed to create team member: {e}")
            raise

    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        try:
            return await self.data_store.get_team_member(member_id)
        except Exception as e:
            logger.error(f"❌ Failed to get team member {member_id}: {e}")
            return None

    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by Telegram ID and team ID."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            for member in team_members:
                if member.telegram_id == telegram_id:
                    return member
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get team member by telegram_id {telegram_id}: {e}")
            return None

    async def update_team_member(self, team_member: TeamMember) -> bool:
        """Update an existing team member."""
        try:
            team_member.updated_at = datetime.now()
            success = await self.data_store.update_team_member(team_member)
            if success:
                logger.info(f"✅ Updated team member: {team_member.name}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to update team member {team_member.id}: {e}")
            return False

    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        try:
            success = await self.data_store.delete_team_member(member_id)
            if success:
                logger.info(f"✅ Deleted team member: {member_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to delete team member {member_id}: {e}")
            return False

    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all team members for a specific team."""
        try:
            return await self.data_store.get_team_members_by_team(team_id)
        except Exception as e:
            logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []

    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members with a specific role."""
        try:
            all_members = await self.get_team_members_by_team(team_id)
            return [member for member in all_members if role in member.roles]
        except Exception as e:
            logger.error(f"❌ Failed to get team members by role {role}: {e}")
            return []

    async def get_leadership_members(self, team_id: str) -> List[TeamMember]:
        """Get all leadership members for a team."""
        try:
            all_members = await self.get_team_members_by_team(team_id)
            leadership_members = []
            for member in all_members:
                if any(role in self.config.leadership_roles for role in member.roles):
                    leadership_members.append(member)
            return leadership_members
        except Exception as e:
            logger.error(f"❌ Failed to get leadership members for team {team_id}: {e}")
            return []

    async def get_players(self, team_id: str) -> List[TeamMember]:
        """Get all players (non-leadership members) for a team."""
        try:
            all_members = await self.get_team_members_by_team(team_id)
            players = []
            for member in all_members:
                if not any(role in self.config.leadership_roles for role in member.roles):
                    players.append(member)
            return players
        except Exception as e:
            logger.error(f"❌ Failed to get players for team {team_id}: {e}")
            return []

    async def add_role_to_member(self, member_id: str, role: str) -> bool:
        """Add a role to a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                logger.error(f"❌ Member not found: {member_id}")
                return False
            
            if role not in member.roles:
                member.roles.append(role)
                member.updated_at = datetime.now()
                success = await self.update_team_member(member)
                if success:
                    logger.info(f"✅ Added role {role} to member {member.name}")
                return success
            else:
                logger.info(f"ℹ️ Role {role} already exists for member {member.name}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to add role {role} to member {member_id}: {e}")
            return False

    async def remove_role_from_member(self, member_id: str, role: str) -> bool:
        """Remove a role from a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                logger.error(f"❌ Member not found: {member_id}")
                return False
            
            if role in member.roles:
                member.roles.remove(role)
                member.updated_at = datetime.now()
                success = await self.update_team_member(member)
                if success:
                    logger.info(f"✅ Removed role {role} from member {member.name}")
                return success
            else:
                logger.info(f"ℹ️ Role {role} doesn't exist for member {member.name}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to remove role {role} from member {member_id}: {e}")
            return False

    async def update_chat_access(self, member_id: str, chat_type: str, has_access: bool) -> bool:
        """Update chat access for a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                logger.error(f"❌ Member not found: {member_id}")
                return False
            
            if chat_type not in member.chat_access:
                member.chat_access[chat_type] = has_access
            else:
                member.chat_access[chat_type] = has_access
            member.updated_at = datetime.now()
            return await self.update_team_member(member)
        except Exception as e:
            logger.error(f"❌ Failed to update chat access for member {member_id}: {e}")
            return False
    
    def is_leadership_role(self, role: str) -> bool:
        """Check if a role is a leadership role."""
        return role in self.config.leadership_roles
    
    def get_leadership_roles(self) -> set:
        """Get all leadership roles."""
        return self.config.leadership_roles.copy()
    
    async def validate_member_roles(self, member: TeamMember) -> List[str]:
        """Validate team member roles and return any issues."""
        issues = []
        
        # Check if member has at least one role
        if not member.roles and self.config.require_roles:
            issues.append("Member must have at least one role")
        
        # Check for invalid roles
        for role in member.roles:
            if role not in self.config.leadership_roles and role != 'player':
                issues.append(f"Invalid role: {role}")
        
        return issues
    
    async def get_user_role(self, user_id: str, team_id: str) -> str:
        """Get the primary role of a user in a team."""
        try:
            # First try to get by telegram_id (user_id)
            member = await self.get_team_member_by_telegram_id(user_id, team_id)
            if member:
                # Return the first role, or 'player' as default
                return member.roles[0] if member.roles else 'player'
            
            # If not found by telegram_id, try to get by user_id
            team_members = await self.get_team_members_by_team(team_id)
            for member in team_members:
                if member.user_id == user_id:
                    return member.roles[0] if member.roles else 'player'
            
            # Default to 'player' if not found
            return 'player'
            
        except Exception as e:
            logger.error(f"❌ Failed to get user role for {user_id} in team {team_id}: {e}")
            return 'player'  # Default to player role on error

    async def generate_invitation(self, identifier: str, team_id: str) -> tuple[bool, str]:
        """Generate an invitation for a player by phone number or player ID."""
        try:
            from core.settings import Settings
            
            settings = Settings()
            
            # Find player by phone or ID
            player = None
            if any(char.isalpha() for char in identifier):
                # It's a player ID - search by player_id
                players = await self.player_operations.get_team_players(team_id)
                for p in players:
                    if p.player_id.lower() == identifier.lower():
                        player = p
                        break
            else:
                # It's a phone number - normalize and search
                normalized_phone = normalize_phone(identifier)
                if normalized_phone:
                    player = await self.player_operations.get_player_by_phone(normalized_phone, team_id)
                else:
                    return False, f"❌ Invalid phone number format: {identifier}"
            
            if not player:
                return False, f"❌ Player not found with identifier: {identifier}"
            
            # Get team info
            team = await self.team_operations.get_team(team_id)
            team_name = team.name if team else "KICKAI Team"
            
            # Get bot configuration for invite link
            bot_token = settings.telegram_bot_token
            if not bot_token or not settings.telegram_main_chat_id:
                return False, f"❌ Bot configuration not available for team {team_id}"
            
            # Create Telegram invite link
            invite_link = await self._create_telegram_invite_link(bot_token, settings.telegram_main_chat_id)
            
            # Generate invitation message
            invitation_message = f"""🎉 <b>Welcome to {team_name}!</b>

Hi {player.name},

You've been invited to join {team_name}! We're excited to have you on the team.

📋 <b>Your Details:</b>
• Name: {player.name}
• Position: {player.position.value.title() if hasattr(player.position, 'value') else player.position}
• Player ID: {player.player_id.upper()}

🔗 <b>Join Our Main Team Chat:</b>
{invite_link}

📱 <b>Next Steps:</b>
1. Click the link above to join our main team group
2. Once you join, the bot will automatically welcome you
3. If the bot doesn't welcome you automatically, type: <code>/register {player.player_id.upper()}</code>
4. Complete your onboarding process by following the bot's prompts
5. Get ready for training and matches!

⚠️ <b>Important:</b> 
• This invitation is for our main team chat only
• Leadership chat access is managed separately
• Make sure to use your Player ID: <b>{player.player_id.upper()}</b> if needed

⚽ <b>What to Expect:</b>
• Team announcements and updates
• Training schedules
• Match information
• Team communication

If you have any questions, please contact the team leadership.

Welcome aboard! 🏆

- {team_name} Management"""
            
            logger.info(f"✅ Invitation generated for player: {player.name} ({identifier})")
            return True, invitation_message
            
        except Exception as e:
            logger.error(f"❌ Error generating invitation for {identifier}: {e}")
            return False, f"❌ Error generating invitation: {str(e)}"
    
    async def _create_telegram_invite_link(self, bot_token: str, chat_id: str) -> str:
        """Create a Telegram group invite link using the Bot API."""
        try:
            import requests
            
            # Create invite link using Telegram Bot API
            url = f"https://api.telegram.org/bot{bot_token}/createChatInviteLink"
            data = {
                'chat_id': chat_id,
                'name': 'KICKAI Team Invite',
                'creates_join_request': False,
                'expire_date': None,  # No expiration
                'member_limit': None  # No member limit
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok') and result.get('result'):
                invite_link = result['result']['invite_link']
                logger.info(f"✅ Created Telegram invite link: {invite_link}")
                return invite_link
            else:
                error_msg = f"Failed to create invite link: {result.get('description', 'Unknown error')}"
                logger.error(error_msg)
                # Fallback to a placeholder link
                return f"https://t.me/+{chat_id.replace('-', '')}"
                
        except Exception as e:
            logger.error(f"❌ Error creating Telegram invite link: {e}")
            # Fallback to a placeholder link
            return f"https://t.me/+{chat_id.replace('-', '')}" 