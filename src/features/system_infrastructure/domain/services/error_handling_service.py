from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import traceback

from features.system_infrastructure.domain.interfaces.error_handling_service_interface import IErrorHandlingService

class ErrorHandlingService(IErrorHandlingService):
    def __init__(self, team_id: str = "default", telegram_service=None):
        self.team_id = team_id
        self.telegram_service = telegram_service
        self._error_log: List[Dict[str, Any]] = []
        self._error_stats: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def handle_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        message_text: Optional[str] = None,
        operation: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        self = args[0] if len(args := locals().get('args', [])) > 0 else self
        error_type = type(error).__name__
        error_message = str(error)
        tb = traceback.format_exc()
        timestamp = datetime.utcnow().isoformat()
        error_entry = {
            "timestamp": timestamp,
            "team_id": self.team_id,
            "user_id": user_id,
            "chat_id": chat_id,
            "operation": operation,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": tb,
            "context": context or {},
            "message_text": message_text,
        }
        async with self._lock:
            self._error_log.append(error_entry)
            self._error_stats[error_type] = self._error_stats.get(error_type, 0) + 1
        # Optionally notify via Telegram or other channels
        if self.telegram_service and chat_id:
            try:
                await self.telegram_service.send_message(
                    chat_id=chat_id,
                    text=f"❌ Error occurred in {operation}: {error_message}"
                )
            except Exception:
                pass  # Don't let notification errors propagate
        # Return a user-friendly message
        return f"❌ An error occurred while processing your request. Please try again later. (Error: {error_type})"

    def get_error_statistics(self) -> Dict[str, Any]:
        # Return a copy to avoid race conditions
        return dict(self._error_stats)

    def get_recent_errors(self, limit: int = 10) -> List[Any]:
        # Return the most recent errors up to the limit
        return list(self._error_log[-limit:]) 