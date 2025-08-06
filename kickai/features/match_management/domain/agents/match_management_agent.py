import logging

from crewai import Agent

from kickai.features.match_management.domain.services.match_service import MatchService
from kickai.features.match_management.domain.tools.match_tools import (
    CreateMatchTool,
    GetMatchDetailsTool,
    ListMatchesTool,
    RecordMatchResultTool,
    SelectSquadTool,
)

logger = logging.getLogger(__name__)


class MatchManagementAgent:
    """CrewAI agent for match management operations."""

    def __init__(self, match_service: MatchService):
        self.match_service = match_service
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the match management agent."""
        tools = [
            CreateMatchTool(self.match_service),
            ListMatchesTool(self.match_service),
            GetMatchDetailsTool(self.match_service),
            SelectSquadTool(self.match_service),
            RecordMatchResultTool(self.match_service),
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
