"""
Team Service

This module provides team management functionality.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger

from kickai.core.interfaces.team_repositories import ITeamRepository

from ..entities.team import Team, TeamStatus
from ..entities.team_member import TeamMember

logger = logging.getLogger(__name__)


@dataclass
class TeamCreateParams:
    name: str
    description: str = ""
    status: TeamStatus = TeamStatus.ACTIVE
    created_by: str = "system"
    settings: dict[str, Any] | None = None
    bot_token: str | None = None
    main_chat_id: str | None = None
    leadership_chat_id: str | None = None


class TeamService:
    """Service for managing teams."""

    def __init__(self, team_repository: ITeamRepository, expense_service: Any | None = None):
        self.team_repository = team_repository
        self.logger = logger
        # Optional dependency used in tests
        self.expense_service = expense_service or type("_NullExpenseService", (), {"get_total_expenses": staticmethod(lambda team_id: 0.0)})()

    async def create_team(self, **kwargs) -> Team:
        """
        Create a new team (accepts kwargs for tests or TeamCreateParams via params=).

        :param kwargs: Team creation parameters
        :type kwargs: dict
        :return: Created team
        :rtype: Team
        """
        if isinstance(kwargs.get("params"), TeamCreateParams):
            p = kwargs["params"]
            name = p.name; description = p.description; status = p.status; created_by = p.created_by
            settings = p.settings or {}; bot_token = p.bot_token; main_chat_id = p.main_chat_id; leadership_chat_id = p.leadership_chat_id
        else:
            name = kwargs.get("name", "")
            description = kwargs.get("description", "")
            status = kwargs.get("status", TeamStatus.ACTIVE)
            created_by = kwargs.get("created_by", "system")
            settings = kwargs.get("settings", {})
            bot_token = kwargs.get("bot_token")
            main_chat_id = kwargs.get("main_chat_id")
            leadership_chat_id = kwargs.get("leadership_chat_id")

        team = Team(
            name=name,
            description=description,
            status=status,
            created_by=created_by,
            created_at=datetime.now(),
            settings=settings,
            bot_token=bot_token,
            main_chat_id=main_chat_id,
            leadership_chat_id=leadership_chat_id,
        )
        # Some tests expect `create`, interface defines `create_team`
        try:
            return await self.team_repository.create(team)  # type: ignore[attr-defined]
        except AttributeError:
            return await self.team_repository.create_team(team)

    async def get_team(self, *, team_id: str) -> Team | None:
        """
        Get a team by ID (supports both get_by_id and get_team_by_id).

        :param team_id: Team ID to get
        :type team_id: str
        :return: Team if found, None otherwise
        :rtype: Team | None
        """
        try:
            return await self.team_repository.get_by_id(team_id)  # type: ignore[attr-defined]
        except AttributeError:
            return await self.team_repository.get_team_by_id(team_id)

    async def get_team_by_id(self, *, team_id: str) -> Team | None:
        """
        Get a team by ID (alias for get_team).

        :param team_id: Team ID to get
        :type team_id: str
        :return: Team if found, None otherwise
        :rtype: Team | None
        """
        return await self.get_team(team_id=team_id)

    async def get_team_by_name(self, name: str) -> Team | None:
        """
        Get a team by name.

        :param name: Team name to search for
        :type name: str
        :return: Team if found, None otherwise
        :rtype: Team | None
        """
        # This would need to be implemented in the repository
        # For now, get all teams and filter by name
        all_teams = await self.get_all_teams()
        for team in all_teams:
            if team.name == name:
                return team
        return None

    async def get_all_teams(self) -> list[Team]:
        """
        Get all teams from the repository.

        :return: List of all teams
        :rtype: list[Team]
        """
        try:
            teams = await self.team_repository.list_all()
            self.logger.info(f"📊 Retrieved {len(teams)} teams from repository")
            return teams
        except Exception as e:
            self.logger.error(f"❌ Failed to get all teams: {e}")
            return []

    async def get_teams_by_status(self, status: TeamStatus) -> list[Team]:
        """
        Get teams by status.

        :param status: Team status to filter by
        :type status: TeamStatus
        :return: List of teams with the specified status
        :rtype: list[Team]
        """
        return await self.team_repository.get_by_status(status)

    async def update_team(self, team_id: str, **updates) -> Team:
        """
        Update a team with provided updates.

        :param team_id: Team ID to update
        :type team_id: str
        :param updates: Updates to apply to the team
        :type updates: dict
        :return: Updated team
        :rtype: Team
        :raises ValueError: If team is not found
        """
        # Some tests use get_by_id instead of get_team_by_id
        try:
            team = await self.team_repository.get_by_id(team_id)  # type: ignore[attr-defined]
        except AttributeError:
            team = await self.team_repository.get_team_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")

        # Apply updates
        for key, value in updates.items():
            if hasattr(team, key):
                setattr(team, key, value)

        team.updated_at = datetime.now()

        try:
            return await self.team_repository.update(team)  # type: ignore[attr-defined]
        except AttributeError:
            return await self.team_repository.update_team(team)

    async def delete_team(self, team_id: str) -> bool:
        """
        Delete a team.

        :param team_id: Team ID to delete
        :type team_id: str
        :return: True if team was deleted successfully
        :rtype: bool
        """
        return await self.team_repository.delete(team_id)

    async def add_team_member(
        self,
        team_id: str,
        telegram_id: int,
        role: str = "player",
        permissions: list[str] | None = None,
        name: str = "",
        phone: str = "",
    ):
        """
        Add a member to a team.

        :param team_id: Team ID to add member to
        :type team_id: str
        :param telegram_id: Telegram user ID of the member
        :type telegram_id: int
        :param role: Role of the member (default: "player")
        :type role: str
        :param permissions: List of permissions for the member
        :type permissions: list[str] | None
        :param name: Name of the member
        :type name: str
        :param phone: Phone number of the member
        :type phone: str
        :return: True if member was added successfully
        :rtype: bool
        """
        # Import TeamMember dynamically to avoid circular imports
        from kickai.features.team_administration.domain.entities.team_member import TeamMember

        # Create team member entity
        team_member = TeamMember(
            team_id=team_id,
            name=name,
            phone=phone,
            telegram_id=telegram_id,  # Use telegram_id directly
            roles=[role],  # Convert single role to list
            permissions=permissions or [],
            joined_at=datetime.now(),
        )

        # Save to repository
        return await self.team_repository.create_team_member(team_member)

    async def remove_team_member(self, team_id: str, telegram_id: int) -> bool:
        """
        Remove a member from a team.

        :param team_id: Team ID to remove member from
        :type team_id: str
        :param telegram_id: Telegram user ID of the member to remove
        :type telegram_id: int
        :return: True if member was removed successfully
        :rtype: bool
        """
        # Get team member first
        team_members = await self.get_team_members(team_id)
        for member in team_members:
            if member.telegram_id == str(telegram_id):
                return await self.team_repository.delete_team_member(member.member_id)
        return False

    async def get_team_members(self, team_id: str) -> list[TeamMember]:
        """Get all members of a team."""
        return await self.team_repository.get_team_members(team_id)

    async def get_team_member_by_telegram_id(
        self, team_id: str, telegram_id: int
    ) -> TeamMember | None:
        """
        Get a team member by Telegram ID.

        :param team_id: Team ID to search in
        :type team_id: str
        :param telegram_id: Telegram user ID of the member
        :type telegram_id: int
        :return: Team member if found, None otherwise
        :rtype: TeamMember | None
        """
        return await self.team_repository.get_team_member_by_telegram_id(team_id, telegram_id)

    async def get_team_financial_summary(self, team_id: str) -> dict[str, Any]:
        """
        Get financial summary for a team including expenses.

        :param team_id: Team ID to get financial summary for
        :type team_id: str
        :return: Financial summary dictionary
        :rtype: dict[str, Any]
        """
        team = await self.get_team_by_id(team_id=team_id)
        if not team:
            return {}

        # Get total expenses using injected expense service (sync or async)
        get_total = getattr(self.expense_service, "get_total_expenses", None)
        if get_total is None:
            total_expenses = 0.0
        else:
            try:
                # Try await if coroutine
                import inspect
                if inspect.iscoroutinefunction(get_total):
                    total_expenses = await get_total(team_id)
                else:
                    total_expenses = get_total(team_id)
            except TypeError:
                total_expenses = get_total(team_id)

        # Get budget information (would need budget service injection)
        budget_info = {
            "total_budget": 0.0,  # Would be calculated from budget service
            "remaining_budget": 0.0,
            "utilization_percentage": 0.0,
        }

        return {
            "team_id": team_id,
            "team_name": team.name,
            "total_expenses": total_expenses,
            "budget_info": budget_info,
            "last_updated": datetime.now().isoformat(),
        }

    # Synchronous methods for CrewAI tools
    def get_team_sync(self, *, team_id: str) -> Team | None:
        """
        Synchronous version of get_team for CrewAI tools.

        :param team_id: Team ID to get
        :type team_id: str
        :return: Team if found, None otherwise
        :rtype: Team | None
        """
        try:
            # Import here to avoid circular imports
            import asyncio

            # Check if we're already in an event loop
            try:
                asyncio.get_running_loop()
                # We're in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.get_team(team_id=team_id))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(self.get_team(team_id=team_id))

        except Exception as e:
            self.logger.error(f"❌ Failed to get team {team_id}: {e}")
            return None

    def get_team_members_sync(self, team_id: str) -> list[TeamMember]:
        """
        Synchronous version of get_team_members for CrewAI tools.

        :param team_id: Team ID to get members for
        :type team_id: str
        :return: List of team members
        :rtype: list[TeamMember]
        """
        try:
            # Import here to avoid circular imports
            import asyncio

            # Check if we're already in an event loop
            try:
                asyncio.get_running_loop()
                # We're in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.get_team_members(team_id))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(self.get_team_members(team_id))

        except Exception as e:
            self.logger.error(f"❌ Failed to get team members for team {team_id}: {e}")
            return []

    def get_team_member_by_telegram_id_sync(
        self, team_id: str, telegram_id: int
    ) -> TeamMember | None:
        """
        Synchronous version of get_team_member_by_telegram_id for CrewAI tools.

        :param team_id: Team ID to search in
        :type team_id: str
        :param telegram_id: Telegram user ID of the member
        :type telegram_id: int
        :return: Team member if found, None otherwise
        :rtype: TeamMember | None
        """
        try:
            # Import here to avoid circular imports
            import asyncio

            # Check if we're already in an event loop
            try:
                asyncio.get_running_loop()
                # We're in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.get_team_member_by_telegram_id(team_id, telegram_id))
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run
                return asyncio.run(self.get_team_member_by_telegram_id(team_id, telegram_id))

        except Exception as e:
            self.logger.error(f"❌ Failed to get team member by telegram_id {telegram_id}: {e}")
            return None
