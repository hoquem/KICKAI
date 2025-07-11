"""
Team Member Service for KICKAI

This service handles all team member operations with dependency injection
and clean architecture principles.
"""

import logging
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass

from database.models_improved import TeamMember
from database.firebase_client import FirebaseClient
from core.exceptions import DatabaseError, ValidationError
from services.interfaces.team_member_service_interface import ITeamMemberService

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
    """Service for managing team members with dependency injection."""
    
    def __init__(self, firebase_client: FirebaseClient, config: Optional[TeamMemberServiceConfig] = None):
        self.firebase_client = firebase_client
        self.config = config or TeamMemberServiceConfig()
        logger.info("✅ TeamMemberService initialized")
    
    async def create_team_member(self, team_member: TeamMember) -> str:
        """Create a new team member."""
        try:
            # Validate telegram_id uniqueness
            if team_member.telegram_id:
                existing = await self.get_team_member_by_telegram_id(team_member.telegram_id, team_member.team_id)
                if existing:
                    raise ValidationError(f"Team member with telegram_id {team_member.telegram_id} already exists")
            
            member_id = await self.firebase_client.create_team_member(team_member)
            logger.info(f"✅ Created team member: {team_member.user_id} with roles {team_member.roles}")
            return member_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create team member: {e}")
            raise DatabaseError(f"Failed to create team member: {str(e)}")
    
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        try:
            return await self.firebase_client.get_team_member(member_id)
        except Exception as e:
            logger.error(f"❌ Failed to get team member {member_id}: {e}")
            return None
    
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by telegram_id and team_id."""
        try:
            team_members = await self.firebase_client.get_team_members_by_team(team_id)
            for member in team_members:
                if member.telegram_id == telegram_id:
                    return member
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get team member by telegram_id {telegram_id}: {e}")
            return None
    
    async def update_team_member(self, team_member: TeamMember) -> bool:
        """Update a team member."""
        try:
            success = await self.firebase_client.update_team_member(team_member)
            if success:
                logger.info(f"✅ Updated team member: {team_member.user_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to update team member {team_member.user_id}: {e}")
            return False
    
    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        try:
            success = await self.firebase_client.delete_team_member(member_id)
            if success:
                logger.info(f"✅ Deleted team member: {member_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to delete team member {member_id}: {e}")
            return False
    
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all team members for a team."""
        try:
            return await self.firebase_client.get_team_members_by_team(team_id)
        except Exception as e:
            logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []
    
    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        """Get team members by role."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            return [member for member in team_members if member.has_role(role)]
        except Exception as e:
            logger.error(f"❌ Failed to get team members by role {role}: {e}")
            return []
    
    async def get_leadership_members(self, team_id: str) -> List[TeamMember]:
        """Get all leadership members (with any leadership role)."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            return [member for member in team_members if member.has_any_leadership_role()]
        except Exception as e:
            logger.error(f"❌ Failed to get leadership members for team {team_id}: {e}")
            return []
    
    async def get_players(self, team_id: str) -> List[TeamMember]:
        """Get all team members who are players."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            return [member for member in team_members if member.is_player()]
        except Exception as e:
            logger.error(f"❌ Failed to get players for team {team_id}: {e}")
            return []
    
    async def add_role_to_member(self, member_id: str, role: str) -> bool:
        """Add a role to a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                return False
            
            if role not in member.roles:
                member.roles.append(role)
                member.updated_at = datetime.now()
                return await self.update_team_member(member)
            
            return True  # Role already exists
        except Exception as e:
            logger.error(f"❌ Failed to add role {role} to member {member_id}: {e}")
            return False
    
    async def remove_role_from_member(self, member_id: str, role: str) -> bool:
        """Remove a role from a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                return False
            
            if role in member.roles:
                member.roles.remove(role)
                member.updated_at = datetime.now()
                
                # Ensure member still has at least one role
                if not member.roles and self.config.require_roles:
                    raise ValidationError("Team member must have at least one role")
                
                return await self.update_team_member(member)
            
            return True  # Role doesn't exist
        except Exception as e:
            logger.error(f"❌ Failed to remove role {role} from member {member_id}: {e}")
            return False
    
    async def update_chat_access(self, member_id: str, chat_type: str, has_access: bool) -> bool:
        """Update chat access for a team member."""
        try:
            member = await self.get_team_member(member_id)
            if not member:
                return False
            
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
            from services.player_service import get_player_service
            from services.team_service import get_team_service
            from core.settings import get_settings
            from utils.phone_utils import normalize_phone
            
            player_service = get_player_service(team_id=team_id)
            team_service = get_team_service(team_id=team_id)
            settings = get_settings()
            
            # Find player by phone or ID
            player = None
            if any(char.isalpha() for char in identifier):
                # It's a player ID - search by player_id
                players = await player_service.get_team_players(team_id)
                for p in players:
                    if p.player_id.lower() == identifier.lower():
                        player = p
                        break
            else:
                # It's a phone number - normalize and search
                normalized_phone = normalize_phone(identifier)
                if normalized_phone:
                    player = await player_service.get_player_by_phone(normalized_phone, team_id)
                else:
                    return False, f"❌ Invalid phone number format: {identifier}"
            
            if not player:
                return False, f"❌ Player not found with identifier: {identifier}"
            
            # Get team info
            team = await team_service.get_team(team_id)
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

# Global instance - now team-specific
_team_member_service_instances: dict[str, TeamMemberService] = {}


def get_team_member_service(team_id: Optional[str] = None) -> TeamMemberService:
    """Get the team member service instance for the specified team."""
    global _team_member_service_instances
    
    # Use default team ID if not provided
    if not team_id:
        import os
        team_id = os.getenv('DEFAULT_TEAM_ID', 'KAI')
    
    # Return existing instance if available for this team
    if team_id in _team_member_service_instances:
        return _team_member_service_instances[team_id]
    
    # Create new instance for this team
    from database.firebase_client import get_firebase_client
    firebase_client = get_firebase_client()
    
    team_member_service = TeamMemberService(firebase_client)
    _team_member_service_instances[team_id] = team_member_service
    
    logger.info(f"Created new TeamMemberService instance for team: {team_id}")
    return team_member_service


def initialize_team_member_service(team_id: Optional[str] = None) -> TeamMemberService:
    """Initialize the team member service for the specified team."""
    global _team_member_service_instances
    
    # Use default team ID if not provided
    if not team_id:
        import os
        team_id = os.getenv('DEFAULT_TEAM_ID', 'KAI')
    
    # Create new instance (overwriting if exists)
    from database.firebase_client import get_firebase_client
    firebase_client = get_firebase_client()
    
    team_member_service = TeamMemberService(firebase_client)
    _team_member_service_instances[team_id] = team_member_service
    
    logger.info(f"Initialized TeamMemberService for team: {team_id}")
    return team_member_service 