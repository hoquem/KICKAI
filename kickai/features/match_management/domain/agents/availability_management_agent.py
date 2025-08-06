import logging

from crewai import Agent

from kickai.features.match_management.domain.services.availability_service import (
    AvailabilityService,
)
from kickai.features.match_management.domain.tools.availability_tools import (
    GetAvailabilityTool,
    GetPlayerAvailabilityHistoryTool,
    MarkAvailabilityTool,
    SendRemindersTool,
)

logger = logging.getLogger(__name__)


class AvailabilityManagementAgent:
    """CrewAI agent for availability management operations."""

    def __init__(self, availability_service: AvailabilityService):
        self.availability_service = availability_service
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the availability management agent."""
        tools = [
            MarkAvailabilityTool(self.availability_service),
            GetAvailabilityTool(self.availability_service),
            GetPlayerAvailabilityHistoryTool(self.availability_service),
            SendRemindersTool(self.availability_service),
        ]

        return Agent(
            role="Availability Coordinator",
            goal="Track player availability and manage attendance for optimal squad planning",
            backstory="""You are a dedicated team coordinator responsible for managing player availability 
            and ensuring the team has enough players for each match. You understand the importance of 
            early communication and work closely with players to get timely responses about their 
            availability. You help team managers make informed decisions about squad selection.""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
        )

    def get_agent(self) -> Agent:
        """Get the availability management agent."""
        return self.agent

    def get_tools(self) -> list:
        """Get the tools available to this agent."""
        return self.agent.tools
