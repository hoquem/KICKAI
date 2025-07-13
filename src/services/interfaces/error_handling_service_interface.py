"""
Error Handling Service Interface

This interface defines the contract for error handling services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IErrorHandlingService(ABC):
    """Interface for error handling services."""
    
    @abstractmethod
    async def handle_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        message_text: Optional[str] = None,
        operation: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Handle an error and return a user-friendly message.
        
        Args:
            error: The exception that occurred
            user_id: ID of the user who triggered the error
            chat_id: ID of the chat where the error occurred
            message_text: Original message text that caused the error
            operation: Operation being performed when error occurred
            context: Additional context information
            
        Returns:
            User-friendly error message to display
        """
        pass
    
    @abstractmethod
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics for monitoring.
        
        Returns:
            Dictionary containing error statistics
        """
        pass
    
    @abstractmethod
    def get_recent_errors(self, limit: int = 10) -> List[Any]:
        """
        Get recent error reports for debugging.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error reports
        """
        pass 