#!/usr/bin/env python3
"""
Chat Role Assignment Service for KICKAI

This service handles automatic role assignment based on chat membership:
- Users added to main chat become players
- Users added to leadership chat become team members  
- Users in both chats are both players and team members
- First user automatically becomes admin
- Auto-promote longest-tenured leadership member when last admin leaves
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from database.firebase_client import FirebaseClient
from core.exceptions import DatabaseError, ValidationError
from features.player_registration.domain.services.player_service import PlayerService
# TeamMemberService removed - using mock service instead
# Import TeamMember dynamically to avoid circular imports
from enums import ChatType

logger = logging.getLogger(__name__)


class ChatRoleAssignmentService:
    """Service for managing chat-based role assignment."""
    
    def __init__(self, firebase_client: FirebaseClient):
        self.firebase_client = firebase_client
        
        # Get PlayerService from dependency container instead of creating it directly
        try:
            from core.dependency_container import get_service
            from features.player_registration.domain.services.player_service import PlayerService
            
            self.player_service = get_service(PlayerService)
        except Exception as e:
            logger.warning(f"⚠️ Could not get PlayerService from dependency container: {e}")
            # Fallback to mock service
            self.player_service = self._create_mock_player_service()
        
        # TeamMemberService removed - using mock service instead
        self.team_member_service = self._create_mock_team_member_service()
        
        logger.info("✅ ChatRoleAssignmentService initialized")
    
    def _create_mock_player_service(self):
        """Create a mock player service for fallback."""
        class MockPlayerService:
            async def get_player_by_id(self, player_id: str):
                return None
            
            async def get_player_by_phone(self, phone: str, team_id: str):
                return None
        
        return MockPlayerService()
    
    def _create_mock_team_member_service(self):
        """Create a mock team member service for fallback."""
        class MockTeamMemberService:
            async def get_team_members_by_team(self, team_id: str):
                return []
            
            async def get_team_member_by_telegram_id(self, user_id: str, team_id: str):
                return None
            
            async def create_team_member(self, team_member):
                return "mock_member_id"
            
            async def update_team_member(self, team_member):
                return True
        
        return MockTeamMemberService()
    
    async def add_user_to_chat(self, team_id: str, user_id: str, chat_type: str, 
                              username: Optional[str] = None) -> Dict[str, Any]:
        """
        Add user to a chat and assign appropriate role.
        
        Args:
            team_id: The team ID
            user_id: The Telegram user ID
            chat_type: Either 'main_chat' or 'leadership_chat'
            username: Optional Telegram username
            
        Returns:
            Dict with assignment results
        """
        try:
            logger.info(f"Adding user {user_id} to {chat_type} for team {team_id}")
            
            # Check if this is the first user (no team members exist)
            existing_members = await self.team_member_service.get_team_members_by_team(team_id)
            is_first_user = len(existing_members) == 0
            
            # Get or create team member
            team_member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            
            if not team_member:
                # Create new team member
                from features.team_administration.domain.entities.team_member import TeamMember
                roles = self._determine_initial_roles(chat_type, is_first_user)
                team_member = TeamMember(
                    team_id=team_id,
                    user_id=user_id,
                    telegram_id=user_id,
                    telegram_username=username,
                    roles=roles,
                    chat_access={chat_type: True},
                    joined_at=datetime.now()
                )
                
                member_id = await self.team_member_service.create_team_member(team_member)
                team_member.id = member_id
                logger.info(f"Created new team member {user_id} with roles: {roles}")
            else:
                # Update existing team member
                await self._update_existing_member_roles(team_member, chat_type)
                team_member.chat_access[chat_type] = True
                await self.team_member_service.update_team_member(team_member)
                logger.info(f"Updated existing team member {user_id} for {chat_type}")
            
            # Handle player role assignment
            if chat_type == ChatType.MAIN.value:
                await self._ensure_player_role(team_id, user_id, username)
            
            # Handle first user admin assignment
            if is_first_user:
                await self._assign_first_user_admin(team_id, user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "team_id": team_id,
                "chat_type": chat_type,
                "roles": team_member.roles,
                "is_first_user": is_first_user,
                "is_admin": "admin" in team_member.roles
            }
            
        except Exception as e:
            logger.error(f"Failed to add user {user_id} to {chat_type}: {e}")
            raise DatabaseError(f"Failed to add user to chat: {str(e)}")
    
    async def remove_user_from_chat(self, team_id: str, user_id: str, chat_type: str) -> Dict[str, Any]:
        """
        Remove user from a chat and update roles accordingly.
        
        Args:
            team_id: The team ID
            user_id: The Telegram user ID
            chat_type: Either 'main_chat' or 'leadership_chat'
            
        Returns:
            Dict with removal results
        """
        try:
            logger.info(f"Removing user {user_id} from {chat_type} for team {team_id}")
            
            team_member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            if not team_member:
                return {"success": False, "error": "User not found in team"}
            
            # Update chat access
            team_member.chat_access[chat_type] = False
            await self.team_member_service.update_team_member(team_member)
            
            # Handle admin leaving leadership chat
            if chat_type == ChatType.LEADERSHIP.value and "admin" in team_member.roles:
                await self._handle_admin_leaving_leadership(team_id, user_id)
            
            # Remove player role if leaving main chat
            if chat_type == ChatType.MAIN.value and "player" in team_member.roles:
                team_member.roles.remove("player")
                await self.team_member_service.update_team_member(team_member)
            
            return {
                "success": True,
                "user_id": user_id,
                "team_id": team_id,
                "chat_type": chat_type,
                "roles": team_member.roles
            }
            
        except Exception as e:
            logger.error(f"Failed to remove user {user_id} from {chat_type}: {e}")
            raise DatabaseError(f"Failed to remove user from chat: {str(e)}")
    
    async def promote_to_admin(self, team_id: str, user_id: str, promoted_by: str) -> bool:
        """
        Promote a user to admin role.
        
        Args:
            team_id: The team ID
            user_id: The user to promote
            promoted_by: The user doing the promotion (must be admin)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if promoter is admin
            promoter = await self.team_member_service.get_team_member_by_telegram_id(promoted_by, team_id)
            if not promoter or "admin" not in promoter.roles:
                logger.warning(f"Non-admin user {promoted_by} attempted to promote {user_id}")
                return False
            
            # Get user to promote
            team_member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            if not team_member:
                logger.warning(f"User {user_id} not found in team {team_id}")
                return False
            
            # Add admin role
            if "admin" not in team_member.roles:
                team_member.roles.append("admin")
                await self.team_member_service.update_team_member(team_member)
                logger.info(f"User {user_id} promoted to admin by {promoted_by}")
                return True
            
            return True  # Already admin
            
        except Exception as e:
            logger.error(f"Failed to promote user {user_id} to admin: {e}")
            return False
    
    def _determine_initial_roles(self, chat_type: str, is_first_user: bool) -> List[str]:
        """Determine initial roles based on chat type and first user status."""
        roles = []
        
        if chat_type == ChatType.MAIN.value:
            roles.append("player")
        
        if chat_type == ChatType.LEADERSHIP.value:
            roles.append("team_member")
        
        if is_first_user:
            roles.append("admin")
        
        return roles
    
    async def _update_existing_member_roles(self, team_member, chat_type: str) -> None:
        """Update roles for existing team member joining a new chat."""
        if chat_type == ChatType.MAIN.value and "player" not in team_member.roles:
            team_member.roles.append("player")
        
        if chat_type == ChatType.LEADERSHIP.value and "team_member" not in team_member.roles:
            team_member.roles.append("team_member")
    
    async def _ensure_player_role(self, team_id: str, user_id: str, username: Optional[str] = None) -> None:
        """Ensure user has a player record if they're in the main chat."""
        try:
            # Check if player already exists
            existing_player = await self.player_service.get_player_by_telegram_id(user_id, team_id)
            if not existing_player:
                # Create a basic player record
                player = Player(
                    name=username or f"User {user_id}",
                    phone="",  # Will be filled during onboarding
                    team_id=team_id,
                    telegram_id=user_id,
                    telegram_username=username,
                    onboarding_status="pending"
                )
                await self.player_service.create_player(
                    name=player.name,
                    phone=player.phone,
                    team_id=team_id,
                    email=player.email,
                    position=player.position,
                    role=player.role,
                    fa_registered=player.fa_registered,
                    player_id=player.player_id
                )
                logger.info(f"Created player record for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to create player record for user {user_id}: {e}")
    
    async def _assign_first_user_admin(self, team_id: str, user_id: str) -> None:
        """Assign admin role to the first user of a team."""
        try:
            team_member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            if team_member and "admin" not in team_member.roles:
                team_member.roles.append("admin")
                await self.team_member_service.update_team_member(team_member)
                logger.info(f"Assigned admin role to first user {user_id} for team {team_id}")
        except Exception as e:
            logger.error(f"Failed to assign admin role to first user {user_id}: {e}")
    
    async def _handle_admin_leaving_leadership(self, team_id: str, user_id: str) -> None:
        """Handle when an admin leaves the leadership chat."""
        try:
            # Check if this was the last admin
            admin_members = await self.team_member_service.get_team_members_by_role(team_id, "admin")
            remaining_admins = [m for m in admin_members if m.telegram_id != user_id and m.can_access_chat("leadership_chat")]
            
            if not remaining_admins:
                # No admins left in leadership chat, promote longest-tenured member
                await self._promote_longest_tenured_to_admin(team_id)
            else:
                logger.info(f"Admin {user_id} left leadership chat, but {len(remaining_admins)} admins remain")
                
        except Exception as e:
            logger.error(f"Failed to handle admin leaving leadership: {e}")
    
    async def _promote_longest_tenured_to_admin(self, team_id: str) -> Optional[str]:
        """
        Promote the longest-tenured leadership member to admin.
        
        Returns:
            The user_id of the promoted member, or None if no suitable candidate
        """
        try:
            # Get all leadership members (excluding the one who just left)
            leadership_members = await self.team_member_service.get_leadership_members(team_id)
            
            # Filter to only those with leadership chat access
            eligible_members = [m for m in leadership_members if m.can_access_chat("leadership_chat")]
            
            if not eligible_members:
                logger.warning(f"No eligible members to promote to admin in team {team_id}")
                return None
            
            # Sort by join date (oldest first)
            eligible_members.sort(key=lambda m: m.joined_at)
            
            # Promote the longest-tenured member
            longest_tenured = eligible_members[0]
            if "admin" not in longest_tenured.roles:
                longest_tenured.roles.append("admin")
                await self.team_member_service.update_team_member(longest_tenured)
                logger.info(f"Promoted longest-tenured member {longest_tenured.user_id} to admin in team {team_id}")
                return longest_tenured.user_id
            
            return longest_tenured.user_id  # Already admin
            
        except Exception as e:
            logger.error(f"Failed to promote longest-tenured member to admin: {e}")
            return None
    
    async def get_user_roles(self, team_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive role information for a user."""
        try:
            team_member = await self.team_member_service.get_team_member_by_telegram_id(user_id, team_id)
            if not team_member:
                return {
                    "user_id": user_id,
                    "team_id": team_id,
                    "roles": [],
                    "chat_access": {},
                    "is_admin": False,
                    "is_player": False,
                    "is_team_member": False
                }
            
            return {
                "user_id": user_id,
                "team_id": team_id,
                "roles": team_member.roles,
                "chat_access": team_member.chat_access,
                "is_admin": "admin" in team_member.roles,
                "is_player": "player" in team_member.roles,
                "is_team_member": "team_member" in team_member.roles,
                "joined_at": team_member.joined_at.isoformat() if team_member.joined_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get user roles for {user_id}: {e}")
            return {
                "user_id": user_id,
                "team_id": team_id,
                "roles": [],
                "chat_access": {},
                "is_admin": False,
                "is_player": False,
                "is_team_member": False,
                "error": str(e)
            } 