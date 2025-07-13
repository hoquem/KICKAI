"""
Financial Report Service Interface

This interface defines the contract for financial report services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IFinancialReportService(ABC):
    """Interface for financial report services."""
    
    @abstractmethod
    async def generate_financial_summary(self) -> str:
        """
        Generate a comprehensive financial summary for the team.
        
        Returns:
            Formatted financial summary string
        """
        pass
    
    @abstractmethod
    async def send_financial_report(self) -> bool:
        """
        Generate and send the financial report to the leadership chat.
        
        Returns:
            True if report was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def schedule_financial_report_task(self) -> None:
        """Schedule the financial report to run based on configuration."""
        pass 