"""
Team Service for KICKAI

This module provides business logic for team management including
creation, validation, and member operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from core.exceptions import (
    TeamError, TeamNotFoundError, TeamValidationError, 
    ValidationError, DatabaseError, create_error_context
)
from database.models_improved import Team, TeamStatus, TeamMember, BotMapping, ExpenseCategory
from database.interfaces import DataStoreInterface
from services.interfaces.team_service_interface import ITeamService
from services.interfaces.budget_service_interface import IBudgetService
from utils.id_generator import generate_team_id
from utils.phone_utils import normalize_phone
from utils.validation_utils import validate_team_name, validate_team_id
from utils.enum_utils import serialize_enums_for_firestore


class TeamService(ITeamService):
    """Service for team management operations."""
    
    def __init__(self, data_store: DataStoreInterface, budget_service: IBudgetService):
        self._data_store = data_store
        self.budget_service = budget_service
    
    async def create_team(self, name: str, description: Optional[str] = None,
                         settings: Optional[Dict[str, Any]] = None,
                         fa_team_url: Optional[str] = None,
                         fa_fixtures_url: Optional[str] = None) -> Team:
        """Create a new team with validation."""
        try:
            # Validate input data
            self._validate_team_data(name)
            
            # Check for duplicate team name
            existing_team = await self._data_store.get_team_by_name(name)
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
                settings=settings or {},
                fa_team_url=fa_team_url,
                fa_fixtures_url=fa_fixtures_url
            )
            
            # Save to database
            saved_team_id = await self._data_store.create_team(team)
            team.id = saved_team_id  # Use the actual saved ID
            
            logging.info(
                f"Team created successfully: {team.name} (ID: {team_id}, Saved ID: {saved_team_id})"
            )
            
            return team
            
        except TeamError:
            raise
        except Exception as e:
            logging.error("Failed to create team", error=e)
            raise TeamError(
                f"Failed to create team: {str(e)}",
                create_error_context("create_team")
            )
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        try:
            team = await self._data_store.get_team(team_id)
            if team:
                logging.info(
                    f"Team retrieved: {team.name}"
                )
            return team
            
        except Exception as e:
            logging.error("Failed to get team", error=e, entity_id=team_id)
            raise TeamError(
                f"Failed to get team: {str(e)}",
                create_error_context("get_team", entity_id=team_id)
            )
    
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get a team by name."""
        try:
            team = await self._data_store.get_team_by_name(name)
            return team
            
        except Exception as e:
            logging.error("Failed to get team by name", error=e)
            raise TeamError(
                f"Failed to get team by name: {str(e)}",
                create_error_context("get_team_by_name", additional_info={'team_name': name})
            )
    
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
                    existing_team = await self._data_store.get_team_by_name(updates['name'])
                    if existing_team and existing_team.id != team_id:
                        raise TeamError(
                            f"Team with name '{updates['name']}' already exists",
                            create_error_context("update_team", entity_id=team_id)
                        )
            if 'fa_team_url' in updates:
                # Basic validation for URL format
                if not updates['fa_team_url'].startswith("http"):
                    raise TeamValidationError("FA team URL must be a valid URL", create_error_context("update_team"))
            if 'fa_fixtures_url' in updates:
                # Basic validation for URL format
                if not updates['fa_fixtures_url'].startswith("http"):
                    raise TeamValidationError("FA fixtures URL must be a valid URL", create_error_context("update_team"))
            
            # Update team
            team.update(**updates)
            
            # Save to database
            success = await self._data_store.update_team(team)
            if not success:
                raise TeamError(
                    "Failed to update team in database",
                    create_error_context("update_team", entity_id=team_id)
                )
            
            logging.info(
                f"Team updated: {team.name}"
            )
            
            return team
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            logging.error("Failed to update team", error=e, entity_id=team_id)
            raise TeamError(
                f"Failed to update team: {str(e)}",
                create_error_context("update_team", entity_id=team_id)
            )
    
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
            success = await self._data_store.delete_team(team_id)
            if not success:
                raise TeamError(
                    "Failed to delete team from database",
                    create_error_context("delete_team", entity_id=team_id)
                )
            
            logging.info(
                f"Team deleted: {team.name}"
            )
            
            return True
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            logging.error("Failed to delete team", error=e, entity_id=team_id)
            raise TeamError(
                f"Failed to delete team: {str(e)}",
                create_error_context("delete_team", entity_id=team_id)
            )
    
    async def get_all_teams(self, status: Optional[TeamStatus] = None) -> List[Team]:
        """Get all teams, optionally filtered by status."""
        try:
            filters = []
            if status:
                filters.append({'field': 'status', 'operator': '==', 'value': status.value})
            
            data_list = await self._data_store.query_documents('teams', filters)
            teams = [Team.from_dict(data) for data in data_list]
            
            logging.info(
                f"Retrieved {len(teams)} teams"
            )
            
            return teams
            
        except Exception as e:
            logging.error("Failed to get all teams", error=e)
            raise TeamError(
                f"Failed to get all teams: {str(e)}",
                create_error_context("get_all_teams")
            )
    
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
            member_id = await self._data_store.create_document('team_members', member.to_dict(), member.id)
            member.id = member_id
            
            logging.info(
                f"Team member added: {user_id} to team {team.name}"
            )
            
            return member
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            logging.error("Failed to add team member", error=e, team_id=team_id, user_id=user_id)
            raise TeamError(
                f"Failed to add team member: {str(e)}",
                create_error_context("add_team_member", team_id=team_id, user_id=user_id)
            )
    
    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        try:
            # Find team member
            filters = [
                {'field': 'team_id', 'operator': '==', 'value': team_id},
                {'field': 'user_id', 'operator': '==', 'value': user_id}
            ]
            data_list = await self._data_store.query_documents('team_members', filters, limit=1)
            
            if not data_list:
                raise TeamError(
                    f"Team member not found: {user_id} in team {team_id}",
                    create_error_context("remove_team_member", team_id=team_id, user_id=user_id)
                )
            
            member_data = data_list[0]
            member_id = member_data['id']
            
            # Delete from database
            success = await self._data_store.delete_document('team_members', member_id)
            if not success:
                raise TeamError(
                    "Failed to remove team member from database",
                    create_error_context("remove_team_member", team_id=team_id, user_id=user_id)
                )
            
            logging.info(
                f"Team member removed: {user_id} from team {team_id}"
            )
            
            return True
            
        except TeamError:
            raise
        except Exception as e:
            logging.error("Failed to remove team member", error=e, team_id=team_id, user_id=user_id)
            raise TeamError(
                f"Failed to remove team member: {str(e)}",
                create_error_context("remove_team_member", team_id=team_id, user_id=user_id)
            )
    
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        try:
            filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
            data_list = await self._data_store.query_documents('team_members', filters)
            members = [TeamMember.from_dict(data) for data in data_list]
            
            logging.info(
                f"Retrieved {len(members)} team members for team {team_id}"
            )
            
            return members
            
        except Exception as e:
            logging.error("Failed to get team members", error=e, team_id=team_id)
            raise TeamError(
                f"Failed to get team members: {str(e)}",
                create_error_context("get_team_members", team_id=team_id)
            )
    
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
            existing_mapping = await self._data_store.get_bot_mapping_by_team(team_name)
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
            mapping_id = await self._data_store.create_bot_mapping(mapping)
            mapping.id = mapping_id
            
            logging.info(
                f"Bot mapping created: {team_name} -> @{bot_username}"
            )
            
            return mapping
            
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            logging.error("Failed to create bot mapping", error=e, team_name=team_name)
            raise TeamError(
                f"Failed to create bot mapping: {str(e)}",
                create_error_context("create_bot_mapping", additional_info={'team_name': team_name})
            )
    
    async def get_bot_mapping(self, team_name: str) -> Optional[BotMapping]:
        """Get bot mapping for a team."""
        try:
            mapping = await self._data_store.get_bot_mapping_by_team(team_name)
            return mapping
            
        except Exception as e:
            logging.error("Failed to get bot mapping", error=e, team_name=team_name)
            raise TeamError(
                f"Failed to get bot mapping: {str(e)}",
                create_error_context("get_bot_mapping", additional_info={'team_name': team_name})
            )

    async def set_budget_limit(self, team_id: str, category: ExpenseCategory, limit: float) -> Team:
        """Sets a budget limit for a specific expense category for a team."""
        try:
            team = await self.get_team(team_id)
            if not team:
                raise TeamNotFoundError(f"Team not found: {team_id}", create_error_context("set_budget_limit"))

            team.budget_limits[category.value] = limit
            await self.update_team(team_id, budget_limits=team.budget_limits)
            logging.info(f"Budget limit for {category.value} set to {limit} for team {team_id}")
            return team
        except (TeamError, TeamNotFoundError):
            raise
        except Exception as e:
            logging.error(f"Failed to set budget limit: {e}")
            raise TeamError(f"Failed to set budget limit: {str(e)}", create_error_context("set_budget_limit"))

    async def get_budget_limit(self, team_id: str, category: ExpenseCategory) -> Optional[float]:
        """Gets the budget limit for a specific expense category for a team."""
        try:
            team = await self.get_team(team_id)
            if not team:
                return None
            return team.budget_limits.get(category.value)
        except Exception as e:
            logging.error(f"Failed to get budget limit: {e}")
            raise TeamError(f"Failed to get budget limit: {str(e)}", create_error_context("get_budget_limit"))

    async def check_expense_against_budget(self, team_id: str, category: ExpenseCategory, amount: float) -> Tuple[bool, Optional[float]]:
        """Checks if a new expense exceeds the budget limit for its category."""
        try:
            # Delegate to budget service
            can_afford, remaining_budget = await self.budget_service.check_expense_against_budget(team_id, category, amount)
            return can_afford, remaining_budget
        except Exception as e:
            logging.error(f"Error checking expense against budget: {e}")
            raise TeamError(f"Error checking expense against budget: {str(e)}", create_error_context("check_expense_against_budget"))

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