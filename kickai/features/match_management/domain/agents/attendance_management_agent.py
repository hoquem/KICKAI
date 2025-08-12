import logging

from crewai import Agent

from kickai.features.match_management.domain.services.attendance_service import AttendanceService
from kickai.features.match_management.domain.tools.attendance_tools import (
    bulk_record_attendance,
    get_match_attendance,
    get_player_attendance_history,
    record_attendance,
)

logger = logging.getLogger(__name__)


class AttendanceManagementAgent:
    """CrewAI agent for attendance management operations."""

    def __init__(self):
        from kickai.core.dependency_container import get_container
        container = get_container()
        self.attendance_service = container.get_service(AttendanceService)
        if not self.attendance_service:
            raise ValueError("AttendanceService not found in container")
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the attendance management agent."""
        # The tools are now function-based and don't need service injection
        # They handle service access internally via dependency container
        tools = [
            record_attendance,
            get_match_attendance,
            get_player_attendance_history,
            bulk_record_attendance,
        ]

        return Agent(
            role="Attendance Manager",
            goal="Accurately track and record match day attendance for team performance analysis",
            backstory="""You are a meticulous attendance manager responsible for recording and tracking
            actual match day attendance. You ensure accurate records of who attended, who was absent,
            and who arrived late. You provide detailed attendance reports and statistics to help team
            managers understand player reliability and make informed decisions about squad selection.""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
        )

    def get_agent(self) -> Agent:
        """Get the attendance management agent."""
        return self.agent

    def get_tools(self) -> list:
        """Get the tools available to this agent."""
        return self.agent.tools
