"""
Team Service for KICKAI

This module provides business logic for team management including
creation, validation, and member operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.exceptions import (
    TeamError, TeamNotFoundError, TeamValidationError, 
    TeamPermissionError, create_error_context
)
from ..core.logging import get_logger, performance_timer
from ..database.firebase_client import get_firebase_client
from ..database.models import Team, TeamStatus, TeamMember, BotMapping
from ..utils.id_generator import generate_team_id


class TeamService:
    """Service for team management operations."""
    
    def __init__(self):
        self._firebase_client = get_firebase_client()
        self._logger = get_logger("team_service")
    
    @performance_timer("team_service_create_team")
    async def create_team(self, name: str, description: Optional[str] = None,
                         settings: Optional[Dict[str, Any]] = None) -> Team:
        """Create a new team with validation."""
        try:
            # Validate input data
            self._validate_team_data(name)
            
            # Check for duplicate team name
            existing_team = await self._firebase_client.get_team_by_name(name)
            if existing_team:
                raise TeamError(
                    f"Team with name '{name}' already exists",
                    create_error_context("create_team", additional_info={'team_name': name})
                )
            
            # Generate human-readable team ID
            team_id = generate_team_id(name)
            
            # Create team object with the generated ID
            team = Team(
                id=team_id,  # Use the human-readable ID
                name=name.strip(),
                description=description.strip() if description else None,
                status=TeamStatus.ACTIVE,
                settings=settings or {}
            )
            
            # Save to database
            saved_team_id = await self._firebase_client.create_team(team)
            team.id = saved_team_id  # Use the actual saved ID
            
            self._logger.info(
                f"Team created successfully: {team.name} (ID: {team_id}, Saved ID: {saved_team_id})",
                operation="create_team",
                entity_id=saved_team_id,
                human_readable_id=team_id
            )
            
            return team
            
        except TeamError:
            raise
        except Exception as e:
            self._logger.error("Failed to create team", error=e)
            raise TeamError(
                f"Failed to create team: {str(e)}",
                create_error_context("create_team")
            )
    
    @performance_timer("team_service_get_team")
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        try:
            team = await self._firebase_client.get_team(team_id)
            if team:
                self._logger.info(
                    f"Team retrieved: {team.name}",
                    operation="get_team",
                    entity_id=team_id
                )
            return team
            
        except Exception as e:
            self._logger.error("Failed to get team", error=e, entity_id=team_id)
            raise TeamError(
                f"Failed to get team: {str(e)}",
                create_error_context("get_team", entity_id=team_id)
            )
    
    @performance_timer("team_service_get_team_by_name")
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get a team by name."""
        try:
            team = await self._firebase_client.get_team_by_name(name)
            return team
            
        except Exception as e:
            self._logger.error("Failed to get team by name", error=e)
            raise TeamError(
                f"Failed to get team by name: {str(e)}",
                create_error_context("get_team_by_name", additional_info={'team_name': name})
            )
    
    @performance_timer("team_service_update_team")
    async def update_team(self, team_id: str, **updates) -> Team:
        """Update a team with validation."""
        try:
            # Get existing team
            team = await self.get_team(team_id)
            if not team:
                raise TeamNotFoundError(
                    f"Team not found: {team_id}",
                    create_error_context("update_team", entity_id=team_id)
                )
            
            # Validate updates if they include validation fields
            if 'name' in updates:
                self._validate_team_name(updates['name'])
                # Check for duplicate name if changed
                if updates['name'] != team.name:
                    existing_team = await self._firebase_client.get_team_by_name(updates['name'])
                    if existing_team and existing_team.id != team_id:
                        raise TeamError(
                            f"Team with name '{updates['name']}' already exists",
                            create_error_context("update_team", entity_id=team_id)
                        )
            
            # Update team
            team.update(**updates)
            
            # Save to database
            success = await self._firebase_client.update_team(team)
            if not success:
                raise TeamError(
                    "Failed to update team in database",
                    create_error_context("update_team", entity_id=team_id)
                )
            
            self._logger.info(
                f"Team updated: {team.name}",
                operation="update_team",
                entity_id=team_id
            )
            
            return team
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            self._logger.error("Failed to update team", error=e, entity_id=team_id)
            raise TeamError(
                f"Failed to update team: {str(e)}",
                create_error_context("update_team", entity_id=team_id)
            )
    
    @performance_timer("team_service_delete_team")
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        try:
            # Get team first to log the operation
            team = await self.get_team(team_id)
            if not team:
                raise TeamNotFoundError(
                    f"Team not found: {team_id}",
                    create_error_context("delete_team", entity_id=team_id)
                )
            
            # Delete from database
            success = await self._firebase_client.delete_team(team_id)
            if not success:
                raise TeamError(
                    "Failed to delete team from database",
                    create_error_context("delete_team", entity_id=team_id)
                )
            
            self._logger.info(
                f"Team deleted: {team.name}",
                operation="delete_team",
                entity_id=team_id
            )
            
            return True
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            self._logger.error("Failed to delete team", error=e, entity_id=team_id)
            raise TeamError(
                f"Failed to delete team: {str(e)}",
                create_error_context("delete_team", entity_id=team_id)
            )
    
    @performance_timer("team_service_get_all_teams")
    async def get_all_teams(self, status: Optional[TeamStatus] = None) -> List[Team]:
        """Get all teams, optionally filtered by status."""
        try:
            filters = []
            if status:
                filters.append({'field': 'status', 'operator': '==', 'value': status.value})
            
            data_list = await self._firebase_client.query_documents('teams', filters)
            teams = [Team.from_dict(data) for data in data_list]
            
            self._logger.info(
                f"Retrieved {len(teams)} teams",
                operation="get_all_teams"
            )
            
            return teams
            
        except Exception as e:
            self._logger.error("Failed to get all teams", error=e)
            raise TeamError(
                f"Failed to get all teams: {str(e)}",
                create_error_context("get_all_teams")
            )
    
    @performance_timer("team_service_add_team_member")
    async def add_team_member(self, team_id: str, user_id: str, role: str = "player",
                            permissions: Optional[List[str]] = None) -> TeamMember:
        """Add a member to a team."""
        try:
            # Validate team exists
            team = await self.get_team(team_id)
            if not team:
                raise TeamNotFoundError(
                    f"Team not found: {team_id}",
                    create_error_context("add_team_member", team_id=team_id)
                )
            
            # Create team member
            member = TeamMember(
                team_id=team_id,
                user_id=user_id,
                role=role,
                permissions=permissions or []
            )
            
            # Save to database
            member_id = await self._firebase_client.create_document('team_members', member.to_dict(), member.id)
            member.id = member_id
            
            self._logger.info(
                f"Team member added: {user_id} to team {team.name}",
                operation="add_team_member",
                entity_id=member_id,
                team_id=team_id,
                user_id=user_id
            )
            
            return member
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            self._logger.error("Failed to add team member", error=e, team_id=team_id, user_id=user_id)
            raise TeamError(
                f"Failed to add team member: {str(e)}",
                create_error_context("add_team_member", team_id=team_id, user_id=user_id)
            )
    
    @performance_timer("team_service_remove_team_member")
    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        try:
            # Find team member
            filters = [
                {'field': 'team_id', 'operator': '==', 'value': team_id},
                {'field': 'user_id', 'operator': '==', 'value': user_id}
            ]
            data_list = await self._firebase_client.query_documents('team_members', filters, limit=1)
            
            if not data_list:
                raise TeamError(
                    f"Team member not found: {user_id} in team {team_id}",
                    create_error_context("remove_team_member", team_id=team_id, user_id=user_id)
                )
            
            member_data = data_list[0]
            member_id = member_data['id']
            
            # Delete from database
            success = await self._firebase_client.delete_document('team_members', member_id)
            if not success:
                raise TeamError(
                    "Failed to remove team member from database",
                    create_error_context("remove_team_member", team_id=team_id, user_id=user_id)
                )
            
            self._logger.info(
                f"Team member removed: {user_id} from team {team_id}",
                operation="remove_team_member",
                team_id=team_id,
                user_id=user_id
            )
            
            return True
            
        except TeamError:
            raise
        except Exception as e:
            self._logger.error("Failed to remove team member", error=e, team_id=team_id, user_id=user_id)
            raise TeamError(
                f"Failed to remove team member: {str(e)}",
                create_error_context("remove_team_member", team_id=team_id, user_id=user_id)
            )
    
    @performance_timer("team_service_get_team_members")
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        try:
            filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
            data_list = await self._firebase_client.query_documents('team_members', filters)
            members = [TeamMember.from_dict(data) for data in data_list]
            
            self._logger.info(
                f"Retrieved {len(members)} team members for team {team_id}",
                operation="get_team_members",
                team_id=team_id
            )
            
            return members
            
        except Exception as e:
            self._logger.error("Failed to get team members", error=e, team_id=team_id)
            raise TeamError(
                f"Failed to get team members: {str(e)}",
                create_error_context("get_team_members", team_id=team_id)
            )
    
    @performance_timer("team_service_create_bot_mapping")
    async def create_bot_mapping(self, team_name: str, bot_username: str, 
                               chat_id: str, bot_token: str) -> BotMapping:
        """Create a bot mapping for a team."""
        try:
            # Validate team exists
            team = await self.get_team_by_name(team_name)
            if not team:
                raise TeamNotFoundError(
                    f"Team not found: {team_name}",
                    create_error_context("create_bot_mapping", additional_info={'team_name': team_name})
                )
            
            # Check for existing mapping
            existing_mapping = await self._firebase_client.get_bot_mapping_by_team(team_name)
            if existing_mapping:
                raise TeamError(
                    f"Bot mapping already exists for team: {team_name}",
                    create_error_context("create_bot_mapping", team_id=team.id)
                )
            
            # Create bot mapping
            mapping = BotMapping(
                team_name=team_name,
                bot_username=bot_username,
                chat_id=chat_id,
                bot_token=bot_token
            )
            
            # Save to database
            mapping_id = await self._firebase_client.create_bot_mapping(mapping)
            mapping.id = mapping_id
            
            self._logger.info(
                f"Bot mapping created: {team_name} -> @{bot_username}",
                operation="create_bot_mapping",
                entity_id=mapping_id,
                team_id=team.id
            )
            
            return mapping
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            self._logger.error("Failed to create bot mapping", error=e, team_name=team_name)
            raise TeamError(
                f"Failed to create bot mapping: {str(e)}",
                create_error_context("create_bot_mapping", additional_info={'team_name': team_name})
            )
    
    @performance_timer("team_service_get_bot_mapping")
    async def get_bot_mapping(self, team_name: str) -> Optional[BotMapping]:
        """Get bot mapping for a team."""
        try:
            mapping = await self._firebase_client.get_bot_mapping_by_team(team_name)
            return mapping
            
        except Exception as e:
            self._logger.error("Failed to get bot mapping", error=e, team_name=team_name)
            raise TeamError(
                f"Failed to get bot mapping: {str(e)}",
                create_error_context("get_bot_mapping", additional_info={'team_name': team_name})
            )
    
    def _validate_team_data(self, name: str):
        """Validate team data."""
        self._validate_team_name(name)
    
    def _validate_team_name(self, name: str):
        """Validate team name."""
        if not name or not name.strip():
            raise TeamValidationError(
                "Team name cannot be empty",
                create_error_context("validate_team_name")
            )
        
        if len(name.strip()) < 2:
            raise TeamValidationError(
                "Team name must be at least 2 characters long",
                create_error_context("validate_team_name")
            )
        
        if len(name.strip()) > 100:
            raise TeamValidationError(
                "Team name cannot exceed 100 characters",
                create_error_context("validate_team_name")
            )


# Global team service instance
_team_service: Optional[TeamService] = None


def get_team_service() -> TeamService:
    """Get the global team service instance."""
    global _team_service
    if _team_service is None:
        _team_service = TeamService()
    return _team_service


def initialize_team_service() -> TeamService:
    """Initialize the global team service."""
    global _team_service
    _team_service = TeamService()
    return _team_service 