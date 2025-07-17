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

    # New methods for chat-based role assignment integration
    
    async def is_first_user(self, team_id: str) -> bool:
        """Check if this would be the first user in the team."""
        try:
            team_members = await self.get_team_members_by_team(team_id)
            return len(team_members) == 0
        except Exception as e:
            logger.error(f"❌ Failed to check if first user for team {team_id}: {e}")
            return False
    
    async def get_longest_tenured_leadership_member(self, team_id: str) -> Optional[TeamMember]:
        """Get the longest-tenured leadership member with leadership chat access."""
        try:
            leadership_members = await self.get_leadership_members(team_id)
            
            # Filter to only those with leadership chat access
            eligible_members = [m for m in leadership_members if m.can_access_chat("leadership_chat")]
            
            if not eligible_members:
                return None
            
            # Sort by join date (oldest first)
            eligible_members.sort(key=lambda m: m.joined_at)
            return eligible_members[0]
            
        except Exception as e:
            logger.error(f"❌ Failed to get longest-tenured leadership member for team {team_id}: {e}")
            return None
    
    async def promote_to_admin(self, user_id: str, team_id: str, promoted_by: str) -> bool:
        """Promote a user to admin role (only by existing admin)."""
        try:
            # Check if promoter is admin
            promoter = await self.get_team_member_by_telegram_id(promoted_by, team_id)
            if not promoter or "admin" not in promoter.roles:
                logger.warning(f"Non-admin user {promoted_by} attempted to promote {user_id}")
                return False
            
            # Get user to promote
            member = await self.get_team_member_by_telegram_id(user_id, team_id)
            if not member:
                logger.warning(f"User {user_id} not found in team {team_id}")
                return False
            
            # Add admin role
            if "admin" not in member.roles:
                member.roles.append("admin")
                member.updated_at = datetime.now()
                success = await self.update_team_member(member)
                if success:
                    logger.info(f"User {user_id} promoted to admin by {promoted_by}")
                return success
            
            return True  # Already admin
            
        except Exception as e:
            logger.error(f"❌ Failed to promote user {user_id} to admin: {e}")
            return False
    
    async def handle_last_admin_leaving(self, team_id: str) -> Optional[str]:
        """Handle when the last admin leaves - promote longest-tenured leadership member."""
        try:
            # Get longest-tenured leadership member
            longest_tenured = await self.get_longest_tenured_leadership_member(team_id)
            if not longest_tenured:
                logger.warning(f"No eligible members to promote to admin in team {team_id}")
                return None
            
            # Promote to admin
            if "admin" not in longest_tenured.roles:
                longest_tenured.roles.append("admin")
                longest_tenured.updated_at = datetime.now()
                success = await self.update_team_member(longest_tenured)
                if success:
                    logger.info(f"Promoted longest-tenured member {longest_tenured.user_id} to admin in team {team_id}")
                    return longest_tenured.user_id
            
            return longest_tenured.user_id  # Already admin
            
        except Exception as e:
            logger.error(f"❌ Failed to handle last admin leaving for team {team_id}: {e}")
            return None

    async def generate_invitation(self, identifier: str, team_id: str) -> tuple[bool, str]:
        """Generate an invitation for a player by phone number or player ID."""
        try:
            # Note: This method would need player_service and team_service injected
            # For now, we'll return a generic message to avoid breaking existing functionality
            # TODO: Refactor to inject player_service and team_service dependencies
            
            invitation_message = f"""🎉 <b>Welcome to KICKAI Team!</b>

Hi there,

You've been invited to join our team! We're excited to have you on board.

📋 <b>Your Details:</b>
• Player ID: {identifier.upper()}

🔗 <b>Join Our Main Team Chat:</b>
[Invite link will be generated when bot is configured]

📋 <b>Next Steps:</b>
1. Join the main team chat
2. Complete your player registration
3. Get approved by team admin

🎯 <b>What You Can Do:</b>
• Register as a player: `/register {identifier.upper()}`
• Check your status: `/myinfo`
• Get help: `/help`

Welcome to the team! ⚽

---
<i>This invitation was generated by the KICKAI team management system.</i>"""

            return True, invitation_message
            
        except Exception as e:
            logger.error(f"❌ Failed to generate invitation: {e}")
            return False, f"Error generating invitation: {str(e)}"

    async def _create_telegram_invite_link(self, bot_token: str, chat_id: str) -> str:
        """Create a Telegram invite link for a chat."""
        try:
            # This would integrate with Telegram Bot API to create invite links
            # For now, return a placeholder
            return f"https://t.me/joinchat/{chat_id}"
        except Exception as e:
            logger.error(f"❌ Failed to create Telegram invite link: {e}")
            return "" 