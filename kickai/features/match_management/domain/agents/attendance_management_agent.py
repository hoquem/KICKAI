import logging

from crewai import Agent

from kickai.features.match_management.domain.services.attendance_service import AttendanceService
from kickai.features.match_management.domain.tools.attendance_tools import (
    BulkRecordAttendanceTool,
    GetMatchAttendanceTool,
    GetPlayerAttendanceHistoryTool,
    RecordAttendanceTool,
)

logger = logging.getLogger(__name__)


class AttendanceManagementAgent:
    """CrewAI agent for attendance management operations."""

    def __init__(self, attendance_service: AttendanceService):
        self.attendance_service = attendance_service
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the attendance management agent."""
        tools = [
            RecordAttendanceTool(self.attendance_service),
            GetMatchAttendanceTool(self.attendance_service),
            GetPlayerAttendanceHistoryTool(self.attendance_service),
            BulkRecordAttendanceTool(self.attendance_service),
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
