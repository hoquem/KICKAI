from abc import ABC, abstractmethod


class IDailyStatusService(ABC):
    """Interface for daily status service operations."""

    @abstractmethod
    async def generate_team_stats(self, team_id: str) -> dict:
        """Generate comprehensive team statistics."""
        pass

    @abstractmethod
    def format_daily_status_message(self, team_stats: dict, team_name: str = "Team", report_content: list[str] | None = None) -> str:
        """Format the daily status message with HTML formatting."""
        pass

    @abstractmethod
    async def send_daily_status_report(self, team_id: str, leadership_chat_id: str) -> bool:
        """Send daily status report to leadership chat."""
        pass

    @abstractmethod
    async def schedule_daily_status_task(self, team_id: str, leadership_chat_id: str) -> None:
        """Schedule daily status report task."""
        pass
