import logging

from crewai import Agent

from kickai.features.match_management.domain.services.match_service import MatchService
from kickai.features.match_management.domain.tools.match_tools import (
    create_match,
    get_match_details,
    list_matches_sync,
    record_match_result,
    select_squad_tool,
)

logger = logging.getLogger(__name__)


class MatchManagementAgent:
    """CrewAI agent for match management operations."""

    def __init__(self):
        from kickai.core.dependency_container import get_container
        container = get_container()
        self.match_service = container.get_service(MatchService)
        if not self.match_service:
            raise ValueError("MatchService not found in container")
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the match management agent."""
        # The tools are now function-based and don't need service injection
        # They handle service access internally via dependency container
        tools = [
            create_match,
            list_matches_sync,
            get_match_details,
            select_squad_tool,
            record_match_result,
        ]

        return Agent(
            role="Match Manager",
            goal="Efficiently manage match scheduling, squad selection, and match operations for Sunday league teams",
            backstory="""You are an experienced football team manager responsible for organizing matches,
            managing squad selection, and ensuring smooth match day operations. You have extensive
            experience in Sunday league football and understand the unique challenges of managing
            amateur teams with busy players who have work and family commitments.""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
        )

    def get_agent(self) -> Agent:
        """Get the match management agent."""
        return self.agent

    def get_tools(self) -> list:
        """Get the tools available to this agent."""
        return self.agent.tools
